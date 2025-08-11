"""Telegram bot client implementation."""

from telegram import Bot
from telegram.ext import ApplicationBuilder
from typing import Optional


class TelegramBotClient:
    """Telegram bot client for interacting with the Telegram API."""
    
    def __init__(self, token: str):
        """Initialize the Telegram bot client.
        
        Args:
            token: Telegram bot token
        """
        self.token = token
        self.bot: Optional[Bot] = None
    
    async def initialize(self) -> None:
        """Initialize the bot client."""
        application = ApplicationBuilder().token(self.token).build()
        self.bot = application.bot
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Any] = None
    ) -> None:
        """Send a message to a chat.
        
        Args:
            chat_id: The chat ID
            text: The message text
            parse_mode: The parse mode (e.g., "Markdown")
            reply_markup: Inline keyboard markup
        """
        if not self.bot:
            raise RuntimeError("Bot not initialized")
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    
    async def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[Any] = None
    ) -> None:
        """Edit a message's text.
        
        Args:
            chat_id: The chat ID
            message_id: The message ID
            text: The new message text
            parse_mode: The parse mode (e.g., "Markdown")
            reply_markup: Inline keyboard markup
        """
        if not self.bot:
            raise RuntimeError("Bot not initialized")
        
        await self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )