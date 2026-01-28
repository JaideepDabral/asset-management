import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def find_active_end_user():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT id, email FROM auth.users WHERE role = 'END_USER' AND status = 'ACTIVE' LIMIT 1;")
    user = cur.fetchone()
    if user:
        print(f"Active End User: ID={user[0]}, Email={user[1]}")
    else:
        print("No active end user found.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    find_active_end_user()
