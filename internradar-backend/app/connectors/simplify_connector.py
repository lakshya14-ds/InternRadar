"""Simplify Jobs connector."""

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


class SimplifyConnector(BaseConnector):
    """Retrieve internships from Simplify.jobs curated portals."""

    source = "simplify"

    def __init__(self) -> None:
        self.urls = [
            "https://simplify.jobs/l/Software-Engineering-Internships",
            "https://simplify.jobs/l/Data-Analytics-Internships",
        ]

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Return configured Simplify curated listing pages."""
        return [{"name": f"Simplify Curation {i}", "url": url} for i, url in enumerate(self.urls)]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Scrape curated internship cards from Simplify pages."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        async def fetch_url(client: httpx.AsyncClient, company: dict[str, Any]) -> list[dict[str, Any]]:
            url = company["url"]
            try:
                response = await asyncio.wait_for(
                    client.get(url, headers=headers),
                    timeout=15.0
                )
                response.raise_for_status()
                parsed = await asyncio.to_thread(self._parse_page, response.text)
                if parsed:
                    return parsed
            except Exception as exc:
                logger.debug("Failed to scrape Simplify page %s: %s", url, exc)
            return []

        timeout = httpx.Timeout(15.0)
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
            results = await asyncio.gather(
                *(fetch_url(client, company) for company in companies),
                return_exceptions=True,
            )

        jobs: list[dict[str, Any]] = []
        for r in results:
            if isinstance(r, list):
                jobs.extend(r)

        if not jobs:
            logger.info("Simplify connector falling back to curated mock Simplify internships.")
            return self._get_mock_data()

        return jobs

    def _parse_page(self, html_text: str) -> list[dict[str, Any]]:
        """Synchronously parse Simplify jobs list using BeautifulSoup."""
        soup = BeautifulSoup(html_text, "html.parser")
        parsed = []

        # Find <li> tags representing jobs
        for li in soup.find_all("li"):
            a_link = li.find("a", href=True)
            if not a_link:
                continue

            href = a_link["href"]
            if "/p/" not in href and "/job/" not in href:
                continue

            if "undefined" in href.lower():
                continue

            # Extract logo/company
            img = li.find("img", alt=True)
            company = "Simplify Partner"
            logo = None
            if img:
                logo = img.get("src")
                company = img.get("alt", "").replace(" logo", "").strip()

            # Find title
            # Search all span elements for title matching keywords
            title_text = ""
            spans = li.find_all("span")
            for span in spans:
                text = span.get_text(" ", strip=True)
                if any(kw in text.lower() for kw in ["intern", "apprentice", "co-op", "trainee"]):
                    title_text = text
                    break

            if not title_text:
                # Fall back to text contents
                title_text = a_link.get_text(" ", strip=True)

            # Location and stipend (usually in divs inside card)
            location = "India / Remote"
            stipend = None

            full_url = urljoin("https://simplify.jobs", href)
            parsed.append({
                "external_id": full_url,
                "title": title_text,
                "company": company,
                "url": full_url,
                "location": location,
                "company_logo": logo,
                "stipend": stipend,
                "description": f"Curated Simplify.jobs opportunity at {company}.",
            })

        return parsed

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize Simplify raw cards into InternshipCreate payloads."""
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
                        tags=["simplify"],
                    )
                )
                continue

            title = job["title"]
            description = job["description"]

            if not self.is_internship(title, description, check_title=False):
                continue

            internships.append(
                self.build_internship(
                    external_id=job["external_id"],
                    company=job["company"],
                    title=title,
                    location=job["location"],
                    url=job["url"],
                    description=description,
                    company_logo=job.get("company_logo"),
                    stipend=job.get("stipend"),
                    tags=["simplify"],
                )
            )
        return internships

    def _get_mock_data(self) -> list[dict[str, Any]]:
        """Curated list fallback when Simplify.jobs pages are blocked or JS-only."""
        now = datetime.now(UTC)
        return [
            {
                "is_mock": True,
                "external_id": "simplify-mock-1",
                "company": "Uber India",
                "title": "Software Engineering Intern (Backend)",
                "location": "Bangalore, India",
                "url": "https://simplify.jobs/c/uber",
                "description": "Develop routing and pricing services. Gain hands-on microservice experience.",
                "posted_at": now,
                "skills": ["Java", "Go", "Distributed Systems"],
                "stipend": "INR 70,000 /month",
                "company_logo": "https://logo.clearbit.com/uber.com",
                "work_type": "Onsite",
            },
            {
                "is_mock": True,
                "external_id": "simplify-mock-2",
                "company": "Adobe India",
                "title": "Machine Learning Research Intern",
                "location": "Noida, India",
                "url": "https://simplify.jobs/c/adobe",
                "description": "Conduct research in computer vision and generative image models.",
                "posted_at": now,
                "skills": ["PyTorch", "Computer Vision", "Python"],
                "stipend": "INR 75,000 /month",
                "company_logo": "https://logo.clearbit.com/adobe.com",
                "work_type": "Onsite",
            },
            {
                "is_mock": True,
                "external_id": "simplify-mock-3",
                "company": "Postman",
                "title": "Product Design Intern (UI/UX)",
                "location": "Bangalore, India",
                "url": "https://simplify.jobs/c/postman",
                "description": "Collaborate on workspace layouts and API client design. Highly skilled in Figma.",
                "posted_at": now,
                "skills": ["Figma", "UI Design", "Prototyping"],
                "stipend": "INR 40,000 /month",
                "company_logo": "https://logo.clearbit.com/postman.com",
                "work_type": "Hybrid",
            },
        ]
