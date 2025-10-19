"""
Handlers de Callbacks para Telegram Bot
======================================

Maneja todas las interacciones con keyboards inline (botones).
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class CallbackHandlers:
    """
    Clase que maneja todos los callbacks de keyboards inline
    """
    
    def __init__(self, bot_instance):
        """
        Args:
            bot_instance: Instancia del bot principal (EliasBot)
        """
        self.bot = bot_instance
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler principal para callbacks de keyboards inline
        """
        try:
            query = update.callback_query
            await query.answer()  # Responder al callback para quitar el "loading"
            
            callback_data = query.data
            user_id = query.from_user.id
            
            logger.info(f"🔘 Callback de usuario {user_id}: {callback_data}")
            
            # Router de callbacks
            if callback_data == "main_menu":
                await self._show_main_menu(query)
            
            elif callback_data == "view_tasks":
                await self._show_task_menu(query)
            
            elif callback_data == "new_task":
                await self._show_new_task_guide(query)
            
            elif callback_data == "view_projects":
                await self._show_projects(query)
            
            elif callback_data == "stats":
                await self._show_stats(query)
            
            elif callback_data == "help":
                await self._show_help_menu(query)
            
            elif callback_data.startswith("tasks_"):
                await self._handle_task_filter(query, callback_data)
            
            elif callback_data.startswith("project_"):
                await self._handle_project_selection(query, callback_data)
            
            elif callback_data.startswith("help_"):
                await self._handle_help_category(query, callback_data)
            
            elif callback_data.startswith("admin_"):
                await self._handle_admin_action(query, callback_data)
            
            else:
                await self._handle_unknown_callback(query, callback_data)
        
        except Exception as e:
            logger.error(f"❌ Error en callback handler: {e}")
            try:
                await query.edit_message_text(
                    "❌ Error procesando acción. Inténtalo de nuevo.",
                    reply_markup=self.bot.keyboards.main_menu()
                )
            except:
                pass
    
    async def _show_main_menu(self, query):
        """Mostrar menú principal"""
        message = """
🤖 **ELiaS - Asistente Inteligente**

¿Qué te gustaría hacer?

💡 **Tip:** También puedes escribir directamente lo que necesites, como:
• "Crear tarea urgente de revisar código"
• "¿Cuántas tareas pendientes tengo?"
        """
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.bot.keyboards.main_menu()
        )
    
    async def _show_task_menu(self, query):
        """Mostrar menú de tareas"""
        message = """
📋 **Gestión de Tareas**

Selecciona qué tareas quieres ver:

💡 **Tip:** También puedes escribir consultas como:
• "Muéstrame las tareas urgentes"
• "¿Qué tareas tengo para hoy?"
        """
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.bot.keyboards.task_actions()
        )
    
    async def _show_new_task_guide(self, query):
        """Guía para crear nuevas tareas"""
        message = """
✨ **Crear Nueva Tarea**

🤖 **La forma más fácil:** ¡Solo escríbeme lo que necesitas!

📝 **Ejemplos:**
• "Tengo que estudiar matemáticas mañana"
• "Nueva tarea urgente: llamar al doctor"  
• "Para el proyecto Personal: hacer ejercicio"
• "Crear tarea alta prioridad: revisar código"

🎯 **Ventajas del lenguaje natural:**
• Detecta automáticamente la prioridad
• Asigna al proyecto correcto
• Extrae múltiples tareas de una frase
• ¡Super rápido y natural!

💬 **¡Escribe tu nueva tarea ahora!**
        """
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.bot.keyboards.back_button()
        )
    
    async def _show_projects(self, query):
        """Mostrar proyectos disponibles"""
        try:
            # Obtener proyectos usando el servicio existente
            from notion import proyectos_service
            
            if proyectos_service:
                proyectos = proyectos_service.cargar_proyectos_como_diccionario()
                project_names = list(proyectos.keys())
                
                if project_names:
                    message = f"""
📁 **Proyectos Disponibles ({len(project_names)})**

Selecciona un proyecto para ver sus tareas:

💡 **Tip:** También puedes preguntar:
• "¿Qué tareas tengo en el proyecto Personal?"
• "Muéstrame las tareas de Trabajo"
                    """
                    
                    await query.edit_message_text(
                        message,
                        parse_mode='Markdown',
                        reply_markup=self.bot.keyboards.project_selector(project_names[:8])  # Max 8 proyectos
                    )
                else:
                    await query.edit_message_text(
                        "📭 No hay proyectos configurados aún.",
                        reply_markup=self.bot.keyboards.back_button()
                    )
            else:
                raise Exception("ProyectosService no disponible")
                
        except Exception as e:
            logger.error(f"Error mostrando proyectos: {e}")
            await query.edit_message_text(
                "❌ Error cargando proyectos.",
                reply_markup=self.bot.keyboards.back_button()
            )
    
    async def _show_stats(self, query):
        """Mostrar estadísticas del sistema"""
        try:
            stats_message = await self.bot.get_stats_message()
            
            await query.edit_message_text(
                stats_message,
                parse_mode='Markdown',
                reply_markup=self.bot.keyboards.back_button()
            )
        except Exception as e:
            logger.error(f"Error mostrando stats: {e}")
            await query.edit_message_text(
                "❌ Error obteniendo estadísticas.",
                reply_markup=self.bot.keyboards.back_button()
            )
    
    async def _show_help_menu(self, query):
        """Mostrar menú de ayuda"""
        message = """
❓ **Centro de Ayuda ELiaS**

Selecciona una categoría para obtener ayuda específica:

🚀 **¿Primera vez?** Prueba escribir:
• "¿Cuántas tareas tengo?"
• "Crear tarea de estudiar"
        """
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.bot.keyboards.help_categories()
        )
    
    async def _handle_task_filter(self, query, callback_data):
        """Manejar filtros de tareas"""
        filter_type = callback_data.replace("tasks_", "")
        
        # Mapeo de filtros a consultas naturales
        filter_queries = {
            "all": "¿Cuántas tareas tengo en total?",
            "pending": "¿Cuáles son mis tareas pendientes?", 
            "completed": "¿Qué tareas he completado?",
            "urgent": "¿Cuáles son mis tareas urgentes?"
        }
        
        if filter_type in filter_queries:
            # Procesar como consulta natural
            try:
                respuesta = await self.bot.process_natural_query(
                    query=filter_queries[filter_type],
                    user_id=query.from_user.id
                )
                
                await query.edit_message_text(
                    respuesta,
                    parse_mode='Markdown',
                    reply_markup=self.bot.keyboards.task_actions()
                )
            except Exception as e:
                logger.error(f"Error filtrando tareas: {e}")
                await query.edit_message_text(
                    "❌ Error obteniendo tareas.",
                    reply_markup=self.bot.keyboards.task_actions()
                )
        else:
            await self._handle_unknown_callback(query, callback_data)
    
    async def _handle_project_selection(self, query, callback_data):
        """Manejar selección de proyecto"""
        project_name = callback_data.replace("project_", "")
        
        try:
            # Crear consulta natural para el proyecto
            natural_query = f"¿Qué tareas tengo en el proyecto {project_name}?"
            
            respuesta = await self.bot.process_natural_query(
                query=natural_query,
                user_id=query.from_user.id
            )
            
            await query.edit_message_text(
                respuesta,
                parse_mode='Markdown',
                reply_markup=self.bot.keyboards.back_button()
            )
            
        except Exception as e:
            logger.error(f"Error consultando proyecto {project_name}: {e}")
            await query.edit_message_text(
                f"❌ Error obteniendo tareas del proyecto {project_name}.",
                reply_markup=self.bot.keyboards.back_button()
            )
    
    async def _handle_help_category(self, query, callback_data):
        """Manejar categorías de ayuda"""
        category = callback_data.replace("help_", "")
        
        help_messages = {
            "ai": """
🤖 **Comandos de IA**

ELiaS entiende lenguaje natural. Puedes escribir como hablas:

✨ **Crear Tareas:**
• "Tengo que hacer ejercicio mañana"
• "Nueva tarea urgente: llamar doctor"
• "Para Personal: comprar vitaminas"

🔍 **Consultar:**
• "¿Cuántas tareas pendientes tengo?"
• "Muéstrame todas mis tareas"
• "¿Qué tareas tengo para hoy?"

📊 **Combinar:**
• "Dame resumen y crea tarea de estudiar"
            """,
            
            "tasks": """
📋 **Gestión de Tareas**

🎯 **Crear tareas:**
Solo describe lo que necesitas hacer de forma natural.

📊 **Estados disponibles:**
• Sin empezar
• Pendiente  
• En curso
• Completado

🏷️ **Prioridades:**
• Baja (🟢)
• Media (🟡) 
• Alta (🟠)
• Crítica (🔴)
            """,
            
            "projects": """
📁 **Proyectos**

Los proyectos organizan tus tareas por categorías.

🎯 **Asignación automática:**
ELiaS detecta el proyecto según el contexto de tu mensaje.

💡 **Ejemplos:**
• "Para el proyecto Personal: hacer deporte"
• "Tarea de Trabajo: revisar documentos"
            """,
            
            "config": """
⚙️ **Configuración**

🔧 **Comandos disponibles:**
• `/start` - Iniciar bot
• `/help` - Ayuda completa
• `/stats` - Estadísticas
• `/admin` - Panel admin (solo admins)

🤖 **IA siempre activa:**
No necesitas comandos especiales, solo escribe naturalmente.
            """
        }
        
        message = help_messages.get(category, "❓ Categoría de ayuda no encontrada.")
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=self.bot.keyboards.help_categories()
        )
    
    async def _handle_admin_action(self, query, callback_data):
        """Manejar acciones de admin"""
        # Verificar permisos
        if not self.bot.is_admin(query.from_user.id):
            await query.edit_message_text(
                "❌ Sin permisos de administrador.",
                reply_markup=self.bot.keyboards.main_menu()
            )
            return
        
        action = callback_data.replace("admin_", "")
        
        admin_messages = {
            "analytics": "📊 Analytics en desarrollo...",
            "users": "👥 Gestión de usuarios en desarrollo...", 
            "system": "🔧 Diagnósticos del sistema en desarrollo...",
            "logs": "📝 Visualización de logs en desarrollo..."
        }
        
        message = admin_messages.get(action, "❓ Acción de admin no encontrada.")
        
        await query.edit_message_text(
            message,
            reply_markup=self.bot.keyboards.admin_panel()
        )
    
    async def _handle_unknown_callback(self, query, callback_data):
        """Manejar callbacks desconocidos"""
        logger.warning(f"⚠️ Callback desconocido: {callback_data}")
        
        await query.edit_message_text(
            "❓ Acción no reconocida.",
            reply_markup=self.bot.keyboards.main_menu()
        )