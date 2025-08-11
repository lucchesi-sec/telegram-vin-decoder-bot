"""Callback router for dispatching to appropriate handlers."""

import logging
from typing import List
from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

from .base import CallbackStrategy

logger = logging.getLogger(__name__)


class CallbackRouter:
    """Routes callback queries to appropriate handlers."""
    
    def __init__(self):
        """Initialize the router with empty strategy list."""
        self.strategies: List[CallbackStrategy] = []
    
    def register(self, strategy: CallbackStrategy) -> None:
        """Register a callback strategy.
        
        Args:
            strategy: The callback strategy to register
        """
        self.strategies.append(strategy)
        logger.debug(f"Registered callback strategy: {strategy.__class__.__name__}")
    
    async def route(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Route a callback query to the appropriate handler.
        
        Args:
            update: The update containing the callback query
            context: The bot context
        """
        query = update.callback_query
        if not query:
            return
        
        # Answer the callback to prevent timeout
        await query.answer()
        
        callback_data = query.data
        logger.debug(f"Routing callback: {callback_data}")
        
        # Find and execute the appropriate strategy
        for strategy in self.strategies:
            if await strategy.can_handle(callback_data):
                try:
                    await strategy.handle(query, context, callback_data)
                    logger.debug(f"Callback handled by {strategy.__class__.__name__}")
                    return
                except Exception as e:
                    logger.error(f"Error in {strategy.__class__.__name__}: {e}", exc_info=True)
                    await query.message.reply_text(
                        "❌ An error occurred processing your request. Please try again."
                    )
                    return
        
        # No handler found
        logger.warning(f"No handler found for callback: {callback_data}")
        await query.message.reply_text(
            "⚠️ This action is not recognized. Please try again."
        )