from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from typing import List, Optional
from ..database.database import get_db
from ..models.models import AuditLog, Asset
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

router = APIRouter(
    prefix="/audit",
    tags=["audit"]
)

class AuditLogResponse(BaseModel):
    id: UUID
    entity_type: str
    entity_id: Optional[str] = None
    action: str
    performed_by: Optional[str] = None
    timestamp: datetime
    details: Optional[dict] = None

    class Config:
        from_attributes = True

@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    after_id: Optional[UUID] = None,
    entity_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get system audit logs (Asynchronous).
    Supports Keyset pagination via 'after_id'.
    """
    query = select(AuditLog)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
        
    if after_id:
        res_anchor = await db.execute(select(AuditLog).filter(AuditLog.id == after_id))
        anchor = res_anchor.scalars().first()
        if anchor:
            # Anchor point for keyset pagination
            query = query.filter(
                and_(
                    AuditLog.timestamp <= anchor.timestamp,
                    AuditLog.id < anchor.id
                )
            )

    query = query.order_by(AuditLog.timestamp.desc(), AuditLog.id.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/stats")
async def get_audit_stats(db: AsyncSession = Depends(get_db)):
    """
    Get audit log statistics (Asynchronous).
    """
    total_res = await db.execute(select(func.count(AuditLog.id)))
    total = total_res.scalar() or 0
    
    api_res = await db.execute(select(func.count(AuditLog.id)).filter(AuditLog.action == "DATA_COLLECT"))
    api_collects = api_res.scalar() or 0
    
    return {
        "total": total,
        "api_collects": api_collects
    }

@router.post("/sync")
async def sync_orphaned_logs(db: AsyncSession = Depends(get_db)):
    """
    Search for DATA_COLLECT logs that don't have corresponding assets and create them (Asynchronous).
    """
    res_logs = await db.execute(select(AuditLog).filter(AuditLog.action == "DATA_COLLECT"))
    logs = res_logs.scalars().all()
    repaired_count = 0
    
    for log in logs:
        data = log.details
        if not data or not isinstance(data, dict):
            continue
        
        serial_number = data.get("serial_number")
        if not serial_number:
            continue
            
        # Check if asset exists
        res_asset = await db.execute(select(Asset).filter(Asset.serial_number == serial_number))
        existing_asset = res_asset.scalars().first()
        if existing_asset:
            continue
            
        # Create asset from log data
        try:
            hostname = data.get("hostname") or data.get("name") or "Unknown"
            asset_metadata = data.get("asset_metadata", {})
            hardware = data.get("hardware", {})
            
            asset_type = data.get("type") or asset_metadata.get("type", "Unknown")
            asset_model = data.get("model") or hardware.get("model") or "Unknown"
            asset_vendor = data.get("vendor") or data.get("manufacturer") or hardware.get("manufacturer") or "Unknown"
            asset_segment = data.get("segment") or asset_metadata.get("segment", "IT")
            asset_location = data.get("location") or asset_metadata.get("location")
            asset_status = data.get("status", "Active")
            
            specifications = {
                "hardware": hardware if hardware else {k: v for k, v in data.items() if k in ["model", "manufacturer", "cpu", "ram", "storage"]},
                "os": data.get("os", {}),
                "network": data.get("network", {})
            }

            new_asset = Asset(
                name=hostname,
                type=asset_type,
                model=asset_model,
                vendor=asset_vendor,
                serial_number=serial_number,
                segment=asset_segment,
                status=asset_status,
                location=asset_location,
                specifications=specifications,
                cost=data.get("cost", 0.0)
            )
            
            db.add(new_asset)
            await db.commit() # Individual commit for safety in loop, or could bulk for perf
            repaired_count += 1
        except Exception as e:
            print(f"Failed to sync log {log.id}: {e}")
            await db.rollback()
            
    return {
        "status": "success",
        "synced_count": repaired_count
    }
