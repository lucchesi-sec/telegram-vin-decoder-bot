"""Configuration validation utilities."""

import os
import logging
from typing import List, Tuple, Optional
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def validate_environment() -> Tuple[bool, List[str]]:
    """Validate required environment variables.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required environment variables
    required_vars = [
        "TELEGRAM_BOT_TOKEN"
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Missing required environment variable: {var}")
    
    # Check for common configuration issues
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if bot_token and (len(bot_token) < 40 or not bot_token.startswith(("bot", "BOT"))):
        errors.append("TELEGRAM_BOT_TOKEN appears to be invalid (should start with 'bot' and be ~45 characters)")
    
    return len(errors) == 0, errors


def validate_settings_creation() -> Tuple[bool, Optional[str]]:
    """Test if settings can be created without errors.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        from src.config.settings import Settings
        settings = Settings()
        logger.info("Settings validation successful")
        return True, None
    except ValidationError as e:
        error_msg = f"Settings validation failed: {e}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error during settings validation: {e}"
        logger.error(error_msg)
        return False, error_msg


def check_startup_requirements() -> bool:
    """Check all startup requirements.
    
    Returns:
        True if all requirements are met, False otherwise
    """
    logger.info("Checking startup requirements...")
    
    # Check environment variables
    env_valid, env_errors = validate_environment()
    if not env_valid:
        logger.error("Environment validation failed:")
        for error in env_errors:
            logger.error(f"  - {error}")
        return False
    
    # Check settings creation
    settings_valid, settings_error = validate_settings_creation()
    if not settings_valid:
        logger.error(f"Settings validation failed: {settings_error}")
        return False
    
    logger.info("All startup requirements met!")
    return True


def print_environment_info():
    """Print environment information for debugging."""
    logger.info("Environment Information:")
    logger.info(f"  TELEGRAM_BOT_TOKEN: {'Set' if os.getenv('TELEGRAM_BOT_TOKEN') else 'NOT SET'}")
    logger.info(f"  AUTODEV_API_KEY: {'Set' if os.getenv('AUTODEV_API_KEY') else 'Not set'}")
    logger.info(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"  LOG_LEVEL: {os.getenv('LOG_LEVEL', 'INFO')}")
    logger.info(f"  DEBUG: {os.getenv('DEBUG', 'false')}")
