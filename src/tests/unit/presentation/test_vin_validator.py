"""Unit tests for VIN validator."""

import pytest

from src.presentation.telegram_bot.utils.vin_validator import VINValidator


class TestVINValidator:
    """Test VIN validation and extraction functionality."""

    def test_valid_vin_extraction(self):
        """Test extraction of valid VINs from text."""
        # Test cases with valid VINs
        test_cases = [
            ("1HGBH41JXMN109186", "1HGBH41JXMN109186"),  # Just VIN
            (
                "Check this VIN: 1HGBH41JXMN109186",
                "1HGBH41JXMN109186",
            ),  # VIN in sentence
            (
                "VIN 1HGBH41JXMN109186 please decode",
                "1HGBH41JXMN109186",
            ),  # VIN in middle
            ("1hgbh41jxmn109186", "1HGBH41JXMN109186"),  # Lowercase VIN
            ("  1HGBH41JXMN109186  ", "1HGBH41JXMN109186"),  # VIN with spaces
        ]

        for text, expected in test_cases:
            result = VINValidator.extract_vin(text)
            assert result == expected, f"Failed for input: {text}"

    def test_invalid_vin_rejection(self):
        """Test rejection of invalid VINs."""
        invalid_vins = [
            "IOQIOQIOQIOQIOQIO",  # Contains invalid characters (I, O, Q)
            "1234567890123456",  # Too short (16 chars)
            "12345678901234567890",  # Too long (20 chars)
            "1HGBH41JXM-109186",  # Contains special character
            "1HGBH41JXM 109186",  # Contains space in middle
            "",  # Empty string
            "ABC",  # Way too short
        ]

        for text in invalid_vins:
            result = VINValidator.extract_vin(text)
            assert result is None, f"Should reject invalid VIN: {text}"

    def test_is_valid_vin(self):
        """Test direct VIN validation."""
        assert VINValidator.is_valid_vin("1HGBH41JXMN109186") is True
        assert VINValidator.is_valid_vin("WBANE53597CM51659") is True
        assert VINValidator.is_valid_vin("JH4KA7650PC008359") is True

        # Invalid VINs
        assert VINValidator.is_valid_vin("IOQIOQIOQIOQIOQIO") is False
        assert VINValidator.is_valid_vin("1234567890123456") is False  # 16 chars
        assert VINValidator.is_valid_vin("12345678901234567890") is False  # 20 chars
        assert VINValidator.is_valid_vin("") is False
        assert VINValidator.is_valid_vin(None) is False

    def test_looks_like_vin_attempt(self):
        """Test detection of VIN input attempts."""
        # Should detect as VIN attempts
        assert (
            VINValidator.looks_like_vin_attempt("1HGBH41JXMN10918") is True
        )  # 16 chars
        assert (
            VINValidator.looks_like_vin_attempt("1HGBH41JXMN1091867") is True
        )  # 18 chars
        assert (
            VINValidator.looks_like_vin_attempt("1HGBH41JXM-109186") is True
        )  # Has dash

        # Should not detect as VIN attempts
        assert VINValidator.looks_like_vin_attempt("hello world") is False
        assert VINValidator.looks_like_vin_attempt("123") is False
        assert VINValidator.looks_like_vin_attempt("") is False

    def test_extract_vin_from_complex_text(self):
        """Test VIN extraction from complex messages."""
        test_cases = [
            ("Can you decode 1HGBH41JXMN109186 for me? Thanks!", "1HGBH41JXMN109186"),
            (
                "I have two VINs: 1HGBH41JXMN109186 and another one",
                "1HGBH41JXMN109186",  # Should extract first valid VIN
            ),
            (
                "VIN#1HGBH41JXMN109186",
                "1HGBH41JXMN109186",  # Should handle VIN with prefix
            ),
            (
                "My car's VIN:\n1HGBH41JXMN109186\nPlease decode",
                "1HGBH41JXMN109186",  # Should handle multiline
            ),
        ]

        for text, expected in test_cases:
            result = VINValidator.extract_vin(text)
            assert result == expected, f"Failed for input: {text}"
