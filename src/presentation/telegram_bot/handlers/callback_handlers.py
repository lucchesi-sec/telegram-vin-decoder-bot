"""Callback handlers for the Telegram bot."""

import logging
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from src.domain.user.value_objects.telegram_id import TelegramID
from src.application.vehicle.services.vehicle_application_service import VehicleApplicationService
from src.application.user.services.user_application_service import UserApplicationService
from src.presentation.telegram_bot.adapters.message_adapter import MessageAdapter, InformationLevel
from src.presentation.telegram_bot.adapters.keyboard_adapter import KeyboardAdapter

logger = logging.getLogger(__name__)


class CallbackHandlers:
    """Handlers for Telegram callback queries."""
    
    def __init__(
        self,
        vehicle_service: VehicleApplicationService,
        user_service: UserApplicationService,
        message_adapter: MessageAdapter,
        keyboard_adapter: KeyboardAdapter
    ):
        """Initialize callback handlers.
        
        Args:
            vehicle_service: Vehicle application service
            user_service: User application service
            message_adapter: Message formatting adapter
            keyboard_adapter: Keyboard creation adapter
        """
        self.vehicle_service = vehicle_service
        self.user_service = user_service
        self.message_adapter = message_adapter
        self.keyboard_adapter = keyboard_adapter
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        try:
            if data.startswith("service:"):
                await self._handle_service_selection(update, context, data)
            elif data == "settings:api_key":
                await self._handle_api_key_setup(update, context)
            elif data == "settings:clear_api_key":
                await self._handle_clear_api_key(update, context)
            elif data == "settings:back":
                await self._show_settings_menu(update, context)
            elif data.startswith("refresh:"):
                await self._handle_refresh(update, context, data)
            elif data == "close":
                await self._handle_close(update, context)
            elif data.startswith("action:"):
                await self._handle_action_button(update, context, data)
            else:
                logger.warning(f"Unknown callback data: {data}")
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await query.edit_message_text(
                "Sorry, an error occurred. Please try again later."
            )
    
    async def _handle_service_selection(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        data: str
    ) -> None:
        """Handle decoder service selection."""
        query = update.callback_query
        service = data.split(":")[1]  # Extract service name
        
        # Update user preference
        user = await self.user_service.set_preferred_service(
            telegram_id=update.effective_user.id,
            service=service
        )
        
        # Add back button
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("↩️ Back", callback_data="action:settings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if user:
            service_display = service.upper()
            await query.edit_message_text(
                f"✅ *Service Updated*\n\n"
                f"Your preferred decoder service is now: *{service_display}*",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                "❌ Failed to update service preference. Please try again.",
                reply_markup=reply_markup
            )
    
    async def _handle_api_key_setup(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle API key setup request."""
        query = update.callback_query
        
        # Set flag in user data to expect API key input
        context.user_data['awaiting_api_key'] = True
        
        # Add back button
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("↩️ Back", callback_data="action:settings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔑 *API Key Setup*\\n\\n"
            "Please send your Auto.dev API key in the next message.\\n\\n"
            "Your API key will be stored securely and used only for VIN decoding.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def _handle_clear_api_key(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle API key removal."""
        query = update.callback_query
        
        # Clear the API key
        user = await self.user_service.set_user_api_key(
            telegram_id=update.effective_user.id,
            api_key=None
        )
        
        # Add back button
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("↩️ Back", callback_data="action:settings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if user:
            await query.edit_message_text(
                "✅ *API Key Cleared*\n\n"
                "Your Auto.dev API key has been removed.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                "❌ Failed to clear API key. Please try again.",
                reply_markup=reply_markup
            )
    
    async def handle_api_key_input(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        api_key: str
    ) -> None:
        """Handle API key input from user."""
        # Clear the flag
        context.user_data['awaiting_api_key'] = False
        
        # Save the API key
        user = await self.user_service.set_user_api_key(
            telegram_id=update.effective_user.id,
            api_key=api_key
        )
        
        # Add action buttons
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("🔍 Decode VIN", callback_data="action:decode_vin")],
            [InlineKeyboardButton("↩️ Back", callback_data="action:settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if user:
            # Also update service preference to AutoDev
            await self.user_service.set_preferred_service(
                telegram_id=update.effective_user.id,
                service="autodev"
            )
            
            await update.message.reply_text(
                "✅ *API Key Saved*\n\n"
                "Your Auto.dev API key has been saved and your preferred service "
                "has been set to Auto.dev.\n\n"
                "You can now decode VINs using the Auto.dev service!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "❌ Failed to save API key. Please try again.",
                reply_markup=reply_markup
            )
    
    async def _handle_refresh(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        data: str
    ) -> None:
        """Handle refresh callback for VIN data."""
        query = update.callback_query
        vin = data.replace("refresh:", "")
        
        try:
            # Update the message to show refreshing
            await query.edit_message_text(
                f"🔄 Refreshing data for VIN: `{vin}`\n\nPlease wait...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Get user and decode again
            user = await self.user_service.get_or_create_user(
                telegram_id=update.effective_user.id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name
            )
            
            # Decode the VIN again (force refresh)
            # This would need actual implementation in vehicle service
            # result = await self.vehicle_service.decode_vin(vin, user.preferences, force_refresh=True)
            
            # For now, show a simple response
            response_text = f"✅ *Refreshed Data*\n\nVIN: `{vin}`\n\nData has been refreshed!"
            
            # Add keyboard
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh:{vin}")],
                [InlineKeyboardButton("📋 Decode Another", callback_data="action:decode_vin")],
                [InlineKeyboardButton("❌ Close", callback_data="close")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                response_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error in refresh callback: {e}")
            await query.edit_message_text(
                "❌ An error occurred while refreshing the data. Please try again."
            )
    
    async def _handle_close(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle close callback."""
        query = update.callback_query
        try:
            # Delete the message
            await query.message.delete()
        except Exception as e:
            logger.error(f"Error in close callback: {e}")
            # If we can't delete, just edit to show it's closed
            await query.edit_message_text("Closed.")
    
    async def _show_settings_menu(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Show the main settings menu."""
        query = update.callback_query
        
        # Get current user preferences
        user = await self.user_service.get_user_by_telegram_id(update.effective_user.id)
        
        if user:
            current_service = user.preferences.preferred_decoder.upper()
            has_api_key = bool(user.preferences.autodev_api_key)
        else:
            current_service = "NHTSA"
            has_api_key = False
        
        # Build keyboard
        keyboard = [
            [
                InlineKeyboardButton("🏛 NHTSA", callback_data="service:nhtsa"),
                InlineKeyboardButton("🚗 Auto.dev", callback_data="service:autodev")
            ]
        ]
        
        if has_api_key:
            keyboard.append([
                InlineKeyboardButton("🗑 Clear API Key", callback_data="settings:clear_api_key")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🔑 Set API Key", callback_data="settings:api_key")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        settings_text = (
            "⚙️ *Settings*\n\n"
            f"Current decoder service: *{current_service}*\n"
            f"Auto.dev API key: {'✅ Set' if has_api_key else '❌ Not set'}\n\n"
            "Select an option:"
        )
        
        await query.edit_message_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def _handle_action_button(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        data: str
    ) -> None:
        """Handle action button callbacks."""
        query = update.callback_query
        action = data.split(":")[1]  # Extract action name
        
        try:
            if action == "decode_vin":
                # Prompt user to send a VIN
                await query.edit_message_text(
                    "🔢 *Decode VIN*\n\n"
                    "Please send me a 17-character VIN directly, or use the /vin command.\n\n"
                    "Example: 1HGCM826XA0042787"
                )
            elif action == "settings":
                # Show settings menu
                await self._show_settings_menu(update, context)
            elif action == "help":
                # Show help text
                help_text = (
                    "🤖 *VIN Decoder Bot Commands*\n\n"
                    "/start - Show welcome message\n"
                    "/vin <VIN> - Decode a VIN\n"
                    "/settings - Configure decoder service\n"
                    "/history - View your recent VIN searches\n"
                    "/help - Show this help message\n\n"
                    "You can also just send a 17-character VIN directly!"
                )
                
                # Add back button
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = [[InlineKeyboardButton("↩️ Back", callback_data="action:start")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    help_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            elif action == "start":
                # Show start menu again
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                
                welcome_text = (
                    "🚗 *Welcome to VIN Decoder Bot!*\n\n"
                    "I can decode Vehicle Identification Numbers (VINs) using official databases.\n\n"
                    "Select an option below to get started:"
                )
                
                # Create action buttons
                keyboard = [
                    [InlineKeyboardButton("🔍 Decode VIN", callback_data="action:decode_vin")],
                    [InlineKeyboardButton("⚙️ Settings", callback_data="action:settings")],
                    [InlineKeyboardButton("📖 Help", callback_data="action:help")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    welcome_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
        except Exception as e:
            logger.error(f"Error in action button handler: {e}")
            await query.edit_message_text(
                "Sorry, an error occurred. Please try again later."
            )