import requests

BASE_URL = "http://localhost:8000"

def test_flow():
    # 1. Register a test user
    email = "testuser_unique_123@example.com"
    password = "testpassword123"
    name = "Test User"
    
    register_payload = {
        "email": email,
        "password": password,
        "name": name,
        "preferences": {
            "preferred_categories": [],
            "preferred_locations": [],
            "preferred_companies": [],
            "remote_only": False,
            "email_alerts_enabled": True
        }
    }
    
    print("Trying to register...")
    reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json=register_payload)
    print("Register Status:", reg_resp.status_code)
    print("Register Response:", reg_resp.text)
    
    # If already registered, try logging in
    if reg_resp.status_code in (201, 200):
        data = reg_resp.json()
        token = data["access_token"]
    else:
        print("Register failed, trying to login...")
        login_payload = {
            "email": email,
            "password": password
        }
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload)
        print("Login Status:", login_resp.status_code)
        print("Login Response:", login_resp.text)
        if login_resp.status_code == 200:
            token = login_resp.json()["access_token"]
        else:
            print("Login failed too.")
            return

    # 2. Get profile
    print("\nQuerying /api/users/me with token...")
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = requests.get(f"{BASE_URL}/api/users/me", headers=headers)
    print("Me Status:", me_resp.status_code)
    print("Me Response:", me_resp.text)

if __name__ == "__main__":
    test_flow()
