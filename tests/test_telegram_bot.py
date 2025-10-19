#!/usr/bin/env python3
"""
Script de Prueba para ELiaS Telegram Bot
=======================================

Prueba las funcionalidades principales sin ejecutar el bot completo.
"""

import sys
import os
from pathlib import Path

# Agregar directorio raíz al path (ahora desde tests/)
ROOT_DIR = Path(__file__).parent.parent  # Subir un nivel más
sys.path.insert(0, str(ROOT_DIR))

def test_configuration():
    """Probar configuración"""
    print("🔧 Probando configuración...")
    
    try:
        from config import settings
        
        print(f"✅ NOTION_TOKEN: {'Configurado' if settings.NOTION_TOKEN else 'NO configurado'}")
        print(f"✅ GOOGLE_API_KEY: {'Configurado' if settings.GOOGLE_API_KEY else 'NO configurado'}")
        print(f"✅ TELEGRAM_BOT_TOKEN: {'Configurado' if settings.TELEGRAM_BOT_TOKEN else 'NO configurado'}")
        
        if settings.TELEGRAM_BOT_TOKEN:
            print(f"   Token: ...{settings.TELEGRAM_BOT_TOKEN[-8:]}")
        
        return all([settings.NOTION_TOKEN, settings.GOOGLE_API_KEY, settings.TELEGRAM_BOT_TOKEN])
        
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False

def test_dependencies():
    """Probar dependencias"""
    print("\n📦 Probando dependencias...")
    
    # Test python-telegram-bot
    try:
        import telegram
        print(f"✅ python-telegram-bot v{telegram.__version__}")
        telegram_ok = True
    except ImportError:
        print("❌ python-telegram-bot NO instalado")
        telegram_ok = False
    
    # Test otros módulos críticos
    modules_to_test = [
        ('notion_client', 'Notion API'),
        ('google.generativeai', 'Gemini AI'),
        ('asyncio', 'Asyncio')
    ]
    
    results = [telegram_ok]
    
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
            results.append(True)
        except ImportError:
            print(f"❌ {display_name} NO disponible")
            results.append(False)
    
    return all(results)

def test_elias_modules():
    """Probar módulos de ELiaS"""
    print("\n🧠 Probando módulos de ELiaS...")
    
    modules = [
        ('notion', 'Módulo Notion'),
        ('ia', 'Módulo IA'),
        ('telegram_bot', 'Módulo Telegram Bot')
    ]
    
    results = []
    
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
            results.append(True)
        except ImportError as e:
            print(f"❌ {display_name}: {e}")
            results.append(False)
    
    return all(results)

def test_services():
    """Probar servicios"""
    print("\n🔧 Probando servicios...")
    
    try:
        from notion import tareas_service, proyectos_service
        from ia.services import gemini_service
        
        # Test servicios Notion
        if tareas_service:
            print("✅ TareasService inicializado")
            # Probar obtener tareas
            try:
                tareas = tareas_service.obtener_todas_las_tareas()
                print(f"   📋 Tareas encontradas: {len(tareas)}")
            except Exception as e:
                print(f"   ⚠️ Error obteniendo tareas: {e}")
        else:
            print("❌ TareasService NO inicializado")
        
        if proyectos_service:
            print("✅ ProyectosService inicializado")
            try:
                proyectos = proyectos_service.cargar_proyectos_como_diccionario()
                print(f"   📁 Proyectos encontrados: {len(proyectos)}")
            except Exception as e:
                print(f"   ⚠️ Error obteniendo proyectos: {e}")
        else:
            print("❌ ProyectosService NO inicializado")
        
        # Test Gemini
        if gemini_service:
            print("✅ GeminiService inicializado")
        else:
            print("❌ GeminiService NO inicializado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando servicios: {e}")
        return False

def test_telegram_bot_creation():
    """Probar creación del bot de Telegram"""
    print("\n🤖 Probando creación del bot...")
    
    try:
        from telegram_bot import EliasBot
        
        print("✅ Clase EliasBot importada")
        
        # Intentar crear instancia
        bot = EliasBot()
        print("✅ Instancia EliasBot creada")
        
        # Verificar configuración
        if bot.admin_ids:
            print(f"✅ Admin IDs configurados: {bot.admin_ids}")
        
        if bot.token:
            print("✅ Token configurado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando bot: {e}")
        return False

def test_telegram_handlers():
    """Probar handlers del bot"""
    print("\n🎯 Probando handlers...")
    
    try:
        from telegram_bot.handlers import CommandHandlers, MessageHandlers
        from telegram_bot.keyboards import TelegramKeyboards
        
        print("✅ CommandHandlers importado")
        print("✅ MessageHandlers importado") 
        print("✅ TelegramKeyboards importado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importando handlers: {e}")
        return False

def run_all_tests():
    """Ejecutar todos los tests"""
    print("=" * 60)
    print("🧪 ELiaS Telegram Bot - Suite de Tests")
    print("=" * 60)
    
    tests = [
        ("Configuración", test_configuration),
        ("Dependencias", test_dependencies),
        ("Módulos ELiaS", test_elias_modules),
        ("Servicios", test_services),
        ("Creación Bot", test_telegram_bot_creation),
        ("Handlers", test_telegram_handlers)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"💥 Error en {test_name}: {e}")
            results.append(False)
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASÓ" if results[i] else "❌ FALLÓ"
        print(f"{test_name:<20} {status}")
    
    exitosos = sum(results)
    total = len(results)
    
    print(f"\n🎯 Total: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("🎉 ¡Todos los tests pasaron! El bot está listo.")
        return True
    else:
        print("⚠️ Algunos tests fallaron. Revisa la configuración.")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Tests interrumpidos por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error fatal ejecutando tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)