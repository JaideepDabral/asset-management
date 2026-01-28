import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def migrate_local_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST'),
            port=os.getenv('DATABASE_PORT'),
            database=os.getenv('DATABASE_NAME'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD')
        )
        conn.autocommit = True
        cur = conn.cursor()

        print("Checking/Adding columns to auth.users...")
        
        columns_to_add = [
            ("status", "VARCHAR(50) DEFAULT 'PENDING'"),
            ("position", "VARCHAR(50)"),
            ("domain", "VARCHAR(50)"),
            ("department", "VARCHAR(100)"),
            ("location", "VARCHAR(100)"),
            ("phone", "VARCHAR(20)")
        ]

        for col_name, col_def in columns_to_add:
            try:
                cur.execute(f"ALTER TABLE auth.users ADD COLUMN IF NOT EXISTS {col_name} {col_def};")
                print(f"Column '{col_name}' checked/added.")
            except Exception as e:
                print(f"Error adding column '{col_name}': {e}")

        # Also ensure status defaults to PENDING for existing rows if null
        cur.execute("UPDATE auth.users SET status = 'PENDING' WHERE status IS NULL;")
        
        print("\nMigration completed successfully!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_local_db()
