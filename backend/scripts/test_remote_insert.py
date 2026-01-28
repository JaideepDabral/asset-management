
from sqlalchemy import create_engine, text
import uuid

def test_remote_insert():
    url = "postgresql+psycopg2://postgres:1234@192.168.0.83:5432/ITSM"
    engine = create_engine(url)
    email = "final_verification_test@example.com"
    
    print(f"Testing insert to {url}...")
    with engine.connect() as conn:
        # 1. Delete if exists
        conn.execute(text(f"DELETE FROM auth.users WHERE email = '{email}'"))
        conn.commit()
        
        # 2. Insert
        user_id = str(uuid.uuid4())
        insert_query = text("""
            INSERT INTO auth.users (id, email, password_hash, full_name, role, status, created_at, updated_at)
            VALUES (:id, :email, :password_hash, :full_name, :role, :status, NOW(), NOW())
        """)
        conn.execute(insert_query, {
            "id": user_id,
            "email": email,
            "password_hash": "testhash",
            "full_name": "Final Test User",
            "role": "END_USER",
            "status": "ACTIVE"
        })
        conn.commit()
        print(f"Insert Successful with ID: {user_id}")
        
        # 3. Verify
        res = conn.execute(text(f"SELECT id FROM auth.users WHERE email = '{email}'"))
        row = res.fetchone()
        if row:
            print(f"Verification SUCCESS: Found row with ID {row[0]}")
        else:
            print("Verification FAILED: Row not found after insert.")

if __name__ == "__main__":
    test_remote_insert()
