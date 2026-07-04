import asyncio
import httpx

async def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        # Test HTML page
        url = "https://boards.greenhouse.io/phonepe"
        resp = await client.get(url)
        print(f"HTML URL: {url}")
        print(f"  Status: {resp.status_code}")
        print(f"  Final URL: {resp.url}")
        print(f"  History: {resp.history}")
        print(f"  Body length: {len(resp.text)}")
        print(f"  Body snippet: {resp.text[:500]}")
        
        # Test API page
        api_url = "https://boards-api.greenhouse.io/v1/boards/phonepe/jobs"
        api_resp = await client.get(api_url)
        print(f"\nAPI URL: {api_url}")
        print(f"  Status: {api_resp.status_code}")
        print(f"  Body snippet: {api_resp.text[:500]}")

if __name__ == "__main__":
    asyncio.run(main())
