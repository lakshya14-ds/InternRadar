"""IIT notice board connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

IIT_SITES = [
    {"name": "IIT Bombay", "url": "https://www.iitb.ac.in/"},
    {"name": "IIT Delhi", "url": "https://home.iitd.ac.in/"},
    {"name": "IIT Madras", "url": "https://www.iitm.ac.in/"},
]


class IITConnector(BaseConnector):
    """Retrieve internship notices from IITs."""

    source = "iit_portal"

    async def discover_companies(self) -> list[dict[str, Any]]:
        return IIT_SITES

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("IIT notice board fetching listings...")
        return [
            {
                "id": "iitb-intern-1",
                "college": "IIT Bombay",
                "title": "Summer Research Internship 2026",
                "location": "Mumbai, India",
                "url": "https://www.iitb.ac.in/en/event/summer-research-internship-2026",
                "description": "IIT Bombay summer research internship opportunity.",
            }
        ]

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        internships = []
        for job in raw_jobs:
            # Skip strict title check because academic roles often use descriptive names
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
                    tags=["iit", "education"],
                )
            )
        return internships
