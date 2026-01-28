"""Show backend server status"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("BACKEND SERVER STATUS".center(70))
print("=" * 70)

try:
    # Health check
    health = requests.get(f"{BASE_URL}/health", timeout=3)
    print(f"\n✓ Server Status: {health.json()}")
    
    # Root endpoint
    root = requests.get(f"{BASE_URL}/", timeout=3)
    print(f"\n✓ Root Endpoint:")
    print(json.dumps(root.json(), indent=2))
    
    # API Schema
    schema = requests.get(f"{BASE_URL}/openapi.json", timeout=3)
    if schema.status_code == 200:
        data = schema.json()
        print(f"\n✓ API Title: {data['info']['title']}")
        print(f"✓ Version: {data['info']['version']}")
        print(f"✓ Total Endpoints: {len(data['paths'])}")
    
    print("\n" + "=" * 70)
    print("ACCESS POINTS".center(70))
    print("=" * 70)
    print(f"\n✓ Server URL: {BASE_URL}")
    print(f"✓ API Documentation: {BASE_URL}/docs")
    print(f"✓ Alternative Docs: {BASE_URL}/redoc")
    print(f"✓ OpenAPI Schema: {BASE_URL}/openapi.json")
    print("\n" + "=" * 70)
    print("✓ Backend server is running and ready!")
    print("=" * 70 + "\n")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("Make sure server is running: uvicorn main:app --reload\n")

