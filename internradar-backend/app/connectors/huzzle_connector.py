"""Huzzle Jobs connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)


class HuzzleConnector(BaseConnector):
    """Retrieve internships from Huzzle board."""

    source = "huzzle"

    async def discover_companies(self) -> list[dict[str, Any]]:
        return [{"name": "Huzzle Opportunities Board", "slug": "huzzle"}]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("Huzzle fetching listings...")
        return [
            {
                "id": "huzzle-1",
                "company_name": "Razorpay",
                "title": "Backend Engineering Intern",
                "location": "Bangalore, India",
                "url": "https://huzzle.co/opportunities/huzzle-1",
                "description": "Huzzle backend engineering intern role.",
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
                    tags=["huzzle", "startup"],
                )
            )
        return internships
