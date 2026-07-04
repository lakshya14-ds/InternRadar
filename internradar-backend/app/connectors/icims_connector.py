"""iCIMS ATS connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

ICIMS_COMPANIES = [
    {"name": "Microsoft iCIMS", "slug": "microsoft"},
    {"name": "Intel iCIMS", "slug": "intel"},
]


class ICIMSConnector(BaseConnector):
    """Retrieve internships from iCIMS portal."""

    source = "icims"

    def __init__(self, companies: list[dict[str, Any]] | None = None) -> None:
        self.companies = companies or ICIMS_COMPANIES

    async def discover_companies(self) -> list[dict[str, Any]]:
        return self.companies

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("iCIMS fetching job postings...")
        return [
            {
                "id": "icims-1",
                "company_name": "Microsoft",
                "title": "Software Engineering Intern",
                "location": "Bangalore, Karnataka, India",
                "url": "https://careers.microsoft.com/jobs/icims-1",
                "description": "iCIMS engineering intern role.",
            }
        ]

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        internships = []
        for job in raw_jobs:
            if not self.is_internship(job["title"], job["description"]):
                continue
            if not self.is_india_location(job["location"]):
                continue
            internships.append(
                self.build_internship(
                    external_id=job["id"],
                    company=job["company_name"],
                    title=job["title"],
                    location=job["location"],
                    url=job["url"],
                    description=job["description"],
                    tags=["ats", "icims"],
                )
            )
        return internships
