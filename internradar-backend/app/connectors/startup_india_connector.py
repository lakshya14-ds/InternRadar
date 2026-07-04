"""Startup India platform connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)


class StartupIndiaConnector(BaseConnector):
    """Retrieve internships from Startup India portal."""

    source = "startup_india"

    async def discover_companies(self) -> list[dict[str, Any]]:
        return [{"name": "Startup India Hub", "slug": "startup_india"}]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("Startup India fetching listings...")
        return [
            {
                "id": "startup-india-1",
                "company_name": "Krutrim AI",
                "title": "AI Research Intern",
                "location": "Bangalore, India",
                "url": "https://www.startupindia.gov.in/jobs/si-1",
                "description": "Startup India AI research intern role.",
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
                    tags=["startup_india", "startup"],
                )
            )
        return internships
