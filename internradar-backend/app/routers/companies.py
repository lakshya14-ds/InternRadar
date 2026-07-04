"""Company API routes."""

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import APIRouter, Depends, HTTPException

from app.database import mongo
from app.models.company import CompanyInDB

router = APIRouter(prefix="/companies", tags=["companies"])


async def get_company_collection() -> AsyncIOMotorCollection:
    return mongo.get_collection("companies")


@router.get("", response_model=list[CompanyInDB])
async def list_companies(
    collection: AsyncIOMotorCollection = Depends(get_company_collection),
) -> list[CompanyInDB]:
    cursor = collection.find({"active": True}).sort("name", 1)
    return [CompanyInDB.model_validate(item) async for item in cursor]


@router.get("/{company_id}", response_model=CompanyInDB)
async def get_company(
    company_id: str,
    collection: AsyncIOMotorCollection = Depends(get_company_collection),
) -> CompanyInDB:
    try:
        object_id = ObjectId(company_id)
    except InvalidId as exc:
        raise HTTPException(status_code=400, detail="Invalid company id") from exc
    document = await collection.find_one({"_id": object_id})
    if document is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyInDB.model_validate(document)


from pydantic import BaseModel

class DiscoveryRequest(BaseModel):
    name: str
    careers_url: str | None = None

@router.post("/discover", status_code=201)
async def discover_company(
    data: DiscoveryRequest,
    collection: AsyncIOMotorCollection = Depends(get_company_collection),
) -> dict:
    from app.discovery.ats_discovery_service import ATSDiscoveryService
    service = ATSDiscoveryService(collection)
    result = await service.discover_and_register(data.name, data.careers_url)
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Could not detect a supported public ATS (Greenhouse, Lever, Ashby, SmartRecruiters) for this company."
        )
    return {
        "success": True,
        "company": {
            "id": str(result.get("_id") or result.get("id")),
            "name": result["name"],
            "ats_provider": result["ats_provider"],
            "careers_url": result["careers_url"]
        }
    }


@router.get("/enrich/{company_name}")
async def get_enriched_company_details(
    company_name: str,
) -> dict:
    from app.services.company_enrichment_service import CompanyEnrichmentService
    assert mongo.db is not None
    return await CompanyEnrichmentService(mongo.db).get_enriched_company(company_name)


@router.get("/details/{company_name}")
async def get_company_page_details(
    company_name: str,
) -> dict:
    from datetime import datetime, UTC, timedelta
    from app.classification.company_classifier import classify_company
    from app.services.company_enrichment_service import CompanyEnrichmentService
    from app.services.internship_service import InternshipService
    
    # 1. Enriched Brand Details
    assert mongo.db is not None
    enrich_service = CompanyEnrichmentService(mongo.db)
    brand = await enrich_service.get_enriched_company(company_name)
    
    # 2. Open internships
    internships_col = mongo.get_collection("internships")
    intern_service = InternshipService(internships_col)
    open_listings = await intern_service.by_company(company_name)
    
    # 3. Dynamic aggregates
    total_postings = len(open_listings)
    
    # Locations
    locations_dict = {}
    for item in open_listings:
        loc = item.location or "Remote"
        locations_dict[loc] = locations_dict.get(loc, 0) + 1
    locations = [{"name": k, "count": v} for k, v in locations_dict.items()]
    locations.sort(key=lambda x: x["count"], reverse=True)
    
    # Skills in demand
    skills_dict = {}
    for item in open_listings:
        for sk in item.skills:
            skills_dict[sk] = skills_dict.get(sk, 0) + 1
    skills_in_demand = [{"name": k, "count": v} for k, v in skills_dict.items()]
    skills_in_demand.sort(key=lambda x: x["count"], reverse=True)
    
    # Hiring Activity (Timeline over last 6 months)
    activity_dict = {}
    now = datetime.now(UTC)
    for i in range(6):
        month_date = now - timedelta(days=i*30)
        month_str = month_date.strftime("%b %Y")
        activity_dict[month_str] = 0
        
    for item in open_listings:
        posted = item.posted_at or item.scraped_at
        if posted:
            m_str = posted.strftime("%b %Y")
            if m_str in activity_dict:
                activity_dict[m_str] += 1
                
    hiring_activity = [{"month": k, "postings": v} for k, v in reversed(list(activity_dict.items()))]

    # v3: attach company_type and funding_stage from the first listing.
    sample = open_listings[0].model_dump() if open_listings else {}
    company_type = sample.get("company_type") or classify_company(
        company_name,
        sample.get("source"),
        sample.get("company_size"),
    )
    funding_stage = sample.get("funding_stage")

    return {
        "brand": brand,
        "open_internships": open_listings,
        "hiring_activity": hiring_activity,
        "internship_history": {
            "total_postings": total_postings,
        },
        "skills_in_demand": skills_in_demand[:10],
        "locations": locations[:5],
        "company_type": company_type,
        "funding_stage": funding_stage,
    }


