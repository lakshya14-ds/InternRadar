"""Lever ATS connector."""

from typing import Any

import asyncio
import logging

import httpx

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

# Lever company slugs.  Indian companies and global companies with India offices.
LEVER_COMPANY_SLUGS: list[str] = [
    # ── Indian-origin companies ─────────────────────────────────────────────
    "swiggy",            # Bangalore
    "zomato",            # Gurugram
    "ola",               # Bangalore
    "phonepe",           # Bangalore
    "paytm",             # Noida
    "nykaa",             # Mumbai
    "mamaearth",         # Gurugram
    "boat-lifestyle",    # Delhi
    "wakefit",           # Bangalore
    "nobroker",          # Bangalore
    "housing",           # Mumbai
    "magicbricks",       # Noida
    "99acres",           # Noida
    "sharechat",         # Bangalore
    "moj",               # Bangalore (ShareChat's short video)
    "inshorts",          # Noida
    "dailyhunt",         # Bangalore
    "vernacular-ai",     # Bangalore
    "sarvam-ai",         # Bangalore
    "krutrim",           # Bangalore
    "scaler",            # Bangalore
    "interviewbit",      # Bangalore
    "springworks",       # Bangalore (Freshworks HR spinoff)
    "juspay",            # Bangalore
    "epifi",             # fi.money — Bangalore
    "niyo",              # Bangalore
    "jupiter",           # Mumbai
    "freo",              # Bangalore
    "stashfin",          # Delhi
    "ixigo",             # Gurugram
    "ola-electric",      # Bangalore
    "pure-ev",           # Hyderabad
    "ather-energy",      # Bangalore
    "revolt-motors",     # Gurugram
    # ── Global companies with India presence ────────────────────────────────
    "netlify",
    "scaleai",
    "ramp",
    "notion",
    "airtable",
    "figma",
]


class LeverConnector(BaseConnector):
    """Retrieve internships from public Lever postings APIs."""

    source = "lever"

    def __init__(self, company_slugs: list[str] | None = None) -> None:
        self.company_slugs = company_slugs or LEVER_COMPANY_SLUGS

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Return configured Lever company slugs."""

        return [{"name": slug.replace("-", " ").title(), "slug": slug} for slug in self.company_slugs]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fetch Lever postings."""

        async def fetch_company(client: httpx.AsyncClient, company: dict[str, Any]) -> list[dict[str, Any]]:
            slug = company["slug"]
            try:
                response = await asyncio.wait_for(
                    client.get(
                        f"https://api.lever.co/v0/postings/{slug}",
                        params={"mode": "json"},
                    ),
                    timeout=3.0
                )
                response.raise_for_status()
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                logger.debug("Lever company skipped: %s (%s)", slug, exc)
                return []

            jobs = response.json()
            for job in jobs:
                job["company_name"] = company["name"]
            return jobs

        timeout = httpx.Timeout(3.0)
        limits = httpx.Limits(max_keepalive_connections=50, max_connections=150)
        async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
            results = await asyncio.gather(
                *(fetch_company(client, company) for company in companies),
                return_exceptions=True,
            )

        jobs: list[dict[str, Any]] = []
        for result in results:
            if isinstance(result, Exception):
                logger.debug("Lever company fetch failed: %s", result)
                continue
            jobs.extend(result)
        return jobs

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize Lever jobs — India locations, internships only."""

        internships: list[InternshipCreate] = []
        for job in raw_jobs:
            title = job.get("text", "")
            description = job.get("descriptionPlain", "") or job.get("description", "")

            if not self.is_internship(title, description):
                continue

            categories = job.get("categories", {})
            location = categories.get("location", "")

            if not self.is_india_location(location):
                continue

            internships.append(
                self.build_internship(
                    external_id=job.get("id", ""),
                    company=job.get("company_name", ""),
                    title=title,
                    location=location,
                    url=job.get("hostedUrl", "") or job.get("applyUrl", ""),
                    description=description,
                    tags=["ats", "lever"],
                )
            )
        return internships
