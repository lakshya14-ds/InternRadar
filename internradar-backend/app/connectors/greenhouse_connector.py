"""Greenhouse ATS connector."""

from typing import Any

import asyncio
import logging

import httpx

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

# Board tokens for companies known to use Greenhouse.
# Indian companies are marked with a comment; the rest are global companies
# that hire interns for their India offices.
GREENHOUSE_BOARD_TOKENS: list[str] = [
    # ── Indian-origin companies ─────────────────────────────────────────────
    "razorpaysoftwareprivatelimited", # Bangalore
    "phonepe",           # Bangalore
    "zepto",             # Mumbai / Bangalore
    "meesho",            # Bangalore
    "mpl",               # Mobile Premier League — Bangalore
    "groww",             # Bangalore
    "slice",             # Bangalore
    "cred",              # Bangalore
    "bharatpe",          # Delhi
    "smallcase",         # Bangalore
    "yellowmessenger",   # Yellow.ai — Bangalore
    "unacademy",         # Bangalore
    "vedantu",           # Bangalore
    "toppr",             # Mumbai
    "byjus",             # Bangalore
    "dunzo",             # Bangalore
    "milkbasket",        # Gurugram
    "purplle",           # Mumbai
    "licious",           # Bangalore
    "udaan",             # Bangalore
    "moglix",            # Noida
    "cashfree",          # Bangalore
    "setu",              # Bangalore
    "leadsquared",       # Bangalore
    "darwinbox",         # Hyderabad
    "freshworks",        # Chennai / Bangalore
    "zoho",              # Chennai
    "chargebee",         # Chennai
    "postman",           # Bangalore
    "browserstack",      # Mumbai
    "clevertap",         # Mumbai
    "moengage",          # Bangalore
    "webengage",         # Mumbai
    # ── Global companies with large India engineering centres ────────────────
    "stripe",
    "databricks",
    "airbnb",
    "adobe",
    "walmart",
    "intuit",
    "paypal",
    "uber",
    "linkedin",
    "microsoft",
    "google",
    "amazon",
    "oracle",
    "sap",
    "airtable",
    "figma",
    "netlify",
    "scaleai",
    "vercel",
]


class GreenhouseConnector(BaseConnector):
    """Retrieve internships from public Greenhouse job board APIs."""

    source = "greenhouse"

    def __init__(self, board_tokens: list[str] | None = None) -> None:
        self.board_tokens = board_tokens or GREENHOUSE_BOARD_TOKENS

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Return configured Greenhouse board tokens."""

        return [{"name": token.replace("-", " ").title(), "board_token": token} for token in self.board_tokens]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fetch jobs from Greenhouse boards."""

        async def fetch_company(client: httpx.AsyncClient, company: dict[str, Any]) -> list[dict[str, Any]]:
            token = company["board_token"]
            try:
                response = await asyncio.wait_for(
                    client.get(
                        f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs",
                        params={"content": "true"},
                    ),
                    timeout=15.0
                )
                response.raise_for_status()
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                logger.debug("Greenhouse board skipped: %s (%s)", token, exc)
                return []

            fetched_jobs = response.json().get("jobs", [])
            for job in fetched_jobs:
                job["company_name"] = company["name"]
                job["board_token"] = token
            return fetched_jobs

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
                logger.debug("Greenhouse board fetch failed: %s", result)
                continue
            jobs.extend(result)
        return jobs

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize Greenhouse jobs — India locations, internships only."""

        internships: list[InternshipCreate] = []
        for job in raw_jobs:
            title = job.get("title", "")
            description = job.get("content", "")

            if not self.is_internship(title, description):
                continue

            location = (job.get("location") or {}).get("name", "")

            if not self.is_india_location(location):
                continue

            internships.append(
                self.build_internship(
                    external_id=str(job.get("id", "")),
                    company=job.get("company_name", job.get("board_token", "")),
                    title=title,
                    location=location,
                    url=job.get("absolute_url", ""),
                    description=description,
                    tags=["ats", "greenhouse"],
                )
            )
        return internships
