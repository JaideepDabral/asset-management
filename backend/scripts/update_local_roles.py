import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def update_admin_role():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Update SYSTEM_ADMIN to ADMIN for standard slugs
    cur.execute("UPDATE auth.users SET role = 'ADMIN' WHERE role = 'SYSTEM_ADMIN';")
    print(f"Updated {cur.rowcount} users from SYSTEM_ADMIN to ADMIN.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    update_admin_role()
