import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()
url = os.getenv('DATABASE_URL')
if url and "asyncpg" in url:
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
print('DATABASE_URL:', url)
engine = create_engine(url, pool_pre_ping=True)
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version()'))
        print('Connected! PostgreSQL version:', result.fetchone()[0])
except Exception as e:
    print('Connection error:', e)
