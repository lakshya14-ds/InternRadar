import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append(".")
from app.config import get_settings

async def main():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.db_name]
    collection = db["internships"]
    
    sources = ["unstop", "simplify", "yc", "workday", "jsearch"]
    for source in sources:
        print(f"\n--- Sample internships for source: {source} ---")
        cursor = collection.find({"source": source})
        jobs = await cursor.to_list(length=10)
        for job in jobs:
            print(f"ID: {job['_id']} | Company: {job.get('company')} | Title: {job.get('title')}")
            print(f"  URL: {job.get('url')}")
            print(f"  External ID: {job.get('external_id')}")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
