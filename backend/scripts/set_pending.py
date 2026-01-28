import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def set_pending():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("UPDATE auth.users SET status = 'PENDING' WHERE email = 'end@gmail.com';")
    print(f"Updated {cur.rowcount} rows.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    set_pending()
