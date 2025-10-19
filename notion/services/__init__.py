"""
Servicios de Notion
"""
from .tareas_service import TareasService, tareas_service
from .proyectos_service import ProyectosService, proyectos_service

__all__ = [
    'TareasService',
    'tareas_service',
    'ProyectosService', 
    'proyectos_service'
]