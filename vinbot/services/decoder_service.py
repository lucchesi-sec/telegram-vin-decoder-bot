"""Decoder selection service for choosing the appropriate VIN decoder."""

import logging
from typing import Optional
from telegram.ext import ContextTypes

from .base import Service
from ..vin_decoder_base import VINDecoderBase
from ..nhtsa_client import NHTSAClient
from ..autodev_client import AutoDevClient
from ..user_data import UserDataManager


class DecoderSelectionService(Service):
    """Service for selecting the appropriate VIN decoder based on user preferences."""
    
    async def get_user_decoder(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: Optional[int] = None
    ) -> Optional[VINDecoderBase]:
        """Get the appropriate decoder for the user based on their settings.
        
        Args:
            context: The bot context
            user_id: The user ID
            
        Returns:
            The appropriate VIN decoder or None if not available
        """
        # Get user data manager
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        
        # Get user settings
        user_settings = {}
        if user_data_mgr and user_id:
            user_settings = await user_data_mgr.get_user_settings(user_id)
        
        # Determine which service to use
        service = user_settings.get("service", "NHTSA")
        
        # Check for default Auto.dev API key from environment
        settings = context.bot_data.get("settings")
        default_autodev_key = ""
        if settings and hasattr(settings, 'autodev_api_key'):
            default_autodev_key = settings.autodev_api_key
        
        # If default Auto.dev key exists and user hasn't explicitly chosen NHTSA
        if default_autodev_key and service != "NHTSA":
            service = "AutoDev"
        
        # Get cache reference
        cache = context.bot_data.get("cache")
        
        # For Auto.dev service
        if service == "AutoDev":
            # Check for API key (user's or default)
            api_key = user_settings.get("autodev_api_key") or default_autodev_key
            
            if api_key:
                # Create client key for caching
                client_key = f"autodev_client_{user_id}" if user_settings.get("autodev_api_key") else "autodev_client_default"
                
                # Store in appropriate context based on whether it's user-specific or default
                if user_settings.get("autodev_api_key"):
                    # User-specific key, store in user_data
                    if client_key not in context.user_data:
                        context.user_data[client_key] = AutoDevClient(
                            api_key=api_key, cache=cache
                        )
                    return context.user_data[client_key]
                else:
                    # Default key, store in bot_data for sharing
                    if client_key not in context.bot_data:
                        context.bot_data[client_key] = AutoDevClient(
                            api_key=api_key, cache=cache
                        )
                    return context.bot_data[client_key]
            else:
                # Fall back to NHTSA if no API key is available
                service = "NHTSA"
        
        # For NHTSA or fallback, use the shared NHTSA client
        if "nhtsa_client" not in context.bot_data:
            context.bot_data["nhtsa_client"] = NHTSAClient(cache=cache)
        
        return context.bot_data["nhtsa_client"]
    
    async def get_service_info(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: Optional[int] = None
    ) -> tuple[str, bool]:
        """Get information about the current service being used.
        
        Args:
            context: The bot context
            user_id: The user ID
            
        Returns:
            Tuple of (service_name, is_using_default_key)
        """
        # Get user data manager
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        
        # Get user settings
        user_settings = {}
        if user_data_mgr and user_id:
            user_settings = await user_data_mgr.get_user_settings(user_id)
        
        # Check for default Auto.dev API key
        settings = context.bot_data.get("settings")
        default_autodev_key = ""
        if settings and hasattr(settings, 'autodev_api_key'):
            default_autodev_key = settings.autodev_api_key
        
        # Determine service
        service = user_settings.get("service", "NHTSA")
        has_user_key = bool(user_settings.get("autodev_api_key"))
        
        # If default key exists and user hasn't explicitly chosen NHTSA
        if default_autodev_key and service != "NHTSA":
            return "AutoDev", not has_user_key
        
        return service, False