import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_id_type():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT data_type FROM information_schema.columns WHERE table_schema = 'auth' AND table_name = 'users' AND column_name = 'id';")
    print(f"ID type: {cur.fetchone()[0]}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_id_type()
