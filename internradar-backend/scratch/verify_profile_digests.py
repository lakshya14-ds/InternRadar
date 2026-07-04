import asyncio
import logging
from datetime import UTC, datetime, timedelta
from app.config import get_settings
from app.database import mongo
from app.models.internship import InternshipInDB
from app.services.saved_search_service import SavedSearchService
from bson import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    settings = get_settings()
    await mongo.connect(settings)
    
    db = mongo.db
    assert db is not None
    users_col = db["users"]
    internships_col = db["internships"]

    # 1. Create a dummy test user with preferences
    test_user_id = ObjectId()
    test_email = "test-user-preferences@example.com"
    
    # Remove any existing test user with this email
    await users_col.delete_one({"email": test_email})
    
    user_doc = {
        "_id": test_user_id,
        "email": test_email,
        "name": "Test User Prefs",
        "hashed_password": "dummy_hash",
        "preferences": {
            "preferred_categories": ["Software Engineering"],
            "preferred_locations": ["Bangalore"],
            "remote_only": False,
            "email_alerts_enabled": True
        },
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }
    await users_col.insert_one(user_doc)
    logger.info("Inserted test user: %s", test_email)

    # 2. Create matching & non-matching internships
    # Clean up any test internships
    await internships_col.delete_many({"company": "TestPrefCompany"})

    # Matching internship
    matching_job = {
        "external_id": "test-pref-1",
        "source": "lever",
        "company": "TestPrefCompany",
        "title": "Software Engineer Intern",
        "location": "Bangalore, India",
        "remote": False,
        "url": "https://example.com/matching",
        "description": "Matching job description",
        "skills": [],
        "tags": [],
        "category": "Software Engineering",
        "fingerprint": "matching-fingerprint-123",
        "posted_at": datetime.now(UTC) - timedelta(hours=2),
        "scraped_at": datetime.now(UTC) - timedelta(hours=2)
    }
    await internships_col.insert_one(matching_job)

    # Non-matching category
    non_matching_category = {
        "external_id": "test-pref-2",
        "source": "lever",
        "company": "TestPrefCompany",
        "title": "Marketing Intern",
        "location": "Bangalore, India",
        "remote": False,
        "url": "https://example.com/non-match-cat",
        "description": "Non matching category description",
        "skills": [],
        "tags": [],
        "category": "Marketing",
        "fingerprint": "non-matching-cat-fingerprint",
        "posted_at": datetime.now(UTC) - timedelta(hours=2),
        "scraped_at": datetime.now(UTC) - timedelta(hours=2)
    }
    await internships_col.insert_one(non_matching_category)

    # Non-matching location
    non_matching_location = {
        "external_id": "test-pref-3",
        "source": "lever",
        "company": "TestPrefCompany",
        "title": "Software Engineer Intern",
        "location": "Mumbai, India",
        "remote": False,
        "url": "https://example.com/non-match-loc",
        "description": "Non matching location description",
        "skills": [],
        "tags": [],
        "category": "Software Engineering",
        "fingerprint": "non-matching-loc-fingerprint",
        "posted_at": datetime.now(UTC) - timedelta(hours=2),
        "scraped_at": datetime.now(UTC) - timedelta(hours=2)
    }
    await internships_col.insert_one(non_matching_location)

    logger.info("Inserted test internships")

    # 3. Initialize SavedSearchService and trigger daily digests
    assert db is not None
    svc = SavedSearchService(db, settings)
    
    logger.info("Running daily profile preference digests...")
    await svc.process_profile_preferences_digests("daily")
    
    # 4. Check if the user document was updated with `last_preferences_notified_at`
    updated_user = await users_col.find_one({"_id": test_user_id})
    assert updated_user is not None
    last_notified = updated_user.get("last_preferences_notified_at")
    
    if last_notified:
        logger.info("SUCCESS: User profile digest was processed and last_preferences_notified_at was updated: %s", last_notified)
    else:
        logger.error("FAILURE: last_preferences_notified_at was not updated on user document")

    # Clean up
    await users_col.delete_one({"_id": test_user_id})
    await internships_col.delete_many({"company": "TestPrefCompany"})
    logger.info("Cleaned up database")
    
    await mongo.close()

if __name__ == "__main__":
    asyncio.run(main())
