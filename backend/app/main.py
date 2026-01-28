from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from .database.database import get_db, test_connection, get_connection_info
from .models.models import AuditLog, Asset
import traceback
from datetime import datetime
import os
from .routers import upload, workflows, disposal, audit, assets, auth, tickets, asset_requests, users, reference, financials

# Create FastAPI app instance
app = FastAPI(
    title="ITSM Asset Management API",
    description="Asset Management API for ITSM Platform (Asynchronous)",
    version="1.1.0"
)

# Enterprise API Router
from .api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")

# Suppress favicon 404s
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return JSONResponse(content={})

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug Exception Handler - Only catch non-HTTP exceptions
from fastapi.exceptions import HTTPException as FastAPIHTTPException

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    # Don't catch HTTPException - let FastAPI handle it properly
    if isinstance(exc, FastAPIHTTPException):
        raise exc
    
    print(f"ERROR: {exc}")
    traceback.print_exc()
    with open("exception.log", "a") as f:
        f.write(f"\n--- {datetime.now()} ---\n")
        f.write(traceback.format_exc())
    
    is_debug = os.getenv("DEBUG", "false").lower() == "true"
    content = {"detail": "Internal Server Error"}
    if is_debug:
        content["detail"] = str(exc)
        content["traceback"] = traceback.format_exc()
        
    return JSONResponse(
        status_code=500,
        content=content,
        headers={"Access-Control-Allow-Origin": "http://localhost:3000"}
    )

# All routers are now registered through the versioned api_router above

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ITSM Asset Management API",
        "version": "1.1.0 (Async)",
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.api_route("/api/v1/collect", methods=["GET", "POST"])
async def collect_data(
    request: Request, 
    db: AsyncSession = Depends(get_db),
    x_api_token: str = Header(None, alias="X-API-Token")
):
    """
    Collect data from external sources (Asynchronous).
    """
    if request.method == "POST":
        try:
            data = await request.json()
        except:
            data = {"error": "Invalid JSON or body"}
    else:
        data = dict(request.query_params)
    
    from .utils.api_token_utils import validate_api_token
    is_valid = await validate_api_token(x_api_token) if x_api_token else False
    
    # Audit log
    try:
        audit_log = AuditLog(
            entity_type="API",
            entity_id="collect_endpoint",
            action="DATA_COLLECT",
            performed_by=f"SRC:{request.client.host} (Token:{'Valid' if is_valid else 'Invalid/Missing'})",
            details={
                "method": request.method,
                "headers": {k: v for k, v in request.headers.items() if k.lower() != "x-api-token"},
                "payload_summary": list(data.keys()) if isinstance(data, dict) else str(data)[:100],
                "auth_success": is_valid,
                "remote_ip": request.client.host
            }
        )
        db.add(audit_log)
        await db.commit()
    except Exception as e:
        print(f"Error saving audit log: {e}")
        await db.rollback()

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    if "serial_number" in data and isinstance(data, dict):
        try:
            serial_number = str(data.get("serial_number")).strip()
            hostname = data.get("hostname") or data.get("name", "Unknown")
            
            # Map fields
            asset_metadata = data.get("asset_metadata", {})
            hardware = data.get("hardware", {})
            asset_type = data.get("type") or asset_metadata.get("type", "Unknown")
            asset_model = data.get("model") or hardware.get("model") or "Unknown"
            asset_vendor = data.get("vendor") or data.get("manufacturer") or hardware.get("manufacturer") or "Unknown"
            asset_segment = data.get("segment") or asset_metadata.get("segment", "IT")
            asset_location = data.get("location") or asset_metadata.get("location")
            asset_status = data.get("status", "Active")
            asset_assigned_to = data.get("assigned_to")
            
            specifications = {
                "hardware": hardware,
                "os": data.get("os", {}),
                "network": data.get("network", {})
            }
            
            res_asset = await db.execute(select(Asset).filter(Asset.serial_number == serial_number))
            existing_asset = res_asset.scalars().first()
            
            if existing_asset:
                existing_asset.name = hostname
                existing_asset.type = asset_type
                existing_asset.model = asset_model
                existing_asset.vendor = asset_vendor
                existing_asset.segment = asset_segment
                existing_asset.location = asset_location or existing_asset.location
                existing_asset.status = asset_status
                if asset_assigned_to:
                    existing_asset.assigned_to = asset_assigned_to
                existing_asset.specifications = specifications
                existing_asset.updated_at = datetime.now()
                await db.commit()
                return {"status": "success", "action": "updated", "asset_id": existing_asset.id}
            else:
                new_asset = Asset(
                    name=hostname,
                    type=asset_type,
                    model=asset_model,
                    vendor=asset_vendor,
                    serial_number=serial_number,
                    segment=asset_segment,
                    status=asset_status,
                    location=asset_location,
                    assigned_to=asset_assigned_to,
                    specifications=specifications,
                    cost=data.get("cost", 0.0)
                )
                db.add(new_asset)
                await db.commit()
                return {"status": "success", "action": "created", "asset_id": new_asset.id}
                
        except Exception as e:
            await db.rollback()
            return {"status": "error", "message": str(e)}
    
    return {"status": "success", "logged": True}

@app.get("/health/db")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    """
    Check database connectivity (Asynchronous).
    """
    try:
        result = await db.execute(text("SELECT current_database(), version()"))
        row = result.fetchone()
        db_name, version = row
        
        info = get_connection_info()
        return {
            "status": "connected",
            "database": db_name,
            "version": version,
            "info": info
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
