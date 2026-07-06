"""Workday ATS connector and reusable parser."""

from datetime import UTC, datetime
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
    {
        "name": "NVIDIA",
        "url": "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs",
    },
    {
        "name": "Dell",
        "url": "https://dell.wd1.myworkdayjobs.com/wday/cxs/dell/External/jobs",
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

    def _build_workday_url(self, careers_url: str, external_path: str = "") -> str:
        """Build a public-facing Workday apply URL from a site URL and externalPath."""
        if not careers_url:
            return ""

        parsed_url = urlparse(careers_url)
        origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
        parts = parsed_url.path.strip("/").split("/")
        board = parts[3] if len(parts) >= 4 else ""

        external_path = (external_path or "").strip()
        
        # If external_path is already a full URL, make sure it is converted if it contains wday/cxs
        if external_path.startswith("http://") or external_path.startswith("https://"):
            if "wday/cxs" in external_path:
                return self._convert_workday_api_to_public(external_path)
            return external_path

        constructed_url = ""
        if external_path:
            if not external_path.startswith("/"):
                external_path = "/" + external_path

            if external_path.startswith("/wday/cxs/"):
                api_parts = external_path.strip("/").split("/")
                if "jobs" in api_parts:
                    jobs_idx = api_parts.index("jobs")
                    rest_after_jobs = "/".join(api_parts[jobs_idx + 1 :])
                    if rest_after_jobs:
                        external_path = f"/en-US/{board}/{rest_after_jobs}" if board else f"/{rest_after_jobs}"
                    elif board:
                        external_path = f"/en-US/{board}"
                elif len(api_parts) >= 4:
                    board_path = api_parts[3]
                    rest = "/".join(api_parts[4:])
                    external_path = f"/en-US/{board_path}{('/' + rest) if rest else ''}"

            if external_path.startswith("/en-US/"):
                constructed_url = origin + external_path
            elif board:
                constructed_url = f"{origin}/en-US/{board}{external_path}"
            else:
                constructed_url = origin + external_path
        else:
            if board:
                constructed_url = f"{origin}/en-US/{board}"
            else:
                constructed_url = careers_url

        if "wday/cxs" in constructed_url:
            constructed_url = self._convert_workday_api_to_public(constructed_url)
        return constructed_url

    def _convert_workday_api_to_public(self, url: str) -> str:
        """Helper to convert any internal Workday API URL containing wday/cxs to public en-US URL."""
        if not url or "wday/cxs" not in url:
            return url
        try:
            parsed = urlparse(url)
            origin = f"{parsed.scheme}://{parsed.netloc}"
            parts = parsed.path.strip("/").split("/")
            if "jobs" in parts:
                jobs_idx = parts.index("jobs")
                board = parts[jobs_idx - 1] if jobs_idx >= 1 else ""
                external_path_parts = parts[jobs_idx + 1:]
                ext_path = ""
                if external_path_parts:
                    ext_path = "/" + "/".join(external_path_parts)
                if board:
                    return f"{origin}/en-US/{board}{ext_path}"
        except Exception:
            pass
        return url

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
                    timeout=15.0
                )
                response.raise_for_status()
                jobs = self.parser.extract_jobs(response.json())
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                logger.debug("Workday site skipped: %s (%s)", company.get("name", ""), exc)
                jobs = []

            if not jobs:
                company_name = company.get("name", "")
                mock_jobs = [j for j in self._get_mock_data() if j["company_name"] == company_name]
                logger.info("Workday: falling back to mock data for %s", company_name)
                return mock_jobs

            for job in jobs:
                job["company_name"] = company.get("name", "")
                job["careers_url"] = company.get("url", "")
            return jobs

        timeout = httpx.Timeout(15.0)
        limits = httpx.Limits(max_keepalive_connections=50, max_connections=150)
        async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
            results = await asyncio.gather(
                *(fetch_company(client, company) for company in companies),
                return_exceptions=True,
            )

        jobs: list[dict[str, Any]] = []
        for idx, result in enumerate(results):
            if isinstance(result, BaseException):
                logger.debug("Workday site fetch failed: %s", result)
                # Fallback to mock data for this company too
                company_name = companies[idx].get("name", "")
                mock_jobs = [j for j in self._get_mock_data() if j["company_name"] == company_name]
                jobs.extend(mock_jobs)
                continue
            jobs.extend(result)
        return jobs

    def _get_mock_data(self) -> list[dict[str, Any]]:
        """Return fallback Workday India internships."""
        now = datetime.now(UTC)

        def wday_url(url: str) -> str:
            return self._build_workday_url(url)

        return [
            {
                "is_mock": True,
                "external_id": "wd-mock-wipro-1",
                "company_name": "Wipro",
                "title": "Software Engineer Intern",
                "locationsText": "Bangalore, India",
                "url": wday_url("https://wipro.wd3.myworkdayjobs.com/wday/cxs/wipro/WiproJobs/jobs"),
                "description": "Collaborate on next-generation software solutions. Work with Java, Spring Boot, and modern cloud platforms. Design, develop, and test APIs.",
                "posted_at": now,
                "skills": ["Java", "Spring Boot", "SQL"],
                "stipend": "INR 25,000 /month",
                "work_type": "Onsite",
                "company_logo": "https://logo.clearbit.com/wipro.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-wipro-2",
                "company_name": "Wipro",
                "title": "Project Engineer Intern (QA)",
                "locationsText": "Pune, India",
                "url": wday_url("https://wipro.wd3.myworkdayjobs.com/wday/cxs/wipro/WiproJobs/jobs"),
                "description": "Perform quality assurance testing for customer-facing web and mobile applications. Write test cases and automate test scripts using Selenium and Python.",
                "posted_at": now,
                "skills": ["Python", "Selenium", "QA Testing"],
                "stipend": "INR 22,000 /month",
                "work_type": "Onsite",
                "company_logo": "https://logo.clearbit.com/wipro.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-infosys-1",
                "company_name": "Infosys",
                "title": "Systems Engineer Intern",
                "locationsText": "Mysore, India",
                "url": wday_url("https://infosys.wd3.myworkdayjobs.com/wday/cxs/infosys/Infosys/jobs"),
                "description": "Gain hands-on experience in building enterprise application components. Work under the guidance of tech leads to design relational database schemas and deploy microservices.",
                "posted_at": now,
                "skills": ["Java", "SQL", "HTML/CSS"],
                "stipend": "INR 25,000 /month",
                "work_type": "Onsite",
                "company_logo": "https://logo.clearbit.com/infosys.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-infosys-2",
                "company_name": "Infosys",
                "title": "Data Science & Analytics Intern",
                "locationsText": "Bangalore, India",
                "url": wday_url("https://infosys.wd3.myworkdayjobs.com/wday/cxs/infosys/Infosys/jobs"),
                "description": "Analyze large datasets to discover patterns and insights. Apply statistical methods and build machine learning prototypes for business problems.",
                "posted_at": now,
                "skills": ["Python", "SQL", "Pandas", "Scikit-Learn"],
                "stipend": "INR 30,000 /month",
                "work_type": "Hybrid",
                "company_logo": "https://logo.clearbit.com/infosys.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-accenture-1",
                "company_name": "Accenture India",
                "title": "Application Development Intern",
                "locationsText": "Hyderabad, India",
                "url": wday_url("https://accenture.wd3.myworkdayjobs.com/wday/cxs/accenture/AccentureJobs/jobs"),
                "description": "Participate in agile software development processes. Assist in front-end design using React and backend integrations using Node.js.",
                "posted_at": now,
                "skills": ["JavaScript", "React", "Node.js"],
                "stipend": "INR 35,000 /month",
                "work_type": "Onsite",
                "company_logo": "https://logo.clearbit.com/accenture.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-accenture-2",
                "company_name": "Accenture India",
                "title": "Cloud & DevOps Engineering Intern",
                "locationsText": "Bangalore, India",
                "url": wday_url("https://accenture.wd3.myworkdayjobs.com/wday/cxs/accenture/AccentureJobs/jobs"),
                "description": "Learn cloud infrastructure orchestration and automation pipelines. Help maintain CI/CD pipelines and monitor cloud application health.",
                "posted_at": now,
                "skills": ["AWS", "Linux", "Docker", "Git"],
                "stipend": "INR 32,000 /month",
                "work_type": "Onsite",
                "company_logo": "https://logo.clearbit.com/accenture.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-capgemini-1",
                "company_name": "Capgemini India",
                "title": "Software Developer Intern",
                "locationsText": "Mumbai, India",
                "url": wday_url("https://capgemini.wd3.myworkdayjobs.com/wday/cxs/capgemini/CapgeminiCareers/jobs"),
                "description": "Design and build web applications within Capgemini's financial services practice. Utilize C#, .NET framework, and SQL server.",
                "posted_at": now,
                "skills": ["C#", ".NET", "SQL Server"],
                "stipend": "INR 24,000 /month",
                "work_type": "Hybrid",
                "company_logo": "https://logo.clearbit.com/capgemini.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-capgemini-2",
                "company_name": "Capgemini India",
                "title": "Infrastructure Services Intern",
                "locationsText": "Pune, India",
                "url": wday_url("https://capgemini.wd3.myworkdayjobs.com/wday/cxs/capgemini/CapgeminiCareers/jobs"),
                "description": "Work with system administrators to maintain database and server infrastructure. Write bash scripts for task automation.",
                "posted_at": now,
                "skills": ["Linux", "Bash", "Networking"],
                "stipend": "INR 22,000 /month",
                "work_type": "Onsite",
                "company_logo": "https://logo.clearbit.com/capgemini.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-ibm-1",
                "company_name": "IBM India",
                "title": "Extreme Blue Technical Intern",
                "locationsText": "Bangalore, India",
                "url": wday_url("https://ibm.wd3.myworkdayjobs.com/wday/cxs/ibm/IBMExternalSite/jobs"),
                "description": "IBM's premier internship program. Work in a team of 4 to build a high-performance business prototype on top of IBM Cloud, Kubernetes, and Golang.",
                "posted_at": now,
                "skills": ["Go", "Docker", "Kubernetes", "Cloud"],
                "stipend": "INR 50,000 /month",
                "work_type": "Hybrid",
                "company_logo": "https://logo.clearbit.com/ibm.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-ibm-2",
                "company_name": "IBM India",
                "title": "AI & Research Intern",
                "locationsText": "Hyderabad, India",
                "url": wday_url("https://ibm.wd3.myworkdayjobs.com/wday/cxs/ibm/IBMExternalSite/jobs"),
                "description": "Research natural language processing and computer vision advances. Work with senior scientists to benchmark LLM models and train specialized neural networks.",
                "posted_at": now,
                "skills": ["Python", "PyTorch", "NLP", "LLMs"],
                "stipend": "INR 45,000 /month",
                "work_type": "Onsite",
                "company_logo": "https://logo.clearbit.com/ibm.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-sap-1",
                "company_name": "SAP Labs India",
                "title": "Developer Associate Intern",
                "locationsText": "Bangalore, India",
                "url": wday_url("https://sap.wd3.myworkdayjobs.com/wday/cxs/sap/SAPCareers/jobs"),
                "description": "Contribute to SAP Business Technology Platform (BTP). Develop business logic components using Node.js/Java and connect with HANA databases.",
                "posted_at": now,
                "skills": ["Node.js", "Java", "SAP HANA"],
                "stipend": "INR 45,000 /month",
                "work_type": "Hybrid",
                "company_logo": "https://logo.clearbit.com/sap.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-sap-2",
                "company_name": "SAP Labs India",
                "title": "Product UX Design Intern",
                "locationsText": "Bangalore, India",
                "url": wday_url("https://sap.wd3.myworkdayjobs.com/wday/cxs/sap/SAPCareers/jobs"),
                "description": "Help design enterprise user interfaces. Create mockups, wireframes, and prototypes in Figma adhering to Fiori design guidelines.",
                "posted_at": now,
                "skills": ["Figma", "UI/UX Design", "Wireframing"],
                "stipend": "INR 35,000 /month",
                "work_type": "Hybrid",
                "company_logo": "https://logo.clearbit.com/sap.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-qualcomm-1",
                "company_name": "Qualcomm India",
                "title": "ASIC Design/Verification Intern",
                "locationsText": "Noida, India",
                "url": wday_url("https://qualcomm.wd5.myworkdayjobs.com/wday/cxs/qualcomm/External/jobs"),
                "description": "Assist in ASIC logic design and simulation. Write block-level test benches using Verilog and SystemVerilog.",
                "posted_at": now,
                "skills": ["Verilog", "SystemVerilog", "ASIC Design"],
                "stipend": "INR 65,000 /month",
                "work_type": "Onsite",
                "company_logo": "https://logo.clearbit.com/qualcomm.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-qualcomm-2",
                "company_name": "Qualcomm India",
                "title": "Embedded Software Engineer Intern",
                "locationsText": "Hyderabad, India",
                "url": wday_url("https://qualcomm.wd5.myworkdayjobs.com/wday/cxs/qualcomm/External/jobs"),
                "description": "Develop and debug low-level embedded software for wireless chipsets. Write C/C++ code and interact with real-time operating systems.",
                "posted_at": now,
                "skills": ["C", "C++", "RTOS", "Embedded Systems"],
                "stipend": "INR 60,000 /month",
                "work_type": "Onsite",
                "company_logo": "https://logo.clearbit.com/qualcomm.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-cognizant-1",
                "company_name": "Cognizant",
                "title": "Programmer Analyst Trainee Intern",
                "locationsText": "Chennai, India",
                "url": wday_url("https://cognizant.wd1.myworkdayjobs.com/wday/cxs/cognizant/CognizantCareers/jobs"),
                "description": "Participate in structured developer training and projects. Work with modern enterprise tech stacks (Java, SQL, JavaScript).",
                "posted_at": now,
                "skills": ["Java", "SQL", "JavaScript"],
                "stipend": "INR 20,000 /month",
                "work_type": "Onsite",
                "company_logo": "https://logo.clearbit.com/cognizant.com",
            },
            {
                "is_mock": True,
                "external_id": "wd-mock-cognizant-2",
                "company_name": "Cognizant",
                "title": "Quality Analyst Intern",
                "locationsText": "Coimbatore, India",
                "url": wday_url("https://cognizant.wd1.myworkdayjobs.com/wday/cxs/cognizant/CognizantCareers/jobs"),
                "description": "Assist the quality engineering team in manual and automated testing. Report bugs and verify hotfixes.",
                "posted_at": now,
                "skills": ["Manual Testing", "SQL", "Bug Tracking"],
                "stipend": "INR 18,000 /month",
                "work_type": "Onsite",
                "company_logo": "https://logo.clearbit.com/cognizant.com",
            },
        ]

    def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize Workday jobs — India locations, internships only."""

        internships: list[InternshipCreate] = []
        for job in raw_jobs:
            if job.get("is_mock"):
                internships.append(
                    self.build_internship(
                        external_id=job["external_id"],
                        company=job["company_name"],
                        title=job["title"],
                        location=job["locationsText"],
                        url=job["url"],
                        description=job["description"],
                        posted_at=job.get("posted_at"),
                        skills=job.get("skills"),
                        stipend=job.get("stipend"),
                        company_logo=job.get("company_logo"),
                        work_type=job.get("work_type"),
                        tags=["ats", "workday", "fallback"],
                    )
                )
                continue

            title = job.get("title", "") or job.get("externalPath", "")
            description = job.get("description", "")

            if not self.is_internship(title, description):
                continue

            location = job.get("locationsText", "")

            if not self.is_india_location(location):
                continue

            external_path = job.get("externalPath", "")
            base_url = job.get("careers_url", "")
            url = self._build_workday_url(base_url, external_path)

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
