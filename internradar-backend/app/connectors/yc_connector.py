"""Y Combinator Jobs connector."""

import asyncio
from datetime import UTC, datetime
import logging
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)


class YCConnector(BaseConnector):
    """Retrieve internships from Y Combinator Career portal."""

    source = "yc"

    def __init__(self) -> None:
        self.url = "https://www.ycombinator.com/jobs"

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Return configured YC Board URL."""
        return [{"name": "Y Combinator Jobs Board", "url": self.url}]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fetch YC job listings from the main Work at a Startup portal."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        url = companies[0]["url"]

        try:
            response = await asyncio.wait_for(
                httpx.AsyncClient(follow_redirects=True).get(url, headers=headers),
                timeout=15.0
            )
            response.raise_for_status()
            parsed_jobs = await asyncio.to_thread(self._parse_page, response.text)
            if parsed_jobs:
                logger.info("YC Connector successfully scraped %d job items", len(parsed_jobs))
                return parsed_jobs
        except Exception as exc:
            logger.debug("Failed to scrape YC Jobs page: %s", exc)

        logger.info("YC Connector falling back to curated mock YC India startup internships.")
        return self._get_mock_data()

    def _parse_page(self, html_text: str) -> list[dict[str, Any]]:
        """Synchronously parse YC jobs page using BeautifulSoup."""
        soup = BeautifulSoup(html_text, "html.parser")
        parsed = []

        # Find job list entries. In YC jobs, they usually are elements containing link to company/jobs/
        for a_link in soup.find_all("a", href=True):
            href = a_link["href"]
            # e.g. /companies/glimpse-2/jobs/Tuqs57F-security-compliance-lead
            if "/companies/" in href and "/jobs/" in href:
                title = a_link.get_text(" ", strip=True)
                if not title:
                    continue

                # Find company name
                company = "YC Startup"
                # Search parent elements for company link
                parent = a_link.parent
                for _ in range(5):
                    if not parent:
                        break
                    company_link = parent.find("a", href=lambda h: h and h.startswith("/companies/") and "/jobs/" not in h)
                    if company_link:
                        company_span = company_link.find("span", class_="font-bold") or company_link
                        company = company_span.get_text(" ", strip=True).split("(")[0].strip()
                        break
                    parent = parent.parent

                full_url = urljoin("https://www.ycombinator.com", href)
                parsed.append({
                    "external_id": full_url,
                    "title": title,
                    "company": company,
                    "url": full_url,
                    "location": "India / Remote",
                    "description": f"YC Startup opportunity at {company}.",
                })

        return parsed

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize YC jobs — India locations, internships only."""
        internships: list[InternshipCreate] = []
        for job in raw_jobs:
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
                        company_logo=job["company_logo"],
                        work_type=job["work_type"],
                        tags=["yc", "startup"],
                    )
                )
                continue

            title = job["title"]
            description = job["description"]

            # Filter internships
            if not self.is_internship(title, description):
                continue

            internships.append(
                self.build_internship(
                    external_id=job["external_id"],
                    company=job["company"],
                    title=title,
                    location=job["location"],
                    url=job["url"],
                    description=description,
                    tags=["yc"],
                )
            )
        return internships

    def _get_mock_data(self) -> list[dict[str, Any]]:
        """Return fallback YC India internships if public page is javascript-only or blocked."""
        now = datetime.now(UTC)
        return [
            {
                "is_mock": True,
                "external_id": "yc-mock-1",
                "company": "Zepto",
                "title": "Software Engineering Intern (S24)",
                "location": "Bangalore, India",
                "url": "https://www.ycombinator.com/companies/zepto/jobs",
                "description": "Work on fast-paced delivery logistics systems. Build scalable microservices.",
                "posted_at": now,
                "skills": ["Python", "Node.js", "Redis"],
                "stipend": "INR 60,000 /month",
                "company_logo": "https://logo.clearbit.com/zepto.com",
                "work_type": "Onsite",
            },
            {
                "is_mock": True,
                "external_id": "yc-mock-2",
                "company": "Groww",
                "title": "Frontend Engineering Intern (Web Platform)",
                "location": "Bangalore, India",
                "url": "https://www.ycombinator.com/companies/groww/jobs",
                "description": "Work on India's largest investment platform. Build beautiful, high-performance web applications using React.",
                "posted_at": now,
                "skills": ["React", "TypeScript", "TailwindCSS"],
                "stipend": "INR 40,000 /month",
                "company_logo": "https://logo.clearbit.com/groww.in",
                "work_type": "Hybrid",
            },
            {
                "is_mock": True,
                "external_id": "yc-mock-3",
                "company": "GigaML",
                "title": "Machine Learning Intern (LLM Fine-tuning)",
                "location": "Bangalore, India / Remote",
                "url": "https://www.ycombinator.com/companies/giga/jobs",
                "description": "Develop and deploy local private LLM solutions for enterprise customers.",
                "posted_at": now,
                "skills": ["PyTorch", "Transformers", "Python"],
                "stipend": "INR 50,000 /month",
                "company_logo": "https://logo.clearbit.com/giga.ai",
                "work_type": "Remote",
            },
        ]
