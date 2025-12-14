"""Handlers de Mensajes para Telegram Bot - Procesamiento de lenguaje natural."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class MessageHandlers:
    """Maneja todos los mensajes de texto del bot (consultas en lenguaje natural)."""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler principal para mensajes de texto - Procesa consultas con IA."""
        try:
            user = update.effective_user
            message_text = update.message.text.strip()
            
            # Log de la consulta (sin datos sensibles)
            logger.info(f"💬 Usuario {user.id}: {message_text[:50]}...")
            
            # Mostrar indicador de "escribiendo..."
            await update.message.reply_chat_action("typing")
            
            # Procesar consulta con LangGraphService
            try:
                # Aquí está la integración clave con ELiaS
                respuesta = await self.bot.process_natural_query(
                    query=message_text,
                    user_id=user.id
                )
                
                # Enviar respuesta al usuario con manejo de errores de formato
                try:
                    await update.message.reply_text(
                        respuesta,
                        parse_mode='Markdown',
                        reply_markup=self.bot.keyboards.quick_actions()
                    )
                except Exception as parse_error:
                    # Si falla el Markdown, enviar sin formato
                    logger.warning(f"⚠️ Error de formato Markdown, enviando sin formato: {parse_error}")
                    await update.message.reply_text(
                        respuesta,
                        reply_markup=self.bot.keyboards.quick_actions()
                    )
                
                logger.info(f"✅ Respuesta enviada a usuario {user.id}")
                
            except Exception as e:
                logger.error(f"❌ Error procesando consulta: {e}")
                
                # Mensaje de error amigable
                error_message = """
❌ **Ups, algo salió mal**

No pude procesar tu consulta en este momento. 

🔄 **¿Qué puedes hacer?**
• Inténtalo de nuevo en un momento
• Usa comandos más simples
• Revisa el `/help` para ejemplos

💡 **Ejemplos que siempre funcionan:**
• "¿Cuántas tareas tengo?"
• "Crear tarea: estudiar"
• "Ayuda"
                """
                
                await update.message.reply_text(
                    error_message,
                    parse_mode='Markdown',
                    reply_markup=self.bot.keyboards.main_menu()
                )
        
        except Exception as e:
            logger.error(f"❌ Error crítico en handler de mensajes: {e}")
            
            # Fallback para errores críticos
            try:
                await update.message.reply_text(
                    "❌ Error del sistema. Usa /start para reiniciar."
                )
            except:
                pass  # No podemos hacer nada más
    
    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler para mensajes de voz usando AssemblyAI
        """
        try:
            user = update.effective_user
            voice = update.message.voice
            
            logger.info(f"🎤 Mensaje de voz recibido de usuario {user.id} (duración: {voice.duration}s)")
            
            # Mostrar indicador de "escribiendo..."
            await update.message.reply_chat_action("typing")
            
            # Validar duración del audio
            max_duration = 300  # 5 minutos
            if voice.duration > max_duration:
                await update.message.reply_text(
                    f"❌ **Audio muy largo**\n\n"
                    f"Duración máxima permitida: {max_duration} segundos\n"
                    f"Tu audio: {voice.duration} segundos\n\n"
                    f"💡 *Intenta con un audio más corto*",
                    parse_mode='Markdown',
                    reply_markup=self.bot.keyboards.quick_actions()
                )
                return
            
            # Descargar archivo de voz
            try:
                voice_file = await context.bot.get_file(voice.file_id)
                voice_bytes = await voice_file.download_as_bytearray()
                
                logger.info(f"📥 Audio descargado: {len(voice_bytes)} bytes")
                
            except Exception as e:
                logger.error(f"❌ Error descargando audio: {e}")
                await update.message.reply_text(
                    "❌ Error descargando el audio. Inténtalo de nuevo.",
                    reply_markup=self.bot.keyboards.main_menu()
                )
                return
            
            # Transcribir audio
            try:
                from ia.services.transcription_service import transcription_service
                
                if not transcription_service or not transcription_service.disponible:
                    await update.message.reply_text(
                        "❌ **Servicio de transcripción no disponible**\n\n"
                        "El administrador debe configurar AssemblyAI.\n\n"
                        "💡 *Por ahora, usa mensajes de texto*",
                        parse_mode='Markdown',
                        reply_markup=self.bot.keyboards.main_menu()
                    )
                    return
                
                # Mostrar mensaje de progreso
                progress_message = await update.message.reply_text(
                    "🎤 **Transcribiendo audio...**\n\n"
                    "⏳ *Esto puede tomar unos segundos*",
                    parse_mode='Markdown'
                )
                
                # Transcribir
                resultado = await transcription_service.transcribir_audio_telegram(
                    file_bytes=bytes(voice_bytes),
                    file_name=f"voice_{user.id}_{voice.file_id[:8]}"
                )
                
                # Borrar mensaje de progreso
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=progress_message.message_id
                    )
                except:
                    pass  # No importa si no se puede borrar
                
                if resultado['exitosa']:
                    texto_transcrito = resultado['texto'].strip()
                    
                    if not texto_transcrito:
                        await update.message.reply_text(
                            "🤔 **No pude entender el audio**\n\n"
                            "💡 *Intenta hablar más claro o usar texto*",
                            parse_mode='Markdown',
                            reply_markup=self.bot.keyboards.quick_actions()
                        )
                        return
                    
                    logger.info(f"✅ Audio transcrito: {texto_transcrito[:50]}...")
                    
                    # Mostrar transcripción y procesar
                    await update.message.reply_text(
                        f"🎤 **Audio transcrito:**\n\n"
                        f"_{texto_transcrito}_\n\n"
                        f"🔄 *Procesando...*",
                        parse_mode='Markdown'
                    )
                    
                    # Procesar el texto transcrito como si fuera un mensaje de texto normal
                    respuesta = await self.bot.process_natural_query(
                        query=texto_transcrito,
                        user_id=user.id
                    )
                    
                    # Enviar respuesta final
                    await update.message.reply_text(
                        respuesta,
                        parse_mode='Markdown',
                        reply_markup=self.bot.keyboards.quick_actions()
                    )
                    
                    logger.info(f"✅ Procesamiento completo de audio para usuario {user.id}")
                    
                else:
                    error = resultado.get('error', 'Error desconocido')
                    logger.error(f"❌ Error en transcripción: {error}")
                    
                    await update.message.reply_text(
                        f"❌ **Error transcribiendo audio**\n\n"
                        f"Error: {error}\n\n"
                        f"💡 *Intenta de nuevo o usa texto*",
                        parse_mode='Markdown',
                        reply_markup=self.bot.keyboards.main_menu()
                    )
                
            except Exception as e:
                logger.error(f"❌ Error en transcripción: {e}")
                await update.message.reply_text(
                    "❌ **Error procesando el audio**\n\n"
                    "Inténtalo de nuevo en un momento.\n\n"
                    "💡 *Por ahora puedes usar mensajes de texto*",
                    parse_mode='Markdown',
                    reply_markup=self.bot.keyboards.main_menu()
                )
        
        except Exception as e:
            logger.error(f"❌ Error crítico en handler de voz: {e}")
            
            try:
                await update.message.reply_text(
                    "❌ Error del sistema procesando audio. Usa /start para reiniciar."
                )
            except:
                pass
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler para documentos (futuro)
        """
        await update.message.reply_text(
            "📎 El procesamiento de documentos estará disponible pronto.\n"
            "Por ahora, usa mensajes de texto.",
            reply_markup=self.bot.keyboards.main_menu()
        )