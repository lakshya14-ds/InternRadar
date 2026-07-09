"""FastAPI application entry point."""

import sys
import asyncio

if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from collections.abc import AsyncIterator
import logging
from contextlib import asynccontextmanager
from app.routers import auth, users
from fastapi import FastAPI
from app.routers import stats
from app.config import get_settings
from app.database import mongo
from app.routers.companies import router as companies_router
from app.routers.health import router as health_router
from app.routers.internships import router as internships_router
from app.routers.scraper import router as scraper_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    import os
    settings = get_settings()
    logger.info("Environment loaded")

    await mongo.connect(settings)
    logger.info("Mongo connected")

    from app.scheduler.scheduler import InternshipScheduler
    scheduler = InternshipScheduler(settings, mongo.get_collection("internships"))
    scheduler.start()
    logger.info("Scheduler started")

    app.state.scheduler = scheduler

    port = os.environ.get("PORT", "8000")
    logger.info("Server started")
    logger.info("Listening on PORT: %s", port)

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
app.include_router(stats.router)
app.include_router(auth.router)
app.include_router(users.router)
