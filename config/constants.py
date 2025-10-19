"""
Constantes del proyecto ELiaS
Valores que no cambian durante la ejecución
"""

# === VERSIÓN ===
VERSION = "1.0.0"
APP_NAME = "ELiaS"
DESCRIPTION = "Asistente Inteligente con Notion, LangGraph y Telegram"

# === NOTION CONSTANTS ===
NOTION_API_VERSION = "2022-06-28"

# Propiedades estándar de Notion (nombres esperados)
NOTION_PROPERTIES = {
    "TAREAS": {
        "NOMBRE": "Nombre",
        "PRIORIDAD": "Prioridad", 
        "FECHA": "Fecha",
        "ESTADO": "Estado",
        "PROYECTOS": "Proyectos"
    },
    "PROYECTOS": {
        "NOMBRE": "Nombre",
    }
}

# Valores por defecto para propiedades
DEFAULT_VALUES = {
    "PRIORIDAD": "Media",
    "ESTADO_TAREA": "Sin empezar",
}

# === AI/LLM CONSTANTS ===
SUPPORTED_MODELS = {
    "GEMINI": [
        "gemini-2.0-flash"
    ]
}

# Límites de tokens
TOKEN_LIMITS = {
    "gemini-2.0-flash": 8192,
}

# === LANGGRAPH CONSTANTS ===
GRAPH_NODES = {
    "DECISOR": "decisor_intencion",
    "CREAR_TAREA": "crear_tarea", 
    "CONSULTAR_TAREAS": "consultar_tareas",
    "ACTUALIZAR_TAREA": "actualizar_tarea",  # Futuro
}

INTENTION_TYPES = {
    "CREAR": "crear",
    "CONSULTAR": "consultar", 
    "ACTUALIZAR": "actualizar",  # Futuro
    "AMBIGUO": "ambiguo"
}

# === TELEGRAM CONSTANTS (FUTURO) ===
TELEGRAM_LIMITS = {
    "MESSAGE_LENGTH": 4096,
    "CAPTION_LENGTH": 1024,
    "BUTTON_TEXT_LENGTH": 64
}

TELEGRAM_COMMANDS = {
    "START": "start",
    "HELP": "help",
    "CONFIG": "config",
    "STATS": "stats",
    "PROYECTOS": "proyectos"
}

# === ERROR MESSAGES ===
ERROR_MESSAGES = {
    "NOTION_CONNECTION": "❌ Error de conexión con Notion",
    "NOTION_TOKEN_INVALID": "❌ Token de Notion inválido o expirado",
    "NOTION_DB_NOT_FOUND": "❌ Base de datos de Notion no encontrada",
    "GEMINI_ERROR": "❌ Error al procesar con Gemini",
    "GEMINI_QUOTA_EXCEEDED": "❌ Cuota de Gemini excedida",
    "LANGGRAPH_ERROR": "❌ Error en procesamiento LangGraph",
    "INVALID_CONFIG": "❌ Configuración inválida",
    "UNKNOWN_ERROR": "❌ Error desconocido"
}

# === SUCCESS MESSAGES ===
SUCCESS_MESSAGES = {
    "TAREA_CREATED": "✅ Tarea creada exitosamente",
    "TAREA_UPDATED": "✅ Tarea actualizada",
    "TAREA_DELETED": "✅ Tarea eliminada",
    "CONFIG_LOADED": "✅ Configuración cargada",
    "CONNECTION_OK": "✅ Conexión establecida"
}

# === LOG FORMATS ===
LOG_FORMATS = {
    "SIMPLE": "%(levelname)s - %(message)s",
    "DETAILED": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "DEBUG": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
}

# === REGEX PATTERNS ===
PATTERNS = {
    "NOTION_PAGE_ID": r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    "NOTION_DB_ID": r"^[a-f0-9]{32}$",
    "TELEGRAM_USER_ID": r"^\d{5,10}$"
}

# === TIMEOUTS ===
TIMEOUTS = {
    "NOTION_API": 30,  # segundos
    "GEMINI_API": 60,  # segundos
    "TELEGRAM_API": 30  # segundos
}

# === CACHE SETTINGS ===
CACHE_SETTINGS = {
    "PROYECTOS_TTL": 300,  # 5 minutos
    "TAREAS_TTL": 60,      # 1 minuto
    "USER_CONTEXT_TTL": 1800  # 30 minutos
}