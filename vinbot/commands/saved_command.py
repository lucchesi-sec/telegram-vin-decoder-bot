"""Saved command handler."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import CommandHandler
from ..user_data import UserDataManager
from ..keyboards import get_saved_vins_keyboard


class SavedCommand(CommandHandler):
    """Handler for the /saved command."""
    
    @property
    def command(self) -> str:
        return "saved"
    
    @property
    def description(self) -> str:
        return "View your saved vehicles"
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show saved vehicles."""
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        user_id = update.effective_user.id if update.effective_user else None
        
        if not user_data_mgr or not user_id:
            await update.message.reply_text("Saved vehicles are not available.")
            return
        
        saved = await user_data_mgr.get_favorites(user_id)
        
        if not saved:
            await update.message.reply_text(
                "No saved vehicles found.\n\n"
                "After decoding a VIN, use the 💾 Save button to add it to your favorites!"
            )
            return
        
        keyboard = get_saved_vins_keyboard(saved)
        await update.message.reply_text(
            "⭐ **Saved Vehicles**\n\n"
            "_Select a vehicle to view or 🗑️ to remove:_",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )