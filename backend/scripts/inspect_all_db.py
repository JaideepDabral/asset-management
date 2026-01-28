import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL')
if url and "asyncpg" in url:
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
engine = create_engine(url)
inspector = inspect(engine)

schemas = ['auth', 'asset', 'exit', 'support', 'procurement', 'system']
for schema in schemas:
    print(f"\nSchema: {schema}")
    tables = inspector.get_table_names(schema=schema)
    for table in tables:
        print(f"  Table: {table}")
        columns = inspector.get_columns(table, schema=schema)
        for column in columns:
            print(f"    - {column['name']} ({column['type']})")
