"""SmartRecruiters ATS connector."""

from typing import Any

import requests

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

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

        jobs: list[dict[str, Any]] = []
        for company in companies:
            try:
                response = requests.get(
                    f"https://api.smartrecruiters.com/v1/companies/{company['slug']}/postings",
                    timeout=20,
                )
                response.raise_for_status()
            except requests.RequestException:
                continue
            for job in response.json().get("content", []):
                job["company_name"] = company["name"]
                jobs.append(job)
        return jobs

    async def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
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

            internships.append(
                self.build_internship(
                    external_id=job.get("id", ""),
                    company=job.get("company_name", ""),
                    title=title,
                    location=location or "India",
                    url=job.get("ref", ""),
                    description=description,
                    tags=["ats", "smartrecruiters"],
                )
            )
        return internships
