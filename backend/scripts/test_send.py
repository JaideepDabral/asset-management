import requests
import json

url = "http://localhost:8000/api/v1/collect"
token = "D012tQJn8MQXfggfHbNcOE-l8tFtnHAGiGMFjYPC45SCssMbZKx2zP9vcHddhkW6"

with open("clean_log_details.json", "r", encoding="utf-8") as f:
    data = json.load(f)

headers = {
    "X-API-Token": token,
    "Content-Type": "application/json"
}

response = requests.post(url, json=data, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
