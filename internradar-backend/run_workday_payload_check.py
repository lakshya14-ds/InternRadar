import httpx
import asyncio

async def test_payload(payload):
    url = "https://infosys.wd3.myworkdayjobs.com/wday/cxs/infosys/Infosys/jobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            resp = await client.post(url, json=payload)
            print(f"Payload: {payload}")
            print(f"  Status code: {resp.status_code}")
            if resp.status_code == 200:
                print(f"  Total postings: {resp.json().get('total')}")
                return True
            else:
                print(f"  Response text: {resp.text[:200]}")
        except Exception as e:
            print(f"  Failed with: {e}")
    return False

async def main():
    # Test different payload variants
    payloads = [
        # Variant 1: standard
        {
            "appliedFacets": {},
            "limit": 20,
            "offset": 0,
            "searchText": ""
        },
        # Variant 2: no searchText
        {
            "appliedFacets": {},
            "limit": 20,
            "offset": 0
        },
        # Variant 3: empty payload
        {}
    ]
    for p in payloads:
        success = await test_payload(p)
        if success:
            break

if __name__ == "__main__":
    asyncio.run(main())
