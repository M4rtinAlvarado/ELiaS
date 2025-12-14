"""
Core - Módulos fundamentales de ELiaS
Incluye optimizaciones, caché y utilidades compartidas
"""

from .optimization import (
    ResponseCache,
    response_cache,
    MessageDebouncer,
    message_debouncer,
    LazyLoader,
    lazy_loader,
    local_response_matcher,
    get_cached_or_fetch,
    get_optimization_stats,
    cached_response
)

__all__ = [
    'ResponseCache',
    'response_cache',
    'MessageDebouncer', 
    'message_debouncer',
    'LazyLoader',
    'lazy_loader',
    'local_response_matcher',
    'get_cached_or_fetch',
    'get_optimization_stats',
    'cached_response'
]
