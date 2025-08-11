"""Recent command handler."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import CommandHandler
from ..user_data import UserDataManager
from ..keyboards import get_recent_vins_keyboard, get_sample_vin_keyboard


class RecentCommand(CommandHandler):
    """Handler for the /recent command."""
    
    @property
    def command(self) -> str:
        return "recent"
    
    @property
    def description(self) -> str:
        return "View your recent VIN searches"
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show recent VIN searches."""
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        user_id = update.effective_user.id if update.effective_user else None
        
        if not user_data_mgr or not user_id:
            await update.message.reply_text("Recent searches are not available.")
            return
        
        recent = await user_data_mgr.get_history(user_id)
        
        if not recent:
            await update.message.reply_text(
                "No recent searches found.\n\n"
                "Start by decoding a VIN to build your history!",
                reply_markup=get_sample_vin_keyboard()
            )
            return
        
        keyboard = get_recent_vins_keyboard(recent)
        await update.message.reply_text(
            "🕐 **Recent Searches**\n\n"
            "_Select a vehicle to decode again:_",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )