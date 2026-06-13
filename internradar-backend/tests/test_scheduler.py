"""Tests for scheduler aggregation workflow."""

from collections.abc import AsyncIterator
from typing import Any

import pytest

from app.models.internship import InternshipCreate
from app.scheduler.scheduler import InternshipScheduler


class FakeSettings:
    scraper_interval_minutes = 30
    bot_token = None
    chat_id = None
    smtp_host = None
    smtp_port = 587
    smtp_username = None
    smtp_password = None
    email_from = None
    email_to = None
    discord_webhook_url = None
    twilio_account_sid = None
    twilio_auth_token = None
    twilio_whatsapp_from = None
    twilio_whatsapp_to = None


class FakeIndiaConnector:
    """Returns one India-based internship."""

    async def run(self) -> list[InternshipCreate]:
        return [
            InternshipCreate(
                external_id="1",
                source="lever",
                company="Swiggy",
                title="Software Engineering Intern",
                location="Bangalore, India",
                remote=False,
                url="https://example.com",
            )
        ]


class FakeNonIndiaConnector:
    """Returns one non-India internship — should be blocked by the service."""

    async def run(self) -> list[InternshipCreate]:
        return [
            InternshipCreate(
                external_id="2",
                source="lever",
                company="Stripe",
                title="Software Engineering Intern",
                location="San Francisco, CA",
                remote=False,
                url="https://stripe.com/job/2",
            )
        ]


class InsertResult:
    inserted_id = "1"


class FakeCollection:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []

    async def find_one(self, query: dict, projection: dict) -> dict | None:
        return None

    async def insert_one(self, document: dict) -> InsertResult:
        self.documents.append(dict(document))
        return InsertResult()

    def find(self, query: dict | None = None) -> AsyncIterator:
        raise NotImplementedError


@pytest.mark.asyncio
async def test_scheduler_inserts_india_internships() -> None:
    collection = FakeCollection()
    scheduler = InternshipScheduler(FakeSettings(), collection)
    scheduler.connectors = [FakeIndiaConnector()]

    await scheduler.run_once()

    assert len(collection.documents) == 1
    assert collection.documents[0]["company"] == "Swiggy"
    assert collection.documents[0]["category"] == "Software Engineering"


@pytest.mark.asyncio
async def test_scheduler_blocks_non_india_internships() -> None:
    collection = FakeCollection()
    scheduler = InternshipScheduler(FakeSettings(), collection)
    scheduler.connectors = [FakeNonIndiaConnector()]

    await scheduler.run_once()

    # Non-India internship must be rejected at the service layer
    assert len(collection.documents) == 0


@pytest.mark.asyncio
async def test_scheduler_mixed_connectors() -> None:
    """Only the India internship should be persisted when both connectors run."""
    collection = FakeCollection()
    scheduler = InternshipScheduler(FakeSettings(), collection)
    scheduler.connectors = [FakeIndiaConnector(), FakeNonIndiaConnector()]

    await scheduler.run_once()

    assert len(collection.documents) == 1
    assert collection.documents[0]["location"] == "Bangalore, India"
