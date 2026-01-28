"""
Add inventory allocation endpoint to asset_requests.py
"""

ENDPOINT_CODE = '''
@router.post("/{request_id}/inventory/allocate", response_model=AssetRequestResponse)
def inventory_allocate_asset(
    request_id: str,
    asset_id: str,
    inventory_manager_id: str,
    db: Session = Depends(get_db)
):
    """
    Inventory manager allocates an available asset to fulfill a request.
    Changes request status to FULFILLED.
    """
    # Get the asset request
    db_request = asset_request_service.get_asset_request_by_id_db(db, request_id)
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset request not found"
        )
    
    # Verify request is IT_APPROVED
    if db_request.status != "IT_APPROVED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Request must be IT_APPROVED. Current status: {db_request.status}"
        )
    
    # Verify asset exists
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset {asset_id} not found"
        )
    
    # Get requester info
    requester = asset_request_service.get_user_by_id_db(db, db_request.requester_id)
    if not requester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requester not found"
        )
    
    # Assign the asset
    asset.assigned_to = requester.full_name
    asset.assigned_by = inventory_manager_id
    asset.status = "Active"
    asset.assignment_date = date.today()
    
    # Update request status
    db_request.status = "FULFILLED"
    db_request.asset_id = asset_id
    
    db.commit()
    db.refresh(db_request)
    
    return AssetRequestResponse.model_validate(db_request)
'''

print(ENDPOINT_CODE)
