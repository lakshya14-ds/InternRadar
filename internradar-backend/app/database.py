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
    import logging
    logger = logging.getLogger(__name__)

    internships = db["internships"]
    await internships.create_index("fingerprint", unique=True)
    await internships.create_index("external_id")
    await internships.create_index("company")
    await internships.create_index("source")
    await internships.create_index("category")
    await internships.create_index("remote")
    await internships.create_index("location")
    await internships.create_index("title")
    await internships.create_index("skills")
    await internships.create_index([("posted_at", DESCENDING)])

    # Compound text index for fuzzy searches
    try:
        await internships.create_index([
            ("title", "text"),
            ("company", "text"),
            ("skills", "text"),
            ("description", "text")
        ], name="internship_text_search")
    except Exception as exc:
        logger.warning("Could not create compound text index, dropping old text index if conflicts: %s", exc)
        try:
            info = await internships.index_information()
            for idx_name, idx_spec in info.items():
                keys = idx_spec.get("key", [])
                # keys is a list of [field, type] or a list of tuples in older motor versions
                is_text = False
                for k in keys:
                    if isinstance(k, list) and len(k) > 1 and k[1] == "text":
                        is_text = True
                    elif isinstance(k, tuple) and len(k) > 1 and k[1] == "text":
                        is_text = True
                if is_text:
                    await internships.drop_index(idx_name)
                    break
            await internships.create_index([
                ("title", "text"),
                ("company", "text"),
                ("skills", "text"),
                ("description", "text")
            ], name="internship_text_search")
        except Exception as err:
            logger.error("Failed to recreate text search index: %s", err)

    await db["companies"].create_index([("ats_provider", 1), ("name", 1)], unique=True)
    await db["notifications"].create_index([("created_at", DESCENDING)])
    await db["bookmarks"].create_index([("user_id", 1), ("internship_id", 1)], unique=True)
    await db["applications"].create_index([("user_id", 1), ("internship_id", 1)], unique=True)



async def get_internship_collection() -> AsyncIterator[AsyncIOMotorCollection]:
    yield mongo.get_collection("internships")
