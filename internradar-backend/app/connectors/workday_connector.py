"""Workday ATS connector and reusable parser."""

from typing import Any

import requests

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

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

        jobs: list[dict[str, Any]] = []
        for company in companies:
            try:
                response = requests.get(company["url"], timeout=20)
                response.raise_for_status()
            except requests.RequestException:
                continue
            for job in self.parser.extract_jobs(response.json()):
                job["company_name"] = company.get("name", "")
                job["careers_url"] = company.get("url", "")
                jobs.append(job)
        return jobs

    async def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
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
            internships.append(
                self.build_internship(
                    external_id=str(job.get("bulletFields", [external_path])[0] or external_path),
                    company=job.get("company_name", ""),
                    title=title,
                    location=location,
                    url=f"{base_url}{external_path}" if external_path else base_url,
                    description=description,
                    tags=["ats", "workday"],
                )
            )
        return internships
