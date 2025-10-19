#!/usr/bin/env python3
"""
Script de Conveniencia para Ejecutar Tests
==========================================

Facilita la ejecución de tests desde cualquier ubicación.

Uso:
    python run_tests.py                    # Todos los tests
    python run_tests.py conexion          # Test específico
    python run_tests.py notion            # Tests de Notion
    python run_tests.py telegram          # Tests de Telegram
    python run_tests.py verificar         # Verificación completa
"""

import sys
from pathlib import Path

# Asegurar que podemos importar módulos
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

def main():
    """Delegar a la suite principal de tests"""
    try:
        # Importar y ejecutar la suite principal
        from tests.run_all_tests import main as run_tests_main
        return run_tests_main()
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        print("\n🔍 Verifica que el módulo tests/ esté correctamente configurado")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Tests interrumpidos")
        sys.exit(1)