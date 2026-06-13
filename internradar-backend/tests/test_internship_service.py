"""Tests for internship persistence logic."""

from collections.abc import AsyncIterator
from typing import Any

import pytest
from bson import ObjectId

from app.models.internship import InternshipCreate
from app.services.internship_service import InternshipService


class InsertResult:
    def __init__(self, inserted_id: ObjectId) -> None:
        self.inserted_id = inserted_id


class FakeCursor:
    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self.documents = documents

    def sort(self, *args: Any) -> "FakeCursor":
        return self

    def skip(self, count: int) -> "FakeCursor":
        self.documents = self.documents[count:]
        return self

    def limit(self, count: int) -> "FakeCursor":
        self.documents = self.documents[:count]
        return self

    def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        async def iterator() -> AsyncIterator[dict[str, Any]]:
            for document in self.documents:
                yield document
        return iterator()


class FakeCollection:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []

    async def find_one(self, query: dict, projection: dict) -> dict | None:
        for doc in self.documents:
            if doc.get("fingerprint") == query.get("fingerprint"):
                return doc
        return None

    async def insert_one(self, document: dict) -> InsertResult:
        inserted = dict(document)
        inserted_id = ObjectId()
        inserted["_id"] = inserted_id
        self.documents.append(inserted)
        return InsertResult(inserted_id)

    def find(self, query: dict | None = None) -> FakeCursor:
        if not query:
            return FakeCursor(list(self.documents))
        company_query = query.get("company", {})
        expected = company_query.get("$regex", "").strip("^$")
        filtered = [
            doc for doc in self.documents
            if doc.get("company", "").casefold() == expected.casefold()
        ]
        return FakeCursor(filtered)


def build_internship(location: str = "Bangalore, India") -> InternshipCreate:
    return InternshipCreate(
        external_id="google-1",
        source="google",
        company="Google",
        title="Software Engineering Intern",
        location=location,
        url="https://example.com/job",
        description="Build things",
    )


@pytest.mark.asyncio
async def test_insert_if_new_inserts_once() -> None:
    collection = FakeCollection()
    service = InternshipService(collection)

    inserted = await service.insert_if_new(build_internship())
    duplicate = await service.insert_if_new(build_internship())

    assert inserted is not None
    assert inserted.company == "Google"
    assert duplicate is None
    assert len(collection.documents) == 1


@pytest.mark.asyncio
async def test_india_location_safety_net_blocks_non_india() -> None:
    """Service must reject non-India internships even if a connector passes them through."""
    collection = FakeCollection()
    service = InternshipService(collection)

    result = await service.insert_if_new(build_internship(location="San Francisco, CA"))

    assert result is None
    assert len(collection.documents) == 0


@pytest.mark.asyncio
async def test_india_location_safety_net_allows_india() -> None:
    collection = FakeCollection()
    service = InternshipService(collection)

    result = await service.insert_if_new(build_internship(location="Hyderabad, India"))

    assert result is not None
    assert len(collection.documents) == 1


@pytest.mark.asyncio
async def test_latest_returns_persisted_internships() -> None:
    collection = FakeCollection()
    service = InternshipService(collection)
    await service.insert_if_new(build_internship())

    latest = await service.latest()

    assert len(latest) == 1
    assert latest[0].title == "Software Engineering Intern"
