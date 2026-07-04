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
    
    url = "https://api.ashbyhq.com/posting-api/job-board/sarvam"
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        resp = await client.get(url, timeout=15.0)
        if resp.status_code == 200:
            jobs = resp.json().get("jobs", [])
            print(f"Total raw jobs at Sarvam: {len(jobs)}")
            for j in jobs:
                title = j.get("title", "")
                loc = j.get("location", "")
                
                # Check if it has any intern keywords in title
                is_intern_title = any(kw in title.lower() for kw in ["intern", "trainee", "apprentice"])
                is_india = tester.is_india_location(loc)
                
                if is_intern_title or "software" in title.lower() or "engineer" in title.lower():
                    print(f"Job: '{title}' | Location: '{loc}'")
                    print(f"  is_internship gate: {tester.is_internship(title)}")
                    print(f"  is_india_location: {is_india}")

if __name__ == "__main__":
    asyncio.run(main())
