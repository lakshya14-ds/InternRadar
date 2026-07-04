import asyncio
import sys
import httpx

sys.path.append(".")
from app.connectors.ashby_connector import ASHBY_ORGANIZATION_SLUGS

async def check_ashby():
    print("=== Checking Ashby Organization Slugs ===")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    active = []
    inactive = []
    
    async def check_slug(client, slug):
        url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
        try:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code == 200:
                jobs = resp.json().get("jobs", [])
                active.append((slug, len(jobs)))
            else:
                inactive.append((slug, resp.status_code))
        except Exception as e:
            inactive.append((slug, str(e)))

    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    async with httpx.AsyncClient(headers=headers, limits=limits, follow_redirects=True) as client:
        await asyncio.gather(*(check_slug(client, slug) for slug in ASHBY_ORGANIZATION_SLUGS))
        
    print(f"\nActive Ashby Slugs ({len(active)}):")
    for slug, count in sorted(active):
        print(f"  {slug}: {count} raw jobs")
        
    print(f"\nInactive/404 Ashby Slugs ({len(inactive)}):")
    for slug, status in sorted(inactive):
        print(f"  {slug}: {status}")

if __name__ == "__main__":
    asyncio.run(check_ashby())
