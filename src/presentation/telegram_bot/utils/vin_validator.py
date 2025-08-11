"""VIN validation utility for automatic VIN detection."""

import re
import logging

logger = logging.getLogger(__name__)


class VINValidator:
    """Validates and extracts VINs from text messages."""

    # VIN pattern: 17 alphanumeric characters, excluding I, O, Q
    VIN_PATTERN = re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b", re.IGNORECASE)

    # Characters not allowed in VINs
    INVALID_CHARS = {"I", "O", "Q", "i", "o", "q"}

    @classmethod
    def extract_vin(cls, text: str) -> str | None:
        """Extract a VIN from text if present.

        Args:
            text: Input text to search for VIN

        Returns:
            The extracted VIN in uppercase if found and valid, None otherwise
        """
        if not text:
            return None

        # Clean the text (remove extra whitespace)
        text = " ".join(text.split())

        # First check if the entire text is a potential VIN
        cleaned_text = text.strip().upper()
        if cls.is_valid_vin(cleaned_text):
            return cleaned_text

        # Search for VIN patterns in the text
        matches = cls.VIN_PATTERN.findall(text)

        for match in matches:
            vin = match.upper()
            if cls.is_valid_vin(vin):
                logger.info(f"Found valid VIN in text: {vin}")
                return vin

        return None

    @classmethod
    def is_valid_vin(cls, vin: str) -> bool:
        """Check if a string is a valid VIN.

        Args:
            vin: String to validate

        Returns:
            True if valid VIN format, False otherwise
        """
        if not vin or len(vin) != 17:
            return False

        # Check for invalid characters
        if any(char in cls.INVALID_CHARS for char in vin):
            return False

        # Basic VIN format validation
        # VINs should be alphanumeric only
        if not vin.isalnum():
            return False

        # Additional VIN rules:
        # - Position 9 is often a check digit (0-9 or X)
        # - Positions 10-17 are usually the sequential production number
        # But we'll keep it simple for now and just validate format

        return True

    @classmethod
    def looks_like_vin_attempt(cls, text: str) -> bool:
        """Check if text looks like a VIN input attempt.

        This is more lenient than is_valid_vin and helps provide better
        user feedback when they're trying to enter a VIN but make mistakes.

        Args:
            text: Input text to check

        Returns:
            True if text appears to be a VIN attempt
        """
        if not text:
            return False

        cleaned = text.strip()

        # Check length is close to VIN length (15-19 chars)
        if 15 <= len(cleaned) <= 19:
            # Check if mostly alphanumeric
            alnum_count = sum(1 for c in cleaned if c.isalnum())
            if alnum_count >= len(cleaned) * 0.8:  # 80% alphanumeric
                return True

        return False
