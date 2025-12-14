# 🤖 ELiaS v2.0 - Asistente Inteligente de Gestión

**E**ficiente **L**ogística **i**nteligente **a**sistida por **S**istemas

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Gemini 2.5](https://img.shields.io/badge/Gemini-2.5%20Flash-orange.svg)](https://ai.google.dev/)
[![Notion API](https://img.shields.io/badge/Notion-API%20v1-black.svg)](https://developers.notion.com/)

Sistema inteligente de gestión de **tareas**, **eventos** y **proyectos** que integra Notion, Gemini AI y Telegram para una experiencia de productividad completa.

## ✨ Novedades v2.0

- 📅 **Gestión de Eventos**: Calendario inteligente con fechas, ubicaciones y tipos
- ⏱️ **Tiempo Estimado**: Seguimiento del tiempo en tareas
- 🔄 **Clasificación IA Mejorada**: Distingue automáticamente tareas vs eventos
- 📊 **Sistema de Benchmark**: Pruebas automatizadas de respuestas del bot
- ⚡ **Optimización de Rendimiento**: Caché de respuestas y lazy loading

## 🚀 Características

- 🤖 **Bot de Telegram**: Interfaz conversacional intuitiva con lenguaje natural
- 📊 **Integración Notion**: Gestión automática de tareas, eventos y proyectos
- 🧠 **IA Gemini 2.5 Flash**: Clasificación inteligente de intenciones y extracción de datos
- 🔄 **LangGraph**: Orquestación de flujos de trabajo con máquinas de estado
- 📱 **Multiplataforma**: Funciona en Windows, Linux y macOS
- 🔒 **Seguro**: Configuración de administradores y permisos
- 🧪 **Bien Testeado**: Suite completa de tests y benchmarks

## 📁 Estructura del Proyecto

```
ELiaS/
├── main.py                   # Punto de entrada principal
├── run_tests.py              # Ejecutor de tests (conveniencia)
├── telegram_bot.py           # Launcher del bot de Telegram
├── config/                   # 🔧 Configuración del sistema
│   └── settings.py           # Variables de entorno y parámetros
├── notion/                   # 📊 Integración con Notion
│   ├── models.py             # Tarea, Proyecto, Evento
│   └── services/             # CRUD de datos
│       ├── tareas_service.py
│       ├── proyectos_service.py
│       └── eventos_service.py
├── ia/                       # 🧠 Inteligencia Artificial
│   ├── models.py             # Prompts y templates
│   └── services/
│       ├── gemini_service.py # Google Gemini 2.5 Flash
│       └── langgraph_service.py # LangGraph workflows
├── telegram_bot/             # 🤖 Bot de Telegram
│   ├── bot.py                # Clase principal EliasBot
│   ├── keyboards.py          # Teclados inline
│   └── handlers/             # Comandos y mensajes
└── tests/                    # 🧪 Suite de pruebas
    ├── benchmark_bot.py      # Banco de pruebas del bot
    ├── run_all_tests.py      # Ejecutor principal
    └── test_*.py             # Tests unitarios
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
NOTION_EVENTOS_DB_ID=id_base_datos_eventos

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

### Benchmark del Bot
```bash
# Ejecutar benchmark completo con banco de 39 preguntas
python tests/benchmark_bot.py

# Ejecutar categoría específica
python tests/benchmark_bot.py --categoria crear_tarea
python tests/benchmark_bot.py --categoria crear_evento
python tests/benchmark_bot.py --categoria consultar

# Guardar resultados en JSON
python tests/benchmark_bot.py --output resultados.json
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
   - "Agregar evento: cumpleaños de mamá el 15 de mayo"
   - "Mis proyectos"
   - "Tareas pendientes"
   - "Próximos eventos"

### Funcionalidades Disponibles

- ✅ **Gestión de Tareas**: Crear, consultar con prioridad, tiempo estimado y fechas
- 📅 **Gestión de Eventos**: Crear eventos con fecha, ubicación y tipo
- 📁 **Proyectos**: Listar y gestionar proyectos
- 📊 **Estadísticas**: Resúmenes, métricas y optimización
- 🎯 **Panel de Admin**: Funciones administrativas
- 💬 **Lenguaje Natural**: Consultas conversacionales inteligentes

### Clasificación Inteligente de Intenciones

ELiaS usa Gemini 2.5 Flash para clasificar automáticamente tus mensajes:

| Intención | Descripción | Ejemplo |
|-----------|-------------|---------|
| `CREAR_TAREA` | Acciones que DEBES hacer | "Estudiar para el examen" |
| `CREAR_EVENTO` | Ocasiones a las que ASISTES | "Cumpleaños de Juan el sábado" |
| `CONSULTAR` | Preguntas sobre tus datos | "¿Cuántas tareas pendientes tengo?" |
| `AMBIGUO` | Requiere más contexto | "Python" |

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
4. **Nuevas Intenciones**: Actualizar prompt en `ia/models.py`

### Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │───▶│  LangGraph Flow  │───▶│   Notion API    │
│   (Interface)   │    │  (Orchestrator)  │    │   (Database)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Gemini 2.5 AI   │
                       │ (Classification) │
                       └──────────────────┘
```

### Flujo de Clasificación de Intenciones

```
Usuario envía mensaje
        │
        ▼
┌───────────────────┐
│ clasificar_intent │ ◀── Gemini analiza el texto
└───────────────────┘
        │
        ├─── CREAR_TAREA ──▶ Extrae datos y crea en Notion
        ├─── CREAR_EVENTO ─▶ Extrae datos y crea evento
        ├─── CONSULTAR ────▶ Busca información y responde
        └─── AMBIGUO ──────▶ Solicita más contexto
```

### Ejecutar en Desarrollo

```bash
# Con logs detallados
python telegram_bot.py

# Solo tests
python run_tests.py

# Benchmark para evaluar cambios
python tests/benchmark_bot.py
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
- 📊 [**notion/**](notion/README.md) - Integración con Notion API (Tareas, Eventos, Proyectos)
- 🤖 [**ia/**](ia/README.md) - Servicios de IA (Gemini 2.5, LangGraph)
- 💬 [**telegram_bot/**](telegram_bot/README.md) - Bot de Telegram y handlers
- 🧪 [**tests/**](tests/README.md) - Suite completa de testing y benchmarks

## 📊 Bases de Datos Notion

### Tareas
| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| Nombre | title | Título de la tarea |
| Prioridad | select | Baja, Media, Alta, Urgente |
| Fecha | date | Fecha de vencimiento |
| Estado | status | Sin empezar, En curso, Completado |
| Tiempo Estimado | number | Horas estimadas |
| Proyectos | relation | Relación con base de proyectos |

### Eventos
| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| Nombre | title | Título del evento |
| Fecha | date | Fecha y hora del evento |
| Estado | status | Programado, En curso, Finalizado, Cancelado |
| Tipo | select | Personal, Trabajo, Social, Académico, Otros |
| Ubicación | rich_text | Lugar del evento |
| Proyectos | relation | Relación con proyectos |

### Guías Adicionales

- 📖 [Guía del Bot de Telegram](TELEGRAM_BOT_README.md) - Tutorial completo del bot
- 🚀 [Configuración Rápida](config/README.md#configuración-rápida) - Setup en 5 minutos

## 🤝 Soporte

¿Problemas o preguntas?

1. **Revisa los tests**: `python run_tests.py`
2. **Ejecuta benchmark**: `python tests/benchmark_bot.py`
3. **Consulta logs**: `telegram_bot.log`
4. **Verifica configuración**: Archivo `.env`

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para detalles.

---

<div align="center">

**ELiaS v2.0** - Haciendo la gestión de tareas y eventos más inteligente, una conversación a la vez. 🤖✨

*Desarrollado con ❤️ usando Python, Gemini AI, Notion y Telegram*

</div>