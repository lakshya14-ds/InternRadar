import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append(".")
from app.config import get_settings

async def main():
    settings = get_settings()
    print(f"Connecting to MongoDB: {settings.mongo_uri}")
    print(f"Database: {settings.db_name}")
    
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.db_name]
    collection = db["internships"]
    
    total = await collection.count_documents({})
    print(f"\nTotal internships in DB: {total}")
    
    pipeline = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    results = await collection.aggregate(pipeline).to_list(None)
    print("\nBreakdown by source:")
    for res in results:
        print(f"  {res['_id'] or 'Unknown'}: {res['count']} internships")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
