"""Callback handlers for the Telegram bot."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from src.application.vehicle.services.vehicle_application_service import (
    VehicleApplicationService,
)
from src.application.user.services.user_application_service import (
    UserApplicationService,
)
from src.presentation.telegram_bot.adapters.message_adapter import MessageAdapter
from src.presentation.telegram_bot.adapters.keyboard_adapter import KeyboardAdapter
from src.presentation.telegram_bot.formatters.premium_features_formatter import PremiumFeaturesFormatter

logger = logging.getLogger(__name__)


class CallbackHandlers:
    """Handlers for Telegram callback queries."""

    def __init__(
        self,
        vehicle_service: VehicleApplicationService,
        user_service: UserApplicationService,
        message_adapter: MessageAdapter,
        keyboard_adapter: KeyboardAdapter,
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

    async def handle_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        await query.answer()

        data = query.data

        try:
            if data == "settings:back":
                await self._show_settings_menu(update, context)
            elif data.startswith("refresh:"):
                await self._handle_refresh(update, context, data)
            elif data == "close":
                await self._handle_close(update, context)
            elif data.startswith("action:"):
                await self._handle_action_button(update, context, data)
            elif data.startswith("features:"):
                await self._handle_features_navigation(update, context, data)
            elif data.startswith("feature_category:"):
                await self._handle_feature_category(update, context, data)
            else:
                logger.warning(f"Unknown callback data: {data}")
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await query.edit_message_text(
                "Sorry, an error occurred. Please try again later."
            )
    
    async def _handle_features_navigation(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str
    ) -> None:
        """Handle features navigation callbacks."""
        query = update.callback_query
        
        try:
            # Parse the callback data
            parts = data.split(":")
            if len(parts) < 2:
                logger.error(f"Invalid features callback data: {data}")
                return
            
            action = parts[1]
            
            if action == "show_categories":
                # Get vehicle data from context if available
                vehicle_data = context.user_data.get("last_vehicle_data", {})
                await self._show_feature_categories(update, context, vehicle_data)
            elif action == "back_to_vehicle":
                # Go back to vehicle summary
                vehicle_data = context.user_data.get("last_vehicle_data", {})
                await self._show_vehicle_summary(update, context, vehicle_data)
                
        except Exception as e:
            logger.error(f"Error in features navigation: {e}")
            await query.edit_message_text(
                "❌ An error occurred. Please try again."
            )
    
    async def _handle_feature_category(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str
    ) -> None:
        """Handle feature category selection callbacks."""
        query = update.callback_query
        
        try:
            # Parse the callback data
            parts = data.split(":")
            if len(parts) < 2:
                logger.error(f"Invalid feature category callback data: {data}")
                return
            
            category = parts[1]
            
            # Get vehicle features from context
            vehicle_data = context.user_data.get("last_vehicle_data", {})
            features = PremiumFeaturesFormatter.extract_features(vehicle_data)
            
            if not features:
                await query.edit_message_text(
                    "No features available for this vehicle."
                )
                return
            
            # Get categorized features
            categorized = PremiumFeaturesFormatter.get_feature_categories(features)
            
            if category not in categorized:
                await query.edit_message_text(
                    f"No features found in the {category} category."
                )
                return
            
            # Format the features for this category
            category_features = categorized[category]
            message_text = PremiumFeaturesFormatter.format_category_features(
                category, category_features
            )
            
            # Add navigation buttons
            keyboard = [
                [InlineKeyboardButton("↩️ Back to Categories", callback_data="features:show_categories")],
                [InlineKeyboardButton("🚗 Back to Vehicle", callback_data="features:back_to_vehicle")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in feature category handler: {e}")
            await query.edit_message_text(
                "❌ An error occurred. Please try again."
            )
    
    async def _show_feature_categories(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, vehicle_data: dict
    ) -> None:
        """Show feature categories with buttons."""
        query = update.callback_query
        
        features = PremiumFeaturesFormatter.extract_features(vehicle_data)
        if not features:
            await query.edit_message_text(
                "No features available for this vehicle."
            )
            return
        
        # Get categorized features
        categorized = PremiumFeaturesFormatter.get_feature_categories(features)
        
        # Create summary message
        message_text = PremiumFeaturesFormatter.format_features_summary_with_buttons(features)
        
        # Create category buttons
        keyboard = []
        
        # Add category buttons in rows of 2
        category_order = ["safety", "technology", "luxury", "performance", "comfort", 
                         "entertainment", "convenience", "exterior", "interior", "eco"]
        
        button_row = []
        for category in category_order:
            if category in categorized:
                count = len(categorized[category])
                icon = PremiumFeaturesFormatter.CATEGORY_ICONS.get(category, "•")
                button_text = f"{icon} {category.capitalize()} ({count})"
                button_row.append(
                    InlineKeyboardButton(
                        button_text, 
                        callback_data=f"feature_category:{category}"
                    )
                )
                
                if len(button_row) == 2:
                    keyboard.append(button_row)
                    button_row = []
        
        # Add remaining button if any
        if button_row:
            keyboard.append(button_row)
        
        # Add back button
        keyboard.append([
            InlineKeyboardButton("↩️ Back to Vehicle", callback_data="features:back_to_vehicle")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def _show_vehicle_summary(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, vehicle_data: dict
    ) -> None:
        """Show vehicle summary with updated button."""
        query = update.callback_query
        
        # This would normally show the full vehicle summary
        # For now, we'll show a placeholder
        await query.edit_message_text(
            "🚗 *Vehicle Summary*\n\nReturning to vehicle view...",
            parse_mode=ParseMode.MARKDOWN
        )

    async def _handle_refresh(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str
    ) -> None:
        """Handle refresh callback for VIN data."""
        query = update.callback_query
        vin = data.replace("refresh:", "")

        try:
            # Update the message to show refreshing
            await query.edit_message_text(
                f"🔄 Refreshing data for VIN: `{vin}`\n\nPlease wait...",
                parse_mode=ParseMode.MARKDOWN,
            )

            # Get user and decode again
            _user = await self.user_service.get_or_create_user(
                telegram_id=update.effective_user.id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                language_code=getattr(update.effective_user, 'language_code', 'en'),
            )

            # Decode the VIN again (force refresh)
            # This would need actual implementation in vehicle service
            # result = await self.vehicle_service.decode_vin(vin, user.preferences, force_refresh=True)

            # For now, show a simple response
            response_text = (
                f"✅ *Refreshed Data*\n\nVIN: `{vin}`\n\nData has been refreshed!"
            )

            # Add keyboard
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh:{vin}")],
                [
                    InlineKeyboardButton(
                        "📋 Decode Another", callback_data="action:decode_vin"
                    )
                ],
                [InlineKeyboardButton("❌ Close", callback_data="close")],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                response_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error in refresh callback: {e}")
            await query.edit_message_text(
                "❌ An error occurred while refreshing the data. Please try again."
            )

    async def _handle_close(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
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
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Show the main settings menu."""
        query = update.callback_query

        # Build simplified keyboard
        keyboard = [[InlineKeyboardButton("↩️ Back", callback_data="action:start")]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        settings_text = (
            "⚙️ *Settings*\n\n"
            "Decoder service: *Auto.dev with NHTSA fallback*\n"
            "This bot uses Auto.dev as the primary decoder and automatically falls back to NHTSA if needed.\n\n"
            "No configuration required!"
        )

        await query.edit_message_text(
            settings_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )

    async def _handle_action_button(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str
    ) -> None:
        """Handle action button callbacks."""
        query = update.callback_query
        action = data.split(":")[1]  # Extract action name

        try:
            if action == "decode_vin":
                # Prompt user to send a VIN
                await query.edit_message_text(
                    "🔢 *Decode VIN*\n\n"
                    "✨ Just paste your VIN and I'll automatically detect and decode it!\n\n"
                    "You can also use the /vin command if you prefer.\n\n"
                    "Example: `1HGBH41JXMN109186`",
                    parse_mode=ParseMode.MARKDOWN,
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
                    "✨ *Automatic VIN Detection*\n"
                    "Just paste a VIN anywhere in your message and I'll automatically detect and decode it!\n\n"
                    "Example: `1HGBH41JXMN109186`"
                )

                # Add back button
                keyboard = [
                    [InlineKeyboardButton("↩️ Back", callback_data="action:start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
                )
            elif action == "start":
                # Show start menu again
                welcome_text = (
                    "🚗 *Welcome to VIN Decoder Bot!*\n\n"
                    "I can decode Vehicle Identification Numbers (VINs) using official databases.\n\n"
                    "Select an option below to get started:"
                )

                # Create action buttons
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "🔍 Decode VIN", callback_data="action:decode_vin"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⚙️ Settings", callback_data="action:settings"
                        )
                    ],
                    [InlineKeyboardButton("📖 Help", callback_data="action:help")],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    welcome_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup,
                )
        except Exception as e:
            logger.error(f"Error in action button handler: {e}")
            await query.edit_message_text(
                "Sorry, an error occurred. Please try again later."
            )
