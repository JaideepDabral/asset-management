import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_asset_request_id_type():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'asset' AND table_name = 'asset_requests';")
    cols = cur.fetchall()
    print("Columns in asset.asset_requests:")
    for col in cols:
        print(f"- {col[0]} ({col[1]})")
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_asset_request_id_type()
