"""SmartRecruiters ATS connector."""

from typing import Any

import asyncio
import logging

import httpx

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

# SmartRecruiters company slugs for Indian and global companies with India offices.
SMARTRECRUITERS_COMPANY_SLUGS: list[str] = [
    # ── Indian-origin companies ─────────────────────────────────────────────
    "TataConsultancyServices",   # Mumbai
    "TataCommunications",        # Mumbai
    "TataElxsi",                 # Bangalore
    "Bajaj-Finserv",             # Pune
    "HDFC-Bank",                 # Mumbai
    "ICICIBank",                 # Mumbai
    "KotakMahindraBank",         # Mumbai
    "AxisBank",                  # Mumbai
    "IndusIndBank",              # Mumbai
    "RelianceIndustries",        # Mumbai
    "RelJio",                    # Mumbai
    "RelianceRetail",            # Mumbai
    "Mahindra",                  # Mumbai
    "Maruti-Suzuki",             # Gurugram
    "Hero-MotoCorp",             # Delhi
    "DreamSports",               # Mumbai (Dream11)
    "Games24x7",                 # Mumbai
    "Nazara-Technologies",       # Mumbai
    "Newgen-Software",           # Delhi
    "Minda-Industries",          # Gurugram
    # ── Global companies with India engineering centres ──────────────────────
    "Siemens",
    "Bosch",
    "Schneider-Electric",
    "Honeywell",
    "3M",
    "Philips",
]


class SmartRecruitersConnector(BaseConnector):
    """Retrieve internships from SmartRecruiters public APIs."""

    source = "smartrecruiters"

    def __init__(self, company_slugs: list[str] | None = None) -> None:
        self.company_slugs = company_slugs if company_slugs is not None else SMARTRECRUITERS_COMPANY_SLUGS

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Return configured SmartRecruiters company slugs."""

        return [{"name": slug.replace("-", " ").title(), "slug": slug} for slug in self.company_slugs]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fetch SmartRecruiters postings."""

        async def fetch_company(client: httpx.AsyncClient, company: dict[str, Any]) -> list[dict[str, Any]]:
            try:
                response = await asyncio.wait_for(
                    client.get(
                        f"https://api.smartrecruiters.com/v1/companies/{company['slug']}/postings",
                    ),
                    timeout=3.0
                )
                response.raise_for_status()
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                logger.debug("SmartRecruiters company skipped: %s (%s)", company["slug"], exc)
                return []

            jobs = response.json().get("content", [])
            for job in jobs:
                job["company_name"] = company["name"]
                job["company_slug"] = company["slug"]
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
                logger.debug("SmartRecruiters company fetch failed: %s", result)
                continue
            jobs.extend(result)
        return jobs

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize SmartRecruiters jobs — India locations, internships only."""

        internships: list[InternshipCreate] = []
        for job in raw_jobs:
            title = job.get("name", "")
            description = job.get("jobAd", {}).get("sections", {}).get("jobDescription", {}).get("text", "")

            if not self.is_internship(title, description):
                continue

            location_obj = job.get("location", {})
            # SmartRecruiters provides city + country separately
            city = location_obj.get("city", "")
            country = location_obj.get("country", "")
            location = f"{city}, {country}".strip(", ") if city or country else ""

            if not self.is_india_location(location):
                continue

            company_slug = job.get("company_slug")
            job_id = job.get("id")
            url = f"https://jobs.smartrecruiters.com/{company_slug}/{job_id}" if company_slug and job_id else job.get("ref", "")

            internships.append(
                self.build_internship(
                    external_id=job.get("id", ""),
                    company=job.get("company_name", ""),
                    title=title,
                    location=location or "India",
                    url=url,
                    description=description,
                    tags=["ats", "smartrecruiters"],
                )
            )
        return internships
