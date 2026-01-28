import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL')
if url and "asyncpg" in url:
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
engine = create_engine(url)
inspector = inspect(engine)

print("Columns in exit.exit_requests:")
columns = inspector.get_columns('exit_requests', schema='exit')
for column in columns:
    print(f"- {column['name']} ({column['type']})")
