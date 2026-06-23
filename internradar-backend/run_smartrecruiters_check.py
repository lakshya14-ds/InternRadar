import httpx
import asyncio

async def main():
    url = "https://api.smartrecruiters.com/v1/companies/ICICIBank/postings"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            resp = await client.get(url)
            print(f"Status code: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"Full response: {data}")
                content = data.get("content", [])
                print(f"Returned postings count: {len(content)}")
                if content:
                    print("Sample posting keys:", content[0].keys())
                    print("Sample posting values of interest:")
                    print("  id:", content[0].get("id"))
                    print("  name:", content[0].get("name"))
                    print("  ref:", content[0].get("ref"))
                    # check for other URL/link fields in the posting
                    for k, v in content[0].items():
                        if isinstance(v, str) and v.startswith("http"):
                            print(f"  {k}: {v}")
                        elif isinstance(v, dict):
                            for subk, subv in v.items():
                                if isinstance(subv, str) and subv.startswith("http"):
                                    print(f"  {k}.{subk}: {subv}")
            else:
                print(f"Response text: {resp.text[:500]}")
        except Exception as e:
            print(f"Failed with: {e}")

if __name__ == "__main__":
    asyncio.run(main())
