import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_status_exact():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT email, status FROM auth.users WHERE email = 'end@gmail.com';")
    row = cur.fetchone()
    if row:
        print(f"Email: '{row[0]}', Status: '{row[1]}'")
    else:
        print("User not found.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_status_exact()
