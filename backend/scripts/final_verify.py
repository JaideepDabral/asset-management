
import requests
import random
import string
import time

# Use the remote IP explicitly in the test just to be sure we are testing the right thing
# But the uvicorn is on localhost:8000
BASE_URL = "http://localhost:8000"

def get_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def run_final_test():
    print(f"=== FINAL INTEGRATION TEST (Backend: {BASE_URL}) ===")
    
    email = f"verified_signup_{get_random_string()}@example.com"
    reg_payload = {
        "email": email,
        "password": "password123",
        "full_name": "Verified Integration User",
        "department": "IT"
    }
    
    print(f"1. Registering: {email}")
    try:
        r_reg = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
        if r_reg.status_code == 200:
            print("SUCCESS: Registration 200 OK")
        else:
            print(f"FAILED: Registration {r_reg.status_code} - {r_reg.text}")
            return
            
        print("2. Verifying login (Form Data)...")
        login_data = {"username": email, "password": "password123"}
        r_login = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if r_login.status_code == 200:
            print("SUCCESS: Login 200 OK")
            print("User ID:", r_login.json()["user"]["id"])
            print("Status:", r_login.json()["user"]["status"])
        else:
            print(f"FAILED: Login {r_login.status_code} - {r_login.text}")
            
    except Exception as e:
        print(f"ERROR: Could not connect to backend: {e}")

if __name__ == "__main__":
    run_final_test()
