"""VIN command handler."""

from telegram import Update
from telegram.ext import ContextTypes

from .base import CommandHandler
from ..vin import normalize_vin


class VinCommand(CommandHandler):
    """Handler for the /vin command."""
    
    @property
    def command(self) -> str:
        return "vin"
    
    @property
    def description(self) -> str:
        return "Decode a VIN (usage: /vin <17-character VIN>)"
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Decode a VIN provided as command argument."""
        if not context.args:
            await update.message.reply_text("Usage: /vin <17-character VIN>")
            return
        
        vin = normalize_vin("".join(context.args))
        
        # Import here to avoid circular dependency
        from ..bot import handle_vin_decode
        await handle_vin_decode(update, context, vin)