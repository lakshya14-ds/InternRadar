import asyncio
import sys
import time
from pathlib import Path
from datetime import UTC, datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))

from app.database import mongo
from app.config import get_settings
from app.services.saved_search_service import SavedSearchService
from app.models.internship import InternshipInDB
from bson import ObjectId

async def main():
    settings = get_settings()
    await mongo.connect(settings)
    
    db = mongo.db
    assert db is not None
    
    searches = mongo.get_collection('saved_searches')
    users = mongo.get_collection('users')
    internships = mongo.get_collection('internships')
    
    # 1. Database Counts
    s_count = await searches.count_documents({})
    u_count = await users.count_documents({})
    i_count = await internships.count_documents({})
    
    print("=== Database Counts ===")
    print(f"Total Saved Searches: {s_count}")
    print(f"Total Users: {u_count}")
    print(f"Total Internships: {i_count}")
    
    frequencies = ["instant", "daily", "weekly"]
    for freq in frequencies:
        freq_count = await searches.count_documents({"frequency": freq})
        print(f"  Saved Searches ({freq}): {freq_count}")
        
    print("\n=== Running Email Alert Checks ===")
    svc = SavedSearchService(db, settings)
    
    # Trigger daily digests
    start_time = time.perf_counter()
    print("Running process_digests('daily')...")
    await svc.process_digests("daily")
    daily_duration = time.perf_counter() - start_time
    print(f"Finished process_digests('daily') in {daily_duration:.4f}s")
    
    # Trigger weekly digests
    start_time = time.perf_counter()
    print("Running process_digests('weekly')...")
    await svc.process_digests("weekly")
    weekly_duration = time.perf_counter() - start_time
    print(f"Finished process_digests('weekly') in {weekly_duration:.4f}s")
    
    # Trigger daily profile preference digests
    start_time = time.perf_counter()
    print("Running process_profile_preferences_digests('daily')...")
    await svc.process_profile_preferences_digests("daily")
    daily_pref_duration = time.perf_counter() - start_time
    print(f"Finished process_profile_preferences_digests('daily') in {daily_pref_duration:.4f}s")
    
    # Trigger weekly profile preference digests
    start_time = time.perf_counter()
    print("Running process_profile_preferences_digests('weekly')...")
    await svc.process_profile_preferences_digests("weekly")
    weekly_pref_duration = time.perf_counter() - start_time
    print(f"Finished process_profile_preferences_digests('weekly') in {weekly_pref_duration:.4f}s")
    
    # Test instant alerts if we fetch some internships
    recent_cursor = internships.find().limit(5)
    recent_jobs = [InternshipInDB.model_validate(job) async for job in recent_cursor]
    
    if recent_jobs:
        start_time = time.perf_counter()
        print(f"Running process_instant_alerts with {len(recent_jobs)} internships...")
        await svc.process_instant_alerts(recent_jobs)
        instant_duration = time.perf_counter() - start_time
        print(f"Finished process_instant_alerts in {instant_duration:.4f}s")
    else:
        print("No internships available to test process_instant_alerts.")
        
    # If database counts of saved searches are 0, let's simulate with temporary test data to verify
    if s_count == 0:
        print("\n=== Simulating Email Alert Checks with Temporary Test Data ===")
        
        # Create a test user
        test_email = "temp-test-alert-check@example.com"
        await users.delete_many({"email": test_email})
        
        test_user = {
            "email": test_email,
            "name": "Temp Test User",
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
        user_res = await users.insert_one(test_user)
        test_user_id = str(user_res.inserted_id)
        print(f"Created temporary user: {test_email} (ID: {test_user_id})")
        
        match_category = "Software Engineering"
        
        temp_searches_docs = [
            {
                "user_id": test_user_id,
                "name": "Temp Instant Search",
                "query_params": {"category": match_category},
                "frequency": "instant",
                "last_notified_at": datetime.now(UTC) - timedelta(hours=24),
                "created_at": datetime.now(UTC) - timedelta(hours=24),
            },
            {
                "user_id": test_user_id,
                "name": "Temp Daily Search",
                "query_params": {"category": match_category},
                "frequency": "daily",
                "last_notified_at": datetime.now(UTC) - timedelta(hours=24),
                "created_at": datetime.now(UTC) - timedelta(hours=24),
            },
            {
                "user_id": test_user_id,
                "name": "Temp Weekly Search",
                "query_params": {"category": match_category},
                "frequency": "weekly",
                "last_notified_at": datetime.now(UTC) - timedelta(days=8),
                "created_at": datetime.now(UTC) - timedelta(days=8),
            }
        ]
        
        inserted_search_ids = []
        for doc in temp_searches_docs:
            res = await searches.insert_one(doc)
            inserted_search_ids.append(res.inserted_id)
        print(f"Created {len(inserted_search_ids)} temporary saved searches.")
        
        # Insert a temporary matching internship
        test_job = {
            "external_id": "temp-test-job-1",
            "source": "lever",
            "company": "TempTestCompany",
            "title": "Software Engineer Intern",
            "location": "Bangalore, India",
            "remote": False,
            "url": "https://example.com/temp-test-job",
            "description": "Software engineer intern position",
            "skills": [],
            "tags": [],
            "category": match_category,
            "fingerprint": "temp-test-job-fingerprint",
            "posted_at": datetime.now(UTC) - timedelta(hours=2),
            "scraped_at": datetime.now(UTC) - timedelta(hours=2)
        }
        await internships.delete_many({"company": "TempTestCompany"})
        await internships.insert_one(test_job)
        print("Inserted temporary matching internship.")
        
        print("\n--- Running checks with temp data ---")
        
        start_time = time.perf_counter()
        await svc.process_digests("daily")
        print(f"process_digests('daily') with test data took {time.perf_counter() - start_time:.4f}s")
        
        start_time = time.perf_counter()
        await svc.process_digests("weekly")
        print(f"process_digests('weekly') with test data took {time.perf_counter() - start_time:.4f}s")
        
        start_time = time.perf_counter()
        await svc.process_profile_preferences_digests("daily")
        print(f"process_profile_preferences_digests('daily') with test data took {time.perf_counter() - start_time:.4f}s")
        
        db_job = await internships.find_one({"company": "TempTestCompany"})
        if db_job:
            job_obj = InternshipInDB.model_validate(db_job)
            start_time = time.perf_counter()
            await svc.process_instant_alerts([job_obj])
            print(f"process_instant_alerts with test data took {time.perf_counter() - start_time:.4f}s")
        
        print("\n--- Cleaning up temporary data ---")
        await users.delete_one({"_id": ObjectId(test_user_id)})
        for s_id in inserted_search_ids:
            await searches.delete_one({"_id": s_id})
        await internships.delete_many({"company": "TempTestCompany"})
        print("Temporary test data cleaned up.")
        
    await mongo.close()

if __name__ == "__main__":
    asyncio.run(main())

