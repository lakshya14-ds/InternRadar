"""APScheduler orchestration for recurring ATS aggregation."""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, cast

from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.config import Settings
from app.connectors.ashby_connector import AshbyConnector
from app.connectors.base_connector import BaseConnector
from app.connectors.greenhouse_connector import GreenhouseConnector
from app.connectors.lever_connector import LeverConnector
from app.connectors.manual_source_connector import ManualSourceConnector
from app.connectors.smartrecruiters_connector import SmartRecruitersConnector
from app.connectors.workday_connector import WorkdayConnector

# Week 3 Connectors
from app.connectors.internshala_connector import InternshalaConnector
from app.connectors.jsearch_connector import JSearchConnector
from app.connectors.yc_connector import YCConnector
from app.connectors.simplify_connector import SimplifyConnector
from app.connectors.wellfound_connector import WellfoundConnector
from app.connectors.ripplematch_connector import RippleMatchConnector
from app.connectors.handshake_connector import HandshakeConnector

from app.connectors.icims_connector import ICIMSConnector
from app.connectors.taleo_connector import TaleoConnector
from app.connectors.successfactors_connector import SuccessFactorsConnector
from app.connectors.jobvite_connector import JobviteConnector
from app.connectors.bamboohr_connector import BambooHRConnector
from app.connectors.huzzle_connector import HuzzleConnector
from app.connectors.startup_india_connector import StartupIndiaConnector
from app.connectors.inc42_connector import Inc42Connector
from app.connectors.headstart_connector import HeadstartConnector
from app.connectors.foundit_connector import FounditConnector
from app.connectors.iit_connector import IITConnector
from app.connectors.nit_connector import NITConnector
from app.connectors.student_platforms_connector import StudentPlatformsConnector

from app.scheduler.connector_manager import ConnectorManager
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
    speed: float | None = None  # jobs / sec
    circuit_breaker_state: str | None = None


class ScraperStatus(BaseModel):
    is_running: bool
    last_run_at: str | None
    last_fetched: int
    last_inserted: int
    current_connector: str | None
    progress: list[ConnectorResult]
    error: str | None
    total_speed: float | None = None  # total jobs / sec
    success_rate: float | None = None
    eta_seconds: float | None = None


class InternshipScheduler:
    """Coordinate connectors, persistence, classification, and notifications."""

    def __init__(self, settings: Settings, collection: AsyncIOMotorCollection) -> None:
        self.settings = settings
        self.collection = collection
        self.scheduler = AsyncIOScheduler()
        
        # Instantiate all 13 connectors
        self.connectors: list[BaseConnector] = [
            GreenhouseConnector(),
            LeverConnector(),
            AshbyConnector(),
            WorkdayConnector(),
            SmartRecruitersConnector(),
            ManualSourceConnector(),
            InternshalaConnector(),
            JSearchConnector(),
            YCConnector(),
            SimplifyConnector(),
            WellfoundConnector(),
            RippleMatchConnector(),
            HandshakeConnector(),
            ICIMSConnector(),
            TaleoConnector(),
            SuccessFactorsConnector(),
            JobviteConnector(),
            BambooHRConnector(),
            HuzzleConnector(),
            StartupIndiaConnector(),
            Inc42Connector(),
            HeadstartConnector(),
            FounditConnector(),
            IITConnector(),
            NITConnector(),
            StudentPlatformsConnector(),
        ]
        
        # Concurrency and resilience runner
        self.manager = ConnectorManager(
            connectors=self.connectors,
            max_concurrency=5,
            connector_timeout=15.0,
            max_retries=2
        )

        # State tracking
        self.is_running = False
        self.current_connector: str | None = None
        self.progress: list[ConnectorResult] = []
        self.last_run_at: datetime | None = None
        self.last_fetched = 0
        self.last_inserted = 0
        self.error: str | None = None
        self._run_lock = asyncio.Lock()

        # Analytics
        self.total_runtime = 0.0

    def start(self) -> None:
        self.scheduler.add_job(
            self.run_once,
            "interval",
            minutes=self.settings.scraper_interval_minutes,
            id="internship_connector_aggregation",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.run_daily_digests,
            "cron",
            hour=9,  # run daily at 9:00 AM
            minute=0,
            id="saved_searches_daily_digest",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.run_weekly_digests,
            "cron",
            day_of_week="mon",  # run weekly on Mondays at 9:00 AM
            hour=9,
            minute=0,
            id="saved_searches_weekly_digest",
            replace_existing=True,
        )
        self.scheduler.start()
        asyncio.create_task(self.run_once())
        logger.info("Internship scheduler started")

    async def run_daily_digests(self) -> None:
        logger.info("Running daily saved search digests")
        try:
            from app.services.saved_search_service import SavedSearchService
            svc = SavedSearchService(cast(AsyncIOMotorDatabase, self.collection.database), self.settings)
            await svc.process_digests("daily")
            await svc.process_profile_preferences_digests("daily")
        except Exception as exc:
            logger.error("Failed running daily digests: %s", exc)

    async def run_weekly_digests(self) -> None:
        logger.info("Running weekly saved search digests")
        try:
            from app.services.saved_search_service import SavedSearchService
            svc = SavedSearchService(cast(AsyncIOMotorDatabase, self.collection.database), self.settings)
            await svc.process_digests("weekly")
            await svc.process_profile_preferences_digests("weekly")
        except Exception as exc:
            logger.error("Failed running weekly digests: %s", exc)

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Internship scheduler stopped")


    def get_status(self) -> ScraperStatus:
        """Return current scraper status."""
        success_rate = None
        total_speed = None
        eta_seconds = None

        if self.progress:
            successful = sum(1 for p in self.progress if p.status == "done")
            success_rate = round(successful / len(self.progress), 2)

        if self.is_running:
            # Estimate ETA
            total_connectors = len(self.connectors)
            completed_count = len(self.progress)
            remaining_count = total_connectors - completed_count
            if completed_count > 0:
                elapsed = sum(p.runtime_seconds or 0.0 for p in self.progress)
                avg_time = elapsed / completed_count
                eta_seconds = round((remaining_count * avg_time) / 5.0, 1)  # scaled by concurrency factor of 5
            else:
                eta_seconds = 20.0  # default estimate

        # Total speed calculation
        if self.last_fetched > 0 and self.total_runtime > 0:
            total_speed = round(self.last_fetched / self.total_runtime, 1)

        return ScraperStatus(
            is_running=self.is_running,
            last_run_at=self.last_run_at.isoformat() if self.last_run_at else None,
            last_fetched=self.last_fetched,
            last_inserted=self.last_inserted,
            current_connector=self.current_connector,
            progress=self.progress,
            error=self.error,
            total_speed=total_speed,
            success_rate=success_rate,
            eta_seconds=eta_seconds,
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
        """Execute one aggregation pass concurrently using the ConnectorManager."""
        self.error = None
        self.progress = []
        self.last_fetched = 0
        self.last_inserted = 0
        self.current_connector = "Gathering concurrent connectors"
        started_at = time.perf_counter()

        try:
            service = InternshipService(self.collection)
            notifier = NotificationEngine(self.settings)

            # Concurrently execute all connectors
            self.current_connector = "Executing crawlers concurrently (max 10 parallel)"
            self.manager.connectors = self.connectors  # Sync connectors dynamically for overrides/tests
            results = await self.manager.run_all()

            connector_payloads = []
            for name, internships, runtime, err in results:
                status_str = "error" if err else "done"
                speed = round(len(internships) / runtime, 1) if runtime > 0 else 0.0
                cb_state = self.manager.circuit_breakers.get(name, None)
                cb_state_str = cb_state.state if cb_state else "closed"

                res_item = ConnectorResult(
                    connector=name,
                    fetched=len(internships),
                    inserted=0,
                    status=status_str,
                    runtime_seconds=round(runtime, 2),
                    error=err,
                    speed=speed,
                    circuit_breaker_state=cb_state_str,
                )
                self.progress.append(res_item)
                connector_payloads.append((name, internships))

            fetched_count = sum(len(internships) for _, internships in connector_payloads)
            self.last_fetched = fetched_count

            # Concurrently insert internships for each connector
            self.current_connector = "Writing listings to database"
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
                self.current_connector = "Dispatching notification alerts"
                # Sort by quality score (highest first) to announce the best opportunities
                inserted_records.sort(key=lambda x: x.quality_score or 0, reverse=True)
                # Cap to prevent spamming and connection pool exhaustion
                for internship in inserted_records[:5]:
                    await notifier.send_new_internship_alert(internship)
                try:
                    if hasattr(self.collection, "database"):
                        from app.services.saved_search_service import SavedSearchService
                        saved_search_svc = SavedSearchService(cast(AsyncIOMotorDatabase, self.collection.database), self.settings)
                        await saved_search_svc.process_instant_alerts(inserted_records)
                except Exception as alert_err:
                    logger.error("Failed to run saved search alerts: %s", alert_err)

            self.last_run_at = datetime.now()
            self.last_inserted = inserted_count
            self.total_runtime = time.perf_counter() - started_at

            logger.info(
                "Aggregation run complete: fetched=%s inserted=%s in %.2fs",
                fetched_count,
                inserted_count,
                self.total_runtime,
            )
            self._log_performance_report(fetched_count, inserted_count, self.total_runtime)
        except Exception as e:
            self.error = str(e)
            logger.error("Aggregation run failed: %s", str(e))
        finally:
            self.current_connector = None
            self.is_running = False

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
                    "%s insert failed: %s",
                    connector_name,
                    result,
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
            f"{item.connector}: {item.runtime_seconds or 0:.2f}s ({item.fetched} fetched, {item.inserted} inserted)"
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
