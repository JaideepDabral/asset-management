import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    url = f"{BASE_URL}/auth/register"
    payload = {
        "email": "testuser@example.com",
        "password": "testpassword",
        "full_name": "Test User",
        "role": "END_USER",
        "location": "New York",
        "position": "TEAM_MEMBER"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_registration()
