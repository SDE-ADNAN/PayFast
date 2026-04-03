from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any
import uuid
import logging

from src.database import get_db_session
from src.auth.dependencies import require_role
from src.models import Account

router = APIRouter(prefix="/admin", tags=["admin"])
audit_logger = logging.getLogger("audit")

@router.get("/dashboard")
async def get_dashboard_metrics(
    session: AsyncSession = Depends(get_db_session),
    payload: dict[str, Any] = Depends(require_role("admin"))
) -> dict[str, Any]:
    
    # 1. Daily Volume
    vol_stmt = text("""
        SELECT COALESCE(SUM(amount_paise), 0)
        FROM transactions 
        WHERE DATE(created_at) = CURRENT_DATE 
        AND status = 'COMPLETED'
    """)
    vol_res = await session.execute(vol_stmt)
    daily_volume = vol_res.scalar() or 0
    
    # 2. Failure Rate
    fail_stmt = text("""
        SELECT 
            COALESCE(COUNT(CASE WHEN status = 'FAILED' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 0.0)
        FROM transactions
        WHERE DATE(created_at) = CURRENT_DATE
    """)
    fail_res = await session.execute(fail_stmt)
    failure_rate = fail_res.scalar() or 0.0
    
    # 3. Active Users
    users_stmt = text("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
    users_res = await session.execute(users_stmt)
    active_users = users_res.scalar() or 0
    
    return {
        "daily_volume_paise": int(daily_volume),
        "daily_failure_rate_percentage": round(float(failure_rate), 2),
        "total_active_users": int(active_users)
    }

@router.post("/accounts/{account_id}/toggle-freeze")
async def toggle_account_freeze(
    account_id: str,
    session: AsyncSession = Depends(get_db_session),
    payload: dict[str, Any] = Depends(require_role("admin"))
) -> dict[str, str]:
    account = await session.get(Account, uuid.UUID(account_id))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    async with session.begin():
        new_status = "active" if account.status == "frozen" else "frozen" # type: ignore
        account.status = new_status # type: ignore
        
        audit_logger.info(f"Admin {payload.get('sub')} changed account {account_id} status to {new_status}")
        
    return {"account_id": account_id, "new_status": new_status}
