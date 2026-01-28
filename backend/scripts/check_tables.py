import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()
url = os.getenv('DATABASE_URL')
if url and "asyncpg" in url:
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
engine = create_engine(url)
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema IN ('auth', 'asset', 'public', 'exit', 'support', 'procurement', 'system') AND table_type = 'BASE TABLE'"))
        print('Tables in database:')
        for row in result:
            print(f"- {row[0]}.{row[1]}")
except Exception as e:
    print('Error:', e)
