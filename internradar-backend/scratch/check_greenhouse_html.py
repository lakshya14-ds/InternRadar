import asyncio
import sys
import httpx
from bs4 import BeautifulSoup

async def check_html():
    tokens = ["razorpay", "zepto", "cred", "dunzo", "meesho"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        for token in tokens:
            url = f"https://boards.greenhouse.io/{token}"
            try:
                resp = await client.get(url, timeout=10.0)
                print(f"Token: {token} -> Status: {resp.status_code}")
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    title = soup.title.string if soup.title else "No title"
                    jobs_count = len(soup.select(".opening"))
                    print(f"  Title: {title.strip()}")
                    print(f"  Job openings count in HTML: {jobs_count}")
            except Exception as e:
                print(f"Token: {token} -> Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_html())
