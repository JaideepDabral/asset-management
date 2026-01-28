
import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_registration_and_login():
    email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    password = "password123"
    
    print(f"1. Attempting to register user: {email}")
    register_payload = {
        "email": email,
        "password": password,
        "full_name": "Test User",
        "role": "ADMIN",  # Directly making it ADMIN
        "status": "ACTIVE" # Directly making it ACTIVE
    }
    
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json=register_payload)
    print(f"Registration status: {reg_resp.status_code}")
    print(f"Registration response: {reg_resp.text}")
    
    if reg_resp.status_code != 200:
        print("Registration failed, stopping.")
        return

    print("\n2. Attempting to login with new user")
    login_payload = {
        "username": email,
        "password": password
    }
    
    # login uses form data
    login_resp = requests.post(f"{BASE_URL}/auth/login", data=login_payload)
    print(f"Login status: {login_resp.status_code}")
    print(f"Login response: {login_resp.text}")

if __name__ == "__main__":
    test_registration_and_login()
