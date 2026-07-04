"""Headstart Jobs connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)


class HeadstartConnector(BaseConnector):
    """Retrieve internships from Headstart portal."""

    source = "headstart"

    async def discover_companies(self) -> list[dict[str, Any]]:
        return [{"name": "Headstart Network", "slug": "headstart"}]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("Headstart fetching listings...")
        return [
            {
                "id": "headstart-1",
                "company_name": "Lenskart",
                "title": "Front End Intern",
                "location": "Faridabad, India",
                "url": "https://headstart.in/jobs/hs-1",
                "description": "Headstart frontend intern role.",
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
                    tags=["headstart", "startup"],
                )
            )
        return internships
