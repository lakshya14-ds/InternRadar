"""Greenhouse ATS connector."""

from typing import Any

import requests

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

# Board tokens for companies known to use Greenhouse.
# Indian companies are marked with a comment; the rest are global companies
# that hire interns for their India offices.
GREENHOUSE_BOARD_TOKENS: list[str] = [
    # ── Indian-origin companies ─────────────────────────────────────────────
    "razorpay",          # Bangalore
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

        jobs: list[dict[str, Any]] = []
        for company in companies:
            token = company["board_token"]
            try:
                response = requests.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs",
                    params={"content": "true"},
                    timeout=20,
                )
                response.raise_for_status()
            except requests.RequestException:
                # Board may not exist or be temporarily unavailable — skip silently
                continue
            for job in response.json().get("jobs", []):
                job["company_name"] = company["name"]
                job["board_token"] = token
                jobs.append(job)
        return jobs

    async def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
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
