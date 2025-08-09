from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
import threading
from typing import Optional

from aiohttp import web
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from .carsxe_client import CarsXEClient, CarsXEError
from .config import load_settings
from .formatter import format_vehicle_summary
from .redis_cache import RedisCache
from .upstash_cache import UpstashCache
from .vin import is_valid_vin, normalize_vin


logger = logging.getLogger(__name__)


WELCOME_TEXT = (
    "Send me a 17-character VIN and I'll decode it using CarsXE.\n\n"
    "Commands:\n"
    "/vin <VIN> — decode a VIN\n"
    "/help — show help"
)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_TEXT)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_TEXT)


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


async def handle_vin_decode(update: Update, context: ContextTypes.DEFAULT_TYPE, vin: str) -> None:
    if not is_valid_vin(vin):
        await update.message.reply_text(
            "That VIN looks invalid. VIN should be 17 characters and exclude I, O, Q."
        )
        return

    settings = context.bot_data.get("settings")
    client: CarsXEClient = context.bot_data.get("carsxe_client")
    if not settings or not client:
        await update.message.reply_text("Bot is not initialized correctly. Try again later.")
        return

    await update.message.chat.send_action(action="typing")

    try:
        data = await client.decode_vin(vin)
    except CarsXEError as e:
        logger.exception("CarsXE error")
        await update.message.reply_text(f"Error decoding VIN: {e}")
        return

    summary = format_vehicle_summary(data)
    # Include raw JSON behind a collapsible code fence-like hint
    pretty_json = json.dumps(data, indent=2)[:3500]  # Telegram message limit safety
    reply = f"{summary}\n\nDetails:\n<pre>{escape_html(pretty_json)}</pre>"

    await update.message.reply_text(reply, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def health_check(request):
    """Health check endpoint for Fly.io"""
    return web.Response(text="OK", status=200)


def run_health_server():
    """Run a simple HTTP server for health checks in a separate thread"""
    async def start_server():
        app = web.Application()
        app.router.add_get('/health', health_check)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        logger.info("Health check server started on port 8080")
        # Keep the server running
        await asyncio.Event().wait()
    
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_server())
    
    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()
    logger.info("Health check server thread started")


async def run() -> None:
    settings = load_settings()
    application = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .build()
    )

    # Store settings and shared client in bot_data
    # Initialize cache - prefer Upstash if configured, otherwise Redis
    cache = None
    if os.getenv("UPSTASH_REDIS_REST_URL") and os.getenv("UPSTASH_REDIS_REST_TOKEN"):
        cache = UpstashCache(ttl_seconds=settings.redis_ttl_seconds)
    elif settings.redis_url:
        cache = RedisCache(redis_url=settings.redis_url, ttl_seconds=settings.redis_ttl_seconds)
    
    carsxe_client = CarsXEClient(
        api_key=settings.carsxe_api_key,
        timeout_seconds=settings.http_timeout_seconds,
        cache=cache
    )
    application.bot_data["settings"] = settings
    application.bot_data["carsxe_client"] = carsxe_client

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("vin", cmd_vin))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    # Ensure HTTP client closes on shutdown
    async def on_shutdown(application) -> None:
        await carsxe_client.aclose()

    application.post_shutdown = on_shutdown

    # Start health check server for Fly.io in separate thread
    run_health_server()
    
    logger.info("Bot starting...")
    await application.run_polling()


def main() -> None:
    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info('Shutting down gracefully...')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

