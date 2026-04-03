from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime
from uuid import UUID

class TransactionResponse(BaseModel):
    id: UUID
    source_account_id: UUID | None
    destination_account_id: UUID | None
    amount_paise: int
    transaction_type: str
    status: str
    reference_number: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedTransactions(BaseModel):
    items: List[TransactionResponse]
    next_cursor: UUID | None
