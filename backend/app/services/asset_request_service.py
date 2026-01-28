"""
Asset Request service layer - Database operations for asset requests (Asynchronous)
"""
import uuid
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from ..models.models import AssetRequest, User, PurchaseOrder, PurchaseInvoice, ProcurementLog
from ..schemas.asset_request_schema import AssetRequestCreate, AssetRequestUpdate, AssetRequestResponse
from ..services import procurement_service
from ..utils.state_machine import validate_state_transition


async def _populate_requester_info(db: AsyncSession, db_request: AssetRequest, user_role: str = None) -> AssetRequestResponse:
    """Helper to add requester name/email and procurement info (role-sensitive)"""
    # Ensure attributes are loaded after a commit and not expired
    await db.refresh(db_request)
    
    result = await db.execute(select(User).filter(User.id == db_request.requester_id))
    user = result.scalars().first()
    
    res = AssetRequestResponse.model_validate(db_request)
    if user:
        res.requester_name = user.full_name
        res.requester_email = user.email
    
    # Step 6: Role-Based Visibility (Backend Enforced)
    if user_role in ["PROCUREMENT_FINANCE", "FINANCE", "ADMIN"]:
        # Fetch current PO
        po_query = select(PurchaseOrder).filter(PurchaseOrder.asset_request_id == db_request.id).order_by(desc(PurchaseOrder.created_at))
        po_result = await db.execute(po_query)
        po = po_result.scalars().first()
        
        if po:
            res.purchase_order = {
                "id": po.id,
                "vendor_name": po.vendor_name,
                "total_cost": po.total_cost,
                "status": po.status,
                "po_pdf_path": po.po_pdf_path,
                "extracted_data": po.extracted_data
            }
            
            # Fetch Invoice linked to this PO
            inv_query = select(PurchaseInvoice).filter(PurchaseInvoice.purchase_order_id == po.id)
            inv_result = await db.execute(inv_query)
            invoice = inv_result.scalars().first()
            
            if invoice:
                res.purchase_invoice = {
                    "purchase_date": invoice.purchase_date.isoformat() if invoice.purchase_date else None,
                    "total_amount": invoice.total_amount,
                    "invoice_pdf_path": invoice.invoice_pdf_path
                }
        
        # Fetch detailed procurement logs
        logs_query = select(ProcurementLog).filter(ProcurementLog.reference_id == db_request.id).order_by(desc(ProcurementLog.created_at))
        logs_result = await db.execute(logs_query)
        logs = logs_result.scalars().all()
        
        res.procurement_logs = [
            {"action": l.action, "performed_by": l.performed_by, "timestamp": l.created_at.isoformat(), "metadata": l.metadata_} 
            for l in logs
        ]
        
    elif user_role == "IT_MANAGEMENT":
        po_query = select(PurchaseOrder).filter(PurchaseOrder.asset_request_id == db_request.id)
        po_result = await db.execute(po_query)
        po = po_result.scalars().first()
        if po:
            res.purchase_order = {
                "status": po.status,
                "vendor_name": po.vendor_name
            }
            
    return res


async def get_asset_request_by_id(db: AsyncSession, request_id: UUID, user_role: str = None) -> Optional[AssetRequestResponse]:
    """
    Get an asset request by ID
    """
    result = await db.execute(select(AssetRequest).filter(AssetRequest.id == request_id))
    request = result.scalars().first()
    if request:
        return await _populate_requester_info(db, request, user_role=user_role)
    return None


async def get_asset_request_by_id_db(db: AsyncSession, request_id: UUID) -> Optional[AssetRequest]:
    """
    Get an asset request by ID (returns DB model, not response)
    """
    result = await db.execute(select(AssetRequest).filter(AssetRequest.id == request_id))
    return result.scalars().first()


async def get_user_by_id_db(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Get a user by ID (returns DB model, not response)
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def create_asset_request(db: AsyncSession, request: AssetRequestCreate, initial_status: str = "SUBMITTED") -> AssetRequestResponse:
    """
    Create a new asset request
    """
    db_request = AssetRequest(
        id=uuid.uuid4(),
        requester_id=request.requester_id,
        asset_id=request.asset_id,
        asset_name=request.asset_name,
        asset_type=request.asset_type,
        asset_ownership_type=request.asset_ownership_type,
        asset_model=request.asset_model,
        asset_vendor=request.asset_vendor,
        serial_number=request.serial_number,
        os_version=request.os_version,
        cost_estimate=request.cost_estimate,
        justification=request.justification,
        business_justification=request.business_justification,
        status=initial_status,
        manager_approvals=[]
    )
    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)
    return await _populate_requester_info(db, db_request)


async def update_asset_request_status_with_validation(
    db: AsyncSession,
    request_id: UUID,
    new_status: str,
    user_role: str,
    reviewer_id: Optional[UUID] = None,
    reviewer_name: Optional[str] = None,
    reason: Optional[str] = None,
    decision: Optional[str] = None
) -> Optional[AssetRequestResponse]:
    """
    Update asset request status with state machine validation
    """
    result = await db.execute(select(AssetRequest).filter(AssetRequest.id == request_id))
    db_request = result.scalars().first()
    if not db_request:
        return None
    
    # Validate state transition
    is_valid, error_msg = validate_state_transition(
        current_status=db_request.status,
        new_status=new_status,
        user_role=user_role,
        asset_ownership_type=db_request.asset_ownership_type
    )
    
    if not is_valid:
        raise ValueError(error_msg)
    
    # Update status
    db_request.status = new_status
    db_request.updated_at = datetime.now()
    
    # Record reviewer info
    if reviewer_id:
        if db_request.manager_approvals is None:
            db_request.manager_approvals = []
        db_request.manager_approvals.append({
            "reviewer_id": reviewer_id,
            "reviewer_name": reviewer_name or reviewer_id,
            "decision": new_status,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "type": "STATUS_CHANGE"
        })
    
    await db.commit()
    await db.refresh(db_request)
    return await _populate_requester_info(db, db_request, user_role=user_role)


async def update_it_review_status(
    db: AsyncSession,
    request_id: UUID,
    new_status: str,
    reviewer_id: UUID,
    reviewer_name: str,
    decision: str,
    reason: Optional[str] = None
) -> Optional[AssetRequestResponse]:
    """
    Update IT review status
    """
    print(f"[DEBUG] update_it_review_status: Looking for request_id={request_id}, new_status={new_status}")
    result = await db.execute(select(AssetRequest).filter(AssetRequest.id == request_id))
    db_request = result.scalars().first()
    if not db_request:
        print(f"[DEBUG] update_it_review_status: Request {request_id} not found in database")
        return None
    print(f"[DEBUG] update_it_review_status: Found request {request_id} with status={db_request.status}")

    is_valid, error_msg = validate_state_transition(
        current_status=db_request.status,
        new_status=new_status,
        user_role="IT_MANAGEMENT",
        asset_ownership_type=db_request.asset_ownership_type
    )
    
    if not is_valid:
        raise ValueError(error_msg)

    db_request.status = new_status
    db_request.it_reviewed_by = reviewer_id
    db_request.it_reviewed_at = datetime.now()

    if db_request.manager_approvals is None:
        db_request.manager_approvals = []
    db_request.manager_approvals.append({
        "reviewer_id": str(reviewer_id),
        "reviewer_name": reviewer_name,
        "decision": decision,
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
        "type": "IT_REVIEW",
    })

    await db.commit()
    await db.refresh(db_request)
    return await _populate_requester_info(db, db_request, user_role="IT_MANAGEMENT")


async def update_procurement_finance_status(
    db: AsyncSession,
    request_id: UUID,
    new_status: str,
    reviewer_id: UUID,
    reviewer_name: str,
    reason: Optional[str] = None
) -> Optional[AssetRequestResponse]:
    """
    Update procurement & finance approval status.
    """
    result = await db.execute(select(AssetRequest).filter(AssetRequest.id == request_id))
    db_request = result.scalars().first()
    if not db_request:
        return None
    
    if db_request.status == "PROCUREMENT_APPROVED" and new_status != "PROCUREMENT_REJECTED":
        return await _populate_requester_info(db, db_request, user_role="PROCUREMENT_FINANCE")

    is_valid, error_msg = validate_state_transition(
        current_status=db_request.status,
        new_status=new_status,
        user_role="PROCUREMENT_FINANCE",
        asset_ownership_type=db_request.asset_ownership_type
    )
    
    if not is_valid:
        raise ValueError(error_msg)
    
    po_query = select(PurchaseOrder).filter(PurchaseOrder.asset_request_id == request_id).order_by(desc(PurchaseOrder.created_at))
    po_result = await db.execute(po_query)
    po = po_result.scalars().first()

    if new_status == "PROCUREMENT_APPROVED":
        if po:
            await procurement_service.validate_finance_budget(
                db=db, 
                po_id=po.id, 
                reviewer_id=reviewer_id, 
                role="FINANCE", 
                action="APPROVE",
                reason=reason
            )
    elif new_status == "PROCUREMENT_REJECTED":
        if po:
            await procurement_service.validate_finance_budget(
                db=db, 
                po_id=po.id, 
                reviewer_id=reviewer_id, 
                role="FINANCE", 
                action="REJECT",
                reason=reason
            )

    db_request.status = new_status
    db_request.procurement_finance_status = "APPROVED" if new_status == "PROCUREMENT_APPROVED" else "REJECTED"
    db_request.procurement_finance_reviewed_by = reviewer_id
    db_request.procurement_finance_reviewed_at = datetime.now()
    if reason:
        db_request.procurement_finance_rejection_reason = reason
    
    if db_request.manager_approvals is None:
        db_request.manager_approvals = []
    db_request.manager_approvals.append({
        "reviewer_id": str(reviewer_id),
        "reviewer_name": reviewer_name,
        "decision": new_status,
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
        "type": "PROCUREMENT_FINANCE_REVIEW"
    })
    
    log = ProcurementLog(
        id=uuid.uuid4(),
        reference_id=request_id,
        action="PO_APPROVED" if new_status == "PROCUREMENT_APPROVED" else "PO_REJECTED",
        performed_by=reviewer_id,
        role="PROCUREMENT_FINANCE",
        metadata_={"reviewer_name": reviewer_name, "decision": new_status, "reason": reason}
    )
    db.add(log)
    
    await db.commit()
    await db.refresh(db_request)
    return await _populate_requester_info(db, db_request, user_role="PROCUREMENT_FINANCE")


async def perform_qc_check(
    db: AsyncSession,
    request_id: UUID,
    qc_status: str,
    performer_id: UUID,
    performer_name: str,
    qc_notes: Optional[str] = None
) -> Optional[AssetRequestResponse]:
    """
    Perform quality check on received asset
    """
    result = await db.execute(select(AssetRequest).filter(AssetRequest.id == request_id))
    db_request = result.scalars().first()
    if not db_request:
        return None
    
    if db_request.status != "QC_PENDING":
        raise ValueError(f"QC can only be performed when status is QC_PENDING. Current status: {db_request.status}")
    
    if qc_status not in ["PASSED", "FAILED"]:
        raise ValueError("qc_status must be PASSED or FAILED")
    
    db_request.qc_status = qc_status
    db_request.qc_performed_by = performer_id
    db_request.qc_performed_at = datetime.now()
    db_request.qc_notes = qc_notes
    
    if qc_status == "PASSED":
        db_request.status = "USER_ACCEPTANCE_PENDING"
    else:
        db_request.status = "QC_FAILED"
    
    if db_request.manager_approvals is None:
        db_request.manager_approvals = []
    db_request.manager_approvals.append({
        "reviewer_id": str(performer_id),
        "reviewer_name": performer_name,
        "decision": qc_status,
        "reason": qc_notes,
        "timestamp": datetime.now().isoformat(),
        "type": "QC_CHECK"
    })
    
    await db.commit()
    await db.refresh(db_request)
    return await _populate_requester_info(db, db_request)


async def update_user_acceptance(
    db: AsyncSession,
    request_id: UUID,
    user_id: UUID,
    acceptance_status: str
) -> Optional[AssetRequestResponse]:
    """
    Update user acceptance status
    """
    result = await db.execute(select(AssetRequest).filter(AssetRequest.id == request_id))
    db_request = result.scalars().first()
    if not db_request:
        return None
    
    if db_request.requester_id != user_id:
        raise ValueError("Only the requester can accept/reject the asset")
    
    if db_request.status != "USER_ACCEPTANCE_PENDING":
        raise ValueError(f"User acceptance can only be performed when status is USER_ACCEPTANCE_PENDING. Current status: {db_request.status}")
    
    if acceptance_status not in ["ACCEPTED", "REJECTED"]:
        raise ValueError("acceptance_status must be ACCEPTED or REJECTED")
    
    db_request.user_acceptance_status = acceptance_status
    db_request.user_accepted_at = datetime.now()
    
    if acceptance_status == "ACCEPTED":
        db_request.status = "IN_USE"
    else:
        db_request.status = "USER_REJECTED"
    
    if db_request.manager_approvals is None:
        db_request.manager_approvals = []
    db_request.manager_approvals.append({
        "reviewer_id": str(user_id),
        "reviewer_name": "END_USER",
        "decision": acceptance_status,
        "timestamp": datetime.now().isoformat(),
        "type": "USER_ACCEPTANCE"
    })
    
    await db.commit()
    await db.refresh(db_request)
    return await _populate_requester_info(db, db_request)


async def register_byod_device_service(
    db: AsyncSession,
    request_id: UUID,
    reviewer_id: UUID,
    reviewer_name: str,
    device_model: str,
    os_version: str,
    serial_number: str
) -> Optional[AssetRequestResponse]:
    """
    Service to register a BYOD device and update request status.
    """
    result = await db.execute(select(AssetRequest).filter(AssetRequest.id == request_id))
    db_request = result.scalars().first()
    if not db_request or db_request.status != "IT_APPROVED":
        return None

    # 1. Create BYOD entry
    from ..models.models import ByodDevice
    byod = ByodDevice(
        id=uuid.uuid4(),
        request_id=db_request.id,
        owner_id=db_request.requester_id,
        device_model=device_model,
        os_version=os_version,
        serial_number=serial_number,
        compliance_status="COMPLIANT",
    )
    db.add(byod)
    
    # 2. Update status
    db_request.status = "IN_USE"
    db_request.updated_at = datetime.now()
    
    # 3. Add to approvals log
    if db_request.manager_approvals is None:
        db_request.manager_approvals = []
    db_request.manager_approvals.append({
        "reviewer_id": str(reviewer_id),
        "reviewer_name": reviewer_name,
        "decision": "IN_USE",
        "timestamp": datetime.now().isoformat(),
        "type": "BYOD_REGISTRATION"
    })
    
    await db.commit()
    await db.refresh(db_request)
    return await _populate_requester_info(db, db_request)


async def get_all_asset_requests(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    requester_id: Optional[UUID] = None,
    domain: Optional[str] = None,
    user_role: Optional[str] = None
) -> List[AssetRequestResponse]:
    """
    Get all asset requests with optional filtering
    """
    print(f"DEBUG: Filtering requests - status={status}, requester_id={requester_id}, domain={domain}")
    
    query = select(AssetRequest)
    if status:
        query = query.filter(AssetRequest.status == status)
    if requester_id:
        query = query.filter(AssetRequest.requester_id == requester_id)
    if domain:
        query = query.join(User, AssetRequest.requester_id == User.id).filter(User.domain == domain)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    results = result.scalars().all()
    
    response_list = []
    for req in results:
        res = await _populate_requester_info(db, req, user_role=user_role)
        response_list.append(res)
        
    return response_list
