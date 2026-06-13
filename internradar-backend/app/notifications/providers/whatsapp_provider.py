"""WhatsApp notification provider skeleton for Twilio."""

import logging

from app.models.internship import InternshipInDB
from app.notifications.providers.base import NotificationProvider

logger = logging.getLogger(__name__)


class WhatsAppProvider(NotificationProvider):
    def __init__(self, account_sid, auth_token, from_number, to_number) -> None:
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.to_number = to_number

    async def send(self, internship: InternshipInDB) -> None:
        if not all([self.account_sid, self.auth_token, self.from_number, self.to_number]):
            logger.info("WhatsApp is not configured; skipping")
            return
        logger.info("WhatsApp provider: Twilio skeleton invoked for %s", internship.id)
