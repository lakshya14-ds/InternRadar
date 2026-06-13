"""Internship API routes."""

from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import APIRouter, Depends, Query

from app.database import get_internship_collection
from app.models.internship import InternshipInDB
from app.search.search_service import SearchService
from app.services.internship_service import InternshipService

router = APIRouter(prefix="/internships", tags=["internships"])


@router.get("", response_model=list[InternshipInDB])
async def list_internships(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return paginated India internships ordered by posting date."""

    return await InternshipService(collection).list_internships(page, page_size)


@router.get("/latest", response_model=list[InternshipInDB])
async def latest_internships(
    limit: int = Query(50, ge=1, le=100),
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return the latest India internships."""

    return await InternshipService(collection).latest(limit=limit)


@router.get("/search", response_model=list[InternshipInDB])
async def search_internships(
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
    limit: int = Query(50, ge=1, le=100),
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Search India internships by common filters.

    All filters are optional and combinable.  ``posted_after`` accepts an
    ISO-8601 datetime string, e.g. ``2024-06-01T00:00:00``.
    """

    return await SearchService(collection).search(
        title=title,
        company=company,
        location=location,
        category=category,
        source=source,
        remote=remote,
        posted_after=posted_after,
        limit=limit,
    )


@router.get("/category/{category}", response_model=list[InternshipInDB])
async def internships_by_category(
    category: str,
    collection: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    """Return India internships in a category.

    Valid categories: Software Engineering, Machine Learning, Data Science,
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
    """Return internships for a company (case-insensitive)."""

    return await InternshipService(collection).by_company(company)
