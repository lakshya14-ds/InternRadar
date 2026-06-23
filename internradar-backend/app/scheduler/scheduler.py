"""APScheduler orchestration for recurring ATS aggregation."""

import asyncio
import logging
import time
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
    runtime_seconds: float | None = None
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
        self._run_lock = asyncio.Lock()

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

    def trigger_once(self) -> asyncio.Task[None] | None:
        """Start a manual run and mark status immediately for UI polling."""
        if self.is_running or self._run_lock.locked():
            return None

        self.is_running = True
        return asyncio.create_task(self._run_once_started())

    async def run_once(self) -> None:
        """Run every connector, store new India internships, and send alerts."""

        if self.is_running or self._run_lock.locked():
            return

        self.is_running = True
        await self._run_once_started()

    async def _run_once_started(self) -> None:
        """Execute a run after ``is_running`` has already been set."""

        async with self._run_lock:
            await self._execute_run()

    async def _execute_run(self) -> None:
        """Execute one aggregation pass."""

        self.error = None
        self.progress = []
        self.last_fetched = 0
        self.last_inserted = 0
        self.current_connector = f"Running {len(self.connectors)} connectors"
        started_at = time.perf_counter()

        try:
            service = InternshipService(self.collection)
            notifier = NotificationEngine(self.settings)
            connector_payloads = await asyncio.gather(
                *(self._run_connector(connector) for connector in self.connectors),
                return_exceptions=False,
            )

            fetched_count = sum(len(internships) for _, internships in connector_payloads)
            self.last_fetched = fetched_count

            insert_tasks = [
                self._insert_connector_internships(service, name, internships)
                for name, internships in connector_payloads
            ]
            inserted_by_connector = await asyncio.gather(*insert_tasks)

            inserted_records = [
                internship
                for connector_records in inserted_by_connector
                for internship in connector_records
            ]
            inserted_count = len(inserted_records)

            if inserted_records:
                await asyncio.gather(
                    *(notifier.send_new_internship_alert(internship) for internship in inserted_records),
                    return_exceptions=True,
                )

            self.last_run_at = datetime.now()
            self.last_inserted = inserted_count
            self.current_connector = None
            total_runtime = time.perf_counter() - started_at

            logger.info(
                "Aggregation run complete: fetched=%s inserted=%s",
                fetched_count,
                inserted_count,
            )
            self._log_performance_report(fetched_count, inserted_count, total_runtime)
        except Exception as e:
            self.error = str(e)
            logger.error("Aggregation run failed: %s", str(e))
        finally:
            self.current_connector = None
            self.is_running = False

    async def _run_connector(self, connector: BaseConnector) -> tuple[str, list[Any]]:
        """Run a connector with timing and isolated failure handling."""

        name = connector.__class__.__name__.replace("Connector", "")
        started_at = time.perf_counter()
        try:
            internships = await connector.run()
            runtime = time.perf_counter() - started_at
            logger.info("%sConnector completed in %.2f seconds", name, runtime)
            self.progress.append(
                ConnectorResult(
                    connector=name,
                    fetched=len(internships),
                    inserted=0,
                    status="done",
                    runtime_seconds=round(runtime, 2),
                )
            )
            return name, internships
        except Exception as exc:
            runtime = time.perf_counter() - started_at
            logger.exception("%sConnector failed after %.2f seconds", name, runtime)
            self.progress.append(
                ConnectorResult(
                    connector=name,
                    fetched=0,
                    inserted=0,
                    status="error",
                    runtime_seconds=round(runtime, 2),
                    error=str(exc),
                )
            )
            return name, []

    async def _insert_connector_internships(
        self,
        service: InternshipService,
        connector_name: str,
        internships: list[Any],
    ) -> list[Any]:
        """Insert one connector's results concurrently and update progress."""

        if not internships:
            return []

        results = await asyncio.gather(
            *(service.insert_if_new(internship) for internship in internships),
            return_exceptions=True,
        )
        inserted = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(
                    "%s insert failed",
                    connector_name,
                    exc_info=(type(result), result, result.__traceback__),
                )
                continue
            if result is not None:
                inserted.append(result)

        for item in self.progress:
            if item.connector == connector_name and item.status == "done":
                item.inserted = len(inserted)
                break

        return inserted

    def _log_performance_report(self, fetched: int, inserted: int, total_runtime: float) -> None:
        """Log the scraper timing report expected during refresh tuning."""

        timings = "\n".join(
            f"{item.connector}: {item.runtime_seconds or 0:.2f}s"
            for item in self.progress
        )
        logger.info(
            "\n=================================================\n"
            "SCRAPER PERFORMANCE REPORT\n"
            "==========================\n\n"
            "%s\n\n"
            "Fetched: %s\n"
            "Inserted: %s\n\n"
            "Total Runtime: %.2fs",
            timings,
            fetched,
            inserted,
            total_runtime,
        )
