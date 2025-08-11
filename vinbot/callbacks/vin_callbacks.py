"""VIN-related callback handlers."""

import logging
from telegram import CallbackQuery
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from .base import CallbackStrategy

logger = logging.getLogger(__name__)


class DecodeVinCallback(CallbackStrategy):
    """Handle VIN decoding from history/saved."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data.startswith("decode_vin:") or callback_data.startswith("sample_vin:")
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Decode a VIN."""
        if data.startswith("decode_vin:"):
            vin = data.replace("decode_vin:", "")
        else:  # sample_vin
            vin = data.replace("sample_vin:", "")
        
        # Import here to avoid circular dependency
        from ..bot import handle_vin_decode
        await handle_vin_decode(query, context, vin, from_callback=True)


class ShowLevelCallback(CallbackStrategy):
    """Handle information level selection for VIN display."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data.startswith("show_level:")
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Show VIN at specific information level."""
        parts = data.split(":")
        if len(parts) >= 3:
            level = parts[1]
            vin = parts[2]
            
            # Track level change for user learning
            user_id = query.from_user.id if query.from_user else None
            user_context_mgr = context.bot_data.get("user_context_manager")
            
            if user_context_mgr and user_id:
                # Get current level from context or assume STANDARD
                current_level_value = context.user_data.get(f"current_level_{vin}", 2)
                try:
                    from ..smart_formatter import InformationLevel
                    current_level = InformationLevel(current_level_value)
                    new_level = InformationLevel(int(level))
                    await user_context_mgr.track_level_change(user_id, current_level, new_level)
                    
                    # Store new level in context
                    context.user_data[f"current_level_{vin}"] = int(level)
                except (ValueError, TypeError):
                    pass
            
            # Re-decode with specific level
            from ..bot import handle_vin_decode
            await handle_vin_decode(query, context, vin, from_callback=True, requested_level=level)


class ShareVinCallback(CallbackStrategy):
    """Handle VIN sharing functionality."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data.startswith("share_vin:")
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Share a VIN."""
        vin = data.replace("share_vin:", "")
        
        # Track action for user learning
        user_id = query.from_user.id if query.from_user else None
        user_context_mgr = context.bot_data.get("user_context_manager")
        
        if user_context_mgr and user_id:
            await user_context_mgr.track_action(user_id, "share_vin")
        
        await query.message.reply_text(
            f"📤 **Share this VIN:**\n\n"
            f"`{vin}`\n\n"
            f"_Copy the VIN above and share it with others!_",
            parse_mode=ParseMode.MARKDOWN
        )


class CompareVinCallback(CallbackStrategy):
    """Handle VIN comparison functionality."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data.startswith("compare_start:")
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Start VIN comparison."""
        vin = data.replace("compare_start:", "")
        
        # Track action for user learning
        user_id = query.from_user.id if query.from_user else None
        user_context_mgr = context.bot_data.get("user_context_manager")
        
        if user_context_mgr and user_id:
            await user_context_mgr.track_action(user_id, "compare_start")
        
        await query.message.reply_text(
            f"📊 **VIN Comparison**\n\n"
            f"First VIN: `{vin}`\n\n"
            f"Please send me a second 17-character VIN to compare with this vehicle.",
            parse_mode=ParseMode.MARKDOWN
        )


class RefreshVinCallback(CallbackStrategy):
    """Handle VIN data refresh."""
    
    async def can_handle(self, callback_data: str) -> bool:
        return callback_data.startswith("refresh:")
    
    async def handle(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
        """Refresh VIN data."""
        vin = data.replace("refresh:", "")
        
        # Import here to avoid circular dependency
        from ..bot import get_user_decoder
        from ..nhtsa_client import NHTSAError
        from ..formatter import format_vehicle_summary
        from ..keyboards import get_details_keyboard
        
        client = await get_user_decoder(context, query.from_user.id)
        
        # Send loading message
        await query.message.edit_text(
            f"🔄 Refreshing data for VIN: `{vin}`\n\nPlease wait...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Clear cache for this VIN if cache exists
            if hasattr(client, 'cache') and client.cache:
                cache_key = f"vin:{client.service_name.lower()}:{vin.upper()}"
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