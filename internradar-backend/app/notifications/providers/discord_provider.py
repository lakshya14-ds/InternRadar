"""Discord notification provider."""

import logging

import httpx

from app.models.internship import InternshipInDB
from app.notifications.providers.base import NotificationProvider

logger = logging.getLogger(__name__)


class DiscordProvider(NotificationProvider):
    def __init__(self, webhook_url: str | None) -> None:
        self.webhook_url = webhook_url

    async def send(self, internship: InternshipInDB) -> None:
        if not self.webhook_url:
            logger.info("Discord is not configured; skipping")
            return
        payload = {
            "content": (
                f"🇮🇳 **New India Internship** | **{internship.title}** at **{internship.company}**\n"
                f"📍 {internship.location} | 🏷️ {internship.category or 'Other'}\n"
                f"{internship.url}"
            )
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            response = await client.post(self.webhook_url, json=payload)
            response.raise_for_status()
