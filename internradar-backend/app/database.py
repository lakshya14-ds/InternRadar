"""MongoDB connection management."""

from collections.abc import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import DESCENDING

from app.config import Settings, get_settings


class MongoDatabase:
    """Small wrapper around Motor client lifecycle."""

    def __init__(self) -> None:
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        self.client = AsyncIOMotorClient(settings.mongo_uri)
        self.db = self.client[settings.db_name]
        await create_indexes(self.db)

    async def close(self) -> None:
        if self.client is not None:
            self.client.close()
        self.client = None
        self.db = None

    def get_collection(self, name: str) -> AsyncIOMotorCollection:
        if self.db is None:
            raise RuntimeError("Database is not connected")
        return self.db[name]


mongo = MongoDatabase()


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    internships = db["internships"]
    await internships.create_index("fingerprint", unique=True)
    await internships.create_index("external_id")
    await internships.create_index("company")
    await internships.create_index("source")
    await internships.create_index("category")
    await internships.create_index("remote")
    await internships.create_index("location")
    await internships.create_index([("posted_at", DESCENDING)])
    await db["companies"].create_index([("ats_provider", 1), ("name", 1)], unique=True)
    await db["notifications"].create_index([("created_at", DESCENDING)])
    await db["bookmarks"].create_index([("user_id", 1), ("internship_id", 1)], unique=True)
    await db["applications"].create_index([("user_id", 1), ("internship_id", 1)], unique=True)


async def get_internship_collection() -> AsyncIterator[AsyncIOMotorCollection]:
    yield mongo.get_collection("internships")
