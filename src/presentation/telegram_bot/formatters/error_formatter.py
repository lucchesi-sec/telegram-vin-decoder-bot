"""Error formatters for Telegram messages."""


class ErrorFormatter:
    """Formatter for error messages in Telegram."""
    
    @staticmethod
    def format_validation_error(error_message: str) -> str:
        """Format validation error message."""
        return format_validation_error(error_message)
    
    @staticmethod
    def format_decode_error(error_message: str) -> str:
        """Format decode error message."""
        return format_decode_error(error_message)
    
    @staticmethod
    def format_service_error(service_name: str, error_message: str) -> str:
        """Format service error message."""
        return format_service_error(service_name, error_message)


def format_validation_error(error_message: str) -> str:
    """Format validation error message.
    
    Args:
        error_message: Validation error message
        
    Returns:
        Formatted error message
    """
    return (
        f"❌ *Invalid VIN Format*\n\n"
        f"{error_message}\n\n"
        "VIN must be:\n"
        "• Exactly 17 characters\n"
        "• Letters and numbers only\n"
        "• No I, O, or Q letters"
    )


def format_decode_error(error_message: str) -> str:
    """Format decode error message.
    
    Args:
        error_message: Decode error message
        
    Returns:
        Formatted error message
    """
    return f"❌ *Decode Error*\n\n{error_message}"


def format_service_error(service_name: str, error_message: str) -> str:
    """Format service error message.
    
    Args:
        service_name: Name of the service
        error_message: Service error message
        
    Returns:
        Formatted error message
    """
    return f"❌ *{service_name} Error*\n\n{error_message}"