"""ATS Discovery Engine to auto-detect and persist company ATS platforms."""

import asyncio
import logging
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

import httpx
from motor.motor_asyncio import AsyncIOMotorCollection

from app.models.company import CompanyInDB

logger = logging.getLogger(__name__)


class ATSDiscoveryService:
    """Service to automatically probe and register company ATS portals."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection

    def _slugify(self, text: str) -> str:
        """Convert company name to slug, e.g. 'Tata Consultancy Services' -> 'tata-consultancy-services'."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        return re.sub(r"[\s_]+", "-", text)

    async def detect_ats(self, company_name: str) -> tuple[str, str] | None:
        """Probe common ATS endpoints for the company name or slug."""
        slug = self._slugify(company_name)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(headers=headers, timeout=3.0, follow_redirects=True) as client:
            # 1. Greenhouse probe
            try:
                res = await client.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
                if res.status_code == 200:
                    return "greenhouse", f"https://boards.greenhouse.io/{slug}"
            except Exception:
                pass

            # 2. Lever probe
            try:
                res = await client.get(f"https://api.lever.co/v0/postings/{slug}?mode=json")
                if res.status_code == 200:
                    return "lever", f"https://lever.co/{slug}"
            except Exception:
                pass

            # 3. Ashby probe
            try:
                res = await client.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
                if res.status_code == 200:
                    return "ashby", f"https://jobs.ashbyhq.com/{slug}"
            except Exception:
                pass

            # 4. SmartRecruiters probe
            try:
                res = await client.get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings")
                if res.status_code == 200:
                    return "smartrecruiters", f"https://jobs.smartrecruiters.com/{slug}"
            except Exception:
                pass

            # 5. Workday check (Workday does not have a single central slug registry, but we check if we can query it)
            # Typically requires exact host, but we can search for Workday patterns if a career URL is explicitly provided.
            
        return None

    async def discover_and_register(self, company_name: str, careers_url: str | None = None) -> dict[str, Any] | None:
        """Detect the ATS system and register the company if successful."""
        provider = None
        url = careers_url

        if url:
            # Explicit URL provided
            parsed = urlparse(url.lower())
            host = parsed.netloc
            path = parsed.path
            
            if "greenhouse.io" in host:
                provider = "greenhouse"
                # Extract board slug
                parts = path.strip("/").split("/")
                slug = parts[0] if parts else company_name.lower()
                url = f"https://boards.greenhouse.io/{slug}"
            elif "lever.co" in host:
                provider = "lever"
                parts = path.strip("/").split("/")
                slug = parts[0] if parts else company_name.lower()
                url = f"https://lever.co/{slug}"
            elif "ashbyhq.com" in host:
                provider = "ashby"
                parts = path.strip("/").split("/")
                slug = parts[0] if parts else company_name.lower()
                url = f"https://jobs.ashbyhq.com/{slug}"
            elif "smartrecruiters.com" in host:
                provider = "smartrecruiters"
                parts = path.strip("/").split("/")
                slug = parts[0] if parts else company_name.lower()
                url = f"https://jobs.smartrecruiters.com/{slug}"
            elif "myworkdayjobs.com" in host:
                provider = "workday"
                # e.g., https://wipro.wd3.myworkdayjobs.com/wday/cxs/wipro/WiproJobs/jobs
                tenant = host.split(".")[0]
                board = path.strip("/").split("/")[-2] if len(path.strip("/").split("/")) >= 2 else tenant
                url = f"https://{host}/wday/cxs/{tenant}/{board}/jobs"
        
        if not provider:
            # Auto-detect using probe logic
            detection = await self.detect_ats(company_name)
            if detection:
                provider, url = detection

        if not provider or not url:
            logger.info("Could not detect any public ATS system for company %s", company_name)
            return None

        # Store in database
        document = {
            "name": company_name.strip(),
            "ats_provider": provider,
            "careers_url": url,
            "active": True,
            "last_checked": datetime.now(UTC),
        }

        try:
            # Check if company already registered
            existing = await self.collection.find_one({
                "ats_provider": provider,
                "name": company_name.strip()
            })
            if existing:
                logger.info("Company %s already registered under %s ATS", company_name, provider)
                return existing

            result = await self.collection.insert_one(document)
            document["_id"] = result.inserted_id
            logger.info("Successfully registered discovered company %s using %s ATS", company_name, provider)
            return document
        except Exception as exc:
            logger.error("Failed to persist discovered company: %s", exc)
            return None
