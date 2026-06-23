import httpx
import asyncio

async def main():
    url_base = "https://infosys.wd3.myworkdayjobs.com/en-US/Infosys"
    url_api = "https://infosys.wd3.myworkdayjobs.com/wday/cxs/infosys/Infosys/jobs"
    get_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    post_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US",
        "Content-Type": "application/json",
        "Origin": "https://wipro.wd3.myworkdayjobs.com",
        "Referer": "https://wipro.wd3.myworkdayjobs.com/en-US/WiproJobs"
    }
    payload = {
        "appliedFacets": {},
        "limit": 20,
        "offset": 0,
        "searchText": ""
    }
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            # 1. GET base page to establish session/cookies
            print("Getting base page...")
            resp_base = await client.get(url_base, headers=get_headers)
            print(f"Base page status: {resp_base.status_code}")
            print(f"Base page text: {resp_base.text[:1000]}")
            print(f"Cookies: {client.cookies}")
            
            # 2. POST to API
            print("Posting to API...")
            resp = await client.post(url_api, json=payload, headers=post_headers)
            print(f"API status code: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Success! Total jobs: {resp.json().get('total')}")
                postings = resp.json().get("jobPostings", [])
                if postings:
                    print(f"Sample externalPath: {postings[0].get('externalPath')}")
            else:
                print(f"Response: {resp.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
