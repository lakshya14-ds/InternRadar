"""Tests for fingerprint and deduplication helpers."""

import pytest

from app.models.internship import InternshipCreate
from app.utils.deduplication import (
    fingerprint_for_internship,
    generate_fingerprint,
    internship_exists,
)


def test_generate_fingerprint_is_stable_and_case_insensitive() -> None:
    first = generate_fingerprint("Google", "Data Analyst Intern", "Bangalore")
    second = generate_fingerprint(" google ", "data analyst intern", "bangalore")
    assert first == second
    assert len(first) == 64


def test_fingerprint_for_internship_uses_core_identity_fields() -> None:
    internship = InternshipCreate(
        external_id="google-1",
        source="google",
        company="Google",
        title="Software Engineering Intern",
        location="Bangalore, India",
        url="https://example.com/job",
        description="One description",
    )
    expected = generate_fingerprint("Google", "Software Engineering Intern", "Bangalore, India", "google")
    assert fingerprint_for_internship(internship) == expected


class FakeCollection:
    def __init__(self, exists: bool) -> None:
        self.exists = exists

    async def find_one(self, query: dict, projection: dict) -> dict | None:
        return {"_id": "abc"} if self.exists else None


@pytest.mark.asyncio
async def test_internship_exists_true() -> None:
    assert await internship_exists(FakeCollection(True), "fingerprint") is True


@pytest.mark.asyncio
async def test_internship_exists_false() -> None:
    assert await internship_exists(FakeCollection(False), "fingerprint") is False
