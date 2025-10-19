# ELiaS - Asistente Inteligente de Gestión

**E**ficiente **L**ogística **i**nteligente **a**sistida por **S**istemas

Sistema inteligente de gestión de tareas que integra Notion, Gemini AI y Telegram para una experiencia de productividad completa.

## 🚀 Características

- 🤖 **Bot de Telegram**: Interfaz conversacional intuitiva
- 📊 **Integración Notion**: Gestión automática de tareas y proyectos
- 🧠 **IA Gemini**: Procesamiento de lenguaje natural avanzado
- 📱 **Multiplataforma**: Funciona en Windows, Linux y macOS
- 🔒 **Seguro**: Configuración de administradores y permisos

## 📁 Estructura del Proyecto

```
ELiaS/
├── run_tests.py              # Ejecutor de tests (conveniencia)
├── telegram_bot.py           # Launcher del bot de Telegram
├── config/                   # Configuración del sistema
│   └── settings.py
├── notion/                   # Integración con Notion
│   ├── models/              # Modelos de datos
│   ├── services/            # Servicios de Notion
│   └── utils/               # Utilidades
├── ia/                      # Servicios de Inteligencia Artificial
│   └── services/            # Gemini, LangGraph, etc.
├── telegram_bot/            # Módulo del bot de Telegram
│   ├── bot.py              # Clase principal del bot
│   ├── handlers/           # Manejadores de comandos y mensajes
│   └── keyboards.py        # Teclados inline personalizados
└── tests/                  # Suite completa de tests
    ├── run_all_tests.py    # Ejecutor principal
    ├── test_conexion.py    # Tests básicos
    ├── test_notion_fix.py  # Tests de Notion
    └── test_telegram_bot.py # Tests del bot
```

## ⚙️ Configuración Rápida

### 1. Clonar y Configurar Entorno

```bash
git clone <repository-url>
cd ELiaS
python -m venv elias-env
source elias-env/bin/activate  # Linux/Mac
# o
elias-env\Scripts\activate     # Windows
```

### 2. Instalar Dependencias

```bash
pip install -r requirements_telegram.txt
```

### 3. Configurar Variables de Entorno

Crear archivo `.env` en la raíz:

```env
# Bot de Telegram
TELEGRAM_BOT_TOKEN=tu_token_del_bot
TELEGRAM_ADMIN_IDS=123456789

# Notion
NOTION_TOKEN=tu_notion_token
NOTION_TAREAS_DB_ID=id_base_datos_tareas
NOTION_PROYECTOS_DB_ID=id_base_datos_proyectos

# Gemini AI
GOOGLE_API_KEY=tu_google_api_key
```

### 4. Verificar Instalación

```bash
# Ejecutar todos los tests
python run_tests.py

# O tests específicos
python run_tests.py conexion
python run_tests.py telegram
```

### 5. Iniciar el Bot

```bash
python telegram_bot.py
```

## 🧪 Testing

El sistema incluye una suite completa de tests organizados en el módulo `tests/`:

### Ejecutar Todos los Tests
```bash
python run_tests.py
```

### Tests Específicos
```bash
python run_tests.py conexion    # Test básico de conectividad
python run_tests.py notion      # Tests del sistema Notion  
python run_tests.py telegram    # Tests completos del bot
python run_tests.py verificar   # Verificación final
```

### Tests Individuales
```bash
python tests/test_conexion.py
python tests/test_notion_fix.py  
python tests/test_telegram_bot.py
python tests/verificar_bot_completo.py
```

## 📱 Uso del Bot de Telegram

Una vez configurado e iniciado:

1. **Busca tu bot** en Telegram usando el nombre que le diste
2. **Inicia conversación** con `/start`
3. **Usa comandos naturales**:
   - "¿Cuántas tareas tengo?"
   - "Crear tarea: estudiar matemáticas"
   - "Mis proyectos"
   - "Tareas pendientes"

### Funcionalidades Disponibles

- ✅ **Gestión de Tareas**: Crear, consultar, actualizar
- 📁 **Proyectos**: Listar y gestionar proyectos
- 📊 **Estadísticas**: Resúmenes y métricas
- 🎯 **Panel de Admin**: Funciones administrativas
- 💬 **Lenguaje Natural**: Consultas conversacionales

## 🔧 Solución de Problemas

### Bot no responde
```bash
# Verificar configuración
python tests/test_conexion.py

# Verificar permisos del bot
python tests/verificar_bot_completo.py
```

### Error de Notion
```bash
# Probar conexión a Notion
python tests/test_notion_fix.py
```

### Problemas de Dependencias
```bash
# Reinstalar dependencias
pip install -r requirements_telegram.txt --upgrade
```

## 🛠️ Desarrollo

### Agregar Nuevas Funcionalidades

1. **Comandos de Telegram**: Editar `telegram_bot/handlers/`
2. **Servicios de Notion**: Editar `notion/services/`
3. **IA y Procesamiento**: Editar `ia/services/`

### Ejecutar en Desarrollo

```bash
# Con logs detallados
python telegram_bot.py

# Solo tests
python run_tests.py
```

### Contribuir

1. Fork del repositorio
2. Crear rama para feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📚 Documentación por Módulos

Cada módulo tiene su propia documentación detallada:

- ⚙️ [**config/**](config/README.md) - Configuración del sistema y variables de entorno
- 📊 [**notion/**](notion/README.md) - Integración con Notion API y gestión de datos
- 🤖 [**ia/**](ia/README.md) - Servicios de IA (Gemini, LangChain, LangGraph)
- 💬 [**telegram_bot/**](telegram_bot/README.md) - Bot de Telegram y handlers
- 🧪 [**tests/**](tests/README.md) - Suite completa de testing y verificación

### Guías Adicionales

- 📖 [Guía del Bot de Telegram](TELEGRAM_BOT_README.md) - Tutorial completo del bot
- 🚀 [Configuración Rápida](config/README.md#configuración-rápida) - Setup en 5 minutos

## 🤝 Soporte

¿Problemas o preguntas?

1. **Revisa los tests**: `python run_tests.py`
2. **Consulta logs**: `telegram_bot.log`
3. **Verifica configuración**: Archivo `.env`

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para detalles.

---

**ELiaS** - Haciendo la gestión de tareas más inteligente, una conversación a la vez. 🤖✨