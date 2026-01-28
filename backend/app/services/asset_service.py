"""
Asset service layer - Database operations using SQLAlchemy (Asynchronous)
"""
import uuid
from uuid import UUID
from datetime import datetime, date, timedelta
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, select, delete, update
from sqlalchemy.orm import selectinload
from ..models.models import Asset, ByodDevice, User, AssetAssignment, AssetInventory
from ..schemas.asset_schema import AssetCreate, AssetUpdate, AssetResponse


async def get_all_assets(db: AsyncSession) -> List[AssetResponse]:
    """
    Get all assets from the database
    """
    # 1. Fetch standard assets
    result = await db.execute(select(Asset))
    standard_assets = result.scalars().all()
    results = [AssetResponse.model_validate(asset) for asset in standard_assets]
    
    # 2. Fetch BYOD devices and map them to AssetResponse
    byod_query = select(ByodDevice, User).join(User, ByodDevice.owner_id == User.id)
    byod_result = await db.execute(byod_query)
    byods = byod_result.all()
    
    for byod, owner in byods:
        results.append(AssetResponse(
            id=byod.id,
            name=f"BYOD: {byod.device_model}",
            type="BYOD",
            model=byod.device_model,
            vendor="Personal",
            serial_number=byod.serial_number,
            status="Active",
            assigned_to=owner.full_name,
            location=owner.location or "Remote",
            segment="IT",
            specifications={"os_version": byod.os_version},
            created_at=byod.created_at or datetime.now(),
            updated_at=byod.created_at or datetime.now(),
            assignment_date=(byod.created_at or datetime.now()).date()
        ))
        
    return results


async def get_asset_by_id(db: AsyncSession, asset_id: UUID) -> Optional[AssetResponse]:
    """
    Get a single asset by ID from the database
    """
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    asset = result.scalars().first()
    if asset:
        return AssetResponse.model_validate(asset)
    return None


async def get_assets_by_assigned_to(db: AsyncSession, user_name: str) -> List[AssetResponse]:
    """
    Get all assets assigned to a specific user
    """
    # 1. Standard assets
    standard_query = select(Asset).filter(func.lower(Asset.assigned_to) == user_name.lower())
    standard_result = await db.execute(standard_query)
    standard_assets = standard_result.scalars().all()
    results = [AssetResponse.model_validate(asset) for asset in standard_assets]
    
    # 2. BYOD devices for this user
    byod_query = select(ByodDevice, User).join(User, ByodDevice.owner_id == User.id).filter(func.lower(User.full_name) == user_name.lower())
    byod_result = await db.execute(byod_query)
    byods = byod_result.all()
    
    for byod, owner in byods:
        results.append(AssetResponse(
            id=byod.id,
            name=f"BYOD: {byod.device_model}",
            type="BYOD",
            model=byod.device_model,
            vendor="Personal",
            serial_number=byod.serial_number,
            status="Active",
            assigned_to=owner.full_name,
            location=owner.location or "Remote",
            segment="IT",
            specifications={"os_version": byod.os_version},
            created_at=byod.created_at or datetime.now(),
            updated_at=byod.created_at or datetime.now(),
            assignment_date=(byod.created_at or datetime.now()).date()
        ))
        
    return results


async def create_asset(db: AsyncSession, asset: AssetCreate) -> AssetResponse:
    """
    Create a new asset in the database
    """
    # Convert Pydantic model to dict, excluding None values for optional fields
    asset_dict = asset.model_dump(exclude_unset=True)
    
    # Create SQLAlchemy model instance
    db_asset = Asset(
        id=uuid.uuid4(),
        **asset_dict
    )
    
    db.add(db_asset)
    
    # Inventory Logic for new assets
    if db_asset.status == "In Stock":
        inventory_item = AssetInventory(
            id=uuid.uuid4(),
            asset_id=db_asset.id,
            location=db_asset.location,
            status="Available",
            stocked_at=datetime.now()
        )
        db.add(inventory_item)
        
    await db.commit()
    await db.refresh(db_asset)
    
    return AssetResponse.model_validate(db_asset)


async def update_asset(db: AsyncSession, asset_id: UUID, asset_update: AssetUpdate) -> Optional[AssetResponse]:
    """
    Update an existing asset in the database
    """
    # Find the asset
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    db_asset = result.scalars().first()
    if not db_asset:
        return None
    
    # Update only provided fields
    update_data = asset_update.model_dump(exclude_unset=True)
    
    # Track status change for Inventory management
    previous_status = db_asset.status
    new_status = update_data.get('status')
    
    for field, value in update_data.items():
        setattr(db_asset, field, value)
        
    # Inventory Management Logic
    if new_status and new_status != previous_status:
        # 1. Entering Stock
        if new_status == "In Stock":
            inv_result = await db.execute(select(AssetInventory).filter(AssetInventory.asset_id == asset_id))
            exists = inv_result.scalars().first()
            if not exists:
                inventory_item = AssetInventory(
                    id=uuid.uuid4(),
                    asset_id=asset_id,
                    location=db_asset.location,
                    status="Available",
                    stocked_at=datetime.now()
                )
                db.add(inventory_item)
        
        # 2. Leaving Stock (assigned, retired, repair, etc.)
        elif previous_status == "In Stock":
            await db.execute(delete(AssetInventory).where(AssetInventory.asset_id == asset_id))
    
    await db.commit()
    await db.refresh(db_asset)
    
    return AssetResponse.model_validate(db_asset)


async def assign_asset(db: AsyncSession, asset_id: UUID, user: str, location: str, assign_date: date) -> Optional[AssetResponse]:
    """
    Assign an asset to a user and record in assignment history
    """
    # 1. Update the Asset record
    updated_asset = await update_asset(
        db,
        asset_id,
        AssetUpdate(
            assigned_to=user,
            location=location,
            assignment_date=assign_date,
            status="Active"
        )
    )
    
    # 2. Create Assignment History Record
    if updated_asset:
        try:
            # Resolve 'user' string (Name or ID) to a User object
            user_obj = None
            
            # Try as ID
            try:
                if isinstance(user, UUID) or (isinstance(user, str) and len(user) in [32, 36]):
                    user_result = await db.execute(select(User).filter(User.id == user))
                    user_obj = user_result.scalars().first()
            except:
                pass
                
            # Try as Name
            if not user_obj:
                user_name_result = await db.execute(select(User).filter(func.lower(User.full_name) == func.lower(user)))
                user_obj = user_name_result.scalars().first()
            
            # If User found, create assignment record
            if user_obj:
                # Check if active assignment already exists to avoid duplicates
                exists_result = await db.execute(select(AssetAssignment).filter(
                    AssetAssignment.asset_id == asset_id,
                    AssetAssignment.user_id == user_obj.id
                ))
                exists = exists_result.scalars().first()
                
                if not exists:
                    assignment = AssetAssignment(
                        id=uuid.uuid4(),
                        asset_id=asset_id,
                        user_id=user_obj.id,
                        assigned_by="System", 
                        location=location,
                        assigned_at=assign_date or datetime.now()
                    )
                    db.add(assignment)
                    await db.commit()
            
        except Exception as e:
            print(f"Error creating assignment history: {e}")
            # Don't fail the request if history creation fails
            
    return updated_asset


async def get_asset_stats(db: AsyncSession):
    """
    Get aggregated statistics from the database
    """
    # Total count
    total = (await db.execute(select(func.count(Asset.id)))).scalar()
    
    # Status counts
    active = (await db.execute(select(func.count(Asset.id)).filter(Asset.status == "Active"))).scalar()
    in_stock = (await db.execute(select(func.count(Asset.id)).filter(Asset.status == "In Stock"))).scalar()
    repair = (await db.execute(select(func.count(Asset.id)).filter(Asset.status == "Repair"))).scalar()
    retired = (await db.execute(select(func.count(Asset.id)).filter(Asset.status == "Retired"))).scalar()
    
    # Warranty expiring soon (next 30 days) or expired
    today = date.today()
    warranty_cutoff = today + timedelta(days=30)
    warranty_risk = (await db.execute(select(func.count(Asset.id)).filter(
        and_(
            Asset.warranty_expiry.isnot(None),
            Asset.warranty_expiry <= warranty_cutoff
        )
    ))).scalar()
    
    # Total value
    total_value_result = (await db.execute(select(func.sum(Asset.cost)))).scalar()
    total_value = float(total_value_result) if total_value_result else 0.0
    
    # Location breakdown
    location_results = (await db.execute(select(
        Asset.location,
        func.count(Asset.id).label('count')
    ).group_by(Asset.location))).all()
    by_location = [
        {"name": loc or "Unknown", "value": count}
        for loc, count in location_results
    ]
    
    # Type breakdown
    type_results = (await db.execute(select(
        Asset.type,
        func.count(Asset.id).label('count')
    ).group_by(Asset.type))).all()
    by_type = [
        {"name": asset_type or "Unknown", "value": count}
        for asset_type, count in type_results
    ]
    
    # Segment breakdown
    segment_results = (await db.execute(select(
        Asset.segment,
        func.count(Asset.id).label('count')
    ).group_by(Asset.segment))).all()
    by_segment = [
        {"name": seg or "Unknown", "value": count}
        for seg, count in segment_results
    ]
    
    # Status breakdown
    status_results = (await db.execute(select(
        Asset.status,
        func.count(Asset.id).label('count')
    ).group_by(Asset.status))).all()
    by_status = [
        {"name": stat or "Unknown", "value": count}
        for stat, count in status_results
    ]
    
    # Trend Data Generation (Mock)
    import random
    import math
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    
    monthly_trends = []
    for i, month in enumerate(months):
        monthly_trends.append({
            "name": month,
            "repaired": int(5 + 3 * math.sin(i * 0.5) + random.randint(0, 3)),
            "renewed": int(8 + 4 * math.cos(i * 0.5) + random.randint(0, 5))
        })
    
    quarterly_trends = []
    for i, q in enumerate(quarters):
        quarterly_trends.append({
            "name": q,
            "repaired": int(15 + 5 * math.sin(i * 1.5) + random.randint(2, 5)),
            "renewed": int(25 + 8 * math.cos(i * 1.5) + random.randint(3, 8))
        })
    
    return {
        "total": total,
        "total_value": total_value,
        "active": active,
        "in_stock": in_stock,
        "repair": repair,
        "retired": retired,
        "warranty_risk": warranty_risk,
        "by_location": by_location,
        "by_type": by_type,
        "by_segment": by_segment,
        "by_status": by_status,
        "trends": {
            "monthly": monthly_trends,
            "quarterly": quarterly_trends
        }
    }


async def get_asset_events(db: AsyncSession, asset_id: UUID) -> List[dict]:
    """
    Get asset event history (mock implementation based on asset data)
    """
    asset = await get_asset_by_id(db, asset_id)
    if not asset:
        return []
    
    events = []
    
    # 1. Procurement/Onboarding (Based on purchase date)
    purchase_date = asset.purchase_date if asset.purchase_date else date.today() - timedelta(days=60)
    events.append({
        "date": purchase_date.strftime("%Y-%m-%d"),
        "event": "Procurement Initiated",
        "description": f"PO Generated for {asset.vendor} {asset.model}",
        "user": "Finance Dept",
        "status": "completed"
    })
    
    # ... (Rest of events logic remains same, just uses async get_asset_by_id)
    received_date = purchase_date + timedelta(days=5)
    events.append({
        "date": received_date.strftime("%Y-%m-%d"),
        "event": "Asset Onboarded",
        "description": f"Received at {asset.location or 'Headquarters'}, Tagged & Scanned",
        "user": "System Admin",
        "status": "completed"
    })
    
    qc_date = received_date + timedelta(days=1)
    events.append({
        "date": qc_date.strftime("%Y-%m-%d"),
        "event": "Quality Check",
        "description": "Passed diagnostics and hardware verification",
        "user": "IT Technician",
        "status": "completed"
    })
    
    if asset.assigned_to:
        assign_date = asset.assignment_date if asset.assignment_date else qc_date + timedelta(days=2)
        events.append({
            "date": assign_date.strftime("%Y-%m-%d"),
            "event": "Asset Assigned",
            "description": f"Assigned to {asset.assigned_to}",
            "user": "IT Manager",
            "status": "completed"
        })
    
    if asset.status == "Repair":
        repair_date = date.today() - timedelta(days=2)
        events.append({
            "date": repair_date.strftime("%Y-%m-%d"),
            "event": "Maintenance Request",
            "description": "Ticket #INC-9982: Hardware malfunction reported",
            "user": asset.assigned_to or "System",
            "status": "active"
        })
    elif asset.status == "Retired":
        retire_date = date.today()
        events.append({
            "date": retire_date.strftime("%Y-%m-%d"),
            "event": "Asset Retired",
            "description": "End of lifecycle processing",
            "user": "Asset Manager",
            "status": "completed"
        })
    
    events.sort(key=lambda x: x['date'], reverse=True)
    return events
