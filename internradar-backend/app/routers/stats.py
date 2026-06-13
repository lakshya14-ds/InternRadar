"""Platform statistics route."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorCollection

from app.database import mongo

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
async def get_stats() -> dict:
    try:
        internships: AsyncIOMotorCollection = mongo.get_collection("internships")
        companies: AsyncIOMotorCollection = mongo.get_collection("companies")
        users: AsyncIOMotorCollection = mongo.get_collection("users")

        total = await internships.count_documents({})
        total_companies = await companies.count_documents({})
        total_users = await users.count_documents({})

        today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        new_today = await internships.count_documents({"scraped_at": {"$gte": today}})

        week_ago = datetime.now(UTC) - timedelta(days=7)
        new_this_week = await internships.count_documents({"scraped_at": {"$gte": week_ago}})

        pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}]
        categories = [{"category": d["_id"], "count": d["count"]} async for d in internships.aggregate(pipeline)]

        source_pipeline = [{"$group": {"_id": "$source", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
        sources = [{"source": d["_id"], "count": d["count"]} async for d in internships.aggregate(source_pipeline)]

        newest = await internships.find_one({}, sort=[("scraped_at", -1)])
        newest_info = None
        if newest:
            newest_info = {"company": newest.get("company"), "title": newest.get("title"), "url": newest.get("url")}

        return {
            "total_internships": total,
            "total_companies": total_companies,
            "total_users": total_users,
            "new_today": new_today,
            "new_this_week": new_this_week,
            "categories": categories,
            "sources": sources,
            "newest": newest_info,
        }
    except Exception:
        return {
            "total_internships": 0,
            "total_companies": 0,
            "total_users": 0,
            "new_today": 0,
            "new_this_week": 0,
            "categories": [],
            "sources": [],
            "newest": None,
        }
