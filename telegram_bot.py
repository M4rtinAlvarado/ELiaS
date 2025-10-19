#!/usr/bin/env python3
"""
ELiaS Telegram Bot - Punto de Entrada Principal
==============================================

Script principal para ejecutar el bot de Telegram de ELiaS.
Integra perfectamente con la arquitectura modular existente.

Uso:
    python telegram_bot.py

Requisitos:
    - Token del bot configurado en .env (TELEGRAM_BOT_TOKEN)
    - Sistema ELiaS completamente configurado (Notion + Gemini)
    - Dependencia: python-telegram-bot>=21.0.0
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Configurar codificación para Windows
if os.name == 'nt':  # Windows
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
        except:
            pass  # Usar configuración por defecto

# Agregar el directorio raíz al path para importar módulos
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Configurar logging antes de importar módulos
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    try:
        import telegram as tg_lib
        logger.info(f"✅ python-telegram-bot v{tg_lib.__version__} está instalado")
        return True
    except ImportError:
        logger.error("❌ python-telegram-bot no está instalado")
        print("\n📦 Para instalar las dependencias necesarias:")
        print("pip install python-telegram-bot>=21.0.0")
        print("\n🤖 O instala desde requirements.txt si existe:")
        print("pip install -r requirements.txt")
        return False

def validate_configuration():
    """Validar configuración necesaria para el bot"""
    try:
        from config import settings
        
        # Verificar configuración crítica
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
            print("\n🔑 Para configurar el bot:")
            print("1. Habla con @BotFather en Telegram")
            print("2. Crea un nuevo bot con /newbot")
            print("3. Copia el token en tu archivo .env")
            print("4. TELEGRAM_BOT_TOKEN=tu_token_aqui")
            return False
        
        if not settings.NOTION_TOKEN:
            logger.error("❌ NOTION_TOKEN no configurado")
            print("\n📊 El bot necesita acceso a Notion para funcionar")
            print("Configura NOTION_TOKEN en tu archivo .env")
            return False
            
        if not settings.GOOGLE_API_KEY:
            logger.error("❌ GOOGLE_API_KEY no configurado") 
            print("\n🤖 El bot necesita acceso a Gemini AI")
            print("Configura GOOGLE_API_KEY en tu archivo .env")
            return False
        
        logger.info("✅ Configuración validada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error validando configuración: {e}")
        return False

def main():
    """Función principal del bot"""
    
    # Banner de inicio
    print("=" * 60)
    print("🤖 ELiaS Telegram Bot v1.0")
    print("=" * 60)
    print("🧠 Asistente Inteligente para Gestión de Tareas")
    print("🔗 Integrado con Notion + Gemini AI + LangGraph")
    print("=" * 60)
    
    # 1. Verificar dependencias
    logger.info("📦 Verificando dependencias...")
    if not check_dependencies():
        sys.exit(1)
    
    # 2. Validar configuración
    logger.info("🔧 Validando configuración...")
    if not validate_configuration():
        sys.exit(1)
    
    # 3. Inicializar sistema ELiaS
    logger.info("🚀 Inicializando ELiaS...")
    
    # 4. Importar e inicializar bot
    try:
        from telegram_bot import EliasBot
        
        logger.info("🤖 Inicializando Telegram Bot...")
        bot = EliasBot()
        
        # 5. Ejecutar bot (ahora sincrónicamente)
        logger.info("🚀 Iniciando bot de Telegram...")
        bot.run()  # Cambio clave: usar run() en lugar de await
        
    except KeyboardInterrupt:
        logger.info("👋 Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error crítico ejecutando bot: {e}")
        raise

def run_bot():
    """Punto de entrada síncrono"""
    try:
        # Ejecutar directamente (ya no es async)
        main()
    except KeyboardInterrupt:
        print("\n👋 ¡Bot detenido correctamente!")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    
    # Verificar versión de Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requerido")
        sys.exit(1)
    
    # Información del entorno
    print(f"\n🐍 Python: {sys.version}")
    print(f"📂 Directorio: {ROOT_DIR}")
    print(f"📋 PID: {os.getpid()}")
    
    # Ejecutar bot
    run_bot()