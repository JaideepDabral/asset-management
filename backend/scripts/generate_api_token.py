"""
Generate an API token for the collect endpoint
"""
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_token_utils import generate_api_token

if __name__ == "__main__":
    # Generate a token that never expires
    token = generate_api_token(
        name="ITSM Data Collection API",
        created_by="System",
        expires_days=None  # Never expires
    )
    
    print("\n" + "="*80)
    print("🔑 API TOKEN GENERATED SUCCESSFULLY")
    print("="*80)
    print(f"\nToken: {token}")
    print("\nUsage:")
    print(f'  curl -X POST http://localhost:8000/api/v1/collect \\')
    print(f'       -H "X-API-Token: {token}" \\')
    print(f'       -H "Content-Type: application/json" \\')
    print(f'       -d \'{{"serial_number": "ABC123", "hostname": "server01"}}\'')
    print("\n" + "="*80)
    print("⚠️  IMPORTANT: Save this token securely. It will not be shown again.")
    print("="*80 + "\n")
