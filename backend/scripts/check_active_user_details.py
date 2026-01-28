import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_user_details(user_id):
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT id, email, role, status, position FROM auth.users WHERE id = %s;", (user_id,))
    user = cur.fetchone()
    if user:
        print(f"User: ID={user[0]}, Email={user[1]}, Role={user[2]}, Status={user[3]}, Position={user[4]}")
    else:
        print("User not found.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_user_details("ed168844-788a-4803-a9b3-d0f638b16875")
