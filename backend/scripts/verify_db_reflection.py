import requests
import json
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

def test_registration_and_verify():
    email = "domain_test@example.com"
    url = f"{BASE_URL}/auth/register"
    payload = {
        "email": email,
        "password": "testpassword",
        "full_name": "Domain Test User",
        "role": "END_USER",
        "location": "Cloud Office",
        "position": "MANAGER",
        "domain": "cloud"
    }
    
    print(f"Registering user: {email}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\nVerifying in database...")
            conn = psycopg2.connect(
                host=os.getenv('DATABASE_HOST'),
                port=os.getenv('DATABASE_PORT'),
                database=os.getenv('DATABASE_NAME'),
                user=os.getenv('DATABASE_USER'),
                password=os.getenv('DATABASE_PASSWORD')
            )
            cur = conn.cursor()
            cur.execute("SELECT email, position, domain, status FROM auth.users WHERE email = %s", (email,))
            user = cur.fetchone()
            if user:
                print(f"User found in DB:")
                print(f"  Email: {user[0]}")
                print(f"  Position: {user[1]}")
                print(f"  Domain: {user[2]}")
                print(f"  Status: {user[3]}")
                
                if user[1] == "MANAGER" and user[2] == "cloud":
                    print("\nSUCCESS: All details reflected in database.")
                else:
                    print("\nFAILURE: Details do not match.")
            else:
                print("\nFAILURE: User not found in database.")
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_registration_and_verify()
