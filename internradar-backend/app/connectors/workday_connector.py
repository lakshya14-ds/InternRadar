"""Workday ATS connector and reusable parser."""

from typing import Any
from urllib.parse import urlparse

import asyncio
import logging

import httpx

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

# Workday career-site API endpoints for companies with India offices.
# Pattern: https://<tenant>.wd<n>.myworkdayjobs.com/wday/cxs/<tenant>/<board>/jobs
WORKDAY_SITES: list[dict[str, str]] = [
    # ── Indian-origin companies ─────────────────────────────────────────────
    {
        "name": "Infosys",
        "url": "https://infosys.wd3.myworkdayjobs.com/wday/cxs/infosys/Infosys/jobs",
    },
    {
        "name": "Wipro",
        "url": "https://wipro.wd3.myworkdayjobs.com/wday/cxs/wipro/WiproJobs/jobs",
    },
    {
        "name": "HCL Technologies",
        "url": "https://hcltech.wd3.myworkdayjobs.com/wday/cxs/hcltech/HCLTechCareers/jobs",
    },
    {
        "name": "Tech Mahindra",
        "url": "https://techmahindra.wd3.myworkdayjobs.com/wday/cxs/techmahindra/External/jobs",
    },
    {
        "name": "Mphasis",
        "url": "https://mphasis.wd3.myworkdayjobs.com/wday/cxs/mphasis/MphasisCareers/jobs",
    },
    {
        "name": "L&T Technology Services",
        "url": "https://ltts.wd3.myworkdayjobs.com/wday/cxs/ltts/LTTS_External/jobs",
    },
    {
        "name": "Persistent Systems",
        "url": "https://persistent.wd3.myworkdayjobs.com/wday/cxs/persistent/PersistentCareers/jobs",
    },
    {
        "name": "Coforge",
        "url": "https://coforge.wd3.myworkdayjobs.com/wday/cxs/coforge/CoforgeJobs/jobs",
    },
    {
        "name": "Hexaware",
        "url": "https://hexaware.wd3.myworkdayjobs.com/wday/cxs/hexaware/HexawareCareers/jobs",
    },
    {
        "name": "NIIT Technologies",
        "url": "https://niit.wd3.myworkdayjobs.com/wday/cxs/niit/NIITCareers/jobs",
    },
    # ── Global MNCs with large India engineering centres ────────────────────
    {
        "name": "Accenture India",
        "url": "https://accenture.wd3.myworkdayjobs.com/wday/cxs/accenture/AccentureJobs/jobs",
    },
    {
        "name": "Capgemini India",
        "url": "https://capgemini.wd3.myworkdayjobs.com/wday/cxs/capgemini/CapgeminiCareers/jobs",
    },
    {
        "name": "Cognizant",
        "url": "https://cognizant.wd1.myworkdayjobs.com/wday/cxs/cognizant/CognizantCareers/jobs",
    },
    {
        "name": "IBM India",
        "url": "https://ibm.wd3.myworkdayjobs.com/wday/cxs/ibm/IBMExternalSite/jobs",
    },
    {
        "name": "SAP Labs India",
        "url": "https://sap.wd3.myworkdayjobs.com/wday/cxs/sap/SAPCareers/jobs",
    },
    {
        "name": "Qualcomm India",
        "url": "https://qualcomm.wd5.myworkdayjobs.com/wday/cxs/qualcomm/External/jobs",
    },
    {
        "name": "Micron Technology India",
        "url": "https://micron.wd1.myworkdayjobs.com/wday/cxs/micron/External/jobs",
    },
    {
        "name": "Texas Instruments India",
        "url": "https://ti.wd5.myworkdayjobs.com/wday/cxs/ti/TIExternalStud/jobs",
    },
]


class WorkdayParser:
    """Parse common Workday job response shapes."""

    def extract_jobs(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract job records from a Workday payload."""

        if "jobPostings" in payload:
            return list(payload.get("jobPostings", []))
        body = payload.get("body", {})
        children = body.get("children", [])
        return [item for item in children if isinstance(item, dict)]


class WorkdayConnector(BaseConnector):
    """Generic Workday integration layer for configured career sites."""

    source = "workday"

    def __init__(self, sites: list[dict[str, str]] | None = None) -> None:
        self.sites = sites if sites is not None else WORKDAY_SITES
        self.parser = WorkdayParser()

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Return configured Workday sites."""

        return list(self.sites)

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fetch jobs from configured Workday endpoints."""

        async def fetch_company(client: httpx.AsyncClient, company: dict[str, Any]) -> list[dict[str, Any]]:
            url = company["url"]
            parsed_url = urlparse(url)
            origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Extract board from URL: e.g. /wday/cxs/infosys/Infosys/jobs -> parts[3]
            parts = parsed_url.path.strip("/").split("/")
            board = parts[3] if len(parts) >= 4 else company.get("name", "")
            
            referer = f"{origin}/en-US/{board}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Origin": origin,
                "Referer": referer
            }
            
            payload = {
                "appliedFacets": {},
                "limit": 20,
                "offset": 0,
                "searchText": ""
            }

            try:
                response = await asyncio.wait_for(
                    client.post(url, json=payload, headers=headers),
                    timeout=3.0
                )
                response.raise_for_status()
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                logger.debug("Workday site skipped: %s (%s)", company.get("name", ""), exc)
                return []

            jobs = self.parser.extract_jobs(response.json())
            for job in jobs:
                job["company_name"] = company.get("name", "")
                job["careers_url"] = company.get("url", "")
            return jobs

        timeout = httpx.Timeout(3.0)
        limits = httpx.Limits(max_keepalive_connections=50, max_connections=150)
        async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
            results = await asyncio.gather(
                *(fetch_company(client, company) for company in companies),
                return_exceptions=True,
            )

        jobs: list[dict[str, Any]] = []
        for result in results:
            if isinstance(result, Exception):
                logger.debug("Workday site fetch failed: %s", result)
                continue
            jobs.extend(result)
        return jobs

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize Workday jobs — India locations, internships only."""

        internships: list[InternshipCreate] = []
        for job in raw_jobs:
            title = job.get("title", "") or job.get("externalPath", "")
            description = job.get("description", "")

            if not self.is_internship(title, description):
                continue

            location = job.get("locationsText", "")

            if not self.is_india_location(location):
                continue

            external_path = job.get("externalPath", "")
            base_url = job.get("careers_url", "")
            url = base_url
            if external_path and base_url:
                parsed_url = urlparse(base_url)
                host = parsed_url.netloc
                parts = parsed_url.path.strip("/").split("/")
                board = parts[3] if len(parts) >= 4 else ""
                if board:
                    url = f"https://{host}/en-US/{board}{external_path}"
                else:
                    url = f"https://{host}/en-US{external_path}"

            internships.append(
                self.build_internship(
                    external_id=str(job.get("bulletFields", [external_path])[0] or external_path),
                    company=job.get("company_name", ""),
                    title=title,
                    location=location,
                    url=url,
                    description=description,
                    tags=["ats", "workday"],
                )
            )
        return internships
