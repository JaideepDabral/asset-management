import requests

URL = "http://127.0.0.1:8000/assets"
HEADERS = {"Origin": "http://localhost:3000"}

try:
    r = requests.get(URL, headers=HEADERS, timeout=20)
    print("Status:", r.status_code)
    print("\nHeaders:")
    for k, v in r.headers.items():
        print(f"{k}: {v}")
    print("\nBody:\n", r.text[:2000])
except Exception as e:
    print("Error:", type(e), e)
