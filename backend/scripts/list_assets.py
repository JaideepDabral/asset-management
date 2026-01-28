from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
url = os.getenv('DATABASE_URL')
if '+asyncpg' in url:
    url = url.replace('+asyncpg', '')

engine = create_engine(url)
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name, type, status FROM asset.assets ORDER BY created_at DESC LIMIT 20"))
    print("\n=== Available Assets in Database ===\n")
    print(f"{'ID':<40} {'Name':<30} {'Type':<15} {'Status':<15}")
    print("-" * 100)
    for row in result:
        print(f"{row[0]:<40} {row[1]:<30} {row[2]:<15} {row[3]:<15}")
    print("\n")
