"""Internship API routes."""

from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import APIRouter, Depends, Query, Response
from bson import ObjectId
from fastapi import HTTPException
from app.database import get_internship_collection
from app.models.internship import InternshipInDB
from app.search.search_service import SearchService
from app.services.internship_service import InternshipService

router = APIRouter(prefix="/internships", tags=["internships"])


@router.get("", response_model=list[InternshipInDB])
async def list_internships(
    response: Response,
    page: int = Query(1, ge=1),
    page_size: int = Query(10000, ge=1, le=100000),
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return paginated India internships ordered by posting date."""

    results, total_count = await InternshipService(collection).list_internships(page, page_size)
    response.headers["X-Total-Count"] = str(total_count)
    return results


@router.get("/latest", response_model=list[InternshipInDB])
async def latest_internships(
    limit: int = Query(10000, ge=1, le=100000),
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return the latest India internships."""

    return await InternshipService(collection).latest(limit=limit)


@router.get("/search", response_model=list[InternshipInDB])
async def search_internships(
    response: Response,
    q: str | None = None,
    title: str | None = None,
    company: str | None = None,
    location: str | None = None,
    category: str | None = None,
    source: str | None = None,
    remote: bool | None = None,
    posted_after: datetime | None = Query(
        default=None,
        description="ISO-8601 datetime — return only internships posted after this timestamp",
    ),
    min_stipend: float | None = None,
    max_stipend: float | None = None,
    duration: str | None = None,
    skills: str | None = Query(
        default=None,
        description="Comma-separated list of skills, e.g. Python,React",
    ),
    sort_by: str = Query(
        default="newest",
        description="Sort order: newest, highest_stipend, most_relevant",
    ),
    limit: int = Query(10000, ge=1, le=100000),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Search India internships by common filters.

    All filters are optional and combinable.  ``posted_after`` accepts an
    ISO-8601 datetime string, e.g. ``2024-06-01T00:00:00``.
    """
    skills_list = [s.strip() for s in skills.split(",")] if skills else None

    results, total_count = await SearchService(collection).search(
        q=q,
        title=title,
        company=company,
        location=location,
        category=category,
        source=source,
        remote=remote,
        posted_after=posted_after,
        min_stipend=min_stipend,
        max_stipend=max_stipend,
        duration=duration,
        skills=skills_list,
        sort_by=sort_by,
        limit=limit,
        page=page,
        page_size=page_size,
    )
    response.headers["X-Total-Count"] = str(total_count)
    return results



@router.get("/category/{category}", response_model=list[InternshipInDB])
async def internships_by_category(
    category: str,
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return India internships in a category.

    Valid categories: Software Engineering, Machine Learning, AI, Data Science,
    Data Analytics, Cybersecurity, Embedded & Hardware, Cloud & DevOps,
    Mobile Development, UI/UX, Research, Product, Business Analytics,
    Finance, Marketing, Operations, Human Resources, Legal & Compliance,
    Content & Writing, Other.
    """

    return await InternshipService(collection).by_category(category)


@router.get("/location/{location}", response_model=list[InternshipInDB])
async def internships_by_location(
    location: str,
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return internships matching an Indian city or region, e.g. Bangalore, NCR, Pune."""

    return await InternshipService(collection).by_location(location)


@router.get("/source/{source}", response_model=list[InternshipInDB])
async def internships_by_source(
    source: str,
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return internships from a specific ATS source (greenhouse, lever, ashby, workday, smartrecruiters, manual)."""

    return await InternshipService(collection).by_source(source)


@router.get("/remote", response_model=list[InternshipInDB])
async def remote_internships(
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return remote internships (currently returns empty — remote roles are excluded by policy)."""

    return await InternshipService(collection).remote()

@router.get("/company/{company}", response_model=list[InternshipInDB])
async def internships_by_company(
    company: str,
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    return await InternshipService(collection).by_company(company)


@router.get("/featured-mnc", response_model=list[InternshipInDB])
async def featured_mnc_internships(
    limit: int = Query(20, ge=1, le=100),
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return top featured MNC internships sorted by quality score."""
    return await InternshipService(collection).get_featured_mnc_internships(limit)


@router.get("/startups", response_model=list[InternshipInDB])
async def startup_internships(
    limit: int = Query(20, ge=1, le=100),
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return top startup internships sorted by quality score."""
    return await InternshipService(collection).get_startup_internships(limit)


@router.get("/{internship_id}/recommendations", response_model=list[InternshipInDB])
async def get_recommendations(
    internship_id: str,
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return recommended internships based on category, company, location, and skills similarity."""
    return await InternshipService(collection).get_recommendations(internship_id)


@router.get("/{internship_id}", response_model=InternshipInDB)
async def get_internship(
    internship_id: str,
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> InternshipInDB:

    if not ObjectId.is_valid(internship_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid internship ID"
        )

    internship = await collection.find_one(
        {"_id": ObjectId(internship_id)}
    )

    if not internship:
        raise HTTPException(
            status_code=404,
            detail="Internship not found"
        )

    return InternshipInDB(**internship)


