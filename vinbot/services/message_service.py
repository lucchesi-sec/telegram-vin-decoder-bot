"""Message handling service for processing incoming messages."""

import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import Service
from ..vin import is_valid_vin, normalize_vin


class MessageHandlingService(Service):
    """Service for handling incoming messages."""
    
    async def process_text_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Process an incoming text message.
        
        Args:
            update: The update containing the message
            context: The bot context
        """
        if not update.message or not update.message.text:
            return
        
        text = update.message.text.strip()
        user_id = update.effective_user.id if update.effective_user else None
        
        # Check if we're waiting for an API key
        if await self._handle_api_key_input(update, context, text, user_id):
            return
        
        # Check if it's a VIN
        if len(text) == 17 and is_valid_vin(text):
            await self._handle_vin_input(update, context, text)
        else:
            await update.message.reply_text(
                "I expected a 17-character VIN. Use /vin <VIN> or send the VIN directly."
            )
    
    async def _handle_api_key_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        user_id: Optional[int]
    ) -> bool:
        """Handle API key input if waiting for one.
        
        Args:
            update: The update
            context: The bot context
            text: The message text
            user_id: The user ID
            
        Returns:
            True if an API key was processed
        """
        if not context.user_data.get("awaiting_api_key_for"):
            return False
        
        service = context.user_data["awaiting_api_key_for"]
        is_update = context.user_data.get("api_key_update", False)
        
        # Clear the state
        del context.user_data["awaiting_api_key_for"]
        if "api_key_update" in context.user_data:
            del context.user_data["api_key_update"]
        
        # Get user service
        user_service = self.get_dependency('user_service')
        if not user_service or not user_id:
            await update.message.reply_text("Unable to save API key.")
            return True
        
        # Validate the API key
        is_valid = await user_service.validate_api_key(service, text)
        
        if is_valid:
            # Save the API key
            await user_service.save_api_key(user_id, service, text)
            
            # Update service if needed
            if not is_update:
                settings = await user_service.get_user_settings(user_id)
                current_service = settings.get("service", "NHTSA")
                if current_service != service:
                    await user_service.update_user_service(user_id, service)
            
            service_name = "Auto.dev" if service == "AutoDev" else service
            await update.message.reply_text(
                f"✅ API key for {service_name} has been saved successfully!\n\n"
                f"You are now using {service_name} for VIN decoding.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Show updated settings
            await self._show_settings_menu(update, context)
        else:
            service_name = "Auto.dev" if service == "AutoDev" else service
            await update.message.reply_text(
                f"❌ Invalid {service_name} API key format.\n\n"
                "Please check your key and try again, or contact support if you believe this is an error.",
                parse_mode=ParseMode.MARKDOWN
            )
            # Show settings again
            await self._show_settings_menu(update, context)
        
        return True
    
    async def _handle_vin_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str
    ) -> None:
        """Handle VIN input.
        
        Args:
            update: The update
            context: The bot context
            text: The VIN text
        """
        # Import here to avoid circular dependency
        from ..bot import handle_vin_decode
        await handle_vin_decode(update, context, normalize_vin(text))
    
    async def _show_settings_menu(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Show the settings menu.
        
        Args:
            update: The update
            context: The bot context
        """
        # Import here to avoid circular dependency
        from ..bot import show_settings_menu
        await show_settings_menu(update, context)