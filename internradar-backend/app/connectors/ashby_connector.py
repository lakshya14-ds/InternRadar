"""Ashby ATS connector."""

from typing import Any

import asyncio
import logging

import httpx

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

# Ashby organization slugs.
ASHBY_ORGANIZATION_SLUGS: list[str] = [
    # ── Indian-origin companies ─────────────────────────────────────────────
    "cred",              # Bangalore
    "zepto",             # Mumbai / Bangalore
    "rapido",            # Bangalore
    "Porter",            # Mumbai
    "locofast",          # Delhi
    "lenskart",          # Faridabad / Bangalore
    "purplle",           # Mumbai
    "simpl",             # Bangalore (BNPL)
    "smallcase",         # Bangalore
    "wint-wealth",       # Delhi
    "stoa",              # Bangalore
    "setu",              # Bangalore (API infra)
    "decentro",          # Bangalore
    "hyperface",         # Bangalore
    "hyperverge",        # Bangalore
    "pixxel",            # Bangalore (space tech)
    "agnikul",           # Chennai (space tech)
    "skyroot",           # Hyderabad (space tech)
    "ati-motors",        # Bangalore (autonomous vehicles)
    "uniphore",          # Chennai (conversational AI)
    "senseforth",        # Bangalore
    "vernacular-ai",     # Bangalore
    "sarvam",            # Bangalore
    "krutrim",           # Bangalore
    "eka-care",          # Bangalore (health tech)
    "mfine",             # Bangalore (health tech)
    "innovaccer",        # Noida (health tech)
    "niramai",           # Bangalore (health AI)
    "perfios",           # Bangalore (fintech)
    "signzy",            # Bangalore (fintech)
    "bureau",            # Bangalore (fraud intelligence)
    "indifi",            # Gurugram (SME lending)
    "credavenue",        # Chennai (debt marketplace)
    "recur-club",        # Bangalore
    "klub",              # Mumbai
    "elevation-capital", # Delhi (VC — hires interns)
    "stellaris",         # Bangalore (VC)
    "blume-ventures",    # Mumbai (VC)
    "prime-venture",     # Bangalore (VC)
    # ── Global companies with India presence ────────────────────────────────
    "openai",
    "cursor",
    "linear",
    "retool",
    "vercel",
    "supabase",
    "ramp",
    "notion",
]


class AshbyConnector(BaseConnector):
    """Retrieve internships from public Ashby job boards."""

    source = "ashby"

    def __init__(self, organization_slugs: list[str] | None = None) -> None:
        self.organization_slugs = organization_slugs or ASHBY_ORGANIZATION_SLUGS

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Return configured Ashby organization slugs."""

        return [{"name": slug.replace("-", " ").title(), "slug": slug} for slug in self.organization_slugs]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fetch Ashby postings."""

        async def fetch_company(client: httpx.AsyncClient, company: dict[str, Any]) -> list[dict[str, Any]]:
            slug = company["slug"]
            try:
                response = await asyncio.wait_for(
                    client.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}"),
                    timeout=15.0
                )
                response.raise_for_status()
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                logger.debug("Ashby organization skipped: %s (%s)", slug, exc)
                return []

            jobs = response.json().get("jobs", [])
            for job in jobs:
                job["company_name"] = company["name"]
                job["organization_slug"] = slug
            return jobs

        timeout = httpx.Timeout(15.0)
        limits = httpx.Limits(max_keepalive_connections=50, max_connections=150)
        async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
            results = await asyncio.gather(
                *(fetch_company(client, company) for company in companies),
                return_exceptions=True,
            )

        jobs: list[dict[str, Any]] = []
        for result in results:
            if isinstance(result, BaseException):
                logger.debug("Ashby organization fetch failed: %s", result)
                continue
            jobs.extend(result)
        return jobs

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize Ashby jobs — India locations, internships only."""

        internships: list[InternshipCreate] = []
        for job in raw_jobs:
            title = job.get("title", "")
            description = job.get("descriptionPlain", "") or job.get("descriptionHtml", "")

            if not self.is_internship(title, description):
                continue

            location = job.get("location", "")

            if not self.is_india_location(location):
                continue

            slug = job.get("organization_slug", "")
            internships.append(
                self.build_internship(
                    external_id=job.get("id", ""),
                    company=job.get("company_name", ""),
                    title=title,
                    location=location,
                    url=f"https://jobs.ashbyhq.com/{slug}/{job.get('id', '')}",
                    description=description,
                    tags=["ats", "ashby"],
                )
            )
        return internships
