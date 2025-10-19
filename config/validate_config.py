#!/usr/bin/env python3
"""
Script de validación de configuración para ELiaS
Ejecuta: python -m config.validate_config
"""
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from config.constants import VERSION, APP_NAME

def main():
    """Función principal de validación"""
    print(f"\n🚀 {APP_NAME} v{VERSION}")
    print("=" * 50)
    
    # Mostrar estado de configuración
    settings.show_status()
    
    # Validar configuración crítica
    print(f"\n🔍 VALIDANDO CONFIGURACIÓN CRÍTICA...")
    try:
        missing_core = settings.validate_core_config()
        
        if not missing_core:
            print("✅ Todas las configuraciones esenciales están presentes")
            
            # Tests adicionales
            test_notion_connection()
            test_gemini_connection()
            
        else:
            print(f"❌ Configuraciones faltantes: {', '.join(missing_core)}")
            print(f"\n💡 Para solucionarlo:")
            print(f"   1. Copia el archivo .env.example como .env")
            print(f"   2. Completa las variables faltantes")
            print(f"   3. Ejecuta este script nuevamente")
            return False
            
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return False
    
    # Validar configuración futura (opcional)
    print(f"\n🔮 VALIDANDO CONFIGURACIÓN FUTURA...")
    missing_telegram = settings.validate_telegram_config()
    
    if not missing_telegram:
        print("✅ Configuración de Telegram lista")
    else:
        print(f"ℹ️ Configuración de Telegram pendiente: {', '.join(missing_telegram)}")
    
    print(f"\n✨ Validación completada")
    return True

def test_notion_connection():
    """Test de conexión básica con Notion"""
    print(f"\n🔗 Probando conexión con Notion...")
    try:
        from notion_client import Client
        
        if not settings.NOTION_TOKEN:
            print("⚠️ Token de Notion no configurado")
            return False
            
        client = Client(auth=settings.NOTION_TOKEN)
        
        # Test simple: obtener info del usuario
        user_info = client.users.me()
        user_name = user_info.get('name', 'Usuario')
        
        print(f"✅ Conexión exitosa con Notion")
        print(f"   👤 Usuario: {user_name}")
        
        # Test de base de datos si está configurada
        if settings.NOTION_DB_TAREAS:
            try:
                response = client.databases.query(
                    database_id=settings.NOTION_DB_TAREAS,
                    page_size=1
                )
                total_pages = len(response.get('results', []))
                print(f"✅ Base de datos de tareas accesible")
                print(f"   📊 Páginas de prueba obtenidas: {total_pages}")
                
            except Exception as db_error:
                print(f"⚠️ Error accediendo a BD de tareas: {db_error}")
        
        return True
        
    except ImportError:
        print("⚠️ notion-client no instalado. Ejecuta: pip install notion-client")
        return False
    except Exception as e:
        print(f"❌ Error conectando con Notion: {e}")
        return False

def test_gemini_connection():
    """Test de conexión básica con Gemini"""
    print(f"\n🤖 Probando conexión con Gemini...")
    try:
        if not settings.GOOGLE_API_KEY:
            print("⚠️ API Key de Google no configurada")
            return False
        
        # Import dinámico para no fallar si no está instalado
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            print("⚠️ langchain-google-genai no instalado")
            print("   Ejecuta: pip install langchain-google-genai")
            return False
        
        # Crear cliente con configuración
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=settings.GEMINI_TEMPERATURE,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        # Test simple
        test_prompt = "Responde solo con 'OK' si puedes procesar este mensaje"
        response = llm.invoke(test_prompt)
        
        print(f"✅ Conexión exitosa con Gemini")
        print(f"   🎯 Modelo: {settings.GEMINI_MODEL}")
        print(f"   💬 Respuesta de prueba: {response.content.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error conectando con Gemini: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)