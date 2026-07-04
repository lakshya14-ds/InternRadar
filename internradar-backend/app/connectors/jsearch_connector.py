"""JSearch RapidAPI connector."""

import asyncio
from datetime import UTC, datetime
import logging
from typing import Any

import httpx

from app.config import get_settings
from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)


class JSearchConnector(BaseConnector):
    """Retrieve internships from RapidAPI JSearch endpoint."""

    source = "jsearch"

    def __init__(self, api_key: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.rapidapi_key
        self.queries = [
            "software engineer intern in India",
            "data science intern in India",
            "machine learning intern in India",
            "product intern in India",
            "cybersecurity intern in India",
        ]

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Return configured queries for JSearch API."""
        return [{"name": f"JSearch: {q}", "query": q} for q in self.queries]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Query the JSearch API endpoints for each search term."""
        if not self.api_key:
            logger.warning("RAPIDAPI_KEY is not set. JSearch connector will return mock fallback data.")
            return self._get_mock_data()

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com",
        }

        async def fetch_query(client: httpx.AsyncClient, company: dict[str, Any]) -> list[dict[str, Any]]:
            query = company["query"]
            try:
                response = await asyncio.wait_for(
                    client.get(
                        "https://jsearch.p.rapidapi.com/search",
                        headers=headers,
                        params={
                            "query": query,
                            "page": "1",
                            "num_pages": "1",
                            "date_posted": "week",
                        },
                    ),
                    timeout=5.0
                )
                response.raise_for_status()
                data = response.json().get("data", [])
                logger.info("JSearch fetched %d jobs for query '%s'", len(data), query)
                return data
            except Exception as exc:
                logger.warning("JSearch API query '%s' failed: %s", query, exc)
                return []

        timeout = httpx.Timeout(5.0)
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
            results = await asyncio.gather(
                *(fetch_query(client, company) for company in companies),
                return_exceptions=True,
            )

        jobs: list[dict[str, Any]] = []
        for r in results:
            if isinstance(r, list):
                jobs.extend(r)
        return jobs

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize JSearch job representations into InternshipCreate payloads."""
        internships: list[InternshipCreate] = []
        for job in raw_jobs:
            # Handle mock payloads directly
            if job.get("is_mock"):
                internships.append(
                    self.build_internship(
                        external_id=job["external_id"],
                        company=job["company"],
                        title=job["title"],
                        location=job["location"],
                        url=job["url"],
                        description=job["description"],
                        posted_at=job["posted_at"],
                        skills=job["skills"],
                        stipend=job["stipend"],
                        duration=job["duration"],
                        company_logo=job["company_logo"],
                        work_type=job["work_type"],
                        tags=["jsearch"],
                    )
                )
                continue

            title = job.get("job_title", "")
            description = job.get("job_description", "")

            if not self.is_internship(title, description):
                continue

            # Handle location
            city = job.get("job_city")
            state = job.get("job_state")
            country = job.get("job_country", "IN")
            loc_parts = [p for p in [city, state, country] if p]
            location = ", ".join(loc_parts) if loc_parts else "India"

            if not self.is_india_location(location):
                continue

            # Parse salary/stipend details
            stipend = None
            min_sal = job.get("job_min_salary")
            max_sal = job.get("job_max_salary")
            currency = job.get("job_salary_currency", "INR")
            period = job.get("job_salary_period", "month")
            if max_sal:
                if min_sal and min_sal != max_sal:
                    stipend = f"{currency} {min_sal} - {max_sal} /{period}"
                else:
                    stipend = f"{currency} {max_sal} /{period}"

            # Format posted_at date
            posted_at = datetime.now(UTC)
            posted_ts = job.get("job_posted_at_timestamp")
            if posted_ts:
                try:
                    posted_at = datetime.fromtimestamp(posted_ts, tz=UTC)
                except Exception:
                    pass

            is_remote = bool(job.get("job_is_remote", False))
            work_type = "Remote" if is_remote else "Onsite"

            internships.append(
                self.build_internship(
                    external_id=job.get("job_id", ""),
                    company=job.get("employer_name", "Unknown Company"),
                    title=title,
                    location=location,
                    url=job.get("job_apply_link", ""),
                    description=description,
                    posted_at=posted_at,
                    skills=[title.split()[-1]] if len(title.split()) > 0 else [],
                    stipend=stipend,
                    company_logo=job.get("employer_logo"),
                    work_type=work_type,
                    tags=["jsearch"],
                )
            )
        return internships

    def _get_mock_data(self) -> list[dict[str, Any]]:
        """Return rich, India-focused mock internship data if API key is not configured."""
        now = datetime.now(UTC)
        return [
            {
                "is_mock": True,
                "external_id": "mock-jsearch-1",
                "company": "Google India",
                "title": "Software Engineering Intern",
                "location": "Bangalore, India",
                "url": "https://careers.google.com/jobs/results/?q=intern",
                "description": "Develop next-gen search features. Requires Python/C++ and active student status.",
                "posted_at": now,
                "skills": ["Python", "C++", "Algorithms"],
                "stipend": "INR 80,000 /month",
                "duration": "3 Months",
                "company_logo": "https://logo.clearbit.com/google.com",
                "work_type": "Onsite",
            },
            {
                "is_mock": True,
                "external_id": "mock-jsearch-2",
                "company": "Microsoft India",
                "title": "Data Science & ML Intern",
                "location": "Hyderabad, India",
                "url": "https://careers.microsoft.com/us/en/search-results?keywords=internship",
                "description": "Analyze large-scale Azure metrics using PyTorch and scikit-learn.",
                "posted_at": now,
                "skills": ["PyTorch", "Python", "SQL"],
                "stipend": "INR 75,000 /month",
                "duration": "6 Months",
                "company_logo": "https://logo.clearbit.com/microsoft.com",
                "work_type": "Hybrid",
            },
            {
                "is_mock": True,
                "external_id": "mock-jsearch-3",
                "company": "Razorpay",
                "title": "Backend Engineering Intern",
                "location": "Bangalore, India",
                "url": "https://razorpay.com/jobs/",
                "description": "Build high-throughput payment gateway services in Go.",
                "posted_at": now,
                "skills": ["Golang", "Redis", "REST APIs"],
                "stipend": "INR 45,000 /month",
                "duration": "6 Months",
                "company_logo": "https://logo.clearbit.com/razorpay.com",
                "work_type": "Onsite",
            },
            {
                "is_mock": True,
                "external_id": "mock-jsearch-4",
                "company": "Cred",
                "title": "Cybersecurity Intern",
                "location": "Pune, India",
                "url": "https://cred.club/careers",
                "description": "Perform application security auditing and penetration testing.",
                "posted_at": now,
                "skills": ["Cybersecurity", "Penetration Testing", "OWASP"],
                "stipend": "INR 50,000 /month",
                "duration": "3 Months",
                "company_logo": "https://logo.clearbit.com/cred.club",
                "work_type": "Remote",
            },
            {
                "is_mock": True,
                "external_id": "mock-jsearch-5",
                "company": "Paytm",
                "title": "Product Management Intern",
                "location": "Noida, India",
                "url": "https://paytm.com/careers",
                "description": "Formulate payment and financial wallet features, working with engineering teams.",
                "posted_at": now,
                "skills": ["Product Strategy", "SQL", "Wireframing"],
                "stipend": "INR 30,000 /month",
                "duration": "6 Months",
                "company_logo": "https://logo.clearbit.com/paytm.com",
                "work_type": "Onsite",
            },
        ]
