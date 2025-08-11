"""Settings service for managing bot and user settings."""

import logging
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import Service
from ..keyboards import get_settings_keyboard


class SettingsService(Service):
    """Service for managing settings operations."""
    
    async def get_settings_display_data(
        self,
        user_id: Optional[int],
        context: ContextTypes.DEFAULT_TYPE
    ) -> Dict[str, Any]:
        """Get data for displaying settings menu.
        
        Args:
            user_id: The user ID
            context: The bot context
            
        Returns:
            Dictionary with settings display data
        """
        # Get user service
        user_service = self.get_dependency('user_service')
        
        # Get user settings
        user_settings = {}
        if user_service and user_id:
            user_settings = await user_service.get_user_settings(user_id)
        
        has_autodev_key = bool(user_settings.get("autodev_api_key"))
        
        # Get default Auto.dev API key from environment
        bot_settings = context.bot_data.get("settings")
        default_autodev_key = ""
        if bot_settings and hasattr(bot_settings, 'autodev_api_key'):
            default_autodev_key = bot_settings.autodev_api_key
        
        # Determine actual service being used
        if default_autodev_key and user_settings.get("service") != "NHTSA":
            actual_service = "AutoDev"
            using_default_key = not has_autodev_key
        else:
            actual_service = user_settings.get("service", "NHTSA")
            using_default_key = False
        
        # Service descriptions
        if actual_service == "AutoDev":
            if using_default_key:
                current_desc = "✅ Using Auto.dev (Enhanced) - Default API key"
            elif has_autodev_key:
                current_desc = "✅ Using Auto.dev (Enhanced) - Your API key"
            else:
                current_desc = "✅ Using Auto.dev (Enhanced)"
        else:
            current_desc = "✅ Using NHTSA (Basic) - Free, no API key required"
        
        return {
            'actual_service': actual_service,
            'has_autodev_key': has_autodev_key,
            'using_default_key': using_default_key,
            'current_desc': current_desc
        }
    
    async def format_settings_message(
        self,
        settings_data: Dict[str, Any]
    ) -> tuple[str, Any]:
        """Format the settings message and keyboard.
        
        Args:
            settings_data: The settings display data
            
        Returns:
            Tuple of (message_text, keyboard)
        """
        keyboard = get_settings_keyboard(
            current_service=settings_data['actual_service'],
            has_autodev_key=settings_data['has_autodev_key']
        )
        
        text = (
            "⚙️ **Settings**\n\n"
            f"**Current Service:** {settings_data['current_desc']}\n\n"
            "Select a service below to change your preference:\n"
            "• **NHTSA (Basic)** - Free government database\n"
            "• **Auto.dev (Enhanced)** - Premium data with more details\n\n"
            "_The green checkmark shows your active service._"
        )
        
        return text, keyboard
    
    async def handle_service_change(
        self,
        user_id: int,
        new_service: str,
        context: ContextTypes.DEFAULT_TYPE
    ) -> Dict[str, Any]:
        """Handle a service change request.
        
        Args:
            user_id: The user ID
            new_service: The new service to use
            context: The bot context
            
        Returns:
            Updated settings display data
        """
        # Get user service
        user_service = self.get_dependency('user_service')
        
        if not user_service:
            raise ValueError("User service not available")
        
        # Update the service
        await user_service.update_user_service(user_id, new_service)
        
        # Return updated settings data
        return await self.get_settings_display_data(user_id, context)
    
    async def prompt_for_api_key(
        self,
        service: str,
        context: ContextTypes.DEFAULT_TYPE,
        is_update: bool = False
    ) -> str:
        """Set up context for API key input.
        
        Args:
            service: The service requiring an API key
            context: The bot context
            is_update: Whether this is updating an existing key
            
        Returns:
            Message to display to user
        """
        context.user_data["awaiting_api_key_for"] = service
        context.user_data["api_key_update"] = is_update
        
        service_name = "Auto.dev" if service == "AutoDev" else service
        
        return (
            f"🔑 **Enter your {service_name} API Key**\n\n"
            f"Please send your {service_name} API key in the next message.\n\n"
            "Note: Your API key will be stored securely and used only for VIN decoding requests."
        )