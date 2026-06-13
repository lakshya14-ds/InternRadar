"""Deduplication helpers for internship records."""

import hashlib

from motor.motor_asyncio import AsyncIOMotorCollection

from app.models.internship import InternshipCreate


def generate_fingerprint(company: str, title: str, location: str, source: str = "") -> str:
    """Create a stable SHA256 fingerprint for an internship."""

    canonical = "|".join(
        part.strip().casefold() for part in (company, title, location, source)
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def fingerprint_for_internship(internship: InternshipCreate) -> str:
    """Create a fingerprint from normalized internship data."""

    return generate_fingerprint(
        internship.company,
        internship.title,
        internship.location,
        internship.source,
    )


async def internship_exists(
    collection: AsyncIOMotorCollection,
    fingerprint: str,
) -> bool:
    """Return whether an internship fingerprint already exists."""

    document = await collection.find_one({"fingerprint": fingerprint}, {"_id": 1})
    return document is not None
