from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from ..models.models import PurchaseOrder, PurchaseInvoice, ProcurementLog, AssetRequest
from ..services import pdf_extraction_service
import asyncio
import os
import uuid
from uuid import UUID
from datetime import datetime

UPLOAD_DIR = "uploads/procurement"

def ensure_upload_dir():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)

async def handle_po_upload(db: AsyncSession, asset_request_id: UUID, uploader_id: UUID, file_path: str):
    """
    Handle PO PDF upload and automated extraction (Asynchronous).
    """
    # PDF extraction is CPU-bound/blocking. Offload it to a worker thread so we don't block the event loop.
    extracted = await asyncio.to_thread(pdf_extraction_service.extract_po_details, file_path)
    
    # Create PurchaseOrder record
    po = PurchaseOrder(
        id=uuid.uuid4(),
        asset_request_id=asset_request_id,
        uploaded_by=uploader_id,
        po_pdf_path=file_path,
        vendor_name=extracted.get("vendor_name"),
        total_cost=extracted.get("total_cost"),
        quantity=extracted.get("quantity"),
        unit_price=extracted.get("unit_price"),
        extracted_data=extracted,
        status="UPLOADED"
    )
    db.add(po)
    
    # Comprehensive Audit Log
    log = ProcurementLog(
        id=uuid.uuid4(),
        reference_id=po.id,
        action="PO_UPLOADED",
        performed_by=uploader_id,
        role="PROCUREMENT",
        metadata_={
            "asset_request_id": asset_request_id,
            "vendor": po.vendor_name,
            "total_cost": po.total_cost,
            "extracted_at": datetime.now().isoformat()
        }
    )
    db.add(log)
    
    # Update AssetRequest status
    result = await db.execute(select(AssetRequest).filter(AssetRequest.id == asset_request_id))
    request = result.scalars().first()
    if request:
        request.procurement_finance_status = "PO_UPLOADED"
    
    await db.commit()
    await db.refresh(po)
    return po

async def validate_finance_budget(db: AsyncSession, po_id: UUID, reviewer_id: UUID, role: str, action: str, reason: str = None):
    """
    Finance budget validation logic (Asynchronous).
    """
    result = await db.execute(select(PurchaseOrder).filter(PurchaseOrder.id == po_id))
    po = result.scalars().first()
    if not po:
        raise ValueError("Purchase Order not found")
        
    if po.status == "VALIDATED" and action != "REJECT":
        return po

    req_result = await db.execute(select(AssetRequest).filter(AssetRequest.id == po.asset_request_id))
    request = req_result.scalars().first()
    
    if action == "APPROVE":
        po.status = "VALIDATED"
        log_action = "PO_APPROVED"
    else:
        po.status = "REJECTED"
        log_action = "PO_REJECTED"
        
    # Immutability Trace
    log = ProcurementLog(
        id=uuid.uuid4(),
        reference_id=po.id,
        action=log_action,
        performed_by=reviewer_id,
        role=role,
        metadata_={
            "reason": reason,
            "po_total": po.total_cost,
            "request_estimate": request.cost_estimate if request else None,
            "budget_pass": po.total_cost <= (request.cost_estimate or 0) * 1.1 if request else True
        }
    )
    db.add(log)
    
    await db.commit()
    await db.refresh(po)
    return po

async def handle_invoice_upload(db: AsyncSession, po_id: UUID, uploader_id: UUID, file_path: str):
    """
    Handle Finance-uploaded purchase confirmation / invoice PDF (Asynchronous).
    """
    # PDF extraction is CPU-bound/blocking. Offload it to a worker thread so we don't block the event loop.
    extracted = await asyncio.to_thread(pdf_extraction_service.extract_invoice_details, file_path)
    
    # Create PurchaseInvoice record
    invoice = PurchaseInvoice(
        id=uuid.uuid4(),
        purchase_order_id=po_id,
        invoice_pdf_path=file_path,
        purchase_date=datetime.now(), 
        total_amount=extracted.get("total_cost"),
        created_by=uploader_id
    )
    db.add(invoice)
    
    # Log action
    log = ProcurementLog(
        id=uuid.uuid4(),
        reference_id=invoice.id,
        action="INVOICE_UPLOADED",
        performed_by=uploader_id,
        role="FINANCE",
        metadata_={
            "po_id": po_id,
            "final_cost": invoice.total_amount,
            "timestamp": datetime.now().isoformat()
        }
    )
    db.add(log)
    
    await db.commit()
    await db.refresh(invoice)
    return invoice

async def get_procurement_logs(db: AsyncSession, reference_id: UUID = None):
    """
    Retrieve audit logs for procurement (Asynchronous).
    """
    query = select(ProcurementLog)
    if reference_id:
        query = query.filter(ProcurementLog.reference_id == reference_id)
    query = query.order_by(desc(ProcurementLog.created_at))
    result = await db.execute(query)
    return result.scalars().all()
