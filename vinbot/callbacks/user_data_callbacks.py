"""User data management callback handlers."""

import logging
from telegram import CallbackQuery
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import CallbackStrategy
from ..user_data import UserDataManager
from ..keyboards import (
    get_recent_vins_keyboard,
    get_saved_vins_keyboard
)

logger = logging.getLogger(__name__)


class SaveVehicleCallback(CallbackStrategy):
    """Handle saving vehicles to favorites."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data.startswith("save_vin:")
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Save a vehicle to favorites."""
        parts = data.split(":")
        if len(parts) < 2:
            await query.message.reply_text("Invalid save request.")
            return
        
        vin = parts[1]
        user_id = query.from_user.id if query.from_user else None
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        
        if not user_data_mgr or not user_id:
            await query.message.reply_text("Unable to save vehicle.")
            return
        
        # Get vehicle data
        vehicle_data = context.user_data.get(f"vehicle_data_{vin}")
        if not vehicle_data:
            vehicle_data = await user_data_mgr.get_vehicle_data(vin)
        
        if not vehicle_data:
            await query.message.reply_text("Vehicle data not found.")
            return
        
        # Save to favorites
        success = await user_data_mgr.add_to_favorites(user_id, vin, vehicle_data)
        
        if success:
            await query.message.reply_text(
                "✅ **Vehicle Saved!**\n\n"
                "You can view your saved vehicles with /saved",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.message.reply_text("Failed to save vehicle. Please try again.")


class DeleteSavedCallback(CallbackStrategy):
    """Handle removing vehicles from favorites."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data.startswith("delete_saved:")
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Remove a vehicle from favorites."""
        vin = data.replace("delete_saved:", "")
        user_id = query.from_user.id if query.from_user else None
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        
        if not user_data_mgr or not user_id:
            await query.message.reply_text("Unable to remove vehicle.")
            return
        
        success = await user_data_mgr.remove_from_favorites(user_id, vin)
        
        if success:
            # Update the saved vehicles list
            saved = await user_data_mgr.get_favorites(user_id)
            if saved:
                keyboard = get_saved_vins_keyboard(saved)
                await query.message.edit_text(
                    "⭐ **Saved Vehicles**\n\n"
                    "_Vehicle removed. Select another vehicle:_",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            else:
                await query.message.edit_text(
                    "No saved vehicles remaining.\n\n"
                    "After decoding a VIN, use the 💾 Save button to add it to your favorites!"
                )
        else:
            await query.message.reply_text("Failed to remove vehicle.")


class ShowRecentCallback(CallbackStrategy):
    """Handle showing recent searches."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data == "show_recent"
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Show recent searches."""
        user_id = query.from_user.id if query.from_user else None
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        
        if not user_data_mgr or not user_id:
            await query.message.edit_text("Recent searches are not available.")
            return
        
        recent = await user_data_mgr.get_history(user_id)
        
        if recent:
            keyboard = get_recent_vins_keyboard(recent)
            await query.message.edit_text(
                "🕐 **Recent Searches**\n\n"
                "_Select a vehicle to decode again:_",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        else:
            await query.message.edit_text("No recent searches found.")


class ShowSavedCallback(CallbackStrategy):
    """Handle showing saved vehicles."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data == "show_saved"
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Show saved vehicles."""
        user_id = query.from_user.id if query.from_user else None
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        
        if not user_data_mgr or not user_id:
            await query.message.edit_text("Saved vehicles are not available.")
            return
        
        saved = await user_data_mgr.get_favorites(user_id)
        
        if saved:
            keyboard = get_saved_vins_keyboard(saved)
            await query.message.edit_text(
                "⭐ **Saved Vehicles**\n\n"
                "_Select a vehicle to view:_",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        else:
            await query.message.edit_text("No saved vehicles found.")