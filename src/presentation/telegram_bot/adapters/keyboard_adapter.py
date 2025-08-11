"""Keyboard adapter for creating inline keyboards."""

from typing import List, Optional, Dict, Any, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.presentation.telegram_bot.keyboards import create_main_menu_keyboard, create_settings_keyboard


class KeyboardAdapter:
    """Adapts domain objects to Telegram inline keyboards."""
    
    def get_vehicle_actions_keyboard(
        self,
        vin: str,
        has_refresh: bool = True,
        has_more_info: bool = False
    ) -> InlineKeyboardMarkup:
        """Create inline keyboard for vehicle actions.
        
        Args:
            vin: Vehicle VIN
            has_refresh: Whether to show refresh button
            has_more_info: Whether more information is available
            
        Returns:
            Inline keyboard markup
        """
        buttons = []
        
        # First row - information levels
        if has_more_info:
            buttons.append([
                InlineKeyboardButton("📋 Standard", callback_data=f"level:standard:{vin}"),
                InlineKeyboardButton("📊 Detailed", callback_data=f"level:detailed:{vin}"),
                InlineKeyboardButton("📚 Complete", callback_data=f"level:complete:{vin}")
            ])
        
        # Second row - actions
        action_row = []
        if has_refresh:
            action_row.append(InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh:{vin}"))
        action_row.append(InlineKeyboardButton("💾 Save", callback_data=f"save:{vin}"))
        action_row.append(InlineKeyboardButton("📤 Share", callback_data=f"share:{vin}"))
        
        if action_row:
            buttons.append(action_row)
        
        # Third row - close
        buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])
        
        return InlineKeyboardMarkup(buttons)
    
    def get_settings_keyboard(
        self,
        current_service: str,
        has_api_key: bool = False
    ) -> InlineKeyboardMarkup:
        """Create settings keyboard for service selection.
        
        Args:
            current_service: Currently selected decoder service
            has_api_key: Whether user has API key configured
            
        Returns:
            Inline keyboard markup
        """
        buttons = []
        
        # Service selection buttons
        nhtsa_check = "✅" if current_service == "nhtsa" else ""
        autodev_check = "✅" if current_service == "autodev" else ""
        
        buttons.append([
            InlineKeyboardButton(
                f"{nhtsa_check} 🏛 NHTSA",
                callback_data="service:nhtsa"
            ),
            InlineKeyboardButton(
                f"{autodev_check} 🚗 Auto.dev",
                callback_data="service:autodev"
            )
        ])
        
        # API key management
        if has_api_key:
            buttons.append([
                InlineKeyboardButton("🗑 Clear API Key", callback_data="settings:clear_api_key")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("🔑 Set API Key", callback_data="settings:api_key")
            ])
        
        # Service info and close
        buttons.append([
            InlineKeyboardButton("ℹ️ Service Info", callback_data="settings:service_info"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ])
        
        return InlineKeyboardMarkup(buttons)
    
    def get_history_keyboard(
        self,
        history_entries: List[Tuple[str, str, str]]
    ) -> InlineKeyboardMarkup:
        """Create keyboard for history entries.
        
        Args:
            history_entries: List of (vin, description, date) tuples
            
        Returns:
            Inline keyboard markup
        """
        buttons = []
        
        # Add buttons for each history entry (max 5)
        for vin, description, _ in history_entries[:5]:
            display_text = description[:30] if description else vin[:17]
            buttons.append([
                InlineKeyboardButton(
                    f"🕐 {display_text}",
                    callback_data=f"decode:{vin}"
                )
            ])
        
        # Add close button
        if buttons:
            buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])
        
        return InlineKeyboardMarkup(buttons)
    
    def get_saved_vehicles_keyboard(
        self,
        saved_vehicles: List[Tuple[str, str]]
    ) -> InlineKeyboardMarkup:
        """Create keyboard for saved vehicles.
        
        Args:
            saved_vehicles: List of (vin, description) tuples
            
        Returns:
            Inline keyboard markup
        """
        buttons = []
        
        # Add buttons for each saved vehicle (max 10)
        for vin, description in saved_vehicles[:10]:
            display_text = description[:25] if description else vin[:17]
            buttons.append([
                InlineKeyboardButton(
                    f"⭐ {display_text}",
                    callback_data=f"decode:{vin}"
                ),
                InlineKeyboardButton(
                    "🗑️",
                    callback_data=f"remove_saved:{vin}"
                )
            ])
        
        # Add close button
        if buttons:
            buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])
        
        return InlineKeyboardMarkup(buttons)
    
    def get_confirmation_keyboard(
        self,
        action: str,
        data: str
    ) -> InlineKeyboardMarkup:
        """Create yes/no confirmation keyboard.
        
        Args:
            action: Action to confirm
            data: Associated data
            
        Returns:
            Inline keyboard markup
        """
        buttons = [[
            InlineKeyboardButton("✅ Yes", callback_data=f"confirm:{action}:{data}"),
            InlineKeyboardButton("❌ No", callback_data="close")
        ]]
        
        return InlineKeyboardMarkup(buttons)
    
    def get_service_info_keyboard(self) -> InlineKeyboardMarkup:
        """Create keyboard for service information display.
        
        Returns:
            Inline keyboard markup
        """
        buttons = [
            [InlineKeyboardButton("🔙 Back to Settings", callback_data="settings:back")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        return InlineKeyboardMarkup(buttons)
    
    def get_api_key_prompt_keyboard(self) -> InlineKeyboardMarkup:
        """Create keyboard for API key input prompt.
        
        Returns:
            Inline keyboard markup
        """
        buttons = [
            [InlineKeyboardButton("❌ Cancel", callback_data="settings:back")]
        ]
        
        return InlineKeyboardMarkup(buttons)
    
    def get_sample_vin_keyboard(self) -> InlineKeyboardMarkup:
        """Create keyboard with sample VIN for testing.
        
        Returns:
            Inline keyboard markup
        """
        sample_vins = [
            ("1HGBH41JXMN109186", "Honda Civic"),
            ("WBA3B5C59EF981215", "BMW 3 Series"),
            ("5YJSA1E26HF174959", "Tesla Model S")
        ]
        
        buttons = []
        for vin, description in sample_vins:
            buttons.append([
                InlineKeyboardButton(
                    f"🚗 {description}",
                    callback_data=f"sample:{vin}"
                )
            ])
        
        buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])
        
        return InlineKeyboardMarkup(buttons)
    
    def get_close_button(self) -> InlineKeyboardMarkup:
        """Create a simple close button.
        
        Returns:
            Inline keyboard markup
        """
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]])
    
    def get_back_button(
        self,
        callback_data: str = "back"
    ) -> InlineKeyboardMarkup:
        """Create a simple back button.
        
        Args:
            callback_data: Callback data for the back action
            
        Returns:
            Inline keyboard markup
        """
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Back", callback_data=callback_data)
        ]])
    
    def get_quick_actions_keyboard(self) -> InlineKeyboardMarkup:
        """Create keyboard for quick actions.
        
        Returns:
            Inline keyboard markup
        """
        buttons = [
            [
                InlineKeyboardButton("🔍 New VIN", callback_data="action:new_vin"),
                InlineKeyboardButton("🕐 Recent", callback_data="action:recent")
            ],
            [
                InlineKeyboardButton("⭐ Saved", callback_data="action:saved"),
                InlineKeyboardButton("⚙️ Settings", callback_data="action:settings")
            ],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        return InlineKeyboardMarkup(buttons)
    
    def get_information_level_keyboard(
        self,
        vin: str,
        current_level: str = "standard"
    ) -> InlineKeyboardMarkup:
        """Create keyboard for selecting information display level.
        
        Args:
            vin: Vehicle VIN
            current_level: Current display level
            
        Returns:
            Inline keyboard markup
        """
        buttons = []
        
        # Level selection buttons
        levels = [
            ("essential", "🔹 Essential"),
            ("standard", "📋 Standard"),
            ("detailed", "📊 Detailed"),
            ("complete", "📚 Complete")
        ]
        
        level_buttons = []
        for level_id, label in levels:
            check = "✅" if level_id == current_level else ""
            level_buttons.append(
                InlineKeyboardButton(
                    f"{check} {label}",
                    callback_data=f"level:{level_id}:{vin}"
                )
            )
        
        # Add buttons in rows of 2
        for i in range(0, len(level_buttons), 2):
            buttons.append(level_buttons[i:i+2])
        
        # Add close button
        buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])
        
        return InlineKeyboardMarkup(buttons)