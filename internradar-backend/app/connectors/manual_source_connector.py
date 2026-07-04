"""Configuration-driven connector for manual internship sources."""

from pathlib import Path
from urllib.parse import urljoin
from typing import Any
import asyncio
import logging
import time

from bs4 import BeautifulSoup
import httpx
import yaml

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate

logger = logging.getLogger(__name__)


class ManualSourceConnector(BaseConnector):
    """Read manual portals from YAML and extract internship links."""

    source = "manual"

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or Path("app/config/sources.yaml")

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Load configured manual sources."""

        if not self.config_path.exists():
            return []

        payload = yaml.safe_load(
            self.config_path.read_text(encoding="utf-8")
        ) or {}

        return list(payload.get("sources", []))

    async def _fetch_source(
        self,
        client: httpx.AsyncClient,
        source: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Fetch a single source."""

        jobs: list[dict[str, Any]] = []
        name = source.get("name", source.get("url", "unknown"))
        started_at = time.perf_counter()

        try:
            response = await asyncio.wait_for(client.get(source["url"]), timeout=15.0)
            response.raise_for_status()

            def parse_html(html_text: str, sel: str, base_url: str) -> list[dict[str, Any]]:
                soup = BeautifulSoup(html_text, "html.parser")
                extracted = []
                for link in soup.select(sel)[:50]:
                    title = link.get_text(" ", strip=True)
                    href = link.get("href", base_url)
                    if isinstance(href, list):
                        href = href[0] if href else base_url
                    href_str = str(href)
                    # Prepend slash to relative paths to avoid urljoin folder directory residue
                    if not href_str.startswith("http") and not href_str.startswith("/"):
                        href_str = "/" + href_str
                    url = urljoin(base_url, href_str)
                    # Specific Internshala URL reconstruction
                    if "internshala.com" in url and "/detail/" in url:
                        slug = url.split("/detail/")[-1]
                        url = f"https://internshala.com/internship/detail/{slug}"
                    extracted.append(
                        {
                            "source_config": source,
                            "title": title,
                            "url": url,
                        }
                    )
                return extracted

            jobs = await asyncio.to_thread(
                parse_html,
                response.text,
                source.get("selector") or "a",
                source["url"]
            )

            runtime = time.perf_counter() - started_at
            logger.info("ManualSource: %s fetched in %.2fs", name, runtime)
        except Exception as exc:
            runtime = time.perf_counter() - started_at
            if isinstance(exc, (httpx.TimeoutException, asyncio.TimeoutError)):
                logger.warning("ManualSource: %s timeout after %.2fs", name, runtime)
                return jobs
            logger.warning(
                "ManualSource: %s failed after %.2fs (%s)",
                name,
                runtime,
                exc,
            )

        return jobs

    async def fetch_jobs(
        self,
        companies: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Fetch all manual sources concurrently."""

        if not companies:
            return []

        timeout = httpx.Timeout(15.0)

        limits = httpx.Limits(
            max_keepalive_connections=50,
            max_connections=150,
        )

        async with httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            follow_redirects=True,
        ) as client:

            results = await asyncio.gather(
                *[
                    self._fetch_source(client, source)
                    for source in companies
                ],
                return_exceptions=True,
            )

        jobs: list[dict[str, Any]] = []

        for result in results:
            if isinstance(result, list):
                jobs.extend(result)

        logger.info(
            "ManualSource fetched %s raw jobs",
            len(jobs),
        )

        return jobs

    def normalize(
        self,
        raw_jobs: list[dict[str, Any]],
    ) -> list[InternshipCreate]:
        """Normalize manual source records."""

        internships: list[InternshipCreate] = []

        for job in raw_jobs:
            title = job.get("title", "")

            if not title or not self.is_internship(title):
                continue

            config = job["source_config"]
            url = job.get("url", "")

            # Skip Internshala links that are not direct detail pages
            if config.get("type") == "internshala" and "/detail/" not in url:
                continue

            location = config.get("location", "India")

            if not self.is_india_location(location):
                continue

            internships.append(
                self.build_internship(
                    external_id=job.get("url", title),
                    company=config.get(
                        "name",
                        "Manual Source",
                    ),
                    title=title,
                    location=location,
                    url=job.get("url", ""),
                    description=(
                        f"Manual source: "
                        f"{config.get('name', '')}"
                    ),
                    tags=[
                        config.get(
                            "type",
                            "manual",
                        )
                    ],
                )
            )

        logger.info(
            "ManualSource normalized %s internships",
            len(internships),
        )

        return internships
