import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def inspect_table():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = 'asset' AND table_name = 'asset_requests'
        ORDER BY ordinal_position;
    """)
    cols = cur.fetchall()
    print(f"Full inspection of asset.asset_requests:")
    for col in cols:
        print(f"Column: {col[0]}")
        print(f"  Type: {col[1]}")
        print(f"  Nullable: {col[2]}")
        print(f"  Default: {col[3]}")
        print("-" * 20)
    cur.close()
    conn.close()

if __name__ == "__main__":
    inspect_table()
