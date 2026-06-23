"""Scraper control and status endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Request
from app.scheduler.scheduler import ScraperStatus

router = APIRouter(prefix="/api/scraper", tags=["scraper"])
logger = logging.getLogger(__name__)


@router.get("/status", response_model=ScraperStatus)
async def get_scraper_status(request: Request) -> ScraperStatus:
    """Get current scraper status and progress."""
    scheduler = getattr(request.app.state, "scheduler", None)
    if scheduler is None:
        raise HTTPException(status_code=503, detail="Scraper scheduler is not ready")
    return scheduler.get_status()


@router.post("/trigger")
async def trigger_scraper(request: Request) -> dict:
    """Manually trigger a scraper run."""
    scheduler = getattr(request.app.state, "scheduler", None)
    if scheduler is None:
        raise HTTPException(status_code=503, detail="Scraper scheduler is not ready")

    task = scheduler.trigger_once()
    if task is None:
        raise HTTPException(status_code=409, detail="Scraper is already running")

    def log_background_failure(done_task) -> None:
        try:
            done_task.result()
        except Exception:
            logger.exception("Manual scraper task failed")

    task.add_done_callback(log_background_failure)
    return {"success": True, "message": "Scraper started"}
