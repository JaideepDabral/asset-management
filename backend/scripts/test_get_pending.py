import requests
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_get_users():
    # Find Admin ID
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT id FROM auth.users WHERE email = 'admin@itsm.com';")
    admin_id = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    print(f"Testing with Admin ID: {admin_id}")
    
    url = f"http://127.0.0.1:8000/auth/users?status=PENDING&admin_user_id={admin_id}"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_get_users()
