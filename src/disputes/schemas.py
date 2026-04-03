from pydantic import BaseModel, ConfigDict
from uuid import UUID

class DisputeCreate(BaseModel):
    transaction_id: UUID
    reason: str

class DisputeResponse(BaseModel):
    id: UUID
    transaction_id: UUID
    status: str
    reason: str
    
    model_config = ConfigDict(from_attributes=True)
