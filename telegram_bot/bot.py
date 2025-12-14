"""
Bot Principal de Telegram para ELiaS
====================================

Clase principal que maneja la configuración y operación del bot de Telegram.
Integra perfectamente con la arquitectura modular existente de ELiaS.
"""

import logging
from typing import Optional
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# Importar servicios existentes de ELiaS
from config import settings
from notion import tareas_service, proyectos_service

# Importar sistema de optimización
try:
    from core.optimization import (
        local_response_matcher,
        message_debouncer,
        response_cache,
        LazyLoader,
        get_optimization_stats
    )
    OPTIMIZATION_ENABLED = True
    lazy_loader = LazyLoader()
except ImportError:
    OPTIMIZATION_ENABLED = False
    local_response_matcher = None
    message_debouncer = None
    lazy_loader = None

# Importar handlers locales
from .handlers.commands import CommandHandlers
from .handlers.messages import MessageHandlers
from .handlers.callbacks import CallbackHandlers
from .keyboards import TelegramKeyboards

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def _get_attr_value(obj, attr: str, default=""):
    """Helper para obtener valor de atributo (soporta enums)."""
    val = getattr(obj, attr, None)
    if val is None:
        return default
    return val.value if hasattr(val, 'value') else val


def _format_tarea(tarea, compact: bool = False) -> str:
    """Formatea una tarea para mostrar al usuario."""
    prioridad = _get_attr_value(tarea, 'prioridad', 'Normal')
    estado = _get_attr_value(tarea, 'estado', 'Pendiente')
    fecha = getattr(tarea, 'fecha_vencimiento', None)
    proyecto_ids = getattr(tarea, 'proyecto_ids', None)
    tiempo_estimado = getattr(tarea, 'tiempo_estimado', None)
    
    if compact:
        linea = f"⚡ {prioridad}"
        if fecha:
            linea += f" | 📅 {fecha.strftime('%d/%m/%Y')}"
        if tiempo_estimado:
            linea += f" | ⏱️ {tiempo_estimado}min"
        if proyecto_ids:
            linea += f" | 📁 {proyecto_ids[0]}"
        return linea
    
    # Formato completo
    resp = f"📝 **Título:** {tarea.nombre}\n"
    resp += f"⚡ **Prioridad:** {prioridad}\n"
    resp += f"📊 **Estado:** {estado}\n"
    if tiempo_estimado:
        resp += f"⏱️ **Tiempo Estimado:** {tiempo_estimado} min\n"
    if fecha:
        resp += f"📅 **Vencimiento:** {fecha.strftime('%d/%m/%Y')}\n"
    if proyecto_ids:
        resp += f"📁 **Proyecto:** {proyecto_ids[0]}\n"
    resp += f"🆔 **ID:** `{tarea.id}`\n"
    return resp


def _format_evento(evento, compact: bool = False) -> str:
    """Formatea un evento para mostrar al usuario."""
    tipo = _get_attr_value(evento, 'tipo', 'Otro')
    estado = _get_attr_value(evento, 'estado', 'Programado')
    fecha = getattr(evento, 'fecha', None)
    ubicacion = getattr(evento, 'ubicacion', None)
    
    if compact:
        linea = f"📌 {tipo}"
        if fecha:
            linea += f" | 🗓️ {fecha.strftime('%d/%m/%Y %H:%M')}"
        if ubicacion:
            linea += f" | 📍 {ubicacion}"
        return linea
    
    # Formato completo
    resp = f"📅 **Evento:** {evento.nombre}\n"
    resp += f"📌 **Tipo:** {tipo}\n"
    resp += f"📊 **Estado:** {estado}\n"
    if fecha:
        resp += f"🗓️ **Fecha:** {fecha.strftime('%d/%m/%Y %H:%M')}\n"
    if ubicacion:
        resp += f"📍 **Ubicación:** {ubicacion}\n"
    resp += f"🆔 **ID:** `{evento.id}`\n"
    return resp


class EliasBot:
    """
    Bot principal de Telegram para ELiaS v2.0
    
    Características:
    - Integración completa con LangGraphService
    - Procesamiento inteligente de consultas en lenguaje natural
    - Creación y consulta de tareas vía chat
    - Interfaz de usuario rica con keyboards inline
    - Gestión de errores robusta
    """
    
    def __init__(self):
        """Inicializar el bot con configuración desde settings"""
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.admin_ids = self._parse_admin_ids()
        self.application = None
        self.langgraph_service = None
        self.keyboards = TelegramKeyboards()
        
        # Inicializar handlers
        self.command_handlers = CommandHandlers(self)
        self.message_handlers = MessageHandlers(self)
        self.callback_handlers = CallbackHandlers(self)
        
        logger.info("🤖 EliasBot inicializado correctamente")
    
    def _parse_admin_ids(self) -> list:
        """Parsear IDs de administradores desde configuración"""
        try:
            # Usar la misma lógica que funciona en el bot simple
            import os
            admin_ids_str = os.getenv("TELEGRAM_ADMIN_IDS", "")
            admin_ids = []
            
            if admin_ids_str:
                # Limpiar corchetes y parsear
                clean_str = admin_ids_str.strip("[]").strip()
                for id_str in clean_str.split(","):
                    id_str = id_str.strip()
                    if id_str:
                        admin_ids.append(int(id_str))
            
            logger.info(f"📋 Admin IDs parseados: {admin_ids}")
            return admin_ids
            
        except Exception as e:
            logger.warning(f"⚠️ Error parseando admin IDs: {e}")
            return []
    
    def is_admin(self, user_id: int) -> bool:
        """Verificar si un usuario es administrador"""
        return user_id in self.admin_ids
    
    def initialize_services(self):
        """Inicializar servicios de ELiaS con lazy loading"""
        try:
            # Usar lazy loading para LangGraphService (carga bajo demanda)
            if OPTIMIZATION_ENABLED and lazy_loader:
                try:
                    self.langgraph_service = lazy_loader.get_langgraph_service()
                    if self.langgraph_service:
                        logger.info("✅ LangGraphService disponible (lazy loading)")
                except Exception as e:
                    logger.warning(f"⚠️ LangGraphService no disponible: {e}")
                    self.langgraph_service = None
            else:
                # Fallback: carga directa
                try:
                    from ia.services import LangGraphService
                    self.langgraph_service = LangGraphService()
                    logger.info("✅ LangGraphService inicializado (directo)")
                except Exception as e:
                    logger.warning(f"⚠️ LangGraphService no disponible: {e}")
                    self.langgraph_service = None
            
            # Verificar servicios críticos de Notion
            if not tareas_service:
                raise RuntimeError("TareasService no disponible")
            
            if not proyectos_service:
                logger.warning("⚠️ ProyectosService no disponible")
            
            # Log de optimizaciones activas
            if OPTIMIZATION_ENABLED:
                logger.info("🚀 Optimizaciones activas: Caché, Debouncing, Lazy Loading")
            
            logger.info("✅ Servicios básicos inicializados para Telegram")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando servicios: {e}")
            return False
    
    async def _process_fallback_query(self, query: str, user_id: int) -> str:
        """
        Procesamiento de fallback para consultas básicas
        
        Args:
            query: Consulta del usuario
            user_id: ID del usuario
            
        Returns:
            Respuesta básica del sistema
        """
        try:
            from notion import tareas_service, proyectos_service
            
            query_lower = query.lower()
            
            if "cuántas tareas" in query_lower or "total" in query_lower:
                tareas = tareas_service.obtener_todas_las_tareas()
                return f"📊 Tienes {len(tareas)} tareas en total"
            
            elif "crear tarea" in query_lower:
                # Extraer título de la tarea
                if ":" in query:
                    titulo = query.split(":", 1)[1].strip()
                else:
                    titulo = query.replace("crear tarea", "", 1).strip()
                
                if titulo:
                    # Usar el método inteligente también en fallback
                    nueva_tarea = tareas_service.crear_tarea_inteligente(titulo)
                    if nueva_tarea:
                        tarea = nueva_tarea[0] if isinstance(nueva_tarea, list) else nueva_tarea
                        respuesta = f"✅ **Tarea creada:** {tarea.nombre}\n"
                        respuesta += _format_tarea(tarea)
                        
                        # Agregar link a Notion
                        if hasattr(settings, 'NOTION_DB_TAREAS') and settings.NOTION_DB_TAREAS:
                            link_notion = f"https://www.notion.so/{settings.NOTION_DB_TAREAS.replace('-', '')}"
                            respuesta += f"\n🔗 [Ver en Notion]({link_notion})"
                        
                        return respuesta
                    else:
                        return "❌ Error creando la tarea"
                else:
                    return "💡 Usa el formato: 'crear tarea: hacer ejercicio'"
            
            elif "crear evento" in query_lower:
                # Extraer datos del evento
                if ":" in query:
                    descripcion = query.split(":", 1)[1].strip()
                else:
                    descripcion = query.replace("crear evento", "", 1).strip()
                
                if descripcion:
                    try:
                        from notion.services.eventos_service import eventos_service
                        if eventos_service:
                            nuevo_evento = eventos_service.crear_evento_inteligente(descripcion)
                            if nuevo_evento:
                                respuesta = f"✅ **Evento creado:** {nuevo_evento.nombre}\n"
                                respuesta += f"📌 **Tipo:** {nuevo_evento.tipo.value}\n"
                                if nuevo_evento.fecha:
                                    respuesta += f"🗓️ **Fecha:** {nuevo_evento.fecha.strftime('%d/%m/%Y %H:%M')}\n"
                                if nuevo_evento.ubicacion:
                                    respuesta += f"📍 **Ubicación:** {nuevo_evento.ubicacion}\n"
                                return respuesta
                            else:
                                return "❌ Error creando el evento"
                        else:
                            return "❌ Servicio de eventos no configurado. Añade NOTION_DB_EVENTOS en .env"
                    except Exception as e:
                        return f"❌ Error con eventos: {e}"
                else:
                    return "💡 Usa el formato: 'crear evento: reunión mañana a las 3pm'"
            
            elif "eventos" in query_lower or "próximos" in query_lower:
                try:
                    from notion.services.eventos_service import eventos_service
                    if eventos_service:
                        eventos = eventos_service.obtener_proximos_eventos(7)
                        if eventos:
                            respuesta = f"📅 **Próximos {len(eventos)} eventos:**\n\n"
                            for i, e in enumerate(eventos[:5], 1):
                                respuesta += f"{i}. **{e.nombre}**\n"
                                if e.fecha:
                                    respuesta += f"   🗓️ {e.fecha.strftime('%d/%m/%Y %H:%M')}\n"
                                respuesta += f"   📌 {e.tipo.value}\n"
                            return respuesta
                        else:
                            return "📭 No tienes eventos próximos en los siguientes 7 días"
                    else:
                        return "❌ Servicio de eventos no configurado"
                except Exception as e:
                    return f"❌ Error consultando eventos: {e}"
            
            elif "proyectos" in query_lower:
                proyectos = proyectos_service.cargar_proyectos_como_diccionario()
                nombres = list(proyectos.keys())[:5]
                return f"📁 Proyectos disponibles:\n• " + "\n• ".join(nombres)
            
            elif "pendientes" in query_lower:
                tareas = tareas_service.obtener_todas_las_tareas()
                pendientes = [t for t in tareas if t.estado.value in ["Sin empezar", "Pendiente", "En curso"]]
                return f"📋 Tienes {len(pendientes)} tareas pendientes"
            
            else:
                return f"""📱 Consulta recibida: {query}

💡 **Comandos disponibles:**
• "¿Cuántas tareas tengo?"
• "Crear tarea: [descripción]"
• "Crear evento: [descripción]"
• "Mis proyectos"
• "Tareas pendientes"
• "Eventos próximos"

🔥 **Nuevo:** Ahora puedes usar lenguaje natural:
• "Tengo que estudiar matemáticas mañana" → Crea tarea
• "Reunión con el equipo el viernes a las 3pm" → Crea evento
• "Cita con el doctor el lunes a las 10" → Crea evento
"""
            
        except Exception as e:
            logger.error(f"❌ Error en fallback: {e}")
            return f"❌ Error al procesar tu consulta: {str(e)}"
    
    async def process_natural_query(self, query: str, user_id: int) -> str:
        """
        Procesar consulta en lenguaje natural usando el sistema mejorado de prompts
        
        Args:
            query: Consulta del usuario
            user_id: ID del usuario (para logs y analytics)
            
        Returns:
            Respuesta procesada por el sistema con información detallada
        """
        try:
            logger.info(f"🔄 Procesando consulta de usuario {user_id}: {query[:50]}...")
            
            # 1. OPTIMIZACIÓN: Intentar respuesta local primero (sin IA)
            if OPTIMIZATION_ENABLED and local_response_matcher:
                local_response = local_response_matcher(query)
                if local_response:
                    logger.info(f"📍 Respuesta local para usuario {user_id}")
                    return local_response
            
            # Intentar usar LangGraphService primero
            if self.langgraph_service:
                try:
                    resultado = self.langgraph_service.procesar_consulta(query)
                    logger.info(f"✅ Consulta procesada con LangGraph para usuario {user_id}")
                    
                    # Mejorar respuesta si es creación de tarea (con manejo seguro de errores)
                    try:
                        if "creada exitosamente" in resultado or "Tarea creada" in resultado:
                            # Agregar link a Notion
                            link_notion = "🔗 [Ver en Notion](https://www.notion.so/)"
                            if hasattr(settings, 'NOTION_DB_TAREAS') and settings.NOTION_DB_TAREAS:
                                link_notion = f"🔗 [Ver en Notion](https://www.notion.so/{settings.NOTION_DB_TAREAS.replace('-', '')})"
                            
                            resultado += f"\n\n{link_notion}"
                            resultado += f"\n\n💡 *Tip: Usa comandos como 'estudiar matemáticas mañana' para crear tareas más rápido*"
                    except Exception as link_error:
                        logger.warning(f"⚠️ Error agregando link a respuesta: {link_error}")
                        # Continuar sin el link, no fallar toda la operación
                    
                    return resultado
                    
                except Exception as e:
                    logger.warning(f"⚠️ LangGraph falló: {e}")
            
            # Fallback mejorado usando GeminiService con nuevos prompts
            try:
                from ia.services.gemini_service import GeminiService
                gemini_service = GeminiService()
                
                # Detectar si es creación de tarea (lista expandida)
                query_lower = query.lower()
                palabras_tarea = [
                    "crear", "hacer", "tengo que", "debo", "necesito", "recordar",
                    "tengo", "hay que", "quiero", "voy a", "mañana tengo", 
                    "hoy tengo", "esta semana", "el lunes", "el martes", 
                    "el miércoles", "el jueves", "el viernes", "tarea", 
                    "proyecto", "estudiar", "comprar", "llamar", "enviar",
                    "entregar", "revisar", "completar", "ir a"
                ]
                
                if any(palabra in query_lower for palabra in palabras_tarea):
                    # Usar el nuevo sistema de extracción de tareas
                    resultado_extraccion = gemini_service.extraer_datos_tarea(query)
                    
                    if resultado_extraccion and resultado_extraccion.get('exitosa'):
                        tareas = resultado_extraccion.get('tareas', [])
                        tareas_creadas = []
                        
                        # Usar el servicio inteligente que maneja todo automáticamente
                        resultado_creacion = tareas_service.crear_tarea_inteligente(query)
                        
                        if resultado_creacion:
                            if isinstance(resultado_creacion, list):
                                # Múltiples tareas creadas
                                respuesta = f"✅ **{len(resultado_creacion)} tareas creadas exitosamente**\n\n"
                                for i, tarea in enumerate(resultado_creacion, 1):
                                    respuesta += f"**{i}.** {tarea.nombre}\n"
                                    respuesta += f"   {_format_tarea(tarea, compact=True)}"
                                    if hasattr(tarea, 'id') and tarea.id:
                                        respuesta += f"\n   🆔 ID: `{tarea.id}`"
                                    respuesta += "\n\n"
                            else:
                                # Una sola tarea creada
                                tarea = resultado_creacion
                                respuesta = f"✅ **Tarea creada exitosamente**\n\n"
                                respuesta += _format_tarea(tarea)
                            
                            # Agregar link a Notion
                            if hasattr(settings, 'NOTION_DB_TAREAS') and settings.NOTION_DB_TAREAS:
                                link_notion = f"https://www.notion.so/{settings.NOTION_DB_TAREAS.replace('-', '')}"
                                respuesta += f"\n🔗 [Ver todas las tareas en Notion]({link_notion})"
                            
                            respuesta += f"\n\n💡 *Tip: Ahora puedes usar lenguaje natural como 'comprar leche en 2 días'*"
                            return respuesta
                        
                        else:
                            return "❌ No se pudo crear la tarea. Intenta con un formato más específico como 'Crear tarea: estudiar matemáticas'"
                    else:
                        error = resultado_extraccion.get('error', 'Error desconocido')
                        return f"❌ Error procesando tu solicitud: {error}\n\n💡 Intenta con: 'Crear tarea estudiar matemáticas mañana'"
                
                # Consultas generales usando fallback básico
                return await self._process_fallback_query(query, user_id)
                
            except Exception as e:
                logger.error(f"Error en procesamiento mejorado: {e}")
                return await self._process_fallback_query(query, user_id)
            
        except Exception as e:
            logger.error(f"❌ Error crítico procesando consulta: {e}")
            return f"❌ Error del sistema. Intenta de nuevo o usa /help para ver comandos disponibles."

    async def get_stats_message(self) -> str:
        """Generar mensaje con estadísticas del sistema"""
        try:
            # Obtener estadísticas usando servicios existentes
            total_tareas = len(tareas_service.obtener_todas_las_tareas()) if tareas_service else 0
            
            proyectos = {}
            if proyectos_service:
                proyectos = proyectos_service.cargar_proyectos_como_diccionario()
            
            mensaje = "📊 **Estado del Sistema ELiaS**\n\n"
            mensaje += f"✅ **Tareas totales:** {total_tareas}\n"
            mensaje += f"📁 **Proyectos:** {len(proyectos)}\n"
            
            if proyectos:
                mensaje += f"📋 **Proyectos disponibles:**\n"
                for nombre in list(proyectos.keys())[:5]:  # Máximo 5
                    mensaje += f"   • {nombre}\n"
            
            # Estado de servicios
            mensaje += f"\n🤖 **Servicios IA:** {'✅ Activo' if self.langgraph_service else '❌ Inactivo'}"
            mensaje += f"\n📊 **Notion:** {'✅ Conectado' if tareas_service else '❌ Desconectado'}"
            
            return mensaje
            
        except Exception as e:
            logger.error(f"Error generando estadísticas: {e}")
            return "❌ Error obteniendo estadísticas del sistema"
    
    def setup_handlers(self):
        """Configurar todos los handlers del bot"""
        if not self.application:
            logger.error("Application no inicializada")
            return
        
        # Comandos básicos
        self.application.add_handler(
            CommandHandler("start", self.command_handlers.start_command)
        )
        self.application.add_handler(
            CommandHandler("help", self.command_handlers.help_command)
        )
        self.application.add_handler(
            CommandHandler("stats", self.command_handlers.stats_command)
        )
        
        # Comandos de administrador
        self.application.add_handler(
            CommandHandler("admin", self.command_handlers.admin_command)
        )
        self.application.add_handler(
            CommandHandler("optstats", self.command_handlers.optstats_command)
        )
        
        # Handler para mensajes de texto (consultas naturales)
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.message_handlers.handle_text_message
            )
        )
        
        # Handler para mensajes de voz
        self.application.add_handler(
            MessageHandler(
                filters.VOICE, 
                self.message_handlers.handle_voice_message
            )
        )
        
        # Handler para documentos (futuro)
        self.application.add_handler(
            MessageHandler(
                filters.Document.ALL,
                self.message_handlers.handle_document
            )
        )
        
        # Handler para callbacks de keyboards inline
        self.application.add_handler(
            CallbackQueryHandler(self.callback_handlers.handle_callback)
        )
        
        # Handler para errores
        self.application.add_error_handler(self.error_handler)
        
        logger.info("🔧 Handlers configurados correctamente")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler global para errores"""
        logger.error(f"❌ Error en bot: {context.error}")
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ Ocurrió un error inesperado. Por favor, inténtalo de nuevo."
                )
            except:
                pass  # No podemos hacer nada si no podemos responder
    
    def build_bot(self):
        """Construir la aplicación del bot (sin ejecutar)"""
        try:
            # Validar configuración
            if not self.token:
                raise ValueError("TELEGRAM_BOT_TOKEN no configurado en .env")
            
            # Construir aplicación
            self.application = ApplicationBuilder().token(self.token).build()
            
            # Configurar handlers
            self.setup_handlers()
            
            # Inicializar servicios de ELiaS
            services_ok = self.initialize_services()
            if not services_ok:
                logger.warning("⚠️ Algunos servicios no se iniciaron correctamente")
            
            logger.info("✅ Bot construido correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error construyendo bot: {e}")
            return False
    

    
    def run(self):
        """Punto de entrada principal para ejecutar el bot"""
        try:
            # Construir bot primero
            if not self.build_bot():
                return False
            
            # Inicializar servicios (síncronamente para evitar conflictos)
            logger.info("🚀 Iniciando EliasBot...")
            logger.info(f"📋 Administradores: {self.admin_ids}")
            
            print("🤖 ELiaS Bot iniciado. Presiona Ctrl+C para detener.")
            
            # EXACTAMENTE como el bot simple que funciona
            import asyncio
            asyncio.run(self.application.run_polling(drop_pending_updates=True))
            
        except KeyboardInterrupt:
            logger.info("👋 Bot detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error ejecutando bot: {e}")
            raise