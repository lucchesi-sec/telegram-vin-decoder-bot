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

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from .carsxe_client import CarsXEClient, CarsXEError
from .config import load_settings
from .formatter import format_vehicle_summary
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
        logger.error(f"CarsXE error for VIN {vin}: {e}")
        await update.message.reply_text(f"❌ Error decoding VIN: {e}")
        return
    except Exception as e:
        logger.exception(f"Unexpected error decoding VIN {vin}")
        await update.message.reply_text(f"❌ Unexpected error: {str(e)}")
        return

    try:
        summary = format_vehicle_summary(data)
        
        # Split message if it's too long (Telegram limit is 4096 characters)
        if len(summary) <= 4096:
            await update.message.reply_text(
                summary,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Split into multiple messages if needed
            parts = []
            current_part = []
            current_length = 0
            
            for line in summary.split('\n'):
                line_length = len(line) + 1  # +1 for newline
                if current_length + line_length > 4000:  # Leave some buffer
                    parts.append('\n'.join(current_part))
                    current_part = [line]
                    current_length = line_length
                else:
                    current_part.append(line)
                    current_length += line_length
            
            if current_part:
                parts.append('\n'.join(current_part))
            
            for part in parts:
                await update.message.reply_text(
                    part,
                    parse_mode=ParseMode.MARKDOWN
                )
        
        # Log success for debugging
        logger.info(f"Successfully sent VIN decode for {vin}")
    except Exception as e:
        logger.exception(f"Error formatting/sending response for VIN {vin}")
        # Try to send without markdown formatting
        try:
            summary = format_vehicle_summary(data)
            # Remove markdown formatting
            summary_plain = summary.replace("**", "").replace("`", "")
            
            if len(summary_plain) <= 4096:
                await update.message.reply_text(summary_plain)
            else:
                # Send just the essential info
                basic_info = "✅ VIN decoded successfully\n\n"
                if isinstance(data, dict) and "attributes" in data:
                    attrs = data["attributes"]
                    basic_info += f"VIN: {attrs.get('vin', 'N/A')}\n"
                    basic_info += f"Year: {attrs.get('year', 'N/A')}\n"
                    basic_info += f"Make: {attrs.get('make', 'N/A')}\n"
                    basic_info += f"Model: {attrs.get('model', 'N/A')}\n"
                    basic_info += f"Body: {attrs.get('body', 'N/A')}\n"
                    basic_info += f"Fuel Type: {attrs.get('fuel_type', 'N/A')}\n"
                    basic_info += f"Manufacturer: {attrs.get('manufacturer', 'N/A')}\n"
                    basic_info += f"Plant Country: {attrs.get('plant_country', 'N/A')}"
                await update.message.reply_text(basic_info)
        except:
            await update.message.reply_text("✅ VIN decoded but had trouble formatting the response.")


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

    # Store settings and shared client in bot_data
    carsxe_client = CarsXEClient(
        api_key=settings.carsxe_api_key,
        timeout_seconds=settings.http_timeout_seconds
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
    
    logger.info("Bot starting...")
    
    # Use run_polling which manages its own event loop
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


def main() -> None:
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


if __name__ == "__main__":
    main()

