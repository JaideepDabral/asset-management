"""
Test script to verify FastAPI server is running and endpoints are working
"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_server_health():
    """Test if server is running"""
    print("=" * 60)
    print("TESTING FASTAPI SERVER")
    print("=" * 60)
    
    # Wait a bit for server to start
    print("\nWaiting for server to start...")
    time.sleep(3)
    
    try:
        # Test root endpoint
        print("\n1. Testing root endpoint...")
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Root endpoint working")
        else:
            print(f"   ✗ Unexpected status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ✗ Server not running or not accessible")
        print("   Make sure uvicorn is running: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    try:
        # Test docs endpoint
        print("\n2. Testing API documentation endpoint...")
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ API docs accessible")
        else:
            print(f"   ⚠ Docs returned status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠ Docs check failed: {e}")
    
    try:
        # Test openapi.json
        print("\n3. Testing OpenAPI schema...")
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ OpenAPI schema loaded")
            print(f"   - Title: {data.get('info', {}).get('title', 'N/A')}")
            print(f"   - Version: {data.get('info', {}).get('version', 'N/A')}")
            print(f"   - Paths: {len(data.get('paths', {}))} endpoints")
        else:
            print(f"   ⚠ OpenAPI returned status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠ OpenAPI check failed: {e}")
    
    # Test key endpoints
    endpoints_to_test = [
        ("GET", "/auth/users", "List users"),
        ("GET", "/assets", "List assets"),
        ("GET", "/asset-requests", "List asset requests"),
        ("GET", "/tickets", "List tickets"),
    ]
    
    print("\n4. Testing key endpoints...")
    for method, path, description in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{path}", timeout=5)
                print(f"   {method} {path}: {response.status_code} - {description}")
                if response.status_code in [200, 401, 403]:
                    print(f"      ✓ Endpoint accessible (status {response.status_code})")
                else:
                    print(f"      ⚠ Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ {method} {path}: Error - {e}")
    
    print("\n" + "=" * 60)
    print("SERVER TEST COMPLETE")
    print("=" * 60)
    print("\n✓ Server is running and responding to requests")
    print(f"✓ API Documentation: {BASE_URL}/docs")
    print(f"✓ Alternative docs: {BASE_URL}/redoc")
    
    return True

if __name__ == "__main__":
    success = test_server_health()
    sys.exit(0 if success else 1)

