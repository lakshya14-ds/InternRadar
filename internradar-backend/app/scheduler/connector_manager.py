"""ConnectorManager for concurrent, resilient connector execution."""

import asyncio
import logging
import time
from typing import Any

from app.connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Track and manage failure state for a connector."""

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 1800) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failure_count = 0
        self.state = "closed"  # closed, open, half_open
        self.last_failure_time: float | None = None

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning("Circuit breaker TRIPPED (state=open) due to %s consecutive failures", self.failure_count)

    def can_execute(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.cooldown_seconds:
                self.state = "half_open"
                logger.info("Circuit breaker cooldown expired, moving to half_open state")
                return True
            return False
        if self.state == "half_open":
            return True
        return False


class ConnectorManager:
    """Manage concurrent execution of connectors with timeout, retries, and circuit breakers."""

    def __init__(
        self,
        connectors: list[BaseConnector],
        max_concurrency: int = 5,
        connector_timeout: float = 15.0,
        max_retries: int = 2,
    ) -> None:
        self.connectors = connectors
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.connector_timeout = connector_timeout
        self.max_retries = max_retries
        self.circuit_breakers: dict[str, CircuitBreaker] = {
            connector.__class__.__name__.replace("Connector", ""): CircuitBreaker()
            for connector in connectors
        }
        # Performance metrics
        self.latencies: dict[str, float] = {}
        self.success_rates: dict[str, list[bool]] = {}

    def get_circuit_breaker_statuses(self) -> dict[str, str]:
        """Return the circuit breaker state for each connector."""
        return {name: cb.state for name, cb in self.circuit_breakers.items()}

    async def run_connector(self, connector: BaseConnector) -> tuple[str, list[Any], float, str | None]:
        """Run a single connector with concurrency limiting, retries, and timeout protection."""
        name = connector.__class__.__name__.replace("Connector", "")
        cb = self.circuit_breakers.setdefault(name, CircuitBreaker())

        if not cb.can_execute():
            logger.warning("Skipping connector %s: Circuit breaker is OPEN", name)
            return name, [], 0.0, "Circuit breaker is OPEN (Skipped)"

        async with self.semaphore:
            started_at = time.perf_counter()
            retries = 0
            last_error = None

            while retries < self.max_retries:
                try:
                    logger.info("Starting connector %s (Attempt %d/%d)", name, retries + 1, self.max_retries)
                    # Run the connector with timeout protection
                    internships = await asyncio.wait_for(connector.run(), timeout=self.connector_timeout)
                    
                    # Record success
                    runtime = time.perf_counter() - started_at
                    cb.record_success()
                    self.latencies[name] = runtime
                    self.success_rates.setdefault(name, []).append(True)
                    logger.info("Connector %s completed successfully in %.2fs", name, runtime)
                    return name, internships, runtime, None

                except (asyncio.TimeoutError, Exception) as exc:
                    retries += 1
                    last_error = str(exc)
                    logger.warning("Connector %s failed attempt %d: %s", name, retries, exc)
                    if retries < self.max_retries:
                        await asyncio.sleep(1.0)  # short backoff

            # All retries failed
            runtime = time.perf_counter() - started_at
            cb.record_failure()
            self.latencies[name] = runtime
            self.success_rates.setdefault(name, []).append(False)
            logger.error("Connector %s failed all %d attempts", name, self.max_retries)
            return name, [], runtime, last_error

    async def run_all(self) -> list[tuple[str, list[Any], float, str | None]]:
        """Run all configured connectors concurrently."""
        tasks = [self.run_connector(c) for c in self.connectors]
        return await asyncio.gather(*tasks)
