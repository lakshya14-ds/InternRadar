import asyncio
import httpx

async def main():
    url = "https://www.workatastartup.com/jobs/L4QRVHl"
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
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
