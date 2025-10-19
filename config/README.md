# Config - Módulo de Configuración

Este módulo centraliza toda la configuración del sistema ELiaS, incluyendo variables de entorno, configuración de APIs y parámetros del sistema.

## 📁 Estructura

```
config/
├── __init__.py           # Inicialización del módulo
├── README.md            # Esta documentación
└── settings.py          # Configuración principal del sistema
```

## ⚙️ Configuración Principal

### Variables de Entorno Requeridas

Crear archivo `.env` en la raíz del proyecto:

```env
# Bot de Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_IDS=123456789,987654321

# Notion API
NOTION_TOKEN=your_notion_integration_token
NOTION_TAREAS_DB_ID=your_tasks_database_id
NOTION_PROYECTOS_DB_ID=your_projects_database_id

# Google Gemini AI
GOOGLE_API_KEY=your_google_ai_api_key
```

### Variables Opcionales

```env
# Configuración del modelo IA (opcional)
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.0
GEMINI_MAX_TOKENS=100000

# Configuración de logging (opcional)
LOG_LEVEL=INFO
LOG_FILE=elias.log

# Configuración de desarrollo (opcional)
DEBUG_MODE=False
ENABLE_VERBOSE_LOGGING=False
```

## 🔧 Uso del Módulo

### Importar Configuración

```python
from config import settings

# Acceder a configuraciones
token = settings.TELEGRAM_BOT_TOKEN
notion_token = settings.NOTION_TOKEN
api_key = settings.GOOGLE_API_KEY
```

### Validar Configuración

```python
from config.settings import validar_configuracion

# Verificar que todas las variables estén configuradas
if validar_configuracion():
    print("✅ Configuración válida")
else:
    print("❌ Faltan configuraciones")
```

## 📋 Configuraciones Disponibles

### Telegram

| Variable | Tipo | Requerido | Descripción |
|----------|------|-----------|-------------|
| `TELEGRAM_BOT_TOKEN` | str | ✅ | Token del bot obtenido de @BotFather |
| `TELEGRAM_ADMIN_IDS` | list[int] | ✅ | IDs de usuarios administradores |

### Notion

| Variable | Tipo | Requerido | Descripción |
|----------|------|-----------|-------------|
| `NOTION_TOKEN` | str | ✅ | Token de integración de Notion |
| `NOTION_TAREAS_DB_ID` | str | ✅ | ID de la base de datos de tareas |
| `NOTION_PROYECTOS_DB_ID` | str | ✅ | ID de la base de datos de proyectos |

### Google AI

| Variable | Tipo | Requerido | Descripción |
|----------|------|-----------|-------------|
| `GOOGLE_API_KEY` | str | ✅ | API Key de Google AI Studio |
| `GEMINI_MODEL` | str | ❌ | Modelo a usar (default: gemini-2.0-flash) |
| `GEMINI_TEMPERATURE` | float | ❌ | Temperatura del modelo (default: 0.0) |
| `GEMINI_MAX_TOKENS` | int | ❌ | Máx. tokens por respuesta (default: 100000) |

## 🚀 Configuración Rápida

### 1. Configurar Bot de Telegram

1. Habla con [@BotFather](https://t.me/botfather)
2. Crea un nuevo bot con `/newbot`
3. Copia el token en `TELEGRAM_BOT_TOKEN`
4. Obtén tu ID de usuario y agrégalo a `TELEGRAM_ADMIN_IDS`

### 2. Configurar Notion

1. Ve a [Notion Integrations](https://www.notion.so/my-integrations)
2. Crea una nueva integración
3. Copia el token en `NOTION_TOKEN`
4. Comparte tus bases de datos con la integración
5. Copia los IDs de las bases de datos

### 3. Configurar Google AI

1. Ve a [Google AI Studio](https://aistudio.google.com/)
2. Crea una API key
3. Cópiala en `GOOGLE_API_KEY`

## 🔍 Validación y Testing

### Verificar Configuración

```python
# Test básico de configuración
from config import settings

print(f"Bot Token: {'✅ Configurado' if settings.TELEGRAM_BOT_TOKEN else '❌ Faltante'}")
print(f"Notion: {'✅ Configurado' if settings.NOTION_TOKEN else '❌ Faltante'}")
print(f"Gemini: {'✅ Configurado' if settings.GOOGLE_API_KEY else '❌ Faltante'}")
```

### Ejecutar Tests

```bash
# Desde la raíz del proyecto
python tests/test_conexion.py
```

## ⚠️ Seguridad

### Buenas Prácticas

- ✅ **Nunca** commitear el archivo `.env` al repositorio
- ✅ Usar variables de entorno en producción
- ✅ Rotar tokens periódicamente
- ✅ Limitar permisos de las integraciones

### Archivo .gitignore

Asegúrate de tener en `.gitignore`:

```gitignore
# Variables de entorno
.env
.env.local
.env.production

# Logs
*.log
```

## 🛠️ Troubleshooting

### Error: "No se pudo cargar .env"

```bash
# Verificar que existe el archivo
ls -la .env

# Crear si no existe
cp .env.example .env
```

### Error: "Variable no configurada"

1. Verificar ortografía en `.env`
2. Reiniciar aplicación después de cambios
3. Verificar que no haya espacios extra

### Error: "Token inválido"

1. Regenerar token en la plataforma correspondiente
2. Verificar que el token no tenga espacios
3. Confirmar permisos de la integración

## 📚 Referencias

- [Python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [Notion API Documentation](https://developers.notion.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Google AI Documentation](https://ai.google.dev/docs)

---

**Configuración centralizada para un sistema robusto** 🔧✨