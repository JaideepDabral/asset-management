
import sys
import os

try:
    from app.routers import workflows
    print("Successfully imported workflows")
except Exception as e:
    print(f"Error importing workflows: {e}")

try:
    from app.services import asset_request_service
    print("Successfully imported asset_request_service")
except Exception as e:
    print(f"Error importing asset_request_service: {e}")

try:
    from app.routers import auth
    print("Successfully imported auth")
except Exception as e:
    print(f"Error importing auth: {e}")

try:
    from app.routers import assets
    print("Successfully imported assets")
except Exception as e:
    print(f"Error importing assets: {e}")

try:
    from app.routers import asset_requests
    print("Successfully imported asset_requests")
except Exception as e:
    print(f"Error importing asset_requests: {e}")
