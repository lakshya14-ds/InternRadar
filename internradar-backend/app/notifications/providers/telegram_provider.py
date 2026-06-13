"""Telegram notification provider."""

import logging

from telegram import Bot
from telegram.error import TelegramError

from app.models.internship import InternshipInDB
from app.notifications.providers.base import NotificationProvider

logger = logging.getLogger(__name__)


class TelegramProvider(NotificationProvider):
    def __init__(self, bot_token: str | None, chat_id: str | None) -> None:
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token) if bot_token else None

    async def send(self, internship: InternshipInDB) -> None:
        if self.bot is None or not self.chat_id:
            logger.info("Telegram is not configured; skipping")
            return
        message = (
            "🚀 New India Internship Found\n\n"
            f"Company: {internship.company}\n\n"
            f"Role: {internship.title}\n\n"
            f"Location: {internship.location}\n\n"
            f"Category: {internship.category or 'Other'}\n\n"
            f"Source: {internship.source}\n\n"
            "Apply Here:\n"
            f"{internship.url}"
        )
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
        except TelegramError:
            logger.exception("Telegram notification failed")
