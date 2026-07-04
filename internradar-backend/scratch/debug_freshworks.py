import asyncio
import sys
import httpx

sys.path.append(".")
from app.connectors.base_connector import BaseConnector

class Tester(BaseConnector):
    source = "tester"
    async def fetch_jobs(self, companies): return []
    def normalize(self, raw_jobs): return []

tester = Tester()

async def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    url = "https://api.smartrecruiters.com/v1/companies/freshworks/postings"
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        resp = await client.get(url, timeout=15.0)
        if resp.status_code == 200:
            jobs = resp.json().get("content", [])
            print(f"Total raw jobs at Freshworks: {len(jobs)}")
            internships_count = 0
            for j in jobs:
                title = j.get("name", "")
                location_obj = j.get("location", {})
                city = location_obj.get("city", "")
                country = location_obj.get("country", "")
                loc = f"{city}, {country}"
                
                is_intern = tester.is_internship(title)
                is_india = tester.is_india_location(loc)
                
                if "intern" in title.lower() or "trainee" in title.lower() or is_intern:
                    print(f"Candidate: '{title}' | Location: '{loc}' | is_intern gate: {is_intern} | is_india: {is_india}")
                    internships_count += 1
            if internships_count == 0:
                print("No internship candidates found in the listings.")

if __name__ == "__main__":
    asyncio.run(main())
