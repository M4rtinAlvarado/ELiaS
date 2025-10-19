"""
Módulo IA - Cliente y servicios para inteligencia artificial
"""

# Importaciones principales
from .client import IAClient
from .models import Prompt, Respuesta, ModeloIA, TipoPrompt, ConfiguracionModelo
from .services import GeminiService

__all__ = [
    # Cliente
    'IAClient',
    # Modelos
    'Prompt',
    'Respuesta',
    'ConfiguracionModelo',
    'ModeloIA',
    'TipoPrompt',
    # Servicios
    'GeminiService'
]
