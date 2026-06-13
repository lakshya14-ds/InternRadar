"""APScheduler orchestration for recurring ATS aggregation."""

import asyncio
import logging
from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from app.config import Settings
from app.connectors.ashby_connector import AshbyConnector
from app.connectors.base_connector import BaseConnector
from app.connectors.greenhouse_connector import GreenhouseConnector
from app.connectors.lever_connector import LeverConnector
from app.connectors.manual_source_connector import ManualSourceConnector
from app.connectors.smartrecruiters_connector import SmartRecruitersConnector
from app.connectors.workday_connector import WorkdayConnector
from app.notifications.notification_engine import NotificationEngine
from app.services.internship_service import InternshipService

logger = logging.getLogger(__name__)


class ConnectorResult(BaseModel):
    connector: str
    fetched: int
    inserted: int
    status: str
    error: str | None = None


class ScraperStatus(BaseModel):
    is_running: bool
    last_run_at: str | None
    last_fetched: int
    last_inserted: int
    current_connector: str | None
    progress: list[ConnectorResult]
    error: str | None


class InternshipScheduler:
    """Coordinate connectors, persistence, classification, and notifications."""

    def __init__(self, settings: Settings, collection: AsyncIOMotorCollection) -> None:
        self.settings = settings
        self.collection = collection
        self.scheduler = AsyncIOScheduler()
        self.connectors: list[BaseConnector] = [
            GreenhouseConnector(),
            LeverConnector(),
            AshbyConnector(),
            WorkdayConnector(),
            SmartRecruitersConnector(),
            ManualSourceConnector(),
        ]
        # State tracking
        self.is_running = False
        self.current_connector: str | None = None
        self.progress: list[ConnectorResult] = []
        self.last_run_at: datetime | None = None
        self.last_fetched = 0
        self.last_inserted = 0
        self.error: str | None = None

    def start(self) -> None:
        self.scheduler.add_job(
            self.run_once,
            "interval",
            minutes=self.settings.scraper_interval_minutes,
            id="internship_connector_aggregation",
            replace_existing=True,
        )
        self.scheduler.start()
        asyncio.create_task(self.run_once())
        logger.info("Internship scheduler started")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Internship scheduler stopped")

    def get_status(self) -> ScraperStatus:
        """Return current scraper status."""
        return ScraperStatus(
            is_running=self.is_running,
            last_run_at=self.last_run_at.isoformat() if self.last_run_at else None,
            last_fetched=self.last_fetched,
            last_inserted=self.last_inserted,
            current_connector=self.current_connector,
            progress=self.progress,
            error=self.error,
        )

    async def run_once(self) -> None:
        """Run every connector, store new India internships, and send alerts."""

        if self.is_running:
            return
        
        self.is_running = True
        self.error = None
        self.progress = []
        self.last_fetched = 0
        self.last_inserted = 0

        try:
            service = InternshipService(self.collection)
            notifier = NotificationEngine(self.settings)
            inserted_count = 0
            fetched_count = 0

            for connector in self.connectors:
                self.current_connector = connector.__class__.__name__.replace("Connector", "")
                try:
                    internships = await connector.run()
                    fetched_count += len(internships)
                    connector_inserted = 0
                    for internship in internships:
                        inserted = await service.insert_if_new(internship)
                        if inserted is None:
                            continue
                        inserted_count += 1
                        connector_inserted += 1
                        await notifier.send_new_internship_alert(inserted)
                    
                    self.progress.append(ConnectorResult(
                        connector=self.current_connector,
                        fetched=len(internships),
                        inserted=connector_inserted,
                        status="done",
                    ))
                except Exception as e:
                    logger.error("Error in connector %s: %s", self.current_connector, str(e))
                    self.progress.append(ConnectorResult(
                        connector=self.current_connector,
                        fetched=0,
                        inserted=0,
                        status="error",
                        error=str(e),
                    ))

            self.last_run_at = datetime.now()
            self.last_fetched = fetched_count
            self.last_inserted = inserted_count
            self.current_connector = None

            logger.info(
                "Aggregation run complete: fetched=%s inserted=%s",
                fetched_count,
                inserted_count,
            )
        except Exception as e:
            self.error = str(e)
            logger.error("Aggregation run failed: %s", str(e))
        finally:
            self.is_running = False
