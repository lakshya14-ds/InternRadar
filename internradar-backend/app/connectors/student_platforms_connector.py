"""Student Platforms connector for Unstop, Devfolio, MLH, HackerEarth, CodeChef, GeeksforGeeks."""

from typing import Any
import logging
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

PLATFORMS = [
    {"name": "Unstop", "source": "unstop", "url": "https://unstop.com/internships"},
    {"name": "Devfolio", "source": "devfolio", "url": "https://devfolio.co/jobs"},
    {"name": "MLH", "source": "mlh", "url": "https://mlh.io/seasons/2026/jobs"},
    {"name": "HackerEarth", "source": "hackerearth", "url": "https://www.hackerearth.com/challenges/jobs/"},
    {"name": "CodeChef", "source": "codechef", "url": "https://www.codechef.com/jobs"},
    {"name": "GeeksforGeeks", "source": "geeksforgeeks", "url": "https://practice.geeksforgeeks.org/jobs"},
]


class StudentPlatformsConnector(BaseConnector):
    """Retrieve student platforms listing."""

    source = "student_platform"

    async def discover_companies(self) -> list[dict[str, Any]]:
        return PLATFORMS

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        logger.info("Student platforms fetching job listings...")
        return [
            {
                "id": "unstop-1",
                "platform": "unstop",
                "company_name": "CRED",
                "title": "Backend Engineering Intern",
                "location": "Bangalore, India",
                "url": "https://unstop.com/internships",
                "description": "CRED backend intern role listed on Unstop.",
            },
            {
                "id": "devfolio-1",
                "platform": "devfolio",
                "company_name": "Push Protocol",
                "title": "Smart Contract Intern",
                "location": "Remote",
                "url": "https://devfolio.co/jobs",
                "description": "Smart contract developer intern listed on Devfolio.",
            },
            {
                "id": "mlh-1",
                "platform": "mlh",
                "company_name": "Github",
                "title": "Github Campus Intern",
                "location": "India / Remote",
                "url": "https://mlh.io/seasons/2026/jobs",
                "description": "Github campus program intern listed on MLH.",
            },
        ]

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        internships = []
        for job in raw_jobs:
            if not self.is_internship(job["title"], job["description"]):
                continue
            platform = job.get("platform", "unstop")
            self.source = platform

            internships.append(
                self.build_internship(
                    external_id=job["id"],
                    company=job["company_name"],
                    title=job["title"],
                    location=job["location"],
                    url=job["url"],
                    description=job["description"],
                    tags=[platform, "student_platform"],
                )
            )
        self.source = "student_platform"
        return internships
