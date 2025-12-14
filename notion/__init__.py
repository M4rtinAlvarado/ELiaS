"""
Módulo Notion - Cliente y modelos para interactuar con Notion API
"""

# Importaciones principales
from .client import NotionClient, notion_client, NotionConnectionError, NotionValidationError
from .models import (
    Tarea, Proyecto, Evento,
    EstadoTarea, PrioridadTarea, EstadoProyecto,
    EstadoEvento, TipoEvento
)
from .services import (
    TareasService, tareas_service,
    ProyectosService, proyectos_service,
    EventosService, eventos_service
)

__all__ = [
    # Cliente
    'NotionClient', 
    'notion_client',
    # Excepciones
    'NotionConnectionError',
    'NotionValidationError', 
    # Modelos
    'Tarea', 
    'Proyecto',
    'Evento',
    # Enums Tarea
    'EstadoTarea',
    'PrioridadTarea', 
    # Enums Proyecto
    'EstadoProyecto',
    # Enums Evento
    'EstadoEvento',
    'TipoEvento',
    # Servicios
    'TareasService',
    'tareas_service',
    'ProyectosService', 
    'proyectos_service',
    'EventosService',
    'eventos_service'
]