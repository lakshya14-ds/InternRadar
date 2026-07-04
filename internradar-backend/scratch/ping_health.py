import requests

try:
    resp = requests.get("http://localhost:8000/health", timeout=5)
    print("Health Status:", resp.status_code)
    print("Health Response:", resp.json())
except Exception as e:
    print("Failed to reach health endpoint:", e)
