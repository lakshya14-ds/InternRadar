import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

async def update_yc_urls():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.db_name]
    collection = db["internships"]

    print("--- Starting YC URL & Info Update ---")

    # 1. Update general URLs that contain gigaml/jobs to giga/jobs
    cursor = collection.find({"url": {"$regex": "ycombinator\\.com/companies/gigaml/jobs"}})
    gigaml_jobs = await cursor.to_list(length=1000)
    print(f"Found {len(gigaml_jobs)} jobs with gigaml/jobs URL.")
    for job in gigaml_jobs:
        new_url = job["url"].replace("gigaml/jobs", "giga/jobs")
        await collection.update_one({"_id": job["_id"]}, {"$set": {"url": new_url}})
        print(f"Updated URL for job ID {job['_id']} from {job['url']} to {new_url}")

    # 2. Update general URLs that contain invideo/jobs (if any)
    cursor = collection.find({"url": {"$regex": "ycombinator\\.com/companies/invideo/jobs"}})
    invideo_jobs = await cursor.to_list(length=1000)
    print(f"Found {len(invideo_jobs)} jobs with invideo/jobs URL.")
    for job in invideo_jobs:
        if job.get("company") == "InVideo":
            new_url = "https://www.ycombinator.com/companies/groww/jobs"
            await collection.update_one(
                {"_id": job["_id"]}, 
                {"$set": {
                    "company": "Groww",
                    "title": "Frontend Engineering Intern (Web Platform)",
                    "location": "Bangalore, India",
                    "url": new_url,
                    "description": "Work on India's largest investment platform. Build beautiful, high-performance web applications using React.",
                    "skills": ["React", "TypeScript", "TailwindCSS"],
                    "stipend": "INR 40,000 /month",
                    "company_logo": "https://logo.clearbit.com/groww.in",
                    "work_type": "Hybrid",
                }}
            )
            print(f"Updated mock InVideo job ID {job['_id']} to Groww.")
        else:
            # Just fallback update
            new_url = job["url"].replace("invideo/jobs", "groww/jobs")
            await collection.update_one({"_id": job["_id"]}, {"$set": {"url": new_url}})
            print(f"Updated URL for job ID {job['_id']} to {new_url}")

    # 3. Explicitly update mock entries by external_id
    # yc-mock-2 (InVideo -> Groww)
    res2 = await collection.update_one(
        {"external_id": "yc-mock-2"},
        {"$set": {
            "company": "Groww",
            "title": "Frontend Engineering Intern (Web Platform)",
            "location": "Bangalore, India",
            "url": "https://www.ycombinator.com/companies/groww/jobs",
            "description": "Work on India's largest investment platform. Build beautiful, high-performance web applications using React.",
            "skills": ["React", "TypeScript", "TailwindCSS"],
            "stipend": "INR 40,000 /month",
            "company_logo": "https://logo.clearbit.com/groww.in",
            "work_type": "Hybrid",
        }}
    )
    if res2.matched_count > 0:
        print("Explicitly updated yc-mock-2 mock entry to Groww in DB.")

    # yc-mock-3 (GigaML URL fix)
    res3 = await collection.update_one(
        {"external_id": "yc-mock-3"},
        {"$set": {
            "url": "https://www.ycombinator.com/companies/giga/jobs",
            "company_logo": "https://logo.clearbit.com/giga.ai"
        }}
    )
    if res3.matched_count > 0:
        print("Explicitly updated yc-mock-3 mock entry URL and logo in DB.")

    client.close()
    print("--- YC URL & Info Update Complete ---")

if __name__ == "__main__":
    asyncio.run(update_yc_urls())
