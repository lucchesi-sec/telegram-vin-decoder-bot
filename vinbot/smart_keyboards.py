"""
Smart Keyboard Layouts for Progressive Disclosure

This module provides intelligent keyboard layouts that adapt to:
- Information disclosure levels
- Available data richness  
- User preferences and context
- Mobile vs desktop optimization
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional, Dict, Any
from .smart_formatter import InformationLevel, get_available_disclosure_levels


def get_smart_details_keyboard(
    vin: str, 
    current_level: InformationLevel = InformationLevel.STANDARD,
    available_levels: Optional[List[InformationLevel]] = None,
    has_history: bool = False, 
    has_marketvalue: bool = False,
    user_context: Optional[Dict] = None
) -> InlineKeyboardMarkup:
    """
    Create smart keyboard for progressive information disclosure
    
    Args:
        vin: Vehicle VIN for callback data
        current_level: Currently displayed information level
        available_levels: Available disclosure levels for this vehicle
        has_history: Whether vehicle has history data
        has_marketvalue: Whether vehicle has market value data
        user_context: User preferences and context
        
    Returns:
        InlineKeyboardMarkup optimized for current context
    """
    buttons = []
    
    # Progressive disclosure buttons
    if available_levels and len(available_levels) > 1:
        disclosure_row = _create_disclosure_row(vin, current_level, available_levels)
        if disclosure_row:
            buttons.append(disclosure_row)
    
    # Data-specific action buttons
    action_row = []
    
    # Add premium data buttons if available
    if has_marketvalue:
        action_row.append(InlineKeyboardButton("💰 Value", callback_data=f"show_marketvalue:{vin}"))
    
    if has_history:
        action_row.append(InlineKeyboardButton("📜 History", callback_data=f"show_history:{vin}"))
    
    # Add action row if we have buttons
    if action_row:
        buttons.append(action_row)
    
    # Quick actions row
    quick_actions = _create_quick_actions_row(vin, user_context)
    if quick_actions:
        buttons.append(quick_actions)
    
    # Utility row
    utility_row = []
    utility_row.append(InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh:{vin}"))
    utility_row.append(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
    buttons.append(utility_row)
    
    return InlineKeyboardMarkup(buttons)


def _create_disclosure_row(
    vin: str, 
    current_level: InformationLevel, 
    available_levels: List[InformationLevel]
) -> Optional[List[InlineKeyboardButton]]:
    """Create row of buttons for information level selection"""
    if len(available_levels) <= 1:
        return None
    
    buttons = []
    
    # Create buttons for each available level (except current)
    level_configs = {
        InformationLevel.ESSENTIAL: ("🔹", "Quick"),
        InformationLevel.STANDARD: ("📋", "Standard"), 
        InformationLevel.DETAILED: ("📊", "Detailed"),
        InformationLevel.COMPLETE: ("📚", "Complete")
    }
    
    for level in available_levels:
        if level == current_level:
            continue  # Skip current level
            
        emoji, label = level_configs.get(level, ("📄", "Info"))
        
        # Show emoji + label for most important levels
        if level in [InformationLevel.ESSENTIAL, InformationLevel.COMPLETE]:
            button_text = f"{emoji} {label}"
        else:
            button_text = emoji
        
        buttons.append(InlineKeyboardButton(
            button_text, 
            callback_data=f"show_level:{level.value}:{vin}"
        ))
    
    # Limit to 3 buttons per row for mobile compatibility
    return buttons[:3] if len(buttons) <= 3 else buttons[:2]


def _create_quick_actions_row(vin: str, user_context: Optional[Dict] = None) -> List[InlineKeyboardButton]:
    """Create quick action buttons based on user context"""
    buttons = []
    
    # Always include save
    buttons.append(InlineKeyboardButton("💾 Save", callback_data=f"save_vin:{vin}"))
    
    # Include share
    buttons.append(InlineKeyboardButton("📤 Share", callback_data=f"share_vin:{vin}"))
    
    # Context-aware additions
    if user_context:
        # If user has comparison history, add compare
        if user_context.get("has_comparisons", False):
            buttons.append(InlineKeyboardButton("⚖️ Compare", callback_data=f"compare_start:{vin}"))
        
        # If user searches frequently, add history
        if user_context.get("frequent_user", False):
            buttons.append(InlineKeyboardButton("🕐 Recent", callback_data="show_recent"))
    else:
        # Default actions for new users
        buttons.append(InlineKeyboardButton("🔍 New VIN", callback_data="new_vin"))
    
    return buttons


def get_level_selection_keyboard(
    vin: str,
    available_levels: List[InformationLevel],
    current_level: InformationLevel
) -> InlineKeyboardMarkup:
    """
    Create detailed keyboard for level selection with descriptions
    
    Args:
        vin: Vehicle VIN
        available_levels: Available information levels
        current_level: Currently displayed level
        
    Returns:
        Keyboard with level options and descriptions
    """
    buttons = []
    
    level_info = {
        InformationLevel.ESSENTIAL: ("🔹", "Quick Facts", "Year, Make, Model, Body Type"),
        InformationLevel.STANDARD: ("📋", "Standard Info", "Engine, Performance, Features"),
        InformationLevel.DETAILED: ("📊", "Detailed View", "Dimensions, Manufacturing, Specs"),
        InformationLevel.COMPLETE: ("📚", "Complete Data", "Everything Available")
    }
    
    for level in available_levels:
        emoji, title, description = level_info.get(level, ("📄", "Info", "Additional data"))
        
        # Mark current level
        if level == current_level:
            button_text = f"{emoji} {title} ✓"
        else:
            button_text = f"{emoji} {title}"
        
        buttons.append([InlineKeyboardButton(
            button_text, 
            callback_data=f"show_level:{level.value}:{vin}"
        )])
    
    # Add back button
    buttons.append([InlineKeyboardButton("⬅️ Back to Vehicle", callback_data=f"back_to_vehicle:{vin}")])
    
    return InlineKeyboardMarkup(buttons)


def get_mobile_optimized_keyboard(
    vin: str,
    has_history: bool = False,
    has_marketvalue: bool = False
) -> InlineKeyboardMarkup:
    """
    Create mobile-optimized keyboard with larger touch targets
    
    Args:
        vin: Vehicle VIN
        has_history: Whether vehicle has history data  
        has_marketvalue: Whether vehicle has market value data
        
    Returns:
        Mobile-optimized keyboard layout
    """
    buttons = []
    
    # Main actions - one per row for easy tapping
    buttons.append([InlineKeyboardButton("📊 Show More Details", callback_data=f"show_level:{InformationLevel.DETAILED.value}:{vin}")])
    
    # Premium data if available
    if has_marketvalue or has_history:
        premium_row = []
        if has_marketvalue:
            premium_row.append(InlineKeyboardButton("💰 Market Value", callback_data=f"show_marketvalue:{vin}"))
        if has_history:
            premium_row.append(InlineKeyboardButton("📜 Vehicle History", callback_data=f"show_history:{vin}"))
        buttons.append(premium_row)
    
    # Quick actions
    buttons.append([
        InlineKeyboardButton("💾 Save Vehicle", callback_data=f"save_vin:{vin}"),
        InlineKeyboardButton("📤 Share VIN", callback_data=f"share_vin:{vin}")
    ])
    
    # Navigation
    buttons.append([
        InlineKeyboardButton("🔍 Decode New VIN", callback_data="new_vin"),
        InlineKeyboardButton("❌ Close", callback_data="close_menu")
    ])
    
    return InlineKeyboardMarkup(buttons)


def get_desktop_optimized_keyboard(
    vin: str,
    current_level: InformationLevel,
    available_levels: List[InformationLevel],
    has_history: bool = False,
    has_marketvalue: bool = False
) -> InlineKeyboardMarkup:
    """
    Create desktop-optimized keyboard with compact layout
    
    Args:
        vin: Vehicle VIN
        current_level: Current information level
        available_levels: Available levels
        has_history: Whether vehicle has history data
        has_marketvalue: Whether vehicle has market value data
        
    Returns:
        Desktop-optimized keyboard layout
    """
    buttons = []
    
    # Information levels in one row
    level_row = _create_disclosure_row(vin, current_level, available_levels)
    if level_row:
        buttons.append(level_row)
    
    # Data and actions in combined rows
    action_row = []
    if has_marketvalue:
        action_row.append(InlineKeyboardButton("💰 Value", callback_data=f"show_marketvalue:{vin}"))
    if has_history:
        action_row.append(InlineKeyboardButton("📜 History", callback_data=f"show_history:{vin}"))
    
    action_row.extend([
        InlineKeyboardButton("💾 Save", callback_data=f"save_vin:{vin}"),
        InlineKeyboardButton("📤 Share", callback_data=f"share_vin:{vin}")
    ])
    
    if action_row:
        buttons.append(action_row)
    
    # Utility row
    buttons.append([
        InlineKeyboardButton("🔍 New VIN", callback_data="new_vin"),
        InlineKeyboardButton("🕐 Recent", callback_data="show_recent"),
        InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh:{vin}"),
        InlineKeyboardButton("❌ Close", callback_data="close_menu")
    ])
    
    return InlineKeyboardMarkup(buttons)


def get_adaptive_keyboard(
    vin: str,
    data: Dict[str, Any],
    current_level: InformationLevel = InformationLevel.STANDARD,
    user_context: Optional[Dict] = None
) -> InlineKeyboardMarkup:
    """
    Create adaptive keyboard that automatically optimizes for context
    
    Args:
        vin: Vehicle VIN
        data: Vehicle data for determining available features
        current_level: Current information disclosure level
        user_context: User context for optimization
        
    Returns:
        Contextually optimized keyboard
    """
    # Determine available levels
    available_levels = get_available_disclosure_levels(data)
    
    # Check for premium data
    has_history = "history" in data and data["history"]
    has_marketvalue = "marketvalue" in data and data["marketvalue"]
    
    # Determine optimal layout based on context
    if user_context:
        is_mobile = user_context.get("is_mobile", False)
        is_frequent_user = user_context.get("frequent_user", False)
        
        if is_mobile:
            return get_mobile_optimized_keyboard(vin, has_history, has_marketvalue)
        elif is_frequent_user:
            return get_desktop_optimized_keyboard(vin, current_level, available_levels, has_history, has_marketvalue)
    
    # Default to smart keyboard
    return get_smart_details_keyboard(
        vin, 
        current_level, 
        available_levels, 
        has_history, 
        has_marketvalue, 
        user_context
    )


def get_onboarding_keyboard(vin: str) -> InlineKeyboardMarkup:
    """
    Create keyboard for new users with helpful guidance
    
    Args:
        vin: Vehicle VIN
        
    Returns:
        Onboarding-focused keyboard
    """
    buttons = []
    
    # Main action with helpful text
    buttons.append([InlineKeyboardButton("📊 Show More Information", callback_data=f"show_level:{InformationLevel.DETAILED.value}:{vin}")])
    
    # Explanation buttons
    buttons.append([
        InlineKeyboardButton("❓ What can I do?", callback_data="help_actions"),
        InlineKeyboardButton("⚙️ Settings", callback_data="show_settings")
    ])
    
    # Basic actions
    buttons.append([
        InlineKeyboardButton("💾 Save This Vehicle", callback_data=f"save_vin:{vin}"),
        InlineKeyboardButton("🔍 Try Another VIN", callback_data="new_vin")
    ])
    
    return InlineKeyboardMarkup(buttons)


def create_level_transition_message(
    from_level: InformationLevel, 
    to_level: InformationLevel
) -> str:
    """
    Create transition message when switching between information levels
    
    Args:
        from_level: Previous information level
        to_level: New information level
        
    Returns:
        Transition message for user feedback
    """
    level_names = {
        InformationLevel.ESSENTIAL: "Quick Facts",
        InformationLevel.STANDARD: "Standard Info",
        InformationLevel.DETAILED: "Detailed View", 
        InformationLevel.COMPLETE: "Complete Data"
    }
    
    from_name = level_names.get(from_level, "Info")
    to_name = level_names.get(to_level, "Info")
    
    if to_level.value > from_level.value:
        return f"🔍 **Expanding to {to_name}**\n_Showing more detailed information..._"
    else:
        return f"📋 **Switching to {to_name}**\n_Showing simplified view..._"
