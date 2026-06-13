"""Lever ATS connector."""

from typing import Any

import requests

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

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

        jobs: list[dict[str, Any]] = []
        for company in companies:
            slug = company["slug"]
            try:
                response = requests.get(
                    f"https://api.lever.co/v0/postings/{slug}",
                    params={"mode": "json"},
                    timeout=20,
                )
                response.raise_for_status()
            except requests.RequestException:
                continue
            for job in response.json():
                job["company_name"] = company["name"]
                jobs.append(job)
        return jobs

    async def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
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
