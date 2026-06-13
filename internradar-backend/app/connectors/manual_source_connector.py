"""Configuration-driven connector for manual internship sources."""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
import requests
import yaml

from app.connectors.base_connector import BaseConnector
from app.models.internship import InternshipCreate


class ManualSourceConnector(BaseConnector):
    """Read manual portals from YAML and extract internship links.

    Every source in sources.yaml is already India-specific, so the
    India-location check here uses the config's ``location`` field as the
    canonical location rather than trying to parse it from link text (which
    is often too short to carry location information).
    """

    source = "manual"

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or Path("app/config/sources.yaml")

    async def discover_companies(self) -> list[dict[str, Any]]:
        """Load configured manual sources."""

        if not self.config_path.exists():
            return []
        payload = yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
        return list(payload.get("sources", []))

    async def fetch_jobs(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fetch visible links from configured manual sources."""

        jobs: list[dict[str, Any]] = []
        for source in companies:
            try:
                response = requests.get(source["url"], timeout=20)
                response.raise_for_status()
            except requests.RequestException:
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            selector = source.get("selector") or "a"
            for link in soup.select(selector)[:50]:
                title = link.get_text(" ", strip=True)
                href = link.get("href", source["url"])
                if isinstance(href, list):
                    href = href[0] if href else source["url"]
                url = (
                    href
                    if str(href).startswith("http")
                    else source["url"].rstrip("/") + "/" + str(href).lstrip("/")
                )
                jobs.append({"source_config": source, "title": title, "url": url})
        return jobs

    async def normalize(self, raw_jobs: list[dict[str, Any]]) -> list[InternshipCreate]:
        """Normalize manual source records — internships only.

        Location is taken directly from the YAML config entry because link
        text rarely contains structured location data.  All sources in
        sources.yaml are India-based, so no additional country filter is
        needed here, but we still validate via ``is_india_location`` in case
        a misconfigured source slips through.
        """

        internships: list[InternshipCreate] = []
        for job in raw_jobs:
            title = job.get("title", "")

            if not title or not self.is_internship(title):
                continue

            config = job["source_config"]
            # Prefer the config-level location; fall back gracefully
            location = config.get("location", "India")

            # Safety net: every manual source must resolve to India
            if not self.is_india_location(location):
                continue

            internships.append(
                self.build_internship(
                    external_id=job.get("url", title),
                    company=config.get("name", "Manual Source"),
                    title=title,
                    location=location,
                    url=job.get("url", ""),
                    description=f"Manual source: {config.get('name', '')}",
                    tags=[config.get("type", "manual")],
                )
            )
        return internships
