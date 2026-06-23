import httpx
import re

async def main():
    url = "https://wipro.wd3.myworkdayjobs.com/en-US/WiproJobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        resp = await client.get(url)
        print(f"Status: {resp.status_code}")
        # Search for any api urls or json scripts
        matches = re.findall(r'"/wday/cxs/[^"]+"', resp.text)
        print(f"wday/cxs matches in HTML: {matches}")
        
        # Search for tenant/client site configurations in javascript
        config_matches = re.findall(r'"clientDesignConfig":\s*({[^}]+})', resp.text)
        print(f"clientDesignConfig matches: {config_matches[:2]}")
        
        # Search for any site/board names in HTML
        site_matches = re.findall(r'"siteId":\s*"([^"]+)"', resp.text)
        print(f"siteId matches: {site_matches}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
