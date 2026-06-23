"""SMTP email notification provider."""

import asyncio
from email.message import EmailMessage
import logging
import smtplib

from app.models.internship import InternshipInDB
from app.notifications.providers.base import NotificationProvider

logger = logging.getLogger(__name__)


class EmailProvider(NotificationProvider):
    def __init__(self, host, port, username, password, from_email, to_email) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_email = to_email

    async def send(self, internship: InternshipInDB) -> None:
        if not all([self.host, self.from_email, self.to_email]):
            logger.info("Email is not configured; skipping")
            return
        message = EmailMessage()
        message["Subject"] = f"[InternRadar India] {internship.title} at {internship.company}"
        message["From"] = self.from_email
        message["To"] = self.to_email
        message.set_content(
            f"Company: {internship.company}\n"
            f"Role: {internship.title}\n"
            f"Location: {internship.location}\n"
            f"Category: {internship.category or 'Other'}\n"
            f"Source: {internship.source}\n"
            f"Apply: {internship.url}\n"
        )
        try:
            await asyncio.to_thread(self._send_message, message)
        except OSError:
            logger.exception("Email notification failed")

    def _send_message(self, message: EmailMessage) -> None:
        with smtplib.SMTP(self.host, self.port, timeout=5) as smtp:
            smtp.starttls()
            if self.username and self.password:
                smtp.login(self.username, self.password)
            smtp.send_message(message)
