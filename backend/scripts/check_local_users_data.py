import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_users_data():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT email, status, role, phone FROM auth.users LIMIT 5;")
    rows = cur.fetchall()
    print("Sample user data:")
    for row in rows:
        print(f"Email: {row[0]}, Status: {row[1]}, Role: {row[2]}, Phone: {row[3]}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_users_data()
