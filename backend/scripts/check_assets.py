import requests
import json

try:
    response = requests.get("http://127.0.0.1:8000/assets/")
    assets = response.json()
    print(f"Total assets: {len(assets)}")
    if assets:
        print("First asset sample:")
        print(json.dumps(assets[0], indent=2))
        
        # Check for missing statuses
        missing_status = [a['id'] for a in assets if not a.get('status')]
        if missing_status:
            print(f"Assets missing status: {len(missing_status)}")
        else:
            print("All assets have a status field.")
except Exception as e:
    print(f"Error: {e}")
