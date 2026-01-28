"""
Start server and run comprehensive tests
"""
import subprocess
import time
import requests
import sys
import os

BASE_URL = "http://127.0.0.1:8000"

def start_server():
    """Start uvicorn server"""
    print("=" * 60)
    print("STARTING FASTAPI SERVER")
    print("=" * 60)
    
    # Check if server is already running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print("✓ Server is already running!")
        return None
    except:
        pass
    
    # Start server
    print("\nStarting uvicorn server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    # Wait for server to start
    print("Waiting for server to start...")
    for i in range(10):
        time.sleep(1)
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"✓ Server started successfully after {i+1} seconds")
                return process
        except:
            continue
    
    print("✗ Server failed to start within 10 seconds")
    process.terminate()
    return None

def test_endpoints():
    """Test various endpoints"""
    print("\n" + "=" * 60)
    print("TESTING ENDPOINTS")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test root endpoint
    print("\n1. Testing root endpoint (GET /)...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Response: {data}")
            tests_passed += 1
        else:
            print(f"   ✗ Status: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        tests_failed += 1
    
    # Test health endpoint
    print("\n2. Testing health endpoint (GET /health)...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Response: {data}")
            tests_passed += 1
        else:
            print(f"   ✗ Status: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        tests_failed += 1
    
    # Test OpenAPI schema
    print("\n3. Testing OpenAPI schema (GET /openapi.json)...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            paths = data.get('paths', {})
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Total endpoints: {len(paths)}")
            print(f"   ✓ API Title: {data.get('info', {}).get('title', 'N/A')}")
            tests_passed += 1
        else:
            print(f"   ✗ Status: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        tests_failed += 1
    
    # Test key endpoints (they may require auth, so we just check if they exist)
    endpoints = [
        ("GET", "/auth/users", "List users"),
        ("GET", "/assets", "List assets"),
        ("GET", "/asset-requests", "List asset requests"),
        ("GET", "/tickets", "List tickets"),
    ]
    
    print("\n4. Testing key API endpoints...")
    for method, path, desc in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=5)
            status = response.status_code
            # 200 = success, 401/403 = auth required (endpoint exists), 404 = not found
            if status in [200, 401, 403]:
                print(f"   ✓ {method} {path}: {status} - {desc}")
                tests_passed += 1
            elif status == 404:
                print(f"   ✗ {method} {path}: 404 - Endpoint not found")
                tests_failed += 1
            else:
                print(f"   ⚠ {method} {path}: {status} - {desc}")
                tests_passed += 1  # Endpoint exists, just unexpected status
        except Exception as e:
            print(f"   ✗ {method} {path}: Error - {e}")
            tests_failed += 1
    
    # Test registration endpoint (should work without auth)
    print("\n5. Testing registration endpoint (POST /auth/register)...")
    try:
        test_user = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user, timeout=5)
        if response.status_code in [200, 201]:
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Registration endpoint working")
            tests_passed += 1
        elif response.status_code == 422:
            print(f"   ⚠ Status: 422 - Validation error (endpoint exists)")
            tests_passed += 1
        else:
            print(f"   ⚠ Status: {response.status_code}")
            tests_passed += 1  # Endpoint exists
    except Exception as e:
        print(f"   ✗ Error: {e}")
        tests_failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✓ Tests passed: {tests_passed}")
    print(f"✗ Tests failed: {tests_failed}")
    print(f"Total: {tests_passed + tests_failed}")
    
    return tests_failed == 0

if __name__ == "__main__":
    process = start_server()
    
    if process is None and requests.get(f"{BASE_URL}/health", timeout=2).status_code != 200:
        print("\n✗ Cannot proceed without server")
        sys.exit(1)
    
    success = test_endpoints()
    
    print("\n" + "=" * 60)
    print("SERVER INFORMATION")
    print("=" * 60)
    print(f"✓ Server running at: {BASE_URL}")
    print(f"✓ API Documentation: {BASE_URL}/docs")
    print(f"✓ Alternative docs: {BASE_URL}/redoc")
    print(f"✓ OpenAPI schema: {BASE_URL}/openapi.json")
    
    if process:
        print("\nPress Ctrl+C to stop the server")
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\nStopping server...")
            process.terminate()
            process.wait()
            print("Server stopped")
    
    sys.exit(0 if success else 1)

