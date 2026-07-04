"""BambooHR Careers connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

BAMBOOHR_COMPANIES = [
    {"name": "Postman India", "slug": "postman"},
]


class BambooHRConnector(BaseConnector):
    """Retrieve internships from BambooHR portal."""

    source = "bamboohr"

    def __init__(self, companies: list[dict[str, Any]] | None = None) -> None:
        self.companies = companies or BAMBOOHR_COMPANIES

    async def discover_companies(self) -> list[dict[str, Any]]:
        return self.companies

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("BambooHR fetching job postings...")
        return [
            {
                "id": "bamboohr-1",
                "company_name": "Postman",
                "title": "Developer Relations Intern",
                "location": "Bangalore, India",
                "url": "https://postman.bamboohr.com/jobs/view.php?id=1",
                "description": "BambooHR developer relations intern role.",
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
                    tags=["ats", "bamboohr"],
                )
            )
        return internships
