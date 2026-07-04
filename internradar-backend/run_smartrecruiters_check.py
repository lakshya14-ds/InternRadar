import httpx
import asyncio

async def main():
    slugs = [
        "TataConsultancyServices", "TataCommunications", "TataElxsi", "Bajaj-Finserv",
        "HDFC-Bank", "ICICIBank", "KotakMahindraBank", "AxisBank", "IndusIndBank",
        "RelianceIndustries", "RelJio", "RelianceRetail", "Mahindra", "Maruti-Suzuki",
        "Hero-MotoCorp", "DreamSports", "Games24x7", "Nazara-Technologies",
        "Newgen-Software", "Minda-Industries", "Siemens", "Bosch", "Schneider-Electric",
        "Honeywell", "3M", "Philips"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        for slug in slugs:
            url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"
            try:
                resp = await client.get(url, timeout=5.0)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data.get("content", [])
                    if len(content) > 0:
                        print(f"Slug: {slug} -> {len(content)} jobs")
                else:
                    # print(f"Slug: {slug} -> Status {resp.status_code}")
                    pass
            except Exception as e:
                print(f"Slug: {slug} -> Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
