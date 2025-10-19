"""
Test para verificar la creación de tareas con el módulo Notion corregido
"""
import sys
import os
from pathlib import Path

# Agregar directorio raíz al path (ahora desde tests/)
ROOT_DIR = Path(__file__).parent.parent  # Subir un nivel más
sys.path.insert(0, str(ROOT_DIR))

from config import settings
from notion.models import Tarea, EstadoTarea, PrioridadTarea
from notion import tareas_service, notion_client

def test_crear_objeto_tarea():
    """Prueba crear solo el objeto Tarea"""
    try:
        print("🧪 Test 1: Creando objeto Tarea...")
        
        tarea = Tarea(
            nombre="Tarea de prueba",
            descripcion="Esta es una tarea de prueba",
            estado=EstadoTarea.SIN_EMPEZAR,
            prioridad=PrioridadTarea.MEDIA,
            proyecto_ids=["Test"]
        )
        
        print(f"✅ Tarea creada: {tarea.nombre}")
        print(f"   Estado: {tarea.estado}")
        print(f"   Prioridad: {tarea.prioridad}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando objeto Tarea: {e}")
        return False

def test_conexion_notion():
    """Prueba la conexión a Notion"""
    try:
        print("\n🧪 Test 2: Conexión a Notion...")
        
        if not settings.NOTION_TOKEN:
            print("❌ NOTION_TOKEN no configurado")
            return False
        
        print(f"✅ Token configurado: ...{settings.NOTION_TOKEN[-8:]}")
        
        # Test básico de cliente
        if notion_client:
            print("✅ Cliente Notion inicializado")
        else:
            print("❌ Cliente Notion no inicializado")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando conexión: {e}")
        return False

def test_servicio_tareas():
    """Prueba el servicio de tareas"""
    try:
        print("\n🧪 Test 3: Servicio de Tareas...")
        
        if not tareas_service:
            print("❌ TareasService no inicializado")
            return False
        
        # Obtener tareas existentes
        tareas = tareas_service.obtener_todas_las_tareas()
        print(f"✅ Tareas encontradas: {len(tareas)}")
        
        if tareas:
            primera = tareas[0]
            print(f"   Primera tarea: {primera.nombre}")
            print(f"   Estado: {primera.estado}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando servicio: {e}")
        return False

def test_crear_tarea_completa():
    """Prueba crear una tarea completa en Notion"""
    try:
        print("\n🧪 Test 4: Crear tarea en Notion...")
        
        # Crear tarea de prueba
        tarea = Tarea(
            nombre=f"Test {os.getpid()}",
            descripcion="Tarea creada por test automatizado",
            estado=EstadoTarea.SIN_EMPEZAR,
            prioridad=PrioridadTarea.BAJA,
            proyecto_ids=["Tests"]
        )
        
        # Intentar crear en Notion
        resultado = tareas_service.crear_tarea_desde_texto(
            titulo=tarea.nombre,
            prioridad="Baja"
            # No incluir proyectos por ahora para evitar problemas de UUID
        )
        
        if resultado:
            print(f"✅ Tarea creada en Notion: {tarea.nombre}")
            return True
        else:
            print(f"❌ Error creando tarea en Notion")
            return False
            
    except Exception as e:
        print(f"❌ Error en test completo: {e}")
        return False

def run_all_tests():
    """Ejecutar todos los tests"""
    print("=" * 50)
    print("🧪 Tests del Sistema Notion")
    print("=" * 50)
    
    tests = [
        test_crear_objeto_tarea,
        test_conexion_notion,
        test_servicio_tareas,
        test_crear_tarea_completa
    ]
    
    resultados = []
    
    for test in tests:
        resultado = test()
        resultados.append(resultado)
    
    # Resumen
    exitosos = sum(resultados)
    total = len(resultados)
    
    print(f"\n📊 Resultados: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("🎉 ¡Todos los tests pasaron!")
        return True
    else:
        print("❌ Algunos tests fallaron")
        return False

def main():
    """Función principal para ejecutar desde el sistema de tests"""
    return run_all_tests()

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n👋 Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"\n💥 Error ejecutando tests: {e}")
        import traceback
        traceback.print_exc()