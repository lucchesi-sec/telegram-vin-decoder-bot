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
from .formatter_extensions import (
    format_market_value,
    format_history,
)
from .keyboards import (
    get_details_keyboard,
    get_actions_keyboard,
    get_recent_vins_keyboard,
    get_saved_vins_keyboard,
    get_sample_vin_keyboard,
    get_comparison_keyboard,
    get_confirmation_keyboard,
    get_close_button,
    get_settings_keyboard,
    get_service_info_keyboard,
    get_api_key_prompt_keyboard
)
from .user_data import UserDataManager
from .vin import is_valid_vin, normalize_vin


logger = logging.getLogger(__name__)


WELCOME_TEXT = (
    "🚗 **Welcome to VIN Decoder Bot!**\n\n"
    "I can decode Vehicle Identification Numbers (VINs) using the official NHTSA database or Auto.dev.\n\n"
    "**How to use:**\n"
    "• Send me a 17-character VIN directly\n"
    "• Use /vin <VIN> command\n"
    "• Try the sample VIN below\n\n"
    "**Commands:**\n"
    "/vin <VIN> — Decode a VIN\n"
    "/recent — View recent searches\n"
    "/saved — View saved vehicles\n"
    "/settings — Configure your preferences\n"
    "/help — Show this help message\n\n"
    "_VIN Format: 17 characters (letters & numbers)_\n"
    "_Invalid characters: I, O, Q_\n"
    "_Data provided by NHTSA or Auto.dev_"
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


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user settings for service selection and API key management"""
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    user_id = update.effective_user.id if update.effective_user else None
    
    if not user_data_mgr or not user_id:
        await update.message.reply_text("Settings are not available.")
        return
    
    # Get user settings
    settings = await user_data_mgr.get_user_settings(user_id)
    current_service = settings.get("service", "NHTSA")
    has_autodev_key = bool(settings.get("autodev_api_key"))
    
    # Create settings keyboard
    from .keyboards import get_settings_keyboard
    keyboard = get_settings_keyboard(
        current_service=current_service,
        has_autodev_key=has_autodev_key
    )
    
    # Service descriptions
    service_desc = {
        "NHTSA": "✅ Using NHTSA (Free, no API key required)",
        "AutoDev": "🔄 Using Auto.dev (Requires API key)"
    }
    
    current_desc = service_desc.get(current_service, "NHTSA (Free)")
    
    text = (
        "⚙️ **Settings**\n\n"
        f"**Current Service:** {current_desc}\n\n"
        "Select a service below to change your preference. "
        "Auto.dev provides more detailed vehicle information but requires an API key.\n\n"
        "NHTSA is completely free and provides basic vehicle information."
    )
    
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
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
    user_id = update.effective_user.id if update.effective_user else None
    
    # Check if we're waiting for an API key
    if context.user_data.get("awaiting_api_key_for"):
        service = context.user_data["awaiting_api_key_for"]
        is_update = context.user_data.get("api_key_update", False)
        
        # Clear the state
        del context.user_data["awaiting_api_key_for"]
        if "api_key_update" in context.user_data:
            del context.user_data["api_key_update"]
        
        # Validate and save the API key
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        if user_data_mgr and user_id:
            # For Auto.dev, validate the key format
            is_valid = True
            if service == "AutoDev":
                from .autodev_client import AutoDevClient
                client = AutoDevClient(api_key=text)
                is_valid = client.validate_api_key(text)
            
            if is_valid:
                await user_data_mgr.set_user_api_key(user_id, service, text)
                
                # If this is a new key for the current service, update the service
                if not is_update:
                    settings = await user_data_mgr.get_user_settings(user_id)
                    current_service = settings.get("service", "NHTSA")
                    if current_service == service:
                        # Already using this service, just confirm the key was set
                        pass
                    else:
                        # Switch to this service
                        await user_data_mgr.set_user_service(user_id, service)
                
                service_name = "Auto.dev" if service == "AutoDev" else service
                await update.message.reply_text(
                    f"✅ API key for {service_name} has been saved successfully!\n\n"
                    f"You are now using {service_name} for VIN decoding."
                )
                
                # Show updated settings
                await show_settings_menu(update, context)
            else:
                service_name = "Auto.dev" if service == "AutoDev" else service
                await update.message.reply_text(
                    f"❌ Invalid {service_name} API key format.\n\n"
                    "Please check your key and try again, or contact support if you believe this is an error."
                )
                # Show settings again
                await show_settings_menu(update, context)
        return
    
    # Normal VIN handling
    if len(text) == 17 and is_valid_vin(text):
        await handle_vin_decode(update, context, normalize_vin(text))
    else:
        await update.message.reply_text(
            "I expected a 17-character VIN. Use /vin <VIN> or send the VIN directly."
        )


async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the settings menu"""
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    user_id = update.effective_user.id if update.effective_user else None
    
    if not user_data_mgr or not user_id:
        # Fallback message
        await update.message.reply_text("Settings are not available.")
        return
    
    # Get user settings
    settings = await user_data_mgr.get_user_settings(user_id)
    current_service = settings.get("service", "NHTSA")
    has_autodev_key = bool(settings.get("autodev_api_key"))
    
    # Create settings keyboard
    from .keyboards import get_settings_keyboard
    keyboard = get_settings_keyboard(
        current_service=current_service,
        has_autodev_key=has_autodev_key
    )
    
    # Service descriptions
    service_desc = {
        "NHTSA": "✅ Using NHTSA (Free, no API key required)",
        "AutoDev": "🔄 Using Auto.dev (Requires API key)"
    }
    
    current_desc = service_desc.get(current_service, "NHTSA (Free)")
    
    text = (
        "⚙️ **Settings**\\n\\n"
        f"**Current Service:** {current_desc}\\n\\n"
        "Select a service below to change your preference. "
        "Auto.dev provides more detailed vehicle information but requires an API key.\\n\\n"
        "NHTSA is completely free and provides basic vehicle information."
    )
    
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
    """Get the user's preferred VIN decoder based on their settings
    
    Args:
        context: Bot context
        user_id: User ID
        
    Returns:
        VIN decoder instance based on user's preference
    """
    # Get user data manager
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    
    # Get user settings
    user_settings = {}
    if user_data_mgr and user_id:
        user_settings = await user_data_mgr.get_user_settings(user_id)
    
    # Determine which service to use
    service = user_settings.get("service", "NHTSA")  # Default to NHTSA
    
    # Initialize the appropriate client based on user preference
    if service == "AutoDev":
        # Check if user has an Auto.dev API key
        api_key = user_settings.get("autodev_api_key")
        if api_key:
            # Create Auto.dev client with user's API key
            cache = context.bot_data.get("cache")
            if f"autodev_client_{user_id}" not in context.user_data:
                context.user_data[f"autodev_client_{user_id}"] = AutoDevClient(
                    api_key=api_key, cache=cache
                )
            return context.user_data[f"autodev_client_{user_id}"]
        else:
            # Fall back to NHTSA if no API key is set
            service = "NHTSA"
    
    # For NHTSA or fallback, use the shared NHTSA client
    if "nhtsa_client" not in context.bot_data:
        cache = context.bot_data.get("cache")
        context.bot_data["nhtsa_client"] = NHTSAClient(cache=cache)
    return context.bot_data["nhtsa_client"]


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
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    user_id = update.effective_user.id if update.effective_user else None
    
    # Get the appropriate decoder based on user settings
    client = await get_user_decoder(context, user_id)
    
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
        except NHTSAError as e:
            service_name = client.service_name if hasattr(client, 'service_name') else "VIN decoder"
            logger.error(f"{service_name} error for VIN {vin}: {e}")
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
        # Format the comprehensive summary view
        summary_text = format_vehicle_summary(data)
        
        # Check what additional data is available
        has_history = "history" in data and data["history"]
        has_marketvalue = "marketvalue" in data and data["marketvalue"]
        
        # Create inline keyboard with available options
        details_keyboard = get_details_keyboard(vin, has_history=has_history, has_marketvalue=has_marketvalue)
        
        # Send the summary with inline keyboard
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
    
    elif data.startswith("share_vin:"):
        # Handle share VIN functionality
        vin = data.replace("share_vin:", "")
        await query.message.reply_text(
            f"📤 **Share this VIN:**\n\n"
            f"`{vin}`\n\n"
            f"_Copy the VIN above and share it with others!_",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data.startswith("compare_start:"):
        # Handle comparison functionality
        vin = data.replace("compare_start:", "")
        await query.message.reply_text(
            f"📊 **VIN Comparison**\n\n"
            f"First VIN: `{vin}`\n\n"
            f"Please send me a second 17-character VIN to compare with this vehicle.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data.startswith("show_marketvalue:"):
        # Show market value data
        vin = data.replace("show_marketvalue:", "")
        await show_market_value(query, context, vin)
    
    elif data.startswith("show_history:"):
        # Show history data
        vin = data.replace("show_history:", "")
        await show_history(query, context, vin)
    
    elif data.startswith("refresh:"):
        # Refresh VIN data
        vin = data.replace("refresh:", "")
        await refresh_vin_data(query, context, vin)
    
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
    
    # Settings-related callbacks
    elif data == "show_settings":
        # Show settings menu
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        user_id = update.effective_user.id if update.effective_user else None
        
        if user_data_mgr and user_id:
            settings = await user_data_mgr.get_user_settings(user_id)
            current_service = settings.get("service", "NHTSA")
            has_autodev_key = bool(settings.get("autodev_api_key"))
            
            from .keyboards import get_settings_keyboard
            keyboard = get_settings_keyboard(
                current_service=current_service,
                has_autodev_key=has_autodev_key
            )
            
            service_desc = {
                "NHTSA": "✅ Using NHTSA (Free, no API key required)",
                "AutoDev": "🔄 Using Auto.dev (Requires API key)"
            }
            
            current_desc = service_desc.get(current_service, "NHTSA (Free)")
            
            text = (
                "⚙️ **Settings**\n\n"
                f"**Current Service:** {current_desc}\n\n"
                "Select a service below to change your preference. "
                "Auto.dev provides more detailed vehicle information but requires an API key.\n\n"
                "NHTSA is completely free and provides basic vehicle information."
            )
            
            await query.message.edit_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
    
    elif data.startswith("set_service:"):
        # Set user's preferred service
        service = data.split(":")[1]
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        user_id = update.effective_user.id if update.effective_user else None
        
        if user_data_mgr and user_id:
            # Update user's service preference
            await user_data_mgr.set_user_service(user_id, service)
            
            # Get updated settings
            settings = await user_data_mgr.get_user_settings(user_id)
            current_service = settings.get("service", "NHTSA")
            has_autodev_key = bool(settings.get("autodev_api_key"))
            
            from .keyboards import get_settings_keyboard
            keyboard = get_settings_keyboard(
                current_service=current_service,
                has_autodev_key=has_autodev_key
            )
            
            service_desc = {
                "NHTSA": "✅ Using NHTSA (Free, no API key required)",
                "AutoDev": "🔄 Using Auto.dev (Requires API key)"
            }
            
            current_desc = service_desc.get(current_service, "NHTSA (Free)")
            
            text = (
                "⚙️ **Settings**\n\n"
                f"**Current Service:** {current_desc}\n\n"
                "Select a service below to change your preference. "
                "Auto.dev provides more detailed vehicle information but requires an API key.\n\n"
                "NHTSA is completely free and provides basic vehicle information."
            )
            
            await query.message.edit_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
    
    elif data.startswith("add_api_key:") or data.startswith("update_api_key:"):
        # Prompt user to enter API key
        service = data.split(":")[1]
        context.user_data["awaiting_api_key_for"] = service
        context.user_data["api_key_update"] = data.startswith("update_api_key:")
        
        service_name = "Auto.dev" if service == "AutoDev" else service
        
        await query.message.reply_text(
            f"🔑 **Enter your {service_name} API Key**\n\n"
            f"Please send your {service_name} API key in the next message.\n\n"
            "Note: Your API key will be stored securely and used only for VIN decoding requests.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_api_key_prompt_keyboard()
        )
    
    elif data.startswith("remove_api_key:"):
        # Remove API key for a service
        service = data.split(":")[1]
        user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
        user_id = update.effective_user.id if update.effective_user else None
        
        if user_data_mgr and user_id:
            # Clear the API key
            await user_data_mgr.clear_user_api_key(user_id, service)
            
            # If this was the current service, switch back to NHTSA
            settings = await user_data_mgr.get_user_settings(user_id)
            current_service = settings.get("service", "NHTSA")
            if current_service == service:
                await user_data_mgr.set_user_service(user_id, "NHTSA")
            
            # Show updated settings
            updated_settings = await user_data_mgr.get_user_settings(user_id)
            current_service = updated_settings.get("service", "NHTSA")
            has_autodev_key = bool(updated_settings.get("autodev_api_key"))
            
            from .keyboards import get_settings_keyboard
            keyboard = get_settings_keyboard(
                current_service=current_service,
                has_autodev_key=has_autodev_key
            )
            
            service_desc = {
                "NHTSA": "✅ Using NHTSA (Free, no API key required)",
                "AutoDev": "🔄 Using Auto.dev (Requires API key)"
            }
            
            current_desc = service_desc.get(current_service, "NHTSA (Free)")
            
            text = (
                "⚙️ **Settings**\n\n"
                f"**Current Service:** {current_desc}\n\n"
                "Select a service below to change your preference. "
                "Auto.dev provides more detailed vehicle information but requires an API key.\n\n"
                "NHTSA is completely free and provides basic vehicle information."
            )
            
            await query.message.edit_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
            
            # Notify user
            service_name = "Auto.dev" if service == "AutoDev" else service
            await query.message.reply_text(
                f"✅ API key for {service_name} has been removed."
            )
    
    elif data == "service_info":
        # Show service information
        text = (
            "ℹ️ **Service Information**\n\n"
            "**NHTSA (National Highway Traffic Safety Administration)**\n"
            "• Free service provided by the U.S. government\n"
            "• Basic vehicle information\n"
            "• No API key required\n"
            "• Data includes make, model, year, body type, etc.\n\n"
            "**Auto.dev**\n"
            "• Premium service with detailed vehicle data\n"
            "• Requires a paid API key\n"
            "• More comprehensive information including features, options, market value, etc.\n"
            "• Visit auto.dev to get an API key\n\n"
            "You can switch between services at any time in settings."
        )
        
        from .keyboards import get_service_info_keyboard
        keyboard = get_service_info_keyboard()
        
        await query.message.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
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
    if section == "all":
        text = format_vehicle_summary(data)
        # For "all" section, we don't need to show any more buttons
        keyboard = None
    else:
        # For other sections, we'll just show the "all" button
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
        else:
            text = "Unknown section requested."
        
        keyboard = get_details_keyboard(vin, [section])
    
    # Send as new message
    await query.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
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


async def show_market_value(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, vin: str) -> None:
    """Show market value information for a vehicle"""
    # Get stored vehicle data
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    data = None
    
    # Try to get from context first
    if f"vehicle_data_{vin}" in context.user_data:
        data = context.user_data[f"vehicle_data_{vin}"]
    elif user_data_mgr:
        data = await user_data_mgr.get_vehicle_data(vin)
    
    if not data:
        await query.message.reply_text("Vehicle data not found. Please decode the VIN again.")
        return
    
    # Format and send market value data
    text = format_market_value(data)
    await query.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN
    )


async def show_history(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, vin: str) -> None:
    """Show history information for a vehicle"""
    # Get stored vehicle data
    user_data_mgr: UserDataManager = context.bot_data.get("user_data_manager")
    data = None
    
    # Try to get from context first
    if f"vehicle_data_{vin}" in context.user_data:
        data = context.user_data[f"vehicle_data_{vin}"]
    elif user_data_mgr:
        data = await user_data_mgr.get_vehicle_data(vin)
    
    if not data:
        await query.message.reply_text("Vehicle data not found. Please decode the VIN again.")
        return
    
    # Format and send history data
    text = format_history(data)
    await query.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN
    )


async def refresh_vin_data(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, vin: str) -> None:
    """Refresh VIN data by fetching fresh from NHTSA API"""
    client = await get_user_decoder(context, query.from_user.id)
    
    # Send loading message
    await query.message.edit_text(
        f"🔄 Refreshing data for VIN: `{vin}`\n\nPlease wait...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Clear cache for this VIN if cache exists
        if hasattr(client, 'cache') and client.cache:
            cache_key = f"vin:{vin.upper()}"
            try:
                await client.cache.delete(cache_key)
            except:
                pass
        
        # Fetch fresh data
        data = await client.decode_vin(vin)
        
        # Store in context
        context.user_data[f"vehicle_data_{vin}"] = data
        
        # Format response
        text = format_vehicle_summary(data)
        
        # Create simple keyboard (NHTSA doesn't have history/market value)
        keyboard = get_details_keyboard(vin, has_history=False, has_marketvalue=False)
        
        # Send updated message
        await query.message.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
        
    except NHTSAError as e:
        await query.message.edit_text(f"❌ Error refreshing data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error refreshing VIN {vin}: {e}")
        await query.message.edit_text("❌ An unexpected error occurred. Please try again.")


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


async def setup_application():
    """Setup and return the application instance"""
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
    elif settings.redis_url:
        try:
            from .redis_cache import RedisCache
            cache = RedisCache(settings.redis_url, ttl=settings.redis_ttl_seconds)
            logger.info("Using Redis cache for user data")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
    
    # Initialize user data manager
    user_data_mgr = UserDataManager(cache=cache)
    
    # Create NHTSA client (doesn't require API key)
    nhtsa_client = NHTSAClient(cache=cache)
    
    application.bot_data["settings"] = settings
    application.bot_data["nhtsa_client"] = nhtsa_client
    application.bot_data["user_data_manager"] = user_data_mgr
    application.bot_data["cache"] = cache  # Store cache reference for cleanup

    # Register command handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("vin", cmd_vin))
    application.add_handler(CommandHandler("recent", cmd_recent))
    application.add_handler(CommandHandler("saved", cmd_saved))
    application.add_handler(CommandHandler("settings", cmd_settings))
    
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
    
    return application


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
    elif settings.redis_url:
        try:
            from .redis_cache import RedisCache
            cache = RedisCache(settings.redis_url, ttl=settings.redis_ttl_seconds)
            logger.info("Using Redis cache for user data")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
    
    # Initialize user data manager
    user_data_mgr = UserDataManager(cache=cache)
    
    # Create NHTSA client (doesn't require API key)
    nhtsa_client = NHTSAClient(cache=cache)
    
    application.bot_data["settings"] = settings
    application.bot_data["nhtsa_client"] = nhtsa_client
    application.bot_data["user_data_manager"] = user_data_mgr

    # Register command handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("vin", cmd_vin))
    application.add_handler(CommandHandler("recent", cmd_recent))
    application.add_handler(CommandHandler("saved", cmd_saved))
    application.add_handler(CommandHandler("settings", cmd_settings))
    
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

