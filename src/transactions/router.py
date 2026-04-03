import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from src.database import get_db_session
from src.models import Transaction, Account
from src.auth.dependencies import get_current_user_token_payload
from src.transactions.schemas import PaginatedTransactions, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("", response_model=PaginatedTransactions)
async def get_history(
    limit: int = Query(20, le=100),
    cursor: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    payload: dict[str, Any] = Depends(get_current_user_token_payload)
) -> PaginatedTransactions:
    user_id = uuid.UUID(str(payload.get("sub")))
    
    acc_res = await session.execute(select(Account.id).where(Account.user_id == user_id))
    account_ids = acc_res.scalars().all()
    
    if not account_ids:
        return PaginatedTransactions(items=[], next_cursor=None)
        
    stmt = (
        select(Transaction)
        .where(or_(
            Transaction.source_account_id.in_(account_ids),
            Transaction.destination_account_id.in_(account_ids)
        ))
        .order_by(Transaction.id.desc())
        .limit(limit)
    )
    
    if cursor:
        stmt = stmt.where(Transaction.id < uuid.UUID(cursor))
        
    result = await session.execute(stmt)
    transactions = result.scalars().all()
    
    next_cursor = transactions[-1].id if transactions and len(transactions) == limit else None # type: ignore
        
    items = []
    for tx in transactions:
        items.append(TransactionResponse(
            id=tx.id, # type: ignore
            source_account_id=tx.source_account_id,
            destination_account_id=tx.destination_account_id,
            amount_paise=tx.amount_paise, # type: ignore
            transaction_type=str(tx.transaction_type),
            status=str(tx.status),
            reference_number=str(tx.reference_number),
            created_at=tx.created_at # type: ignore
        ))
        
    return PaginatedTransactions(items=items, next_cursor=next_cursor)

@router.get("/statement.pdf")
async def get_statement_pdf(
    session: AsyncSession = Depends(get_db_session),
    payload: dict[str, Any] = Depends(get_current_user_token_payload)
) -> Response:
    paginated = await get_history(limit=50, cursor=None, session=session, payload=payload)
    
    html = "<h1>PayFast Statement</h1><ul>"
    for tx in paginated.items:
        html += f"<li>{tx.created_at}: {tx.transaction_type} of ₹{tx.amount_paise/100:.2f} - {tx.status}</li>"
    html += "</ul>"
    
    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html).write_pdf()
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf", 
            headers={"Content-Disposition": 'attachment; filename="payfast_statement.pdf"'}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF rendering failed. Check OS deps (cairo/pango). Error: {e}")
