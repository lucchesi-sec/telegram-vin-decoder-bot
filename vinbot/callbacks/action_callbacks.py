"""General action callback handlers."""

import logging
from telegram import CallbackQuery
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import CallbackStrategy
from ..user_data import UserDataManager
from ..formatter import (
    format_vehicle_summary,
    format_specs_section,
    format_manufacturing_section,
    format_dimensions_section,
    format_performance_section,
    format_features_section
)
from ..formatter_extensions import (
    format_market_value,
    format_history
)
from ..keyboards import get_details_keyboard

logger = logging.getLogger(__name__)


class ShowSectionCallback(CallbackStrategy):
    """Handle showing specific vehicle sections."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data.startswith("show_")
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Show a specific section of vehicle data."""
        # Parse the callback data
        parts = data.split(":")
        if len(parts) != 2:
            return
        
        section = parts[0].replace("show_", "")
        vin = parts[1]
        
        # Skip if it's a different type of show callback
        if section in ["recent", "saved", "settings", "level", "marketvalue", "history"]:
            return
        
        # Get the stored vehicle data
        vehicle_data = context.user_data.get(f"vehicle_data_{vin}")
        
        if not vehicle_data:
            # Try to fetch from user data manager
            user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
            if user_data_mgr:
                vehicle_data = await user_data_mgr.get_vehicle_data(vin)
        
        if not vehicle_data:
            await query.message.reply_text("Vehicle data not found. Please decode the VIN again.")
            return
        
        # Format the appropriate section
        if section == "all":
            text = format_vehicle_summary(vehicle_data)
            keyboard = None
        else:
            # Format specific section
            if section == "specs":
                text = format_specs_section(vehicle_data)
            elif section == "manufacturing":
                text = format_manufacturing_section(vehicle_data)
            elif section == "dimensions":
                text = format_dimensions_section(vehicle_data)
            elif section == "performance":
                text = format_performance_section(vehicle_data)
            elif section == "features":
                text = format_features_section(vehicle_data)
            else:
                text = "Unknown section requested."
            
            keyboard = get_details_keyboard(vin, [section])
        
        # Send as new message
        await query.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )


class ShowMarketValueCallback(CallbackStrategy):
    """Handle showing market value information."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data.startswith("show_marketvalue:")
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Show market value information for a vehicle."""
        vin = data.replace("show_marketvalue:", "")
        
        # Get stored vehicle data
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        vehicle_data = None
        
        # Try to get from context first
        if f"vehicle_data_{vin}" in context.user_data:
            vehicle_data = context.user_data[f"vehicle_data_{vin}"]
        elif user_data_mgr:
            vehicle_data = await user_data_mgr.get_vehicle_data(vin)
        
        if not vehicle_data:
            await query.message.reply_text("Vehicle data not found. Please decode the VIN again.")
            return
        
        # Format and send market value data
        text = format_market_value(vehicle_data)
        await query.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN
        )


class ShowHistoryCallback(CallbackStrategy):
    """Handle showing history information."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data.startswith("show_history:")
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Show history information for a vehicle."""
        vin = data.replace("show_history:", "")
        
        # Get stored vehicle data
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        vehicle_data = None
        
        # Try to get from context first
        if f"vehicle_data_{vin}" in context.user_data:
            vehicle_data = context.user_data[f"vehicle_data_{vin}"]
        elif user_data_mgr:
            vehicle_data = await user_data_mgr.get_vehicle_data(vin)
        
        if not vehicle_data:
            await query.message.reply_text("Vehicle data not found. Please decode the VIN again.")
            return
        
        # Format and send history data
        text = format_history(vehicle_data)
        await query.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN
        )


class NewVinCallback(CallbackStrategy):
    """Handle prompting for new VIN."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data == "new_vin"
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Prompt for new VIN."""
        await query.message.reply_text(
            "Please send me a 17-character VIN to decode:"
        )


class CloseMenuCallback(CallbackStrategy):
    """Handle closing the menu."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data == "close_menu"
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Close the menu."""
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.edit_text(
            query.message.text + "\n\n_[Menu closed]_",
            parse_mode=ParseMode.MARKDOWN
        )