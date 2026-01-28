
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def check_api_requests():
    # User 'end' ID from deep_inspect.py
    requester_id = "c4cc209a-0f40-4a60-9ee3-b8d0566b65d6" 
    
    print(f"Fetching requests for Requester ID: {requester_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/asset-requests", params={"requester_id": requester_id})
        
        if response.status_code == 200:
            data = response.json()
            print(f"Count: {len(data)}")
            if len(data) > 0:
                print(json.dumps(data, indent=2))
            else:
                print("No requests found via API for this ID.")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_api_requests()
