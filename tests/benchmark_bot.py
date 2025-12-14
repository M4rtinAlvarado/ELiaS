#!/usr/bin/env python3
"""
Benchmark de ELiaS Bot - Test de Respuestas Completo
=====================================================

Ejecuta un conjunto de preguntas al bot y guarda las respuestas
para evaluar el funcionamiento del sistema.

Uso:
    python tests/benchmark_bot.py                    # Ejecutar todo
    python tests/benchmark_bot.py --guardar-notion   # Crear tareas/eventos reales
    python tests/benchmark_bot.py --rapido           # Solo clasificación (sin crear)
    python tests/benchmark_bot.py --categoria crear  # Solo una categoría
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()


# ============================================================================
# BANCO DE PREGUNTAS DE PRUEBA
# ============================================================================

PREGUNTAS_BENCHMARK = {
    "crear_tarea": [
        # Tareas simples
        "Tengo que estudiar matemáticas mañana",
        "Comprar leche y pan",
        "Necesito llamar al doctor esta semana",
        "Hacer ejercicio 30 minutos",
        # Tareas con proyecto
        "Para la universidad: entregar trabajo de historia",
        "Proyecto personal: organizar el closet",
        # Tareas con prioridad
        "Urgente: revisar el código del proyecto",
        "Tarea importante: preparar presentación",
        # Tareas con tiempo estimado
        "Estudiar física por 2 horas",
        "Revisar documentación durante 45 minutos",
        # Tareas múltiples
        "Necesito comprar vitaminas y hacer ejercicio mañana",
    ],
    
    "crear_evento": [
        # Eventos con hora
        "Reunión con el equipo mañana a las 3pm",
        "Cita con el doctor el viernes a las 10am",
        "Clase de inglés mañana de 5 a 7 de la tarde",
        # Eventos sociales
        "El cumpleaños de Juan es el sábado",
        "Fiesta de navidad el 24 de diciembre",
        # Eventos académicos
        "Examen de cálculo el lunes a las 8am",
        "Exposición del proyecto el miércoles a las 2pm",
        # Eventos con ubicación
        "Reunión en la oficina central mañana a las 9",
        "Cita en el hospital Santa María el jueves a las 11",
    ],
    
    "consultar": [
        # Consultas de tareas
        "¿Cuántas tareas tengo pendientes?",
        "Muéstrame todas mis tareas",
        "¿Qué tareas tengo para hoy?",
        "Listar tareas del proyecto Universidad",
        # Consultas de eventos
        "¿Qué eventos tengo esta semana?",
        "Próximos eventos",
        "¿Tengo alguna reunión programada?",
        # Consultas generales
        "Dame un resumen de mis tareas",
        "¿Cuáles son mis proyectos?",
        "Estado del sistema",
    ],
    
    "ambiguo": [
        # Saludos
        "Hola",
        "Buenos días",
        "¿Qué tal?",
        # Preguntas genéricas
        "¿Qué puedes hacer?",
        "Ayuda",
        "¿Cómo funciona esto?",
    ],
    
    "mixto": [
        # Combinaciones complejas
        "Tengo examen mañana a las 8, necesito estudiar hoy 3 horas",
        "Reunión el viernes y preparar documentos para ella",
        "¿Cuántas tareas tengo? También agrega comprar café",
    ],
}


# ============================================================================
# CLASE PRINCIPAL DE BENCHMARK
# ============================================================================

class BenchmarkBot:
    """Ejecuta benchmark completo del bot ELiaS"""
    
    def __init__(self, guardar_notion: bool = False):
        self.guardar_notion = guardar_notion
        self.resultados: List[Dict[str, Any]] = []
        self.stats = {
            "total": 0,
            "exitosas": 0,
            "fallidas": 0,
            "por_categoria": {},
            "por_intencion_detectada": {},
            "tiempo_total": 0.0,
        }
        
        # Inicializar servicios
        self._init_services()
    
    def _init_services(self):
        """Inicializa los servicios necesarios"""
        print("🔧 Inicializando servicios...")
        
        self.gemini_service = None
        self.langgraph_service = None
        self.tareas_service = None
        self.eventos_service = None
        
        try:
            from ia.services.gemini_service import GeminiService
            self.gemini_service = GeminiService()
            if self.gemini_service.disponible:
                print("  ✅ GeminiService disponible")
            else:
                print("  ⚠️ GeminiService no disponible")
                self.gemini_service = None
        except Exception as e:
            print(f"  ❌ Error GeminiService: {e}")
        
        try:
            from ia.services.langgraph_service import LangGraphService
            self.langgraph_service = LangGraphService()
            print("  ✅ LangGraphService disponible")
        except Exception as e:
            print(f"  ⚠️ LangGraphService no disponible: {e}")
        
        try:
            from notion.services.tareas_service import TareasService
            self.tareas_service = TareasService()
            print("  ✅ TareasService disponible")
        except Exception as e:
            print(f"  ⚠️ TareasService no disponible: {e}")
        
        try:
            from notion.services.eventos_service import EventosService
            self.eventos_service = EventosService()
            print("  ✅ EventosService disponible")
        except Exception as e:
            print(f"  ⚠️ EventosService no disponible: {e}")
        
        print()
    
    def clasificar_intencion(self, query: str) -> Dict[str, Any]:
        """Clasifica la intención de una consulta"""
        if not self.gemini_service:
            return {"error": "GeminiService no disponible"}
        
        try:
            resultado = self.gemini_service.clasificar_intencion(query)
            return resultado
        except Exception as e:
            return {"error": str(e)}
    
    def procesar_consulta_completa(self, query: str) -> Dict[str, Any]:
        """Procesa una consulta completa con LangGraph"""
        if not self.langgraph_service:
            return {"error": "LangGraphService no disponible", "respuesta": None}
        
        try:
            respuesta = self.langgraph_service.procesar_consulta(query)
            return {"respuesta": respuesta, "exitosa": True}
        except Exception as e:
            return {"error": str(e), "respuesta": None}
    
    def ejecutar_query(self, query: str, categoria: str, procesar_completo: bool = True) -> Dict[str, Any]:
        """Ejecuta una query y registra el resultado"""
        resultado = {
            "query": query,
            "categoria_esperada": categoria,
            "timestamp": datetime.now().isoformat(),
            "clasificacion": None,
            "respuesta_completa": None,
            "tiempo_clasificacion": 0,
            "tiempo_total": 0,
            "exitosa": False,
        }
        
        inicio = time.time()
        
        # 1. Clasificar intención
        inicio_clasificacion = time.time()
        clasificacion = self.clasificar_intencion(query)
        resultado["tiempo_clasificacion"] = time.time() - inicio_clasificacion
        resultado["clasificacion"] = clasificacion
        
        # 2. Procesar consulta completa (si está habilitado)
        if procesar_completo and not clasificacion.get("error"):
            respuesta = self.procesar_consulta_completa(query)
            resultado["respuesta_completa"] = respuesta.get("respuesta")
            resultado["exitosa"] = respuesta.get("exitosa", False)
        elif not clasificacion.get("error"):
            resultado["exitosa"] = True
        
        resultado["tiempo_total"] = time.time() - inicio
        
        return resultado
    
    def ejecutar_benchmark(self, categorias: List[str] = None, procesar_completo: bool = True):
        """Ejecuta el benchmark completo"""
        if categorias is None:
            categorias = list(PREGUNTAS_BENCHMARK.keys())
        
        print("=" * 60)
        print("🚀 BENCHMARK DE ELIAS BOT")
        print("=" * 60)
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 Categorías: {', '.join(categorias)}")
        print(f"💾 Guardar en Notion: {'Sí' if self.guardar_notion else 'No'}")
        print(f"🔄 Procesar completo: {'Sí' if procesar_completo else 'No (solo clasificación)'}")
        print("=" * 60)
        print()
        
        # Contar total de queries
        total_queries = sum(
            len(PREGUNTAS_BENCHMARK.get(cat, [])) 
            for cat in categorias
        )
        
        query_num = 0
        
        for categoria in categorias:
            preguntas = PREGUNTAS_BENCHMARK.get(categoria, [])
            if not preguntas:
                continue
            
            print(f"\n📂 Categoría: {categoria.upper()}")
            print("-" * 40)
            
            # Inicializar stats de categoría
            if categoria not in self.stats["por_categoria"]:
                self.stats["por_categoria"][categoria] = {
                    "total": 0,
                    "exitosas": 0,
                    "coinciden": 0,
                }
            
            for pregunta in preguntas:
                query_num += 1
                print(f"\n[{query_num}/{total_queries}] 💬 \"{pregunta[:50]}{'...' if len(pregunta) > 50 else ''}\"")
                
                resultado = self.ejecutar_query(pregunta, categoria, procesar_completo)
                self.resultados.append(resultado)
                
                # Actualizar stats
                self.stats["total"] += 1
                self.stats["por_categoria"][categoria]["total"] += 1
                self.stats["tiempo_total"] += resultado["tiempo_total"]
                
                if resultado["exitosa"]:
                    self.stats["exitosas"] += 1
                    self.stats["por_categoria"][categoria]["exitosas"] += 1
                else:
                    self.stats["fallidas"] += 1
                
                # Mostrar resultado
                clasificacion = resultado.get("clasificacion", {})
                if clasificacion.get("error"):
                    print(f"    ❌ Error: {clasificacion['error']}")
                else:
                    intencion = clasificacion.get("intencion", "DESCONOCIDO")
                    confianza = clasificacion.get("confianza", 0)
                    
                    # Registrar intención detectada
                    if intencion not in self.stats["por_intencion_detectada"]:
                        self.stats["por_intencion_detectada"][intencion] = 0
                    self.stats["por_intencion_detectada"][intencion] += 1
                    
                    # Verificar si coincide con lo esperado
                    intencion_esperada = self._mapear_categoria_a_intencion(categoria)
                    coincide = intencion.upper() in intencion_esperada
                    
                    if coincide:
                        self.stats["por_categoria"][categoria]["coinciden"] += 1
                    
                    emoji = "✅" if coincide else "⚠️"
                    print(f"    {emoji} Intención: {intencion} (confianza: {confianza}%)")
                    print(f"    ⏱️ Tiempo: {resultado['tiempo_total']:.2f}s")
                    
                    # Mostrar respuesta si hay
                    if resultado.get("respuesta_completa"):
                        resp_preview = resultado["respuesta_completa"][:100]
                        print(f"    📤 Respuesta: {resp_preview}...")
        
        # Mostrar resumen
        self._mostrar_resumen()
        
        return self.resultados
    
    def _mapear_categoria_a_intencion(self, categoria: str) -> List[str]:
        """Mapea categoría de test a intenciones esperadas"""
        mapeo = {
            "crear_tarea": ["CREAR_TAREA", "CREAR"],
            "crear_evento": ["CREAR_EVENTO"],
            "consultar": ["CONSULTAR"],
            "ambiguo": ["AMBIGUO"],
            "mixto": ["CREAR_TAREA", "CREAR_EVENTO", "CONSULTAR", "CREAR"],
        }
        return mapeo.get(categoria, [])
    
    def _mostrar_resumen(self):
        """Muestra resumen del benchmark"""
        print("\n")
        print("=" * 60)
        print("📊 RESUMEN DEL BENCHMARK")
        print("=" * 60)
        
        print(f"\n📈 Estadísticas Generales:")
        print(f"   Total queries: {self.stats['total']}")
        print(f"   Exitosas: {self.stats['exitosas']} ({self.stats['exitosas']/max(1, self.stats['total'])*100:.1f}%)")
        print(f"   Fallidas: {self.stats['fallidas']}")
        print(f"   Tiempo total: {self.stats['tiempo_total']:.2f}s")
        print(f"   Tiempo promedio: {self.stats['tiempo_total']/max(1, self.stats['total']):.2f}s")
        
        print(f"\n📂 Por Categoría:")
        for cat, datos in self.stats["por_categoria"].items():
            total = datos["total"]
            exitosas = datos["exitosas"]
            coinciden = datos["coinciden"]
            print(f"   {cat}: {exitosas}/{total} exitosas, {coinciden}/{total} intención correcta")
        
        print(f"\n🎯 Intenciones Detectadas:")
        for intencion, count in sorted(self.stats["por_intencion_detectada"].items()):
            print(f"   {intencion}: {count}")
        
        print("=" * 60)
    
    def guardar_resultados(self, filename: str = None) -> str:
        """Guarda los resultados en un archivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tests/benchmark_results_{timestamp}.json"
        
        # Calcular tiempo promedio
        self.stats["tiempo_promedio"] = (
            self.stats["tiempo_total"] / max(1, self.stats["total"])
        )
        
        data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_queries": self.stats["total"],
                "save_to_notion": self.guardar_notion,
            },
            "stats": self.stats,
            "results": self.resultados,
        }
        
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 Resultados guardados en: {filepath}")
        return str(filepath)


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark de ELiaS Bot")
    parser.add_argument(
        "--guardar-notion", 
        action="store_true",
        help="Crear tareas/eventos reales en Notion"
    )
    parser.add_argument(
        "--rapido",
        action="store_true", 
        help="Solo clasificación (sin procesar completo)"
    )
    parser.add_argument(
        "--categoria",
        type=str,
        choices=list(PREGUNTAS_BENCHMARK.keys()),
        help="Ejecutar solo una categoría"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Archivo de salida para resultados"
    )
    
    args = parser.parse_args()
    
    # Determinar categorías
    categorias = None
    if args.categoria:
        categorias = [args.categoria]
    
    # Crear y ejecutar benchmark
    benchmark = BenchmarkBot(guardar_notion=args.guardar_notion)
    benchmark.ejecutar_benchmark(
        categorias=categorias,
        procesar_completo=not args.rapido
    )
    
    # Guardar resultados
    benchmark.guardar_resultados(args.output)


if __name__ == "__main__":
    main()
