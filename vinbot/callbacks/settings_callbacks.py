"""Settings-related callback handlers."""

import logging
from telegram import CallbackQuery
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import CallbackStrategy
from ..user_data import UserDataManager
from ..keyboards import (
    get_settings_keyboard,
    get_service_info_keyboard,
    get_api_key_prompt_keyboard
)

logger = logging.getLogger(__name__)


class ShowSettingsCallback(CallbackStrategy):
    """Handle showing settings menu."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data == "show_settings"
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Show settings menu."""
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        user_id = query.from_user.id if query.from_user else None
        
        if not user_data_mgr or not user_id:
            await query.message.reply_text("Settings are not available.")
            return
        
        user_settings = await user_data_mgr.get_user_settings(user_id)
        has_autodev_key = bool(user_settings.get("autodev_api_key"))
        
        # Get default Auto.dev API key from environment
        bot_settings = context.bot_data.get("settings")
        default_autodev_key = bot_settings.autodev_api_key if bot_settings and hasattr(bot_settings, 'autodev_api_key') else ""
        
        # Determine actual service being used
        if default_autodev_key and user_settings.get("service") != "NHTSA":
            actual_service = "AutoDev"
            using_default_key = not has_autodev_key
        else:
            actual_service = user_settings.get("service", "NHTSA")
            using_default_key = False
        
        keyboard = get_settings_keyboard(
            current_service=actual_service,
            has_autodev_key=has_autodev_key
        )
        
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
        
        text = (
            "⚙️ **Settings**\n\n"
            f"**Current Service:** {current_desc}\n\n"
            "Select a service below to change your preference:\n"
            "• **NHTSA (Basic)** - Free government database\n"
            "• **Auto.dev (Enhanced)** - Premium data with more details\n\n"
            "_The green checkmark shows your active service._"
        )
        
        await query.message.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )


class SetServiceCallback(CallbackStrategy):
    """Handle setting user's preferred service."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data.startswith("set_service:")
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Set user's preferred service."""
        service = data.split(":")[1]
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        user_id = query.from_user.id if query.from_user else None
        
        if not user_data_mgr or not user_id:
            await query.message.reply_text("Unable to update settings.")
            return
        
        # Update user's service preference
        await user_data_mgr.set_user_service(user_id, service)
        
        # Get updated settings
        settings = await user_data_mgr.get_user_settings(user_id)
        current_service = settings.get("service", "NHTSA")
        has_autodev_key = bool(settings.get("autodev_api_key"))
        
        keyboard = get_settings_keyboard(
            current_service=current_service,
            has_autodev_key=has_autodev_key
        )
        
        service_desc = {
            "NHTSA": "✅ Using NHTSA (Free, no API key required)",
            "AutoDev": "🔄 Using Auto.dev (Requires API key)",
        }
        
        current_desc = service_desc.get(current_service, "NHTSA (Free)")
        
        text = (
            "⚙️ **Settings**\n\n"
            f"**Current Service:** {current_desc}\n\n"
            "Select a service below to change your preference. "
            "Auto.dev provides more detailed vehicle information but requires an API key.\n\n"
            "NHTSA is completely free and provides basic vehicle information."
        )
        
        await query.message.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
        
        # If switching to AutoDev and no API key is set, prompt for one
        if service == "AutoDev" and not has_autodev_key:
            await query.message.reply_text(
                "🔑 **Auto.dev API Key Required**\n\n"
                "To use Auto.dev, please add your API key.\n"
                "Click the '🔑 Add API Key' button below, or use the /settings command again after obtaining your key.",
                parse_mode=ParseMode.MARKDOWN
            )


class ApiKeyCallback(CallbackStrategy):
    """Handle API key management."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return (callback_data.startswith("add_api_key:") or 
                callback_data.startswith("update_api_key:") or
                callback_data.startswith("remove_api_key:"))
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Handle API key operations."""
        if data.startswith("remove_api_key:"):
            await self._remove_api_key(query, context, data)
        else:
            await self._prompt_for_api_key(query, context, data)
    
    async def _prompt_for_api_key(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Prompt user to enter API key."""
        service = data.split(":")[1]
        context.user_data["awaiting_api_key_for"] = service
        context.user_data["api_key_update"] = data.startswith("update_api_key:")
        
        service_name = "Auto.dev" if service == "AutoDev" else service
        
        await query.message.reply_text(
            f"🔑 **Enter your {service_name} API Key**\n\n"
            f"Please send your {service_name} API key in the next message.\n\n"
            "Note: Your API key will be stored securely and used only for VIN decoding requests.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_api_key_prompt_keyboard()
        )
    
    async def _remove_api_key(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Remove API key for a service."""
        service = data.split(":")[1]
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        user_id = query.from_user.id if query.from_user else None
        
        if not user_data_mgr or not user_id:
            await query.message.reply_text("Unable to remove API key.")
            return
        
        # Clear the API key
        await user_data_mgr.clear_user_api_key(user_id, service)
        
        # If this was the current service, switch back to NHTSA
        settings = await user_data_mgr.get_user_settings(user_id)
        current_service = settings.get("service", "NHTSA")
        if current_service == service:
            await user_data_mgr.set_user_service(user_id, "NHTSA")
        
        # Show updated settings
        updated_settings = await user_data_mgr.get_user_settings(user_id)
        current_service = updated_settings.get("service", "NHTSA")
        has_autodev_key = bool(updated_settings.get("autodev_api_key"))
        
        keyboard = get_settings_keyboard(
            current_service=current_service,
            has_autodev_key=has_autodev_key
        )
        
        service_desc = {
            "NHTSA": "✅ Using NHTSA (Free, no API key required)",
            "AutoDev": "🔄 Using Auto.dev (Requires API key)",
        }
        
        current_desc = service_desc.get(current_service, "NHTSA (Free)")
        
        text = (
            "⚙️ **Settings**\n\n"
            f"**Current Service:** {current_desc}\n\n"
            "Select a service below to change your preference. "
            "Auto.dev provides more detailed vehicle information but requires an API key.\n\n"
            "NHTSA is completely free and provides basic vehicle information."
        )
        
        await query.message.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
        
        # Notify user
        service_name = "Auto.dev" if service == "AutoDev" else service
        await query.message.reply_text(
            f"✅ API key for {service_name} has been removed."
        )


class ServiceInfoCallback(CallbackStrategy):
    """Handle showing service information."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data == "service_info"
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Show service information."""
        text = (
            "ℹ️ **Service Information**\n\n"
            "**NHTSA (National Highway Traffic Safety Administration)**\n"
            "• Free service provided by the U.S. government\n"
            "• Basic vehicle information\n"
            "• No API key required\n"
            "• Data includes make, model, year, body type, etc.\n\n"
            "**Auto.dev**\n"
            "• Premium service with detailed vehicle data\n"
            "• Requires a paid API key\n"
            "• More comprehensive information including features, options, market value, etc.\n"
            "• Visit auto.dev to get an API key\n\n"
            "You can switch between services at any time in settings."
        )
        
        keyboard = get_service_info_keyboard()
        
        await query.message.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )