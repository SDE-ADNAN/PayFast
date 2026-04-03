import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db_session
from src.models import Account
from src.auth.dependencies import get_current_user_token_payload, require_role
from src.accounts.schemas import AccountResponse, AccountStatusUpdate

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("", response_model=list[AccountResponse])
async def get_user_accounts(
    session: AsyncSession = Depends(get_db_session),
    payload: dict[str, Any] = Depends(get_current_user_token_payload)
) -> list[AccountResponse]:
    user_id = str(payload.get("sub"))
    result = await session.execute(
        select(Account).where(Account.user_id == uuid.UUID(user_id))
    )
    accounts = result.scalars().all()
    return [AccountResponse.construct_from_orm(a) for a in accounts]

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    session: AsyncSession = Depends(get_db_session),
    payload: dict[str, Any] = Depends(get_current_user_token_payload)
) -> AccountResponse:
    user_id = str(payload.get("sub"))
    result = await session.execute(
        select(Account).where(Account.id == uuid.UUID(account_id))
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    if str(account.user_id) != user_id and payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this account")
        
    return AccountResponse.construct_from_orm(account)

@router.patch("/{account_id}/status", response_model=AccountResponse)
async def update_account_status(
    account_id: str,
    update: AccountStatusUpdate,
    session: AsyncSession = Depends(get_db_session),
    payload: dict[str, Any] = Depends(require_role("admin"))
) -> AccountResponse:
    result = await session.execute(
        select(Account).where(Account.id == uuid.UUID(account_id))
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    if update.status not in ("active", "frozen", "closed"):
        raise HTTPException(status_code=400, detail="Invalid status")
        
    account.status = update.status # type: ignore
    session.add(account)
    await session.commit()
    
    return AccountResponse.construct_from_orm(account)
