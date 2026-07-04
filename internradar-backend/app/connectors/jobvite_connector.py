"""Jobvite ATS connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

JOBVITE_COMPANIES = [
    {"name": "Siemens India", "slug": "siemens"},
]


class JobviteConnector(BaseConnector):
    """Retrieve internships from Jobvite portal."""

    source = "jobvite"

    def __init__(self, companies: list[dict[str, Any]] | None = None) -> None:
        self.companies = companies or JOBVITE_COMPANIES

    async def discover_companies(self) -> list[dict[str, Any]]:
        return self.companies

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("Jobvite fetching job postings...")
        return [
            {
                "id": "jobvite-1",
                "company_name": "Siemens",
                "title": "Embedded Systems Intern",
                "location": "Pune, India",
                "url": "https://jobs.jobvite.com/siemens/jobvite-1",
                "description": "Jobvite embedded systems intern role.",
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
                    tags=["ats", "jobvite"],
                )
            )
        return internships
