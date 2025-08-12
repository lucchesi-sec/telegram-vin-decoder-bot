"""Command handlers for the Telegram bot."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from src.application.vehicle.services.vehicle_application_service import (
    VehicleApplicationService,
)
from src.application.user.services.user_application_service import (
    UserApplicationService,
)
from src.presentation.telegram_bot.adapters.message_adapter import MessageAdapter
from src.presentation.telegram_bot.adapters.keyboard_adapter import KeyboardAdapter
from src.presentation.telegram_bot.formatters.vehicle_formatter import VehicleFormatter

logger = logging.getLogger(__name__)


class CommandHandlers:
    """Handlers for Telegram commands."""

    def __init__(
        self,
        vehicle_service: VehicleApplicationService,
        user_service: UserApplicationService,
        message_adapter: MessageAdapter,
        keyboard_adapter: KeyboardAdapter,
    ):
        self.vehicle_service = vehicle_service
        self.user_service = user_service
        self.message_adapter = message_adapter
        self.keyboard_adapter = keyboard_adapter

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            welcome_text = (
                "🚗 *Welcome to VIN Decoder Bot!*\n\n"
                "I can decode Vehicle Identification Numbers (VINs) using official databases.\n\n"
                "✨ *NEW: Just paste a VIN and I'll automatically decode it!*\n\n"
                "Select an option below to get started:"
            )

            # Create action buttons
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔍 Decode VIN", callback_data="action:decode_vin"
                    )
                ],
                [InlineKeyboardButton("⚙️ Settings", callback_data="action:settings")],
                [InlineKeyboardButton("📖 Help", callback_data="action:help")],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
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

            # Get or create user to ensure we have their preferences
            user = await self.user_service.get_or_create_user(
                telegram_id=update.effective_user.id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                language_code=getattr(update.effective_user, 'language_code', 'en'),
            )

            logger.info(
                f"User {update.effective_user.id} preferences: decoder={user.preferences.preferred_decoder}"
            )

            # Show processing message
            processing_msg = await update.message.reply_text(
                f"🔍 Decoding VIN: `{vin}`...", parse_mode=ParseMode.MARKDOWN
            )

            # Decode the VIN
            result = await self.vehicle_service.decode_vin(vin, user.preferences)

            # Delete processing message
            try:
                await processing_msg.delete()
            except Exception:
                pass  # Ignore if message already deleted

            # Format and send response
            if result.success:
                # Create a data dictionary that matches what the formatter expects
                vehicle_data = {
                    "success": True,
                    "vin": result.vin,
                    "attributes": result.attributes or {},
                    "service": result.service_used,
                    "raw_data": result.raw_data if hasattr(result, "raw_data") else {},
                }

                # Use our enhanced vehicle formatter
                response_text = VehicleFormatter.format_summary(vehicle_data)

                # Add service information
                response_text += f"\n\n🔧 _Decoded by {result.service_used}_"

                # Store vehicle data in context for feature navigation
                context.user_data["last_vehicle_data"] = vehicle_data
                
                # Check if there are features to display
                from src.presentation.telegram_bot.formatters.premium_features_formatter import PremiumFeaturesFormatter
                features = PremiumFeaturesFormatter.extract_features(vehicle_data)
                
                # Add action buttons
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup

                keyboard = []
                
                # Add features button if features exist
                if features:
                    keyboard.append([
                        InlineKeyboardButton(
                            f"✨ View Features ({len(features)})", 
                            callback_data="features:show_categories"
                        )
                    ])
                
                keyboard.extend([
                    [
                        InlineKeyboardButton(
                            "🔄 Refresh", callback_data=f"refresh:{result.vin}"
                        ),
                        InlineKeyboardButton(
                            "📋 Decode Another", callback_data="action:decode_vin"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "⚙️ Settings", callback_data="action:settings"
                        ),
                        InlineKeyboardButton("❌ Close", callback_data="close"),
                    ],
                ])
                reply_markup = InlineKeyboardMarkup(keyboard)

                # Trim message if too long for Telegram (4096 char limit)
                if len(response_text) > 4000:
                    response_text = response_text[:3997] + "..."

                await update.message.reply_text(
                    response_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup,
                )
            else:
                # Add action buttons for error case
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "📋 Try Again", callback_data="action:decode_vin"
                        )
                    ],
                    [InlineKeyboardButton("❓ Help", callback_data="action:help")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    f"❌ *Error*\n\nUnable to decode VIN: {result.error_message}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup,
                )
        except Exception as e:
            logger.error(f"Error in vin command: {e}")
            await update.message.reply_text(
                "Sorry, an error occurred while decoding the VIN. Please try again later."
            )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command."""
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            help_text = (
                "🤖 *VIN Decoder Bot Commands*\n\n"
                "/start - Show welcome message\n"
                "/vin <VIN> - Decode a VIN\n"
                "/settings - Configure decoder service\n"
                "/history - View your recent VIN searches\n"
                "/help - Show this help message\n\n"
                "✨ *Automatic VIN Detection*\n"
                "Just paste a VIN anywhere in your message and I'll automatically detect and decode it!\n\n"
                "Example: `1HGBH41JXMN109186`"
            )

            # Add back button
            keyboard = [[InlineKeyboardButton("↩️ Back", callback_data="action:start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await update.message.reply_text(
                "Sorry, an error occurred. Please try again later."
            )

    async def settings(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /settings command."""
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            # Get or create user (for future use with preferences)
            _user = await self.user_service.get_or_create_user(
                telegram_id=update.effective_user.id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                language_code=getattr(update.effective_user, 'language_code', 'en'),
            )

            # Build keyboard - simplified without decoder selection or API key management
            keyboard = [[InlineKeyboardButton("↩️ Back", callback_data="action:start")]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            settings_text = (
                "⚙️ *Settings*\n\n"
                "Decoder service: *Auto.dev with NHTSA fallback*\n"
                "This bot uses Auto.dev as the primary decoder and automatically falls back to NHTSA if needed.\n\n"
                "No configuration required!"
            )

            await update.message.reply_text(
                settings_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error in settings command: {e}")
            await update.message.reply_text(
                "Sorry, an error occurred. Please try again later."
            )

    async def history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /history command."""
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            # Get user history
            history = await self.user_service.get_user_history(
                telegram_id=update.effective_user.id, limit=10
            )

            # Add action buttons
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔍 Decode VIN", callback_data="action:decode_vin"
                    )
                ],
                [InlineKeyboardButton("↩️ Back", callback_data="action:start")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if not history:
                await update.message.reply_text(
                    "📋 *Search History*\n\n"
                    "You haven't searched for any VINs yet.\n"
                    "Send a VIN to get started!",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup,
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
                history_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error in history command: {e}")
            await update.message.reply_text(
                "Sorry, an error occurred. Please try again later."
            )
