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

from .nhtsa_client import NHTSAClient, NHTSAError
from .autodev_client import AutoDevClient, AutoDevError
from .vin_decoder_base import VINDecoderBase
from .config import load_settings
from .formatter import format_vehicle_summary
from .keyboards import get_details_keyboard
from .user_data import UserDataManager
from .vin import is_valid_vin, normalize_vin

# Import callback system
from .callbacks import CallbackRouter
from .callbacks.vin_callbacks import (
    DecodeVinCallback,
    ShowLevelCallback,
    ShareVinCallback,
    CompareVinCallback,
    RefreshVinCallback
)
from .callbacks.settings_callbacks import (
    ShowSettingsCallback,
    SetServiceCallback,
    ApiKeyCallback,
    ServiceInfoCallback
)
from .callbacks.user_data_callbacks import (
    SaveVehicleCallback,
    DeleteSavedCallback,
    ShowRecentCallback,
    ShowSavedCallback
)
from .callbacks.action_callbacks import (
    ShowSectionCallback,
    ShowMarketValueCallback,
    ShowHistoryCallback,
    NewVinCallback,
    CloseMenuCallback
)

# Import command system
from .commands import (
    CommandRegistry,
    StartCommand,
    HelpCommand,
    VinCommand,
    SettingsCommand,
    RecentCommand,
    SavedCommand
)

# Import service layer
from .services.container import initialize_services, get_container
from .services.vin_service import VINDecodingService
from .services.decoder_service import DecoderSelectionService
from .services.message_service import MessageHandlingService
from .services.settings_service import SettingsService
from .services.user_service import UserPreferencesService


logger = logging.getLogger(__name__)



async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages using the message service."""
    container = get_container()
    message_service = container.get_typed('message_service', MessageHandlingService)
    
    if message_service:
        await message_service.process_text_message(update, context)
    else:
        # Fallback if service not available
        if not update.message or not update.message.text:
            return
        await update.message.reply_text(
            "I expected a 17-character VIN. Use /vin <VIN> or send the VIN directly."
        )


async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the settings menu using the settings service."""
    container = get_container()
    settings_service = container.get_typed('settings_service', SettingsService)
    
    user_id = update.effective_user.id if update.effective_user else None
    
    if not settings_service or not user_id:
        # Fallback message
        message = "Settings are not available."
        if update.message:
            await update.message.reply_text(message)
        elif update.callback_query:
            await update.callback_query.message.reply_text(message)
        return
    
    # Get settings display data
    settings_data = await settings_service.get_settings_display_data(user_id, context)
    
    # Format message and keyboard
    text, keyboard = await settings_service.format_settings_message(settings_data)
    
    # Send the message
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    elif update.message:
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )


async def get_user_decoder(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> VINDecoderBase:
    """Get the user's preferred VIN decoder using the decoder service.
    
    Args:
        context: Bot context
        user_id: User ID
        
    Returns:
        VIN decoder instance based on user's preference
    """
    container = get_container()
    decoder_service = container.get_typed('decoder_service', DecoderSelectionService)
    
    if decoder_service:
        return await decoder_service.get_decoder_for_user(user_id, context)
    
    # Fallback to NHTSA if service not available
    if "nhtsa_client" not in context.bot_data:
        cache = context.bot_data.get("cache")
        context.bot_data["nhtsa_client"] = NHTSAClient(cache=cache)
    return context.bot_data["nhtsa_client"]


async def handle_vin_decode(update: Update, context: ContextTypes.DEFAULT_TYPE, vin: str, from_callback: bool = False, requested_level: Optional[str] = None) -> None:
    """Handle VIN decoding using the VIN service."""
    
    container = get_container()
    vin_service = container.get_typed('vin_service', VINDecodingService)
    
    user_id = update.effective_user.id if update.effective_user else None
    
    if not vin_service:
        # Fallback to basic error
        error_msg = "VIN decoding service is not available. Try again later."
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
    
    # Decode VIN using the service
    result = await vin_service.decode_vin(vin, user_id, context)
    
    if not result['success']:
        # Send error message
        if from_callback:
            await update.callback_query.message.reply_text(
                result['error_message'],
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                result['error_message'],
                parse_mode=ParseMode.MARKDOWN
            )
        return
    
    # Get the decoded data
    data = result['data']
    from_cache = result.get('from_cache', False)
    
    # Store the data temporarily for section display
    context.user_data[f"vehicle_data_{vin}"] = data
    
    # Add from_cache flag to data
    if from_cache:
        data["from_cache"] = True

    try:
        # Import smart formatting components
        from .smart_formatter import (
            format_vehicle_smart_card, 
            InformationLevel, 
            DisplayMode,
            suggest_information_level
        )
        from .smart_keyboards import get_adaptive_keyboard
        from .user_context import UserContextManager
        
        # Get or create user context manager
        if not user_context_mgr and user_id:
            user_context_mgr = UserContextManager(cache=context.bot_data.get("cache"))
            context.bot_data["user_context_manager"] = user_context_mgr
        
        # Determine information level to display
        if requested_level:
            # User explicitly requested a level
            try:
                display_level = InformationLevel(int(requested_level))
            except (ValueError, TypeError):
                display_level = InformationLevel.STANDARD
        else:
            # Use smart suggestion
            if user_context_mgr and user_id:
                data_richness = await user_context_mgr.calculate_data_richness(data)
                display_level = await user_context_mgr.suggest_optimal_level(user_id, data_richness)
            else:
                display_level = suggest_information_level(data)
        
        # Detect mobile user
        is_mobile = False
        if user_context_mgr and user_id:
            is_mobile = await user_context_mgr.detect_mobile_user(user_id, context)
        
        # Get user context for adaptive keyboard
        user_context = {}
        if user_context_mgr and user_id:
            user_context = await user_context_mgr.get_user_context_dict(user_id)
        
        # Format the smart summary
        display_mode = DisplayMode.MOBILE if is_mobile else DisplayMode.DESKTOP
        summary_text = format_vehicle_smart_card(data, display_level, display_mode)
        
        # Create adaptive keyboard
        keyboard = get_adaptive_keyboard(vin, data, display_level, user_context)
        
        # Send the summary with smart keyboard
        if from_callback:
            message = await update.callback_query.message.reply_text(
                summary_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        else:
            message = await update.message.reply_text(
                summary_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        
        # Track the search for user learning
        if user_context_mgr and user_id:
            await user_context_mgr.track_vin_search(user_id, vin, display_level, is_mobile)
        
        logger.info(f"Successfully sent smart VIN decode card for {vin} at level {display_level.name}")
        
    except Exception as e:
        logger.exception(f"Error in smart formatting for VIN {vin}, falling back to original")
        # Fallback to original formatting
        try:
            from .formatter import format_vehicle_summary
            from .keyboards import get_details_keyboard
            
            summary_text = format_vehicle_summary(data)
            has_history = "history" in data and data["history"]
            has_marketvalue = "marketvalue" in data and data["marketvalue"]
            details_keyboard = get_details_keyboard(vin, has_history=has_history, has_marketvalue=has_marketvalue)
            
            if from_callback:
                message = await update.callback_query.message.reply_text(
                    summary_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=details_keyboard
                )
            else:
                message = await update.message.reply_text(
                    summary_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=details_keyboard
                )
        except Exception as fallback_error:
            logger.exception(f"Even fallback formatting failed for VIN {vin}")
            # Last resort - basic info
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








async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all callback queries from inline keyboards using the router."""
    # The router will handle everything
    router: CallbackRouter = context.bot_data.get("callback_router")
    if router:
        await router.route(update, context)
    else:
        logger.error("Callback router not initialized")




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
    """Run the bot using run_polling (handles its own event loop)"""
    # Start health check server in separate thread
    run_health_server()
    
    logger.info("Bot starting...")
    
    # Create application synchronously
    settings = load_settings()
    
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
    # Redis support removed; Upstash only
    
    # Initialize user data manager
    user_data_mgr = UserDataManager(cache=cache)
    
    # Create NHTSA client (doesn't require API key)
    nhtsa_client = NHTSAClient(cache=cache)
    
    # Initialize callback router and register all strategies
    callback_router = CallbackRouter()
    
    # Register VIN callbacks
    callback_router.register(DecodeVinCallback())
    callback_router.register(ShowLevelCallback())
    callback_router.register(ShareVinCallback())
    callback_router.register(CompareVinCallback())
    callback_router.register(RefreshVinCallback())
    
    # Register settings callbacks
    callback_router.register(ShowSettingsCallback())
    callback_router.register(SetServiceCallback())
    callback_router.register(ApiKeyCallback())
    callback_router.register(ServiceInfoCallback())
    
    # Register user data callbacks
    callback_router.register(SaveVehicleCallback())
    callback_router.register(DeleteSavedCallback())
    callback_router.register(ShowRecentCallback())
    callback_router.register(ShowSavedCallback())
    
    # Register action callbacks
    callback_router.register(ShowSectionCallback())
    callback_router.register(ShowMarketValueCallback())
    callback_router.register(ShowHistoryCallback())
    callback_router.register(NewVinCallback())
    callback_router.register(CloseMenuCallback())
    
    # Initialize command registry and register all commands
    command_registry = CommandRegistry()
    command_registry.register(StartCommand())
    command_registry.register(HelpCommand())
    command_registry.register(VinCommand())
    command_registry.register(SettingsCommand())
    command_registry.register(RecentCommand())
    command_registry.register(SavedCommand())
    
    application.bot_data["settings"] = settings
    application.bot_data["nhtsa_client"] = nhtsa_client
    application.bot_data["user_data_manager"] = user_data_mgr
    application.bot_data["cache"] = cache  # Store cache reference for AutoDevClient
    application.bot_data["callback_router"] = callback_router
    application.bot_data["command_registry"] = command_registry
    
    # Initialize the service container with all services
    container = initialize_services(application)
    application.bot_data["service_container"] = container

    # Register all command handlers from the registry
    for handler in command_registry.get_telegram_handlers():
        application.add_handler(handler)
    
    # Register callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Register message handler for direct VIN input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    # Ensure cache closes on shutdown
    async def on_shutdown(application) -> None:
        cache = application.bot_data.get("cache")
        if cache and hasattr(cache, 'aclose'):
            await cache.aclose()

    application.post_shutdown = on_shutdown
    
    # run_polling manages its own event loop - this is the blocking call
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

