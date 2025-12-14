"""
Cliente centralizado para servicios de IA
Maneja conexiones, configuración y operaciones básicas con modelos de IA
"""
from typing import Dict, Any, Optional, List
from config import settings
from config.constants import ERROR_MESSAGES, TIMEOUTS

# Importar sistema de caché
try:
    from core.optimization import response_cache, cached_response
    CACHE_ENABLED = True
except ImportError:
    CACHE_ENABLED = False
    response_cache = None

class IAConnectionError(Exception):
    """Excepción personalizada para errores de conexión con servicios de IA"""
    pass

class IAConfigurationError(Exception):
    """Excepción personalizada para errores de configuración de IA"""
    pass

class IAClient:
    """Cliente centralizado para todas las operaciones de IA"""
    
    def __init__(self):
        """Inicializa el cliente con validaciones"""
        self._gemini_client = None
        self._langgraph_available = False
        self._langchain_available = False
        
        self._validate_configuration()
        self._initialize_clients()
    
    def _validate_configuration(self) -> None:
        """Valida la configuración de IA"""
        if not settings.GOOGLE_API_KEY:
            raise IAConfigurationError("Google API Key no configurada")
        
        if not settings.GEMINI_MODEL:
            raise IAConfigurationError("Modelo Gemini no especificado")
        
        print(f"✅ Configuración IA validada:")
        print(f"   • Modelo: {settings.GEMINI_MODEL}")
        print(f"   • Temperatura: {settings.GEMINI_TEMPERATURE}")
        print(f"   • Max tokens: {settings.GEMINI_MAX_TOKENS}")
    
    def _initialize_clients(self) -> None:
        """Inicializa los clientes de IA disponibles (lazy loading)"""
        # Intentar inicializar Gemini
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            self._gemini_client = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=settings.GEMINI_TEMPERATURE,
                max_tokens=settings.GEMINI_MAX_TOKENS
            )
            
            # NO hacer test aquí - se valida en primera llamada real
            self._connection_verified = False
            print(f"✅ Gemini cliente inicializado (verificación lazy)")
            
        except ImportError:
            print("⚠️ langchain_google_genai no disponible - Instalar: pip install langchain-google-genai")
            self._gemini_client = None
        except Exception as e:
            print(f"❌ Error inicializando Gemini: {e}")
            self._gemini_client = None
        
        # Verificar disponibilidad de LangGraph
        try:
            from langgraph.graph import StateGraph, END
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
            self._langgraph_available = True
            print(f"✅ LangGraph disponible")
        except ImportError:
            print("⚠️ LangGraph no disponible - Instalar: pip install langgraph")
            self._langgraph_available = False
        
        # Verificar disponibilidad de LangChain
        try:
            from langchain.agents import initialize_agent, AgentType
            from langchain.tools import Tool
            self._langchain_available = True
            print(f"✅ LangChain disponible")
        except ImportError:
            print("⚠️ LangChain no disponible - Instalar: pip install langchain")
            self._langchain_available = False
    
    @property
    def gemini_client(self):
        """Obtiene el cliente de Gemini"""
        if not self._gemini_client:
            raise IAConnectionError("Cliente Gemini no disponible")
        return self._gemini_client
    
    @property
    def gemini_disponible(self) -> bool:
        """Verifica si Gemini está disponible y configurado"""
        return self._gemini_client is not None
    
    @property
    def langgraph_available(self) -> bool:
        """Verifica si LangGraph está disponible"""
        return self._langgraph_available
    
    @property
    def langchain_available(self) -> bool:
        """Verifica si LangChain está disponible"""
        return self._langchain_available
    
    def invoke_gemini(self, prompt: str, use_cache: bool = True, **kwargs) -> str:
        """
        Invoca Gemini con un prompt (con soporte de caché)
        
        Args:
            prompt: Texto del prompt
            use_cache: Si usar caché de respuestas (default: True)
            **kwargs: Parámetros adicionales
        
        Returns:
            Respuesta del modelo
        
        Raises:
            IAConnectionError: Si hay error de conexión
        """
        try:
            if not self._gemini_client:
                raise IAConnectionError("Cliente Gemini no disponible")
            
            # Verificar conexión en primera llamada (lazy validation)
            if not getattr(self, '_connection_verified', False):
                try:
                    test = self._gemini_client.invoke("Hi")
                    self._connection_verified = True
                    print("✅ Conexión con Gemini verificada")
                except Exception as e:
                    raise IAConnectionError(f"No se pudo conectar con Gemini: {e}")
            
            # Intentar obtener de caché primero
            if use_cache and CACHE_ENABLED and response_cache:
                cached = response_cache.get(prompt, **kwargs)
                if cached is not None:
                    print(f"🗄️ Respuesta desde caché")
                    return cached
            
            # Configurar parámetros opcionales
            params = {k: kwargs[k] for k in ['temperature', 'max_tokens'] if k in kwargs}
            
            # Crear cliente temporal si hay parámetros custom
            if params:
                from langchain_google_genai import ChatGoogleGenerativeAI
                client_temp = ChatGoogleGenerativeAI(
                    model=settings.GEMINI_MODEL,
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=params.get('temperature', settings.GEMINI_TEMPERATURE),
                    max_tokens=params.get('max_tokens', settings.GEMINI_MAX_TOKENS)
                )
                response = client_temp.invoke(prompt)
            else:
                response = self._gemini_client.invoke(prompt)
            
            # Extraer contenido de la respuesta
            result = response.content if hasattr(response, 'content') else str(response)
            
            # Guardar en caché
            if use_cache and CACHE_ENABLED and response_cache:
                response_cache.set(prompt, result, **kwargs)
            
            return result
                
        except Exception as e:
            raise IAConnectionError(f"Error invocando Gemini: {e}")
    
    def batch_invoke_gemini(self, prompts: List[str], **kwargs) -> List[str]:
        """
        Invoca Gemini con múltiples prompts en lote
        
        Args:
            prompts: Lista de prompts
            **kwargs: Parámetros adicionales
        
        Returns:
            Lista de respuestas
        """
        try:
            if not self._gemini_client:
                raise IAConnectionError("Cliente Gemini no disponible")
            
            responses = []
            for prompt in prompts:
                response = self.invoke_gemini(prompt, **kwargs)
                responses.append(response)
            
            return responses
            
        except Exception as e:
            raise IAConnectionError(f"Error en batch invoke: {e}")
    
    def get_ai_status(self) -> Dict[str, Any]:
        """
        Obtiene estado de todos los servicios de IA
        
        Returns:
            Diccionario con información de estado
        """
        status = {
            'gemini': {
                'available': self._gemini_client is not None,
                'model': settings.GEMINI_MODEL if self._gemini_client else None,
                'error': None
            },
            'langgraph': {
                'available': self._langgraph_available
            },
            'langchain': {
                'available': self._langchain_available
            },
            'configuration': {
                'api_key_configured': bool(settings.GOOGLE_API_KEY),
                'model_configured': bool(settings.GEMINI_MODEL),
                'temperature': settings.GEMINI_TEMPERATURE,
                'max_tokens': settings.GEMINI_MAX_TOKENS
            }
        }
        
        # Test de conectividad con Gemini
        if self._gemini_client:
            try:
                test_response = self._gemini_client.invoke("Test")
                status['gemini']['connection_test'] = 'success'
            except Exception as e:
                status['gemini']['connection_test'] = 'failed'
                status['gemini']['error'] = str(e)
        
        return status
    
    def validate_prompt(self, prompt: str, max_length: int = 10000) -> bool:
        """
        Valida un prompt antes de enviarlo
        
        Args:
            prompt: Texto del prompt
            max_length: Longitud máxima permitida
        
        Returns:
            True si es válido
        
        Raises:
            IAConfigurationError: Si el prompt no es válido
        """
        if not prompt or not prompt.strip():
            raise IAConfigurationError("Prompt no puede estar vacío")
        
        if len(prompt) > max_length:
            raise IAConfigurationError(f"Prompt excede longitud máxima ({max_length} caracteres)")
        
        return True

# Instancia global del cliente
try:
    ia_client = IAClient()
except Exception as e:
    print(f"⚠️ Error inicializando cliente IA: {e}")
    ia_client = None
