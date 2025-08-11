"""Settings command handler."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import CommandHandler
from ..user_data import UserDataManager
from ..keyboards import get_settings_keyboard


class SettingsCommand(CommandHandler):
    """Handler for the /settings command."""
    
    @property
    def command(self) -> str:
        return "settings"
    
    @property
    def description(self) -> str:
        return "Configure decoder service and API keys"
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user settings for service selection and API key management."""
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        user_id = update.effective_user.id if update.effective_user else None
        
        if not user_data_mgr or not user_id:
            await update.message.reply_text("Settings are not available.")
            return
        
        # Get user settings
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
        
        # Create settings keyboard with actual service
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
        
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )