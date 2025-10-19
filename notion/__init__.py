"""
Módulo Notion - Cliente y modelos para interactuar con Notion API
"""

# Importaciones principales
from .client import NotionClient, notion_client, NotionConnectionError, NotionValidationError
from .models import Tarea, Proyecto, EstadoTarea, PrioridadTarea, EstadoProyecto
from .services import TareasService, tareas_service, ProyectosService, proyectos_service

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
    # Enums
    'EstadoTarea',
    'PrioridadTarea', 
    'EstadoProyecto',
    # Servicios
    'TareasService',
    'tareas_service',
    'ProyectosService', 
    'proyectos_service'
]