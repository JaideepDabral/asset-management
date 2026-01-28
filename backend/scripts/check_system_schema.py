import os
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL')
if url and "asyncpg" in url:
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
engine = create_engine(url)
inspector = inspect(engine)

schema = 'system'
print(f"Checking schema: {schema}")
tables = inspector.get_table_names(schema=schema)
if tables:
    for table in tables:
        print(f"Table: {table}")
else:
    print(f"No tables found in schema '{schema}'")

# Check if schema exists
with engine.connect() as conn:
    res = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'system'"))
    if res.fetchone():
        print(f"Schema '{schema}' exists in information_schema")
    else:
        print(f"Schema '{schema}' DOES NOT EXIST in information_schema")
