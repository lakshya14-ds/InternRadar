"""Base connector contract for ATS and manual sources."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
import logging
import re
from typing import Any

from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)

# ── Phase 1: title must contain at least one of these ────────────────────────
# Checked on TITLE ONLY — description is too noisy ("we are hiring for an
# intern-facing product" would match otherwise).
INTERNSHIP_TITLE_KEYWORDS = (
    "intern",
    "internship",
    "trainee",
    "apprentice",
    "graduate trainee",
    "industrial trainee",
    "summer trainee",
    "winter trainee",
    "project trainee",
    "student trainee",
)

# ── Phase 2: title must NOT contain any of these ─────────────────────────────
NON_INTERNSHIP_TITLE_KEYWORDS = (
    "senior",
    "sr.",
    "sr ",
    "staff ",
    "lead ",
    "principal",
    "director",
    "manager",
    "head of",
    "vp ",
    "avp ",
    "svp ",
    "evp ",
    "vice president",
    "associate vice president",
    "president",
    "c-level",
    "cto",
    "ceo",
    "cfo",
    "coo",
    "chief ",
    "architect",
    "consultant",
    "contract ",
    "contractor",
    "freelance",
    "part-time",
    "part time",
    "full-time",
    "full time",
    "permanent",
    "experienced",
    "mid-level",
    "mid level",
    "associate -",      # "Associate - Finance" style senior role patterns
)

# ── Phase 3: description must NOT contain any of these ───────────────────────
# Patterns handle both ASCII hyphen (-) and Unicode en-dash (–, \u2013) and
# em-dash (—, \u2014) because Indian ATS job descriptions frequently use
# en-dashes in experience ranges like "EXPERIENCE 7 – 10 Years".
NON_INTERNSHIP_DESCRIPTION_PATTERNS: tuple[re.Pattern, ...] = (
    # "X – Y Years [of experience]" or "X+ Years" where X >= 2
    # Catches: "7 – 10 Years", "2+ years", "3 years of experience"
    re.compile(
        r"\b([2-9]|\d{2,})\s*[\u2013\u2014\-\+]?\s*\d*\s*years?\s*(of\s*)?(experience|exp)?\b",
        re.IGNORECASE,
    ),
    # "EXPERIENCE: X – Y Years" label-value format common in Indian JDs
    # Catches: "EXPERIENCE 7 – 10 Years", "Experience: 5 years"
    re.compile(
        r"\bexperience\s*[:\-]?\s*\d+\s*[\u2013\u2014\-\+]?\s*\d*\s*years?\b",
        re.IGNORECASE,
    ),
    # "minimum X years" / "at least X years" where X >= 2
    re.compile(r"\b(minimum|at\s+least)\s+([2-9]|\d{2,})\s*years?\b", re.IGNORECASE),
    # "Senior Manager / Senior Engineer" as a job title in the description body
    re.compile(
        r"\bsenior\s+(manager|engineer|analyst|consultant|associate|developer|architect)\b",
        re.IGNORECASE,
    ),
    # "CTC: 15 LPA" / "Salary: 20 Lakhs" — only appear in experienced-hire JDs
    re.compile(r"\b(ctc|salary)\s*[:\-]?\s*\d+\s*(lpa|lakh|lakhs|l\.p\.a)", re.IGNORECASE),
    # "CA / MBA" qualification combo signals a finance senior role
    re.compile(r"\bca\s*/\s*mba\b", re.IGNORECASE),
    # "MBA in Finance with 3 years" etc.
    re.compile(r"\bmba\s*(in\s+\w+)?\s+with\s+\d+\s*years?\b", re.IGNORECASE),
)

# ── Canonical Indian city / region tokens ────────────────────────────────────
INDIA_LOCATION_TOKENS = (
    "india",
    "bengaluru",
    "bangalore",
    "mumbai",
    "delhi",
    "new delhi",
    "ncr",
    "gurugram",
    "gurgaon",
    "noida",
    "hyderabad",
    "pune",
    "chennai",
    "kolkata",
    "ahmedabad",
    "jaipur",
    "surat",
    "indore",
    "chandigarh",
    "coimbatore",
    "kochi",
    "thiruvananthapuram",
    "trivandrum",
    "bhubaneswar",
    "nagpur",
    "lucknow",
    "vizag",
    "visakhapatnam",
    "vadodara",
    "mysuru",
    "mysore",
    "mangalore",
    "mangaluru",
    "patna",
    "ranchi",
    "bhopal",
    "in",   # ISO country code in structured location fields
)


class BaseConnector(ABC):
    """Abstract connector that exposes normalized internships."""

    source: str

    async def run(self) -> list[InternshipCreate]:
        """Run connector safely and return an empty list on failure."""

        try:
            companies = await self.discover_companies()
            raw_jobs = await self.fetch_jobs(companies)
            return await self.normalize(raw_jobs)
        except Exception:
            logger.exception("%s connector failed", self.source)
            return []

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Discover or return configured company boards for this connector."""

        return []

    @abstractmethod
    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fetch raw jobs for configured companies."""

    @abstractmethod
    async def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize raw jobs into the shared internship model."""

    def is_internship(self, title: str, description: str = "") -> bool:
        """Three-phase internship gate — all three must pass.

        Phase 1 — Title inclusion:
            Title must contain an internship keyword (intern, trainee, etc.).
            Description is intentionally excluded from Phase 1 because words
            like "intern-facing", "internal", or "interning team" appear in
            regular job descriptions and would produce false positives.

        Phase 2 — Title exclusion:
            Title must not contain a seniority/contract signal (senior, manager,
            director, full-time, contract, etc.) even if it also has an
            internship keyword (e.g. "Senior Internal Tools Engineer").

        Phase 3 — Description exclusion:
            Description must not contain strong experienced-hire signals:
            - "2+ years of experience" or any higher number
            - "Senior Manager / Senior Engineer" etc. in the body
            - "CA / MBA" qualification combos
            - Salary/CTC lines (only appear in experienced-hire JDs on Indian
              boards e.g. "CTC: 15 LPA")
            This is what catches the Paytm "Treasury Operations / Senior Manager
            – 7–10 years" case that previously slipped through.
        """

        title_lower = title.casefold()
        desc_lower = description.casefold()

        # ── Phase 1: title must look like an internship ───────────────────────
        if not any(kw in title_lower for kw in INTERNSHIP_TITLE_KEYWORDS):
            logger.debug("Phase1 fail (no internship keyword in title): %s", title)
            return False

        # ── Phase 2: title must not contain a seniority signal ────────────────
        if any(sig in title_lower for sig in NON_INTERNSHIP_TITLE_KEYWORDS):
            logger.debug("Phase2 fail (seniority keyword in title): %s", title)
            return False

        # ── Phase 3: description must not contain experienced-hire signals ────
        for pattern in NON_INTERNSHIP_DESCRIPTION_PATTERNS:
            if pattern.search(description):
                logger.debug(
                    "Phase3 fail (experienced-hire pattern '%s' in description): %s",
                    pattern.pattern,
                    title,
                )
                return False

        return True

    def is_india_location(self, location: str) -> bool:
        """Return True when the location resolves to India.

        Handles strings like:
          "Bangalore, India", "Bengaluru, KA, IN", "New Delhi", "NCR", "India"
        """

        if not location:
            return False

        loc = location.casefold().strip()

        for token in INDIA_LOCATION_TOKENS:
            pattern = r"(^|[\s,/\-])" + re.escape(token) + r"($|[\s,/\-])"
            if re.search(pattern, loc):
                return True

        return False

    def build_internship(
        self,
        external_id: str,
        company: str,
        title: str,
        location: str,
        url: str,
        description: str = "",
        posted_at: datetime | None = None,
        employment_type: str = "Internship",
        skills: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> InternshipCreate:
        """Build a normalized internship record."""

        clean_location = location.strip() or "Not specified"
        return InternshipCreate(
            external_id=external_id.strip(),
            source=self.source,
            company=company.strip(),
            title=title.strip(),
            location=clean_location,
            remote=False,
            employment_type=employment_type,
            url=url.strip(),
            description=description.strip(),
            posted_at=posted_at or datetime.now(UTC),
            skills=skills or [],
            tags=tags or [],
        )
