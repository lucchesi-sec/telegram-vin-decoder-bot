"""Start command handler."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import CommandHandler
from ..keyboards import get_sample_vin_keyboard


WELCOME_TEXT = (
    "🚗 **Welcome to VIN Decoder Bot!**\n\n"
    "I can decode Vehicle Identification Numbers (VINs) using the official NHTSA database or Auto.dev.\n\n"
    "**How to use:**\n"
    "• Send me a 17-character VIN directly\n"
    "• Use /vin <VIN> command\n"
    "• Try sample VINs below\n\n"
    "**Other commands:**\n"
    "/help - Show all commands\n"
    "/recent - View recent searches\n"
    "/saved - View saved vehicles\n"
    "/settings - Configure decoder service\n"
)


class StartCommand(CommandHandler):
    """Handler for the /start command."""
    
    @property
    def command(self) -> str:
        return "start"
    
    @property
    def description(self) -> str:
        return "Show welcome message and instructions"
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send welcome message with sample VINs."""
        # Check if Auto.dev is configured by default
        settings = context.bot_data.get("settings")
        service_info = ""
        
        if settings and hasattr(settings, 'autodev_api_key') and settings.autodev_api_key:
            service_info = "\n\n✨ **Using Auto.dev (Premium) by default**"
        
        await update.message.reply_text(
            WELCOME_TEXT + service_info,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_sample_vin_keyboard()
        )