"""
Modelos de datos para IA
Define estructuras para prompts, respuestas y configuración de modelos
"""
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class TipoPrompt(Enum):
    """Tipos de prompts disponibles"""
    SISTEMA = "sistema"
    USUARIO = "usuario"
    ASISTENTE = "asistente"
    CREAR_TAREA = "crear_tarea"
    CONSULTAR_TAREA = "consultar_tarea"
    CLASIFICAR_INTENCION = "clasificar_intencion"
    EXTRAER_DATOS = "extraer_datos"
    ANALIZAR_TEXTO = "analizar_texto"

class ModeloIA(Enum):
    """Modelos de IA disponibles"""
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"

@dataclass
class ConfiguracionModelo:
    """Configuración para un modelo de IA"""
    modelo: ModeloIA
    temperatura: float = 0.7
    max_tokens: int = 1024
    top_p: float = 0.9
    top_k: int = 40
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario"""
        return {
            'model': self.modelo.value,
            'temperature': self.temperatura,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'top_k': self.top_k
        }
    
    @classmethod
    def from_settings(cls, modelo: str = None) -> 'ConfiguracionModelo':
        """Crea configuración desde settings centralizados"""
        from config import settings
        
        modelo_enum = ModeloIA.GEMINI_PRO
        if modelo:
            try:
                modelo_enum = ModeloIA(modelo)
            except ValueError:
                modelo_enum = ModeloIA.GEMINI_PRO
        elif settings.GEMINI_MODEL:
            try:
                modelo_enum = ModeloIA(settings.GEMINI_MODEL)
            except ValueError:
                modelo_enum = ModeloIA.GEMINI_PRO
        
        return cls(
            modelo=modelo_enum,
            temperatura=settings.GEMINI_TEMPERATURE,
            max_tokens=settings.GEMINI_MAX_TOKENS
        )

@dataclass
class Prompt:
    """Modelo para un prompt de IA"""
    # Identificadores
    id: Optional[str] = None
    
    # Contenido
    texto: str = ""
    tipo: TipoPrompt = TipoPrompt.USUARIO
    contexto: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Configuración
    configuracion: Optional[ConfiguracionModelo] = None
    
    # Metadatos
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_estimados: Optional[int] = None
    
    def __post_init__(self):
        """Inicialización posterior"""
        if not self.configuracion:
            self.configuracion = ConfiguracionModelo.from_settings()
        
        # Estimar tokens (aproximación simple)
        if not self.tokens_estimados:
            self.tokens_estimados = len(self.texto.split()) * 1.3  # Estimación básica
    
    def formato_completo(self) -> str:
        """
        Genera el texto completo del prompt con contexto y variables
        
        Returns:
            Texto del prompt formateado
        """
        texto_completo = ""
        
        # Agregar contexto si existe
        if self.contexto:
            texto_completo += f"Contexto: {self.contexto}\n\n"
        
        # Texto principal
        texto_completo += self.texto
        
        # Reemplazar variables si existen
        if self.variables:
            for variable, valor in self.variables.items():
                placeholder = f"{{{variable}}}"
                texto_completo = texto_completo.replace(placeholder, str(valor))
        
        return texto_completo
    
    def agregar_variable(self, nombre: str, valor: Any) -> None:
        """Agrega una variable al prompt"""
        self.variables[nombre] = valor
    
    def validar(self) -> bool:
        """
        Valida que el prompt esté correctamente formado
        
        Returns:
            True si es válido
        
        Raises:
            ValueError: Si hay errores de validación
        """
        if not self.texto or not self.texto.strip():
            raise ValueError("El texto del prompt no puede estar vacío")
        
        if len(self.texto) > 50000:  # Límite aproximado
            raise ValueError("El prompt es demasiado largo")
        
        # Verificar que todas las variables en el texto tengan valores
        import re
        variables_en_texto = re.findall(r'\{(\w+)\}', self.texto)
        for variable in variables_en_texto:
            if variable not in self.variables:
                raise ValueError(f"Variable '{variable}' no definida")
        
        return True
    
    @classmethod
    def crear_tarea(cls, texto_usuario: str, proyectos_disponibles: List[str] = None) -> 'Prompt':
        """
        Crea un prompt especializado para crear tareas estructuradas
        
        Args:
            texto_usuario: Texto del usuario describiendo la tarea
            proyectos_disponibles: Lista de proyectos disponibles
        
        Returns:
            Prompt configurado para crear tareas con estructura específica
        """
        # Obtener fecha actual para cálculos de fechas relativas
        from datetime import datetime, timedelta
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        contexto = """Eres un asistente experto en gestión de tareas que convierte texto natural en tareas estructuradas y organizadas.

REGLAS OBLIGATORIAS:
1. PROYECTO: SIEMPRE asignar uno de los proyectos disponibles (OBLIGATORIO)
2. FECHA: Calcular fechas exactas basándote en la fecha actual
3. TÍTULO: Usar formato "VERBO + objeto/acción" (ej: "Revisar documentación", "Comprar materiales")
4. MÚLTIPLES TAREAS: Si detectas varias acciones, crear una tarea separada para cada una"""
        
        texto_base = """FECHA ACTUAL: {fecha_actual}

TEXTO DEL USUARIO: "{texto_usuario}"

PROYECTOS DISPONIBLES:
{proyectos_formateados}

INSTRUCCIONES ESPECÍFICAS:

📋 TÍTULO DE LA TAREA:
- SIEMPRE empezar con un VERBO en infinitivo
- Seguido del objeto/acción específica
- Ejemplos: "Comprar vitaminas", "Revisar código", "Llamar al médico", "Estudiar capítulo 5"

📁 ASIGNACIÓN DE PROYECTO:
- Universidad: estudios, exámenes, trabajos académicos, clases, investigación
- Personal: salud, ejercicio, compras personales, trámites, hobbies, familia
- Tienda Decants: negocio, ventas, productos, clientes, marketing, inventario
- CEE 2025: Centro de estudiantes, reuniones, eventos, actividades, proyectos estudiantiles

📅 FECHAS INTELIGENTES:
- "mañana" = {fecha_manana}
- "pasado mañana" = {fecha_pasado_manana}
- "en 2 días" = {fecha_en_2_dias}
- "en una semana" = {fecha_en_semana}
- "en 2 semanas" = {fecha_en_2_semanas}
- "este viernes" = calcular el próximo viernes
- "la próxima semana" = lunes de la semana siguiente
- "fin de mes" = último día del mes actual

⚡ PRIORIDAD AUTOMÁTICA:
- Urgente: palabras clave "urgente", "ya", "ahora", "inmediato"
- Alta: fechas cercanas (1-2 días), palabras "importante", "crítico"
- Media: fechas normales (3-7 días), tareas rutinarias
- Baja: fechas lejanas (>1 semana), tareas opcionales

RESPONDE ÚNICAMENTE CON UN JSON VÁLIDO:
{{
    "tareas": [
        {{
            "titulo": "Verbo + acción específica",
            "descripcion": "Contexto adicional si es necesario",
            "prioridad": "Baja|Media|Alta|Urgente",
            "proyecto": "uno de los proyectos disponibles OBLIGATORIO",
            "fecha_vencimiento": "YYYY-MM-DD (calculada exactamente)"
        }}
    ]
}}

EJEMPLOS DE ENTRADA → SALIDA:

Entrada: "Para el proyecto personal necesito hacer ejercicio y comprar vitaminas"
Salida: {{
    "tareas": [
        {{
            "titulo": "Hacer ejercicio",
            "descripcion": "Actividad física para mantenimiento",
            "prioridad": "Media", 
            "proyecto": "Personal",
            "fecha_vencimiento": null
        }},
        {{
            "titulo": "Comprar vitaminas",
            "descripcion": "Suplementos para salud personal",
            "prioridad": "Media",
            "proyecto": "Personal", 
            "fecha_vencimiento": null
        }}
    ]
}}

Entrada: "Estudiar el capítulo 5 para el examen del viernes"
Salida: {{
    "tareas": [
        {{
            "titulo": "Estudiar capítulo 5",
            "descripcion": "Preparación para examen del viernes",
            "prioridad": "Alta",
            "proyecto": "Universidad",
            "fecha_vencimiento": "2025-10-18"
        }}
    ]
}}

¡PROCESA AHORA EL TEXTO DEL USUARIO!"""
        
        # Calcular fechas dinámicamente
        hoy = datetime.now()
        fechas_calculadas = {
            "fecha_actual": hoy.strftime("%Y-%m-%d"),
            "fecha_manana": (hoy + timedelta(days=1)).strftime("%Y-%m-%d"),
            "fecha_pasado_manana": (hoy + timedelta(days=2)).strftime("%Y-%m-%d"),
            "fecha_en_2_dias": (hoy + timedelta(days=2)).strftime("%Y-%m-%d"),
            "fecha_en_semana": (hoy + timedelta(days=7)).strftime("%Y-%m-%d"),
            "fecha_en_2_semanas": (hoy + timedelta(days=14)).strftime("%Y-%m-%d")
        }
        
        # Formatear proyectos disponibles
        proyectos_lista = proyectos_disponibles or ["Universidad", "Personal", "Tienda Decants", "CEE 2025"]
        proyectos_formateados = "\n".join([f"• {proyecto}" for proyecto in proyectos_lista])
        
        # Combinar todas las variables
        variables_completas = {
            "texto_usuario": texto_usuario,
            "proyectos_formateados": proyectos_formateados,
            **fechas_calculadas
        }
        
        prompt = cls(
            tipo=TipoPrompt.CREAR_TAREA,
            contexto=contexto,
            texto=texto_base,
            variables=variables_completas
        )
        
        return prompt
    
    @classmethod
    def clasificar_intencion(cls, texto_usuario: str) -> 'Prompt':
        """
        Crea un prompt especializado para clasificar intenciones con alta precisión
        
        Args:
            texto_usuario: Texto del usuario a analizar
        
        Returns:
            Prompt configurado para clasificar intenciones
        """
        contexto = """Eres un clasificador de intenciones experto en gestión de tareas y productividad.
Tu trabajo es analizar con precisión qué acción específica quiere realizar el usuario."""
        
        texto_base = """ANALIZA ESTE TEXTO DEL USUARIO: "{texto_usuario}"

🎯 CLASIFICACIÓN DE INTENCIONES:

📝 CREAR (Usuario quiere crear nueva(s) tarea(s)):
- Indicadores: "necesito", "tengo que", "debo", "quiero hacer", "para el proyecto"
- Verbos de acción: "comprar", "llamar", "estudiar", "revisar", "hacer"
- Menciona proyectos específicos: "para universidad", "del trabajo"
- Expresiones temporales: "mañana", "esta semana", "para el viernes"
- Ejemplos: 
  * "Tengo que comprar leche"
  * "Para el proyecto necesito revisar el código" 
  * "Debo estudiar para el examen"

🔍 CONSULTAR (Usuario quiere ver información existente):
- Preguntas directas: "¿cuántas?", "¿qué tareas?", "¿cómo va?"
- Verbos de consulta: "ver", "mostrar", "listar", "revisar estado"
- Palabras clave: "pendientes", "completadas", "resumen", "estadísticas"
- Ejemplos:
  * "¿Cuántas tareas tengo pendientes?"
  * "Muéstrame las tareas del proyecto Universidad"
  * "¿Cómo van mis proyectos?"

❓ AMBIGUO (No está claro qué quiere hacer):
- Saludos simples: "hola", "buenos días"
- Consultas muy genéricas: "¿qué tal?", "¿cómo estás?"
- Texto incompleto o confuso
- Ejemplos:
  * "Hola"
  * "¿Qué puedes hacer?"
  * "Ayuda"

📊 NIVELES DE CONFIANZA:
- 90-100: Muy claro, indicadores múltiples
- 70-89: Claro, algunos indicadores
- 50-69: Probable, indicadores débiles  
- 0-49: Incierto, clasificar como AMBIGUO

RESPONDE ÚNICAMENTE CON ESTE JSON:
{{
    "intencion": "CREAR|CONSULTAR|AMBIGUO",
    "confianza": número_entre_0_y_100,
    "razonamiento": "explicación específica con indicadores detectados",
    "indicadores_encontrados": ["lista", "de", "palabras_clave", "detectadas"]
}}"""
        
        prompt = cls(
            tipo=TipoPrompt.CLASIFICAR_INTENCION,
            contexto=contexto,
            texto=texto_base,
            variables={
                "texto_usuario": texto_usuario
            }
        )
        
        return prompt

@dataclass
class Respuesta:
    """Modelo para una respuesta de IA"""
    # Identificadores
    id: Optional[str] = None
    prompt_id: Optional[str] = None
    
    # Contenido
    texto: str = ""
    texto_crudo: str = ""  # Respuesta sin procesar
    
    # Metadatos
    timestamp: datetime = field(default_factory=datetime.now)
    modelo_usado: str = ""
    tokens_usados: Optional[int] = None
    tiempo_respuesta: Optional[float] = None  # en segundos
    
    # Datos procesados
    datos_extraidos: Dict[str, Any] = field(default_factory=dict)
    json_extraido: Optional[Dict[str, Any]] = None
    
    # Estado
    exitosa: bool = True
    error: Optional[str] = None
    
    def extraer_json(self) -> Optional[Dict[str, Any]]:
        """
        Extrae JSON de la respuesta si existe
        
        Returns:
            Diccionario con datos JSON o None si no se encuentra
        """
        import json
        import re
        
        # Buscar JSON en la respuesta
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, self.texto, re.DOTALL)
        
        for match in matches:
            try:
                data = json.loads(match)
                self.json_extraido = data
                return data
            except json.JSONDecodeError:
                continue
        
        return None
    
    def extraer_valor(self, clave: str, default: Any = None) -> Any:
        """
        Extrae un valor específico del JSON
        
        Args:
            clave: Clave a buscar
            default: Valor por defecto si no se encuentra
        
        Returns:
            Valor encontrado o default
        """
        if not self.json_extraido:
            self.extraer_json()
        
        if self.json_extraido:
            return self.json_extraido.get(clave, default)
        
        return default
    
    def validar_respuesta(self, claves_requeridas: List[str] = None) -> bool:
        """
        Valida que la respuesta tenga el formato esperado
        
        Args:
            claves_requeridas: Lista de claves que deben existir en el JSON
        
        Returns:
            True si es válida
        """
        if not self.exitosa:
            return False
        
        if claves_requeridas:
            if not self.json_extraido:
                self.extraer_json()
            
            if not self.json_extraido:
                return False
            
            for clave in claves_requeridas:
                if clave not in self.json_extraido:
                    return False
        
        return True
    
    @classmethod
    def from_raw_response(cls, raw_response: Any, prompt_id: str = None, modelo: str = "") -> 'Respuesta':
        """
        Crea una Respuesta desde respuesta cruda de IA
        
        Args:
            raw_response: Respuesta cruda del modelo
            prompt_id: ID del prompt asociado
            modelo: Nombre del modelo usado
        
        Returns:
            Objeto Respuesta procesado
        """
        # Extraer contenido de la respuesta
        if hasattr(raw_response, 'content'):
            texto = raw_response.content
        else:
            texto = str(raw_response)
        
        respuesta = cls(
            prompt_id=prompt_id,
            texto=texto,
            texto_crudo=str(raw_response),
            modelo_usado=modelo,
            exitosa=True
        )
        
        # Intentar extraer JSON automáticamente
        respuesta.extraer_json()
        
        return respuesta
