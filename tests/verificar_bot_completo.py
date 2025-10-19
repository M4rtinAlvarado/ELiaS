#!/usr/bin/env python3
"""
Verificar que el bot completo está listo
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path (ahora desde tests/)
ROOT_DIR = Path(__file__).parent.parent  # Subir un nivel más
sys.path.insert(0, str(ROOT_DIR))

def test_bot_completo():
    """Test del bot completo"""
    
    print("🔍 Verificando bot completo...")
    
    try:
        # 1. Configuración
        from config import settings
        print(f"✅ Token: ...{settings.TELEGRAM_BOT_TOKEN[-8:]}")
        print(f"✅ Admin IDs: {settings.TELEGRAM_ADMIN_IDS}")
        
        # 2. Módulo bot
        from telegram_bot import EliasBot
        print("✅ Clase EliasBot importada")
        
        # 3. Crear bot
        bot = EliasBot()
        print("✅ Bot creado")
        
        # 4. Verificar componentes
        if hasattr(bot, 'command_handlers'):
            print("✅ CommandHandlers disponible")
        
        if hasattr(bot, 'message_handlers'):
            print("✅ MessageHandlers disponible")
            
        if hasattr(bot, 'keyboards'):
            print("✅ TelegramKeyboards disponible")
        
        # 5. Build bot
        if bot.build_bot():
            print("✅ Bot construido correctamente")
        else:
            print("❌ Error construyendo bot")
            return False
        
        print("🎉 ¡Bot completo listo para ejecutar!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 50)
    print("🤖 Verificación Bot Completo")
    print("=" * 50)
    
    if test_bot_completo():
        print("\n✅ Verificación exitosa")
        print("🚀 Puedes ejecutar: python telegram_bot.py")
        return True
    else:
        print("\n❌ Verificación falló")
        print("🔧 Revisa la configuración y dependencias")
        return False

if __name__ == "__main__":
    main()