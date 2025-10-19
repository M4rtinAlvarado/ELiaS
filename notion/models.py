"""
Modelos de datos para Notion
Define estructuras para Tareas y Proyectos
"""
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum

class EstadoTarea(Enum):
    """Estados posibles para una tarea"""
    SIN_EMPEZAR = "Sin empezar"
    EN_CURSO = "En curso"
    COMPLETADO = "Completado"

class PrioridadTarea(Enum):
    """Niveles de prioridad para tareas"""
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"
    URGENTE = "Urgente"

class EstadoProyecto(Enum):
    """Estados posibles para un proyecto"""
    PLANIFICACION = "Planificación"
    ACTIVO = "Activo"
    PAUSADO = "Pausado"
    COMPLETADO = "Completado"
    CANCELADO = "Cancelado"

@dataclass
class PropiedadNotion:
    """Clase base para propiedades de Notion"""
    tipo: str
    valor: Any = None
    
    def to_notion_format(self) -> Dict[str, Any]:
        """Convierte la propiedad al formato de Notion API"""
        raise NotImplementedError("Debe implementarse en subclases")
    
    @classmethod
    def from_notion_format(cls, data: Dict[str, Any]) -> 'PropiedadNotion':
        """Crea la propiedad desde formato de Notion API"""
        raise NotImplementedError("Debe implementarse en subclases")

@dataclass
class PropiedadTexto(PropiedadNotion):
    """Propiedad de texto de Notion"""
    valor: str = ""
    
    def __init__(self, valor: str = "", tipo: str = "title"):
        super().__init__(tipo=tipo, valor=valor)
    
    def to_notion_format(self) -> Dict[str, Any]:
        return {
            self.tipo: [
                {
                    "text": {
                        "content": str(self.valor)
                    }
                }
            ]
        }
    
    @classmethod
    def from_notion_format(cls, data: Dict[str, Any], tipo: str = "title") -> 'PropiedadTexto':
        contenido = ""
        if data.get(tipo):
            contenido = "".join([
                bloque.get("text", {}).get("content", "") 
                for bloque in data[tipo]
            ])
        return cls(tipo=tipo, valor=contenido)

@dataclass
class PropiedadSelect(PropiedadNotion):
    """Propiedad de selección de Notion"""
    valor: str = ""
    opciones: List[str] = field(default_factory=list)
    
    def __init__(self, valor: str = "", opciones: List[str] = None):
        super().__init__(tipo="select", valor=valor)
        self.opciones = opciones or []
    
    def to_notion_format(self) -> Dict[str, Any]:
        return {
            "select": {
                "name": self.valor
            } if self.valor else None
        }
    
    @classmethod
    def from_notion_format(cls, data: Dict[str, Any]) -> 'PropiedadSelect':
        valor = ""
        if data.get("select") and data["select"]:
            valor = data["select"].get("name", "")
        return cls(valor=valor)

@dataclass
class PropiedadFecha(PropiedadNotion):
    """Propiedad de fecha de Notion"""
    fecha_fin: Optional[datetime] = None
    
    def __init__(self, valor: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
        super().__init__(tipo="date", valor=valor)
        self.fecha_fin = fecha_fin
    
    def to_notion_format(self) -> Dict[str, Any]:
        if not self.valor:
            return {"date": None}
        
        fecha_dict = {
            "start": self.valor.isoformat() if isinstance(self.valor, datetime) else self.valor
        }
        
        if self.fecha_fin:
            fecha_dict["end"] = self.fecha_fin.isoformat() if isinstance(self.fecha_fin, datetime) else self.fecha_fin
        
        return {"date": fecha_dict}
    
    @classmethod
    def from_notion_format(cls, data: Dict[str, Any]) -> 'PropiedadFecha':
        if not data.get("date"):
            return cls()
        
        fecha_data = data["date"]
        valor = None
        fecha_fin = None
        
        if fecha_data.get("start"):
            try:
                valor = datetime.fromisoformat(fecha_data["start"].replace('Z', '+00:00'))
            except:
                valor = fecha_data["start"]
        
        if fecha_data.get("end"):
            try:
                fecha_fin = datetime.fromisoformat(fecha_data["end"].replace('Z', '+00:00'))
            except:
                fecha_fin = fecha_data["end"]
        
        return cls(valor=valor, fecha_fin=fecha_fin)

@dataclass
class PropiedadRelacion(PropiedadNotion):
    """Propiedad de relación con otras páginas"""
    
    def __init__(self, valor: List[str] = None):
        super().__init__(tipo="relation", valor=valor or [])
    
    def to_notion_format(self) -> Dict[str, Any]:
        return {
            "relation": [
                {"id": page_id} for page_id in self.valor if page_id
            ]
        }
    
    @classmethod
    def from_notion_format(cls, data: Dict[str, Any]) -> 'PropiedadRelacion':
        ids = []
        if data.get("relation"):
            ids = [item.get("id", "") for item in data["relation"] if item.get("id")]
        return cls(valor=ids)

@dataclass
class PropiedadRichText(PropiedadNotion):
    """Propiedad de texto enriquecido"""
    
    def __init__(self, valor: str = ""):
        super().__init__(tipo="rich_text", valor=valor)
    
    def to_notion_format(self) -> Dict[str, Any]:
        return {
            "rich_text": [
                {
                    "text": {
                        "content": str(self.valor)
                    }
                }
            ]
        }
    
    @classmethod
    def from_notion_format(cls, data: Dict[str, Any]) -> 'PropiedadRichText':
        contenido = ""
        if data.get("rich_text"):
            contenido = "".join([
                bloque.get("text", {}).get("content", "") 
                for bloque in data["rich_text"]
            ])
        return cls(valor=contenido)

@dataclass
class PropiedadStatus(PropiedadNotion):
    """Propiedad de status de Notion"""
    
    def __init__(self, valor: str = ""):
        super().__init__(tipo="status", valor=valor)
    
    def to_notion_format(self) -> Dict[str, Any]:
        return {
            "status": {
                "name": self.valor
            } if self.valor else None
        }
    
    @classmethod
    def from_notion_format(cls, data: Dict[str, Any]) -> 'PropiedadStatus':
        valor = ""
        if data.get("status") and data["status"]:
            valor = data["status"].get("name", "")
        return cls(valor=valor)

@dataclass
class Tarea:
    """Modelo para una tarea de Notion"""
    # Identificadores
    id: Optional[str] = None
    url: Optional[str] = None
    
    # Propiedades principales
    nombre: str = ""
    descripcion: str = ""
    estado: EstadoTarea = EstadoTarea.SIN_EMPEZAR
    prioridad: PrioridadTarea = PrioridadTarea.MEDIA
    
    # Fechas
    fecha_creacion: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    fecha_completada: Optional[datetime] = None
    
    # Relaciones
    proyecto_ids: List[str] = field(default_factory=list)
    
    # Metadatos
    propiedades_raw: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_notion_page(cls, page_data: Dict[str, Any]) -> 'Tarea':
        """Crea una Tarea desde los datos de una página de Notion"""
        properties = page_data.get('properties', {})
        
        # Extraer nombre (título)
        nombre = ""
        if 'Nombre' in properties or 'Name' in properties:
            prop_nombre = properties.get('Nombre') or properties.get('Name')
            if prop_nombre and prop_nombre.get('title'):
                nombre = "".join([
                    item.get('text', {}).get('content', '') 
                    for item in prop_nombre['title']
                ])
        
        # Extraer descripción
        descripcion = ""
        if 'Descripción' in properties or 'Description' in properties:
            prop_desc = properties.get('Descripción') or properties.get('Description')
            if prop_desc and prop_desc.get('rich_text'):
                descripcion = "".join([
                    item.get('text', {}).get('content', '') 
                    for item in prop_desc['rich_text']
                ])
        
        # Extraer estado (puede ser status o select)
        estado = EstadoTarea.SIN_EMPEZAR
        if 'Estado' in properties or 'Status' in properties:
            prop_estado = properties.get('Estado') or properties.get('Status')
            estado_nombre = ""
            
            # Primero probar status
            if prop_estado and prop_estado.get('status'):
                estado_nombre = prop_estado['status'].get('name', '')
            # Fallback a select
            elif prop_estado and prop_estado.get('select'):
                estado_nombre = prop_estado['select'].get('name', '')
                
            if estado_nombre:
                try:
                    estado = EstadoTarea(estado_nombre)
                except ValueError:
                    estado = EstadoTarea.SIN_EMPEZAR
        
        # Extraer prioridad
        prioridad = PrioridadTarea.MEDIA
        if 'Prioridad' in properties or 'Priority' in properties:
            prop_prioridad = properties.get('Prioridad') or properties.get('Priority')
            if prop_prioridad and prop_prioridad.get('select'):
                prioridad_nombre = prop_prioridad['select'].get('name', '')
                try:
                    prioridad = PrioridadTarea(prioridad_nombre)
                except ValueError:
                    prioridad = PrioridadTarea.MEDIA
        
        # Extraer fechas
        fecha_vencimiento = None
        if 'Fecha' in properties or 'Due Date' in properties or 'Fecha límite' in properties:
            prop_fecha = (properties.get('Fecha') or 
                         properties.get('Due Date') or 
                         properties.get('Fecha límite'))
            if prop_fecha and prop_fecha.get('date') and prop_fecha['date'].get('start'):
                try:
                    fecha_vencimiento = datetime.fromisoformat(
                        prop_fecha['date']['start'].replace('Z', '+00:00')
                    )
                except:
                    pass
        
        # Extraer relaciones con proyectos
        proyecto_ids = []
        if 'Proyectos' in properties or 'Project' in properties or 'Proyecto' in properties:
            prop_proyecto = (properties.get('Proyectos') or 
                           properties.get('Project') or 
                           properties.get('Proyecto'))
            if prop_proyecto and prop_proyecto.get('relation'):
                proyecto_ids = [
                    item.get('id', '') for item in prop_proyecto['relation'] 
                    if item.get('id')
                ]
        
        return cls(
            id=page_data.get('id'),
            url=page_data.get('url'),
            nombre=nombre,
            descripcion=descripcion,
            estado=estado,
            prioridad=prioridad,
            fecha_creacion=datetime.fromisoformat(
                page_data.get('created_time', '').replace('Z', '+00:00')
            ) if page_data.get('created_time') else None,
            fecha_vencimiento=fecha_vencimiento,
            proyecto_ids=proyecto_ids,
            propiedades_raw=properties
        )
    
    def to_notion_properties(self) -> Dict[str, Any]:
        """Convierte la tarea al formato de propiedades de Notion"""
        propiedades = {}
        
        # Nombre (título)
        if self.nombre:
            propiedades['Nombre'] = PropiedadTexto(valor=self.nombre, tipo='title').to_notion_format()
        
        # Descripción
        if self.descripcion:
            propiedades['Descripción'] = PropiedadRichText(valor=self.descripcion).to_notion_format()
        
        # Estado (usar status, no select)
        propiedades['Estado'] = PropiedadStatus(valor=self.estado.value).to_notion_format()
        
        # Prioridad (esta sí es select)
        propiedades['Prioridad'] = PropiedadSelect(valor=self.prioridad.value).to_notion_format()
        
        # Fecha de vencimiento
        if self.fecha_vencimiento:
            propiedades['Fecha'] = PropiedadFecha(valor=self.fecha_vencimiento).to_notion_format()
        
        # Relación con proyecto (cambiar a "Proyectos")
        if self.proyecto_ids:
            propiedades['Proyectos'] = PropiedadRelacion(valor=self.proyecto_ids).to_notion_format()
        
        return propiedades
    
    def __str__(self) -> str:
        return f"Tarea: {self.nombre} ({self.estado.value}) - {self.prioridad.value}"

@dataclass
class Proyecto:
    """Modelo para un proyecto de Notion"""
    # Identificadores
    id: Optional[str] = None
    url: Optional[str] = None
    
    # Propiedades principales
    nombre: str = ""
    descripcion: str = ""
    estado: EstadoProyecto = EstadoProyecto.PLANIFICACION
    
    # Fechas
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None
    
    # Progreso
    progreso: int = 0  # Porcentaje 0-100
    
    # Metadatos
    propiedades_raw: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_notion_page(cls, page_data: Dict[str, Any]) -> 'Proyecto':
        """Crea un Proyecto desde los datos de una página de Notion"""
        properties = page_data.get('properties', {})
        
        # Extraer nombre
        nombre = ""
        if 'Nombre' in properties or 'Name' in properties:
            prop_nombre = properties.get('Nombre') or properties.get('Name')
            if prop_nombre and prop_nombre.get('title'):
                nombre = "".join([
                    item.get('text', {}).get('content', '') 
                    for item in prop_nombre['title']
                ])
        
        # Extraer descripción
        descripcion = ""
        if 'Descripción' in properties or 'Description' in properties:
            prop_desc = properties.get('Descripción') or properties.get('Description')
            if prop_desc and prop_desc.get('rich_text'):
                descripcion = "".join([
                    item.get('text', {}).get('content', '') 
                    for item in prop_desc['rich_text']
                ])
        
        # Extraer estado
        estado = EstadoProyecto.PLANIFICACION
        if 'Estado' in properties or 'Status' in properties:
            prop_estado = properties.get('Estado') or properties.get('Status')
            if prop_estado and prop_estado.get('select'):
                estado_nombre = prop_estado['select'].get('name', '')
                try:
                    estado = EstadoProyecto(estado_nombre)
                except ValueError:
                    estado = EstadoProyecto.PLANIFICACION
        
        # Extraer fechas
        fecha_inicio = None
        fecha_fin = None
        if 'Fechas' in properties or 'Dates' in properties:
            prop_fechas = properties.get('Fechas') or properties.get('Dates')
            if prop_fechas and prop_fechas.get('date'):
                fecha_data = prop_fechas['date']
                if fecha_data.get('start'):
                    try:
                        fecha_inicio = datetime.fromisoformat(
                            fecha_data['start'].replace('Z', '+00:00')
                        )
                    except:
                        pass
                if fecha_data.get('end'):
                    try:
                        fecha_fin = datetime.fromisoformat(
                            fecha_data['end'].replace('Z', '+00:00')
                        )
                    except:
                        pass
        
        # Extraer progreso
        progreso = 0
        if 'Progreso' in properties or 'Progress' in properties:
            prop_progreso = properties.get('Progreso') or properties.get('Progress')
            if prop_progreso and prop_progreso.get('number') is not None:
                progreso = int(prop_progreso['number'])
        
        return cls(
            id=page_data.get('id'),
            url=page_data.get('url'),
            nombre=nombre,
            descripcion=descripcion,
            estado=estado,
            fecha_creacion=datetime.fromisoformat(
                page_data.get('created_time', '').replace('Z', '+00:00')
            ) if page_data.get('created_time') else None,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            progreso=progreso,
            propiedades_raw=properties
        )
    
    def to_notion_properties(self) -> Dict[str, Any]:
        """Convierte el proyecto al formato de propiedades de Notion"""
        propiedades = {}
        
        # Nombre (título)
        if self.nombre:
            propiedades['Nombre'] = PropiedadTexto(valor=self.nombre, tipo='title').to_notion_format()
        
        # Descripción
        if self.descripcion:
            propiedades['Descripción'] = PropiedadRichText(valor=self.descripcion).to_notion_format()
        
        # Estado
        propiedades['Estado'] = PropiedadSelect(valor=self.estado.value).to_notion_format()
        
        # Fechas (rango)
        if self.fecha_inicio or self.fecha_fin:
            propiedades['Fechas'] = PropiedadFecha(
                valor=self.fecha_inicio, 
                fecha_fin=self.fecha_fin
            ).to_notion_format()
        
        # Progreso
        propiedades['Progreso'] = {
            "number": self.progreso
        }
        
        return propiedades
    
    def __str__(self) -> str:
        return f"Proyecto: {self.nombre} ({self.estado.value}) - {self.progreso}%"