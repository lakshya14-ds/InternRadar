"""Business logic for user management."""

from datetime import UTC, datetime
import logging

from motor.motor_asyncio import AsyncIOMotorCollection
from passlib.context import CryptContext

from app.models.user import UserCreate, UserInDB, UserPreferences, UserPublic, UserUpdate

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


class UserService:
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection

    async def get_by_email(self, email: str) -> UserInDB | None:
        doc = await self.collection.find_one({"email": email.lower()})
        return UserInDB.model_validate(doc) if doc else None

    async def get_by_id(self, user_id: str) -> UserInDB | None:
        from bson import ObjectId
        from bson.errors import InvalidId
        try:
            oid = ObjectId(user_id)
        except InvalidId:
            return None
        doc = await self.collection.find_one({"_id": oid})
        return UserInDB.model_validate(doc) if doc else None

    async def create(self, data: UserCreate) -> UserInDB:
        doc = {
            "email": data.email.lower(),
            "name": data.name,
            "hashed_password": hash_password(data.password),
            "preferences": data.preferences.model_dump(),
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return UserInDB.model_validate(doc)

    async def update(self, user_id: str, data: UserUpdate) -> UserInDB | None:
        from bson import ObjectId
        from bson.errors import InvalidId
        try:
            oid = ObjectId(user_id)
        except InvalidId:
            return None
        update: dict = {"updated_at": datetime.now(UTC)}
        if data.name is not None:
            update["name"] = data.name
        if data.preferences is not None:
            update["preferences"] = data.preferences.model_dump()
        await self.collection.update_one({"_id": oid}, {"$set": update})
        return await self.get_by_id(user_id)

    def to_public(self, user: UserInDB) -> UserPublic:
        return UserPublic(
            id=user.id or "",
            email=user.email,
            name=user.name,
            preferences=user.preferences,
            created_at=user.created_at.isoformat() if user.created_at else None,
        )
