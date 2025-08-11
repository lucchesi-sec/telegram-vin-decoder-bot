"""Decoder factory for selecting appropriate decoder based on user preferences."""

import logging
from typing import Any
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.infrastructure.external_services.nhtsa.nhtsa_adapter import NHTSAAdapter
from src.infrastructure.external_services.autodev.autodev_adapter import AutoDevAdapter
from src.infrastructure.external_services.autodev.autodev_client import AutoDevClient

logger = logging.getLogger(__name__)


class DecoderFactory:
    """Factory for creating appropriate decoder based on user preferences."""
    
    def __init__(
        self,
        nhtsa_adapter: NHTSAAdapter,
        autodev_adapter: AutoDevAdapter,
        default_service: str = "nhtsa"
    ):
        self.nhtsa_adapter = nhtsa_adapter
        self.autodev_adapter = autodev_adapter
        self.default_service = default_service
    
    def get_decoder(self, user_preferences: UserPreferences) -> Any:
        """Get the appropriate decoder based on user preferences.
        
        Args:
            user_preferences: User's service preferences
            
        Returns:
            Appropriate decoder adapter
        """
        logger.info(f"Selecting decoder - Preferred: {user_preferences.preferred_decoder}, Has user API key: {bool(user_preferences.autodev_api_key)}")
        
        # Check if user prefers AutoDev
        if user_preferences.preferred_decoder == "autodev":
            # If user has their own API key, use it
            if user_preferences.autodev_api_key:
                logger.info("Using AutoDev decoder with user's API key")
                client = AutoDevClient(api_key=user_preferences.autodev_api_key, timeout=15)
                return AutoDevAdapter(client=client)
            # Otherwise use the environment-configured AutoDev adapter
            elif self.autodev_adapter.client.api_key:
                logger.info("Using AutoDev decoder with environment API key")
                return self.autodev_adapter
            else:
                logger.warning("AutoDev selected but no API key available, falling back to NHTSA")
                return self.nhtsa_adapter
        
        # Default to NHTSA
        logger.info("Using NHTSA decoder (default/user preference)")
        return self.nhtsa_adapter