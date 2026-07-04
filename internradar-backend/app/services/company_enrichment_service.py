"""CompanyEnrichmentService to collect and cache company branding details."""

import logging
import re
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

POPULAR_COMPANIES_ENRICHMENT = {
    "google": {
        "logo": "https://logo.clearbit.com/google.com",
        "website": "https://google.com",
        "industry": "Internet & Software Services",
        "company_size": "10,000+ employees",
        "description": "Google's mission is to organize the world's information and make it universally accessible and useful.",
    },
    "microsoft": {
        "logo": "https://logo.clearbit.com/microsoft.com",
        "website": "https://microsoft.com",
        "industry": "Computer Software & Cloud",
        "company_size": "10,000+ employees",
        "description": "Microsoft enables digital transformation for the era of an intelligent cloud and an intelligent edge.",
    },
    "uber": {
        "logo": "https://logo.clearbit.com/uber.com",
        "website": "https://uber.com",
        "industry": "Transportation & Tech",
        "company_size": "10,000+ employees",
        "description": "Uber is a technology platform that connects physical and digital worlds to make movement real.",
    },
    "adobe": {
        "logo": "https://logo.clearbit.com/adobe.com",
        "website": "https://adobe.com",
        "industry": "Design & Document Software",
        "company_size": "10,000+ employees",
        "description": "Adobe is the global leader in digital media and digital marketing solutions.",
    },
    "razorpay": {
        "logo": "https://logo.clearbit.com/razorpay.com",
        "website": "https://razorpay.com",
        "industry": "Financial Technology",
        "company_size": "1,000 - 5,000 employees",
        "description": "Razorpay is a leading converged payments solution company in India, helping businesses accept, process and disburse payments.",
    },
    "zepto": {
        "logo": "https://logo.clearbit.com/zepto.com",
        "website": "https://www.zeptonow.com",
        "industry": "E-Commerce & Quick Commerce",
        "company_size": "1,000 - 5,000 employees",
        "description": "Zepto is a fast-growing instant grocery delivery service in India, delivering groceries in 10 minutes.",
    },
    "meesho": {
        "logo": "https://logo.clearbit.com/meesho.com",
        "website": "https://meesho.com",
        "industry": "E-Commerce & Social Commerce",
        "company_size": "1,000 - 5,000 employees",
        "description": "Meesho is India's fastest-growing internet commerce platform, democratizing e-commerce for small businesses.",
    },
    "cred": {
        "logo": "https://logo.clearbit.com/cred.club",
        "website": "https://cred.club",
        "industry": "Financial Services",
        "company_size": "500 - 1,000 employees",
        "description": "CRED is a members-only club that rewards individuals for their high credit score and financial discipline.",
    },
    "paytm": {
        "logo": "https://logo.clearbit.com/paytm.com",
        "website": "https://paytm.com",
        "industry": "Financial Technology & Payments",
        "company_size": "5,000 - 10,000 employees",
        "description": "Paytm is India's leading financial services company, offering payments, banking, lending, and insurance.",
    },
    "swiggy": {
        "logo": "https://logo.clearbit.com/swiggy.com",
        "website": "https://swiggy.com",
        "industry": "Food Delivery & Quick Commerce",
        "company_size": "5,000 - 10,000 employees",
        "description": "Swiggy is India's leading on-demand convenience platform, delivering food, groceries, and packages.",
    },
    "wipro": {
        "logo": "https://logo.clearbit.com/wipro.com",
        "website": "https://wipro.com",
        "industry": "IT Consulting & Services",
        "company_size": "10,000+ employees",
        "description": "Wipro Limited is a leading technology services and consulting company focused on building innovative solutions.",
    },
    "infosys": {
        "logo": "https://logo.clearbit.com/infosys.com",
        "website": "https://infosys.com",
        "industry": "IT Consulting & Services",
        "company_size": "10,000+ employees",
        "description": "Infosys is a global leader in next-generation digital services and consulting, enabling digital journeys.",
    },
}


class CompanyEnrichmentService:
    """Collect, cache, and serve enriched brand profiles for companies."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.companies = db["companies"]

    def _get_key(self, name: str) -> str:
        """Convert company name to key, e.g. 'Google India' -> 'google'."""
        clean = name.lower().strip()
        clean = re.sub(r"\s+india$", "", clean)  # strip trailing India
        clean = re.sub(r"[^\w\s]", "", clean)
        return clean.split()[0] if clean.split() else ""

    async def get_enriched_company(self, company_name: str) -> dict[str, Any]:
        """Fetch cached company details or auto-enrich using Clearbit and presets."""
        company_name_clean = company_name.strip()
        
        # 1. Look up in companies collection
        doc = await self.companies.find_one({"name": {"$regex": f"^{re.escape(company_name_clean)}$", "$options": "i"}})
        if doc and doc.get("description"):
            return {
                "logo": doc.get("logo"),
                "website": doc.get("website"),
                "industry": doc.get("industry"),
                "company_size": doc.get("company_size"),
                "description": doc.get("description"),
            }

        # 2. Not cached -> Enrich
        key = self._get_key(company_name)
        preset = POPULAR_COMPANIES_ENRICHMENT.get(key)

        if preset:
            enriched = {
                "name": company_name_clean,
                "logo": preset["logo"],
                "website": preset["website"],
                "industry": preset["industry"],
                "company_size": preset["company_size"],
                "description": preset["description"],
                "ats_provider": doc.get("ats_provider") if doc else "manual",
                "careers_url": doc.get("careers_url") if doc else preset["website"],
                "active": True,
            }
        else:
            # Auto-generated fallback using Clearbit logo API
            domain = f"{key}.com" if key else "company.com"
            enriched = {
                "name": company_name_clean,
                "logo": f"https://logo.clearbit.com/{domain}",
                "website": f"https://www.{domain}",
                "industry": "Technology / Software",
                "company_size": "100 - 500 employees",
                "description": f"{company_name_clean} is an innovative organization providing specialized products and services to their global customer base.",
                "ats_provider": doc.get("ats_provider") if doc else "manual",
                "careers_url": doc.get("careers_url") if doc else f"https://www.{domain}",
                "active": True,
            }

        # 3. Cache it in database
        try:
            if doc:
                await self.companies.update_one({"_id": doc["_id"]}, {"$set": enriched})
            else:
                await self.companies.insert_one(enriched)
        except Exception as exc:
            logger.warning("Failed to cache enriched company %s: %s", company_name, exc)

        return {
            "logo": enriched["logo"],
            "website": enriched["website"],
            "industry": enriched["industry"],
            "company_size": enriched["company_size"],
            "description": enriched["description"],
        }
