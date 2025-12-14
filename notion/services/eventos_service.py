"""
Servicio para gestión de eventos en Notion
Operaciones CRUD y lógica de negocio para eventos
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..client import notion_client, NotionConnectionError, NotionValidationError
from ..models import Evento, EstadoEvento, TipoEvento
from config import settings

class EventosService:
    """Servicio para operaciones con eventos en Notion"""
    
    def __init__(self):
        """Inicializa el servicio con validaciones"""
        if not notion_client:
            raise NotionConnectionError("Cliente Notion no disponible")
        
        if not settings.NOTION_DB_EVENTOS:
            raise NotionValidationError("Base de datos de eventos no configurada (NOTION_DB_EVENTOS)")
        
        self.client = notion_client
        self.db_id = settings.NOTION_DB_EVENTOS
    
    def obtener_todos_los_eventos(self, filtros: Optional[Dict[str, Any]] = None) -> List[Evento]:
        """
        Obtiene todos los eventos de la base de datos
        
        Args:
            filtros: Filtros opcionales para la consulta
        
        Returns:
            Lista de objetos Evento
        """
        try:
            query_params = {}
            
            if filtros:
                query_params['filter'] = filtros
            
            # Ordenar por fecha ascendente (próximos primero)
            query_params['sorts'] = [
                {
                    "property": "Fecha",
                    "direction": "ascending"
                }
            ]
            
            response = self.client.query_database(self.db_id, **query_params)
            
            eventos = []
            for page in response.get('results', []):
                try:
                    evento = Evento.from_notion_page(page)
                    eventos.append(evento)
                except Exception as e:
                    print(f"⚠️ Error procesando evento {page.get('id', 'unknown')}: {e}")
            
            return eventos
            
        except Exception as e:
            raise NotionConnectionError(f"Error obteniendo eventos: {e}")
    
    def obtener_evento_por_id(self, evento_id: str) -> Optional[Evento]:
        """
        Obtiene un evento específico por su ID
        
        Args:
            evento_id: ID del evento en Notion
        
        Returns:
            Objeto Evento o None si no se encuentra
        """
        try:
            page_data = self.client.get_page(evento_id)
            return Evento.from_notion_page(page_data)
            
        except Exception as e:
            print(f"⚠️ Error obteniendo evento {evento_id}: {e}")
            return None
    
    def crear_evento(self, evento: Evento) -> Optional[Evento]:
        """
        Crea un nuevo evento en Notion
        
        Args:
            evento: Objeto Evento con los datos a crear
        
        Returns:
            Objeto Evento creado con ID asignado o None si falla
        """
        try:
            # Validar datos mínimos
            if not evento.nombre:
                raise NotionValidationError("El nombre del evento es requerido")
            
            # Preparar datos para crear página
            page_data = {
                "parent": {"database_id": self.db_id},
                "properties": evento.to_notion_properties()
            }
            
            # Crear página
            response = self.client.create_page(**page_data)
            
            # Retornar evento con datos actualizados
            return Evento.from_notion_page(response)
            
        except Exception as e:
            print(f"❌ Error creando evento: {e}")
            return None
    
    def actualizar_evento(self, evento: Evento) -> Optional[Evento]:
        """
        Actualiza un evento existente
        
        Args:
            evento: Objeto Evento con datos actualizados
        
        Returns:
            Objeto Evento actualizado o None si falla
        """
        try:
            if not evento.id:
                raise NotionValidationError("ID de evento es requerido para actualizar")
            
            properties = evento.to_notion_properties()
            
            response = self.client.update_page(
                page_id=evento.id,
                properties=properties
            )
            
            return Evento.from_notion_page(response)
            
        except Exception as e:
            print(f"❌ Error actualizando evento: {e}")
            return None
    
    def cambiar_estado_evento(self, evento_id: str, nuevo_estado: EstadoEvento) -> Optional[Evento]:
        """
        Cambia el estado de un evento específico
        
        Args:
            evento_id: ID del evento
            nuevo_estado: Nuevo estado para el evento
        
        Returns:
            Objeto Evento actualizado o None si falla
        """
        try:
            evento = self.obtener_evento_por_id(evento_id)
            if not evento:
                return None
            
            evento.estado = nuevo_estado
            return self.actualizar_evento(evento)
            
        except Exception as e:
            print(f"❌ Error cambiando estado de evento: {e}")
            return None
    
    def obtener_eventos_por_estado(self, estado: EstadoEvento) -> List[Evento]:
        """
        Obtiene eventos filtrados por estado
        
        Args:
            estado: Estado a filtrar
        
        Returns:
            Lista de eventos con el estado especificado
        """
        filtro = {
            "property": "Estado",
            "status": {
                "equals": estado.value
            }
        }
        
        return self.obtener_todos_los_eventos(filtros=filtro)
    
    def obtener_eventos_por_tipo(self, tipo: TipoEvento) -> List[Evento]:
        """
        Obtiene eventos filtrados por tipo
        
        Args:
            tipo: Tipo a filtrar
        
        Returns:
            Lista de eventos con el tipo especificado
        """
        filtro = {
            "property": "Tipo",
            "select": {
                "equals": tipo.value
            }
        }
        
        return self.obtener_todos_los_eventos(filtros=filtro)
    
    def obtener_proximos_eventos(self, dias: int = 7) -> List[Evento]:
        """
        Obtiene eventos próximos en los siguientes N días
        
        Args:
            dias: Número de días a buscar (default: 7)
        
        Returns:
            Lista de eventos próximos
        """
        from datetime import timedelta
        
        hoy = datetime.now().date().isoformat()
        fecha_limite = (datetime.now() + timedelta(days=dias)).date().isoformat()
        
        filtro = {
            "and": [
                {
                    "property": "Fecha",
                    "date": {
                        "on_or_after": hoy
                    }
                },
                {
                    "property": "Fecha",
                    "date": {
                        "on_or_before": fecha_limite
                    }
                },
                {
                    "property": "Estado",
                    "status": {
                        "does_not_equal": EstadoEvento.CANCELADO.value
                    }
                }
            ]
        }
        
        return self.obtener_todos_los_eventos(filtros=filtro)
    
    def obtener_eventos_hoy(self) -> List[Evento]:
        """
        Obtiene eventos programados para hoy
        
        Returns:
            Lista de eventos de hoy
        """
        hoy = datetime.now().date().isoformat()
        
        filtro = {
            "and": [
                {
                    "property": "Fecha",
                    "date": {
                        "equals": hoy
                    }
                },
                {
                    "property": "Estado",
                    "status": {
                        "does_not_equal": EstadoEvento.CANCELADO.value
                    }
                }
            ]
        }
        
        return self.obtener_todos_los_eventos(filtros=filtro)
    
    def obtener_eventos_por_proyecto(self, proyecto_id: str) -> List[Evento]:
        """
        Obtiene eventos asociados a un proyecto específico
        
        Args:
            proyecto_id: ID del proyecto en Notion
        
        Returns:
            Lista de eventos del proyecto
        """
        filtro = {
            "property": "Proyectos",
            "relation": {
                "contains": proyecto_id
            }
        }
        
        return self.obtener_todos_los_eventos(filtros=filtro)
    
    def crear_evento_inteligente(self, texto_usuario: str) -> Optional[Evento]:
        """
        Crea un evento usando IA para extraer datos del texto natural
        
        Args:
            texto_usuario: Descripción en lenguaje natural del evento
        
        Returns:
            Evento creado o None si falla
        """
        try:
            from ia.services.gemini_service import GeminiService
            from ia.models import Prompt
            
            gemini = GeminiService()
            if not gemini.disponible:
                print("⚠️ Gemini no disponible, creando evento básico")
                return self.crear_evento(Evento(nombre=texto_usuario))
            
            # Usar prompt especializado para eventos
            prompt = Prompt.crear_evento(texto_usuario)
            respuesta = gemini.generar_respuesta(prompt)
            
            if respuesta.exitosa and respuesta.json_extraido:
                datos = respuesta.json_extraido
                
                # Extraer datos del JSON
                nombre = datos.get('nombre', texto_usuario)
                
                # Parsear fecha
                fecha = None
                fecha_str = datos.get('fecha')
                if fecha_str:
                    try:
                        fecha = datetime.fromisoformat(fecha_str)
                    except:
                        pass
                
                # Parsear tipo
                tipo = TipoEvento.OTRO
                tipo_str = datos.get('tipo', '')
                if tipo_str:
                    try:
                        tipo = TipoEvento(tipo_str)
                    except ValueError:
                        tipo = TipoEvento.OTRO
                
                ubicacion = datos.get('ubicacion', '')
                
                evento = Evento(
                    nombre=nombre,
                    fecha=fecha,
                    tipo=tipo,
                    ubicacion=ubicacion,
                    estado=EstadoEvento.PROGRAMADO
                )
                
                return self.crear_evento(evento)
            
            # Fallback: crear evento básico
            return self.crear_evento(Evento(nombre=texto_usuario))
            
        except Exception as e:
            print(f"❌ Error creando evento inteligente: {e}")
            return None
    
    def eliminar_evento(self, evento_id: str) -> bool:
        """
        Archiva (elimina lógicamente) un evento
        
        Args:
            evento_id: ID del evento a eliminar
        
        Returns:
            True si se archivó correctamente, False en caso contrario
        """
        try:
            self.client.update_page(
                page_id=evento_id,
                archived=True
            )
            return True
        except Exception as e:
            print(f"❌ Error eliminando evento: {e}")
            return False


# Instancia global del servicio (lazy initialization)
_eventos_service = None

def get_eventos_service() -> EventosService:
    """Obtiene la instancia del servicio de eventos"""
    global _eventos_service
    if _eventos_service is None:
        _eventos_service = EventosService()
    return _eventos_service

# Para compatibilidad con el patrón existente
try:
    eventos_service = EventosService()
except Exception as e:
    eventos_service = None
    print(f"⚠️ EventosService no inicializado: {e}")
