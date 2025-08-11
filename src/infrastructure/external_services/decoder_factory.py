"""Decoder factory for selecting appropriate decoder based on user preferences."""

from typing import Any
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.infrastructure.external_services.nhtsa.nhtsa_adapter import NHTSAAdapter
from src.infrastructure.external_services.autodev.autodev_adapter import AutoDevAdapter


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
        # If user has AutoDev API key and prefers AutoDev, use it
        if (user_preferences.preferred_decoder == "autodev" and 
            user_preferences.autodev_api_key):
            return self.autodev_adapter
        
        # Otherwise, use NHTSA (free service)
        return self.nhtsa_adapter