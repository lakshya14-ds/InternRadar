"""Notification engine that fans out to enabled providers."""

import logging

from app.config import Settings
from app.models.internship import InternshipInDB
from app.notifications.providers.discord_provider import DiscordProvider
from app.notifications.providers.email_provider import EmailProvider
from app.notifications.providers.telegram_provider import TelegramProvider
from app.notifications.providers.whatsapp_provider import WhatsAppProvider

logger = logging.getLogger(__name__)


class NotificationEngine:
    def __init__(self, settings: Settings) -> None:
        self.providers = [
            TelegramProvider(settings.bot_token, settings.chat_id),
            EmailProvider(
                settings.smtp_host, settings.smtp_port,
                settings.smtp_username, settings.smtp_password,
                settings.email_from, settings.email_to,
            ),
            DiscordProvider(settings.discord_webhook_url),
            WhatsAppProvider(
                settings.twilio_account_sid, settings.twilio_auth_token,
                settings.twilio_whatsapp_from, settings.twilio_whatsapp_to,
            ),
        ]

    async def send_new_internship_alert(self, internship: InternshipInDB) -> None:
        for provider in self.providers:
            try:
                await provider.send(internship)
            except Exception:
                logger.exception("%s provider failed", provider.__class__.__name__)
