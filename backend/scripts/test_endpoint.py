"""
Test the FastAPI endpoint directly using Python requests
"""
import requests
import json

def test_endpoint():
    print("\n=== TESTING /assets/stats ENDPOINT ===\n")
    
    url = "http://localhost:8000/assets/stats"
    
    try:
        print(f"Requesting: {url}")
        print("Setting 15 second timeout...")
        
        response = requests.get(url, timeout=15)
        
        print(f"\n✅ SUCCESS!")
        print(f"Status Code: {response.status_code}")
        print(f"\nResponse Data:")
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.Timeout:
        print("\n❌ REQUEST TIMED OUT (15s)")
        print("The server is not responding to the stats endpoint.")
        print("This suggests the FastAPI server may need to be restarted.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR")
        print("Could not connect to the server. Is it running?")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_endpoint()
