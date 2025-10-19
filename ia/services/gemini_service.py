"""
Servicio de Gemini - Especializado en operaciones con modelos Gemini
Maneja generación de contenido, clasificación y extracción de datos
"""
import json
from typing import Dict, Any, Optional, List
import time
from datetime import datetime

from config import settings, constants
from ..models import Prompt, Respuesta, TipoPrompt, ModeloIA, ConfiguracionModelo

class GeminiService:
    """
    Servicio especializado para operaciones con Gemini
    """
    
    def __init__(self):
        """Inicializa el servicio Gemini"""
        from ..client import IAClient
        self._client = IAClient()
        self.modelo_por_defecto = ModeloIA.GEMINI_PRO
        self._estadisticas = {
            'requests_total': 0,
            'requests_exitosas': 0,
            'tokens_usados': 0,
            'tiempo_total': 0.0
        }
    
    @property
    def disponible(self) -> bool:
        """Verifica si Gemini está disponible"""
        return self._client.gemini_disponible
    
    @property
    def estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso"""
        return self._estadisticas.copy()
    
    def generar_respuesta(self, prompt: Prompt) -> Respuesta:
        """
        Genera una respuesta usando Gemini
        
        Args:
            prompt: Prompt a procesar
        
        Returns:
            Respuesta generada
        
        Raises:
            RuntimeError: Si Gemini no está disponible
            ValueError: Si el prompt es inválido
        """
        if not self.disponible:
            raise RuntimeError("Gemini no está disponible")
        
        # Validar prompt
        try:
            prompt.validar()
        except ValueError as e:
            raise ValueError(f"Prompt inválido: {e}")
        
        inicio = time.time()
        self._estadisticas['requests_total'] += 1
        
        try:
            # Obtener cliente Gemini
            gemini_client = self._client.gemini_client
            
            # Configurar modelo
            config = prompt.configuracion or ConfiguracionModelo.from_settings()
            
            # Generar contenido usando LangChain
            texto_completo = prompt.formato_completo()
            
            # Para LangChain, usar invoke directamente (la configuración se hace al crear el cliente)
            raw_response = gemini_client.invoke(texto_completo)
            
            # Procesar respuesta
            tiempo_transcurrido = time.time() - inicio
            respuesta = Respuesta.from_raw_response(
                raw_response,
                prompt_id=prompt.id,
                modelo=config.modelo.value
            )
            
            respuesta.tiempo_respuesta = tiempo_transcurrido
            respuesta.tokens_usados = self._estimar_tokens_respuesta(respuesta.texto)
            
            # Actualizar estadísticas
            self._estadisticas['requests_exitosas'] += 1
            self._estadisticas['tokens_usados'] += respuesta.tokens_usados or 0
            self._estadisticas['tiempo_total'] += tiempo_transcurrido
            
            return respuesta
            
        except Exception as e:
            tiempo_transcurrido = time.time() - inicio
            
            # Crear respuesta de error
            respuesta = Respuesta(
                prompt_id=prompt.id,
                texto="",
                exitosa=False,
                error=str(e),
                tiempo_respuesta=tiempo_transcurrido
            )
            
            print(f"❌ Error en Gemini: {e}")
            return respuesta
    
    def clasificar_intencion(self, texto_usuario: str) -> Dict[str, Any]:
        """
        Clasifica la intención del usuario
        
        Args:
            texto_usuario: Texto del usuario a analizar
        
        Returns:
            Diccionario con intención, confianza y razonamiento
        """
        try:
            prompt = Prompt.clasificar_intencion(texto_usuario)
            respuesta = self.generar_respuesta(prompt)
            
            if respuesta.exitosa and respuesta.json_extraido:
                return {
                    'intencion': respuesta.extraer_valor('intencion', 'AMBIGUO'),
                    'confianza': respuesta.extraer_valor('confianza', 0),
                    'razonamiento': respuesta.extraer_valor('razonamiento', ''),
                    'exitosa': True
                }
            else:
                return {
                    'intencion': 'AMBIGUO',
                    'confianza': 0,
                    'razonamiento': 'Error en el procesamiento',
                    'exitosa': False,
                    'error': respuesta.error
                }
                
        except Exception as e:
            print(f"❌ Error clasificando intención: {e}")
            return {
                'intencion': 'AMBIGUO',
                'confianza': 0,
                'razonamiento': f'Error: {e}',
                'exitosa': False,
                'error': str(e)
            }
    
    def extraer_datos_tarea(self, texto_usuario: str, proyectos_disponibles: List[str] = None) -> Dict[str, Any]:
        """
        Extrae datos estructurados para crear una o múltiples tareas
        
        Args:
            texto_usuario: Descripción de la(s) tarea(s)
            proyectos_disponibles: Lista de proyectos disponibles
        
        Returns:
            Diccionario con datos de las tareas extraídas
        """
        try:
            prompt = Prompt.crear_tarea(texto_usuario, proyectos_disponibles)
            respuesta = self.generar_respuesta(prompt)
            
            if respuesta.exitosa and respuesta.json_extraido:
                datos_respuesta = respuesta.json_extraido
                
                # Validar estructura de respuesta
                if 'tareas' not in datos_respuesta or not isinstance(datos_respuesta['tareas'], list):
                    # Fallback: tratar como tarea única (compatibilidad con formato anterior)
                    if 'titulo' in datos_respuesta:
                        datos_respuesta = {'tareas': [datos_respuesta]}
                    else:
                        raise ValueError("Formato de respuesta inválido")
                
                # Validar y normalizar cada tarea
                tareas_procesadas = []
                for i, tarea in enumerate(datos_respuesta['tareas']):
                    tarea_validada = self._validar_y_normalizar_tarea(tarea, i + 1)
                    tareas_procesadas.append(tarea_validada)
                
                return {
                    'tareas': tareas_procesadas,
                    'total_tareas': len(tareas_procesadas),
                    'exitosa': True,
                    'raw_response': respuesta.texto
                }
            else:
                # Fallback: crear tarea básica
                return {
                    'tareas': [self._crear_tarea_fallback(texto_usuario)],
                    'total_tareas': 1,
                    'exitosa': False,
                    'error': respuesta.error,
                    'raw_response': respuesta.texto
                }
                
        except Exception as e:
            print(f"❌ Error extrayendo datos de tarea: {e}")
            return {
                'tareas': [self._crear_tarea_fallback(texto_usuario)],
                'total_tareas': 1,
                'exitosa': False,
                'error': str(e)
            }
    
    def _validar_y_normalizar_tarea(self, tarea: dict, numero_tarea: int) -> dict:
        """
        Valida y normaliza una tarea individual
        
        Args:
            tarea: Diccionario con datos de la tarea
            numero_tarea: Número de la tarea para identificación
            
        Returns:
            Tarea validada y normalizada
        """
        tarea_normalizada = {
            'titulo': tarea.get('titulo', f"Tarea {numero_tarea}").strip(),
            'descripcion': tarea.get('descripcion', '').strip(),
            'prioridad': tarea.get('prioridad', 'Media').strip(),
            'proyecto': tarea.get('proyecto', '').strip() if tarea.get('proyecto') else None,
            'fecha_vencimiento': tarea.get('fecha_vencimiento')
        }
        
        # Validar prioridad
        prioridades_validas = ['Baja', 'Media', 'Alta', 'Urgente']
        if tarea_normalizada['prioridad'] not in prioridades_validas:
            tarea_normalizada['prioridad'] = 'Media'
        
        # Validar formato de fecha
        if tarea_normalizada['fecha_vencimiento']:
            try:
                from datetime import datetime
                # Intentar parsear la fecha
                datetime.strptime(tarea_normalizada['fecha_vencimiento'], '%Y-%m-%d')
            except (ValueError, TypeError):
                print(f"⚠️ Fecha inválida para tarea '{tarea_normalizada['titulo']}': {tarea_normalizada['fecha_vencimiento']}")
                tarea_normalizada['fecha_vencimiento'] = None
        
        # Asegurar título con verbo
        titulo = tarea_normalizada['titulo']
        if titulo and not self._titulo_tiene_verbo(titulo):
            tarea_normalizada['titulo'] = f"Realizar {titulo.lower()}"
        
        return tarea_normalizada
    
    def _crear_tarea_fallback(self, texto_usuario: str) -> dict:
        """
        Crea una tarea básica como fallback cuando falla el análisis IA
        
        Args:
            texto_usuario: Texto original del usuario
            
        Returns:
            Diccionario con tarea básica
        """
        titulo = texto_usuario[:100].strip()
        
        # Intentar extraer un título básico
        if titulo and not self._titulo_tiene_verbo(titulo):
            titulo = f"Realizar {titulo.lower()}"
        
        return {
            'titulo': titulo or "Tarea sin especificar",
            'descripcion': texto_usuario,
            'prioridad': 'Media',
            'proyecto': None,  # Será asignado por el servicio de tareas
            'fecha_vencimiento': None
        }
    
    def _titulo_tiene_verbo(self, titulo: str) -> bool:
        """
        Verifica si un título comienza con un verbo en infinitivo
        
        Args:
            titulo: Título a verificar
            
        Returns:
            True si tiene formato de verbo + acción
        """
        if not titulo:
            return False
            
        # Lista de verbos comunes en infinitivo
        verbos_infinitivo = [
            'hacer', 'crear', 'revisar', 'estudiar', 'comprar', 'llamar',
            'enviar', 'escribir', 'leer', 'completar', 'terminar', 'iniciar',
            'planificar', 'organizar', 'preparar', 'investigar', 'desarrollar',
            'implementar', 'diseñar', 'analizar', 'verificar', 'comprobar',
            'actualizar', 'modificar', 'corregir', 'solucionar', 'resolver',
            'contactar', 'reunir', 'coordinar', 'programar', 'agendar',
            'visitar', 'ir', 'volver', 'entregar', 'recoger', 'buscar'
        ]
        
        primera_palabra = titulo.lower().split()[0] if titulo.split() else ""
        return primera_palabra in verbos_infinitivo
    
    def generar_texto_libre(self, 
                           texto_prompt: str, 
                           contexto: str = "", 
                           temperatura: float = None,
                           max_tokens: int = None) -> Respuesta:
        """
        Genera texto libre con Gemini
        
        Args:
            texto_prompt: Prompt de entrada
            contexto: Contexto adicional (opcional)
            temperatura: Temperatura personalizada (opcional)
            max_tokens: Máximo de tokens (opcional)
        
        Returns:
            Respuesta generada
        """
        # Crear configuración personalizada si es necesario
        config = ConfiguracionModelo.from_settings()
        if temperatura is not None:
            config.temperatura = temperatura
        if max_tokens is not None:
            config.max_tokens = max_tokens
        
        # Crear prompt
        prompt = Prompt(
            texto=texto_prompt,
            contexto=contexto,
            tipo=TipoPrompt.USUARIO,
            configuracion=config
        )
        
        return self.generar_respuesta(prompt)
    
    def procesar_lote(self, prompts: List[Prompt]) -> List[Respuesta]:
        """
        Procesa múltiples prompts en lote
        
        Args:
            prompts: Lista de prompts a procesar
        
        Returns:
            Lista de respuestas en el mismo orden
        """
        respuestas = []
        
        print(f"🔄 Procesando lote de {len(prompts)} prompts...")
        
        for i, prompt in enumerate(prompts, 1):
            print(f"  Procesando {i}/{len(prompts)}...")
            
            try:
                respuesta = self.generar_respuesta(prompt)
                respuestas.append(respuesta)
                
                # Pausa breve entre requests para evitar rate limits
                if i < len(prompts):
                    time.sleep(0.5)
                    
            except Exception as e:
                print(f"❌ Error procesando prompt {i}: {e}")
                respuesta_error = Respuesta(
                    prompt_id=prompt.id,
                    exitosa=False,
                    error=str(e)
                )
                respuestas.append(respuesta_error)
        
        print(f"✅ Lote procesado: {len([r for r in respuestas if r.exitosa])}/{len(prompts)} exitosas")
        
        return respuestas
    
    def _estimar_tokens_respuesta(self, texto: str) -> int:
        """
        Estima el número de tokens en una respuesta
        
        Args:
            texto: Texto de la respuesta
        
        Returns:
            Número estimado de tokens
        """
        # Estimación simple basada en palabras
        # Para una estimación más precisa, se podría usar tiktoken
        palabras = len(texto.split())
        return int(palabras * 1.3)  # Aproximación para español
    
    def obtener_modelos_disponibles(self) -> List[str]:
        """
        Obtiene lista de modelos Gemini disponibles
        
        Returns:
            Lista de nombres de modelos
        """
        return [modelo.value for modelo in ModeloIA if 'gemini' in modelo.value.lower()]
    
    def probar_conexion(self) -> Dict[str, Any]:
        """
        Prueba la conexión con Gemini
        
        Returns:
            Resultado de la prueba
        """
        if not self.disponible:
            return {
                'conectado': False,
                'error': 'Gemini no está disponible - verificar configuración'
            }
        
        try:
            # Crear prompt de prueba simple
            prompt_prueba = Prompt(
                texto="Responde solo con 'OK' si me puedes leer.",
                tipo=TipoPrompt.USUARIO
            )
            
            respuesta = self.generar_respuesta(prompt_prueba)
            
            return {
                'conectado': respuesta.exitosa,
                'modelo': respuesta.modelo_usado,
                'tiempo_respuesta': respuesta.tiempo_respuesta,
                'respuesta': respuesta.texto[:100] if respuesta.texto else None,
                'error': respuesta.error if not respuesta.exitosa else None
            }
            
        except Exception as e:
            return {
                'conectado': False,
                'error': f'Error en prueba de conexión: {e}'
            }
    
    def limpiar_estadisticas(self) -> None:
        """Limpia las estadísticas de uso"""
        self._estadisticas = {
            'requests_total': 0,
            'requests_exitosas': 0,
            'tokens_usados': 0,
            'tiempo_total': 0.0
        }