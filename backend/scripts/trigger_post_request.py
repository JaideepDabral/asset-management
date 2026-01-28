import requests
import json

def trigger_error():
    url = "http://127.0.0.1:8000/asset-requests"
    payload = {
        "requester_id": "ed168844-788a-4803-a9b3-d0f638b16875",
        "asset_name": "Test Laptop",
        "asset_type": "LAPTOP",
        "asset_ownership_type": "COMPANY_OWNED",
        "justification": "Test justification",
        "business_justification": "Test business justification"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        if response.status_code == 500 and "traceback" in data:
            print("Traceback:")
            print(data["traceback"])
        else:
            print(f"Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_error()
