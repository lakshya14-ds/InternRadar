import asyncio
import sys
import httpx

sys.path.append(".")
from app.connectors.greenhouse_connector import GREENHOUSE_BOARD_TOKENS
from app.connectors.lever_connector import LEVER_COMPANY_SLUGS

async def check_greenhouse():
    print("=== Checking Greenhouse Board Tokens ===")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    active = []
    inactive = []
    
    async def check_token(client, token):
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
        try:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code == 200:
                jobs = resp.json().get("jobs", [])
                active.append((token, len(jobs)))
            else:
                inactive.append((token, resp.status_code))
        except Exception as e:
            inactive.append((token, str(e)))

    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    async with httpx.AsyncClient(headers=headers, limits=limits, follow_redirects=True) as client:
        await asyncio.gather(*(check_token(client, token) for token in GREENHOUSE_BOARD_TOKENS))
        
    print(f"\nActive Greenhouse Boards ({len(active)}):")
    for token, count in sorted(active):
        print(f"  {token}: {count} raw jobs")
        
    print(f"\nInactive/404 Greenhouse Boards ({len(inactive)}):")
    for token, status in sorted(inactive):
        print(f"  {token}: {status}")

async def check_lever():
    print("\n=== Checking Lever Company Slugs ===")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    active = []
    inactive = []
    
    async def check_slug(client, slug):
        url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
        try:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code == 200:
                jobs = resp.json()
                active.append((slug, len(jobs)))
            else:
                inactive.append((slug, resp.status_code))
        except Exception as e:
            inactive.append((slug, str(e)))

    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    async with httpx.AsyncClient(headers=headers, limits=limits, follow_redirects=True) as client:
        await asyncio.gather(*(check_slug(client, slug) for slug in LEVER_COMPANY_SLUGS))
        
    print(f"\nActive Lever Slugs ({len(active)}):")
    for slug, count in sorted(active):
        print(f"  {slug}: {count} raw jobs")
        
    print(f"\nInactive/404 Lever Slugs ({len(inactive)}):")
    for slug, status in sorted(inactive):
        print(f"  {slug}: {status}")

if __name__ == "__main__":
    asyncio.run(check_greenhouse())
    asyncio.run(check_lever())
