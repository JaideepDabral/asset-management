from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
url = os.getenv('DATABASE_URL')
# Convert async url to sync if needed for simple test
if '+asyncpg' in url:
    url = url.replace('+asyncpg', '')

engine = create_engine(url)
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, length(id) FROM asset.assets"))
    for row in result:
        print(f"ID: '{row[0]}', Length: {row[1]}")
