import asyncio
import sys
import httpx

sys.path.append(".")
from app.connectors.greenhouse_connector import GreenhouseConnector
from app.connectors.lever_connector import LeverConnector

async def check_greenhouse():
    print("=== Greenhouse Check ===")
    connector = GreenhouseConnector()
    companies = await connector.discover_companies()
    
    # Let's check a few known Indian companies
    target_tokens = ["razorpay", "zepto", "groww", "cred", "postman"]
    targets = [c for c in companies if c["board_token"] in target_tokens]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        for t in targets:
            token = t["board_token"]
            url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
            try:
                resp = await client.get(url, params={"content": "true"}, timeout=10.0)
                if resp.status_code == 200:
                    jobs = resp.json().get("jobs", [])
                    print(f"Company: {token} -> Total raw jobs: {len(jobs)}")
                    for j in jobs:
                        title = j.get("title", "")
                        loc_name = (j.get("location") or {}).get("name", "")
                        desc = j.get("content", "")
                        
                        is_intern = connector.is_internship(title, desc)
                        is_india = connector.is_india_location(loc_name)
                        
                        if "intern" in title.lower() or "trainee" in title.lower():
                            print(f"  [Found Internship Title]: '{title}'")
                            print(f"    Location: '{loc_name}' (is_india: {is_india})")
                            print(f"    is_internship gate: {is_intern}")
                else:
                    print(f"Company: {token} -> HTTP Status {resp.status_code}")
            except Exception as e:
                print(f"Company: {token} -> Error: {e}")

async def check_lever():
    print("\n=== Lever Check ===")
    connector = LeverConnector()
    companies = await connector.discover_companies()
    
    target_slugs = ["swiggy", "phonepe", "paytm", "juspay"]
    targets = [c for c in companies if c["slug"] in target_slugs]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        for t in targets:
            slug = t["slug"]
            url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
            try:
                resp = await client.get(url, timeout=10.0)
                if resp.status_code == 200:
                    jobs = resp.json()
                    print(f"Company: {slug} -> Total raw jobs: {len(jobs)}")
                    for j in jobs:
                        title = j.get("text", "")
                        loc = j.get("categories", {}).get("location", "")
                        desc = j.get("descriptionPlain", "") or j.get("description", "")
                        
                        is_intern = connector.is_internship(title, desc)
                        is_india = connector.is_india_location(loc)
                        
                        if "intern" in title.lower() or "trainee" in title.lower():
                            print(f"  [Found Internship Title]: '{title}'")
                            print(f"    Location: '{loc}' (is_india: {is_india})")
                            print(f"    is_internship gate: {is_intern}")
                else:
                    print(f"Company: {slug} -> HTTP Status {resp.status_code}")
            except Exception as e:
                print(f"Company: {slug} -> Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_greenhouse())
    asyncio.run(check_lever())
