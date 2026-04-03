from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
import uuid

from src.models import Dispute, Transaction
from src.ledger.services import post_double_entry
from src.exceptions import InsufficientFundsError, AccountFrozenError

async def resolve_dispute(session: AsyncSession, dispute_id: uuid.UUID) -> None:
    result = await session.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
        
    if dispute.status == "resolved":
        raise HTTPException(status_code=400, detail="Dispute is already resolved")
        
    tx_res = await session.execute(select(Transaction).where(Transaction.id == dispute.transaction_id))
    tx = tx_res.scalar_one_or_none()
    
    if not tx or not tx.destination_account_id or not tx.source_account_id:
        raise HTTPException(status_code=404, detail="Original transaction missing or invalid for refund")
        
    # Process Refund by reversing the flow direction
    try:
        async with session.begin():
            refund_tx = Transaction(
                source_account_id=tx.destination_account_id,
                destination_account_id=tx.source_account_id,
                amount_paise=tx.amount_paise,
                transaction_type="REFUND",
                status="COMPLETED",
                reference_number=f"REF-{tx.reference_number}"
            )
            session.add(refund_tx)
            await session.flush()
            
            await post_double_entry(
                session=session,
                transaction=refund_tx,
                from_account_id=tx.destination_account_id, # Target is now the source of funds
                to_account_id=tx.source_account_id,
                amount_paise=int(tx.amount_paise) # type: ignore
            )
            
            upd_dispute = await session.get(Dispute, dispute.id)
            upd_dispute.status = "resolved" # type: ignore
            
    except (InsufficientFundsError, AccountFrozenError) as e:
        raise HTTPException(status_code=400, detail=f"Refund failed: {e}")
    except Exception:
        raise HTTPException(status_code=500, detail="Unknown error resolving dispute")
