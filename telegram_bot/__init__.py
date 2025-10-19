"""
Módulo Telegram para ELiaS v2.0
===============================

Bot de Telegram que integra perfectamente con la arquitectura modular existente.
Utiliza LangGraphService para procesamiento inteligente de consultas.
"""

from .bot import EliasBot
from .keyboards import TelegramKeyboards

__all__ = ['EliasBot', 'TelegramKeyboards']