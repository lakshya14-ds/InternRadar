"""Internship domain models."""

from datetime import UTC, datetime
from typing import Any

import re
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator


def parse_stipend_to_numeric(stipend_str: str) -> float | None:
    if not stipend_str:
        return None

    # Normalize string
    clean = stipend_str.lower().replace(",", "").replace(" ", "")

    # Find all numbers (including decimals)
    numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", clean)]
    if not numbers:
        return None

    # Calculate average if a range is present
    base_val = sum(numbers) / len(numbers)

    # Scale based on frequency/units
    if "lpa" in clean or "annum" in clean or "yr" in clean or "year" in clean:
        # e.g. 3 LPA = 300,000 / 12 = 25,000
        if base_val < 50:  # likely in Lakhs, e.g. 3 LPA
            return (base_val * 100000) / 12
        return base_val / 12
    elif "hr" in clean or "hour" in clean:
        # e.g. $30/hr -> monthly estimate (assuming 160 hours/month)
        return base_val * 160
    elif "wk" in clean or "week" in clean:
        return base_val * 4.33

    # Default is monthly
    return base_val


class InternshipBase(BaseModel):
    """Normalized internship data shared by connectors and APIs."""

    external_id: str = ""
    source: str = ""
    company: str = ""
    title: str = ""
    location: str = ""
    remote: bool = False
    employment_type: str = "Internship"
    url: str = ""
    posted_at: datetime | None = None
    description: str = ""
    skills: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    category: str | None = None

    # Upgraded Week 3 Fields
    stipend: str | None = None
    salary: str | None = None
    stipend_numeric: float | None = None
    duration: str | None = None
    company_logo: str | None = None
    industry: str | None = None
    experience_level: str | None = None
    application_deadline: str | None = None
    benefits: list[str] | None = Field(default_factory=list)
    work_type: str | None = None
    company_size: str | None = None
    original_url: str | None = None
    canonical_url: str | None = None
    final_url: str | None = None

    # v3 classification + ranking metadata (computed at ingest, backfilled on read)
    quality_score: int | None = None
    company_type: str | None = None  # "startup" | "mnc" | "enterprise"
    funding_stage: str | None = None  # best-effort, startup-only (e.g. "Series A")

    @field_validator("external_id", "source", "company", "title", "location", "url", mode="before")
    @classmethod
    def strip_required_strings(cls, value: Any) -> str:
        return str(value or "").strip()

    @field_validator("description", mode="before")
    @classmethod
    def strip_description(cls, value: Any) -> str:
        return str(value or "").strip()

    @field_validator("stipend_numeric", mode="before")
    @classmethod
    def auto_parse_stipend_numeric(cls, value: Any, info: Any) -> float | None:
        """Attempt to parse numerical value from stipend string if not explicitly set."""
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        return None

    @model_validator(mode="after")
    def populate_stipend_numeric(self) -> "InternshipBase":
        if self.stipend_numeric is None and self.stipend:
            self.stipend_numeric = parse_stipend_to_numeric(self.stipend)
        return self




class InternshipCreate(InternshipBase):
    """Payload used before persistence."""


class InternshipInDB(InternshipBase):
    """Internship document stored in MongoDB."""

    id: str | None = Field(default=None, alias="_id")
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    fingerprint: str = ""

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    @field_validator("id", mode="before")
    @classmethod
    def serialize_object_id(cls, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, ObjectId):
            return str(value)
        return str(value)

    @field_serializer("posted_at", "scraped_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None
