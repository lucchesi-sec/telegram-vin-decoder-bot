from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional


def get_details_keyboard(vin: str, sections_shown: List[str] = None) -> InlineKeyboardMarkup:
    """Create inline keyboard for vehicle details sections"""
    if sections_shown is None:
        sections_shown = []
    
    buttons = []
    
    # First row - Main sections
    row1 = []
    if "specs" not in sections_shown:
        row1.append(InlineKeyboardButton("📋 Specs", callback_data=f"show_specs:{vin}"))
    if "manufacturing" not in sections_shown:
        row1.append(InlineKeyboardButton("🏭 Manufacturing", callback_data=f"show_manufacturing:{vin}"))
    if buttons or row1:
        buttons.append(row1)
    
    # Second row - Technical details
    row2 = []
    if "dimensions" not in sections_shown:
        row2.append(InlineKeyboardButton("📏 Dimensions", callback_data=f"show_dimensions:{vin}"))
    if "performance" not in sections_shown:
        row2.append(InlineKeyboardButton("🏁 Performance", callback_data=f"show_performance:{vin}"))
    if row2:
        buttons.append(row2)
    
    # Third row - Additional info
    row3 = []
    if "features" not in sections_shown:
        row3.append(InlineKeyboardButton("🔧 Features", callback_data=f"show_features:{vin}"))
    if "all" not in sections_shown:
        row3.append(InlineKeyboardButton("📊 All Details", callback_data=f"show_all:{vin}"))
    if row3:
        buttons.append(row3)
    
    return InlineKeyboardMarkup(buttons)


def get_actions_keyboard(vin: str, user_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for quick actions after VIN decode"""
    buttons = [
        [
            InlineKeyboardButton("💾 Save", callback_data=f"save_vin:{vin}:{user_id}"),
            InlineKeyboardButton("📤 Share", callback_data=f"share_vin:{vin}")
        ],
        [
            InlineKeyboardButton("🔍 New VIN", callback_data="new_vin"),
            InlineKeyboardButton("📊 Compare", callback_data=f"compare_start:{vin}")
        ],
        [
            InlineKeyboardButton("🕐 Recent", callback_data="show_recent"),
            InlineKeyboardButton("⭐ Saved", callback_data="show_saved")
        ]
    ]
    
    return InlineKeyboardMarkup(buttons)


def get_recent_vins_keyboard(recent_vins: List[tuple]) -> InlineKeyboardMarkup:
    """Create keyboard for recent VIN searches
    
    Args:
        recent_vins: List of tuples (vin, make_model, timestamp)
    """
    buttons = []
    
    for vin, make_model, _ in recent_vins[:5]:  # Show max 5 recent
        display_text = f"{make_model[:20]}" if make_model else vin
        buttons.append([
            InlineKeyboardButton(
                f"🕐 {display_text}", 
                callback_data=f"decode_vin:{vin}"
            )
        ])
    
    if buttons:
        buttons.append([InlineKeyboardButton("❌ Close", callback_data="close_menu")])
    
    return InlineKeyboardMarkup(buttons)


def get_saved_vins_keyboard(saved_vins: List[tuple]) -> InlineKeyboardMarkup:
    """Create keyboard for saved vehicles
    
    Args:
        saved_vins: List of tuples (vin, nickname, make_model)
    """
    buttons = []
    
    for vin, nickname, make_model in saved_vins[:10]:  # Show max 10 saved
        display_text = nickname if nickname else (make_model[:20] if make_model else vin)
        buttons.append([
            InlineKeyboardButton(
                f"⭐ {display_text}", 
                callback_data=f"decode_vin:{vin}"
            ),
            InlineKeyboardButton(
                "🗑️",
                callback_data=f"delete_saved:{vin}"
            )
        ])
    
    if buttons:
        buttons.append([InlineKeyboardButton("❌ Close", callback_data="close_menu")])
    
    return InlineKeyboardMarkup(buttons)


def get_sample_vin_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with sample VIN for testing"""
    buttons = [[
        InlineKeyboardButton(
            "🚗 Try Sample VIN", 
            callback_data="sample_vin:1HGBH41JXMN109186"
        )
    ]]
    
    return InlineKeyboardMarkup(buttons)


def get_comparison_keyboard(vin1: str, vin2: Optional[str] = None) -> InlineKeyboardMarkup:
    """Create keyboard for VIN comparison feature"""
    if vin2:
        # Both VINs provided, show comparison options
        buttons = [
            [InlineKeyboardButton("📊 View Comparison", callback_data=f"compare_view:{vin1}:{vin2}")],
            [InlineKeyboardButton("🔄 Compare Different", callback_data="compare_new")]
        ]
    else:
        # Only first VIN provided, prompt for second
        buttons = [
            [InlineKeyboardButton("➕ Add Second VIN", callback_data=f"compare_add:{vin1}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="close_menu")]
        ]
    
    return InlineKeyboardMarkup(buttons)


def get_confirmation_keyboard(action: str, data: str) -> InlineKeyboardMarkup:
    """Create yes/no confirmation keyboard"""
    buttons = [[
        InlineKeyboardButton("✅ Yes", callback_data=f"confirm_{action}:{data}"),
        InlineKeyboardButton("❌ No", callback_data="close_menu")
    ]]
    
    return InlineKeyboardMarkup(buttons)


def get_back_button(callback_data: str = "back") -> InlineKeyboardMarkup:
    """Create a simple back button"""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⬅️ Back", callback_data=callback_data)
    ]])


def get_close_button() -> InlineKeyboardMarkup:
    """Create a simple close button"""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Close", callback_data="close_menu")
    ]])