# 🧠 IA - Módulo de Inteligencia Artificial

Este módulo integra servicios de IA avanzada usando **Google Gemini 2.5 Flash** y **LangGraph** para clasificación de intenciones, extracción de datos y orquestación de flujos de trabajo.

## 📁 Estructura

```
ia/
├── __init__.py              # Inicialización del módulo
├── README.md                # Esta documentación
├── models.py                # Prompts y templates de IA
└── services/                # Servicios de IA
    ├── __init__.py
    ├── gemini_service.py    # Servicio Google Gemini 2.5 Flash
    └── langgraph_service.py # Servicio LangGraph con estado
```

## 🚀 Inicio Rápido

### Importar Servicios

```python
from ia.services import gemini_service
from ia.services.langgraph_service import LangGraphService
from ia.models import Prompt

# Clasificar intención del usuario
intencion = await gemini_service.clasificar_intencion(
    "Crear tarea urgente: revisar código"
)
# Resultado: "CREAR_TAREA"

# Usar LangGraph para flujos complejos
langgraph = LangGraphService()
resultado = await langgraph.procesar_mensaje("Agregar evento: cumpleaños de Juan mañana")
```

## 🎯 Sistema de Clasificación de Intenciones

ELiaS usa un sistema de 4 intenciones para clasificar mensajes:

| Intención | Descripción | Ejemplos |
|-----------|-------------|----------|
| `CREAR_TAREA` | Acciones que el usuario DEBE hacer | "Estudiar Python", "Terminar el informe" |
| `CREAR_EVENTO` | Ocasiones a las que ASISTE | "Cumpleaños de Juan", "Reunión del equipo" |
| `CONSULTAR` | Preguntas sobre datos existentes | "¿Cuántas tareas tengo?", "Mis eventos de hoy" |
| `AMBIGUO` | Requiere más contexto | "Python", "Mañana" |

### Criterios de Clasificación

```
CREAR_TAREA: Acciones personales que requieren ESFUERZO
  ✓ Estudiar, Trabajar, Revisar, Completar, Hacer

CREAR_EVENTO: Ocasiones sociales/programadas que ASISTES
  ✓ Cumpleaños, Reuniones, Citas, Fiestas, Conferencias

CONSULTAR: Preguntas sobre información existente
  ✓ Palabras interrogativas: cuántas, cuáles, qué, lista
```

## 🤖 Servicios Disponibles

### GeminiService

Servicio principal de IA usando Google Gemini 2.5 Flash para clasificación y extracción de datos.

#### Configuración

```python
from ia.services.gemini_service import GeminiService

# Inicialización automática con configuración del sistema
service = GeminiService()

# O configuración personalizada
service = GeminiService(
    model="gemini-2.5-flash",
    temperature=0.0,
    max_tokens=100000
)
```

#### Métodos Principales

```python
# Clasificar intención del mensaje
intencion = await service.clasificar_intencion("Estudiar para el examen")
# "CREAR_TAREA"

# Extraer datos de tarea
datos = await service.extraer_datos_tarea(
    "Estudiar cálculo urgente para el viernes, unas 3 horas"
)
# {"nombre": "Estudiar cálculo", "prioridad": "Urgente", "fecha": "viernes", "tiempo_estimado": 3.0}

# Extraer datos de evento
datos = await service.extraer_datos_evento(
    "Cumpleaños de mamá el 15 de mayo en su casa"
)
# {"nombre": "Cumpleaños de mamá", "fecha": "15 de mayo", "ubicacion": "su casa", "tipo": "Social"}

# Generar respuesta a consulta
respuesta = await service.generar_respuesta_consulta(
    pregunta="¿Cuántas tareas pendientes tengo?",
    contexto=lista_tareas
)
```

### LangGraphService

Servicio de orquestación con LangGraph para flujos de trabajo con estado.
# Generar respuesta simple
respuesta = gemini_service.generar_respuesta(
    prompt="Explica qué es una tarea",
    contexto="Sistema de gestión de tareas"
)

# Análisis de texto
analisis = gemini_service.analizar_texto(
    "Crear tarea urgente: revisar código",
    tipo_analisis="extraccion_entidades"
)

# Generar contenido estructurado
contenido = gemini_service.generar_contenido_estructurado(
    template="resumen_tareas",
    datos={"tareas": lista_tareas}
)
```

### LangGraphService

Servicio de orquestación con LangGraph para flujos de trabajo con estado.

#### Arquitectura del Grafo

```
                    ┌─────────────────┐
                    │ clasificar_nodo │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
   │  crear_tarea  │ │ crear_evento  │ │   consultar   │
   └───────────────┘ └───────────────┘ └───────────────┘
           │                 │                 │
           └─────────────────┴─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   responder     │
                    └─────────────────┘
```

#### Uso del Servicio

```python
from ia.services.langgraph_service import LangGraphService

# Inicializar
langgraph = LangGraphService()

# Procesar mensaje (clasifica y ejecuta automáticamente)
resultado = await langgraph.procesar_mensaje(
    "Crear tarea urgente: revisar código para el viernes"
)

# El grafo automáticamente:
# 1. Clasifica la intención → CREAR_TAREA
# 2. Extrae datos (nombre, prioridad, fecha, tiempo_estimado)
# 3. Crea la tarea en Notion
# 4. Genera respuesta formateada
```

#### Nodos Disponibles

| Nodo | Función | Salida |
|------|---------|--------|
| `nodo_clasificar` | Clasifica intención con Gemini | Intención detectada |
| `nodo_crear_tarea` | Extrae datos y crea tarea | Tarea creada |
| `nodo_crear_evento` | Extrae datos y crea evento | Evento creado |
| `nodo_consultar` | Busca información y responde | Respuesta formateada |
| `nodo_pedir_clarificacion` | Solicita más contexto | Pregunta de clarificación |

## 💡 Ejemplos de Uso

### Análisis de Mensajes de Usuario

```python
def procesar_mensaje_usuario(mensaje: str) -> dict:
    """Analizar mensaje del usuario y extraer intención"""
    
    # Usar Gemini para análisis
    prompt = f"""
    Analiza este mensaje del usuario y extrae:
    1. Intención (crear_tarea, consultar_tareas, etc.)
    2. Entidades mencionadas (fechas, prioridades, proyectos)
    3. Parámetros para la acción
    
    Mensaje: "{mensaje}"
    
    Responde en formato JSON.
    """
    
    respuesta = gemini_service.generar_respuesta(prompt)
    return json.loads(respuesta)

# Ejemplo de uso
resultado = procesar_mensaje_usuario(
    "Crear una tarea urgente para revisar el código del proyecto web antes del viernes"
)
# Resultado: {
#     "intencion": "crear_tarea",
#     "entidades": {
#         "prioridad": "urgente",
#         "descripcion": "revisar el código",
#         "proyecto": "proyecto web",
#         "fecha_limite": "viernes"
#     }
# }
```

### Generación de Resúmenes Inteligentes

```python
def generar_resumen_tareas(tareas: list) -> str:
    """Generar resumen inteligente de tareas"""
    
    # Preparar contexto
    contexto_tareas = "\n".join([
        f"- {t.nombre} (Prioridad: {t.prioridad}, Estado: {t.estado})"
        for t in tareas
    ])
    
    prompt = f"""
    Genera un resumen ejecutivo de estas tareas:
    
    {contexto_tareas}
    
    Incluye:
    - Estadísticas generales
    - Tareas más urgentes
    - Recomendaciones de priorización
    
    Usa emojis para hacerlo más visual.
    """
    
    return gemini_service.generar_respuesta(prompt)

# Uso en bot de Telegram
async def comando_resumen(update, context):
    tareas = tareas_service.obtener_todas_las_tareas()
    resumen = generar_resumen_tareas(tareas)
    await update.message.reply_text(resumen)
```

### Asistente Conversacional

```python
class AsistenteIA:
    """Asistente conversacional inteligente"""
    
    def __init__(self):
        self.historial = []
        
    def procesar_conversacion(self, mensaje_usuario: str) -> str:
        """Procesar mensaje en contexto conversacional"""
        
        # Agregar al historial
        self.historial.append(f"Usuario: {mensaje_usuario}")
        
        # Construir contexto completo
        contexto = "\n".join(self.historial[-5:])  # Últimos 5 mensajes
        
        prompt = f"""
        Eres ELiaS, un asistente inteligente para gestión de tareas.
        
        Contexto de la conversación:
        {contexto}
        
        Responde de manera natural y útil. Si el usuario quiere:
        - Crear tareas: pide los detalles necesarios
        - Consultar información: proporciona datos claros
        - Ayuda: explica las funcionalidades disponibles
        
        Asistente:
        """
        
        respuesta = gemini_service.generar_respuesta(prompt)
        self.historial.append(f"Asistente: {respuesta}")
        
        return respuesta

# Uso en handlers de Telegram
asistente = AsistenteIA()

async def handle_mensaje_natural(update, context):
    mensaje = update.message.text
    respuesta = asistente.procesar_conversacion(mensaje)
    await update.message.reply_text(respuesta)
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```env
# Gemini AI (requerido)
GOOGLE_API_KEY=your_api_key_here

# Configuración del modelo (opcional)
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.0
GEMINI_MAX_TOKENS=100000

# LangChain (opcional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key

# Configuración de cache (opcional)
ENABLE_AI_CACHE=true
AI_CACHE_TTL=3600
```

### Personalización de Modelos

```python
# Configurar Gemini personalizado
from ia.services.gemini_service import GeminiService

gemini_custom = GeminiService(
    model="gemini-2.0-flash",
    temperature=0.7,  # Más creativo
    max_tokens=50000,
    safety_settings={
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE"
    }
)
```

## 🧪 Testing y Debugging

### Verificar Servicios de IA

```python
# Test básico de Gemini
def test_gemini():
    try:
        respuesta = gemini_service.generar_respuesta("Hola, ¿funcionas?")
        print(f"✅ Gemini funciona: {respuesta}")
        return True
    except Exception as e:
        print(f"❌ Error en Gemini: {e}")
        return False

# Test de LangGraph (opcional)
def test_langgraph():
    try:
        from ia.services.langgraph_service import LangGraphService
        service = LangGraphService()
        print("✅ LangGraph disponible")
        return True
    except ImportError:
        print("⚠️ LangGraph no instalado")
        return False
```

### Ejecutar Tests

```bash
# Test específico de IA
python -c "from ia.services import gemini_service; print(gemini_service.generar_respuesta('Test'))"

# Tests completos del sistema
python run_tests.py telegram  # Incluye tests de IA
```

## 📊 Monitoreo y Logging

### Habilitar Logs Detallados

```python
import logging

# Configurar logging para IA
logging.getLogger('ia').setLevel(logging.DEBUG)
logging.getLogger('google.generativeai').setLevel(logging.INFO)

# Logs de requests a APIs
logging.getLogger('httpx').setLevel(logging.INFO)
```

### Métricas de Uso

```python
from ia.services.gemini_service import get_usage_stats

# Obtener estadísticas de uso
stats = get_usage_stats()
print(f"Tokens usados hoy: {stats.get('tokens_used', 0)}")
print(f"Requests realizados: {stats.get('requests_count', 0)}")
```

## ⚠️ Limitaciones y Consideraciones

### Límites de API

- **Gemini API**: Límites de requests por minuto y por día
- **Tokens**: Límite de tokens por request y por mes
- **Rate Limiting**: Implementar retry logic para requests fallidos

### Costos

- **Gemini**: Facturado por tokens de entrada y salida
- **LangChain**: Algunos servicios pueden tener costos adicionales
- **Monitoreo**: Importante trackear uso para controlar costos

### Fallbacks y Robustez

```python
def generar_respuesta_robusta(prompt: str) -> str:
    """Generar respuesta with fallbacks"""
    
    try:
        # Intentar Gemini primero
        return gemini_service.generar_respuesta(prompt)
    except Exception as e:
        print(f"⚠️ Gemini falló: {e}")
        
        try:
            # Fallback a LangGraph si está disponible
            langgraph = LangGraphService()
            return langgraph.procesar_consulta_simple(prompt)
        except:
            # Último fallback: respuesta genérica
            return "⚠️ Servicio de IA temporalmente no disponible. Intenta más tarde."
```

## 🔒 Seguridad y Privacidad

### Buenas Prácticas

- ✅ No enviar información sensible a APIs externas
- ✅ Filtrar contenido antes de procesarlo
- ✅ Implementar timeouts para evitar requests colgados
- ✅ Validar respuestas de IA antes de usarlas

### Filtrado de Contenido

```python
def es_contenido_seguro(texto: str) -> bool:
    """Verificar que el contenido es seguro para procesar"""
    
    # Lista de patrones a evitar
    patrones_prohibidos = [
        r'password.*[:=]\s*\w+',
        r'token.*[:=]\s*\w+',
        r'api[_-]?key.*[:=]\s*\w+'
    ]
    
    import re
    for patron in patrones_prohibidos:
        if re.search(patron, texto, re.IGNORECASE):
            return False
    
    return True

# Usar en procesamiento
def procesar_mensaje_seguro(mensaje: str) -> str:
    if not es_contenido_seguro(mensaje):
        return "⚠️ No puedo procesar contenido que pueda contener información sensible."
    
    return gemini_service.generar_respuesta(mensaje)
```

## 📚 Referencias

- [Google AI Documentation](https://ai.google.dev/docs)
- [LangChain Documentation](https://docs.langchain.com/)
- [LangGraph Documentation](https://docs.langchain.com/langgraph)
- [Gemini API Reference](https://ai.google.dev/api)

## 🤝 Contribuir

### Agregar Nuevo Servicio de IA

1. Crear archivo en `services/nuevo_servicio.py`
2. Implementar interfaz estándar
3. Agregar tests correspondientes
4. Actualizar documentación

### Optimizar Prompts

1. Crear templates reutilizables
2. A/B testing de diferentes enfoques
3. Métricas de calidad de respuestas
4. Documentar mejores prácticas

---

**Inteligencia artificial avanzada para automatización inteligente** 🤖✨