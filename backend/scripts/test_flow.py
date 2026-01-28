import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def register_pending_user():
    email = f"user_{int(time.time())}@example.com"
    payload = {
        "email": email,
        "password": "password123",
        "full_name": "New Pending User",
        "role": "END_USER",
        "location": "Remote",
        "position": "TEAM_MEMBER",
        "phone": "0000000000"
    }
    
    print(f"Registering user: {email}...")
    r = requests.post(f"{BASE_URL}/auth/register", json=payload)
    if r.status_code == 200:
        print("Registration successful.")
        user_info = r.json()
        print(f"User Status: {user_info.get('status')}")
        
        # Now check if it appears in pending users
        # For this we need an admin ID
        # Let's find admin ID first
        r_admin = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin@itsm.com", "password": "adminpassword123"})
        if r_admin.status_code == 200:
            admin_id = r_admin.json()['user']['id']
            print(f"Admin ID: {admin_id}")
            
            r_users = requests.get(f"{BASE_URL}/auth/users?status=PENDING&admin_user_id={admin_id}")
            if r_users.status_code == 200:
                pending_users = r_users.json()
                print(f"Pending Users Count: {len(pending_users)}")
                if any(u['email'] == email for u in pending_users):
                    print("SUCCESS: New user is in the pending list.")
                else:
                    print("FAILURE: New user NOT in the pending list.")
            else:
                print(f"Failed to fetch pending users: {r_users.text}")
        else:
            print(f"Admin login failed: {r_admin.text}")
    else:
        print(f"Registration failed: {r.text}")

if __name__ == "__main__":
    register_pending_user()
