"""Platform statistics route."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Request
from motor.motor_asyncio import AsyncIOMotorCollection

from app.classification.company_classifier import FEATURED_MNCS, STARTUP_SOURCES, classify_company
from app.database import mongo

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
async def get_stats(request: Request) -> dict:
    try:
        import re
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

        # Category Breakdown
        pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}]
        categories = [{"category": d["_id"] or "Other", "count": d["count"]} async for d in internships.aggregate(pipeline)]

        # Source Breakdown
        source_pipeline = [{"$group": {"_id": "$source", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]
        sources = [{"source": d["_id"], "count": d["count"]} async for d in internships.aggregate(source_pipeline)]

        # Top Companies (Top 10)
        company_pipeline = [{"$group": {"_id": "$company", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}]
        top_companies = [{"company": d["_id"] or "Unknown", "count": d["count"]} async for d in internships.aggregate(company_pipeline)]

        # Top Locations (Top 10)
        location_pipeline = [{"$group": {"_id": "$location", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}]
        top_locations = [{"location": d["_id"] or "Remote", "count": d["count"]} async for d in internships.aggregate(location_pipeline)]

        # Company-type distribution (3-way: MNC / Startup / Enterprise).
        # Prefer the persisted ``company_type`` field where available; fall
        # back to live classification for older documents.
        startup_vs_mnc = [
            {"name": "MNCs", "value": 0},
            {"name": "Startups", "value": 0},
            {"name": "Enterprise", "value": 0},
        ]
        if total > 0:
            mnc_count = await internships.count_documents({
                "$or": [
                    {"company_type": "mnc"},
                    {"company": {"$regex": "|".join(f"^{re.escape(m)}$" for m in FEATURED_MNCS), "$options": "i"}},
                ]
            })
            startup_count = await internships.count_documents({
                "$or": [
                    {"company_type": "startup"},
                    {"source": {"$in": list(STARTUP_SOURCES)}},
                ]
            })
            enterprise_count = max(total - mnc_count - startup_count, 0)
            startup_vs_mnc = [
                {"name": "MNCs", "value": mnc_count},
                {"name": "Startups", "value": startup_count},
                {"name": "Enterprise", "value": enterprise_count},
            ]

        # Remote vs Onsite Distribution
        remote_count = await internships.count_documents({"remote": True})
        onsite_count = max(total - remote_count, 0)
        remote_vs_onsite = [
            {"name": "Remote", "value": remote_count},
            {"name": "Onsite/Hybrid", "value": onsite_count}
        ]

        newest = await internships.find_one({}, sort=[("scraped_at", -1)])
        newest_info = None
        if newest:
            newest_info = {"company": newest.get("company"), "title": newest.get("title"), "url": newest.get("url")}

        # Calculate daily growth trends (past 7 days)
        growth = []
        for i in range(7):
            day = datetime.now(UTC).date() - timedelta(days=i)
            start_dt = datetime.combine(day, datetime.min.time(), tzinfo=UTC)
            end_dt = datetime.combine(day, datetime.max.time(), tzinfo=UTC)
            cnt = await internships.count_documents({"scraped_at": {"$gte": start_dt, "$lte": end_dt}})
            growth.append({"date": day.strftime("%b %d"), "count": cnt})
        growth.reverse()

        # Scraper Performance Metrics
        scheduler = getattr(request.app.state, "scheduler", None)
        connector_perf = []
        if scheduler:
            for item in scheduler.progress:
                connector_perf.append({
                    "connector": item.connector,
                    "runtime_seconds": item.runtime_seconds,
                    "fetched": item.fetched,
                    "inserted": item.inserted,
                    "status": item.status,
                    "speed": item.speed,
                    "circuit_breaker_state": item.circuit_breaker_state,
                })

        return {
            "total_internships": total,
            "total_companies": total_companies,
            "total_users": total_users,
            "new_today": new_today,
            "new_this_week": new_this_week,
            "categories": categories,
            "sources": sources,
            "top_companies": top_companies,
            "top_locations": top_locations,
            "startup_vs_mnc": startup_vs_mnc,
            "remote_vs_onsite": remote_vs_onsite,
            "newest": newest_info,
            "growth": growth,
            "connector_performance": connector_perf,
        }
    except Exception as exc:
        import logging
        logging.getLogger(__name__).exception("Failed to build statistics: %s", exc)
        return {
            "total_internships": 0,
            "total_companies": 0,
            "total_users": 0,
            "new_today": 0,
            "new_this_week": 0,
            "categories": [],
            "sources": [],
            "newest": None,
            "growth": [],
            "connector_performance": [],
        }

