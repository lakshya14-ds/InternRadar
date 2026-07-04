import asyncio
import httpx
from bs4 import BeautifulSoup

async def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = "https://joinhandshake.com/sitemap-0.xml"
    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=10.0) as client:
            res = await client.get(url)
            print(f"Status: {res.status_code}, Length: {len(res.text)}")
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                locs = [loc.text for loc in soup.find_all("loc")]
                print(f"Found {len(locs)} links.")
                print("First 30 links:")
                for loc in locs[:30]:
                    print(loc)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
