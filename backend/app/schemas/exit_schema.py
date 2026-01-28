from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

class ExitRequestResponse(BaseModel):
    id: str
    user_id: str
    status: str
    assets_snapshot: Optional[List[Any]] = None
    byod_snapshot: Optional[List[Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)