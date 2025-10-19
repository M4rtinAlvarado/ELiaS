"""
Servicio para gestión de proyectos en Notion
Operaciones CRUD y lógica de negocio para proyectos
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..client import notion_client, NotionConnectionError, NotionValidationError
from ..models import Proyecto, EstadoProyecto
from config import settings
from config.constants import ERROR_MESSAGES

class ProyectosService:
    """Servicio para operaciones con proyectos en Notion"""
    
    def __init__(self):
        """Inicializa el servicio con validaciones"""
        if not notion_client:
            raise NotionConnectionError("Cliente Notion no disponible")
        
        if not settings.NOTION_DB_PROYECTOS:
            raise NotionValidationError("Base de datos de proyectos no configurada")
        
        self.client = notion_client
        self.db_id = settings.NOTION_DB_PROYECTOS
        self._cache_proyectos = {}  # Cache para mejorar rendimiento
    
    def obtener_todos_los_proyectos(self, filtros: Optional[Dict[str, Any]] = None) -> List[Proyecto]:
        """
        Obtiene todos los proyectos de la base de datos
        
        Args:
            filtros: Filtros opcionales para la consulta
        
        Returns:
            Lista de objetos Proyecto
        """
        try:
            query_params = {}
            
            if filtros:
                query_params['filter'] = filtros
            
            # Ordenar por fecha de creación descendente
            query_params['sorts'] = [
                {
                    "timestamp": "created_time",
                    "direction": "descending"
                }
            ]
            
            response = self.client.query_database(self.db_id, **query_params)
            
            proyectos = []
            for page in response.get('results', []):
                try:
                    proyecto = Proyecto.from_notion_page(page)
                    proyectos.append(proyecto)
                except Exception as e:
                    print(f"⚠️ Error procesando proyecto {page.get('id', 'unknown')}: {e}")
            
            return proyectos
            
        except Exception as e:
            raise NotionConnectionError(f"Error obteniendo proyectos: {e}")
    
    def obtener_proyecto_por_id(self, proyecto_id: str) -> Optional[Proyecto]:
        """
        Obtiene un proyecto específico por su ID
        
        Args:
            proyecto_id: ID del proyecto en Notion
        
        Returns:
            Objeto Proyecto o None si no se encuentra
        """
        try:
            page_data = self.client.get_page(proyecto_id)
            return Proyecto.from_notion_page(page_data)
            
        except Exception as e:
            print(f"⚠️ Error obteniendo proyecto {proyecto_id}: {e}")
            return None
    
    def crear_proyecto(self, proyecto: Proyecto) -> Optional[Proyecto]:
        """
        Crea un nuevo proyecto en Notion
        
        Args:
            proyecto: Objeto Proyecto con los datos a crear
        
        Returns:
            Objeto Proyecto creado con ID asignado o None si falla
        """
        try:
            # Validar datos mínimos
            if not proyecto.nombre:
                raise NotionValidationError("El nombre del proyecto es requerido")
            
            # Preparar datos para crear página
            page_data = {
                "parent": {"database_id": self.db_id},
                "properties": proyecto.to_notion_properties()
            }
            
            # Crear página
            response = self.client.create_page(**page_data)
            
            # Retornar proyecto con datos actualizados
            return Proyecto.from_notion_page(response)
            
        except Exception as e:
            print(f"❌ Error creando proyecto: {e}")
            return None
    
    def actualizar_proyecto(self, proyecto: Proyecto) -> Optional[Proyecto]:
        """
        Actualiza un proyecto existente
        
        Args:
            proyecto: Objeto Proyecto con datos actualizados
        
        Returns:
            Objeto Proyecto actualizado o None si falla
        """
        try:
            if not proyecto.id:
                raise NotionValidationError("ID de proyecto es requerido para actualizar")
            
            # Preparar propiedades a actualizar
            properties = proyecto.to_notion_properties()
            
            # Actualizar página
            response = self.client.update_page(
                page_id=proyecto.id,
                properties=properties
            )
            
            return Proyecto.from_notion_page(response)
            
        except Exception as e:
            print(f"❌ Error actualizando proyecto: {e}")
            return None
    
    def cambiar_estado_proyecto(self, proyecto_id: str, nuevo_estado: EstadoProyecto) -> Optional[Proyecto]:
        """
        Cambia el estado de un proyecto específico
        
        Args:
            proyecto_id: ID del proyecto
            nuevo_estado: Nuevo estado para el proyecto
        
        Returns:
            Objeto Proyecto actualizado o None si falla
        """
        try:
            # Obtener proyecto actual
            proyecto = self.obtener_proyecto_por_id(proyecto_id)
            if not proyecto:
                return None
            
            # Actualizar estado
            proyecto.estado = nuevo_estado
            
            # Si se marca como completado, establecer fecha fin si no existe
            if nuevo_estado == EstadoProyecto.COMPLETADO and not proyecto.fecha_fin:
                proyecto.fecha_fin = datetime.now()
                proyecto.progreso = 100
            
            # Actualizar en Notion
            return self.actualizar_proyecto(proyecto)
            
        except Exception as e:
            print(f"❌ Error cambiando estado de proyecto: {e}")
            return None
    
    def actualizar_progreso_proyecto(self, proyecto_id: str, nuevo_progreso: int) -> Optional[Proyecto]:
        """
        Actualiza el progreso de un proyecto
        
        Args:
            proyecto_id: ID del proyecto
            nuevo_progreso: Nuevo porcentaje de progreso (0-100)
        
        Returns:
            Objeto Proyecto actualizado o None si falla
        """
        try:
            if not 0 <= nuevo_progreso <= 100:
                raise NotionValidationError("El progreso debe estar entre 0 y 100")
            
            # Obtener proyecto actual
            proyecto = self.obtener_proyecto_por_id(proyecto_id)
            if not proyecto:
                return None
            
            # Actualizar progreso
            proyecto.progreso = nuevo_progreso
            
            # Si llega a 100%, marcar como completado
            if nuevo_progreso == 100 and proyecto.estado != EstadoProyecto.COMPLETADO:
                proyecto.estado = EstadoProyecto.COMPLETADO
                if not proyecto.fecha_fin:
                    proyecto.fecha_fin = datetime.now()
            
            # Actualizar en Notion
            return self.actualizar_proyecto(proyecto)
            
        except Exception as e:
            print(f"❌ Error actualizando progreso de proyecto: {e}")
            return None
    
    def obtener_proyectos_por_estado(self, estado: EstadoProyecto) -> List[Proyecto]:
        """
        Obtiene proyectos filtrados por estado
        
        Args:
            estado: Estado a filtrar
        
        Returns:
            Lista de proyectos con el estado especificado
        """
        filtro = {
            "property": "Estado",
            "select": {
                "equals": estado.value
            }
        }
        
        return self.obtener_todos_los_proyectos(filtros=filtro)
    
    def obtener_proyectos_activos(self) -> List[Proyecto]:
        """
        Obtiene proyectos que están activos (no completados, cancelados o pausados)
        
        Returns:
            Lista de proyectos activos
        """
        filtro = {
            "or": [
                {
                    "property": "Estado",
                    "select": {
                        "equals": EstadoProyecto.ACTIVO.value
                    }
                },
                {
                    "property": "Estado",
                    "select": {
                        "equals": EstadoProyecto.PLANIFICACION.value
                    }
                }
            ]
        }
        
        return self.obtener_todos_los_proyectos(filtros=filtro)
    
    def buscar_proyectos(self, termino: str) -> List[Proyecto]:
        """
        Busca proyectos por término en nombre o descripción
        
        Args:
            termino: Término de búsqueda
        
        Returns:
            Lista de proyectos que coinciden con la búsqueda
        """
        try:
            # Buscar en toda la base de datos
            all_proyectos = self.obtener_todos_los_proyectos()
            
            # Filtrar por término de búsqueda
            termino_lower = termino.lower()
            proyectos_encontrados = []
            
            for proyecto in all_proyectos:
                if (termino_lower in proyecto.nombre.lower() or 
                    termino_lower in proyecto.descripcion.lower()):
                    proyectos_encontrados.append(proyecto)
            
            return proyectos_encontrados
            
        except Exception as e:
            print(f"❌ Error en búsqueda de proyectos: {e}")
            return []
    
    def obtener_tareas_de_proyecto(self, proyecto_id: str) -> List:
        """
        Obtiene todas las tareas asociadas a un proyecto
        Nota: Esta función requiere el servicio de tareas
        
        Args:
            proyecto_id: ID del proyecto
        
        Returns:
            Lista de tareas del proyecto
        """
        try:
            # Importación local para evitar dependencia circular
            from .tareas_service import tareas_service
            
            if not tareas_service:
                print("⚠️ Servicio de tareas no disponible")
                return []
            
            return tareas_service.obtener_tareas_por_proyecto(proyecto_id)
            
        except Exception as e:
            print(f"❌ Error obteniendo tareas del proyecto: {e}")
            return []
    
    def obtener_resumen_proyectos(self) -> Dict[str, Any]:
        """
        Obtiene un resumen estadístico de los proyectos
        
        Returns:
            Diccionario con estadísticas de proyectos
        """
        try:
            todos_los_proyectos = self.obtener_todos_los_proyectos()
            
            # Contar por estado
            conteo_estados = {}
            for estado in EstadoProyecto:
                conteo_estados[estado.value] = 0
            
            # Calcular estadísticas
            progreso_total = 0
            proyectos_con_fechas = 0
            
            for proyecto in todos_los_proyectos:
                # Contar estado
                conteo_estados[proyecto.estado.value] += 1
                
                # Sumar progreso
                progreso_total += proyecto.progreso
                
                # Contar proyectos con fechas
                if proyecto.fecha_inicio and proyecto.fecha_fin:
                    proyectos_con_fechas += 1
            
            # Calcular progreso promedio
            progreso_promedio = (
                progreso_total / len(todos_los_proyectos) 
                if todos_los_proyectos else 0
            )
            
            return {
                "total_proyectos": len(todos_los_proyectos),
                "por_estado": conteo_estados,
                "progreso_promedio": round(progreso_promedio, 2),
                "proyectos_con_fechas": proyectos_con_fechas,
                "tasa_completada": (
                    conteo_estados[EstadoProyecto.COMPLETADO.value] / len(todos_los_proyectos) * 100
                    if todos_los_proyectos else 0
                )
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo resumen: {e}")
            return {}
    
    def cargar_proyectos_como_diccionario(self) -> Dict[str, str]:
        """
        Carga todos los proyectos disponibles como diccionario {nombre: id}
        
        Returns:
            Diccionario con nombres como keys e IDs como values
        """
        try:
            print("🔄 Cargando proyectos disponibles...")
            
            proyectos_objetos = self.obtener_todos_los_proyectos()
            
            proyectos_dict = {}
            for proyecto_obj in proyectos_objetos:
                if proyecto_obj.nombre and proyecto_obj.id:
                    proyectos_dict[proyecto_obj.nombre] = proyecto_obj.id
                    self._cache_proyectos[proyecto_obj.id] = proyecto_obj.nombre
                else:
                    # Si no se puede extraer el nombre, usar el ID como nombre
                    nombre_fallback = f"Proyecto_{proyecto_obj.id[:8]}"
                    proyectos_dict[nombre_fallback] = proyecto_obj.id
                    self._cache_proyectos[proyecto_obj.id] = nombre_fallback
            
            print(f"✅ {len(proyectos_dict)} proyectos cargados: {list(proyectos_dict.keys())}")
            return proyectos_dict
            
        except Exception as e:
            print(f"❌ Error al cargar proyectos: {e}")
            return {}
    
    def obtener_nombre_por_id(self, proyecto_id: str) -> str:
        """
        Obtiene el nombre de un proyecto por su ID
        
        Args:
            proyecto_id: ID del proyecto
        
        Returns:
            Nombre del proyecto o nombre fallback
        """
        # Buscar en cache primero
        if proyecto_id in self._cache_proyectos:
            return self._cache_proyectos[proyecto_id]
        
        # Si no está en cache, consultar directamente
        try:
            proyecto = self.obtener_proyecto_por_id(proyecto_id)
            if proyecto and proyecto.nombre:
                self._cache_proyectos[proyecto_id] = proyecto.nombre
                return proyecto.nombre
            
            nombre_fallback = f"Proyecto_{proyecto_id[:8]}"
            self._cache_proyectos[proyecto_id] = nombre_fallback
            return nombre_fallback
            
        except Exception as e:
            print(f"⚠️ No se pudo obtener nombre del proyecto {proyecto_id}: {e}")
            nombre_fallback = f"Proyecto_{proyecto_id[:8]}"
            self._cache_proyectos[proyecto_id] = nombre_fallback
            return nombre_fallback
    
    def listar_proyectos_disponibles(self) -> Dict[str, str]:
        """
        Lista todos los proyectos disponibles con formato amigable
        
        Returns:
            Diccionario de proyectos {nombre: id}
        """
        proyectos_dict = self.cargar_proyectos_como_diccionario()
        
        print("📁 Proyectos disponibles:")
        for i, (nombre, proyecto_id) in enumerate(proyectos_dict.items(), 1):
            print(f"   {i}. {nombre} (ID: {proyecto_id[:8]}...)")
        
        return proyectos_dict

# Instancia global del servicio
try:
    proyectos_service = ProyectosService()
except Exception as e:
    print(f"⚠️ Error inicializando servicio de proyectos: {e}")
    proyectos_service = None