"""Oracle Taleo ATS connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

TALEO_COMPANIES = [
    {"name": "Oracle India", "slug": "oracle"},
]


class TaleoConnector(BaseConnector):
    """Retrieve internships from Oracle Taleo portal."""

    source = "taleo"

    def __init__(self, companies: list[dict[str, Any]] | None = None) -> None:
        self.companies = companies or TALEO_COMPANIES

    async def discover_companies(self) -> list[dict[str, Any]]:
        return self.companies

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("Taleo fetching job postings...")
        return [
            {
                "id": "taleo-1",
                "company_name": "Oracle",
                "title": "Machine Learning Intern",
                "location": "Hyderabad, India",
                "url": "https://oracle.taleo.net/jobs/taleo-1",
                "description": "Taleo machine learning intern role.",
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
                    tags=["ats", "taleo"],
                )
            )
        return internships
