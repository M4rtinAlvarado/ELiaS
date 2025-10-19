#!/usr/bin/env python3
"""
Test Básico - Solo verificar que el bot puede conectar
"""

import os
import sys
from pathlib import Path

# Agregar directorio raíz al path (ahora desde tests/)
ROOT_DIR = Path(__file__).parent.parent  # Subir un nivel más
sys.path.insert(0, str(ROOT_DIR))

async def test_bot_connection():
    """Test básico de conexión"""
    
    print("🔍 Probando conexión del bot...")
    
    # 1. Cargar configuración
    from config import settings
    
    if not settings.TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        return False
    
    print(f"✅ Token: ...{settings.TELEGRAM_BOT_TOKEN[-8:]}")
    
    # 2. Test python-telegram-bot
    try:
        import telegram
        print(f"✅ python-telegram-bot v{telegram.__version__}")
    except ImportError:
        print("❌ python-telegram-bot no instalado")
        return False
    
    # 3. Crear bot simple
    try:
        from telegram import Bot
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        # Test básico - obtener info del bot
        bot_info = await bot.get_me()
        print(f"✅ Bot conectado: @{bot_info.username}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error conectando bot: {e}")
        return False

def main():
    """Función principal para ejecutar tests"""
    import asyncio
    
    try:
        result = asyncio.run(test_bot_connection())
        if result:
            print("\n🎉 ¡Test de conexión exitoso!")
            return True
        else:
            print("\n❌ Test de conexión falló")
            return False
    except Exception as e:
        print(f"\n💥 Error ejecutando test: {e}")
        return False

if __name__ == "__main__":
    main()