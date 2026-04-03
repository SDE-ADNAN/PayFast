import uuid
from typing import Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis

from src.database import get_db_session
from src.redis_client import get_redis
from src.models import Account, UpiId, PaymentRequest
from src.auth.dependencies import get_current_user_token_payload
from src.payments.schemas import TransferRequest, TransferResponse, CollectRequest, CollectResponse
from src.payments.services import execute_transfer

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/transfer", response_model=TransferResponse)
async def p2p_transfer(
    req: TransferRequest,
    session: AsyncSession = Depends(get_db_session),
    redis: aioredis.Redis = Depends(get_redis),
    payload: dict[str, Any] = Depends(get_current_user_token_payload)
) -> TransferResponse:
    user_id = str(payload.get("sub"))
    
    # Needs a context lookup for sender account if multiple exist, but assume primary for now
    sender_account_stmt = select(Account).where(Account.user_id == uuid.UUID(user_id))
    result = await session.execute(sender_account_stmt)
    sender_account = result.scalars().first()
    if not sender_account:
        raise HTTPException(status_code=400, detail="Sender account not found")
        
    destination_account_id = req.to_account_id
    if req.to_vpa:
        # Resolve VPA
        vpa_result = await session.execute(select(UpiId).where(UpiId.vpa == req.to_vpa))
        upi_rec = vpa_result.scalar_one_or_none()
        if not upi_rec:
            raise HTTPException(status_code=404, detail="Destination VPA not found")
        destination_account_id = upi_rec.account_id
        
    if not destination_account_id:
        raise HTTPException(status_code=400, detail="Must provide to_vpa or to_account_id")
        
    tx = await execute_transfer(
        session=session,
        redis=redis,
        user_id=user_id,
        from_account_id=sender_account.id, # type: ignore
        to_account_id=destination_account_id,
        amount_paise=req.amount_paise,
        notes=req.notes
    )
    
    return TransferResponse(
        transaction_id=tx.id, # type: ignore
        reference_number=str(tx.reference_number),
        status=str(tx.status),
        amount_paise=int(tx.amount_paise), # type: ignore
        created_at=str(tx.created_at)
    )

@router.post("/collect/request", response_model=CollectResponse)
async def request_collect(
    req: CollectRequest,
    session: AsyncSession = Depends(get_db_session),
    payload: dict[str, Any] = Depends(get_current_user_token_payload)
) -> CollectResponse:
    user_id = uuid.UUID(str(payload.get("sub")))
    
    # Validate target VPA exists
    vpa_result = await session.execute(select(UpiId).where(UpiId.vpa == req.from_vpa))
    payer_upi = vpa_result.scalar_one_or_none()
    if not payer_upi:
        raise HTTPException(status_code=404, detail="Target VPA not found")
        
    # Get requestor VPA 
    req_vpa_res = await session.execute(select(UpiId).where(UpiId.user_id == user_id))
    requestor_upi = req_vpa_res.scalar_one_or_none()
    if not requestor_upi:
        raise HTTPException(status_code=400, detail="You do not have a VPA to receive funds")
        
    # Expiry 15 mins
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    async with session.begin():
        pr = PaymentRequest(
            requester_user_id=user_id,
            payer_user_id=payer_upi.user_id,
            amount_paise=req.amount_paise,
            status="PENDING",
            expires_at=expires,
            metadata={"notes": req.notes, "vpa": req.from_vpa}
        )
        session.add(pr)
    
    # TODO: Phase 4 WebSockets - Push to `payer_user_id` channel
    # TODO: Phase 4 Celery - Submit delayed task to mark EXPIRED if not actioned
    
    return CollectResponse(
        request_id=pr.id, # type: ignore
        status=str(pr.status),
        amount_paise=int(pr.amount_paise), # type: ignore
        expires_at=str(pr.expires_at)
    )

@router.post("/collect/{request_id}/approve")
async def approve_collect(
    request_id: str,
    session: AsyncSession = Depends(get_db_session),
    redis: aioredis.Redis = Depends(get_redis),
    payload: dict[str, Any] = Depends(get_current_user_token_payload)
) -> TransferResponse:
    user_id = str(payload.get("sub"))
    
    result = await session.execute(select(PaymentRequest).where(PaymentRequest.id == uuid.UUID(request_id)))
    pr = result.scalar_one_or_none()
    
    if not pr:
        raise HTTPException(status_code=404, detail="Payment request not found")
        
    if str(pr.payer_user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to approve this request")
        
    if pr.status != "PENDING" or (pr.expires_at and pr.expires_at < datetime.now(timezone.utc)): # type: ignore
        raise HTTPException(status_code=400, detail="Request is expired or inactive")
        
    payer_acc_res = await session.execute(select(Account).where(Account.user_id == uuid.UUID(user_id)))
    payer_account = payer_acc_res.scalars().first()
    
    requester_acc_res = await session.execute(select(Account).where(Account.user_id == pr.requester_user_id))
    req_account = requester_acc_res.scalars().first()
    
    if not payer_account or not req_account:
        raise HTTPException(status_code=500, detail="Account resolution failed")
        
    # Execute Transfer
    tx = await execute_transfer(
        session=session,
        redis=redis,
        user_id=user_id,
        from_account_id=payer_account.id, # type: ignore
        to_account_id=req_account.id, # type: ignore
        amount_paise=int(pr.amount_paise), # type: ignore
        notes=f"Collect Request {pr.id}"
    )
    
    # Mark Collect Request
    async with session.begin():
        pr_update = await session.get(PaymentRequest, pr.id)
        pr_update.status = "APPROVED" # type: ignore
        
    return TransferResponse(
        transaction_id=tx.id, # type: ignore
        reference_number=str(tx.reference_number),
        status=str(tx.status),
        amount_paise=int(tx.amount_paise), # type: ignore
        created_at=str(tx.created_at)
    )
