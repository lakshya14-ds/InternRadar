"""Mongo-backed internship search service."""

from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import DESCENDING

from app.models.internship import InternshipInDB


class SearchService:
    """Build indexed MongoDB queries for internship search."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection

    async def search(
        self,
        title: str | None = None,
        company: str | None = None,
        location: str | None = None,
        category: str | None = None,
        source: str | None = None,
        remote: bool | None = None,
        posted_after: datetime | None = None,
        limit: int = 50,
    ) -> list[InternshipInDB]:
        """Search internships by indexed filters.

        All results are already India-only because the persistence layer
        enforces the country constraint at insert time.
        """

        query: dict[str, object] = {}

        if title:
            query["title"] = {"$regex": title, "$options": "i"}
        if company:
            query["company"] = {"$regex": company, "$options": "i"}
        if location:
            # Allow partial city/region match, e.g. "Bangalore", "NCR"
            query["location"] = {"$regex": location, "$options": "i"}
        if category:
            query["category"] = category
        if source:
            query["source"] = source
        if remote is not None:
            query["remote"] = remote
        if posted_after:
            query["posted_at"] = {"$gte": posted_after}

        cursor = self.collection.find(query).sort("posted_at", DESCENDING).limit(limit)
        return [InternshipInDB.model_validate(item) async for item in cursor]
