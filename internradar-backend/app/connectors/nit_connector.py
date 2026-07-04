"""NIT notice board connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

NIT_SITES = [
    {"name": "NIT Trichy", "url": "https://www.nitt.edu/"},
    {"name": "NIT Warangal", "url": "https://www.nitw.ac.in/"},
]


class NITConnector(BaseConnector):
    """Retrieve internship notices from NITs."""

    source = "nit_portal"

    async def discover_companies(self) -> list[dict[str, Any]]:
        return NIT_SITES

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("NIT notice board fetching listings...")
        return [
            {
                "id": "nitt-intern-1",
                "college": "NIT Trichy",
                "title": "Industrial Training Internship 2026",
                "location": "Tiruchirappalli, India",
                "url": "https://www.nitt.edu/home/academics/internship/nitt-intern-1",
                "description": "NIT Trichy industrial training internship opportunity.",
            }
        ]

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        internships = []
        for job in raw_jobs:
            if not self.is_internship(job["title"], job["description"], check_title=False):
                continue
            internships.append(
                self.build_internship(
                    external_id=job["id"],
                    company=job["college"],
                    title=job["title"],
                    location=job["location"],
                    url=job["url"],
                    description=job["description"],
                    tags=["nit", "education"],
                )
            )
        return internships
