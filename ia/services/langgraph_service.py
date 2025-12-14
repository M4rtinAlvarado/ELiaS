"""
LangGraph Service - Orquestación de flujos de trabajo con IA
Maneja el workflow de procesamiento de consultas naturales usando LangGraph
"""
from typing import Dict, Any, Optional, List, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

# Importar servicios
from notion.services.proyectos_service import ProyectosService  
from notion.services.tareas_service import TareasService
from ia.services.gemini_service import GeminiService

class EliasState(TypedDict):
    """Estado del grafo de LangGraph para ELiaS"""
    messages: List[Any]
    user_query: str
    verified_data: Dict[str, Any]
    processing_step: str
    final_response: str
    intencion: Optional[str]

class LangGraphService:
    """
    Servicio de LangGraph para orquestación de flujos de IA
    Maneja el workflow completo de procesamiento de consultas
    """
    
    def __init__(self):
        """Inicializa el servicio LangGraph"""
        self._proyectos_service = None
        self._tareas_service = None
        self._eventos_service = None
        self._gemini_service = None
        self._workflow = None
        
        # Verificar disponibilidad de LangGraph
        self._langgraph_disponible = self._verificar_langgraph()
    
    def _verificar_langgraph(self) -> bool:
        """Verifica si LangGraph está disponible"""
        try:
            import langgraph
            return True
        except ImportError:
            print("❌ LangGraph no disponible. Instala con: pip install langgraph")
            return False
    
    @property
    def proyectos_service(self):
        """Lazy loading del servicio de proyectos"""
        if self._proyectos_service is None:
            self._proyectos_service = ProyectosService()
        return self._proyectos_service
    
    @property
    def tareas_service(self):
        """Lazy loading del servicio de tareas"""
        if self._tareas_service is None:
            self._tareas_service = TareasService()
        return self._tareas_service
    
    @property
    def eventos_service(self):
        """Lazy loading del servicio de eventos"""
        if self._eventos_service is None:
            from notion.services.eventos_service import EventosService
            try:
                self._eventos_service = EventosService()
            except Exception as e:
                print(f"⚠️ EventosService no disponible: {e}")
                self._eventos_service = None
        return self._eventos_service
    
    @property
    def gemini_service(self):
        """Lazy loading del servicio de Gemini"""
        if self._gemini_service is None:
            self._gemini_service = GeminiService()
        return self._gemini_service
    
    # ===== NODOS DEL WORKFLOW =====
    
    def nodo_decisor_intencion(self, state: EliasState) -> EliasState:
        """NODO DECISOR: Determina si el usuario quiere crear tarea, evento, consultar o ambas"""
        consulta = state["user_query"]
        
        try:
            # Usar servicio modular de Gemini
            resultado = self.gemini_service.clasificar_intencion(consulta)
            
            if resultado['exitosa']:
                intencion = resultado['intencion'].lower()
                confianza = resultado['confianza'] / 100 if resultado['confianza'] > 1 else resultado['confianza']
                razonamiento = resultado['razonamiento']
                
                print(f"🧠 Decisor IA (Modular): {intencion.upper()} (confianza: {confianza:.0%})")
                print(f"💭 Razonamiento: {razonamiento}")
                
                return {
                    **state,
                    "intencion": intencion,
                    "processing_step": f"decision_{intencion}",
                    "messages": state.get("messages", []) + [
                        SystemMessage(content=f"Intención detectada: {intencion} (confianza: {confianza:.0%})")
                    ]
                }
            
        except Exception as e:
            print(f"⚠️ Error en decisor, usando fallback: {e}")
            # Fallback simple basado en keywords
            if any(palabra in consulta.lower() for palabra in ["crear", "nueva", "agregar", "hacer", "añadir"]):
                intencion = "crear"
            else:
                intencion = "consultar"
            
            return {
                **state,
                "intencion": intencion,
                "processing_step": f"fallback_{intencion}",
                "messages": state.get("messages", []) + [
                    SystemMessage(content=f"Intención detectada por fallback: {intencion}")
                ]
            }
    
    def nodo_crear_tarea(self, state: EliasState) -> EliasState:
        """NODO: Crear nueva tarea usando servicios modulares"""
        consulta = state["user_query"]
        
        try:
            print("✨ Procesando creación de tarea...")
            
            # Usar el servicio inteligente de tareas (con análisis IA)
            resultado = self.tareas_service.crear_tarea_inteligente(consulta)
            
            if resultado and hasattr(resultado, 'nombre'):
                # Una sola tarea creada (formato tradicional)
                respuesta = f"✅ **Tarea creada exitosamente**\n\n"
                respuesta += f"📝 **Título:** {resultado.nombre}\n"
                respuesta += f"⚡ **Prioridad:** {resultado.prioridad.value if hasattr(resultado.prioridad, 'value') else resultado.prioridad}\n"
                respuesta += f"📊 **Estado:** {resultado.estado.value if hasattr(resultado.estado, 'value') else resultado.estado}\n"
                
                if hasattr(resultado, 'tiempo_estimado') and resultado.tiempo_estimado:
                    respuesta += f"⏱️ **Tiempo Estimado:** {resultado.tiempo_estimado} min\n"
                
                if hasattr(resultado, 'fecha_vencimiento') and resultado.fecha_vencimiento:
                    respuesta += f"📅 **Vencimiento:** {resultado.fecha_vencimiento.strftime('%d/%m/%Y')}\n"
                
                if hasattr(resultado, 'proyecto_ids') and resultado.proyecto_ids:
                    respuesta += f"📁 **Proyecto:** {resultado.proyecto_ids[0]}\n"
                
                if hasattr(resultado, 'id') and resultado.id:
                    respuesta += f"🆔 **ID:** `{resultado.id}`\n"
                    
                # Agregar link a Notion si está configurado
                try:
                    from config import settings
                    if settings.NOTION_DATABASE_TAREAS_ID:
                        link_notion = f"https://www.notion.so/{settings.NOTION_DATABASE_TAREAS_ID.replace('-', '')}"
                        respuesta += f"\n🔗 [Ver todas las tareas en Notion]({link_notion})"
                except:
                    pass
                    
                respuesta += f"\n\n💡 *Tip: Ahora puedes usar lenguaje natural como 'estudiar matemáticas mañana por 2 horas'*"
                print(f"✅ {respuesta}")
                
                return {
                    **state,
                    "final_response": respuesta,
                    "processing_step": "tarea_creada"
                }
            
            elif isinstance(resultado, list) and len(resultado) > 0:
                # Múltiples tareas creadas
                tareas_exitosas = [t for t in resultado if t and hasattr(t, 'nombre')]
                
                if len(tareas_exitosas) == 1:
                    tarea = tareas_exitosas[0]
                    respuesta = f"✅ Tarea creada exitosamente: '{tarea.nombre}'"
                    if hasattr(tarea, 'id') and tarea.id:
                        respuesta += f" (ID: {tarea.id})"
                elif len(tareas_exitosas) > 1:
                    respuesta = f"✅ **{len(tareas_exitosas)} tareas creadas exitosamente**\n\n"
                    for i, tarea in enumerate(tareas_exitosas, 1):
                        respuesta += f"**{i}.** {tarea.nombre}\n"
                        respuesta += f"   ⚡ {tarea.prioridad.value if hasattr(tarea.prioridad, 'value') else tarea.prioridad}"
                        
                        if hasattr(tarea, 'tiempo_estimado') and tarea.tiempo_estimado:
                            respuesta += f" | ⏱️ {tarea.tiempo_estimado}min"
                        
                        if hasattr(tarea, 'fecha_vencimiento') and tarea.fecha_vencimiento:
                            respuesta += f" | 📅 {tarea.fecha_vencimiento.strftime('%d/%m/%Y')}"
                            
                        if hasattr(tarea, 'proyecto_ids') and tarea.proyecto_ids:
                            respuesta += f" | 📁 {tarea.proyecto_ids[0]}"
                            
                        if hasattr(tarea, 'id') and tarea.id:
                            respuesta += f"\n   🆔 ID: `{tarea.id}`"
                        respuesta += "\n\n"
                    
                    # Agregar link a Notion
                    try:
                        from config import settings
                        if settings.NOTION_DATABASE_TAREAS_ID:
                            link_notion = f"https://www.notion.so/{settings.NOTION_DATABASE_TAREAS_ID.replace('-', '')}"
                            respuesta += f"🔗 [Ver todas las tareas en Notion]({link_notion})"
                    except:
                        pass
                else:
                    respuesta = "❌ Error al crear las tareas"
                
                print(f"✅ {respuesta}")
                
                return {
                    **state,
                    "final_response": respuesta,
                    "processing_step": "tareas_creadas"
                }
                
            else:
                respuesta = "❌ Error al crear la tarea"
                print(respuesta)
                
                return {
                    **state,
                    "final_response": respuesta,
                    "processing_step": "error_creacion"
                }
            
        except Exception as e:
            error_msg = f"❌ Error inesperado al crear tarea: {e}"
            print(error_msg)
            return {
                **state,
                "final_response": error_msg,
                "processing_step": "error_creacion"
            }
    
    def nodo_consultar_tareas(self, state: EliasState) -> EliasState:
        """NODO: Consultar y mostrar tareas existentes"""
        try:
            print("📋 Consultando tareas existentes...")
            
            # Obtener tareas usando servicio
            tareas = self.tareas_service.obtener_todas_las_tareas()
            
            if not tareas:
                respuesta = "📭 No tienes tareas registradas en Notion."
                print(respuesta)
                return {
                    **state,
                    "final_response": respuesta,
                    "verified_data": {"tareas_count": 0},
                    "processing_step": "sin_tareas"
                }
            
            # Procesar y formatear tareas
            tareas_formateadas = self._formatear_tareas_para_consulta(tareas)
            
            # Generar respuesta usando IA
            respuesta = self._generar_respuesta_consulta(state["user_query"], tareas_formateadas)
            
            return {
                **state,
                "final_response": respuesta,
                "verified_data": {"tareas_count": len(tareas), "tareas": tareas_formateadas},
                "processing_step": "consulta_completada"
            }
            
        except Exception as e:
            error_msg = f"❌ Error al consultar tareas: {e}"
            print(error_msg)
            return {
                **state,
                "final_response": error_msg,
                "processing_step": "error_consulta"
            }
    
    def _formatear_tareas_para_consulta(self, tareas: List[Any]) -> List[Dict]:
        """Formatea las tareas para consulta con información legible"""
        tareas_formateadas = []
        
        for i, tarea in enumerate(tareas, 1):
            # Los objetos Tarea ya tienen propiedades bien estructuradas
            nombre = tarea.nombre if tarea.nombre else "Sin título"
            prioridad = tarea.prioridad.value if tarea.prioridad else "Sin prioridad"
            estado = tarea.estado.value if tarea.estado else "Sin estado"
            
            # Obtener nombres de proyectos
            proyecto = "Sin proyecto"
            if tarea.proyecto_ids:
                nombres_proyectos = []
                for proyecto_id in tarea.proyecto_ids:
                    nombre_proyecto = self.proyectos_service.obtener_nombre_por_id(proyecto_id)
                    if nombre_proyecto:
                        nombres_proyectos.append(nombre_proyecto)
                
                if nombres_proyectos:
                    proyecto = ", ".join(nombres_proyectos)
            
            # Fecha de vencimiento si existe
            fecha = "Sin fecha"
            if tarea.fecha_vencimiento:
                fecha = tarea.fecha_vencimiento.strftime("%Y-%m-%d") if hasattr(tarea.fecha_vencimiento, 'strftime') else str(tarea.fecha_vencimiento)
            
            tarea_formateada = {
                "numero": i,
                "nombre": nombre,
                "prioridad": prioridad,
                "estado": estado,
                "proyecto": proyecto,
                "fecha": fecha
            }
            
            tareas_formateadas.append(tarea_formateada)
        
        return tareas_formateadas
    
    def _generar_respuesta_consulta(self, consulta: str, tareas: List[Dict]) -> str:
        """Genera respuesta inteligente para consultas de tareas"""
        try:
            # Preparar contexto para IA
            contexto = f"Consulta del usuario: {consulta}\n\n"
            contexto += f"Tareas disponibles ({len(tareas)}):\n"
            
            for tarea in tareas:
                contexto += f"- {tarea['nombre']} ({tarea['estado']}) - {tarea['proyecto']}\n"
            
            # Generar respuesta usando Gemini con instrucciones específicas
            prompt_completo = f"""Consulta: {consulta}

Contexto:
{contexto}

INSTRUCCIONES:
- Responde de forma natural y conversacional
- USA formato Markdown para Telegram (negritas: *texto*, cursivas: _texto_)
- NO uses caracteres especiales sin escapar
- Estructura la respuesta con emojis y formato claro
- Si hay muchas tareas, resume las más importantes
- Incluye un tip útil al final

Respuesta:"""
            
            resultado = self.gemini_service.generar_texto_libre(
                texto_prompt=prompt_completo,
                temperatura=0.3
            )
            
            if resultado.exitosa and resultado.texto:
                # Verificar que la respuesta no tenga caracteres problemáticos sin escapar
                respuesta = resultado.texto.strip()
                
                # Si la respuesta tiene problemas de formato, usar fallback
                if len(respuesta) > 4000 or '\\' in respuesta:
                    print("⚠️ Respuesta IA demasiado larga o con caracteres problemáticos, usando fallback")
                    return self._generar_respuesta_simple(tareas)
                
                return respuesta
            else:
                # Fallback a respuesta simple
                return self._generar_respuesta_simple(tareas)
                
        except Exception as e:
            print(f"⚠️ Error generando respuesta IA: {e}")
            return self._generar_respuesta_simple(tareas)
    
    def _escape_markdown(self, texto: str) -> str:
        """Escapa caracteres especiales para Markdown de Telegram"""
        if not texto:
            return ""
        
        # Caracteres que necesitan escape en Telegram Markdown
        caracteres_especiales = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in caracteres_especiales:
            texto = texto.replace(char, f'\\{char}')
        
        return texto
    
    def _generar_respuesta_simple(self, tareas: List[Dict]) -> str:
        """Genera respuesta simple sin IA con texto safe para Telegram"""
        total = len(tareas)
        respuesta = f"📊 *Tienes {total} tarea{'s' if total != 1 else ''} registrada{'s' if total != 1 else ''}:*\n\n"
        
        for tarea in tareas[:5]:  # Mostrar máximo 5
            # Escapar caracteres especiales para Markdown
            nombre_safe = self._escape_markdown(tarea['nombre'])
            estado_safe = self._escape_markdown(tarea['estado'])
            proyecto_safe = self._escape_markdown(tarea['proyecto'])
            
            respuesta += f"• *{nombre_safe}* ({estado_safe})\n"
            respuesta += f"  📁 {proyecto_safe}\n"
            
            if tarea['fecha'] != "Sin fecha":
                fecha_safe = self._escape_markdown(tarea['fecha'])
                respuesta += f"  📅 {fecha_safe}\n"
            
            respuesta += "\n"
        
        if total > 5:
            respuesta += f"... y *{total - 5}* tarea{'s' if total - 5 != 1 else ''} más\n\n"
        
        respuesta += "💡 _Usa 'crear tarea: [descripción]' para agregar nuevas tareas_"
        
        return respuesta
    
    # ===== NODO CREAR EVENTO =====
    
    def nodo_crear_evento(self, state: EliasState) -> EliasState:
        """NODO: Crear nuevo evento usando servicios modulares"""
        consulta = state["user_query"]
        
        try:
            print("📅 Procesando creación de evento...")
            
            # Verificar si el servicio de eventos está disponible
            if not self.eventos_service:
                return {
                    **state,
                    "final_response": "❌ El servicio de eventos no está configurado. Añade NOTION_DB_EVENTOS en tu archivo .env",
                    "processing_step": "error_config_eventos"
                }
            
            # Crear evento usando el servicio inteligente
            resultado = self.eventos_service.crear_evento_inteligente(consulta)
            
            if resultado and hasattr(resultado, 'nombre'):
                respuesta = f"✅ **Evento creado exitosamente**\n\n"
                respuesta += f"📅 **Nombre:** {resultado.nombre}\n"
                respuesta += f"📌 **Tipo:** {resultado.tipo.value if hasattr(resultado.tipo, 'value') else resultado.tipo}\n"
                respuesta += f"📊 **Estado:** {resultado.estado.value if hasattr(resultado.estado, 'value') else resultado.estado}\n"
                
                if hasattr(resultado, 'fecha') and resultado.fecha:
                    respuesta += f"🗓️ **Fecha:** {resultado.fecha.strftime('%d/%m/%Y %H:%M')}\n"
                
                if hasattr(resultado, 'fecha_fin') and resultado.fecha_fin:
                    respuesta += f"⏰ **Hasta:** {resultado.fecha_fin.strftime('%d/%m/%Y %H:%M')}\n"
                
                if hasattr(resultado, 'ubicacion') and resultado.ubicacion:
                    respuesta += f"📍 **Ubicación:** {resultado.ubicacion}\n"
                
                if hasattr(resultado, 'id') and resultado.id:
                    respuesta += f"🆔 **ID:** `{resultado.id}`\n"
                
                respuesta += f"\n💡 *Tip: Puedes decir 'reunión mañana a las 3pm' o 'cita con el doctor el viernes'*"
                print(f"✅ Evento creado: {resultado.nombre}")
                
                return {
                    **state,
                    "final_response": respuesta,
                    "processing_step": "evento_creado"
                }
            else:
                respuesta = "❌ Error al crear el evento"
                print(respuesta)
                
                return {
                    **state,
                    "final_response": respuesta,
                    "processing_step": "error_creacion_evento"
                }
                
        except Exception as e:
            error_msg = f"❌ Error inesperado al crear evento: {e}"
            print(error_msg)
            return {
                **state,
                "final_response": error_msg,
                "processing_step": "error_creacion_evento"
            }
    
    # ===== FUNCIONES DE DECISIÓN =====
    
    def decidir_siguiente_nodo(self, state: EliasState) -> str:
        """Decide el siguiente nodo basado en la intención"""
        intencion = state.get("intencion", "consultar")
        
        # Normalizar la intención
        intencion_lower = intencion.lower().replace("_", " ")
        
        if "crear_evento" in intencion or "crear evento" in intencion_lower or intencion_lower == "crear_evento":
            return "crear_evento"
        elif "crear_tarea" in intencion or "crear tarea" in intencion_lower or intencion in ["crear", "nueva", "agregar"]:
            return "crear_tarea"
        else:
            return "consultar_tareas"
    
    # ===== CREACIÓN DEL WORKFLOW =====
    
    def crear_workflow(self) -> Optional[Any]:
        """Crea y compila el workflow de LangGraph"""
        if not self._langgraph_disponible:
            return None
        
        try:
            workflow = StateGraph(EliasState)
            
            # Añadir nodos
            workflow.add_node("decisor", self.nodo_decisor_intencion)
            workflow.add_node("crear_tarea", self.nodo_crear_tarea)
            workflow.add_node("crear_evento", self.nodo_crear_evento)
            workflow.add_node("consultar_tareas", self.nodo_consultar_tareas)
            
            # Flujo condicional
            workflow.set_entry_point("decisor")
            workflow.add_conditional_edges(
                "decisor",
                self.decidir_siguiente_nodo,
                {
                    "crear_tarea": "crear_tarea",
                    "crear_evento": "crear_evento",
                    "consultar_tareas": "consultar_tareas"
                }
            )
            workflow.add_edge("crear_tarea", END)
            workflow.add_edge("crear_evento", END)
            workflow.add_edge("consultar_tareas", END)
            
            print("✅ Workflow de LangGraph compilado exitosamente (con soporte de eventos)")
            return workflow.compile()
            
        except Exception as e:
            print(f"❌ Error al crear workflow: {e}")
            return None
    
    def procesar_consulta(self, pregunta: str) -> str:
        """
        Función principal para procesar consultas en lenguaje natural
        """
        print(f"🔍 Procesando consulta: {pregunta}")
        
        # Crear o reutilizar workflow
        if self._workflow is None:
            self._workflow = self.crear_workflow()
        
        if not self._workflow:
            return "❌ Error: Sistema LangGraph no disponible"
        
        # Estado inicial
        estado_inicial = {
            "messages": [],
            "user_query": pregunta,
            "verified_data": {},
            "processing_step": "inicio",
            "final_response": "",
            "intencion": None
        }
        
        try:
            # Ejecutar el grafo
            print("🚀 Ejecutando workflow LangGraph...")
            resultado = self._workflow.invoke(estado_inicial)
            
            respuesta_final = resultado.get("final_response", "No se pudo generar respuesta")
            print(f"✅ Procesamiento completado")
            
            return respuesta_final
            
        except Exception as e:
            error_msg = f"❌ Error en workflow LangGraph: {e}"
            print(error_msg)
            return error_msg
    
    def diagnosticar_sistema(self) -> bool:
        """Diagnostica el estado del sistema LangGraph"""
        try:
            print("🔧 Diagnosticando sistema LangGraph...")
            
            # Verificar LangGraph
            if not self._langgraph_disponible:
                print("❌ LangGraph no disponible")
                return False
            
            # Verificar servicios
            try:
                tareas = self.tareas_service.obtener_todas_las_tareas()
                total = len(tareas) if tareas else 0
                print(f"✅ Sistema funcionando - {total} tareas detectadas")
                return True
            except Exception as e:
                print(f"❌ Error accediendo a servicios: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error en diagnóstico: {e}")
            return False