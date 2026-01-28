
import requests
import json

url = "http://localhost:8000/api/v1/collect"
token = "D012tQJn8MQXfggfHbNcOE-l8tFtnHAGiGMFjYPC45SCssMbZKx2zP9vcHddhkW6"
headers = {
    "X-API-Token": token,
    "Content-Type": "application/json"
}

payload = {
    "serial_number": "VMware-56 4d 3d f7 16 0d 22 51-1b 84 83 20 89 2b 43 14",
    "hostname": "test-vm",
    "hardware": {
        "manufacturer": "VMware, Inc.",
        "model": "VMware Virtual Platform"
    }
}

print(f"Sending payload to {url}...")
try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
