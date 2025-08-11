"""Command handlers for the Telegram bot."""

import logging
from typing import Optional, Dict, Any
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from src.domain.user.value_objects.telegram_id import TelegramID
from src.domain.user.value_objects.user_preferences import UserPreferences
from src.application.vehicle.services.vehicle_application_service import VehicleApplicationService
from src.application.user.services.user_application_service import UserApplicationService
from src.presentation.telegram_bot.adapters.message_adapter import MessageAdapter
from src.presentation.telegram_bot.adapters.keyboard_adapter import KeyboardAdapter

logger = logging.getLogger(__name__)


class CommandHandlers:
    """Handlers for Telegram commands."""
    
    def __init__(
        self,
        vehicle_service: VehicleApplicationService,
        user_service: UserApplicationService,
        message_adapter: MessageAdapter,
        keyboard_adapter: KeyboardAdapter
    ):
        self.vehicle_service = vehicle_service
        self.user_service = user_service
        self.message_adapter = message_adapter
        self.keyboard_adapter = keyboard_adapter
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        try:
            welcome_text = (
                "🚗 *Welcome to VIN Decoder Bot!*\n\n"
                "I can decode Vehicle Identification Numbers (VINs) using official databases.\n\n"
                "*How to use:*\n"
                "• Send me a 17-character VIN directly\n"
                "• Use /vin <VIN> command\n\n"
                "*Other commands:*\n"
                "/help - Show all commands\n"
                "/settings - Configure decoder service\n"
            )
            
            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text(
                "Sorry, an error occurred. Please try again later."
            )
    
    async def vin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /vin command."""
        try:
            if not context.args:
                await update.message.reply_text("Usage: /vin <17-character VIN>")
                return
            
            vin = " ".join(context.args).strip()
            
            # Get user preferences
            telegram_id = TelegramID(update.effective_user.id)
            user = await self.user_service.get_user_by_telegram_id(telegram_id)
            preferences = user.preferences if user else UserPreferences()
            
            # Decode the VIN
            result = await self.vehicle_service.decode_vin(vin, preferences)
            
            # Format and send response
            # This would use the message adapter in a full implementation
            if result.success:
                attrs = result.data.get("attributes", {})
                vehicle_desc = " ".join(str(v) for v in [
                    attrs.get("year", ""),
                    attrs.get("make", ""),
                    attrs.get("model", "")
                ] if v)
                
                response_text = f"✅ *{vehicle_desc}*\n\n"
                response_text += f"`{result.vin.value}`\n\n"
                
                if attrs.get("body_type"):
                    response_text += f"Body Type: {attrs['body_type']}\n"
                if attrs.get("fuel_type"):
                    response_text += f"Fuel Type: {attrs['fuel_type']}\n"
                if attrs.get("transmission"):
                    response_text += f"Transmission: {attrs['transmission']}\n"
                
                await update.message.reply_text(
                    response_text,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    f"❌ *Error*\n\nUnable to decode VIN: {result.error_message}",
                    parse_mode=ParseMode.MARKDOWN
                )
        except Exception as e:
            logger.error(f"Error in vin command: {e}")
            await update.message.reply_text(
                "Sorry, an error occurred while decoding the VIN. Please try again later."
            )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command."""
        try:
            help_text = (
                "🤖 *VIN Decoder Bot Commands*\n\n"
                "/start - Show welcome message\n"
                "/vin <VIN> - Decode a VIN\n"
                "/settings - Configure decoder service\n"
                "/history - View your recent VIN searches\n"
                "/help - Show this help message\n\n"
                "You can also just send a 17-character VIN directly!"
            )
            
            await update.message.reply_text(
                help_text,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await update.message.reply_text(
                "Sorry, an error occurred. Please try again later."
            )
    
    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /settings command."""
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            # Get or create user
            user = await self.user_service.get_or_create_user(
                telegram_id=update.effective_user.id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name
            )
            
            current_service = user.preferences.preferred_service.value.upper()
            has_api_key = bool(user.preferences.autodev_api_key)
            
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
            
            await update.message.reply_text(
                settings_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error in settings command: {e}")
            await update.message.reply_text(
                "Sorry, an error occurred. Please try again later."
            )
    
    async def history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /history command."""
        try:
            # Get user history
            history = await self.user_service.get_user_history(
                telegram_id=update.effective_user.id,
                limit=10
            )
            
            if not history:
                await update.message.reply_text(
                    "📋 *Search History*\n\n"
                    "You haven't searched for any VINs yet.\n"
                    "Send a VIN to get started!",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            history_text = "📋 *Recent Search History*\n\n"
            for i, entry in enumerate(history, 1):
                vehicle_info = entry.get("vehicle_info", {})
                vehicle_desc = vehicle_info.get("description", "Unknown Vehicle")
                decoded_at = entry.get("decoded_at", "Unknown")
                vin = entry.get("vin", "Unknown")
                
                history_text += f"{i}. *{vehicle_desc}*\n"
                history_text += f"   VIN: `{vin}`\n"
                history_text += f"   Date: {decoded_at}\n\n"
            
            await update.message.reply_text(
                history_text,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Error in history command: {e}")
            await update.message.reply_text(
                "Sorry, an error occurred. Please try again later."
            )