import asyncio
import sys
import httpx

# Master list of unique company base identifiers
COMPANIES = [
    # A-Z
    "razorpay", "zepto", "meesho", "mpl", "groww", "slice", "cred", "bharatpe", 
    "smallcase", "yellowmessenger", "unacademy", "vedantu", "toppr", "byjus", 
    "dunzo", "milkbasket", "purplle", "licious", "udaan", "moglix", "cashfree", 
    "setu", "leadsquared", "darwinbox", "freshworks", "zoho", "chargebee", 
    "postman", "browserstack", "clevertap", "moengage", "webengage", "stripe", 
    "databricks", "airbnb", "walmart", "intuit", "paypal", "uber", "linkedin", 
    "microsoft", "google", "amazon", "oracle", "sap", "swiggy", "zomato", "ola", 
    "phonepe", "paytm", "nykaa", "mamaearth", "boat-lifestyle", "wakefit", 
    "nobroker", "housing", "magicbricks", "99acres", "sharechat", "moj", "inshorts", 
    "dailyhunt", "vernacular-ai", "sarvam-ai", "krutrim", "scaler", "interviewbit", 
    "springworks", "juspay", "epifi", "niyo", "jupiter", "freo", "stashfin", 
    "ixigo", "ola-electric", "pure-ev", "ather-energy", "revolt-motors", "netlify", 
    "scaleai", "ramp", "notion", "airtable", "figma", "rapido", "porter", "locofast", 
    "lenskart", "simpl", "wint-wealth", "stoa", "decentro", "hyperface", "hyperverge", 
    "pixxel", "agnikul", "skyroot", "ati-motors", "uniphore", "senseforth", "sarvam", 
    "eka-care", "mfine", "innovaccer", "niramai", "perfios", "signzy", "bureau", 
    "indifi", "credavenue", "recur-club", "klub", "elevation-capital", "stellaris", 
    "blume-ventures", "prime-venture", "openai", "cursor", "linear", "retool", 
    "vercel", "supabase", "tataconsultancyservices", "tatacommunications", "tataelxsi", 
    "bajaj-finserv", "hdfc-bank", "icicibank", "kotakmahindrabank", "axisbank", 
    "indusindbank", "relianceindustries", "reljio", "relianceretail", "mahindra", 
    "maruti-suzuki", "hero-motocorp", "dreamsports", "games24x7", "nazara-technologies", 
    "newgen-software", "minda-industries", "siemens", "bosch", "schneider-electric", 
    "honeywell", "3m", "philips"
]

# We will try standard slug variations
def get_variations(base):
    res = [base]
    # slug formats
    res.append(base.lower())
    res.append(base.capitalize())
    res.append(base.replace("-", ""))
    
    # common suffixes
    res.append(f"{base}softwareprivatelimited")
    res.append(f"{base}group")
    res.append(f"{base}india")
    res.append(f"{base}careers")
    
    # Remove duplicates while keeping order
    seen = set()
    return [x for x in res if not (x in seen or seen.add(x))]

async def scan():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    active_greenhouse = []
    active_lever = []
    active_ashby = []
    active_smartrecruiters = []
    
    semaphore = asyncio.Semaphore(20) # max concurrent requests
    
    async def check_gh(client, token):
        async with semaphore:
            url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
            try:
                resp = await client.get(url, timeout=5.0)
                if resp.status_code == 200:
                    jobs = resp.json().get("jobs", [])
                    active_greenhouse.append((token, len(jobs)))
            except Exception:
                pass

    async def check_lever(client, slug):
        async with semaphore:
            url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
            try:
                resp = await client.get(url, timeout=5.0)
                if resp.status_code == 200:
                    jobs = resp.json()
                    active_lever.append((slug, len(jobs)))
            except Exception:
                pass

    async def check_ashby(client, slug):
        async with semaphore:
            url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
            try:
                resp = await client.get(url, timeout=5.0)
                if resp.status_code == 200:
                    jobs = resp.json().get("jobs", [])
                    active_ashby.append((slug, len(jobs)))
            except Exception:
                pass

    async def check_sr(client, slug):
        async with semaphore:
            url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"
            try:
                resp = await client.get(url, timeout=5.0)
                if resp.status_code == 200:
                    jobs = resp.json().get("content", [])
                    active_smartrecruiters.append((slug, len(jobs)))
            except Exception:
                pass

    limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
    async with httpx.AsyncClient(headers=headers, limits=limits, follow_redirects=True) as client:
        tasks = []
        for base in COMPANIES:
            for var in get_variations(base):
                tasks.append(check_gh(client, var))
                tasks.append(check_lever(client, var))
                tasks.append(check_ashby(client, var))
                tasks.append(check_sr(client, var))
                
        print(f"Scanning {len(tasks)} combinations...")
        await asyncio.gather(*tasks)
        
    print("\n--- ACTIVE GREENHOUSE BOARDS ---")
    for token, count in sorted(active_greenhouse):
        print(f"  {token}: {count} jobs")
        
    print("\n--- ACTIVE LEVER SLUGS ---")
    for slug, count in sorted(active_lever):
        print(f"  {slug}: {count} jobs")
        
    print("\n--- ACTIVE ASHBY SLUGS ---")
    for slug, count in sorted(active_ashby):
        print(f"  {slug}: {count} jobs")
        
    print("\n--- ACTIVE SMARTRECRUITERS SLUGS ---")
    for slug, count in sorted(active_smartrecruiters):
        print(f"  {slug}: {count} jobs")

if __name__ == "__main__":
    asyncio.run(scan())
