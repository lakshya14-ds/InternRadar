import asyncio
import httpx

async def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = "https://api.lever.co/v0/postings/cred?mode=json"
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        resp = await client.get(url)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Jobs returned: {len(resp.json())}")
            print("Sample job name:", resp.json()[0].get("text"))
        else:
            print(resp.text[:500])

if __name__ == "__main__":
    asyncio.run(main())
