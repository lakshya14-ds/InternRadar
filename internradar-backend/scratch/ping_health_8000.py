import requests

try:
    resp = requests.get("http://localhost:8000/health", timeout=5)
    print("Health 8000 Status:", resp.status_code)
    print("Health 8000 Response:", resp.json())
except Exception as e:
    print("Failed to reach health 8000:", e)
