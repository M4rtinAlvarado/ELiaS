# 📊 Notion - Módulo de Integración con Notion

Este módulo proporciona una interfaz completa para interactuar con Notion, incluyendo gestión de **tareas**, **eventos** y **proyectos** con sincronización bidireccional.

## 📁 Estructura

```
notion/
├── __init__.py              # Inicialización y exports principales
├── README.md                # Esta documentación
├── models.py                # Modelos de datos (Tarea, Proyecto, Evento)
├── services/                # Servicios de negocio
│   ├── __init__.py
│   ├── tareas_service.py    # Gestión de tareas
│   ├── proyectos_service.py # Gestión de proyectos
│   └── eventos_service.py   # Gestión de eventos (NEW)
└── utils/                   # Utilidades y helpers
    ├── __init__.py
    ├── notion_client.py     # Cliente base de Notion
    └── notion_helpers.py    # Funciones auxiliares
```

## 🚀 Inicio Rápido

### Configuración

```python
from notion import tareas_service, proyectos_service, eventos_service

# Los servicios se inicializan automáticamente
# usando la configuración del módulo config
```

### Operaciones con Tareas

```python
# Obtener todas las tareas
tareas = tareas_service.obtener_todas_las_tareas()

# Crear nueva tarea con tiempo estimado
nueva_tarea = tareas_service.crear_tarea_desde_texto(
    titulo="Estudiar Python",
    prioridad="Alta",
    tiempo_estimado=2.5,  # Horas
    proyectos=["Programación"]
)

# Crear tarea inteligente (extrae datos automáticamente)
tarea = await tareas_service.crear_tarea_inteligente(
    "Estudiar para el examen de cálculo, es urgente, para el viernes, unas 3 horas"
)
```

### Operaciones con Eventos

```python
# Obtener todos los eventos
eventos = eventos_service.obtener_todos_los_eventos()

# Crear evento con ubicación
evento = eventos_service.crear_evento(
    nombre="Cumpleaños de Juan",
    fecha="2024-12-15",
    tipo="Social",
    ubicacion="Casa de Juan"
)

# Crear evento inteligente (extrae datos automáticamente)
evento = await eventos_service.crear_evento_inteligente(
    "Cena de Navidad el 24 de diciembre a las 8pm en casa de la abuela"
)

# Obtener próximos eventos
proximos = eventos_service.obtener_proximos_eventos(dias=7)

# Eventos de hoy
hoy = eventos_service.obtener_eventos_hoy()
```

### Operaciones con Proyectos

```python
# Obtener proyectos como diccionario
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
    tiempo_estimado: Optional[float] = None  # Horas estimadas
    
    # Fechas
    fecha_creacion: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    fecha_completada: Optional[datetime] = None
    
    # Relaciones
    proyecto_ids: List[str] = field(default_factory=list)
```

### Clase Evento (NEW)

```python
@dataclass
class Evento:
    """Modelo para un evento de Notion"""
    # Identificadores
    id: Optional[str] = None
    url: Optional[str] = None
    
    # Propiedades principales
    nombre: str = ""
    descripcion: str = ""
    estado: EstadoEvento = EstadoEvento.PROGRAMADO
    tipo: TipoEvento = TipoEvento.OTROS
    ubicacion: str = ""
    
    # Fechas
    fecha: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    
    # Relaciones
    proyecto_ids: List[str] = field(default_factory=list)
```

### Enums Disponibles

```python
# Estados de Tarea
class EstadoTarea(Enum):
    SIN_EMPEZAR = "Sin empezar"
    EN_CURSO = "En curso"
    COMPLETADO = "Completado"

# Prioridades de Tarea
class PrioridadTarea(Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"
    URGENTE = "Urgente"

# Estados de Evento
class EstadoEvento(Enum):
    PROGRAMADO = "Programado"
    EN_CURSO = "En curso"
    FINALIZADO = "Finalizado"
    CANCELADO = "Cancelado"

# Tipos de Evento
class TipoEvento(Enum):
    PERSONAL = "Personal"
    TRABAJO = "Trabajo"
    SOCIAL = "Social"
    ACADEMICO = "Académico"
    OTROS = "Otros"
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
    tiempo_estimado=2.5,  # Horas
    proyectos=["Proyecto1"]
)

# Crear tarea inteligente (usa IA)
tarea = await tareas_service.crear_tarea_inteligente(
    "Estudiar para el examen urgente, unas 3 horas para el viernes"
)

# Actualizar tareas
tarea_actualizada = tareas_service.actualizar_tarea(tarea_id, nuevos_datos)

# Buscar tareas
tareas_filtradas = tareas_service.buscar_tareas_por_estado(EstadoTarea.SIN_EMPEZAR)
```

### EventosService (NEW)

#### Métodos Principales

```python
# Obtener eventos
eventos = eventos_service.obtener_todos_los_eventos()
evento = eventos_service.obtener_evento(evento_id)

# Crear eventos
evento = eventos_service.crear_evento(
    nombre="Reunión de equipo",
    fecha="2024-12-15T10:00:00",
    tipo="Trabajo",
    ubicacion="Sala de conferencias"
)

# Crear evento inteligente (usa IA)
evento = await eventos_service.crear_evento_inteligente(
    "Cumpleaños de mamá el 20 de enero en su casa"
)

# Consultar eventos
proximos = eventos_service.obtener_proximos_eventos(dias=7)
hoy = eventos_service.obtener_eventos_hoy()
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