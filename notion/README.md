# Notion - Módulo de Integración con Notion

Este módulo proporciona una interfaz completa para interactuar with Notion, incluyendo gestión de tareas, proyectos y sincronización de datos.

## 📁 Estructura

```
notion/
├── __init__.py              # Inicialización y exports principales
├── README.md               # Esta documentación
├── models.py               # Modelos de datos (Tarea, Proyecto)
├── models/                 # Modelos específicos
│   ├── __init__.py
│   ├── tarea.py           # Modelo Tarea
│   └── proyecto.py        # Modelo Proyecto
├── services/              # Servicios de negocio
│   ├── __init__.py
│   ├── tareas_service.py  # Gestión de tareas
│   └── proyectos_service.py # Gestión de proyectos
└── utils/                 # Utilidades y helpers
    ├── __init__.py
    ├── notion_client.py   # Cliente base de Notion
    └── notion_helpers.py  # Funciones auxiliares
```

## 🚀 Inicio Rápido

### Configuración

```python
from notion import tareas_service, proyectos_service

# Los servicios se inicializan automáticamente
# usando la configuración del módulo config
```

### Operaciones Básicas

```python
# Obtener todas las tareas
tareas = tareas_service.obtener_todas_las_tareas()

# Crear nueva tarea
nueva_tarea = tareas_service.crear_tarea_desde_texto(
    titulo="Estudiar Python",
    prioridad="Alta",
    proyectos=["Programación"]
)

# Obtener proyectos
proyectos = proyectos_service.cargar_proyectos_como_diccionario()
```

## 📋 Modelos de Datos

### Clase Tarea

```python
@dataclass
class Tarea:
    """Modelo para una tarea de Notion"""
    # Identificadores
    id: Optional[str] = None
    url: Optional[str] = None
    
    # Propiedades principales
    nombre: str = ""
    descripcion: str = ""
    estado: EstadoTarea = EstadoTarea.SIN_EMPEZAR
    prioridad: PrioridadTarea = PrioridadTarea.MEDIA
    
    # Fechas
    fecha_creacion: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    fecha_completada: Optional[datetime] = None
    
    # Relaciones
    proyecto_ids: List[str] = field(default_factory=list)
```

### Enums Disponibles

```python
class EstadoTarea(Enum):
    SIN_EMPEZAR = "Sin empezar"
    EN_CURSO = "En curso"
    COMPLETADO = "Completado"

class PrioridadTarea(Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"
    URGENTE = "Urgente"
```

## 🔧 Servicios Disponibles

### TareasService

#### Métodos Principales

```python
# Obtener tareas
tareas = tareas_service.obtener_todas_las_tareas()
tarea = tareas_service.obtener_tarea(tarea_id)

# Crear tareas
tarea = tareas_service.crear_tarea(tarea_objeto)
tarea = tareas_service.crear_tarea_desde_texto(
    titulo="Mi tarea",
    prioridad="Media",
    fecha="2024-12-31",
    proyectos=["Proyecto1"]
)

# Actualizar tareas
tarea_actualizada = tareas_service.actualizar_tarea(tarea_id, nuevos_datos)

# Buscar tareas
tareas_filtradas = tareas_service.buscar_tareas_por_estado(EstadoTarea.SIN_EMPEZAR)
```

#### Filtros y Búsquedas

```python
# Por estado
pendientes = tareas_service.buscar_tareas_por_estado(EstadoTarea.SIN_EMPEZAR)

# Por prioridad
urgentes = tareas_service.buscar_tareas_por_prioridad(PrioridadTarea.URGENTE)

# Por proyecto
del_proyecto = tareas_service.buscar_tareas_por_proyecto("Mi Proyecto")

# Búsqueda de texto
encontradas = tareas_service.buscar_tareas("palabra clave")
```

### ProyectosService

#### Métodos Principales

```python
# Obtener proyectos
proyectos_dict = proyectos_service.cargar_proyectos_como_diccionario()
proyecto = proyectos_service.obtener_proyecto(proyecto_id)

# Crear proyecto
nuevo_proyecto = proyectos_service.crear_proyecto(
    nombre="Mi Proyecto",
    descripcion="Descripción del proyecto"
)

# Estadísticas
stats = proyectos_service.obtener_estadisticas_proyecto(proyecto_id)
```

## 💡 Ejemplos de Uso

### Crear y Gestionar Tareas

```python
from notion import tareas_service
from notion.models import EstadoTarea, PrioridadTarea

# Crear tarea simple
tarea = tareas_service.crear_tarea_desde_texto(
    titulo="Revisar documentación",
    prioridad="Media"
)

# Crear tarea completa
tarea_completa = tareas_service.crear_tarea_desde_texto(
    titulo="Implementar feature",
    prioridad="Alta",
    fecha="2024-12-15",
    proyectos=["Desarrollo", "Q4 2024"]
)

# Obtener tareas pendientes
pendientes = tareas_service.buscar_tareas_por_estado(EstadoTarea.SIN_EMPEZAR)
print(f"Tienes {len(pendientes)} tareas pendientes")

# Buscar tareas urgentes
urgentes = tareas_service.buscar_tareas_por_prioridad(PrioridadTarea.URGENTE)
for tarea in urgentes:
    print(f"🔥 URGENTE: {tarea.nombre}")
```

### Trabajar con Proyectos

```python
from notion import proyectos_service

# Obtener todos los proyectos
proyectos = proyectos_service.cargar_proyectos_como_diccionario()

# Listar proyectos
for nombre, proyecto in proyectos.items():
    print(f"📁 {nombre}: {proyecto.descripcion}")

# Obtener estadísticas de un proyecto
if "Mi Proyecto" in proyectos:
    stats = proyectos_service.obtener_estadisticas_proyecto(
        proyectos["Mi Proyecto"].id
    )
    print(f"Tareas completadas: {stats.get('completadas', 0)}")
```

### Integración con Telegram Bot

```python
async def handle_crear_tarea(update, context):
    """Handler para crear tareas desde Telegram"""
    mensaje = update.message.text
    
    # Extraer información del mensaje
    if mensaje.startswith("crear tarea:"):
        titulo = mensaje.replace("crear tarea:", "").strip()
        
        # Crear la tarea
        tarea = tareas_service.crear_tarea_desde_texto(
            titulo=titulo,
            prioridad="Media"
        )
        
        if tarea:
            await update.message.reply_text(
                f"✅ Tarea creada: {tarea.nombre}\n"
                f"🔗 [Ver en Notion]({tarea.url})"
            )
        else:
            await update.message.reply_text("❌ Error creando la tarea")
```

## 🔍 Debugging y Logging

### Habilitar Logs Detallados

```python
import logging

# Configurar logging para Notion
logging.getLogger('notion').setLevel(logging.DEBUG)

# Ver requests HTTP a Notion API
logging.getLogger('httpx').setLevel(logging.INFO)
```

### Verificar Conexión

```python
from notion.utils.notion_client import notion_client

# Test básico de conexión
try:
    user = notion_client.users.me()
    print(f"✅ Conectado como: {user.get('name', 'Usuario')}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
```

## 🧪 Testing

### Ejecutar Tests del Módulo

```bash
# Test específico de Notion
python tests/test_notion_fix.py

# O desde el ejecutor principal
python run_tests.py notion
```

### Tests Disponibles

- ✅ **Creación de objetos**: Verificar modelos de datos
- ✅ **Conexión API**: Test de conectividad con Notion
- ✅ **Servicios**: Validar funcionamiento de TareasService
- ✅ **CRUD completo**: Crear, leer, actualizar tareas

## ⚠️ Limitaciones y Consideraciones

### Límites de API

- **Rate Limits**: Notion API tiene límites de requests por segundo
- **Paginación**: Bases de datos grandes requieren paginación
- **Timeouts**: Requests pueden fallar por timeout en conexiones lentas

### Manejo de Errores

```python
try:
    tareas = tareas_service.obtener_todas_las_tareas()
except NotionAPIError as e:
    print(f"Error de API: {e}")
except ConnectionError as e:
    print(f"Error de conexión: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
```

## 🔧 Configuración Avanzada

### Variables de Entorno Opcionales

```env
# Timeouts personalizados
NOTION_REQUEST_TIMEOUT=30
NOTION_MAX_RETRIES=3

# Configuración de cache
ENABLE_NOTION_CACHE=True
CACHE_TTL_SECONDS=300

# Logging
NOTION_LOG_LEVEL=INFO
ENABLE_API_LOGGING=False
```

### Personalizar Cliente

```python
from notion.utils.notion_client import NotionClient

# Cliente personalizado
cliente = NotionClient(
    token="tu_token",
    timeout=60,
    max_retries=5
)
```

## 📚 Referencias Útiles

- [Notion API Documentation](https://developers.notion.com/)
- [Notion Python SDK](https://github.com/ramnes/notion-sdk-py)
- [Notion Database Properties](https://developers.notion.com/reference/property-object)
- [API Rate Limits](https://developers.notion.com/reference/request-limits)

## 🤝 Contribuir

### Agregar Nueva Funcionalidad

1. Crear modelo en `models/` si es necesario
2. Implementar servicio en `services/`
3. Agregar tests correspondientes
4. Actualizar documentación

### Reportar Bugs

1. Ejecutar tests: `python tests/test_notion_fix.py`
2. Incluir logs de error
3. Especificar configuración de Notion utilizada

---

**Integración robusta con Notion para gestión inteligente de datos** 📊✨