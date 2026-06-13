"""User domain models."""

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer, field_validator


class UserPreferences(BaseModel):
    preferred_categories: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    preferred_companies: list[str] = Field(default_factory=list)
    remote_only: bool = False
    email_alerts_enabled: bool = True


class UserBase(BaseModel):
    email: EmailStr
    name: str
    preferences: UserPreferences = Field(default_factory=UserPreferences)


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    preferences: UserPreferences | None = None


class UserInDB(UserBase):
    id: str | None = Field(default=None, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    @field_validator("id", mode="before")
    @classmethod
    def serialize_object_id(cls, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, ObjectId):
            return str(value)
        return str(value)

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None


class UserPublic(BaseModel):
    id: str
    email: str
    name: str
    preferences: UserPreferences
    created_at: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class TokenData(BaseModel):
    user_id: str | None = None
    email: str | None = None
