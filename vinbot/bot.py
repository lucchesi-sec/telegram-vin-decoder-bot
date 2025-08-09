from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
import threading
from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, CallbackQuery
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from .carsxe_client import CarsXEClient, CarsXEError
from .config import load_settings
from .formatter import (
    format_vehicle_summary, 
    format_vehicle_card,
    format_specs_section,
    format_manufacturing_section,
    format_dimensions_section,
    format_performance_section,
    format_features_section,
    format_comparison
)
from .keyboards import (
    get_details_keyboard,
    get_actions_keyboard,
    get_recent_vins_keyboard,
    get_saved_vins_keyboard,
    get_sample_vin_keyboard,
    get_comparison_keyboard,
    get_confirmation_keyboard,
    get_close_button
)
from .user_data import UserDataManager
from .vin import is_valid_vin, normalize_vin


logger = logging.getLogger(__name__)


WELCOME_TEXT = (
    "🚗 **Welcome to VIN Decoder Bot!**\n\n"
    "I can decode Vehicle Identification Numbers (VINs) and provide detailed vehicle information.\n\n"
    "**How to use:**\n"
    "• Send me a 17-character VIN directly\n"
    "• Use /vin <VIN> command\n"
    "• Try the sample VIN below\n\n"
    "**Commands:**\n"
    "/vin <VIN> — Decode a VIN\n"
    "/recent — View recent searches\n"
    "/saved — View saved vehicles\n"
    "/help — Show this help message\n\n"
    "_VIN Format: 17 characters (letters & numbers)_\n"
    "_Invalid characters: I, O, Q_"
)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_sample_vin_keyboard()
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_sample_vin_keyboard()
    )


async def cmd_vin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /vin <17-character VIN>")
        return
    vin = normalize_vin("".join(context.args))
    await handle_vin_decode(update, context, vin)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    if len(text) == 17 and is_valid_vin(text):
        await handle_vin_decode(update, context, normalize_vin(text))
    else:
        await update.message.reply_text(
            "I expected a 17-character VIN. Use /vin <VIN> or send the VIN directly."
        )


async def handle_vin_decode(update: Update, context: ContextTypes.DEFAULT_TYPE, vin: str, from_callback: bool = False) -> None:
    """Handle VIN decoding with new UX improvements"""
    
    # Validate VIN
    if not is_valid_vin(vin):
        error_msg = (
            "❌ **Invalid VIN Format**\n\n"
            "VIN must be:\n"
            "• Exactly 17 characters\n"
            "• Letters and numbers only\n"
            "• No I, O, or Q letters\n\n"
            f"_You entered: {len(vin)} characters_"
        )
        if from_callback:
            await update.callback_query.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)
        return

    # Get bot components
    settings = context.bot_data.get("settings")
    client: CarsXEClient = context.bot_data.get("carsxe_client")
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    
    if not settings or not client:
        error_msg = "Bot is not initialized correctly. Try again later."
        if from_callback:
            await update.callback_query.message.reply_text(error_msg)
        else:
            await update.message.reply_text(error_msg)
        return

    # Send typing indicator
    if from_callback:
        await update.callback_query.message.chat.send_action(action="typing")
    else:
        await update.message.chat.send_action(action="typing")

    # First check if we have cached vehicle data (from history/favorites)
    from_cache = False
    data = None
    
    if user_data_mgr:
        data = await user_data_mgr.get_vehicle_data(vin)
        if data:
            from_cache = True
            logger.info(f"Using cached vehicle data for VIN {vin}")

    # If not in user cache, fetch from API (which might use Redis cache)
    if not data:
        try:
            data = await client.decode_vin(vin)
        except CarsXEError as e:
            logger.error(f"CarsXE error for VIN {vin}: {e}")
            error_msg = f"❌ Error decoding VIN: {e}"
            if from_callback:
                await update.callback_query.message.reply_text(error_msg)
            else:
                await update.message.reply_text(error_msg)
            return
        except Exception as e:
            logger.exception(f"Unexpected error decoding VIN {vin}")
            error_msg = f"❌ Unexpected error: {str(e)}"
            if from_callback:
                await update.callback_query.message.reply_text(error_msg)
            else:
                await update.message.reply_text(error_msg)
            return

    # Store the data temporarily for section display
    context.user_data[f"vehicle_data_{vin}"] = data
    
    # Add to user history
    user_id = update.effective_user.id if update.effective_user else None
    if user_data_mgr and user_id:
        await user_data_mgr.add_to_history(user_id, vin, data)

    try:
        # Format the concise card view
        card_text = format_vehicle_card(data, from_cache=from_cache)
        
        # Create inline keyboards
        details_keyboard = get_details_keyboard(vin, sections_shown=[])
        actions_keyboard = get_actions_keyboard(vin, user_id) if user_id else None
        
        # Send the card with inline keyboard
        if from_callback:
            message = await update.callback_query.message.reply_text(
                card_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=details_keyboard
            )
        else:
            message = await update.message.reply_text(
                card_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=details_keyboard
            )
        
        # Send actions as a follow-up message
        if actions_keyboard:
            await message.reply_text(
                "**Quick Actions:**",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=actions_keyboard
            )
        
        logger.info(f"Successfully sent VIN decode card for {vin}")
        
    except Exception as e:
        logger.exception(f"Error formatting/sending response for VIN {vin}")
        # Fallback to simple format
        try:
            basic_info = "✅ VIN decoded successfully\n\n"
            if isinstance(data, dict) and "attributes" in data:
                attrs = data["attributes"]
                basic_info += f"VIN: {attrs.get('vin', 'N/A')}\n"
                basic_info += f"Year: {attrs.get('year', 'N/A')}\n"
                basic_info += f"Make: {attrs.get('make', 'N/A')}\n"
                basic_info += f"Model: {attrs.get('model', 'N/A')}\n"
                basic_info += f"Body: {attrs.get('body', 'N/A')}\n"
                basic_info += f"Fuel Type: {attrs.get('fuel_type', 'N/A')}\n"
            
            if from_callback:
                await update.callback_query.message.reply_text(basic_info)
            else:
                await update.message.reply_text(basic_info)
        except:
            error_msg = "✅ VIN decoded but had trouble formatting the response."
            if from_callback:
                await update.callback_query.message.reply_text(error_msg)
            else:
                await update.message.reply_text(error_msg)


async def cmd_recent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show recent VIN searches"""
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    user_id = update.effective_user.id if update.effective_user else None
    
    if not user_data_mgr or not user_id:
        await update.message.reply_text("Recent searches are not available.")
        return
    
    recent = await user_data_mgr.get_history(user_id)
    
    if not recent:
        await update.message.reply_text(
            "No recent searches found.\n\n"
            "Start by decoding a VIN to build your history!",
            reply_markup=get_sample_vin_keyboard()
        )
        return
    
    keyboard = get_recent_vins_keyboard(recent)
    await update.message.reply_text(
        "🕐 **Recent Searches**\n\n"
        "_Select a vehicle to decode again:_",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )


async def cmd_saved(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show saved vehicles"""
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    user_id = update.effective_user.id if update.effective_user else None
    
    if not user_data_mgr or not user_id:
        await update.message.reply_text("Saved vehicles are not available.")
        return
    
    saved = await user_data_mgr.get_favorites(user_id)
    
    if not saved:
        await update.message.reply_text(
            "No saved vehicles found.\n\n"
            "After decoding a VIN, use the 💾 Save button to add it to your favorites!"
        )
        return
    
    keyboard = get_saved_vins_keyboard(saved)
    await update.message.reply_text(
        "⭐ **Saved Vehicles**\n\n"
        "_Select a vehicle to view or 🗑️ to remove:_",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all callback queries from inline keyboards"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id if update.effective_user else None
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    
    # Handle different callback types
    if data.startswith("show_"):
        # Handle section display callbacks
        parts = data.split(":")
        if len(parts) == 2:
            section, vin = parts[0].replace("show_", ""), parts[1]
            await show_vehicle_section(query, context, section, vin)
    
    elif data.startswith("sample_vin:"):
        # Handle sample VIN
        vin = data.replace("sample_vin:", "")
        await handle_vin_decode(update, context, vin, from_callback=True)
    
    elif data.startswith("decode_vin:"):
        # Decode a VIN from history/saved
        vin = data.replace("decode_vin:", "")
        await handle_vin_decode(update, context, vin, from_callback=True)
    
    elif data.startswith("save_vin:"):
        # Save a VIN to favorites
        parts = data.split(":")
        if len(parts) >= 2:
            vin = parts[1]
            await save_vehicle(query, context, vin, user_id)
    
    elif data.startswith("delete_saved:"):
        # Remove from favorites
        vin = data.replace("delete_saved:", "")
        await delete_saved_vehicle(query, context, vin, user_id)
    
    elif data == "show_recent":
        # Show recent searches
        if user_data_mgr and user_id:
            recent = await user_data_mgr.get_history(user_id)
            if recent:
                keyboard = get_recent_vins_keyboard(recent)
                await query.message.edit_text(
                    "🕐 **Recent Searches**\n\n"
                    "_Select a vehicle to decode again:_",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            else:
                await query.message.edit_text("No recent searches found.")
    
    elif data == "show_saved":
        # Show saved vehicles
        if user_data_mgr and user_id:
            saved = await user_data_mgr.get_favorites(user_id)
            if saved:
                keyboard = get_saved_vins_keyboard(saved)
                await query.message.edit_text(
                    "⭐ **Saved Vehicles**\n\n"
                    "_Select a vehicle to view:_",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            else:
                await query.message.edit_text("No saved vehicles found.")
    
    elif data == "new_vin":
        # Prompt for new VIN
        await query.message.reply_text(
            "Please send me a 17-character VIN to decode:"
        )
    
    elif data == "close_menu":
        # Close the menu
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.edit_text(
            query.message.text + "\n\n_[Menu closed]_",
            parse_mode=ParseMode.MARKDOWN
        )


async def show_vehicle_section(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, section: str, vin: str) -> None:
    """Show a specific section of vehicle data"""
    
    # Get the stored vehicle data
    data = context.user_data.get(f"vehicle_data_{vin}")
    
    if not data:
        # Try to fetch from user data manager
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        if user_data_mgr:
            data = await user_data_mgr.get_vehicle_data(vin)
    
    if not data:
        await query.message.reply_text("Vehicle data not found. Please decode the VIN again.")
        return
    
    # Format the appropriate section
    if section == "specs":
        text = format_specs_section(data)
    elif section == "manufacturing":
        text = format_manufacturing_section(data)
    elif section == "dimensions":
        text = format_dimensions_section(data)
    elif section == "performance":
        text = format_performance_section(data)
    elif section == "features":
        text = format_features_section(data)
    elif section == "all":
        text = format_vehicle_summary(data)
    else:
        text = "Unknown section requested."
    
    # Update keyboard to show remaining sections
    sections_shown = [section] if section != "all" else ["all"]
    keyboard = get_details_keyboard(vin, sections_shown)
    
    # Send as new message
    await query.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard if section != "all" else None
    )


async def save_vehicle(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, vin: str, user_id: int) -> None:
    """Save a vehicle to favorites"""
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    
    if not user_data_mgr or not user_id:
        await query.message.reply_text("Unable to save vehicle.")
        return
    
    # Get vehicle data
    data = context.user_data.get(f"vehicle_data_{vin}")
    if not data:
        data = await user_data_mgr.get_vehicle_data(vin)
    
    if not data:
        await query.message.reply_text("Vehicle data not found.")
        return
    
    # Save to favorites
    success = await user_data_mgr.add_to_favorites(user_id, vin, data)
    
    if success:
        await query.message.reply_text(
            "✅ **Vehicle Saved!**\n\n"
            "You can view your saved vehicles with /saved",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await query.message.reply_text("Failed to save vehicle. Please try again.")


async def delete_saved_vehicle(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, vin: str, user_id: int) -> None:
    """Remove a vehicle from favorites"""
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    
    if not user_data_mgr or not user_id:
        await query.message.reply_text("Unable to remove vehicle.")
        return
    
    success = await user_data_mgr.remove_from_favorites(user_id, vin)
    
    if success:
        # Update the saved vehicles list
        saved = await user_data_mgr.get_favorites(user_id)
        if saved:
            keyboard = get_saved_vins_keyboard(saved)
            await query.message.edit_text(
                "⭐ **Saved Vehicles**\n\n"
                "_Vehicle removed. Select another vehicle:_",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        else:
            await query.message.edit_text(
                "No saved vehicles remaining.\n\n"
                "After decoding a VIN, use the 💾 Save button to add it to your favorites!"
            )
    else:
        await query.message.reply_text("Failed to remove vehicle.")


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks"""
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress request logging
        pass


def run_health_server():
    """Run health check server in a separate thread"""
    def serve():
        server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
        logger.info("Health check server started on port 8080")
        server.serve_forever()
    
    thread = threading.Thread(target=serve, daemon=True)
    thread.start()


def run() -> None:
    settings = load_settings()
    
    # Start health check server in separate thread
    run_health_server()
    
    application = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .build()
    )

    # Initialize cache backend (if configured)
    cache = None
    upstash_url = os.getenv("UPSTASH_REDIS_REST_URL", "").strip()
    upstash_token = os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip()
    
    if upstash_url and upstash_token:
        try:
            from .upstash_cache import UpstashCache
            cache = UpstashCache(upstash_url, upstash_token, ttl=settings.redis_ttl_seconds)
            logger.info("Using Upstash cache for user data")
        except Exception as e:
            logger.warning(f"Failed to initialize Upstash cache: {e}")
    elif settings.redis_url:
        try:
            from .redis_cache import RedisCache
            cache = RedisCache(settings.redis_url, ttl=settings.redis_ttl_seconds)
            logger.info("Using Redis cache for user data")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
    
    # Initialize user data manager
    user_data_mgr = UserDataManager(cache=cache)
    
    # Store settings and shared clients in bot_data
    carsxe_client = CarsXEClient(
        api_key=settings.carsxe_api_key,
        timeout_seconds=settings.http_timeout_seconds
    )
    
    # Set cache for CarsXE client if available
    if cache:
        carsxe_client.cache = cache
    
    application.bot_data["settings"] = settings
    application.bot_data["carsxe_client"] = carsxe_client
    application.bot_data["user_data_manager"] = user_data_mgr

    # Register command handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("vin", cmd_vin))
    application.add_handler(CommandHandler("recent", cmd_recent))
    application.add_handler(CommandHandler("saved", cmd_saved))
    
    # Register callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Register message handler for direct VIN input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    # Ensure HTTP client closes on shutdown
    async def on_shutdown(application) -> None:
        await carsxe_client.aclose()
        if hasattr(cache, 'aclose'):
            await cache.aclose()

    application.post_shutdown = on_shutdown
    
    logger.info("Bot starting...")
    
    # run_polling manages its own event loop, so call it directly without await
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info('Shutting down gracefully...')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # run_polling manages its own event loop, so just call it directly
    try:
        run()
    except KeyboardInterrupt:
        pass

