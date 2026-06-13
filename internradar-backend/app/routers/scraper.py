"""Scraper control and status endpoints."""

from fastapi import APIRouter, Request
from app.scheduler.scheduler import ScraperStatus

router = APIRouter(prefix="/api/scraper", tags=["scraper"])


@router.get("/status", response_model=ScraperStatus)
async def get_scraper_status(request: Request) -> ScraperStatus:
    """Get current scraper status and progress."""
    scheduler = request.app.state.scheduler
    return scheduler.get_status()


@router.post("/trigger")
async def trigger_scraper(request: Request) -> dict:
    """Manually trigger a scraper run."""
    scheduler = request.app.state.scheduler
    # Create task for async execution without blocking response
    import asyncio
    asyncio.create_task(scheduler.run_once())
    return {"status": "triggered"}
