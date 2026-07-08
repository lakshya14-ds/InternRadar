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
                    board = parts[jobs_idx - 1] if jobs_idx >= 1 else ""
                    external_path_parts = parts[jobs_idx + 1:]
                    ext_path = ""
                    if external_path_parts:
                        ext_path = "/" + "/".join(external_path_parts)
                    if board:
                        new_url = f"https://{host}/en-US/{board}{ext_path}"
                        await collection.update_one({"_id": job["_id"]}, {"$set": {"url": new_url}})
                        wd_updates += 1
            except Exception as e:
                print(f"Failed to migrate Workday URL {old_url}: {e}")
    print(f"Updated {wd_updates} Workday URLs.")

    # 3. Unstop
    cursor = collection.find({"source": "unstop"})
    unstop_jobs = await cursor.to_list(length=1000)
    print(f"Found {len(unstop_jobs)} Unstop jobs in the database.")
    unstop_updates = 0
    for job in unstop_jobs:
        old_url = job.get("url", "")
        if "unstop-1" in old_url or "unstop-1" in str(job.get("external_id", "")):
            new_url = "https://unstop.com/company/cred-124625"
            await collection.update_one({"_id": job["_id"]}, {"$set": {"url": new_url}})
            unstop_updates += 1
    print(f"Updated {unstop_updates} Unstop URLs.")

    # 4. Simplify Mock URLs
    cursor = collection.find({"source": "simplify"})
    simplify_jobs = await cursor.to_list(length=1000)
    print(f"Found {len(simplify_jobs)} Simplify jobs in the database.")
    simplify_updates = 0
    for job in simplify_jobs:
        ext_id = str(job.get("external_id", ""))
        old_url = job.get("url", "")
        new_url = old_url
        if "simplify-mock-1" in ext_id or "uber" in old_url:
            new_url = "https://simplify.jobs/c/uber"
        elif "simplify-mock-2" in ext_id or "adobe" in old_url:
            new_url = "https://simplify.jobs/c/adobe"
        elif "simplify-mock-3" in ext_id or "postman" in old_url:
            new_url = "https://simplify.jobs/c/postman"

        if new_url != old_url:
            await collection.update_one({"_id": job["_id"]}, {"$set": {"url": new_url}})
            simplify_updates += 1
    print(f"Updated {simplify_updates} Simplify URLs.")

    # 5. YC Mock URLs
    cursor = collection.find({"source": "yc"})
    yc_jobs = await cursor.to_list(length=1000)
    print(f"Found {len(yc_jobs)} YC jobs in the database.")
    yc_updates = 0
    for job in yc_jobs:
        ext_id = str(job.get("external_id", ""))
        old_url = job.get("url", "")
        new_url = old_url
        if "yc-mock-1" in ext_id:
            new_url = "https://www.ycombinator.com/companies/zepto/jobs"
        elif "yc-mock-2" in ext_id:
            new_url = "https://www.ycombinator.com/companies/groww/jobs"
        elif "yc-mock-3" in ext_id:
            new_url = "https://www.ycombinator.com/companies/giga/jobs"

        if new_url != old_url:
            await collection.update_one({"_id": job["_id"]}, {"$set": {"url": new_url}})
            yc_updates += 1
    print(f"Updated {yc_updates} YC URLs.")

    # 6. JSearch Mock URLs
    cursor = collection.find({"source": "jsearch"})
    jsearch_jobs = await cursor.to_list(length=1000)
    print(f"Found {len(jsearch_jobs)} JSearch jobs in the database.")
    jsearch_updates = 0
    for job in jsearch_jobs:
        ext_id = str(job.get("external_id", ""))
        old_url = job.get("url", "")
        new_url = old_url
        if "mock-jsearch-1" in ext_id:
            new_url = "https://careers.google.com/jobs/results/?q=intern"
        elif "mock-jsearch-2" in ext_id:
            new_url = "https://careers.microsoft.com/us/en/search-results?keywords=internship"
        elif "mock-jsearch-3" in ext_id:
            new_url = "https://razorpay.com/jobs/"
        elif "mock-jsearch-4" in ext_id:
            new_url = "https://cred.club/careers"
        elif "mock-jsearch-5" in ext_id:
            new_url = "https://paytm.com/careers"

        if new_url != old_url:
            await collection.update_one({"_id": job["_id"]}, {"$set": {"url": new_url}})
            jsearch_updates += 1
    print(f"Updated {jsearch_updates} JSearch URLs.")

    # 7. Manual source (just double checking if any relative links remain)
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
