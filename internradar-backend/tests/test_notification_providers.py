"""Tests for notification providers."""

import pytest

from app.models.internship import InternshipInDB
from app.notifications.providers.telegram_provider import TelegramProvider
from app.notifications.providers.discord_provider import DiscordProvider
from app.notifications.providers.whatsapp_provider import WhatsAppProvider


def make_internship() -> InternshipInDB:
    return InternshipInDB(
        external_id="1",
        source="greenhouse",
        company="Razorpay",
        title="Software Engineering Intern",
        location="Bangalore, India",
        remote=False,
        url="https://example.com",
        fingerprint="abc",
    )


@pytest.mark.asyncio
async def test_telegram_provider_skips_when_unconfigured() -> None:
    await TelegramProvider(None, None).send(make_internship())


@pytest.mark.asyncio
async def test_discord_provider_skips_when_unconfigured() -> None:
    await DiscordProvider(None).send(make_internship())


@pytest.mark.asyncio
async def test_whatsapp_provider_skips_when_unconfigured() -> None:
    await WhatsAppProvider(None, None, None, None).send(make_internship())
