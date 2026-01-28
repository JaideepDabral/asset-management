
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_assign():
    asset_id = "AST-736"
    url = f"{BASE_URL}/assets/{asset_id}/assign"
    
    payload = {
        "assigned_to": "Test User",
        "assigned_to_id": "test-uuid-123",
        "location": "Home Office"
    }
    
    print(f"PATCHing {url} with {payload}...")
    try:
        response = requests.patch(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_assign()
