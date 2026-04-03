from pydantic import BaseModel, Field
from uuid import UUID

class TransferRequest(BaseModel):
    to_vpa: str | None = None
    to_account_id: UUID | None = None
    amount_paise: int = Field(gt=0, description="Amount must be positive")
    notes: str | None = None
    
class TransferResponse(BaseModel):
    transaction_id: UUID
    reference_number: str
    status: str
    amount_paise: int
    created_at: str
    
class CollectRequest(BaseModel):
    from_vpa: str
    amount_paise: int = Field(gt=0)
    notes: str | None = None
    
class CollectResponse(BaseModel):
    request_id: UUID
    status: str
    amount_paise: int
    expires_at: str
