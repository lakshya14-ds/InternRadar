"""Business logic for storing and retrieving internships."""

import re
from datetime import UTC, datetime
import logging

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import DESCENDING
from pymongo.errors import DuplicateKeyError

from app.classification.company_classifier import (
    FEATURED_MNCS,
    STARTUP_SOURCES,
    classify_company,
)
from app.classification.internship_classifier import InternshipClassifier
from app.connectors.base_connector import INDIA_LOCATION_TOKENS
from app.models.internship import InternshipCreate, InternshipInDB
from app.utils.deduplication import fingerprint_for_internship

logger = logging.getLogger(__name__)


def _is_india_location(location: str) -> bool:
    """Return True when the location resolves to India.

    Mirrors BaseConnector.is_india_location so the service has no dependency
    on a concrete connector instance.
    """
    if not location:
        return False
    loc = location.casefold().strip()
    for token in INDIA_LOCATION_TOKENS:
        pattern = r"(^|[\s,/\-])" + re.escape(token) + r"($|[\s,/\-])"
        if re.search(pattern, loc):
            return True
    return False


def resolve_company_logo(company_name: str) -> str:
    if not company_name:
        return "https://logo.clearbit.com/company.com"
    clean = company_name.lower().strip()
    clean = re.sub(r"\s+india$", "", clean)  # strip trailing India
    clean = re.sub(r"[^\w\s]", "", clean)
    words = clean.split()
    key = words[0] if words else "company"
    return f"https://logo.clearbit.com/{key}.com"

def calculate_quality_score(item: dict) -> int:
    score = 0
    company = item.get("company", "").lower()
    # 1. Company reputation
    if any(mnc in company for mnc in FEATURED_MNCS):
        score += 30
    
    # 2. Source trust
    source = item.get("source", "").lower()
    high_trust_sources = {"greenhouse", "lever", "ashby", "yc", "wellfound", "simplify", "ripplematch", "handshake"}
    if source in high_trust_sources:
        score += 20
    elif source == "internshala":
        score += 10
    
    # 3. Freshness
    posted_at = item.get("posted_at")
    scraped_at = item.get("scraped_at")
    date_to_use = posted_at or scraped_at
    if isinstance(date_to_use, str):
        try:
            date_to_use = datetime.fromisoformat(date_to_use)
        except Exception:
            date_to_use = None
            
    if date_to_use:
        # Calculate age in hours
        try:
            if date_to_use.tzinfo is None:
                date_to_use = date_to_use.replace(tzinfo=UTC)
            now = datetime.now(date_to_use.tzinfo)
            age_hours = (now - date_to_use).total_seconds() / 3600.0
            if age_hours <= 24:
                score += 20
            elif age_hours <= 72:
                score += 15
            elif age_hours <= 168:
                score += 10
            else:
                score += 5
        except Exception:
            score += 5
    else:
        score += 5
        
    # 4. Description completeness
    desc = item.get("description", "")
    if len(desc) > 500:
        score += 10
    elif len(desc) > 100:
        score += 5
        
    # 5. Presence of skills
    skills = item.get("skills", [])
    if skills:
        score += 10
        
    # 6. Remote option
    if item.get("remote"):
        score += 10
        
    return score


# Best-effort mapping of startup sources to a plausible funding stage label.
# These are heuristics for display only; the source field is the ground truth.
_STARTUP_FUNDING_HEURISTIC = {
    "yc": "YC Backed",
    "wellfound": "Venture Funded",
    "simplify": "Startup",
    "ripplematch": "Startup",
}


def enrich_internship_metadata(document: dict) -> None:
    """Compute and attach ``company_type``, ``funding_stage`` and
    ``quality_score`` to a raw internship document *in place*.

    Used at ingest time (:meth:`InternshipService.insert_if_new`) so these
    fields are persisted, and can be reused by analytics/ranking without
    re-computing on every read. Existing documents lacking these fields are
    backfilled lazily on read, so old data keeps working.
    """
    if document.get("company_type") is None:
        document["company_type"] = classify_company(
            document.get("company", ""),
            document.get("source"),
            document.get("company_size"),
        )

    if document.get("funding_stage") is None:
        source = (document.get("source") or "").lower().strip()
        if source in STARTUP_SOURCES:
            document["funding_stage"] = _STARTUP_FUNDING_HEURISTIC.get(source)

    if document.get("quality_score") is None:
        document["quality_score"] = calculate_quality_score(document)


def diversify_feed(
    candidates: list[InternshipInDB],
    page_size: int = 20,
    *,
    window: int = 20,
    max_per_company: int = 2,
    internshala_fraction: float = 0.3,
) -> list[InternshipInDB]:
    """Reorder ``candidates`` so the feed is balanced across sources/companies.

    The first ``window`` cards are the "premium" window that users see first
    and are subject to diversity constraints:

    * No single company occupies more than ``max_per_company`` slots
      (defaults to 2) within the window — prevents "Google, Google, Google".
    * The Internshala source is capped to ``internshala_fraction`` of the
      window (defaults to 30%) — it can no longer dominate the first page.

    Constraints are only relaxed once no other source can supply a card, so
    the window is never starved. Cards beyond the window fall back to a
    quality-weighted order while still rotating sources.
    """
    # Group candidates by source, keeping their original (quality-sorted) order.
    source_pools: dict[str, list[InternshipInDB]] = {}
    for item in candidates:
        if not item.company_logo:
            item.company_logo = resolve_company_logo(item.company)
        source = item.source.lower()
        source_pools.setdefault(source, []).append(item)

    source_weights = {
        "wellfound": 2.0, "yc": 2.0, "ripplematch": 2.0, "huzzle": 1.8,
        "greenhouse": 1.5, "lever": 1.5, "ashby": 1.5, "workday": 1.5,
        "smartrecruiters": 1.5, "simplify": 1.5, "handshake": 1.5,
        "icims": 1.5, "taleo": 1.5, "successfactors": 1.5, "jobvite": 1.5, "bamboohr": 1.5,
        "startup_india": 1.8, "inc42": 1.8, "headstart": 1.8, "foundit": 1.5,
        "iit_portal": 2.0, "nit_portal": 1.8,
        "unstop": 1.5, "devfolio": 1.5, "mlh": 2.0, "hackerearth": 1.5, "codechef": 1.5, "geeksforgeeks": 1.2,
        "internshala": 0.5, "manual": 0.5,
    }
    # Highest-weight / highest-volume sources are served first in each round.
    active_sources = sorted(
        source_pools.keys(),
        key=lambda s: (source_weights.get(s, 1.0), len(source_pools[s])),
        reverse=True,
    )

    selected: list[InternshipInDB] = []
    company_counts: dict[str, int] = {}
    internshala_in_window = 0
    target = min(len(candidates), page_size)

    def _company_key(item: InternshipInDB) -> str:
        return item.company.lower().strip()

    def _take(source: str, idx: int) -> None:
        item = source_pools[source].pop(idx)
        selected.append(item)
        comp = _company_key(item)
        company_counts[comp] = company_counts.get(comp, 0) + 1
        if source == "internshala" and len(selected) <= window:
            nonlocal internshala_in_window
            internshala_in_window += 1

    # --- Phase 1: build the diversity-constrained window ---------------------
    while len(selected) < target:
        progress = False
        for source in active_sources:
            pool = source_pools[source]
            if not pool:
                continue

            in_window = len(selected) < window
            if in_window:
                # Internshala cap inside the window.
                internshala_cap = max(int(window * internshala_fraction), 1)
                if source == "internshala" and internshala_in_window >= internshala_cap:
                    continue

            # First item that does not breach the per-company cap (window only).
            found_idx = -1
            for idx, item in enumerate(pool):
                comp = _company_key(item)
                if in_window and company_counts.get(comp, 0) >= max_per_company:
                    continue
                found_idx = idx
                break

            if found_idx != -1:
                _take(source, found_idx)
                progress = True
                if len(selected) >= target:
                    break

        if not progress:
            # Window constraints can't be satisfied by any source — relax them
            # one at a time (company cap first, then Internshala cap) so we
            # never deadlock or empty the feed.
            relaxed = False
            for source in active_sources:
                pool = source_pools[source]
                if not pool:
                    continue
                in_window = len(selected) < window
                if in_window:
                    internshala_cap = max(int(window * internshala_fraction), 1)
                    if source == "internshala" and internshala_in_window >= internshala_cap:
                        # Allow one more Internshala card to make progress.
                        _take(source, 0)
                        relaxed = True
                        break
                # Drop the company-cap for this pick.
                _take(source, 0)
                relaxed = True
                break
            if not relaxed:
                break

    # --- Phase 2: append any remaining candidates (quality order preserved) -
    remaining: list[InternshipInDB] = []
    for source in active_sources:
        for item in source_pools[source]:
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)
            remaining.append(item)
    selected.extend(remaining)

    return selected


class InternshipService:
    """Service for internship persistence and lookup."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection
        self.classifier = InternshipClassifier()

    async def insert_if_new(self, internship: InternshipCreate) -> InternshipInDB | None:
        """Insert an internship only when it is from India and not a duplicate."""

        # Safety net: India-only
        if not _is_india_location(internship.location):
            logger.debug(
                "Skipping non-India internship: company=%s title=%s location=%s",
                internship.company,
                internship.title,
                internship.location,
            )
            return None

        # 1. Normalize company name
        from app.utils.normalization import normalize_company_name
        internship.company = normalize_company_name(internship.company)

        # 2. Validate URL (skip for mocks, tests, and certain bypass sources)
        from app.utils.validation import validate_job_url, clean_url
        bypass_validation_sources = {"workday", "yc", "simplify", "unstop", "jsearch"}
        is_bypass = internship.source.lower() in bypass_validation_sources
        is_mock = "mock" in internship.external_id or "test" in internship.external_id or "example.com" in internship.url or not internship.url.startswith("http")
        
        if not is_mock and not is_bypass:
            is_valid, orig_url, canonical_url, final_url = await validate_job_url(internship.url)
            if not is_valid:
                logger.info("Discarding internship due to invalid URL: %s", internship.url)
                return None
            internship.url = canonical_url
            internship.original_url = orig_url
            internship.canonical_url = canonical_url
            internship.final_url = final_url
        else:
            cleaned = clean_url(internship.url)
            internship.url = cleaned
            internship.original_url = internship.url
            internship.canonical_url = cleaned
            internship.final_url = cleaned

        # Deduplication
        fingerprint = fingerprint_for_internship(internship)
        document = internship.model_dump()
        document["fingerprint"] = fingerprint
        document["scraped_at"] = datetime.now(UTC)
        document["category"] = internship.category or self.classifier.classify(internship)

        # v3: persist classification + quality metadata so ranking/analytics
        # can read them directly instead of recomputing per request.
        enrich_internship_metadata(document)

        if hasattr(self.collection, "update_one"):
            try:
                result = await self.collection.update_one(
                    {"fingerprint": fingerprint},
                    {"$setOnInsert": document},
                    upsert=True,
                )
            except DuplicateKeyError:
                return None

            if result.upserted_id is None:
                return None

            document["_id"] = result.upserted_id
            return InternshipInDB.model_validate(document)

        # Test fakes may not implement Mongo's atomic upsert API.
        existing = await self.collection.find_one({"fingerprint": fingerprint}, {"_id": 1})
        if existing is not None:
            return None

        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return InternshipInDB.model_validate(document)

    async def list_internships(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict | None = None,
    ) -> tuple[list[InternshipInDB], int]:
        # Always fetch a candidate pool of up to 600 items to sort in memory.
        # This allows us to prioritize non-Internshala sources first across all views.
        cursor = (
            self.collection.find(filters or {})
            .sort("posted_at", DESCENDING)
            .limit(600)
        )
        raw_candidates = [InternshipInDB.model_validate(item) async for item in cursor]

        # Backfill metadata for old docs that lack the new fields.
        for item in raw_candidates:
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)
            dump = item.model_dump()
            if dump.get("quality_score") is None:
                enrich_internship_metadata(dump)
                item.quality_score = dump.get("quality_score")
                item.company_type = dump.get("company_type")
                item.funding_stage = dump.get("funding_stage")

        def get_newest_sort_key(item: InternshipInDB):
            is_internshala = 0 if item.source.lower() == "internshala" else 1
            posted_time = item.posted_at or item.scraped_at or datetime.min
            if posted_time.tzinfo is not None:
                posted_time = posted_time.replace(tzinfo=None)
            return (is_internshala, posted_time)

        raw_candidates.sort(key=get_newest_sort_key, reverse=True)

        skip = max(page - 1, 0) * page_size
        total_count = await self.collection.count_documents(filters or {})
        return raw_candidates[skip:skip + page_size], total_count

    async def latest(self, limit: int = 50) -> list[InternshipInDB]:
        cursor = self.collection.find().sort("posted_at", DESCENDING).limit(300)
        results = [InternshipInDB.model_validate(item) async for item in cursor]
        for item in results:
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)

        def get_newest_sort_key(item: InternshipInDB):
            is_internshala = 0 if item.source.lower() == "internshala" else 1
            posted_time = item.posted_at or item.scraped_at or datetime.min
            if posted_time.tzinfo is not None:
                posted_time = posted_time.replace(tzinfo=None)
            return (is_internshala, posted_time)

        results.sort(key=get_newest_sort_key, reverse=True)
        return results[:limit]

    async def by_company(self, company: str) -> list[InternshipInDB]:
        cursor = (
            self.collection.find({"company": {"$regex": f"^{company}$", "$options": "i"}})
            .sort("posted_at", DESCENDING)
        )
        results = [InternshipInDB.model_validate(item) async for item in cursor]
        for item in results:
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)
        return results

    async def by_category(self, category: str) -> list[InternshipInDB]:
        cursor = self.collection.find({"category": category}).sort("posted_at", DESCENDING).limit(300)
        results = [InternshipInDB.model_validate(item) async for item in cursor]
        for item in results:
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)

        def get_newest_sort_key(item: InternshipInDB):
            is_internshala = 0 if item.source.lower() == "internshala" else 1
            posted_time = item.posted_at or item.scraped_at or datetime.min
            if posted_time.tzinfo is not None:
                posted_time = posted_time.replace(tzinfo=None)
            return (is_internshala, posted_time)

        results.sort(key=get_newest_sort_key, reverse=True)
        return results

    async def remote(self) -> list[InternshipInDB]:
        cursor = self.collection.find({"remote": True}).sort("posted_at", DESCENDING).limit(300)
        results = [InternshipInDB.model_validate(item) async for item in cursor]
        for item in results:
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)

        def get_newest_sort_key(item: InternshipInDB):
            is_internshala = 0 if item.source.lower() == "internshala" else 1
            posted_time = item.posted_at or item.scraped_at or datetime.min
            if posted_time.tzinfo is not None:
                posted_time = posted_time.replace(tzinfo=None)
            return (is_internshala, posted_time)

        results.sort(key=get_newest_sort_key, reverse=True)
        return results

    async def by_location(self, location: str) -> list[InternshipInDB]:
        cursor = (
            self.collection.find({"location": {"$regex": location, "$options": "i"}})
            .sort("posted_at", DESCENDING)
            .limit(300)
        )
        results = [InternshipInDB.model_validate(item) async for item in cursor]
        for item in results:
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)

        def get_newest_sort_key(item: InternshipInDB):
            is_internshala = 0 if item.source.lower() == "internshala" else 1
            posted_time = item.posted_at or item.scraped_at or datetime.min
            if posted_time.tzinfo is not None:
                posted_time = posted_time.replace(tzinfo=None)
            return (is_internshala, posted_time)

        results.sort(key=get_newest_sort_key, reverse=True)
        return results

    async def by_source(self, source: str) -> list[InternshipInDB]:
        cursor = self.collection.find({"source": source}).sort("posted_at", DESCENDING)
        results = [InternshipInDB.model_validate(item) async for item in cursor]
        for item in results:
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)
        return results

    async def get_featured_mnc_internships(self, limit: int = 20) -> list[InternshipInDB]:
        mnc_regex = "|".join(f"^{re.escape(mnc)}$" for mnc in FEATURED_MNCS)
        cursor = (
            self.collection.find({"company": {"$regex": mnc_regex, "$options": "i"}})
            .sort("posted_at", DESCENDING)
            .limit(100)
        )
        raw_candidates = [InternshipInDB.model_validate(item) async for item in cursor]
        for item in raw_candidates:
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)
        
        raw_candidates.sort(key=lambda x: calculate_quality_score(x.model_dump()), reverse=True)
        return raw_candidates[:limit]

    async def get_startup_internships(self, limit: int = 20) -> list[InternshipInDB]:
        # Use $or so documents with the new company_type field are found,
        # while older docs that only have a startup source still match.
        startup_sources_list = list(STARTUP_SOURCES)
        cursor = (
            self.collection.find({
                "$or": [
                    {"source": {"$in": startup_sources_list}},
                    {"company_type": "startup"},
                ]
            })
            .sort("posted_at", DESCENDING)
            .limit(100)
        )
        raw_candidates = [InternshipInDB.model_validate(item) async for item in cursor]
        for item in raw_candidates:
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)

        raw_candidates.sort(key=lambda x: calculate_quality_score(x.model_dump()), reverse=True)
        return raw_candidates[:limit]

    async def get_recommendations(self, internship_id: str) -> list[InternshipInDB]:
        from bson import ObjectId
        if not ObjectId.is_valid(internship_id):
            return []
        
        baseline = await self.collection.find_one({"_id": ObjectId(internship_id)})
        if not baseline:
            return []
            
        category = baseline.get("category")
        skills = baseline.get("skills") or []
        company = baseline.get("company")
        location = baseline.get("location")
        source = baseline.get("source")
        
        related_map = {
            "Software Engineering": ["Cloud & DevOps", "Mobile Development", "Embedded & Hardware", "UI/UX"],
            "Data Science": ["Machine Learning", "AI", "Data Analytics", "Research"],
            "Machine Learning": ["Data Science", "AI", "Research"],
            "AI": ["Machine Learning", "Data Science", "Research"],
            "Data Analytics": ["Data Science", "Business Analytics"],
            "Cloud & DevOps": ["Software Engineering", "Cybersecurity"],
            "Product": ["UI/UX", "Business Analytics", "Marketing"],
            "UI/UX": ["Product", "Software Engineering"],
            "Marketing": ["Product", "Content & Writing", "Operations"],
        }
        related_categories = related_map.get(category, [])
        
        cursor = self.collection.find({"_id": {"$ne": ObjectId(internship_id)}}).sort("posted_at", DESCENDING).limit(100)
        raw_candidates = [item for item in await cursor.to_list(length=100)]
        
        scored_candidates = []
        for cand in raw_candidates:
            score = 0
            cand_cat = cand.get("category")
            cand_skills = cand.get("skills") or []
            cand_company = cand.get("company")
            cand_location = cand.get("location")
            cand_source = cand.get("source")
            
            if cand_cat == category:
                score += 50
            elif cand_cat in related_categories:
                score += 30
                
            overlap = set(skills).intersection(set(cand_skills))
            score += len(overlap) * 10
            
            if cand_company and company and cand_company.lower().strip() == company.lower().strip():
                score += 20
                
            if cand_location and location and cand_location.lower().strip() == location.lower().strip():
                score += 15
                
            if cand_source and source and cand_source.lower().strip() == source.lower().strip():
                score += 5
                
            scored_candidates.append((score, cand))
            
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        top_candidates = []
        for _, doc in scored_candidates[:6]:
            item = InternshipInDB.model_validate(doc)
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)
            top_candidates.append(item)
            
        return top_candidates
