#!/usr/bin/env python3
"""
Suite Principal de Tests para ELiaS
==================================

Ejecuta todos los tests disponibles en el sistema ELiaS.

Uso:
    python tests/run_all_tests.py
    
    # O desde la raíz:
    python -m tests.run_all_tests
"""

import sys
from pathlib import Path

# Configurar path para importar módulos
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

def run_test_suite():
    """Ejecutar suite completa de tests"""
    
    print("🧪 ELiaS - Suite Completa de Tests")
    print("=" * 60)
    
    # Lista de módulos de test disponibles
    test_modules = [
        ("test_conexion", "Test de Conexión Básica"),
        ("test_notion_fix", "Tests del Sistema Notion"),
        ("test_telegram_bot", "Tests del Bot de Telegram"),
        ("verificar_bot_completo", "Verificación Completa del Bot")
    ]
    
    results = []
    
    for module_name, description in test_modules:
        print(f"\n🔍 Ejecutando: {description}")
        print("-" * 50)
        
        try:
            # Importar y ejecutar el test
            test_module = __import__(f"tests.{module_name}", fromlist=[module_name])
            
            # Intentar ejecutar main() si existe
            if hasattr(test_module, 'main'):
                result = test_module.main()
            elif hasattr(test_module, 'run_all_tests'):
                result = test_module.run_all_tests()
            else:
                print(f"⚠️ No se encontró función principal en {module_name}")
                result = False
            
            # Normalizar resultado a boolean
            results.append(bool(result) if result is not None else False)
            
        except Exception as e:
            print(f"❌ Error ejecutando {module_name}: {e}")
            results.append(False)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN GENERAL DE TESTS")
    print("=" * 60)
    
    for i, (_, description) in enumerate(test_modules):
        status = "✅ EXITOSO" if results[i] else "❌ FALLÓ"
        print(f"{description:<35} {status}")
    
    # Suma segura de resultados booleanos
    exitosos = sum(1 for r in results if r)
    total = len(results)
    
    print(f"\n🎯 Resultado Final: {exitosos}/{total} suites exitosas")
    
    if exitosos == total:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        print("🚀 El sistema ELiaS está completamente funcional")
        return True
    else:
        print("⚠️ ALGUNOS TESTS FALLARON")
        print("🔧 Revisa los errores mostrados arriba")
        return False

def run_specific_test(test_name: str):
    """Ejecutar un test específico"""
    
    available_tests = {
        "conexion": ("test_conexion", "Test de Conexión"),
        "notion": ("test_notion_fix", "Tests de Notion"),
        "telegram": ("test_telegram_bot", "Tests de Telegram"),
        "verificar": ("verificar_bot_completo", "Verificación Completa")
    }
    
    if test_name not in available_tests:
        print(f"❌ Test '{test_name}' no encontrado")
        print(f"📋 Tests disponibles: {', '.join(available_tests.keys())}")
        return False
    
    module_name, description = available_tests[test_name]
    
    print(f"🔍 Ejecutando: {description}")
    print("=" * 50)
    
    try:
        test_module = __import__(f"tests.{module_name}", fromlist=[module_name])
        
        # Ejecutar test
        if hasattr(test_module, 'main'):
            return test_module.main()
        elif hasattr(test_module, 'run_all_tests'):
            return test_module.run_all_tests()
        else:
            print(f"⚠️ No se encontró función principal en {module_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando {test_name}: {e}")
        return False

def main():
    """Función principal"""
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        # Ejecutar test específico
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Ejecutar todos los tests
        success = run_test_suite()
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Tests interrumpidos por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)