"""
Cliente centralizado para Notion API
Maneja conexiones, errores y operaciones básicas
"""
from typing import Dict, Any, Optional, List
from notion_client import Client
from config import settings
from config.constants import ERROR_MESSAGES, TIMEOUTS, PATTERNS
import re

class NotionConnectionError(Exception):
    """Excepción personalizada para errores de conexión con Notion"""
    pass

class NotionValidationError(Exception):
    """Excepción personalizada para errores de validación de datos"""
    pass

class NotionClient:
    """Cliente centralizado para todas las operaciones con Notion"""
    
    def __init__(self):
        """Inicializa el cliente con validaciones"""
        if not settings.NOTION_TOKEN:
            raise NotionConnectionError("Token de Notion no configurado en settings")
        
        try:
            self.client = Client(
                auth=settings.NOTION_TOKEN,
                timeout_ms=TIMEOUTS["NOTION_API"] * 1000
            )
            self._validate_connection()
            
        except Exception as e:
            raise NotionConnectionError(f"Error inicializando cliente Notion: {e}")
    
    def _validate_connection(self) -> None:
        """Valida la conexión realizando una consulta simple"""
        try:
            # Test simple: obtener información del usuario
            user_info = self.client.users.me()
            print(f"✅ Conectado a Notion como: {user_info.get('name', 'Usuario')}")
            
        except Exception as e:
            raise NotionConnectionError(f"Falló la validación de conexión: {e}")
    
    def _validate_database_id(self, database_id: str) -> str:
        """Valida formato del ID de base de datos"""
        if not database_id:
            raise NotionValidationError("ID de base de datos no puede estar vacío")
        
        # Limpiar ID (remover guiones)
        clean_id = database_id.replace("-", "").replace(" ", "")
        
        # Validar formato usando regex de constants
        if not re.match(PATTERNS["NOTION_DB_ID"], clean_id):
            raise NotionValidationError(f"Formato de ID de BD inválido: {database_id}")
        
        return clean_id
    
    def _validate_page_id(self, page_id: str) -> str:
        """Valida formato del ID de página"""
        if not page_id:
            raise NotionValidationError("ID de página no puede estar vacío")
            
        # El ID puede venir con o sin guiones
        if "-" in page_id:
            # Validar formato UUID completo
            if not re.match(PATTERNS["NOTION_PAGE_ID"], page_id):
                raise NotionValidationError(f"Formato de ID de página inválido: {page_id}")
        else:
            # Formato sin guiones, agregamos guiones para validar
            formatted_id = f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
            if not re.match(PATTERNS["NOTION_PAGE_ID"], formatted_id):
                raise NotionValidationError(f"Formato de ID de página inválido: {page_id}")
            
        return page_id
    
    def query_database(self, database_id: str, **kwargs) -> Dict[str, Any]:
        """
        Consulta una base de datos con validaciones y manejo de errores
        
        Args:
            database_id: ID de la base de datos
            **kwargs: Parámetros adicionales (filter, sorts, page_size, etc.)
        
        Returns:
            Respuesta de la API de Notion
        
        Raises:
            NotionConnectionError: Si hay error de conexión
            NotionValidationError: Si los parámetros son inválidos
        """
        try:
            # Validar y limpiar ID
            clean_id = self._validate_database_id(database_id)
            
            # Limitar page_size si no se especifica o es muy alto
            if 'page_size' not in kwargs or kwargs['page_size'] > 100:
                kwargs['page_size'] = 100
            
            # Ejecutar consulta
            response = self.client.databases.query(
                database_id=clean_id,
                **kwargs
            )
            
            return response
            
        except NotionValidationError:
            raise  # Re-lanzar errores de validación
        except Exception as e:
            raise NotionConnectionError(f"{ERROR_MESSAGES['NOTION_CONNECTION']}: {e}")
    
    def create_page(self, **kwargs) -> Dict[str, Any]:
        """
        Crea una nueva página con validaciones
        
        Args:
            **kwargs: Parámetros de creación (parent, properties, etc.)
        
        Returns:
            Página creada
        
        Raises:
            NotionConnectionError: Si hay error de conexión
            NotionValidationError: Si los parámetros son inválidos
        """
        try:
            # Validar estructura básica
            if 'parent' not in kwargs:
                raise NotionValidationError("Parámetro 'parent' es requerido")
            
            if 'properties' not in kwargs:
                raise NotionValidationError("Parámetro 'properties' es requerido")
            
            # Validar database_id en parent si existe
            if 'database_id' in kwargs['parent']:
                kwargs['parent']['database_id'] = self._validate_database_id(
                    kwargs['parent']['database_id']
                )
            
            # Crear página
            response = self.client.pages.create(**kwargs)
            return response
            
        except NotionValidationError:
            raise  # Re-lanzar errores de validación
        except Exception as e:
            raise NotionConnectionError(f"Error al crear página: {e}")
    
    def update_page(self, page_id: str, **kwargs) -> Dict[str, Any]:
        """
        Actualiza una página existente
        
        Args:
            page_id: ID de la página a actualizar
            **kwargs: Propiedades a actualizar
        
        Returns:
            Página actualizada
        """
        try:
            # Validar ID de página
            clean_page_id = self._validate_page_id(page_id)
            
            # Actualizar página
            response = self.client.pages.update(
                page_id=clean_page_id,
                **kwargs
            )
            
            return response
            
        except NotionValidationError:
            raise
        except Exception as e:
            raise NotionConnectionError(f"Error al actualizar página: {e}")
    
    def get_page(self, page_id: str) -> Dict[str, Any]:
        """
        Obtiene una página específica
        
        Args:
            page_id: ID de la página
        
        Returns:
            Datos de la página
        """
        try:
            clean_page_id = self._validate_page_id(page_id)
            response = self.client.pages.retrieve(page_id=clean_page_id)
            return response
            
        except NotionValidationError:
            raise
        except Exception as e:
            raise NotionConnectionError(f"Error al obtener página: {e}")
    
    def get_database(self, database_id: str) -> Dict[str, Any]:
        """
        Obtiene información de una base de datos
        
        Args:
            database_id: ID de la base de datos
        
        Returns:
            Información de la base de datos
        """
        try:
            clean_id = self._validate_database_id(database_id)
            response = self.client.databases.retrieve(database_id=clean_id)
            return response
            
        except NotionValidationError:
            raise
        except Exception as e:
            raise NotionConnectionError(f"Error al obtener BD: {e}")
    
    def search(self, query: str = "", **kwargs) -> Dict[str, Any]:
        """
        Realiza búsqueda en Notion
        
        Args:
            query: Texto a buscar
            **kwargs: Parámetros adicionales (filter, sort, etc.)
        
        Returns:
            Resultados de búsqueda
        """
        try:
            search_params = {"query": query}
            search_params.update(kwargs)
            
            response = self.client.search(**search_params)
            return response
            
        except Exception as e:
            raise NotionConnectionError(f"Error en búsqueda: {e}")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Obtiene estado de la conexión y configuración
        
        Returns:
            Diccionario con información de estado
        """
        try:
            user_info = self.client.users.me()
            
            # Probar acceso a bases de datos configuradas
            databases_status = {}
            
            if settings.NOTION_DB_TAREAS:
                try:
                    db_info = self.get_database(settings.NOTION_DB_TAREAS)
                    databases_status['tareas'] = {
                        'accessible': True,
                        'title': db_info.get('title', [{}])[0].get('plain_text', 'Sin título'),
                        'id': settings.NOTION_DB_TAREAS
                    }
                except Exception as e:
                    databases_status['tareas'] = {
                        'accessible': False,
                        'error': str(e),
                        'id': settings.NOTION_DB_TAREAS
                    }
            
            if settings.NOTION_DB_PROYECTOS:
                try:
                    db_info = self.get_database(settings.NOTION_DB_PROYECTOS)
                    databases_status['proyectos'] = {
                        'accessible': True,
                        'title': db_info.get('title', [{}])[0].get('plain_text', 'Sin título'),
                        'id': settings.NOTION_DB_PROYECTOS
                    }
                except Exception as e:
                    databases_status['proyectos'] = {
                        'accessible': False,
                        'error': str(e),
                        'id': settings.NOTION_DB_PROYECTOS
                    }
            
            return {
                'connected': True,
                'user_name': user_info.get('name', 'Usuario'),
                'user_id': user_info.get('id'),
                'databases': databases_status,
                'token_valid': True
            }
            
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'token_valid': False
            }

# Instancia global del cliente
try:
    notion_client = NotionClient()
except Exception as e:
    print(f"⚠️ Error inicializando cliente Notion: {e}")
    notion_client = None