"""Deduplication helpers for internship records."""

import hashlib
import re
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from motor.motor_asyncio import AsyncIOMotorCollection

from app.models.internship import InternshipCreate


def clean_url(url: str) -> str:
    """Strip tracking parameters from the URL."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        qsl = parse_qsl(parsed.query)
        # Filter out common tracking query params
        filtered = [
            (k, v) for k, v in qsl
            if not k.lower().startswith("utm_") and k.lower() not in [
                "fbclid", "gclid", "sessionid", "sid", "affiliate", "ref"
            ]
        ]
        new_query = urlencode(filtered)
        return urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    except Exception:
        return url


def extract_city(location: str) -> str:
    """Extract primary city/metropolitan hub from location string."""
    if not location:
        return "remote"
    loc = location.lower()
    cities = [
        "bangalore", "bengaluru", "mumbai", "pune", "delhi", "noida", 
        "gurgaon", "gurugram", "ncr", "hyderabad", "chennai", "kolkata"
    ]
    for city in cities:
        if city in loc:
            return city
    if "remote" in loc:
        return "remote"
    # Fallback to the first section of the location string
    return location.strip().split(",")[0].strip().lower()


def generate_fingerprint(company: str, title: str, location: str, url: str) -> str:
    """Create a stable SHA256 fingerprint for an internship using cleaned fields."""
    norm_company = re.sub(r"\s+", "", company.strip().casefold())
    norm_title = re.sub(r"\s+", "", title.strip().casefold())
    city = extract_city(location)
    cleaned_url = clean_url(url).strip().casefold()

    canonical = "|".join([norm_company, norm_title, city, cleaned_url])
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def fingerprint_for_internship(internship: InternshipCreate) -> str:
    """Create a fingerprint from normalized internship data."""
    return generate_fingerprint(
        internship.company,
        internship.title,
        internship.location,
        internship.url,
    )


async def internship_exists(
    collection: AsyncIOMotorCollection,
    fingerprint: str,
) -> bool:
    """Return whether an internship fingerprint already exists."""
    document = await collection.find_one({"fingerprint": fingerprint}, {"_id": 1})
    return document is not None

