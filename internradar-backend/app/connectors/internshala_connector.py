"""Internshala dedicated connector."""

import asyncio
from datetime import UTC, datetime, timedelta
import logging
from typing import Any
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)


class InternshalaConnector(BaseConnector):
    """Retrieve internships directly from Internshala listing pages."""

    source = "internshala"

    def __init__(self) -> None:
        categories = [
            "",
            "engineering-internship",
            "computer-science-internship",
            "data-science-internship",
        ]
        self.urls = []
        for cat in categories:
            for page in range(1, 6):
                cat_part = f"{cat}/" if cat else ""
                if page == 1:
                    self.urls.append(f"https://internshala.com/internships/{cat_part}")
                else:
                    self.urls.append(f"https://internshala.com/internships/{cat_part}page-{page}")

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Return configured Internshala listings URLs."""
        return [{"name": f"Internshala Listing {i}", "url": url} for i, url in enumerate(self.urls)]

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fetch raw listing cards from Internshala pages."""
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
                return await asyncio.to_thread(self._parse_page, response.text, url)
            except Exception as exc:
                logger.debug("Failed to fetch Internshala page %s: %s", url, exc)
                return []

        timeout = httpx.Timeout(15.0)
        limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
        async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
            results = await asyncio.gather(
                *(fetch_url(client, company) for company in companies),
                return_exceptions=True,
            )

        jobs: list[dict[str, Any]] = []
        for r in results:
            if isinstance(r, list):
                jobs.extend(r)
        return jobs

    def _parse_page(self, html_text: str, base_url: str) -> list[dict[str, Any]]:
        """Synchronously parse html using BeautifulSoup inside threadpool."""
        soup = BeautifulSoup(html_text, "html.parser")
        cards = soup.select(".individual_internship")
        parsed = []

        for card in cards:
            # Check employment type
            etype = card.get("employment_type", "internship")
            if etype != "internship":
                continue

            link_el = card.select_one("a.job-title-href")
            if not link_el:
                continue

            title = link_el.get_text(" ", strip=True)
            href = link_el.get("href", "")
            if not href or "/training/" in href or "/online-trainings/" in href:
                continue

            # Ensure direct detail link
            href_str = str(href).strip()
            if not href_str.startswith("http"):
                if not href_str.startswith("/"):
                    href_str = "/" + href_str
                # Make direct detail URL
                if "/detail/" in href_str:
                    slug = href_str.split("/detail/")[-1]
                    href_str = f"/internship/detail/{slug}"
                url = urljoin("https://internshala.com", href_str)
            else:
                url = href_str

            # Company
            company_el = card.select_one(".company-name")
            company = company_el.get_text(" ", strip=True) if company_el else "Unknown Company"

            # Logo
            logo_el = card.select_one(".internship_logo img")
            logo = logo_el.get("src") if logo_el else None
            if logo and not logo.startswith("http"):
                logo = urljoin("https://internshala.com", logo)

            # Location
            loc_el = card.select_one(".locations span a") or card.select_one(".locations span")
            location = loc_el.get_text(" ", strip=True) if loc_el else "India"

            # Stipend
            stipend_el = card.select_one(".stipend")
            stipend = stipend_el.get_text(" ", strip=True) if stipend_el else None

            # Duration
            duration = None
            for item in card.select(".row-1-item"):
                if item.select_one("i.ic-16-calendar"):
                    duration_span = item.select_one("span")
                    if duration_span:
                        duration = duration_span.get_text(" ", strip=True)
                    break

            # Skills
            skills = [s.get_text(" ", strip=True) for s in card.select(".job_skill")]

            # Description (quick text overview)
            desc_el = card.select_one(".about_job .text")
            description = desc_el.get_text(" ", strip=True) if desc_el else ""

            # Posted date
            posted_text = ""
            posted_el = card.select_one(".status-info span")
            if posted_el:
                posted_text = posted_el.get_text(" ", strip=True)

            parsed.append({
                "external_id": url,
                "title": title,
                "url": url,
                "company": company,
                "logo": logo,
                "location": location,
                "stipend": stipend,
                "duration": duration,
                "skills": skills,
                "description": description,
                "posted_text": posted_text,
            })
        return parsed

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize parsed Internshala raw cards into InternshipCreate payloads."""
        internships: list[InternshipCreate] = []
        for job in raw_jobs:
            title = job["title"]
            description = job["description"]

            if not self.is_internship(title, description, check_title=False):
                continue

            location = job["location"]
            if not self.is_india_location(location):
                continue

            # Parse posted date
            posted_at = datetime.now(UTC)
            posted_text = job["posted_text"].lower()
            match = re.search(r"(\d+)\s+days?\s+ago", posted_text)
            if match:
                days = int(match.group(1))
                posted_at = datetime.now(UTC) - timedelta(days=days)
            elif "today" in posted_text or "just now" in posted_text:
                posted_at = datetime.now(UTC)

            internships.append(
                self.build_internship(
                    external_id=job["external_id"],
                    company=job["company"],
                    title=title,
                    location=location,
                    url=job["url"],
                    description=description,
                    posted_at=posted_at,
                    skills=job["skills"],
                    stipend=job["stipend"],
                    duration=job["duration"],
                    company_logo=job["logo"],
                    tags=["internshala"],
                )
            )
        return internships
