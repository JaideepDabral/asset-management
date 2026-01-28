import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_special_users():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT email, password_hash, status, role FROM auth.users;")
    rows = cur.fetchall()
    print("Email | Status | Role | Hashed | Password")
    print("-" * 80)
    for row in rows:
        email, pwd, status, role = row
        is_hashed = pwd.startswith('$2') if pwd else False
        pwd_display = pwd if not is_hashed else f"{pwd[:10]}..."
        print(f"{email} | {status} | {role} | {is_hashed} | {pwd_display}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_special_users()
