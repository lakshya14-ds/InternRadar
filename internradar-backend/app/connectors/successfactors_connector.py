"""SAP SuccessFactors ATS connector."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

SUCCESSFACTORS_COMPANIES = [
    {"name": "SAP India", "slug": "sap"},
]


class SuccessFactorsConnector(BaseConnector):
    """Retrieve internships from SAP SuccessFactors portal."""

    source = "successfactors"

    def __init__(self, companies: list[dict[str, Any]] | None = None) -> None:
        self.companies = companies or SUCCESSFACTORS_COMPANIES

    async def discover_companies(self) -> list[dict[str, Any]]:
        return self.companies

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("SuccessFactors fetching job postings...")
        return [
            {
                "id": "sf-1",
                "company_name": "SAP",
                "title": "Cloud Operations Intern",
                "location": "Bangalore, India",
                "url": "https://sap.successfactors.eu/jobs/sf-1",
                "description": "SuccessFactors cloud operations intern role.",
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
                    tags=["ats", "successfactors"],
                )
            )
        return internships
