"""Business logic for storing and retrieving internships."""

import re
from datetime import UTC, datetime
import logging

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import DESCENDING
from pymongo.errors import DuplicateKeyError

from app.classification.internship_classifier import InternshipClassifier
from app.connectors.base_connector import INDIA_LOCATION_TOKENS
from app.models.internship import InternshipCreate, InternshipInDB
from app.utils.deduplication import fingerprint_for_internship

logger = logging.getLogger(__name__)


def _is_india_location(location: str) -> bool:
    """Return True when the location resolves to India.

    Mirrors BaseConnector.is_india_location so the service has no dependency
    on a concrete connector instance.
    """
    if not location:
        return False
    loc = location.casefold().strip()
    for token in INDIA_LOCATION_TOKENS:
        pattern = r"(^|[\s,/\-])" + re.escape(token) + r"($|[\s,/\-])"
        if re.search(pattern, loc):
            return True
    return False


class InternshipService:
    """Service for internship persistence and lookup."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection
        self.classifier = InternshipClassifier()

    async def insert_if_new(self, internship: InternshipCreate) -> InternshipInDB | None:
        """Insert an internship only when it is from India and not a duplicate."""

        # Safety net: India-only
        if not _is_india_location(internship.location):
            logger.debug(
                "Skipping non-India internship: company=%s title=%s location=%s",
                internship.company,
                internship.title,
                internship.location,
            )
            return None

        # Deduplication
        fingerprint = fingerprint_for_internship(internship)
        document = internship.model_dump()
        document["fingerprint"] = fingerprint
        document["scraped_at"] = datetime.now(UTC)
        document["category"] = internship.category or self.classifier.classify(internship)

        if hasattr(self.collection, "update_one"):
            try:
                result = await self.collection.update_one(
                    {"fingerprint": fingerprint},
                    {"$setOnInsert": document},
                    upsert=True,
                )
            except DuplicateKeyError:
                return None

            if result.upserted_id is None:
                return None

            document["_id"] = result.upserted_id
            return InternshipInDB.model_validate(document)

        # Test fakes may not implement Mongo's atomic upsert API.
        existing = await self.collection.find_one({"fingerprint": fingerprint}, {"_id": 1})
        if existing is not None:
            return None

        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return InternshipInDB.model_validate(document)

    async def list_internships(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict | None = None,
    ) -> list[InternshipInDB]:
        skip = max(page - 1, 0) * page_size
        cursor = (
            self.collection.find(filters or {})
            .sort("posted_at", DESCENDING)
            .skip(skip)
            .limit(page_size)
        )
        return [InternshipInDB.model_validate(item) async for item in cursor]

    async def latest(self, limit: int = 50) -> list[InternshipInDB]:
        cursor = self.collection.find().sort("posted_at", DESCENDING).limit(limit)
        return [InternshipInDB.model_validate(item) async for item in cursor]

    async def by_company(self, company: str) -> list[InternshipInDB]:
        cursor = (
            self.collection.find({"company": {"$regex": f"^{company}$", "$options": "i"}})
            .sort("posted_at", DESCENDING)
        )
        return [InternshipInDB.model_validate(item) async for item in cursor]

    async def by_category(self, category: str) -> list[InternshipInDB]:
        cursor = self.collection.find({"category": category}).sort("posted_at", DESCENDING)
        return [InternshipInDB.model_validate(item) async for item in cursor]

    async def remote(self) -> list[InternshipInDB]:
        cursor = self.collection.find({"remote": True}).sort("posted_at", DESCENDING)
        return [InternshipInDB.model_validate(item) async for item in cursor]

    async def by_location(self, location: str) -> list[InternshipInDB]:
        cursor = (
            self.collection.find({"location": {"$regex": location, "$options": "i"}})
            .sort("posted_at", DESCENDING)
        )
        return [InternshipInDB.model_validate(item) async for item in cursor]

    async def by_source(self, source: str) -> list[InternshipInDB]:
        cursor = self.collection.find({"source": source}).sort("posted_at", DESCENDING)
        return [InternshipInDB.model_validate(item) async for item in cursor]
