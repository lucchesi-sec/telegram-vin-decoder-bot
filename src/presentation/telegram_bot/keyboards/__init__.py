"""Keyboard utilities for the Telegram bot."""

from typing import List, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.domain.vehicle.value_objects import VINNumber


def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create main menu inline keyboard.
    
    Returns:
        Inline keyboard markup
    """
    buttons = [
        [InlineKeyboardButton("📋 Recent VINs", callback_data="recent")],
        [InlineKeyboardButton("💾 Saved VINs", callback_data="saved")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    
    return InlineKeyboardMarkup(buttons)


def create_settings_keyboard() -> InlineKeyboardMarkup:
    """Create settings inline keyboard.
    
    Returns:
        Inline keyboard markup
    """
    buttons = [
        [InlineKeyboardButton("🔌 Decoder Service", callback_data="decoder_service")],
        [InlineKeyboardButton("🔑 API Keys", callback_data="api_keys")],
        [InlineKeyboardButton("📱 Preferences", callback_data="preferences")],
        [InlineKeyboardButton("🔙 Back to Main", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(buttons)


def get_details_keyboard(vin: str) -> InlineKeyboardMarkup:
    """Create inline keyboard for vehicle details actions.
    
    Args:
        vin: Vehicle VIN
        
    Returns:
        Inline keyboard markup
    """
    buttons = [
        [InlineKeyboardButton("🔄 Refresh Data", callback_data=f"refresh:{vin}")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    return InlineKeyboardMarkup(buttons)


def get_refresh_keyboard(vin: str) -> InlineKeyboardMarkup:
    """Create inline keyboard with refresh option.
    
    Args:
        vin: Vehicle VIN
        
    Returns:
        Inline keyboard markup
    """
    buttons = [
        [InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh:{vin}")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    return InlineKeyboardMarkup(buttons)


def get_close_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard with close option.
    
    Returns:
        Inline keyboard markup
    """
    buttons = [
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    return InlineKeyboardMarkup(buttons)