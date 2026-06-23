import httpx
import asyncio

async def main():
    url = "https://wipro.wd3.myworkdayjobs.com/wday/cxs/wipro/WiproJobs/jobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://wipro.wd3.myworkdayjobs.com",
        "Referer": "https://wipro.wd3.myworkdayjobs.com/en-US/WiproJobs"
    }
    payload = {
        "appliedFacets": {},
        "limit": 20,
        "offset": 0,
        "searchText": ""
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            resp = await client.post(url, json=payload)
            print(f"Status code: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"Total job postings: {data.get('total')}")
                postings = data.get("jobPostings", [])
                print(f"Returned job count: {len(postings)}")
            else:
                print(f"Response text: {resp.text[:500]}")
        except Exception as e:
            print(f"Failed with: {e}")

if __name__ == "__main__":
    asyncio.run(main())
