"""Mongo-backed internship search service."""

from datetime import datetime
import re

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import DESCENDING

from app.models.internship import InternshipInDB
from app.services.internship_service import (
    calculate_quality_score,
    diversify_feed,
    enrich_internship_metadata,
    resolve_company_logo,
)


def parse_hybrid_query(q: str) -> dict:
    filters = {}
    if not q:
        return filters
        
    q_lower = q.lower().strip()
    
    # 1. Detect location
    cities = ["bangalore", "bengaluru", "mumbai", "pune", "delhi", "new delhi", "noida", "gurgaon", "gurugram", "ncr", "hyderabad", "chennai", "kolkata"]
    for city in cities:
        pattern = r"\b" + re.escape(city) + r"\b"
        if re.search(pattern, q_lower):
            filters["location"] = city
            q_lower = re.sub(pattern, "", q_lower).strip()
            
    # 2. Detect remote
    if "remote" in q_lower:
        filters["remote"] = True
        q_lower = q_lower.replace("remote", "").strip()
        
    # 3. Detect category / role terms
    category_map = {
        "software engineer": "Software Engineering",
        "software engineering": "Software Engineering",
        "swe": "Software Engineering",
        "developer": "Software Engineering",
        "data science": "Data Science",
        "data scientist": "Data Science",
        "machine learning": "Machine Learning",
        "ml": "Machine Learning",
        "ai": "AI",
        "artificial intelligence": "AI",
        "data analytics": "Data Analytics",
        "data analyst": "Data Analytics",
        "product manager": "Product",
        "product management": "Product",
        "pm": "Product",
        "ui/ux": "UI/UX",
        "designer": "UI/UX",
        "cybersecurity": "Cybersecurity",
        "cloud": "Cloud & DevOps",
        "devops": "Cloud & DevOps",
        "marketing": "Marketing",
        "finance": "Finance",
    }
    for term, cat in category_map.items():
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, q_lower):
            filters["category"] = cat
            q_lower = re.sub(pattern, "", q_lower).strip()
            
    # 4. Detect company names
    companies_list = [
        "google", "microsoft", "amazon", "nvidia", "adobe", "atlassian", 
        "salesforce", "databricks", "uber", "stripe", "snowflake", "mongodb", 
        "servicenow", "cisco", "intel", "qualcomm", "oracle", "vmware", 
        "paypal", "sap", "zepto", "meesho", "invideo", "cred", "paytm", "swiggy"
    ]
    for comp in companies_list:
        pattern = r"\b" + re.escape(comp) + r"\b"
        if re.search(pattern, q_lower):
            filters["company"] = comp
            q_lower = re.sub(pattern, "", q_lower).strip()
            
    # 5. Clean up noise words
    noise_words = ["internship", "intern", "role", "jobs", "job", "opportunity", "position", "hiring"]
    for word in noise_words:
        pattern = r"\b" + re.escape(word) + r"\b"
        q_lower = re.sub(pattern, "", q_lower).strip()
        
    # 6. Any remaining words as general keyword search
    remaining = " ".join([w.strip() for w in q_lower.split() if w.strip()])
    if remaining:
        filters["remaining"] = remaining
        
    return filters


class SearchService:
    """Build indexed MongoDB queries for internship search."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection

    async def search(
        self,
        q: str | None = None,
        title: str | None = None,
        company: str | None = None,
        location: str | None = None,
        category: str | None = None,
        source: str | None = None,
        remote: bool | None = None,
        posted_after: datetime | None = None,
        min_stipend: float | None = None,
        max_stipend: float | None = None,
        duration: str | None = None,
        skills: list[str] | None = None,
        sort_by: str = "newest",
        limit: int = 50,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[InternshipInDB], int]:
        """Search internships by indexed filters, fuzzy query, range, and custom sort order."""

        parsed_filters = parse_hybrid_query(q) if q else {}
        
        # Apply parsed filters as fallback or strict filters
        if "location" in parsed_filters and not location:
            location = parsed_filters["location"]
        if "company" in parsed_filters and not company:
            company = parsed_filters["company"]
        if "category" in parsed_filters and not category:
            category = parsed_filters["category"]
        if "remote" in parsed_filters and remote is None:
            remote = parsed_filters["remote"]
            
        remaining_q = parsed_filters.get("remaining")
        
        query: dict[str, object] = {}

        if remaining_q:
            query["$text"] = {"$search": remaining_q}
        elif q and not parsed_filters:
            query["$text"] = {"$search": q}
        elif title:
            query["title"] = {"$regex": title, "$options": "i"}

        if company:
            query["company"] = {"$regex": company, "$options": "i"}
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
        if category:
            query["category"] = category
        if source:
            query["source"] = source
        if remote is not None:
            query["remote"] = remote
        if posted_after:
            query["posted_at"] = {"$gte": posted_after}
        if duration:
            query["duration"] = {"$regex": duration, "$options": "i"}
        if skills:
            query["skills"] = {"$all": skills}

        # Stipend range filter
        if min_stipend is not None or max_stipend is not None:
            stipend_query = {}
            if min_stipend is not None:
                stipend_query["$gte"] = min_stipend
            if max_stipend is not None:
                stipend_query["$lte"] = max_stipend
            query["stipend_numeric"] = stipend_query

        projection = None
        if remaining_q or (q and not parsed_filters):
            projection = {"score": {"$meta": "textScore"}}

        # Determine sorting
        sort_spec = []
        if sort_by == "highest_stipend":
            sort_spec = [("stipend_numeric", -1), ("posted_at", -1)]
        elif sort_by == "most_relevant" and (remaining_q or (q and not parsed_filters)):
            sort_spec = [("score", {"$meta": "textScore"})]
        else:  # default: newest
            sort_spec = [("posted_at", -1)]

        cursor = self.collection.find(query, projection)
        if sort_spec:
            cursor = cursor.sort(sort_spec)
        cursor = cursor.limit(300)
        
        results = [InternshipInDB.model_validate(item) async for item in cursor]

        # Backfill metadata for older docs missing v3 fields.
        for item in results:
            if not item.company_logo:
                item.company_logo = resolve_company_logo(item.company)
            dump = item.model_dump()
            if dump.get("quality_score") is None:
                enrich_internship_metadata(dump)
                item.quality_score = dump.get("quality_score")
                item.company_type = dump.get("company_type")
                item.funding_stage = dump.get("funding_stage")

        if sort_by == "most_relevant" and (remaining_q or (q and not parsed_filters)):
            # Blend MongoDB textScore (60%) with our quality_score (40%).
            # This ensures high-quality MNC / startup roles surface above
            # generic Internshala keyword matches.
            max_text_score = 1.0  # MongoDB textScore is normalised to [0, 1]
            blended: list[tuple[float, InternshipInDB]] = []
            for item in results:
                raw = item.model_dump()
                text_val = raw.get("score", 0.0) or 0.0
                q_score = item.quality_score if item.quality_score is not None else calculate_quality_score(raw)
                # Normalise q_score to [0, 1] range (max possible ~100).
                normalised_quality = min(q_score / 100.0, 1.0)
                combined = 0.6 * text_val + 0.4 * normalised_quality
                blended.append((combined, item))
            blended.sort(key=lambda x: x[0], reverse=True)
            results = [item for _, item in blended]

        elif sort_by == "newest":
            def get_newest_sort_key(item: InternshipInDB):
                is_internshala = 0 if item.source.lower() == "internshala" else 1
                posted_time = item.posted_at or item.scraped_at or datetime.min
                if posted_time.tzinfo is not None:
                    posted_time = posted_time.replace(tzinfo=None)
                return (is_internshala, posted_time)

            results.sort(key=get_newest_sort_key, reverse=True)

        elif sort_by not in ("highest_stipend", "newest"):
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

            def get_candidate_sort_key(item: InternshipInDB):
                q_score = item.quality_score if item.quality_score is not None else calculate_quality_score(item.model_dump())
                weight = source_weights.get(item.source.lower(), 1.0)
                posted_time = item.posted_at or item.scraped_at or datetime.min
                if posted_time.tzinfo is not None:
                    posted_time = posted_time.replace(tzinfo=None)
                return (q_score * weight, posted_time)

            results.sort(key=get_candidate_sort_key, reverse=True)
            results = diversify_feed(results, page_size=len(results))

        skip = max(page - 1, 0) * page_size
        total_count = await self.collection.count_documents(query)
        return results[skip:skip + page_size], total_count

