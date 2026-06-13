"""Internship domain models."""

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class InternshipBase(BaseModel):
    """Normalized internship data shared by connectors and APIs."""

    external_id: str
    source: str
    company: str
    title: str
    location: str
    remote: bool = False
    employment_type: str = "Internship"
    url: str
    posted_at: datetime | None = None
    description: str = ""
    skills: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    category: str | None = None

    @field_validator("external_id", "source", "company", "title", "location", "url", mode="before")
    @classmethod
    def strip_required_strings(cls, value: Any) -> str:
        return str(value or "").strip()

    @field_validator("description", mode="before")
    @classmethod
    def strip_description(cls, value: Any) -> str:
        return str(value or "").strip()


class InternshipCreate(InternshipBase):
    """Payload used before persistence."""


class InternshipInDB(InternshipBase):
    """Internship document stored in MongoDB."""

    id: str | None = Field(default=None, alias="_id")
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    fingerprint: str

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
