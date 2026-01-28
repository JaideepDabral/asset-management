from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID
from ..database.database import get_db
from ..schemas.ticket_schema import TicketCreate, TicketUpdate, TicketResponse, ITDiagnosisRequest, ResolutionUpdate
from ..services import ticket_service
from ..services import asset_request_service
from ..schemas.user_schema import UserResponse
from ..models.models import Asset, ByodDevice
from datetime import datetime

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"]
)


async def verify_it_management(user_id: UUID, db: AsyncSession) -> UserResponse:
    """
    Verify that the user is IT management (role=IT_MANAGEMENT) and active (Asynchronous).
    """
    user = await asset_request_service.get_user_by_id_db(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != "IT_MANAGEMENT":
        raise HTTPException(
            status_code=403,
            detail="Only users with role=IT_MANAGEMENT can perform this action",
        )
    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=403,
            detail="User account is not active",
        )
    return user


@router.post("/", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate, db: AsyncSession = Depends(get_db)):
    """Create a new ticket (Asynchronous)."""
    if ticket.related_asset_id:
        res_asset = await db.execute(select(Asset).filter(Asset.id == ticket.related_asset_id))
        asset = res_asset.scalars().first()
        if not asset:
            res_byod = await db.execute(select(ByodDevice).filter(ByodDevice.id == ticket.related_asset_id))
            byod = res_byod.scalars().first()
            if not byod:
                raise HTTPException(
                    status_code=400,
                    detail="related_asset_id must reference a valid asset or BYOD device",
                )
    return await ticket_service.create_ticket(db=db, ticket=ticket)

@router.get("/", response_model=List[TicketResponse])
async def read_tickets(requestor_id: Optional[UUID] = None, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Read all tickets (Asynchronous)."""
    return await ticket_service.get_tickets(db, requestor_id=requestor_id, skip=skip, limit=limit)

@router.get("/{ticket_id}", response_model=TicketResponse)
async def read_ticket(ticket_id: UUID, db: AsyncSession = Depends(get_db)):
    """Read a specific ticket (Asynchronous)."""
    db_ticket = await ticket_service.get_ticket(db, ticket_id=ticket_id)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db_ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: UUID, ticket_update: TicketUpdate, db: AsyncSession = Depends(get_db)):
    """Update a ticket (Asynchronous)."""
    db_ticket = await ticket_service.update_ticket(db, ticket_id=ticket_id, ticket_update=ticket_update)
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db_ticket


@router.post("/{ticket_id}/it/diagnose", response_model=TicketResponse)
async def it_diagnose_ticket(
    ticket_id: UUID,
    payload: ITDiagnosisRequest,
    db: AsyncSession = Depends(get_db),
):
    """IT Management diagnosis for tickets (Asynchronous)."""
    reviewer = await verify_it_management(payload.reviewer_id, db)

    db_ticket = await ticket_service.get_ticket(db, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not db_ticket.related_asset_id:
        raise HTTPException(
            status_code=400,
            detail="Ticket is not linked to any asset or BYOD device",
        )

    # Try to resolve as company asset
    res_asset = await db.execute(select(Asset).filter(Asset.id == db_ticket.related_asset_id))
    asset = res_asset.scalars().first()
    if asset:
        if payload.outcome == "repair":
            asset.status = "Repair"
            db_ticket.status = "IN_PROGRESS"
        elif payload.outcome == "secure":
            db_ticket.status = "RESOLVED"
            
        await db.commit()
        await db.refresh(db_ticket)
        return db_ticket

    # Otherwise treat as BYOD device
    res_byod = await db.execute(select(ByodDevice).filter(ByodDevice.id == db_ticket.related_asset_id))
    byod = res_byod.scalars().first()
    if not byod:
        raise HTTPException(
            status_code=400,
            detail="related_asset_id does not match any asset or BYOD device",
        )

    if payload.outcome == "secure":
        byod.compliance_status = "MDM_ENFORCED"
        db_ticket.status = "RESOLVED"
    elif payload.outcome == "repair":
        byod.compliance_status = "NON_COMPLIANT"
        db_ticket.status = "IN_PROGRESS"
        
    await db.commit()
    await db.refresh(db_ticket)
    return db_ticket

@router.post("/{ticket_id}/acknowledge", response_model=TicketResponse)
async def acknowledge_ticket(ticket_id: UUID, payload: ITDiagnosisRequest, db: AsyncSession = Depends(get_db)):
    """IT Management acknowledges the ticket (Asynchronous)."""
    reviewer = await verify_it_management(payload.reviewer_id, db)
    
    db_ticket = await ticket_service.get_ticket(db, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    if db_ticket.status and db_ticket.status.upper() == "OPEN":
        db_ticket.status = "IN_PROGRESS"
        
        new_event = {
            "action": "ACKNOWLEDGED",
            "byRole": "IT_MANAGEMENT",
            "byUser": reviewer.full_name,
            "timestamp": datetime.utcnow().isoformat(),
            "comment": payload.notes or "Ticket acknowledged and moved to Investigation"
        }
        
        current_timeline = list(db_ticket.timeline) if db_ticket.timeline else []
        current_timeline.append(new_event)
        db_ticket.timeline = current_timeline
        
        if payload.notes:
            db_ticket.resolution_notes = payload.notes

    await db.commit()
    await db.refresh(db_ticket)
    return db_ticket

@router.post("/{ticket_id}/progress", response_model=TicketResponse)
async def update_ticket_progress(ticket_id: UUID, payload: ResolutionUpdate, db: AsyncSession = Depends(get_db)):
    """Update resolution progress (Asynchronous)."""
    reviewer = await verify_it_management(payload.reviewer_id, db)
    
    db_ticket = await ticket_service.get_ticket(db, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    db_ticket.resolution_notes = payload.notes
    db_ticket.resolution_checklist = payload.checklist
    db_ticket.resolution_percentage = payload.percentage
    
    if db_ticket.status != "IN_PROGRESS" and db_ticket.status != "RESOLVED":
        db_ticket.status = "IN_PROGRESS"

    new_event = {
        "action": "PROGRESS_UPDATE",
        "byRole": "IT_MANAGEMENT",
        "byUser": reviewer.full_name,
        "timestamp": datetime.utcnow().isoformat(),
        "comment": f"Resolution progress updated to {payload.percentage}%"
    }
    current_timeline = list(db_ticket.timeline) if db_ticket.timeline else []
    current_timeline.append(new_event)
    db_ticket.timeline = current_timeline

    await db.commit()
    await db.refresh(db_ticket)
    return db_ticket

@router.post("/{ticket_id}/resolve", response_model=TicketResponse)
async def resolve_ticket(ticket_id: UUID, payload: ResolutionUpdate, db: AsyncSession = Depends(get_db)):
    """IT Management resolves the ticket (Asynchronous)."""
    reviewer = await verify_it_management(payload.reviewer_id, db)
    
    db_ticket = await ticket_service.get_ticket(db, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    db_ticket.resolution_notes = payload.notes
    db_ticket.resolution_checklist = payload.checklist
    db_ticket.resolution_percentage = 100.0
    
    db_ticket.status = "RESOLVED"

    new_event = {
        "action": "RESOLVED",
        "byRole": "IT_MANAGEMENT",
        "byUser": reviewer.full_name,
        "timestamp": datetime.utcnow().isoformat(),
        "comment": payload.notes or "Ticket has been marked as Resolved"
    }
    current_timeline = list(db_ticket.timeline) if db_ticket.timeline else []
    current_timeline.append(new_event)
    db_ticket.timeline = current_timeline
    
    await db.commit()
    await db.refresh(db_ticket)
    return db_ticket
