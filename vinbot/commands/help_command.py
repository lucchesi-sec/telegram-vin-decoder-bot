"""Help command handler."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import CommandHandler


HELP_TEXT = (
    "📚 **VIN Decoder Bot Help**\n\n"
    "**Basic Commands:**\n"
    "/start - Show welcome message\n"
    "/help - Show this help message\n"
    "/vin `<VIN>` - Decode a specific VIN\n"
    "/recent - View your recent searches\n"
    "/saved - View your saved vehicles\n"
    "/settings - Configure decoder service\n\n"
    "**How to use:**\n"
    "1️⃣ Send me any 17-character VIN directly\n"
    "2️⃣ Use the /vin command followed by a VIN\n"
    "3️⃣ Choose from sample VINs in /start\n\n"
    "**Features:**\n"
    "• Decode vehicle specifications\n"
    "• View manufacturing details\n"
    "• Check dimensions & performance\n"
    "• Save favorite vehicles\n"
    "• Search history tracking\n"
    "• Compare vehicles (Auto.dev)\n"
    "• Market value data (Auto.dev)\n\n"
    "**Services:**\n"
    "• **NHTSA** - Free government database\n"
    "• **Auto.dev** - Premium data with more details\n\n"
    "_Tip: Configure your preferred service in /settings_"
)


class HelpCommand(CommandHandler):
    """Handler for the /help command."""
    
    @property
    def command(self) -> str:
        return "help"
    
    @property  
    def description(self) -> str:
        return "Show help information"
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message."""
        await update.message.reply_text(
            HELP_TEXT,
            parse_mode=ParseMode.MARKDOWN
        )