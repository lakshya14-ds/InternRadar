import asyncio
import sys
import httpx

sys.path.append(".")
from app.connectors.base_connector import BaseConnector

class Tester(BaseConnector):
    source = "tester"
    async def fetch_jobs(self, companies): return []
    def normalize(self, raw_jobs): return []

tester = Tester()

async def check_greenhouse_active():
    active_tokens = ["airbnb", "databricks", "groww", "linkedin", "postman", "slice", "stripe"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    total_raw = 0
    total_valid = 0
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        for token in active_tokens:
            url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
            try:
                resp = await client.get(url, timeout=15.0)
                if resp.status_code == 200:
                    jobs = resp.json().get("jobs", [])
                    total_raw += len(jobs)
                    company_valid = 0
                    for j in jobs:
                        title = j.get("title", "")
                        desc = j.get("content", "")
                        loc = (j.get("location") or {}).get("name", "")
                        
                        is_intern = tester.is_internship(title, desc)
                        is_india = tester.is_india_location(loc)
                        
                        if is_intern and is_india:
                            company_valid += 1
                            total_valid += 1
                    print(f"Greenhouse: {token} -> {len(jobs)} raw jobs, {company_valid} valid India internships")
                else:
                    print(f"Greenhouse: {token} -> HTTP Status {resp.status_code}")
            except Exception as e:
                print(f"Greenhouse: {token} -> Error: {e}")
                
    print(f"Total Greenhouse: {total_raw} raw, {total_valid} valid")

async def check_lever_active():
    active_slugs = ["epifi", "paytm"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    total_raw = 0
    total_valid = 0
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        for slug in active_slugs:
            url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
            try:
                resp = await client.get(url, timeout=15.0)
                if resp.status_code == 200:
                    jobs = resp.json()
                    total_raw += len(jobs)
                    company_valid = 0
                    for j in jobs:
                        title = j.get("text", "")
                        desc = j.get("descriptionPlain", "") or j.get("description", "")
                        loc = j.get("categories", {}).get("location", "")
                        
                        is_intern = tester.is_internship(title, desc)
                        is_india = tester.is_india_location(loc)
                        
                        if is_intern and is_india:
                            company_valid += 1
                            total_valid += 1
                    print(f"Lever: {slug} -> {len(jobs)} raw jobs, {company_valid} valid India internships")
                else:
                    print(f"Lever: {slug} -> HTTP Status {resp.status_code}")
            except Exception as e:
                print(f"Lever: {slug} -> Error: {e}")
                
    print(f"Total Lever: {total_raw} raw, {total_valid} valid")

async def check_ashby_active():
    active_slugs = ["bureau", "cursor", "linear", "openai", "sarvam", "supabase", "vercel"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    total_raw = 0
    total_valid = 0
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        for slug in active_slugs:
            url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
            try:
                resp = await client.get(url, timeout=15.0)
                if resp.status_code == 200:
                    jobs = resp.json().get("jobs", [])
                    total_raw += len(jobs)
                    company_valid = 0
                    for j in jobs:
                        title = j.get("title", "")
                        desc = j.get("descriptionPlain", "") or j.get("descriptionHtml", "")
                        loc = j.get("location", "")
                        
                        is_intern = tester.is_internship(title, desc)
                        is_india = tester.is_india_location(loc)
                        
                        if is_intern and is_india:
                            company_valid += 1
                            total_valid += 1
                    print(f"Ashby: {slug} -> {len(jobs)} raw jobs, {company_valid} valid India internships")
                else:
                    print(f"Ashby: {slug} -> HTTP Status {resp.status_code}")
            except Exception as e:
                print(f"Ashby: {slug} -> Error: {e}")
                
    print(f"Total Ashby: {total_raw} raw, {total_valid} valid")

if __name__ == "__main__":
    asyncio.run(check_greenhouse_active())
    asyncio.run(check_lever_active())
    asyncio.run(check_ashby_active())
