"""
Quick endpoint validation test
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("ENDPOINT VALIDATION TEST")
print("=" * 70)

# Get OpenAPI schema
try:
    response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
    if response.status_code == 200:
        schema = response.json()
        paths = schema.get('paths', {})
        
        print(f"\n✓ Total endpoints: {len(paths)}")
        
        # Check for workflow endpoints
        workflow_endpoints = {
            "Procurement Approve": "/asset-requests/{id}/procurement/approve",
            "Procurement Reject": "/asset-requests/{id}/procurement/reject",
            "QC Perform": "/asset-requests/{id}/qc/perform",
            "User Accept": "/asset-requests/{id}/user/accept",
            "User Reject": "/asset-requests/{id}/user/reject",
            "Process Exit Assets": "/exit-requests/{id}/process-assets",
            "Process Exit BYOD": "/exit-requests/{id}/process-byod",
            "Complete Exit": "/exit-requests/{id}/complete",
        }
        
        print("\nWorkflow Endpoints Check:")
        print("-" * 70)
        
        for name, endpoint_pattern in workflow_endpoints.items():
            # Check various path formats
            found = False
            for path in paths.keys():
                if endpoint_pattern.split('/')[-1] in path or endpoint_pattern.split('/')[-2:] == path.split('/')[-2:]:
                    found = True
                    print(f"✓ {name}: Found as {path}")
                    break
            
            if not found:
                # Check if it exists with different parameter names
                alt_found = any(
                    endpoint_pattern.replace("{id}", "").replace("/", "") in path.replace("/", "").replace("-", "")
                    for path in paths.keys()
                )
                if alt_found:
                    print(f"⚠ {name}: May exist (check path format)")
                else:
                    print(f"✗ {name}: Not found")
        
        # List all asset-request endpoints
        print("\n" + "-" * 70)
        print("All Asset Request Endpoints:")
        print("-" * 70)
        asset_request_paths = [p for p in sorted(paths.keys()) if 'asset-request' in p.lower()]
        for path in asset_request_paths[:15]:
            methods = list(paths[path].keys())
            print(f"  {', '.join(methods):6} {path}")
        
        # List exit endpoints
        print("\n" + "-" * 70)
        print("Exit Workflow Endpoints:")
        print("-" * 70)
        exit_paths = [p for p in sorted(paths.keys()) if 'exit' in p.lower()]
        for path in exit_paths:
            methods = list(paths[path].keys())
            print(f"  {', '.join(methods):6} {path}")
        
        print("\n" + "=" * 70)
        print("✓ Endpoint validation complete")
        print("=" * 70)
        
except Exception as e:
    print(f"✗ Error: {e}")

