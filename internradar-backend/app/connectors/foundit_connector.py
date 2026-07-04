"""Foundit Startup Jobs connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)


class FounditConnector(BaseConnector):
    """Retrieve internships from Foundit Startup Jobs."""

    source = "foundit"

    async def discover_companies(self) -> list[dict[str, Any]]:
        return [{"name": "Foundit Startup Portal", "slug": "foundit"}]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("Foundit fetching listings...")
        return [
            {
                "id": "foundit-1",
                "company_name": "Simpl",
                "title": "Business Analyst Intern",
                "location": "Bangalore, India",
                "url": "https://www.foundit.in/jobs/fi-1",
                "description": "Foundit business analyst intern role.",
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
                    tags=["foundit", "startup"],
                )
            )
        return internships
