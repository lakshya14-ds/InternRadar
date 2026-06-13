"""Discover and persist companies using ATS providers."""

from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError


class CompanyDiscovery:
    """Persist discovered ATS company boards."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection

    async def store_discovered_companies(self, companies: list[dict[str, Any]]) -> int:
        inserted = 0
        for company in companies:
            document = {
                "name": company["name"],
                "ats_provider": company["ats_provider"],
                "careers_url": company["careers_url"],
                "active": company.get("active", True),
                "last_checked": datetime.now(UTC),
            }
            try:
                await self.collection.insert_one(document)
                inserted += 1
            except DuplicateKeyError:
                continue
        return inserted

    async def list_companies(self) -> list[dict[str, Any]]:
        return [company async for company in self.collection.find({"active": True})]
