"""
Asset Request endpoints for manager approvals (Asynchronous)
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from ..database.database import get_db
from ..schemas.asset_request_schema import (
    AssetRequestCreate,
    AssetRequestResponse,
    ManagerApprovalRequest,
    ManagerRejectionRequest,
    ByodRegisterRequest,
    ProcurementApprovalRequest,
    ProcurementRejectionRequest,
    QCPerformRequest,
    UserAcceptanceRequest,
    ITApprovalRequest,
    ITRejectionRequest,
)
from ..services import asset_request_service
from ..schemas.user_schema import UserResponse
from ..models.models import ByodDevice, Asset, AssetAssignment, PurchaseRequest, User, PurchaseOrder, AssetInventory
from ..services import asset_service
from ..schemas.asset_schema import AssetCreate
import uuid as _uuid
from uuid import UUID
from datetime import date

router = APIRouter(
    prefix="/asset-requests",
    tags=["asset-requests"]
)

@router.get("", response_model=List[AssetRequestResponse])
async def get_asset_requests(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    requester_id: Optional[UUID] = None,
    domain: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all asset requests (Asynchronous).
    """
    return await asset_request_service.get_all_asset_requests(
        db, skip=skip, limit=limit, status=status, requester_id=requester_id, domain=domain
    )


@router.get("/{request_id}", response_model=AssetRequestResponse)
async def get_asset_request_by_id(
    request_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single asset request by ID (Asynchronous).
    """
    asset_request = await asset_request_service.get_asset_request_by_id(db, request_id)
    if not asset_request:
        raise HTTPException(status_code=404, detail="Asset request not found")
    return asset_request


async def verify_active_end_user(
    requester_id: UUID,
    db: AsyncSession
):
    """
    Verify that the user is an ACTIVE END_USER (Asynchronous).
    """
    user = await asset_request_service.get_user_by_id_db(db, requester_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != "END_USER":
        raise HTTPException(status_code=403, detail="Only END_USER can create requests")
    if user.status != "ACTIVE":
        raise HTTPException(status_code=403, detail="User account is not active")
    
    return user

@router.post("", response_model=AssetRequestResponse, status_code=201)
async def create_asset_request(
    request: AssetRequestCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new asset request (Asynchronous).
    """
    await verify_active_end_user(request.requester_id, db)
    return await asset_request_service.create_asset_request(db, request, initial_status="SUBMITTED")


async def verify_manager_authorization(
    manager_id: UUID,
    db: AsyncSession
):
    """
    Verify that the user is a valid manager (Asynchronous).
    """
    manager = await asset_request_service.get_user_by_id_db(db, manager_id)
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    if manager.role != "END_USER" or manager.position != "MANAGER":
        raise HTTPException(status_code=403, detail="Only managers can approve/reject")
    if manager.status != "ACTIVE":
        raise HTTPException(status_code=403, detail="Manager account is not active")
    return manager


@router.post("/{request_id}/manager/approve", response_model=AssetRequestResponse)
async def approve_asset_request(
    request_id: UUID,
    approval: ManagerApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Approve an asset request (Asynchronous).
    """
    manager = await verify_manager_authorization(approval.manager_id, db)
    db_request = await asset_request_service.get_asset_request_by_id_db(db, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if db_request.status != "SUBMITTED":
        raise HTTPException(status_code=403, detail="Already processed")
    
    requester = await asset_request_service.get_user_by_id_db(db, db_request.requester_id)
    if not requester:
        raise HTTPException(status_code=404, detail="Requester not found")
    
    # Verify domain match
    if not (manager.department == requester.department or manager.domain == requester.domain):
        raise HTTPException(status_code=403, detail="Manager/Requester domain mismatch")
    
    return await asset_request_service.update_asset_request_status_with_validation(
        db, request_id, "MANAGER_APPROVED", "MANAGER", manager.id, manager.full_name, decision="APPROVED"
    )

@router.post("/{request_id}/manager/reject", response_model=AssetRequestResponse)
async def reject_asset_request(
    request_id: UUID,
    rejection: ManagerRejectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reject an asset request (Asynchronous).
    """
    manager = await verify_manager_authorization(rejection.manager_id, db)
    db_request = await asset_request_service.get_asset_request_by_id_db(db, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if db_request.status != "SUBMITTED":
        raise HTTPException(status_code=403, detail="Already processed")
    
    requester = await asset_request_service.get_user_by_id_db(db, db_request.requester_id)
    if not (manager.department == requester.department or manager.domain == requester.domain):
        raise HTTPException(status_code=403, detail="Mismatch")
    
    return await asset_request_service.update_asset_request_status_with_validation(
        db, request_id, "MANAGER_REJECTED", "MANAGER", manager.id, manager.full_name, reason=rejection.reason
    )

# Backward compatibility aliases
@router.post("/{id}/manager/approve-v2", response_model=AssetRequestResponse)
async def manager_approve_request_v2(id: UUID, approval: ManagerApprovalRequest, db: AsyncSession = Depends(get_db)):
    return await approve_asset_request(id, approval, db)

@router.post("/{id}/manager/reject-v2", response_model=AssetRequestResponse)
async def manager_reject_request_v2(id: UUID, rejection: ManagerRejectionRequest, db: AsyncSession = Depends(get_db)):
    return await reject_asset_request(id, rejection, db)

# ---------------- IT APPROVAL ROUTES ----------------

async def verify_it_management(user_id: UUID, db: AsyncSession) -> User:
    user = await asset_request_service.get_user_by_id_db(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role != "IT_MANAGEMENT":
        raise HTTPException(status_code=403, detail="Not IT_MANAGEMENT")
    if user.status != "ACTIVE":
        raise HTTPException(status_code=403, detail="Not active")
    return user


@router.post("/{request_id}/it/approve", response_model=AssetRequestResponse)
async def it_approve_request(
    request_id: UUID,
    approval: ITApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    print(f"[IT_APPROVE] Received request for request_id={request_id}, reviewer_id={approval.reviewer_id}")
    reviewer = await verify_it_management(approval.reviewer_id, db)
    print(f"[IT_APPROVE] Reviewer verified: {reviewer.full_name} (ID: {reviewer.id})")
    try:
        res = await asset_request_service.update_it_review_status(
            db, request_id, "IT_APPROVED", reviewer.id, reviewer.full_name, "IT_APPROVED"
        )
        if not res:
            print(f"[IT_APPROVE] Request {request_id} not found or update failed")
            raise HTTPException(status_code=404, detail="Asset request not found")
        print(f"[IT_APPROVE] Successfully approved request {request_id}")
        return res
    except HTTPException:
        # Re-raise HTTPException as-is (don't wrap it)
        raise
    except ValueError as e:
        # Handle state transition validation errors
        print(f"[IT_APPROVE] State validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle any other unexpected errors
        import traceback
        print(f"[IT_APPROVE] Unexpected error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{request_id}/it/reject", response_model=AssetRequestResponse)
async def it_reject_request(
    request_id: UUID,
    rejection: ITRejectionRequest,
    db: AsyncSession = Depends(get_db)
):
    reviewer = await verify_it_management(rejection.reviewer_id, db)
    try:
        res = await asset_request_service.update_it_review_status(
            db, request_id, "IT_REJECTED", reviewer.id, reviewer.full_name, "IT_REJECTED", reason=rejection.reason
        )
        if not res:
            raise HTTPException(status_code=404, detail="Asset request not found")
        return res
    except HTTPException:
        # Re-raise HTTPException as-is (don't wrap it)
        raise
    except ValueError as e:
        # Handle state transition validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle any other unexpected errors
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ---------------- BYOD REGISTRATION ROUTE ----------------

@router.post("/{id}/byod/register", response_model=AssetRequestResponse)
async def byod_register_device(
    id: UUID,
    payload: ByodRegisterRequest,
    reviewer_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    reviewer = await verify_it_management(reviewer_id, db)
    res = await asset_request_service.register_byod_device_service(
        db, id, reviewer.id, reviewer.full_name, payload.device_model, payload.os_version, payload.serial_number
    )
    if not res:
        raise HTTPException(status_code=403, detail="Invalid request state for BYOD")
    return res


# ---------------- COMPANY-OWNED FULFILLMENT ROUTE ----------------

async def verify_asset_inventory_manager(user_id: UUID, db: AsyncSession) -> User:
    user = await asset_request_service.get_user_by_id_db(db, user_id)
    if not user or user.role not in ["ASSET_INVENTORY_MANAGER", "ASSET_MANAGER"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return user


@router.post("/{id}/company-owned/fulfill", response_model=AssetRequestResponse)
async def fulfill_company_owned_request(
    id: UUID,
    inventory_manager_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    await verify_asset_inventory_manager(inventory_manager_id, db)
    db_request = await asset_request_service.get_asset_request_by_id_db(db, id)
    if not db_request or db_request.status != "IT_APPROVED":
        raise HTTPException(status_code=403, detail="Not IT_APPROVED")

    # Try inventory
    res_asset = await db.execute(select(Asset).filter(
        Asset.type == db_request.asset_type,
        Asset.status == "In Stock"
    ))
    candidate_asset = res_asset.scalars().first()

    if candidate_asset:
        await asset_service.assign_asset(db, candidate_asset.id, db_request.requester_id, candidate_asset.location, date.today())
        db_request.status = "IN_USE"
        db_request.asset_id = candidate_asset.id
        await db.commit()
        return await asset_request_service._populate_requester_info(db, db_request)

    # Procurement fallback
    db_request.status = "PROCUREMENT_REQUESTED"
    pr = PurchaseRequest(
        id=_uuid.uuid4(),
        asset_request_id=db_request.id,
        requester_id=db_request.requester_id,
        asset_name=db_request.asset_name,
        status="Requested"
    )
    db.add(pr)
    await db.commit()
    return await asset_request_service._populate_requester_info(db, db_request)


# ---------------- PROCUREMENT & FINANCE ----------------

async def verify_procurement_finance(user_id: UUID, db: AsyncSession) -> User:
    user = await asset_request_service.get_user_by_id_db(db, user_id)
    if not user or user.role not in ["PROCUREMENT_FINANCE", "FINANCE"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return user

@router.post("/{id}/procurement/approve", response_model=AssetRequestResponse)
async def procurement_approve_request(id: UUID, approval: ProcurementApprovalRequest, db: AsyncSession = Depends(get_db)):
    reviewer = await verify_procurement_finance(approval.reviewer_id, db)
    res = await asset_request_service.update_procurement_finance_status(db, id, "PROCUREMENT_APPROVED", reviewer.id, reviewer.full_name)
    if not res:
        raise HTTPException(status_code=404, detail="Asset request not found")
    return res

@router.post("/{id}/procurement/reject", response_model=AssetRequestResponse)
async def procurement_reject_request(id: UUID, rejection: ProcurementRejectionRequest, db: AsyncSession = Depends(get_db)):
    reviewer = await verify_procurement_finance(rejection.reviewer_id, db)
    res = await asset_request_service.update_procurement_finance_status(db, id, "PROCUREMENT_REJECTED", reviewer.id, reviewer.full_name, reason=rejection.reason)
    if not res:
        raise HTTPException(status_code=404, detail="Asset request not found")
    return res

@router.post("/{id}/procurement/confirm-delivery", response_model=AssetRequestResponse)
async def procurement_confirm_delivery(id: UUID, reviewer_id: UUID, db: AsyncSession = Depends(get_db)):
    await verify_procurement_finance(reviewer_id, db)
    db_request = await asset_request_service.get_asset_request_by_id_db(db, id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Asset request not found")
        
    db_request.status = "QC_PENDING"
    
    # Automated Asset Onboarding: Create Asset record in 'In Stock' state
    po_result = await db.execute(select(PurchaseOrder).filter(PurchaseOrder.asset_request_id == id))
    po = po_result.scalars().first()
    
    # Use PO info for name if it's not the generic placeholder
    asset_name = db_request.asset_name
    if po and po.product_details and "Generated from PDF" not in po.product_details:
        asset_name = po.product_details

    new_asset = Asset(
        id=_uuid.uuid4(),
        name=asset_name,
        type=db_request.asset_type,
        model=db_request.asset_model or "Standard",
        vendor=db_request.asset_vendor or (po.vendor_name if po else "Commercial"),
        serial_number=f"PENDING-{str(_uuid.uuid4())[:8].upper()}",
        status="In Stock",
        location="IT Warehouse",
        cost=po.total_cost if po else (db_request.cost_estimate or 0.0),
        segment="IT"
    )
    db.add(new_asset)
    db_request.asset_id = new_asset.id
    
    # Also add to asset.asset_inventory for the stock dashboard
    inventory_item = AssetInventory(
        id=_uuid.uuid4(),
        asset_id=new_asset.id,
        location=new_asset.location,
        status="Available"
    )
    db.add(inventory_item)
    
    await db.commit()
    return await asset_request_service._populate_requester_info(db, db_request)

# ---------------- QC & USER ACCEPTANCE ----------------

@router.post("/{id}/qc/perform", response_model=AssetRequestResponse)
async def perform_qc(id: UUID, qc_request: QCPerformRequest, db: AsyncSession = Depends(get_db)):
    mgr = await verify_asset_inventory_manager(qc_request.qc_performer_id, db)
    res = await asset_request_service.perform_qc_check(db, id, qc_request.qc_status, mgr.id, mgr.full_name, qc_request.qc_notes)
    if not res:
        raise HTTPException(status_code=404, detail="Asset request not found")
    return res

@router.post("/{id}/user/accept", response_model=AssetRequestResponse)
async def user_accept_asset(id: UUID, acceptance: UserAcceptanceRequest, db: AsyncSession = Depends(get_db)):
    await verify_active_end_user(acceptance.user_id, db)
    res = await asset_request_service.update_user_acceptance(db, id, acceptance.user_id, "ACCEPTED")
    if not res:
        raise HTTPException(status_code=404, detail="Asset request not found")
    return res

@router.post("/{request_id}/inventory/allocate", response_model=AssetRequestResponse)
async def inventory_allocate_asset(request_id: UUID, asset_id: UUID, inventory_manager_id: UUID, db: AsyncSession = Depends(get_db)):
    await verify_asset_inventory_manager(inventory_manager_id, db)
    db_request = await asset_request_service.get_asset_request_by_id_db(db, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Asset request not found")
    asset_res = await db.execute(select(Asset).filter(Asset.id == asset_id))
    asset = asset_res.scalars().first()
    if asset:
        user = await asset_request_service.get_user_by_id_db(db, db_request.requester_id)
        asset.assigned_to = user.full_name
        asset.status = "Active"
        db_request.status = "FULFILLED"
        db_request.asset_id = asset_id
        await db.commit()
    return await asset_request_service._populate_requester_info(db, db_request)

@router.post("/{request_id}/inventory/not-available", response_model=AssetRequestResponse)
async def inventory_mark_not_available(request_id: UUID, inventory_manager_id: UUID, db: AsyncSession = Depends(get_db)):
    await verify_asset_inventory_manager(inventory_manager_id, db)
    db_request = await asset_request_service.get_asset_request_by_id_db(db, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Asset request not found")
    db_request.status = "PROCUREMENT_REQUESTED"
    await db.commit()
    return await asset_request_service._populate_requester_info(db, db_request)
