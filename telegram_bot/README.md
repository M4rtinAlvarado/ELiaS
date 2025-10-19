# Telegram Bot - Módulo del Bot de Telegram

Este módulo proporciona una interfaz completa de bot de Telegram para interactuar con ELiaS mediante conversaciones naturales, comandos y teclados interactivos.

## 📁 Estructura

```
telegram_bot/
├── __init__.py              # Inicialización y exports principales
├── README.md               # Esta documentación
├── bot.py                  # Clase principal EliasBot
├── keyboards.py            # Teclados inline personalizados
└── handlers/               # Manejadores de eventos
    ├── __init__.py
    ├── command_handlers.py  # Comandos del bot (/start, /help, etc.)
    ├── message_handlers.py  # Mensajes de texto y consultas
    └── callback_handlers.py # Botones inline y callbacks
```

## 🚀 Inicio Rápido

### Ejecutar el Bot

```bash
# Desde la raíz del proyecto
python telegram_bot.py

# O directamente el módulo
python -m telegram_bot
```

### Uso Básico

1. **Busca tu bot** en Telegram usando el nombre configurado
2. **Inicia conversación** con `/start`
3. **Usa comandos o lenguaje natural**:
   - `/help` - Ver ayuda completa
   - "¿Cuántas tareas tengo?" - Consulta natural
   - "Crear tarea: estudiar Python" - Crear tareas
   - `/admin` - Panel de administración

## 🤖 Funcionalidades del Bot

### Comandos Disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/start` | Mensaje de bienvenida y configuración inicial | `/start` |
| `/help` | Ayuda completa con todos los comandos | `/help` |
| `/tareas` | Ver resumen de todas las tareas | `/tareas` |
| `/proyectos` | Listar proyectos disponibles | `/proyectos` |
| `/stats` | Estadísticas del sistema | `/stats` |
| `/admin` | Panel de administración (solo admins) | `/admin` |

### Consultas en Lenguaje Natural

El bot entiende consultas conversacionales:

```
Usuario: "¿Cuántas tareas tengo pendientes?"
Bot: "📋 Tienes 5 tareas pendientes"

Usuario: "Crear tarea: revisar código del proyecto web"
Bot: "✅ Tarea creada: revisar código del proyecto web"

Usuario: "Mis proyectos activos"
Bot: "📁 Proyectos activos:
     • Desarrollo Web
     • Estudio Personal
     • CEE 2025"
```

### Teclados Interactivos

El bot incluye teclados personalizados para navegación fácil:

- **Menú Principal**: Acceso rápido a funciones principales
- **Gestión de Tareas**: Crear, ver, filtrar tareas
- **Panel de Admin**: Funciones administrativas
- **Configuración**: Ajustes del usuario

## 🔧 Arquitectura del Bot

### Clase Principal: EliasBot

```python
from telegram_bot import EliasBot

# Crear instancia del bot
bot = EliasBot()

# Ejecutar bot
bot.run()  # Bloquea hasta Ctrl+C
```

#### Métodos Principales

```python
# Configuración
bot.build_bot()              # Construir aplicación sin ejecutar
bot.initialize_services()    # Inicializar servicios ELiaS

# Control de ejecución  
bot.run()                    # Ejecutar bot (blocking)
bot.stop()                   # Detener bot

# Utilidades
bot.is_admin(user_id)        # Verificar si usuario es admin
bot.send_to_admins(message)  # Enviar mensaje a todos los admins
```

### Sistema de Handlers

#### CommandHandlers

Maneja todos los comandos del bot (`/start`, `/help`, etc.):

```python
from telegram_bot.handlers import CommandHandlers

class CommandHandlers:
    async def start_command(self, update, context):
        """Comando /start con mensaje de bienvenida"""
        
    async def help_command(self, update, context):
        """Comando /help con información completa"""
        
    async def tareas_command(self, update, context):
        """Comando /tareas para ver resumen"""
```

#### MessageHandlers

Procesa mensajes de texto y consultas naturales:

```python
from telegram_bot.handlers import MessageHandlers

class MessageHandlers:
    async def handle_text_message(self, update, context):
        """Procesar mensaje de texto normal"""
        
    async def handle_natural_query(self, update, context):
        """Procesar consulta en lenguaje natural"""
        
    async def handle_task_creation(self, update, context):
        """Detectar y procesar creación de tareas"""
```

#### CallbackHandlers

Maneja interacciones con botones inline:

```python
from telegram_bot.handlers import CallbackHandlers

class CallbackHandlers:
    async def handle_main_menu(self, update, context):
        """Manejar selecciones del menú principal"""
        
    async def handle_task_actions(self, update, context):
        """Manejar acciones sobre tareas"""
        
    async def handle_admin_panel(self, update, context):
        """Manejar panel de administración"""
```

### Sistema de Teclados

```python
from telegram_bot.keyboards import TelegramKeyboards

keyboards = TelegramKeyboards()

# Teclados disponibles
main_menu = keyboards.get_main_menu()
task_menu = keyboards.get_task_management_menu()  
admin_menu = keyboards.get_admin_menu()
projects_menu = keyboards.get_projects_menu()
```

## 💡 Ejemplos de Uso Avanzado

### Personalizar Handlers

```python
from telegram_bot import EliasBot
from telegram.ext import CommandHandler

class MiBotPersonalizado(EliasBot):
    def setup_custom_handlers(self):
        """Agregar handlers personalizados"""
        
        async def comando_personalizado(update, context):
            await update.message.reply_text("¡Comando personalizado!")
        
        # Agregar handler
        self.application.add_handler(
            CommandHandler("custom", comando_personalizado)
        )
    
    def build_bot(self):
        # Llamar al build original
        super().build_bot()
        
        # Agregar nuestros handlers
        self.setup_custom_handlers()

# Usar bot personalizado
mi_bot = MiBotPersonalizado()
mi_bot.run()
```

### Integración con Servicios Personalizados

```python
class BotConServiciosExtra(EliasBot):
    def __init__(self):
        super().__init__()
        self.mi_servicio_extra = MiServicioExtra()
    
    async def handle_consulta_especial(self, update, context):
        """Handler para consultas especiales"""
        mensaje = update.message.text
        
        if "análisis especial" in mensaje.lower():
            # Usar nuestro servicio extra
            resultado = await self.mi_servicio_extra.analizar(mensaje)
            await update.message.reply_text(f"📊 Análisis: {resultado}")
```

### Middleware Personalizado

```python
async def logging_middleware(update, context, next_handler):
    """Middleware para logging de todas las interacciones"""
    
    user = update.effective_user
    print(f"📝 Usuario {user.id} ({user.username}): {update.message.text}")
    
    # Continuar con el handler normal
    await next_handler(update, context)

# Agregar middleware al bot
bot.application.add_middleware(logging_middleware)
```

## 🔒 Administración y Seguridad

### Sistema de Administradores

```python
# Configurar administradores en .env
TELEGRAM_ADMIN_IDS=123456789,987654321

# Verificar permisos en handlers
async def comando_admin(update, context):
    user_id = update.effective_user.id
    
    if not bot.is_admin(user_id):
        await update.message.reply_text("❌ Solo administradores pueden usar este comando")
        return
    
    # Lógica para administradores
    await update.message.reply_text("🔧 Panel de administración...")
```

### Panel de Administración

Funcionalidades disponibles para administradores:

- 📊 **Estadísticas del sistema**
- 👥 **Gestión de usuarios**
- 🔧 **Configuración del bot**
- 📋 **Logs y debugging**
- 🔄 **Reiniciar servicios**

### Limitación de Rate

```python
from functools import wraps
from time import time

def rate_limit(max_calls=10, period=60):
    """Decorator para limitar requests por usuario"""
    user_calls = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context):
            user_id = update.effective_user.id
            now = time()
            
            # Limpiar llamadas antiguas
            if user_id in user_calls:
                user_calls[user_id] = [
                    call_time for call_time in user_calls[user_id] 
                    if now - call_time < period
                ]
            else:
                user_calls[user_id] = []
            
            # Verificar límite
            if len(user_calls[user_id]) >= max_calls:
                await update.message.reply_text(
                    "⚠️ Demasiadas solicitudes. Espera un momento."
                )
                return
            
            # Registrar llamada y ejecutar
            user_calls[user_id].append(now)
            await func(update, context)
        
        return wrapper
    return decorator

# Usar en handlers
@rate_limit(max_calls=5, period=60)
async def comando_limitado(update, context):
    # Handler con límite de 5 llamadas por minuto
    pass
```

## 🧪 Testing del Bot

### Tests Disponibles

```bash
# Test completo del bot
python run_tests.py telegram

# Test específico de conexión
python run_tests.py conexion

# Verificación final
python run_tests.py verificar
```

### Test Manual

```python
# Crear bot de test
from telegram_bot import EliasBot

bot = EliasBot()
if bot.build_bot():
    print("✅ Bot construido correctamente")
    print("🚀 Listo para ejecutar")
else:
    print("❌ Error en configuración")
```

### Debug Mode

```python
import logging

# Habilitar debug completo
logging.basicConfig(level=logging.DEBUG)

# Logs específicos del bot
logging.getLogger('telegram_bot').setLevel(logging.DEBUG)
logging.getLogger('telegram').setLevel(logging.INFO)
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```env
# Bot Configuration (requerido)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ADMIN_IDS=123456789,987654321

# Bot Behavior (opcional)
TELEGRAM_ENABLE_LOGGING=true
TELEGRAM_PARSE_MODE=Markdown
TELEGRAM_DISABLE_NOTIFICATION=false

# Rate Limiting (opcional)
TELEGRAM_MAX_REQUESTS_PER_MINUTE=30
TELEGRAM_ENABLE_RATE_LIMITING=true

# Features (opcional)
TELEGRAM_ENABLE_NATURAL_LANGUAGE=true
TELEGRAM_ENABLE_ADMIN_PANEL=true
TELEGRAM_ENABLE_INLINE_KEYBOARDS=true
```

### Personalización de Mensajes

```python
# Personalizar mensajes del bot
MENSAJES_PERSONALIZADOS = {
    "bienvenida": "¡Hola! Soy tu asistente personalizado 🤖",
    "error_permisos": "❌ No tienes permisos para esta acción",
    "tarea_creada": "✅ Tarea '{nombre}' creada exitosamente",
    "sistema_ocupado": "⚠️ Sistema ocupado, intenta en un momento"
}

# Usar en handlers
async def start_personalizado(update, context):
    await update.message.reply_text(MENSAJES_PERSONALIZADOS["bienvenida"])
```

## 📊 Monitoreo y Analytics

### Métricas Básicas

```python
from collections import defaultdict
from datetime import datetime

class BotMetrics:
    def __init__(self):
        self.user_interactions = defaultdict(int)
        self.command_usage = defaultdict(int)
        self.daily_active_users = set()
    
    def track_interaction(self, user_id, command=None):
        self.user_interactions[user_id] += 1
        self.daily_active_users.add(user_id)
        if command:
            self.command_usage[command] += 1
    
    def get_stats(self):
        return {
            "total_users": len(self.user_interactions),
            "active_today": len(self.daily_active_users),
            "most_used_commands": dict(self.command_usage.most_common(5))
        }

# Integrar en el bot
metrics = BotMetrics()

async def track_usage(update, context):
    user_id = update.effective_user.id
    command = update.message.text.split()[0] if update.message.text else None
    metrics.track_interaction(user_id, command)
```

## ⚠️ Troubleshooting

### Problemas Comunes

#### Bot no responde
```bash
# Verificar configuración
python tests/test_conexion.py

# Verificar token
python -c "from config import settings; print(f'Token: ...{settings.TELEGRAM_BOT_TOKEN[-8:]}')"
```

#### Error de permisos
```bash
# Verificar admin IDs
python -c "from config import settings; print(f'Admins: {settings.TELEGRAM_ADMIN_IDS}')"
```

#### Memoria alta
```bash
# Verificar handlers duplicados
# Revisar logs para memory leaks
# Implementar rate limiting
```

### Logs Útiles

```python
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
```

## 📚 Referencias

- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Bot Father Guide](https://core.telegram.org/bots#botfather)
- [Telegram Bot Best Practices](https://core.telegram.org/bots/faq)

## 🤝 Contribuir

### Agregar Nuevo Comando

1. Crear handler en `handlers/command_handlers.py`
2. Registrar en `setup_handlers()` del bot
3. Agregar documentación en `/help`
4. Crear tests correspondientes

### Agregar Nueva Funcionalidad

1. Planificar la interfaz de usuario
2. Crear handlers necesarios
3. Actualizar teclados si es necesario
4. Documentar y testing

---

**Bot de Telegram inteligente y conversacional** 🤖💬