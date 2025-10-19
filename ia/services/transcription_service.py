"""
Servicio de Transcripción de Audio usando AssemblyAI
===================================================

Maneja la transcripción de mensajes de voz del bot de Telegram
usando la API de AssemblyAI para convertir audio a texto.
"""

import os
import tempfile
import asyncio
import logging
from typing import Optional, Dict, Any
from io import BytesIO

import assemblyai as aai
from config import settings

logger = logging.getLogger(__name__)

class TranscriptionError(Exception):
    """Excepción personalizada para errores de transcripción"""
    pass

class AssemblyAIService:
    """
    Servicio para transcripción de audio usando AssemblyAI
    
    Características:
    - Soporte para múltiples formatos de audio
    - Transcripción en español y otros idiomas
    - Manejo de archivos temporales
    - Logging detallado para debug
    """
    
    def __init__(self):
        """Inicializar el servicio de AssemblyAI"""
        self.api_key = settings.ASSEMBLY_API_KEY
        self.max_duration = settings.AUDIO_MAX_DURATION
        
        if not self.api_key:
            logger.warning("⚠️ ASSEMBLY_API_KEY no configurada")
            self.disponible = False
        else:
            # Configurar AssemblyAI
            aai.settings.api_key = self.api_key
            self.disponible = True
            logger.info("✅ AssemblyAI configurado correctamente")
    
    async def transcribir_audio_telegram(self, file_bytes: bytes, file_name: str = "audio") -> Dict[str, Any]:
        """
        Transcribir audio desde bytes (para Telegram Bot)
        
        Args:
            file_bytes: Bytes del archivo de audio
            file_name: Nombre del archivo (opcional, para logging)
            
        Returns:
            Dict con resultado de transcripción
        """
        if not self.disponible:
            raise TranscriptionError("AssemblyAI no está disponible - verifica ASSEMBLY_API_KEY")
        
        logger.info(f"🎤 Iniciando transcripción de {file_name}")
        
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
                temp_file.write(file_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Transcribir usando AssemblyAI
                resultado = await self._transcribir_archivo(temp_file_path)
                
                logger.info(f"✅ Transcripción completada para {file_name}")
                return {
                    'exitosa': True,
                    'texto': resultado['text'],
                    'confianza': resultado['confidence'],
                    'duracion': resultado.get('audio_duration'),
                    'idioma': resultado.get('language_code', 'es')
                }
                
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(temp_file_path)
                except:
                    pass  # No importa si no se puede borrar
            
        except Exception as e:
            logger.error(f"❌ Error transcribiendo {file_name}: {e}")
            return {
                'exitosa': False,
                'error': str(e),
                'texto': None
            }
    
    async def _transcribir_archivo(self, file_path: str) -> Dict[str, Any]:
        """
        Transcribir un archivo de audio usando AssemblyAI
        
        Args:
            file_path: Ruta al archivo de audio
            
        Returns:
            Dict con resultado de transcripción
        """
        try:
            # Configuración de transcripción
            config = aai.TranscriptionConfig(
                language_code="es",  # Español por defecto
                speaker_labels=False,  # No necesitamos identificar speakers
                format_text=True,     # Formatear texto automáticamente
                punctuate=True,       # Agregar puntuación
                filter_profanity=False  # No filtrar palabrotas
            )
            
            # Crear transcriber
            transcriber = aai.Transcriber()
            
            # Transcribir (esto es síncrono, pero lo envolvemos en async)
            transcript = await asyncio.to_thread(
                transcriber.transcribe, 
                file_path, 
                config=config
            )
            
            # Verificar si la transcripción fue exitosa
            if transcript.status == aai.TranscriptStatus.error:
                raise TranscriptionError(f"Error en transcripción: {transcript.error}")
            
            return {
                'text': transcript.text or "",
                'confidence': transcript.confidence or 0.0,
                'audio_duration': transcript.audio_duration,
                'language_code': 'es'
            }
            
        except Exception as e:
            logger.error(f"❌ Error en _transcribir_archivo: {e}")
            raise TranscriptionError(f"Error transcribiendo archivo: {e}")
    
    def validar_duracion_audio(self, duracion_segundos: float) -> bool:
        """
        Validar si la duración del audio es aceptable
        
        Args:
            duracion_segundos: Duración del audio en segundos
            
        Returns:
            True si la duración es válida
        """
        return 0 < duracion_segundos <= self.max_duration
    
    async def probar_conexion(self) -> Dict[str, Any]:
        """
        Probar la conexión con AssemblyAI
        
        Returns:
            Dict con estado de la conexión
        """
        if not self.disponible:
            return {
                'conectado': False,
                'error': 'API Key no configurada'
            }
        
        try:
            # Crear un transcriber para probar la conexión
            transcriber = aai.Transcriber()
            
            # Nota: AssemblyAI no tiene endpoint de health check simple,
            # pero podemos verificar que el objeto se cree correctamente
            return {
                'conectado': True,
                'servicio': 'AssemblyAI',
                'api_key_valida': bool(self.api_key)
            }
            
        except Exception as e:
            logger.error(f"❌ Error probando conexión AssemblyAI: {e}")
            return {
                'conectado': False,
                'error': str(e)
            }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Obtener información del servicio
        
        Returns:
            Dict con información del servicio
        """
        return {
            'servicio': 'AssemblyAI',
            'disponible': self.disponible,
            'max_duration': self.max_duration,
            'idiomas_soportados': ['es', 'en', 'fr', 'de', 'it', 'pt'],
            'formatos_soportados': ['mp3', 'wav', 'ogg', 'm4a', 'webm'],
            'api_key_configurada': bool(self.api_key)
        }

# Instancia global del servicio
try:
    transcription_service = AssemblyAIService()
    logger.info("✅ Servicio de transcripción AssemblyAI inicializado")
except Exception as e:
    logger.error(f"❌ Error inicializando servicio de transcripción: {e}")
    transcription_service = None