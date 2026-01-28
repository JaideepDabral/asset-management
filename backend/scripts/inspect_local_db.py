import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def inspect_local_users():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'auth' AND table_name = 'users'
        ORDER BY ordinal_position;
    """)
    cols = cur.fetchall()
    print("Full column list for auth.users:")
    for col in cols:
        print(f"{col[0]} ({col[1]})")
    cur.close()
    conn.close()

if __name__ == "__main__":
    inspect_local_users()
