import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_assign():
    asset_id = "AST-736"
    url = f"{BASE_URL}/assets/{asset_id}/assign"
    payload = {
        "assigned_to": "Test User",
        "location": "Remote"
    }
    response = requests.patch(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_assign()
