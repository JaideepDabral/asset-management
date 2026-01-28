import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_column_defaults():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, column_default, is_nullable 
        FROM information_schema.columns 
        WHERE table_schema = 'asset' AND table_name = 'asset_requests';
    """)
    cols = cur.fetchall()
    print("Column defaults for asset.asset_requests:")
    for col in cols:
        print(f"- {col[0]}: default={col[1]}, nullable={col[2]}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_column_defaults()
