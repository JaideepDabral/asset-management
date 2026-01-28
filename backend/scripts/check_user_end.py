import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_user_end():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT id, email, status, role FROM auth.users WHERE email = 'end@gmail.com';")
    user = cur.fetchone()
    if user:
        print(f"User found: ID={user[0]}, Email={user[1]}, Status={user[2]}, Role={user[3]}")
    else:
        print("User 'end@gmail.com' not found in database.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_user_end()
