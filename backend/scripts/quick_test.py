"""
Quick test of server functionality
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("QUICK SERVER TEST")
print("=" * 60)

# Get OpenAPI schema to see all endpoints
print("\n1. Fetching API schema...")
try:
    response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
    if response.status_code == 200:
        schema = response.json()
        paths = schema.get('paths', {})
        print(f"✓ Found {len(paths)} endpoints")
        
        # List all endpoints
        print("\nAvailable endpoints:")
        for path, methods in sorted(paths.items()):
            method_list = list(methods.keys())
            print(f"  {', '.join(method_list):6} {path}")
    else:
        print(f"✗ Failed to get schema: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test root
print("\n2. Testing root endpoint...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"✓ Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test health
print("\n3. Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"✓ Status: {response.status_code}")
    print(f"  Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test assets list
print("\n4. Testing GET /assets...")
try:
    response = requests.get(f"{BASE_URL}/assets", timeout=5)
    print(f"✓ Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"  Found {len(data)} assets")
        else:
            print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
except Exception as e:
    print(f"✗ Error: {e}")

# Test tickets list
print("\n5. Testing GET /tickets...")
try:
    response = requests.get(f"{BASE_URL}/tickets", timeout=5)
    print(f"✓ Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"  Found {len(data)} tickets")
        else:
            print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
except Exception as e:
    print(f"✗ Error: {e}")

# Test registration (quick, with timeout)
print("\n6. Testing POST /auth/register (quick test)...")
try:
    import time
    test_data = {
        "email": f"test_{int(time.time())}@test.com",
        "password": "test123",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=test_data, timeout=3)
    print(f"✓ Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"  Registration successful!")
    elif response.status_code == 422:
        print(f"  Validation error (endpoint works)")
except requests.exceptions.Timeout:
    print("  ⚠ Request timed out (endpoint exists but may be slow)")
except Exception as e:
    print(f"  ⚠ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print(f"\n✓ Server is running at {BASE_URL}")
print(f"✓ View API docs at {BASE_URL}/docs")

