"""Company domain models."""

from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class CompanyInDB(BaseModel):
    """Company document stored in MongoDB."""

    id: str | None = Field(default=None, alias="_id")
    name: str
    ats_provider: str
    careers_url: str
    active: bool = True
    last_checked: datetime | None = None

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    @field_validator("id", mode="before")
    @classmethod
    def serialize_object_id(cls, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, ObjectId):
            return str(value)
        return str(value)

    @field_serializer("last_checked")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None
