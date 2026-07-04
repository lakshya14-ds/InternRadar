"""RecommendationService to suggest internships based on user bookmarks and preferences."""

import logging
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import DESCENDING

from app.models.internship import InternshipInDB

logger = logging.getLogger(__name__)


class RecommendationService:
    """Analyze user preferences and bookmarks to suggest matching internships."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.internships = db["internships"]
        self.users = db["users"]
        self.bookmarks = db["bookmarks"]

    async def get_recommendations(self, user_id: str, limit: int = 12) -> list[InternshipInDB]:
        """Aggregate preferences and generate a personalized feed."""
        try:
            # 1. Fetch user profile
            user = await self.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return await self._get_default_feed(limit)

            preferences = user.get("preferences", {})
            pref_categories = preferences.get("preferred_categories", [])
            pref_locations = preferences.get("preferred_locations", [])
            pref_companies = preferences.get("preferred_companies", [])

            # 2. Fetch user bookmarks
            bookmark_docs = await self.bookmarks.find({"user_id": user_id}).to_list(length=100)
            bookmarked_ids = []
            for b in bookmark_docs:
                try:
                    bookmarked_ids.append(ObjectId(b["internship_id"]))
                except Exception:
                    pass

            # Exclude already bookmarked internships
            exclude_ids = [ObjectId(b["internship_id"]) for b in bookmark_docs if ObjectId.is_valid(b.get("internship_id"))]

            # 3. Analyze bookmarks for category/skills density
            bookmarked_categories = set()
            bookmarked_skills = set()
            if bookmarked_ids:
                bookmarked_internships = await self.internships.find({"_id": {"$in": bookmarked_ids}}).to_list(length=100)
                for item in bookmarked_internships:
                    if item.get("category"):
                        bookmarked_categories.add(item["category"])
                    for skill in item.get("skills", []):
                        bookmarked_skills.add(skill)

            # Combine categories, locations, companies, and skills
            categories = list(set(pref_categories).union(bookmarked_categories))
            locations = pref_locations
            companies = pref_companies
            skills = list(bookmarked_skills)

            # 4. Build query
            or_conditions = []
            
            if categories:
                or_conditions.append({"category": {"$in": categories}})
            if companies:
                or_conditions.append({"company": {"$in": companies}})
            if locations:
                # Compile regex for partial matches, e.g. "Bangalore"
                loc_regexes = [{"location": {"$regex": loc, "$options": "i"}} for loc in locations]
                or_conditions.extend(loc_regexes)
            if skills:
                or_conditions.append({"skills": {"$in": skills}})

            query: dict[str, Any] = {}
            if exclude_ids:
                query["_id"] = {"$nin": exclude_ids}

            if or_conditions:
                query["$or"] = or_conditions
            else:
                # No preferences or bookmarks -> return default latest feed
                return await self._get_default_feed(limit, exclude_ids)

            cursor = self.internships.find(query).sort("posted_at", DESCENDING).limit(limit)
            results = [InternshipInDB.model_validate(item) async for item in cursor]
            
            if not results:
                # Fall back to default feed if recommendation matches are empty
                return await self._get_default_feed(limit, exclude_ids)

            return results

        except Exception as exc:
            logger.error("Failed to calculate recommendations: %s", exc)
            return await self._get_default_feed(limit)

    async def _get_default_feed(self, limit: int, exclude_ids: list[ObjectId] | None = None) -> list[InternshipInDB]:
        """Return the latest opportunities if user has no preferences/bookmarks yet."""
        query = {}
        if exclude_ids:
            query["_id"] = {"$nin": exclude_ids}
        cursor = self.internships.find(query).sort("posted_at", DESCENDING).limit(limit)
        return [InternshipInDB.model_validate(item) async for item in cursor]
