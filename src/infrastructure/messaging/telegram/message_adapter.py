"""Message adapter for converting domain data to Telegram messages."""

from typing import Dict, Any, Tuple
from telegram import InlineKeyboardMarkup


class MessageAdapter:
    """Adapter for converting domain data to Telegram messages."""
    
    def format_vehicle_response(
        self,
        vehicle_data: Dict[str, Any],
        level: str = "standard"
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """Format vehicle data for Telegram response.
        
        Args:
            vehicle_data: The vehicle data to format
            level: The information level to display
            
        Returns:
            Tuple of (formatted_text, keyboard_markup)
        """
        # This would be implemented based on the actual formatting logic
        # For now, we'll create a placeholder implementation
        
        # Extract basic info
        attrs = vehicle_data.get("attributes", {})
        vin = attrs.get("vin", "Unknown")
        year = attrs.get("year", "")
        make = attrs.get("make", "")
        model = attrs.get("model", "")
        
        # Create vehicle description
        vehicle_desc = " ".join(str(v) for v in [year, make, model] if v)
        
        # Create formatted text
        text = f"🚗 *{vehicle_desc}*\n\n"
        text += f"`{vin}`\n\n"
        
        # Add some basic information
        if attrs.get("body_type"):
            text += f"Body Type: {attrs['body_type']}\n"
        if attrs.get("fuel_type"):
            text += f"Fuel Type: {attrs['fuel_type']}\n"
        if attrs.get("transmission"):
            text += f"Transmission: {attrs['transmission']}\n"
        
        # Create a simple keyboard (placeholder)
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh:{vin}")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ])
        
        return text, keyboard
    
    def format_error_response(self, error_message: str) -> str:
        """Format an error message for Telegram response.
        
        Args:
            error_message: The error message to format
            
        Returns:
            Formatted error message
        """
        return f"❌ *Error*\n\n{error_message}"