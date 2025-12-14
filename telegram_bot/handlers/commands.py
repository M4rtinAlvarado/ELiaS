"""Handlers de Comandos para Telegram Bot - /start, /help, /stats, /admin, etc."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from core.optimization import get_optimization_stats

logger = logging.getLogger(__name__)


class CommandHandlers:
    """Maneja todos los comandos slash del bot de Telegram."""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Mensaje de bienvenida"""
        try:
            user = update.effective_user
            
            # Mensaje de bienvenida personalizado
            welcome_message = f"""
🤖 **¡Hola {user.first_name}! Soy ELiaS Bot**

Soy tu asistente inteligente para gestión de tareas y eventos con **Notion** e **IA**. 

🎯 **¿Qué puedo hacer por ti?**
• 📋 Crear tareas en lenguaje natural
• 📅 Crear eventos (reuniones, citas, cumpleaños)
• 🔍 Consultar tus tareas y eventos
• 📊 Generar resúmenes y estadísticas
• 🧠 Responder consultas inteligentes

💬 **Ejemplos de consultas:**
• "Tengo que estudiar matemáticas urgente" → Tarea
• "Reunión con el equipo mañana a las 3pm" → Evento
• "Cita con el doctor el viernes a las 10" → Evento
• "¿Cuántas tareas pendientes tengo?"
• "¿Qué eventos tengo esta semana?"

🚀 **¡Solo escríbeme en lenguaje natural y yo me encargo del resto!**
            """
            
            # Enviar mensaje con keyboard principal
            await update.message.reply_text(
                welcome_message,
                parse_mode='Markdown',
                reply_markup=self.bot.keyboards.main_menu()
            )
            
            logger.info(f"👋 Usuario {user.id} ({user.first_name}) inició el bot")
            
        except Exception as e:
            logger.error(f"Error en comando start: {e}")
            await update.message.reply_text(
                "❌ Error iniciando el bot. Inténtalo de nuevo."
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Ayuda detallada"""
        try:
            help_message = """
📚 **Guía Completa de ELiaS Bot**

🤖 **Comandos Disponibles:**
• `/start` - Iniciar el bot
• `/help` - Esta ayuda
• `/stats` - Estadísticas del sistema
• `/admin` - Panel admin (solo admins)

💬 **Consultas en Lenguaje Natural:**

📝 **Crear Tareas (cosas por HACER):**
• "Tengo que hacer ejercicio mañana"
• "Nueva tarea urgente: llamar al doctor"
• "Para el proyecto Personal: comprar vitaminas"

📅 **Crear Eventos (ocasiones a las que ASISTES):**
• "Reunión con el equipo mañana a las 3pm"
• "Cita con el doctor el viernes a las 10am"
• "El cumpleaños de Juan es el sábado"
• "Examen de matemáticas el lunes a las 8"

🔍 **Consultar Tareas y Eventos:**
• "¿Cuántas tareas tengo pendientes?"
• "Muéstrame todas mis tareas"
• "¿Qué eventos tengo esta semana?"
• "Próximos eventos"

📊 **Información y Estadísticas:**
• "Dame un resumen de mis tareas"
• "¿Cuáles son mis proyectos?"
• "Estado del sistema"

🎯 **Diferencia Tarea vs Evento:**
• **Tarea**: "Estudiar para el examen" (acción que debes hacer)
• **Evento**: "Examen el lunes a las 8am" (ocasión a la que asistes)

🚀 **¡Simplemente escribe lo que necesitas de forma natural!**
            """
            
            await update.message.reply_text(
                help_message,
                parse_mode='Markdown',
                reply_markup=self.bot.keyboards.help_categories()
            )
            
        except Exception as e:
            logger.error(f"Error en comando help: {e}")
            await update.message.reply_text("❌ Error mostrando ayuda.")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stats - Estadísticas del sistema"""
        try:
            # Generar mensaje de estadísticas
            stats_message = await self.bot.get_stats_message()
            
            await update.message.reply_text(
                stats_message,
                parse_mode='Markdown',
                reply_markup=self.bot.keyboards.quick_actions()
            )
            
            logger.info(f"📊 Usuario {update.effective_user.id} consultó estadísticas")
            
        except Exception as e:
            logger.error(f"Error en comando stats: {e}")
            await update.message.reply_text("❌ Error obteniendo estadísticas.")
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /admin - Panel de administración (solo admins)"""
        try:
            user_id = update.effective_user.id
            
            # Verificar permisos de admin
            if not self.bot.is_admin(user_id):
                await update.message.reply_text(
                    "❌ No tienes permisos de administrador.",
                    reply_markup=self.bot.keyboards.main_menu()
                )
                return
            
            admin_message = """
🔧 **Panel de Administración ELiaS**

👤 **Información del Admin:**
• ID: {user_id}
• Nombre: {user_name}

🤖 **Estado del Sistema:**
• Bot: ✅ Activo
• LangGraph: {langgraph_status}
• Notion: {notion_status}

📊 **Estadísticas Rápidas:**
• Total usuarios: En desarrollo
• Consultas hoy: En desarrollo
• Errores recientes: En desarrollo

⚙️ **Acciones disponibles en el panel below**
            """.format(
                user_id=user_id,
                user_name=update.effective_user.first_name,
                langgraph_status="✅ Activo" if self.bot.langgraph_service else "❌ Inactivo",
                notion_status="✅ Conectado" # Simplificado por ahora
            )
            
            await update.message.reply_text(
                admin_message,
                parse_mode='Markdown',
                reply_markup=self.bot.keyboards.admin_panel()
            )
            
            logger.info(f"🔧 Admin {user_id} accedió al panel")
            
        except Exception as e:
            logger.error(f"Error en comando admin: {e}")
            await update.message.reply_text("❌ Error accediendo al panel de admin.")

    async def optstats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /optstats - Estadísticas de optimización (solo admins)"""
        try:
            user_id = update.effective_user.id
            
            # Verificar permisos de admin
            if not self.bot.is_admin(user_id):
                await update.message.reply_text(
                    "❌ Este comando es solo para administradores.",
                    reply_markup=self.bot.keyboards.main_menu()
                )
                return
            
            # Obtener estadísticas de optimización
            stats = get_optimization_stats()
            cache_stats = stats.get("cache", {})
            debouncer_stats = stats.get("debouncer", {})
            lazy_loader_stats = stats.get("lazy_loader", {})
            
            # Datos del caché
            cache_hits = cache_stats.get("hits", 0)
            cache_misses = cache_stats.get("misses", 0)
            hit_rate = cache_stats.get("hit_rate_percent", 0)
            
            # Datos del lazy loader
            modules_loaded = lazy_loader_stats.get("modules_loaded", [])
            load_times = lazy_loader_stats.get("load_times", {})
            total_load_time = lazy_loader_stats.get("total_load_time", 0)
            
            # Formatear módulos cargados
            modules_str = ", ".join(modules_loaded) if modules_loaded else "Ninguno aún"
            
            stats_message = f"""
⚡ **Estadísticas de Optimización ELiaS**

📦 **Caché de Respuestas:**
• Tamaño actual: {cache_stats.get('current_size', 0)} / {cache_stats.get('max_size', 100)}
• Hits: {cache_hits}
• Misses: {cache_misses}
• Hit Rate: {hit_rate:.1f}%
• TTL: {cache_stats.get('ttl_seconds', 300)}s

⏱️ **Debouncer de Mensajes:**
• Usuarios pendientes: {debouncer_stats.get('pending_users', 0)}
• Mensajes recibidos: {debouncer_stats.get('messages_received', 0)}
• Mensajes combinados: {debouncer_stats.get('messages_combined', 0)}
• Delay: {debouncer_stats.get('delay_seconds', 1.5)}s

🚀 **Lazy Loader:**
• Módulos cargados: {modules_str}
• Tiempo total carga: {total_load_time:.2f}s

📊 **Eficiencia:**
• Llamadas AI evitadas por caché: {cache_hits}
• Ahorro estimado: ~{cache_hits * 0.5:.1f}s
            """
            
            await update.message.reply_text(
                stats_message,
                parse_mode='Markdown',
                reply_markup=self.bot.keyboards.main_menu()
            )
            
            logger.info(f"📊 Admin {user_id} consultó estadísticas de optimización")
            
        except Exception as e:
            logger.error(f"Error en comando optstats: {e}")
            await update.message.reply_text("❌ Error obteniendo estadísticas de optimización.")