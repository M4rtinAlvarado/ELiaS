"""
Keyboards y UI para Telegram Bot
================================

Teclados inline y elementos de interfaz de usuario para mejorar 
la experiencia del usuario en Telegram.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional

class TelegramKeyboards:
    """
    Clase para generar keyboards inline y elementos de UI
    """
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Menú principal del bot"""
        keyboard = [
            [
                InlineKeyboardButton("📋 Ver Tareas", callback_data="view_tasks"),
                InlineKeyboardButton("✨ Nueva Tarea", callback_data="new_task")
            ],
            [
                InlineKeyboardButton("📁 Proyectos", callback_data="view_projects"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="stats")
            ],
            [
                InlineKeyboardButton("❓ Ayuda", callback_data="help"),
                InlineKeyboardButton("⚙️ Config", callback_data="config")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def task_actions() -> InlineKeyboardMarkup:
        """Acciones para tareas"""
        keyboard = [
            [
                InlineKeyboardButton("📋 Todas", callback_data="tasks_all"),
                InlineKeyboardButton("⏳ Pendientes", callback_data="tasks_pending")
            ],
            [
                InlineKeyboardButton("✅ Completadas", callback_data="tasks_completed"),
                InlineKeyboardButton("🚨 Urgentes", callback_data="tasks_urgent")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def project_selector(projects: List[str]) -> InlineKeyboardMarkup:
        """Selector de proyectos"""
        keyboard = []
        
        # Agregar botones de proyectos (máximo 2 por fila)
        for i in range(0, len(projects), 2):
            row = []
            for j in range(2):
                if i + j < len(projects):
                    project = projects[i + j]
                    row.append(InlineKeyboardButton(
                        f"📁 {project[:15]}...", 
                        callback_data=f"project_{project}"
                    ))
            keyboard.append(row)
        
        # Botón volver
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="main_menu")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def task_priority_selector() -> InlineKeyboardMarkup:
        """Selector de prioridad para nuevas tareas"""
        keyboard = [
            [
                InlineKeyboardButton("🟢 Baja", callback_data="priority_baja"),
                InlineKeyboardButton("🟡 Media", callback_data="priority_media")
            ],
            [
                InlineKeyboardButton("🟠 Alta", callback_data="priority_alta"),
                InlineKeyboardButton("🔴 Crítica", callback_data="priority_critica")
            ],
            [
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_task")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_action(action: str, item_id: str = None) -> InlineKeyboardMarkup:
        """Confirmación para acciones críticas"""
        callback_confirm = f"confirm_{action}"
        callback_cancel = f"cancel_{action}"
        
        if item_id:
            callback_confirm += f"_{item_id}"
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data=callback_confirm),
                InlineKeyboardButton("❌ Cancelar", callback_data=callback_cancel)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def quick_actions() -> InlineKeyboardMarkup:
        """Acciones rápidas para usuarios frecuentes"""
        keyboard = [
            [
                InlineKeyboardButton("🚀 Tarea Rápida", callback_data="quick_task"),
                InlineKeyboardButton("📋 Resumen Hoy", callback_data="today_summary")
            ],
            [
                InlineKeyboardButton("🏠 Menú Principal", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod  
    def admin_panel() -> InlineKeyboardMarkup:
        """Panel de administración (solo para admins)"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Analytics", callback_data="admin_analytics"),
                InlineKeyboardButton("👥 Usuarios", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("🔧 Sistema", callback_data="admin_system"),
                InlineKeyboardButton("📝 Logs", callback_data="admin_logs")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_button() -> InlineKeyboardMarkup:
        """Botón simple para volver"""
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="main_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def help_categories() -> InlineKeyboardMarkup:
        """Categorías de ayuda"""
        keyboard = [
            [
                InlineKeyboardButton("🤖 Comandos IA", callback_data="help_ai"),
                InlineKeyboardButton("📋 Gestión Tareas", callback_data="help_tasks")
            ],
            [
                InlineKeyboardButton("📁 Proyectos", callback_data="help_projects"),
                InlineKeyboardButton("⚙️ Configuración", callback_data="help_config")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)