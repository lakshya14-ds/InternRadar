"""SavedSearchService to persist search configurations and process notifications."""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.models.internship import InternshipInDB
from app.notifications.providers.email_provider import EmailProvider

logger = logging.getLogger(__name__)


class SavedSearchService:
    """Manage saved searches and filter-matching alert pipelines."""

    def __init__(self, db: AsyncIOMotorDatabase, settings: Any) -> None:
        self.db = db
        self.saved_searches = db["saved_searches"]
        self.users = db["users"]
        self.internships = db["internships"]
        self.settings = settings

    async def save_search(
        self,
        user_id: str,
        name: str,
        query_params: dict[str, Any],
        frequency: str = "daily",
    ) -> dict[str, Any]:
        """Save a search query for a user."""
        document = {
            "user_id": user_id,
            "name": name.strip(),
            "query_params": query_params,
            "frequency": frequency,  # instant, daily, weekly
            "last_notified_at": datetime.now(UTC),
            "created_at": datetime.now(UTC),
        }
        result = await self.saved_searches.insert_one(document)
        document["_id"] = str(result.inserted_id)
        return document

    async def list_saved_searches(self, user_id: str) -> list[dict[str, Any]]:
        """List all saved searches for a user."""
        cursor = self.saved_searches.find({"user_id": user_id})
        return [{**doc, "_id": str(doc["_id"])} async for doc in cursor]

    async def delete_saved_search(self, user_id: str, search_id: str) -> bool:
        """Delete a saved search configuration."""
        res = await self.saved_searches.delete_one({"_id": ObjectId(search_id), "user_id": user_id})
        return res.deleted_count > 0

    def matches_search(self, internship: InternshipInDB, query_params: dict[str, Any]) -> bool:
        """Check if a normalized internship matches saved search criteria."""
        # 1. Text Query (Fuzzy check)
        q = query_params.get("q")
        if q:
            q_lower = q.lower()
            haystack = " ".join([
                internship.title or "",
                internship.company or "",
                internship.description or "",
                " ".join(internship.skills or [])
            ]).lower()
            if q_lower not in haystack:
                return False

        # 2. Title Filter
        title = query_params.get("title")
        if title and title.lower() not in (internship.title or "").lower():
            return False

        # 3. Company Filter
        company = query_params.get("company")
        if company and company.lower() not in (internship.company or "").lower():
            return False

        # 4. Location Filter
        location = query_params.get("location")
        if location and location.lower() not in (internship.location or "").lower():
            return False

        # 5. Category Filter
        category = query_params.get("category")
        if category and category != internship.category:
            return False

        # 6. Source Filter
        source = query_params.get("source")
        if source and source != internship.source:
            return False

        # 7. Remote Filter
        remote = query_params.get("remote")
        if remote is not None and bool(remote) != internship.remote:
            return False

        # 8. Stipend Filters
        min_stipend = query_params.get("min_stipend")
        if min_stipend is not None:
            val = float(min_stipend)
            if internship.stipend_numeric is None or internship.stipend_numeric < val:
                return False

        max_stipend = query_params.get("max_stipend")
        if max_stipend is not None:
            val = float(max_stipend)
            if internship.stipend_numeric is None or internship.stipend_numeric > val:
                return False

        # 9. Duration Filter
        duration = query_params.get("duration")
        if duration and duration.lower() not in (internship.duration or "").lower():
            return False

        return True

    async def process_instant_alerts(self, new_internships: list[InternshipInDB]) -> None:
        """Scan instant searches and send email alerts for matching newly inserted internships."""
        if not new_internships:
            return

        cursor = self.saved_searches.find({"frequency": "instant"})
        async for search in cursor:
            user_id = search["user_id"]
            user = await self.users.find_one({"_id": ObjectId(user_id)})
            if not user or not user.get("preferences", {}).get("email_alerts_enabled", True):
                continue

            matches = [job for job in new_internships if self.matches_search(job, search["query_params"])]
            if matches:
                await self._send_instant_email(user["email"], search["name"], matches)
                await self.saved_searches.update_one(
                    {"_id": search["_id"]},
                    {"$set": {"last_notified_at": datetime.now(UTC)}}
                )

    async def process_digests(self, frequency: str) -> None:
        """Run daily or weekly digest scans, aggregating jobs since last notifications."""
        cursor = self.saved_searches.find({"frequency": frequency})
        async for search in cursor:
            user_id = search["user_id"]
            user = await self.users.find_one({"_id": ObjectId(user_id)})
            if not user or not user.get("preferences", {}).get("email_alerts_enabled", True):
                continue

            last_notified = search.get("last_notified_at", datetime.now(UTC) - timedelta(days=1))
            
            # Query recent internships
            job_cursor = self.internships.find({"posted_at": {"$gt": last_notified}})
            recent_jobs = [InternshipInDB.model_validate(job) async for job in job_cursor]

            matches = [job for job in recent_jobs if self.matches_search(job, search["query_params"])]
            if matches:
                await self._send_digest_email(user["email"], search["name"], matches, frequency)
                await self.saved_searches.update_one(
                    {"_id": search["_id"]},
                    {"$set": {"last_notified_at": datetime.now(UTC)}}
                )

    async def _send_instant_email(self, email: str, search_name: str, matches: list[InternshipInDB]) -> None:
        """Send instant match alert via SMTP email."""
        logger.info("Sending instant saved search alert for '%s' to %s", search_name, email)
        provider = EmailProvider(
            self.settings.smtp_host, self.settings.smtp_port,
            self.settings.smtp_username, self.settings.smtp_password,
            self.settings.email_from, email
        )
        
        # Build text message
        body_parts = [f"We found {len(matches)} new internships matching your saved search '{search_name}':\n"]
        for job in matches[:10]:
            body_parts.append(
                f"- {job.title} at {job.company}\n"
                f"  Location: {job.location}\n"
                f"  Stipend: {job.stipend or 'Not specified'}\n"
                f"  Link: {job.url}\n"
            )
        if len(matches) > 10:
            body_parts.append(f"...and {len(matches) - 10} more! View them on InternRadar.\n")

        # Mock SMTP fallback logging
        if not self.settings.smtp_host:
            logger.info("Email is not configured; logged message:\n%s", "".join(body_parts))
            return

        # Trigger SMTP send in helper class
        message = provider._send_message
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["Subject"] = f"[InternRadar Alert] New Internships for '{search_name}'"
        msg["From"] = self.settings.email_from
        msg["To"] = email
        msg.set_content("".join(body_parts))
        await asyncio.to_thread(provider._send_message, msg)

    async def _send_digest_email(self, email: str, search_name: str, matches: list[InternshipInDB], frequency: str) -> None:
        """Send daily/weekly aggregated match alerts."""
        logger.info("Sending %s saved search digest for '%s' to %s", frequency, search_name, email)
        provider = EmailProvider(
            self.settings.smtp_host, self.settings.smtp_port,
            self.settings.smtp_username, self.settings.smtp_password,
            self.settings.email_from, email
        )
        
        body_parts = [f"Here is your {frequency} digest of internships matching your saved search '{search_name}':\n"]
        for job in matches[:25]:
            body_parts.append(
                f"- {job.title} at {job.company}\n"
                f"  Location: {job.location}\n"
                f"  Stipend: {job.stipend or 'Not specified'}\n"
                f"  Link: {job.url}\n"
            )

        if not self.settings.smtp_host:
            logger.info("Email is not configured; logged digest:\n%s", "".join(body_parts))
            return

        from email.message import EmailMessage
        msg = EmailMessage()
        msg["Subject"] = f"[InternRadar Digest] {frequency.capitalize()} updates for '{search_name}'"
        msg["From"] = self.settings.email_from
        msg["To"] = email
        msg.set_content("".join(body_parts))
        await asyncio.to_thread(provider._send_message, msg)

    def matches_profile_preferences(self, internship: InternshipInDB, preferences: dict[str, Any]) -> bool:
        """Check if a normalized internship matches user profile target categories/locations."""
        if not preferences.get("email_alerts_enabled", True):
            return False

        if preferences.get("remote_only", False) and not internship.remote:
            return False

        preferred_categories = preferences.get("preferred_categories", [])
        if preferred_categories and internship.category not in preferred_categories:
            return False

        preferred_locations = preferences.get("preferred_locations", [])
        if preferred_locations:
            loc_lower = (internship.location or "").lower()
            matched = False
            for loc in preferred_locations:
                if loc.lower() in loc_lower:
                    matched = True
                    break
                if loc.lower() == "remote" and internship.remote:
                    matched = True
                    break
            if not matched:
                return False

        return True

    async def process_profile_preferences_digests(self, frequency: str) -> None:
        """Run daily/weekly digest scans for user profile preferences."""
        query = {
            "preferences.email_alerts_enabled": True,
            "$or": [
                {"preferences.preferred_categories": {"$exists": True, "$ne": []}},
                {"preferences.preferred_locations": {"$exists": True, "$ne": []}}
            ]
        }
        cursor = self.users.find(query)
        
        days = 7 if frequency == "weekly" else 1
        time_threshold = datetime.now(UTC) - timedelta(days=days)
        
        job_cursor = self.internships.find({
            "$or": [
                {"posted_at": {"$gt": time_threshold}},
                {"scraped_at": {"$gt": time_threshold}}
            ]
        })
        recent_jobs = [InternshipInDB.model_validate(job) async for job in job_cursor]
        
        if not recent_jobs:
            logger.info("No recent jobs found for profile preference digests (%s)", frequency)
            return

        async for user in cursor:
            preferences = user.get("preferences", {})
            
            last_notified = user.get("last_preferences_notified_at")
            if last_notified:
                if isinstance(last_notified, str):
                    try:
                        last_notified = datetime.fromisoformat(last_notified)
                    except ValueError:
                        last_notified = None
                
                if last_notified and last_notified.tzinfo is None:
                    last_notified = last_notified.replace(tzinfo=UTC)
                
                if last_notified and (datetime.now(UTC) - last_notified) < timedelta(hours=23 if frequency == "daily" else 160):
                    continue

            matches = []
            for job in recent_jobs:
                posted_time = job.posted_at or job.scraped_at or datetime.min
                if posted_time.tzinfo is None:
                    posted_time = posted_time.replace(tzinfo=UTC)
                
                if last_notified and posted_time <= last_notified:
                    continue
                
                if self.matches_profile_preferences(job, preferences):
                    matches.append(job)

            if matches:
                await self._send_profile_preferences_email(user["email"], user.get("name", "Student"), matches, frequency)
                await self.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"last_preferences_notified_at": datetime.now(UTC)}}
                )

    async def _send_profile_preferences_email(self, email: str, name: str, matches: list[InternshipInDB], frequency: str) -> None:
        """Send daily/weekly profile preference match alerts via SMTP."""
        logger.info("Sending %s profile preference digest to %s", frequency, email)
        provider = EmailProvider(
            self.settings.smtp_host, self.settings.smtp_port,
            self.settings.smtp_username, self.settings.smtp_password,
            self.settings.email_from, email
        )
        
        body_parts = [
            f"Hi {name},\n\n"
            f"Here is your {frequency} digest of fresh internships matching your profile target categories/locations:\n\n"
        ]
        for job in matches[:25]:
            body_parts.append(
                f"- {job.title} at {job.company}\n"
                f"  Location: {job.location}\n"
                f"  Stipend: {job.stipend or 'Not specified'}\n"
                f"  Link: {job.url}\n\n"
            )
        
        if len(matches) > 25:
            body_parts.append(f"...and {len(matches) - 25} more! View all opportunities on InternRadar.\n\n")

        body_parts.append("Manage your profile and alert preferences here: http://localhost:3000/profile\n")

        if not self.settings.smtp_host:
            logger.info("Email is not configured; logged digest:\n%s", "".join(body_parts))
            return

        from email.message import EmailMessage
        msg = EmailMessage()
        msg["Subject"] = f"[InternRadar] {frequency.capitalize()} Internship Matches for You"
        msg["From"] = self.settings.email_from
        msg["To"] = email
        msg.set_content("".join(body_parts))
        await asyncio.to_thread(provider._send_message, msg)
