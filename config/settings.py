"""
Configuración centralizada para ELiaS
Maneja todas las variables de entorno y validaciones
"""
import os
from pathlib import Path
from typing import Optional, List
import dotenv

# Detectar directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env"

# Cargar variables de entorno
if ENV_FILE.exists():
    dotenv.load_dotenv(ENV_FILE)
    print(f"✅ Configuración cargada desde: {ENV_FILE}")
else:
    print(f"⚠️ Archivo .env no encontrado en: {ENV_FILE}")

class Settings:
    """Clase de configuración centralizada"""
    
    # === NOTION CONFIGURATION ===
    NOTION_TOKEN: Optional[str] = os.getenv("NOTION_TOKEN")
    NOTION_DB_TAREAS: Optional[str] = os.getenv("NOTION_DB_TAREAS")
    NOTION_DB_PROYECTOS: Optional[str] = os.getenv("NOTION_DB_PROYECTOS")
    NOTION_DB_EVENTOS: Optional[str] = os.getenv("NOTION_DB_EVENTOS")  # Futuro
    
    # === AI/LLM CONFIGURATION ===
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")

    
    # Configuración de Gemini
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0"))
    GEMINI_MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))
    
    # === TELEGRAM CONFIGURATION ===
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_WEBHOOK_URL: Optional[str] = os.getenv("TELEGRAM_WEBHOOK_URL")
    
    # Función auxiliar para parsear admin IDs
    def __parse_admin_ids():
        admin_ids_str = os.getenv("TELEGRAM_ADMIN_IDS", "")
        if not admin_ids_str:
            return []
        
        try:
            # Limpiar corchetes y espacios
            clean_str = admin_ids_str.strip("[]").strip()
            
            # Dividir por comas y parsear
            ids = []
            for id_str in clean_str.split(","):
                id_str = id_str.strip()
                if id_str:
                    ids.append(int(id_str))
            return ids
        except Exception as e:
            print(f"⚠️ Error parseando TELEGRAM_ADMIN_IDS: {e}")
            return []
    
    TELEGRAM_ADMIN_IDS: List[int] = __parse_admin_ids()
    
    # === ASSEMBLYAI CONFIGURATION ===
    ASSEMBLY_API_KEY: str = os.getenv("ASSEMBLY_API_KEY", "")
    AUDIO_MAX_DURATION: int = int(os.getenv("AUDIO_MAX_DURATION", "300"))
    
    # === DATABASE CONFIGURATION ===
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///elias.db")  # Futuro
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() == "true"  # Futuro
    
    # === APPLICATION CONFIGURATION ===
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # === RAG CONFIGURATION (FUTURO) ===
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
    RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "vectordb")
    
    @classmethod
    def validate_core_config(cls) -> List[str]:
        """
        Valida configuraciones esenciales para el funcionamiento básico
        Returns: Lista de configuraciones faltantes
        """
        missing = []
        
        # Configuraciones críticas actuales
        if not cls.NOTION_TOKEN:
            missing.append("NOTION_TOKEN")
        if not cls.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        if not cls.NOTION_DB_TAREAS:
            missing.append("NOTION_DB_TAREAS")
            
        return missing
    
    @classmethod
    def validate_telegram_config(cls) -> List[str]:
        """
        Valida configuraciones para Telegram (futuro)
        Returns: Lista de configuraciones faltantes
        """
        missing = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
            
        return missing
    
    @classmethod
    def validate_all(cls) -> None:
        """
        Valida todas las configuraciones críticas
        Raises: ValueError si faltan configuraciones esenciales
        """
        missing_core = cls.validate_core_config()
        
        if missing_core:
            raise ValueError(
                f"❌ Configuraciones esenciales faltantes: {', '.join(missing_core)}\n"
                f"💡 Verifica tu archivo .env en: {ENV_FILE}"
            )
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """
        Retorna un resumen de la configuración actual (sin secretos)
        """
        return {
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "log_level": cls.LOG_LEVEL,
            "notion_configured": bool(cls.NOTION_TOKEN),
            "notion_db_tareas": bool(cls.NOTION_DB_TAREAS),
            "notion_db_proyectos": bool(cls.NOTION_DB_PROYECTOS),
            "gemini_configured": bool(cls.GOOGLE_API_KEY),
            "gemini_model": cls.GEMINI_MODEL,
            "telegram_configured": bool(cls.TELEGRAM_BOT_TOKEN),
            "assembly_configured": bool(cls.ASSEMBLY_API_KEY),
            "audio_max_duration": cls.AUDIO_MAX_DURATION,
            "database_url": cls.DATABASE_URL,
            "base_dir": str(BASE_DIR),
            "env_file": str(ENV_FILE)
        }
    
    @classmethod
    def show_status(cls) -> None:
        """Muestra el estado actual de la configuración"""
        summary = cls.get_config_summary()
        
        print("\n🔧 ESTADO DE CONFIGURACIÓN")
        print("=" * 50)
        
        # Configuraciones básicas
        print(f"📁 Directorio base: {summary['base_dir']}")
        print(f"🌍 Entorno: {summary['environment']}")
        print(f"🐛 Debug: {'✅' if summary['debug'] else '❌'}")
        print(f"📊 Log Level: {summary['log_level']}")
        
        # Notion
        print(f"\n📋 NOTION:")
        print(f"  • Token: {'✅' if summary['notion_configured'] else '❌'}")
        print(f"  • BD Tareas: {'✅' if summary['notion_db_tareas'] else '❌'}")
        print(f"  • BD Proyectos: {'✅' if summary['notion_db_proyectos'] else '❌'}")
        
        # IA
        print(f"\n🤖 IA/LLM:")
        print(f"  • Gemini: {'✅' if summary['gemini_configured'] else '❌'}")
        print(f"  • Modelo: {summary['gemini_model']}")
        
        # Telegram (futuro)
        print(f"\n💬 TELEGRAM:")
        print(f"  • Bot Token: {'✅' if summary['telegram_configured'] else '❌ (futuro)'}")
        
        # Validar configuración crítica
        try:
            cls.validate_core_config()
            print(f"\n✅ Configuración básica: VÁLIDA")
        except ValueError as e:
            print(f"\n❌ Configuración básica: INVÁLIDA")
            print(f"   {str(e)}")

# Instancia global de configuración
settings = Settings()

# Validación automática al importar (solo para configuraciones críticas actuales)
def validate_on_import():
    """Validación automática al importar el módulo"""
    try:
        missing_core = settings.validate_core_config()
        if missing_core:
            print(f"⚠️ Configuraciones faltantes: {', '.join(missing_core)}")
            print(f"💡 El sistema funcionará en modo limitado")
        else:
            print("✅ Configuración básica válida")
    except Exception as e:
        print(f"⚠️ Error validando configuración: {e}")

# Ejecutar validación al importar
if __name__ != "__main__":
    validate_on_import()

# Para testing desde terminal
if __name__ == "__main__":
    settings.show_status()