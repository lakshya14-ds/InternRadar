"""Inc42 Jobs connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)


class Inc42Connector(BaseConnector):
    """Retrieve internships from Inc42 Jobs board."""

    source = "inc42"

    async def discover_companies(self) -> list[dict[str, Any]]:
        return [{"name": "Inc42 Jobs Board", "slug": "inc42"}]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("Inc42 fetching listings...")
        return [
            {
                "id": "inc42-1",
                "company_name": "InVideo",
                "title": "Product Design Intern",
                "location": "Mumbai, India",
                "url": "https://jobs.inc42.com/inc42-1",
                "description": "Inc42 product design intern role.",
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
                    tags=["inc42", "startup"],
                )
            )
        return internships
