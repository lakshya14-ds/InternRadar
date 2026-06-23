import asyncio
from urllib.parse import urlparse
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

async def migrate_internships():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.db_name]
    collection = db["internships"]

    print("--- Starting URL Migration for Existing Database Entries ---")
    
    # 1. SmartRecruiters
    cursor = collection.find({"source": "smartrecruiters"})
    sr_jobs = await cursor.to_list(length=1000)
    print(f"Found {len(sr_jobs)} SmartRecruiters jobs in the database.")
    sr_updates = 0
    for job in sr_jobs:
        old_url = job.get("url", "")
        if "api.smartrecruiters.com" in old_url:
            # Reconstruct candidate URL
            try:
                # Format: https://api.smartrecruiters.com/v1/companies/{company}/postings/{id}
                parts = old_url.split("/")
                if "companies" in parts and "postings" in parts:
                    comp_idx = parts.index("companies")
                    post_idx = parts.index("postings")
                    comp_slug = parts[comp_idx + 1]
                    job_id = parts[post_idx + 1]
                    new_url = f"https://jobs.smartrecruiters.com/{comp_slug}/{job_id}"
                    
                    await collection.update_one({"_id": job["_id"]}, {"$set": {"url": new_url}})
                    sr_updates += 1
            except Exception as e:
                print(f"Failed to migrate SmartRecruiters URL {old_url}: {e}")
    print(f"Updated {sr_updates} SmartRecruiters URLs.")

    # 2. Workday
    cursor = collection.find({"source": "workday"})
    wd_jobs = await cursor.to_list(length=1000)
    print(f"Found {len(wd_jobs)} Workday jobs in the database.")
    wd_updates = 0
    for job in wd_jobs:
        old_url = job.get("url", "")
        if "wday/cxs" in old_url:
            try:
                parsed = urlparse(old_url)
                host = parsed.netloc
                parts = parsed.path.strip("/").split("/")
                if "jobs" in parts:
                    jobs_idx = parts.index("jobs")
                    board = parts[3] if len(parts) >= 4 else ""
                    external_path_parts = parts[jobs_idx + 1:]
                    if board and external_path_parts:
                        ext_path = "/" + "/".join(external_path_parts)
                        new_url = f"https://{host}/en-US/{board}{ext_path}"
                        
                        await collection.update_one({"_id": job["_id"]}, {"$set": {"url": new_url}})
                        wd_updates += 1
            except Exception as e:
                print(f"Failed to migrate Workday URL {old_url}: {e}")
    print(f"Updated {wd_updates} Workday URLs.")

    # 3. Manual source (just double checking if any relative links remain)
    cursor = collection.find({"source": "manual"})
    manual_jobs = await cursor.to_list(length=1000)
    print(f"Found {len(manual_jobs)} manual source jobs in the database.")
    manual_updates = 0
    manual_deletes = 0
    for job in manual_jobs:
        old_url = job.get("url", "")
        new_url = old_url
        
        # Comprehensive Internshala URL correction
        if "internshala.com" in old_url:
            if "/detail/" in old_url:
                slug = old_url.split("/detail/")[-1]
                new_url = f"https://internshala.com/internship/detail/{slug}"
            else:
                # If there's no detail slug, it's a search page link, delete it!
                await collection.delete_one({"_id": job["_id"]})
                manual_deletes += 1
                continue
            
        if new_url != old_url:
            await collection.update_one({"_id": job["_id"]}, {"$set": {"url": new_url}})
            manual_updates += 1
    print(f"Updated {manual_updates} manual source URLs. Deleted {manual_deletes} invalid manual entries.")

    client.close()
    print("--- URL Migration Complete ---")

if __name__ == "__main__":
    asyncio.run(migrate_internships())
