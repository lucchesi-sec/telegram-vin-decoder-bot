from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional


def get_details_keyboard(vin: str, has_history: bool = False, has_marketvalue: bool = False) -> InlineKeyboardMarkup:
    """Create inline keyboard for vehicle details sections"""
    buttons = []
    
    # Add buttons for available additional data
    row = []
    if has_marketvalue:
        row.append(InlineKeyboardButton("💰 Market Value", callback_data=f"show_marketvalue:{vin}"))
    if has_history:
        row.append(InlineKeyboardButton("📜 History", callback_data=f"show_history:{vin}"))
    
    if row:
        buttons.append(row)
    
    # Add refresh button
    buttons.append([InlineKeyboardButton("🔄 Refresh Data", callback_data=f"refresh:{vin}")])
    
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


def get_settings_keyboard(current_service: str = "NHTSA", has_carsxe_key: bool = False, has_autodev_key: bool = False) -> InlineKeyboardMarkup:
    """Create settings keyboard for service selection and API key management
    
    Args:
        current_service: Currently selected service (CarsXE, NHTSA, or AutoDev)
        has_carsxe_key: Whether user has a CarsXE API key configured
        has_autodev_key: Whether user has an Auto.dev API key configured
    """
    buttons = []
    
    # Service selection buttons
    carsxe_check = "✅" if current_service == "CarsXE" else ""
    nhtsa_check = "✅" if current_service == "NHTSA" else ""
    autodev_check = "✅" if current_service == "AutoDev" else ""
    
    # First row: CarsXE and NHTSA
    buttons.append([
        InlineKeyboardButton(
            f"{carsxe_check} CarsXE", 
            callback_data="set_service:CarsXE"
        ),
        InlineKeyboardButton(
            f"{nhtsa_check} NHTSA (Free)", 
            callback_data="set_service:NHTSA"
        )
    ])
    
    # Second row: Auto.dev
    buttons.append([
        InlineKeyboardButton(
            f"{autodev_check} Auto.dev (Premium)", 
            callback_data="set_service:AutoDev"
        )
    ])
    
    # API key management for CarsXE
    if current_service == "CarsXE":
        if has_carsxe_key:
            buttons.append([
                InlineKeyboardButton("🔐 Update API Key", callback_data="update_api_key:CarsXE"),
                InlineKeyboardButton("🗑️ Remove API Key", callback_data="remove_api_key:CarsXE")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("🔑 Add API Key", callback_data="add_api_key:CarsXE")
            ])
    
    # API key management for Auto.dev
    elif current_service == "AutoDev":
        if has_autodev_key:
            buttons.append([
                InlineKeyboardButton("🔐 Update API Key", callback_data="update_api_key:AutoDev"),
                InlineKeyboardButton("🗑️ Remove API Key", callback_data="remove_api_key:AutoDev")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("🔑 Add API Key", callback_data="add_api_key:AutoDev")
            ])
    
    # Info button
    buttons.append([
        InlineKeyboardButton("ℹ️ Service Info", callback_data="service_info"),
        InlineKeyboardButton("❌ Close", callback_data="close_menu")
    ])
    
    return InlineKeyboardMarkup(buttons)


def get_service_info_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for service information display"""
    buttons = [
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="show_settings")],
        [InlineKeyboardButton("❌ Close", callback_data="close_menu")]
    ]
    return InlineKeyboardMarkup(buttons)


def get_api_key_prompt_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for API key input prompt"""
    buttons = [
        [InlineKeyboardButton("❌ Cancel", callback_data="show_settings")]
    ]
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