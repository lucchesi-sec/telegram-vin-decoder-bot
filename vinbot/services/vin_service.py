"""VIN decoding service for handling all VIN-related business logic."""

import logging
from typing import Optional, Dict, Any, Tuple
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import Service
from ..vin import is_valid_vin, normalize_vin
from ..nhtsa_client import NHTSAError
from ..user_data import UserDataManager


class VINDecodingService(Service):
    """Service for handling VIN decoding operations."""
    
    async def decode_vin(
        self,
        vin: str,
        user_id: Optional[int],
        context: ContextTypes.DEFAULT_TYPE,
        requested_level: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """Decode a VIN and return the data with appropriate formatting.
        
        Args:
            vin: The VIN to decode
            user_id: The user ID for tracking
            context: The bot context
            requested_level: Optional information level requested
            
        Returns:
            Tuple of (vehicle_data, error_message)
        """
        # Normalize and validate VIN
        vin = normalize_vin(vin)
        
        if not is_valid_vin(vin):
            error_msg = (
                "❌ **Invalid VIN Format**\n\n"
                "VIN must be:\n"
                "• Exactly 17 characters\n"
                "• Letters and numbers only\n"
                "• No I, O, or Q letters\n\n"
                f"_You entered: {len(vin)} characters_"
            )
            return None, error_msg
        
        # Get decoder service
        decoder_service = self.get_dependency('decoder_service')
        client = await decoder_service.get_user_decoder(context, user_id)
        
        if not client:
            return None, "Bot is not initialized correctly. Try again later."
        
        # Check cache first
        user_data_mgr = self.get_dependency('user_data_manager')
        from_cache = False
        data = None
        
        if user_data_mgr:
            data = await user_data_mgr.get_vehicle_data(vin)
            if data:
                from_cache = True
                self._logger.info(f"Using cached vehicle data for VIN {vin}")
        
        # If not in cache, fetch from API
        if not data:
            try:
                data = await client.decode_vin(vin)
            except NHTSAError as e:
                service_name = client.service_name if hasattr(client, 'service_name') else "VIN decoder"
                self._logger.error(f"{service_name} error for VIN {vin}: {e}")
                return None, f"❌ Error decoding VIN: {e}"
            except Exception as e:
                self._logger.exception(f"Unexpected error decoding VIN {vin}")
                return None, f"❌ Unexpected error: {str(e)}"
        
        # Add metadata
        if from_cache:
            data["from_cache"] = True
        
        # Store in context for later use
        context.user_data[f"vehicle_data_{vin}"] = data
        
        # Add to user history
        if user_data_mgr and user_id:
            await user_data_mgr.add_to_history(user_id, vin, data)
        
        return data, None
    
    async def determine_display_level(
        self,
        data: Dict[str, Any],
        user_id: Optional[int],
        context: ContextTypes.DEFAULT_TYPE,
        requested_level: Optional[str] = None
    ) -> Any:
        """Determine the appropriate information level for display.
        
        Args:
            data: The vehicle data
            user_id: The user ID
            context: The bot context
            requested_level: Optional requested level
            
        Returns:
            The appropriate InformationLevel
        """
        from ..smart_formatter import InformationLevel, suggest_information_level
        
        if requested_level:
            try:
                return InformationLevel(int(requested_level))
            except (ValueError, TypeError):
                return InformationLevel.STANDARD
        
        # Get user context manager
        user_context_mgr = context.bot_data.get("user_context_manager")
        
        if user_context_mgr and user_id:
            data_richness = await user_context_mgr.calculate_data_richness(data)
            return await user_context_mgr.suggest_optimal_level(user_id, data_richness)
        else:
            return suggest_information_level(data)
    
    async def format_vehicle_response(
        self,
        data: Dict[str, Any],
        user_id: Optional[int],
        context: ContextTypes.DEFAULT_TYPE,
        display_level: Any
    ) -> Tuple[str, Any]:
        """Format the vehicle data for display.
        
        Args:
            data: The vehicle data
            user_id: The user ID
            context: The bot context
            display_level: The information level to use
            
        Returns:
            Tuple of (formatted_text, keyboard)
        """
        from ..smart_formatter import format_vehicle_smart_card, DisplayMode
        from ..smart_keyboards import get_adaptive_keyboard
        
        # Get user context manager
        user_context_mgr = context.bot_data.get("user_context_manager")
        
        # Detect mobile user
        is_mobile = False
        if user_context_mgr and user_id:
            is_mobile = await user_context_mgr.detect_mobile_user(user_id, context)
        
        # Get user context for adaptive keyboard
        user_context = None
        if user_context_mgr and user_id:
            user_context = await user_context_mgr.get_user_context(user_id)
        
        # Format the response with smart progressive disclosure
        display_mode = DisplayMode.MOBILE if is_mobile else DisplayMode.DESKTOP
        text = format_vehicle_smart_card(data, display_level, display_mode)
        
        # Get the VIN
        vin = data.get("attributes", {}).get("vin") or data.get("vin", "")
        
        # Create adaptive keyboard
        keyboard = get_adaptive_keyboard(
            vin=vin,
            level=display_level,
            data_richness=data.get("data_richness", "standard"),
            user_context=user_context,
            has_history=bool(data.get("history")),
            has_market_value=bool(data.get("marketvalue")),
            from_cache=data.get("from_cache", False)
        )
        
        # Store current level for tracking
        context.user_data[f"current_level_{vin}"] = display_level.value
        
        # Track VIN decode for user learning
        if user_context_mgr and user_id:
            await user_context_mgr.track_vin_decode(user_id, display_level)
        
        return text, keyboard