"""Ashby ATS connector."""

from typing import Any

import requests

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

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

        jobs: list[dict[str, Any]] = []
        for company in companies:
            slug = company["slug"]
            try:
                response = requests.get(
                    f"https://api.ashbyhq.com/posting-api/job-board/{slug}",
                    timeout=20,
                )
                response.raise_for_status()
            except requests.RequestException:
                continue
            for job in response.json().get("jobs", []):
                job["company_name"] = company["name"]
                job["organization_slug"] = slug
                jobs.append(job)
        return jobs

    async def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
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
