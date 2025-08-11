"""Decoder factory for selecting appropriate decoder based on user preferences."""

import logging
from typing import Any
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.infrastructure.external_services.nhtsa.nhtsa_adapter import NHTSAAdapter
from src.infrastructure.external_services.autodev.autodev_adapter import AutoDevAdapter

logger = logging.getLogger(__name__)


class DecoderFactory:
    """Factory for creating appropriate decoder based on user preferences."""

    def __init__(
        self,
        nhtsa_adapter: NHTSAAdapter,
        autodev_adapter: AutoDevAdapter,
        default_service: str = "nhtsa",
    ):
        self.nhtsa_adapter = nhtsa_adapter
        self.autodev_adapter = autodev_adapter
        self.default_service = default_service

    def get_decoder(self, user_preferences: UserPreferences) -> Any:
        """Get the appropriate decoder based on user preferences.

        Uses auto.dev as the primary decoder, falling back to NHTSA if auto.dev fails.

        Args:
            user_preferences: User's service preferences

        Returns:
            Appropriate decoder adapter
        """
        logger.info("Selecting decoder - Using auto.dev as default")

        # Try auto.dev first if it's configured
        if self.autodev_adapter.client.api_key:
            logger.info("Using auto.dev decoder (primary service)")
            return self.autodev_adapter
        else:
            logger.info("auto.dev not configured, using NHTSA decoder")
            return self.nhtsa_adapter
