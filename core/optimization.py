"""
Módulo de Optimización para ELiaS
=================================

Implementa:
1. Caché de respuestas con TTL (reduce llamadas a Gemini)
2. Debouncing de mensajes (agrupa mensajes rápidos)
3. Lazy Loading de módulos (carga bajo demanda)
4. Respuestas locales (evita IA para consultas simples)
"""

import hashlib
import re
import asyncio
import time
import threading
from typing import Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# 1. CACHÉ DE RESPUESTAS
# =============================================================================

@dataclass
class CacheEntry:
    """Entrada individual del caché con TTL"""
    value: Any
    created_at: datetime
    hits: int = 0
    ttl_seconds: int = 300


class ResponseCache:
    """Caché de respuestas con TTL - Thread-safe con estadísticas"""
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 100):
        self._cache: Dict[str, CacheEntry] = {}
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._lock = threading.Lock()
        self._stats = {'hits': 0, 'misses': 0, 'evictions': 0, 'sets': 0}
        logger.info(f"🗄️ ResponseCache inicializado (TTL: {ttl_seconds}s, Max: {max_size})")
    
    def _generate_key(self, prompt: str, **kwargs) -> str:
        """Genera clave MD5 única para un prompt normalizado"""
        normalized = " ".join(prompt.lower().split())
        key_parts = [normalized] + [f"{k}:{v}" for k, v in sorted(kwargs.items()) if k in ['temperature', 'max_tokens', 'model']]
        return hashlib.md5("|".join(key_parts).encode()).hexdigest()
    
    def get(self, prompt: str, **kwargs) -> Optional[Any]:
        """Obtiene respuesta del caché (None si no existe o expiró)"""
        key = self._generate_key(prompt, **kwargs)
        
        with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            entry = self._cache[key]
            
            # Verificar si expiró
            age = (datetime.now() - entry.created_at).total_seconds()
            if age > entry.ttl_seconds:
                del self._cache[key]
                self._stats['misses'] += 1
                self._stats['evictions'] += 1
                logger.debug(f"🗑️ Cache expirado para key: {key[:8]}...")
                return None
            
            # Hit exitoso
            entry.hits += 1
            self._stats['hits'] += 1
            logger.debug(f"✅ Cache HIT para key: {key[:8]}... (hits: {entry.hits})")
            return entry.value
    
    def set(self, prompt: str, value: Any, ttl_seconds: Optional[int] = None, **kwargs) -> None:
        """Guarda respuesta en caché con TTL opcional"""
        key = self._generate_key(prompt, **kwargs)
        ttl = ttl_seconds or self._ttl
        
        with self._lock:
            # Limpiar si excede tamaño máximo
            if len(self._cache) >= self._max_size:
                self._evict_oldest()
            
            self._cache[key] = CacheEntry(
                value=value,
                created_at=datetime.now(),
                ttl_seconds=ttl
            )
            self._stats['sets'] += 1
            logger.debug(f"💾 Cache SET para key: {key[:8]}... (TTL: {ttl}s)")
    
    def _evict_oldest(self) -> None:
        """Elimina las entradas más antiguas"""
        if not self._cache:
            return
        
        # Ordenar por fecha de creación
        sorted_keys = sorted(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at
        )
        
        # Eliminar el 20% más antiguo
        to_remove = max(1, len(sorted_keys) // 5)
        for key in sorted_keys[:to_remove]:
            del self._cache[key]
            self._stats['evictions'] += 1
        
        logger.info(f"🗑️ Evicted {to_remove} entradas antiguas del caché")
    
    def clear(self) -> None:
        """Limpia todo el caché"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"🧹 Caché limpiado ({count} entradas eliminadas)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del caché"""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self._stats,
                'current_size': len(self._cache),
                'max_size': self._max_size,
                'hit_rate_percent': round(hit_rate, 2),
                'ttl_seconds': self._ttl
            }
    
    def cleanup_expired(self) -> int:
        """Limpia manualmente entradas expiradas"""
        with self._lock:
            now = datetime.now()
            expired_keys = []
            
            for key, entry in self._cache.items():
                age = (now - entry.created_at).total_seconds()
                if age > entry.ttl_seconds:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                self._stats['evictions'] += 1
            
            if expired_keys:
                logger.info(f"🧹 Limpiadas {len(expired_keys)} entradas expiradas")
            
            return len(expired_keys)


# Instancia global del caché de respuestas
response_cache = ResponseCache(ttl_seconds=300, max_size=100)


# =============================================================================
# 2. DEBOUNCING DE MENSAJES
# =============================================================================

@dataclass
class PendingMessage:
    """Mensaje pendiente de procesar"""
    messages: list = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)
    task: Optional[asyncio.Task] = None


class MessageDebouncer:
    """Agrupa mensajes rápidos del usuario antes de procesarlos con IA"""
    
    def __init__(self, delay: float = 1.5, max_messages: int = 5):
        self._pending: Dict[int, PendingMessage] = {}
        self._delay = delay
        self._max_messages = max_messages
        self._lock = asyncio.Lock()
        self._callbacks: Dict[int, Callable] = {}
        self._stats = {'messages_received': 0, 'messages_combined': 0, 'batches_processed': 0}
        logger.info(f"⏱️ MessageDebouncer inicializado (delay: {delay}s, max: {max_messages})")
    
    async def add_message(self, user_id: int, message: str, callback: Optional[Callable] = None) -> Optional[str]:
        """Agrega mensaje al buffer. Retorna mensaje combinado si está listo, None si pendiente."""
        async with self._lock:
            self._stats['messages_received'] += 1
            
            if user_id not in self._pending:
                self._pending[user_id] = PendingMessage()
            
            pending = self._pending[user_id]
            pending.messages.append(message)
            pending.last_update = datetime.now()
            
            if callback:
                self._callbacks[user_id] = callback
            
            # Si alcanzamos el máximo, procesar inmediatamente
            if len(pending.messages) >= self._max_messages:
                return await self._flush_user(user_id)
            
            # Cancelar tarea anterior si existe
            if pending.task and not pending.task.done():
                pending.task.cancel()
            
            # Crear nueva tarea de espera
            pending.task = asyncio.create_task(
                self._delayed_flush(user_id)
            )
            
            return None
    
    async def _delayed_flush(self, user_id: int) -> None:
        """Espera el delay y luego procesa los mensajes"""
        try:
            await asyncio.sleep(self._delay)
            
            async with self._lock:
                if user_id in self._pending:
                    combined = await self._flush_user(user_id)
                    
                    # Ejecutar callback si existe
                    if user_id in self._callbacks and combined:
                        callback = self._callbacks.pop(user_id)
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(combined)
                            else:
                                callback(combined)
                        except Exception as e:
                            logger.error(f"Error en callback de debounce: {e}")
                            
        except asyncio.CancelledError:
            # Tarea cancelada porque llegó otro mensaje
            pass
    
    async def _flush_user(self, user_id: int) -> Optional[str]:
        """Procesa y limpia los mensajes pendientes de un usuario"""
        if user_id not in self._pending:
            return None
        
        pending = self._pending[user_id]
        messages = pending.messages
        
        if not messages:
            return None
        
        # Combinar mensajes
        if len(messages) == 1:
            combined = messages[0]
        else:
            combined = " ".join(messages)
            self._stats['messages_combined'] += len(messages) - 1
            logger.info(f"📦 Combinados {len(messages)} mensajes de usuario {user_id}")
        
        # Limpiar
        del self._pending[user_id]
        self._stats['batches_processed'] += 1
        
        return combined
    
    async def flush_all(self) -> Dict[int, str]:
        """Fuerza el procesamiento de todos los mensajes pendientes"""
        async with self._lock:
            results = {}
            user_ids = list(self._pending.keys())
            
            for user_id in user_ids:
                combined = await self._flush_user(user_id)
                if combined:
                    results[user_id] = combined
            
            return results
    
    def get_pending_count(self, user_id: int) -> int:
        """Retorna cantidad de mensajes pendientes para un usuario"""
        if user_id in self._pending:
            return len(self._pending[user_id].messages)
        return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del debouncer"""
        return {
            **self._stats,
            'pending_users': len(self._pending),
            'delay_seconds': self._delay,
            'max_messages': self._max_messages
        }


# Instancia global del debouncer
message_debouncer = MessageDebouncer(delay=1.5, max_messages=5)


# =============================================================================
# 3. LAZY LOADING DE MÓDULOS
# =============================================================================

class LazyLoader:
    """Singleton para carga bajo demanda de módulos pesados (Gemini, LangGraph, etc.)"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._gemini_client = None
        self._langgraph_service = None
        self._gemini_service = None
        self._ia_client = None
        self._transcription_service = None
        
        # Estadísticas de carga
        self._load_times: Dict[str, float] = {}
        self._load_count: Dict[str, int] = {}
        
        self._initialized = True
        logger.info("🚀 LazyLoader inicializado")
    
    def _load_module(self, name: str, import_func: Callable, required: bool = True):
        """Helper genérico para carga lazy de módulos"""
        start = time.time()
        try:
            instance = import_func()
            self._record_load(name, time.time() - start)
            logger.info(f"✅ {name} cargado en {time.time() - start:.2f}s")
            return instance
        except Exception as e:
            if required:
                logger.error(f"❌ Error cargando {name}: {e}")
                raise
            logger.warning(f"⚠️ {name} no disponible: {e}")
            return None
    
    def get_ia_client(self):
        """Obtiene el cliente de IA"""
        if self._ia_client is None:
            from ia.client import IAClient
            self._ia_client = self._load_module('ia_client', IAClient, required=True)
        return self._ia_client
    
    def get_gemini_service(self):
        """Obtiene el servicio de Gemini"""
        if self._gemini_service is None:
            from ia.services.gemini_service import GeminiService
            self._gemini_service = self._load_module('gemini_service', GeminiService, required=True)
        return self._gemini_service
    
    def get_langgraph_service(self):
        """Obtiene el servicio de LangGraph"""
        if self._langgraph_service is None:
            def load():
                from ia.services.langgraph_service import LangGraphService
                return LangGraphService()
            self._langgraph_service = self._load_module('langgraph_service', load, required=False)
        return self._langgraph_service
    
    def get_transcription_service(self):
        """Obtiene el servicio de transcripción"""
        if self._transcription_service is None:
            def load():
                from ia.services.transcription_service import transcription_service
                return transcription_service
            self._transcription_service = self._load_module('transcription_service', load, required=False)
        return self._transcription_service
    
    def _record_load(self, name: str, load_time: float) -> None:
        """Registra estadísticas de carga"""
        self._load_times[name] = load_time
        self._load_count[name] = self._load_count.get(name, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de carga"""
        return {
            'modules_loaded': list(self._load_times.keys()),
            'load_times': self._load_times,
            'total_load_time': sum(self._load_times.values()),
            'load_counts': self._load_count
        }
    
    def is_loaded(self, module_name: str) -> bool:
        """Verifica si un módulo ya está cargado"""
        mappings = {
            'ia_client': self._ia_client,
            'gemini_service': self._gemini_service,
            'langgraph_service': self._langgraph_service,
            'transcription_service': self._transcription_service
        }
        return mappings.get(module_name) is not None
    
    def preload_essential(self) -> None:
        """Precarga módulos esenciales en background"""
        def _preload():
            try:
                self.get_ia_client()
            except Exception:
                pass
        
        thread = threading.Thread(target=_preload, daemon=True)
        thread.start()
        logger.info("🔄 Precarga de módulos esenciales iniciada en background")


# Instancia global del lazy loader
lazy_loader = LazyLoader()


# =============================================================================
# 4. RESPUESTAS LOCALES (SIN IA)
# =============================================================================

# Patrones que NO necesitan llamar a Gemini
LOCAL_PATTERNS: Dict[str, str] = {
    # Saludos
    r"^(hola|hey|hi|hello|buenas|buenos días|buenas tardes|buenas noches)[\s!]*$": 
        "¡Hola! 👋 Soy ELiaS, tu asistente de tareas. ¿En qué puedo ayudarte?",
    
    # Agradecimientos
    r"^(gracias|thanks|thx|ty|muchas gracias|te agradezco)[\s!]*$": 
        "¡De nada! 😊 Estoy aquí para ayudarte.",
    
    # Despedidas
    r"^(adiós|adios|bye|chau|nos vemos|hasta luego|hasta pronto)[\s!]*$": 
        "¡Hasta pronto! 👋 Vuelve cuando necesites gestionar tus tareas.",
    
    # Confirmaciones simples
    r"^(ok|okay|vale|listo|entendido|perfecto|genial|bien)[\s!]*$": 
        "👍 ¡Perfecto! ¿Necesitas algo más?",
    
    # Estado del bot
    r"^(estás ahí|estas ahi|funcionas|me escuchas|estás|estas)\??[\s!]*$": 
        "¡Sí, aquí estoy! 🤖 Listo para ayudarte con tus tareas.",
    
    # Preguntas sobre el bot
    r"^(quién eres|quien eres|qué eres|que eres|cómo te llamas|como te llamas)\??[\s!]*$": 
        "Soy ELiaS 🤖, tu asistente inteligente para gestionar tareas con Notion. Usa /help para ver lo que puedo hacer.",
}


def local_response_matcher(message: str) -> Optional[str]:
    """Responde localmente sin IA si el mensaje coincide con patrones simples."""
    normalized = message.lower().strip()
    
    for pattern, response in LOCAL_PATTERNS.items():
        if re.match(pattern, normalized, re.IGNORECASE):
            logger.debug(f"📍 Respuesta local para: '{message[:30]}...'")
            return response
    
    return None


# =============================================================================
# 5. HELPER FUNCTIONS
# =============================================================================

def get_cached_or_fetch(prompt: str, fetch_func: Callable, cache: ResponseCache = None,
                        ttl_seconds: Optional[int] = None, **kwargs) -> Tuple[Any, bool]:
    """Obtiene de caché o ejecuta función. Retorna (respuesta, from_cache)."""
    cache = cache or response_cache
    cached = cache.get(prompt, **kwargs)
    if cached is not None:
        return cached, True
    
    result = fetch_func(prompt, **kwargs) if kwargs else fetch_func(prompt)
    cache.set(prompt, result, ttl_seconds=ttl_seconds, **kwargs)
    return result, False


def cached_response(ttl_seconds: int = 300):
    """Decorador para cachear respuestas de funciones."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = str(args[0]) if args else str(kwargs)
            cached = response_cache.get(cache_key)
            if cached is not None:
                return cached
            result = func(*args, **kwargs)
            response_cache.set(cache_key, result, ttl_seconds=ttl_seconds)
            return result
        return wrapper
    return decorator


# =============================================================================
# 6. ESTADÍSTICAS GLOBALES
# =============================================================================

def get_optimization_stats() -> Dict[str, Any]:
    """Obtiene estadísticas de todas las optimizaciones"""
    return {
        'cache': response_cache.get_stats(),
        'debouncer': message_debouncer.get_stats(),
        'lazy_loader': lazy_loader.get_stats(),
        'timestamp': datetime.now().isoformat()
    }


def print_optimization_stats() -> None:
    """Imprime estadísticas de optimización en consola"""
    stats = get_optimization_stats()
    
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS DE OPTIMIZACIÓN - ELiaS")
    print("=" * 60)
    
    # Caché
    cache_stats = stats['cache']
    print(f"\n🗄️ CACHÉ DE RESPUESTAS:")
    print(f"   • Hit Rate: {cache_stats['hit_rate_percent']}%")
    print(f"   • Hits: {cache_stats['hits']} | Misses: {cache_stats['misses']}")
    print(f"   • Tamaño: {cache_stats['current_size']}/{cache_stats['max_size']}")
    print(f"   • Evictions: {cache_stats['evictions']}")
    
    # Debouncer
    debounce_stats = stats['debouncer']
    print(f"\n⏱️ DEBOUNCING:")
    print(f"   • Mensajes recibidos: {debounce_stats['messages_received']}")
    print(f"   • Mensajes combinados: {debounce_stats['messages_combined']}")
    print(f"   • Batches procesados: {debounce_stats['batches_processed']}")
    
    # Lazy Loader
    loader_stats = stats['lazy_loader']
    print(f"\n🚀 LAZY LOADING:")
    print(f"   • Módulos cargados: {len(loader_stats['modules_loaded'])}")
    print(f"   • Tiempo total: {loader_stats['total_load_time']:.2f}s")
    for module, load_time in loader_stats['load_times'].items():
        print(f"      - {module}: {load_time:.2f}s")
    
    print("\n" + "=" * 60 + "\n")
