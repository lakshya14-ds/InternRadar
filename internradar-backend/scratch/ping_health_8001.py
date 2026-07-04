import requests

try:
    resp = requests.get("http://localhost:8001/health", timeout=5)
    print("Health 8001 Status:", resp.status_code)
    print("Health 8001 Response:", resp.json())
except Exception as e:
    print("Failed to reach health 8001:", e)
