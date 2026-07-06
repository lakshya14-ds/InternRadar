import asyncio
import sys
import httpx
sys.path.append(".")

async def main():
    url = "https://wipro.wd3.myworkdayjobs.com/en-US/WiproJobs"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            print("Status Code:", response.status_code)
            print("Final URL:", response.url)
            # print first 500 chars of response.text
            print("Text snippet:", response.text[:500])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
