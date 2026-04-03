import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
import redis.asyncio as aioredis
from fastapi import HTTPException
import string
import random

from src.models import Transaction, Account, UpiId
from src.ledger.services import post_double_entry
from src.exceptions import InsufficientFundsError, AccountFrozenError, ConcurrentModificationError
from src.fraud.rules import evaluate_transaction_risk

DAILY_LIMIT_PAISE = 1_00_000 * 100 # ₹1 Lakh

def generate_reference_number() -> str:
    # 12 digit UTR-style reference
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"{date_str}{random_str}"

async def check_and_reserve_daily_limit(session: AsyncSession, account_id: uuid.UUID, amount_paise: int) -> None:
    """Checks daily velocity limits based on transaction sum for current day"""
    stmt = text("""
        SELECT SUM(amount_paise) 
        FROM transactions 
        WHERE source_account_id = :account_id
        AND DATE(created_at) = CURRENT_DATE
        AND status IN ('COMPLETED', 'PENDING')
    """)
    result = await session.execute(stmt, {"account_id": str(account_id)})
    current_spent = result.scalar() or 0
    if current_spent + amount_paise > DAILY_LIMIT_PAISE:
        raise HTTPException(
            status_code=400, 
            detail=f"Daily limit of ₹{DAILY_LIMIT_PAISE/100} exceeded."
        )

async def execute_transfer(
    session: AsyncSession,
    redis: aioredis.Redis,
    user_id: str,
    from_account_id: uuid.UUID,
    to_account_id: uuid.UUID,
    amount_paise: int,
    notes: str | None = None
) -> Transaction:
    # Distributed lock per user to throttle massive fan-out abuse
    lock_key = f"lock:transfer:{user_id}"
    lock_acquired = await redis.set(lock_key, "locked", nx=True, px=2000)
    if not lock_acquired:
         raise HTTPException(status_code=429, detail="Concurrent transfer in progress, please wait")
         
    try:
        # Check Daily Limits safely outside the massive pessimistic lock
        # Evaluate Fraud Signatures
        risk_score = await evaluate_transaction_risk(session, from_account_id, amount_paise)
        if risk_score >= 80:
            async with session.begin():
                account_to_freeze = await session.get(Account, from_account_id)
                if account_to_freeze:
                    account_to_freeze.status = "frozen" # type: ignore
            raise HTTPException(
                status_code=403, 
                detail="Transaction declined due to suspicious activity. Account has been securely frozen."
            )
            
        async with session.begin():
            # Setup Transaction
            tx = Transaction(
                source_account_id=from_account_id,
                destination_account_id=to_account_id,
                amount_paise=amount_paise,
                transaction_type="P2P",
                status="PENDING",
                reference_number=generate_reference_number(),
                metadata={"notes": notes}
            )
            session.add(tx)
            await session.flush() # get ID
            
            # Post Double Entry
            try:
                await post_double_entry(
                    session=session,
                    transaction=tx,
                    from_account_id=from_account_id,
                    to_account_id=to_account_id,
                    amount_paise=amount_paise
                )
                tx.status = "COMPLETED" # type: ignore
            except (InsufficientFundsError, AccountFrozenError) as e:
                tx.status = "FAILED" # type: ignore
                # Log the natural domain failure
                raise HTTPException(status_code=400, detail=str(e))
            except ConcurrentModificationError:
                tx.status = "FAILED" # type: ignore
                raise HTTPException(status_code=409, detail="Transaction conflict. Please retry.")
            except Exception as e:
                tx.status = "FAILED" # type: ignore
                raise HTTPException(status_code=500, detail="Internal processing error")
            
            return tx
    finally:
        await redis.delete(lock_key)
