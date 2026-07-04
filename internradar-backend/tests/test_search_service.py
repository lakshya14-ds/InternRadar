"""Tests for internship search service."""

from collections.abc import AsyncIterator
from typing import Any

import pytest

from app.search.search_service import SearchService


class FakeCursor:
    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self.documents = documents

    def sort(self, *args: Any) -> "FakeCursor":
        return self

    def limit(self, count: int) -> "FakeCursor":
        self.documents = self.documents[:count]
        return self

    def skip(self, count: int) -> "FakeCursor":
        self.documents = self.documents[count:]
        return self

    def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        async def iterator() -> AsyncIterator[dict[str, Any]]:
            for document in self.documents:
                yield document
        return iterator()


class FakeCollection:
    def __init__(self) -> None:
        self.query: dict[str, Any] | None = None

    def find(self, query: dict[str, Any], projection: dict[str, Any] | None = None) -> FakeCursor:
        self.query = query
        return FakeCursor([
            {
                "_id": "1",
                "external_id": "1",
                "source": "lever",
                "company": "Swiggy",
                "title": "Data Analyst Intern",
                "location": "Bangalore, India",
                "remote": False,
                "employment_type": "Internship",
                "url": "https://example.com",
                "description": "",
                "skills": [],
                "tags": [],
                "category": "Data Analytics",
                "fingerprint": "abc",
            }
        ])

    async def count_documents(self, query: dict[str, Any]) -> int:
        return 1


@pytest.mark.asyncio
async def test_search_builds_filters() -> None:
    collection = FakeCollection()
    results, total = await SearchService(collection).search(company="Swiggy", remote=False)  # type: ignore

    assert len(results) == 1
    assert total == 1
    assert collection.query == {
        "company": {"$regex": "Swiggy", "$options": "i"},
        "remote": False,
    }


@pytest.mark.asyncio
async def test_search_with_location_filter() -> None:
    collection = FakeCollection()
    await SearchService(collection).search(location="Bangalore")  # type: ignore

    assert collection.query == {"location": {"$regex": "Bangalore", "$options": "i"}}


@pytest.mark.asyncio
async def test_search_with_no_filters() -> None:
    collection = FakeCollection()
    results, total = await SearchService(collection).search()  # type: ignore

    assert len(results) == 1
    assert total == 1
    assert collection.query == {}
