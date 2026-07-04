import asyncio
import logging
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Setup path and logging
sys.path.append(".")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("cleanup_database")

from app.config import get_settings
from app.connectors.base_connector import BaseConnector

# Dummy subclass to access filter methods
class FilterHelper(BaseConnector):
    source = "helper"
    async def fetch_jobs(self, companies): return []
    def normalize(self, raw_jobs): return []

async def run_cleanup():
    settings = get_settings()
    logger.info("Connecting to MongoDB: %s", settings.mongo_uri)
    logger.info("Target Database: %s", settings.db_name)
    
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.db_name]
    collection = db["internships"]

    helper = FilterHelper()
    
    total_docs = await collection.count_documents({})
    logger.info("Total documents in database before cleanup: %d", total_docs)

    deleted_count = 0
    retained_count = 0

    # Retrieve all documents to analyze
    cursor = collection.find({})
    async for doc in cursor:
        doc_id = doc["_id"]
        title = doc.get("title", "")
        description = doc.get("description", "")
        location = doc.get("location", "")
        url = doc.get("url", "")
        source = doc.get("source", "")
        external_id = doc.get("external_id", "")

        delete_reason = None

        # Check for undefined in URL
        if "undefined" in str(url).lower():
            delete_reason = "undefined URL"
        
        # Check if it is an internship using our new word boundary checks
        # Skip this check for mock data since they are predefined fallbacks
        # Skip validation for all mock listings
        elif not (source == "simplify" and "simplify-mock-" in str(external_id)) and \
             not (source == "jsearch" and "mock-jsearch-" in str(external_id)) and \
             not (source == "handshake" and "hs-mock-" in str(external_id)) and \
             not (source == "ripplematch" and "rm-mock-" in str(external_id)) and \
             not (source == "wellfound" and "wf-mock-" in str(external_id)) and \
             not (source == "workday" and "wd-mock-" in str(external_id)):
            
            # Perform strict validation - bypass Phase 1 title check for internship-only sources
            check_title = source not in ("internshala", "simplify")
            is_intern = helper.is_internship(title, description, check_title=check_title)
            is_india = helper.is_india_location(location) or doc.get("remote")

            if not is_intern:
                delete_reason = "fails internship title/description check"
            elif not is_india:
                delete_reason = "fails India/Remote location check"

        if delete_reason:
            logger.info("Deleting: [ID: %s] | Company: %s | Title: %s | Reason: %s", doc_id, doc.get("company"), title, delete_reason)
            await collection.delete_one({"_id": doc_id})
            deleted_count += 1
        else:
            retained_count += 1

    logger.info("--- Cleanup Completed ---")
    logger.info("Deleted documents: %d", deleted_count)
    logger.info("Retained documents: %d", retained_count)
    
    total_after = await collection.count_documents({})
    logger.info("Total documents in database after cleanup: %d", total_after)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(run_cleanup())
