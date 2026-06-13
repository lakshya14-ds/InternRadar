"""FastAPI application entry point."""

from collections.abc import AsyncIterator
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.database import mongo
from app.routers.companies import router as companies_router
from app.routers.health import router as health_router
from app.routers.internships import router as internships_router
from app.routers.scraper import router as scraper_router
from app.scheduler.scheduler import InternshipScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    await mongo.connect(settings)
    scheduler = InternshipScheduler(settings, mongo.get_collection("internships"))
    scheduler.start()
    app.state.scheduler = scheduler
    try:
        yield
    finally:
        scheduler.shutdown()
        await mongo.close()


app = FastAPI(title="InternRadar India API", version="0.2.0", lifespan=lifespan)
app.include_router(health_router)
app.include_router(companies_router)
app.include_router(internships_router)
app.include_router(scraper_router)
