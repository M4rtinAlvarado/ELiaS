"""
Servicio para gestión de tareas en Notion
Operaciones CRUD y lógica de negocio para tareas
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from ..client import notion_client, NotionConnectionError, NotionValidationError
from ..models import Tarea, EstadoTarea, PrioridadTarea
from config import settings
from config.constants import ERROR_MESSAGES

class TareasService:
    """Servicio para operaciones con tareas en Notion"""
    
    def __init__(self):
        """Inicializa el servicio con validaciones"""
        if not notion_client:
            raise NotionConnectionError("Cliente Notion no disponible")
        
        if not settings.NOTION_DB_TAREAS:
            raise NotionValidationError("Base de datos de tareas no configurada")
        
        self.client = notion_client
        self.db_id = settings.NOTION_DB_TAREAS
    
    def obtener_todas_las_tareas(self, filtros: Optional[Dict[str, Any]] = None) -> List[Tarea]:
        """
        Obtiene todas las tareas de la base de datos
        
        Args:
            filtros: Filtros opcionales para la consulta
        
        Returns:
            Lista de objetos Tarea
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
            
            tareas = []
            for page in response.get('results', []):
                try:
                    tarea = Tarea.from_notion_page(page)
                    tareas.append(tarea)
                except Exception as e:
                    print(f"⚠️ Error procesando tarea {page.get('id', 'unknown')}: {e}")
            
            return tareas
            
        except Exception as e:
            raise NotionConnectionError(f"Error obteniendo tareas: {e}")
    
    def obtener_tarea_por_id(self, tarea_id: str) -> Optional[Tarea]:
        """
        Obtiene una tarea específica por su ID
        
        Args:
            tarea_id: ID de la tarea en Notion
        
        Returns:
            Objeto Tarea o None si no se encuentra
        """
        try:
            page_data = self.client.get_page(tarea_id)
            return Tarea.from_notion_page(page_data)
            
        except Exception as e:
            print(f"⚠️ Error obteniendo tarea {tarea_id}: {e}")
            return None
    
    def crear_tarea(self, tarea: Tarea) -> Optional[Tarea]:
        """
        Crea una nueva tarea en Notion
        
        Args:
            tarea: Objeto Tarea con los datos a crear
        
        Returns:
            Objeto Tarea creado con ID asignado o None si falla
        """
        try:
            # Validar datos mínimos
            if not tarea.nombre:
                raise NotionValidationError("El nombre de la tarea es requerido")
            
            # Preparar datos para crear página
            page_data = {
                "parent": {"database_id": self.db_id},
                "properties": tarea.to_notion_properties()
            }
            
            # Crear página
            response = self.client.create_page(**page_data)
            
            # Retornar tarea con datos actualizados
            return Tarea.from_notion_page(response)
            
        except Exception as e:
            print(f"❌ Error creando tarea: {e}")
            return None
    
    def actualizar_tarea(self, tarea: Tarea) -> Optional[Tarea]:
        """
        Actualiza una tarea existente
        
        Args:
            tarea: Objeto Tarea con datos actualizados
        
        Returns:
            Objeto Tarea actualizado o None si falla
        """
        try:
            if not tarea.id:
                raise NotionValidationError("ID de tarea es requerido para actualizar")
            
            # Preparar propiedades a actualizar
            properties = tarea.to_notion_properties()
            
            # Actualizar página
            response = self.client.update_page(
                page_id=tarea.id,
                properties=properties
            )
            
            return Tarea.from_notion_page(response)
            
        except Exception as e:
            print(f"❌ Error actualizando tarea: {e}")
            return None
    
    def cambiar_estado_tarea(self, tarea_id: str, nuevo_estado: EstadoTarea) -> Optional[Tarea]:
        """
        Cambia el estado de una tarea específica
        
        Args:
            tarea_id: ID de la tarea
            nuevo_estado: Nuevo estado para la tarea
        
        Returns:
            Objeto Tarea actualizado o None si falla
        """
        try:
            # Obtener tarea actual
            tarea = self.obtener_tarea_por_id(tarea_id)
            if not tarea:
                return None
            
            # Actualizar estado
            tarea.estado = nuevo_estado
            
            # Si se marca como completado, establecer fecha
            if nuevo_estado == EstadoTarea.COMPLETADO:
                tarea.fecha_completada = datetime.now()
            
            # Actualizar en Notion
            return self.actualizar_tarea(tarea)
            
        except Exception as e:
            print(f"❌ Error cambiando estado de tarea: {e}")
            return None
    
    def obtener_tareas_por_estado(self, estado: EstadoTarea) -> List[Tarea]:
        """
        Obtiene tareas filtradas por estado
        
        Args:
            estado: Estado a filtrar
        
        Returns:
            Lista de tareas con el estado especificado
        """
        filtro = {
            "property": "Estado",
            "select": {
                "equals": estado.value
            }
        }
        
        return self.obtener_todas_las_tareas(filtros=filtro)
    
    def obtener_tareas_por_prioridad(self, prioridad: PrioridadTarea) -> List[Tarea]:
        """
        Obtiene tareas filtradas por prioridad
        
        Args:
            prioridad: Prioridad a filtrar
        
        Returns:
            Lista de tareas con la prioridad especificada
        """
        filtro = {
            "property": "Prioridad",
            "select": {
                "equals": prioridad.value
            }
        }
        
        return self.obtener_todas_las_tareas(filtros=filtro)
    
    def obtener_tareas_vencidas(self) -> List[Tarea]:
        """
        Obtiene tareas que están vencidas (fecha límite pasada y no completadas)
        
        Returns:
            Lista de tareas vencidas
        """
        filtro = {
            "and": [
                {
                    "property": "Fecha límite",
                    "date": {
                        "before": datetime.now().isoformat()
                    }
                },
                {
                    "property": "Estado",
                    "status": {
                        "does_not_equal": EstadoTarea.COMPLETADO.value
                    }
                }
            ]
        }
        
        return self.obtener_todas_las_tareas(filtros=filtro)
    
    def obtener_tareas_por_proyecto(self, proyecto_id: str) -> List[Tarea]:
        """
        Obtiene tareas asociadas a un proyecto específico
        
        Args:
            proyecto_id: ID del proyecto en Notion
        
        Returns:
            Lista de tareas del proyecto
        """
        filtro = {
            "property": "Proyecto",
            "relation": {
                "contains": proyecto_id
            }
        }
        
        return self.obtener_todas_las_tareas(filtros=filtro)
    
    def buscar_tareas(self, termino: str) -> List[Tarea]:
        """
        Busca tareas por término en nombre o descripción
        
        Args:
            termino: Término de búsqueda
        
        Returns:
            Lista de tareas que coinciden con la búsqueda
        """
        try:
            # Buscar en toda la base de datos
            all_tareas = self.obtener_todas_las_tareas()
            
            # Filtrar por término de búsqueda
            termino_lower = termino.lower()
            tareas_encontradas = []
            
            for tarea in all_tareas:
                if (termino_lower in tarea.nombre.lower() or 
                    termino_lower in tarea.descripcion.lower()):
                    tareas_encontradas.append(tarea)
            
            return tareas_encontradas
            
        except Exception as e:
            print(f"❌ Error en búsqueda de tareas: {e}")
            return []
    
    def obtener_resumen_tareas(self) -> Dict[str, Any]:
        """
        Obtiene un resumen estadístico de las tareas
        
        Returns:
            Diccionario con estadísticas de tareas
        """
        try:
            todas_las_tareas = self.obtener_todas_las_tareas()
            
            # Contar por estado
            conteo_estados = {}
            for estado in EstadoTarea:
                conteo_estados[estado.value] = 0
            
            # Contar por prioridad
            conteo_prioridades = {}
            for prioridad in PrioridadTarea:
                conteo_prioridades[prioridad.value] = 0
            
            # Procesar tareas
            tareas_vencidas = 0
            for tarea in todas_las_tareas:
                # Contar estado
                conteo_estados[tarea.estado.value] += 1
                
                # Contar prioridad
                conteo_prioridades[tarea.prioridad.value] += 1
                
                # Verificar si está vencida
                if (tarea.fecha_vencimiento and 
                    tarea.fecha_vencimiento < datetime.now() and
                    tarea.estado != EstadoTarea.COMPLETADO):
                    tareas_vencidas += 1
            
            return {
                "total_tareas": len(todas_las_tareas),
                "por_estado": conteo_estados,
                "por_prioridad": conteo_prioridades,
                "tareas_vencidas": tareas_vencidas,
                "tasa_completada": (
                    conteo_estados[EstadoTarea.COMPLETADO.value] / len(todas_las_tareas) * 100
                    if todas_las_tareas else 0
                )
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo resumen: {e}")
            return {}
    
    def crear_tarea_desde_texto(self, titulo: str, prioridad: str = "Media", 
                               fecha: Optional[str] = None, estado: str = "Sin empezar", 
                               proyectos: Optional[List[str]] = None,
                               tiempo_estimado: Optional[int] = None) -> Optional[Tarea]:
        """
        Crea una nueva tarea con parámetros de texto simples (helper para main.py)
        
        Args:
            titulo: Título de la tarea
            prioridad: Prioridad como string ("Baja", "Media", "Alta", "Urgente") 
            fecha: Fecha como string YYYY-MM-DD
            estado: Estado como string 
            proyectos: Lista de nombres/IDs de proyectos
            tiempo_estimado: Tiempo estimado en minutos
        
        Returns:
            Objeto Tarea creado o None si hay error
        """
        try:
            print(f"📝 Creando nueva tarea: {titulo}")
            
            # Mapear prioridad
            prioridad_map = {
                "Baja": PrioridadTarea.BAJA,
                "Media": PrioridadTarea.MEDIA, 
                "Alta": PrioridadTarea.ALTA,
                "Urgente": PrioridadTarea.URGENTE
            }
            prioridad_enum = prioridad_map.get(prioridad, PrioridadTarea.MEDIA)
            
            # Mapear estado
            estado_map = {
                "Sin empezar": EstadoTarea.SIN_EMPEZAR,
                "Pendiente": EstadoTarea.SIN_EMPEZAR,  # Mapear Pendiente a Sin empezar
                "En curso": EstadoTarea.EN_CURSO,
                "Completado": EstadoTarea.COMPLETADO,
                # Mantener compatibilidad con valores antiguos
                "No iniciada": EstadoTarea.SIN_EMPEZAR,
                "En progreso": EstadoTarea.EN_CURSO,
                "Completada": EstadoTarea.COMPLETADO
            }
            estado_enum = estado_map.get(estado, EstadoTarea.SIN_EMPEZAR)
            
            # Procesar fecha
            fecha_vencimiento = None
            if fecha:
                try:
                    fecha_vencimiento = datetime.strptime(fecha, "%Y-%m-%d")
                except:
                    print(f"⚠️ Formato de fecha inválido: {fecha}")
                    fecha_vencimiento = None
            
            # Por ahora proyectos se manejará desde main.py
            # En versión futura se puede integrar con ProyectosService
            
            # Crear objeto Tarea
            nueva_tarea = Tarea(
                nombre=titulo,
                prioridad=prioridad_enum,
                estado=estado_enum,
                fecha_vencimiento=fecha_vencimiento,
                proyecto_ids=proyectos or [],  # Recibe IDs ya resueltos
                tiempo_estimado=tiempo_estimado
            )
            
            # Crear usando el método estándar
            tarea_creada = self.crear_tarea(nueva_tarea)
            
            if tarea_creada:
                print(f"✅ Tarea creada exitosamente:")
                print(f"   📝 Título: {titulo}")
                print(f"   ⚡ Prioridad: {prioridad}")
                if tiempo_estimado:
                    print(f"   ⏱️ Tiempo estimado: {tiempo_estimado} min")
                print(f"   🆔 ID: {tarea_creada.id}")
            
            return tarea_creada
            
        except Exception as e:
            print(f"❌ Error al crear tarea: {e}")
            return None

    def crear_tarea_inteligente(self, texto_usuario: str) -> Union[Tarea, List[Tarea], None]:
        """
        Crear tarea(s) usando análisis de lenguaje natural con IA
        
        Args:
            texto_usuario: Texto en lenguaje natural del usuario
            
        Returns:
            Tarea creada, lista de tareas creadas, o None si hay error
        """
        try:
            print(f"🤖 Analizando texto con IA: {texto_usuario[:50]}...")
            
            # Usar el servicio de IA para extraer datos
            from ia.services.gemini_service import GeminiService
            gemini_service = GeminiService()
            
            resultado_analisis = gemini_service.extraer_datos_tarea(texto_usuario)
            
            if not resultado_analisis or not resultado_analisis.get('exitosa'):
                error = resultado_analisis.get('error', 'Error desconocido') if resultado_analisis else 'No se pudo analizar'
                print(f"❌ Error en análisis IA: {error}")
                
                # Fallback: crear tarea básica
                return self.crear_tarea_desde_texto(
                    titulo=texto_usuario[:100], 
                    prioridad="Media"
                )
            
            tareas_datos = resultado_analisis.get('tareas', [])
            if not tareas_datos:
                print("⚠️ No se detectaron tareas en el análisis")
                return None
            
            tareas_creadas = []
            
            for tarea_datos in tareas_datos:
                try:
                    print(f"📝 Creando tarea: {tarea_datos.get('titulo', 'Sin título')}")
                    
                    # Resolver proyecto a ID si es necesario
                    proyecto_ids = []
                    if tarea_datos.get('proyecto'):
                        proyecto_nombre = tarea_datos['proyecto']
                        proyecto_id = self._resolver_proyecto_a_id(proyecto_nombre)
                        if proyecto_id:
                            proyecto_ids = [proyecto_id]
                        else:
                            print(f"⚠️ No se encontró proyecto '{proyecto_nombre}', se creará sin proyecto")
                    
                    tarea_creada = self.crear_tarea_desde_texto(
                        titulo=tarea_datos.get('titulo', 'Tarea sin título'),
                        prioridad=tarea_datos.get('prioridad', 'Media'),
                        fecha=tarea_datos.get('fecha_vencimiento'),
                        proyectos=proyecto_ids,
                        tiempo_estimado=tarea_datos.get('tiempo_estimado')
                    )
                    
                    if tarea_creada:
                        tareas_creadas.append(tarea_creada)
                        print(f"✅ Tarea creada: {tarea_creada.nombre} (ID: {tarea_creada.id})")
                    else:
                        print(f"❌ No se pudo crear tarea: {tarea_datos.get('titulo')}")
                        
                except Exception as e:
                    print(f"❌ Error creando tarea individual: {e}")
                    continue
            
            # Retornar resultado según cantidad de tareas
            if len(tareas_creadas) == 0:
                return None
            elif len(tareas_creadas) == 1:
                return tareas_creadas[0]
            else:
                return tareas_creadas
                
        except Exception as e:
            print(f"❌ Error en creación inteligente de tarea: {e}")
            
            # Fallback final: crear tarea básica
            try:
                return self.crear_tarea_desde_texto(
                    titulo=texto_usuario[:100],
                    prioridad="Media"
                )
            except:
                return None

    def _resolver_proyecto_a_id(self, nombre_proyecto: str) -> Optional[str]:
        """
        Convierte un nombre de proyecto a su ID de Notion
        
        Args:
            nombre_proyecto: Nombre del proyecto (ej: "Universidad", "Personal")
            
        Returns:
            ID del proyecto en Notion o None si no se encuentra
        """
        try:
            # Usar el servicio de proyectos para obtener el mapeo
            from notion.services.proyectos_service import proyectos_service
            
            if proyectos_service:
                proyectos_dict = proyectos_service.cargar_proyectos_como_diccionario()
                
                # Buscar por nombre exacto (case-insensitive)
                for nombre, proyecto_id in proyectos_dict.items():
                    if nombre.lower() == nombre_proyecto.lower():
                        print(f"🎯 Proyecto '{nombre_proyecto}' → ID: {proyecto_id}")
                        return proyecto_id
                
                # Si no se encuentra exacto, buscar parcial
                for nombre, proyecto_id in proyectos_dict.items():
                    if nombre_proyecto.lower() in nombre.lower() or nombre.lower() in nombre_proyecto.lower():
                        print(f"🎯 Proyecto '{nombre_proyecto}' → '{nombre}' (ID: {proyecto_id})")
                        return proyecto_id
                        
                print(f"❌ Proyecto '{nombre_proyecto}' no encontrado en: {list(proyectos_dict.keys())}")
                return None
            else:
                print("⚠️ Servicio de proyectos no disponible")
                return None
                
        except Exception as e:
            print(f"❌ Error resolviendo proyecto '{nombre_proyecto}': {e}")
            return None

# Instancia global del servicio
try:
    tareas_service = TareasService()
except Exception as e:
    print(f"⚠️ Error inicializando servicio de tareas: {e}")
    tareas_service = None