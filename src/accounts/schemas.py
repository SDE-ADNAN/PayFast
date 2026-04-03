from pydantic import BaseModel, ConfigDict
from typing import Any
from datetime import datetime

class AccountResponse(BaseModel):
    id: str
    account_number: str
    account_type: str
    balance_paise: int
    balance_formatted: str
    currency: str
    status: str
    created_at: datetime
    
    @staticmethod
    def construct_from_orm(obj: Any) -> 'AccountResponse':
        return AccountResponse(
            id=str(obj.id),
            account_number=obj.account_number,
            account_type=obj.account_type,
            balance_paise=obj.balance_paise,
            balance_formatted=f"₹{obj.balance_paise / 100:.2f}",
            currency=obj.currency,
            status=obj.status,
            created_at=obj.created_at
        )

class AccountStatusUpdate(BaseModel):
    status: str # 'active', 'frozen', 'closed'
