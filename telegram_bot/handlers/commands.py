"""
Handlers de Comandos para Telegram Bot
=====================================

Maneja todos los comandos slash del bot (/start, /help, etc.)
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class CommandHandlers:
    """
    Clase que maneja todos los comandos del bot de Telegram
    """
    
    def __init__(self, bot_instance):
        """
        Args:
            bot_instance: Instancia del bot principal (EliasBot)
        """
        self.bot = bot_instance
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Comando /start - Mensaje de bienvenida
        """
        try:
            user = update.effective_user
            
            # Mensaje de bienvenida personalizado
            welcome_message = f"""
🤖 **¡Hola {user.first_name}! Soy ELiaS Bot**

Soy tu asistente inteligente para gestión de tareas con **Notion** e **IA**. 

🎯 **¿Qué puedo hacer por ti?**
• 📋 Crear tareas en lenguaje natural
• 🔍 Consultar tus tareas existentes  
• 📊 Generar resúmenes y estadísticas
• 🧠 Responder consultas inteligentes

💬 **Ejemplos de consultas:**
• "Tengo que estudiar matemáticas urgente"
• "¿Cuántas tareas pendientes tengo?"
• "Crear tarea importante: revisar código"
• "Muéstrame las tareas del proyecto Personal"

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
        """
        Comando /help - Ayuda detallada
        """
        try:
            help_message = """
📚 **Guía Completa de ELiaS Bot**

🤖 **Comandos Disponibles:**
• `/start` - Iniciar el bot
• `/help` - Esta ayuda
• `/stats` - Estadísticas del sistema
• `/admin` - Panel admin (solo admins)

💬 **Consultas en Lenguaje Natural:**

📝 **Crear Tareas:**
• "Tengo que hacer ejercicio mañana"
• "Nueva tarea urgente: llamar al doctor"
• "Para el proyecto Personal: comprar vitaminas"

🔍 **Consultar Tareas:**
• "¿Cuántas tareas tengo pendientes?"
• "Muéstrame todas mis tareas"
• "¿Qué tareas tengo para hoy?"
• "Tareas del proyecto Trabajo"

📊 **Información y Estadísticas:**
• "Dame un resumen de mis tareas"
• "¿Cuáles son mis proyectos?"
• "Estado del sistema"

🎯 **Combinadas:**
• "Dame un resumen y crea tarea de estudiar"
• "¿Qué tareas tengo? También agrega llamar cliente"

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
        """
        Comando /stats - Estadísticas del sistema
        """
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
        """
        Comando /admin - Panel de administración (solo admins)
        """
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