from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid
import logging

logger = logging.getLogger(__name__)

async def evaluate_transaction_risk(
    session: AsyncSession, 
    account_id: uuid.UUID, 
    amount_paise: int
) -> int:
    """
    Evaluates transaction risk based on configurable rules.
    Returns a normalized risk score between 0 and 100.
    """
    score = 0
    
    # Rule 1: Large single transfer ( > ₹50,000 )
    if amount_paise > 50_000_00:
        score += 30
        
    # Rule 2: Velocity Check ( > 5 txns in the last minute )
    stmt = text("""
        SELECT COUNT(*) 
        FROM transactions 
        WHERE source_account_id = :account_id
        AND created_at >= NOW() - INTERVAL '1 minute'
    """)
    result = await session.execute(stmt, {"account_id": str(account_id)})
    tx_count_last_min = result.scalar() or 0
    
    if tx_count_last_min >= 5:
        score += 40
        
    # Standardize ceiling bound
    final_score = min(score, 100)
    
    logger.info(f"Risk Evaluation for account {account_id} | Amount: {amount_paise} | Score: {final_score}")
    return final_score
