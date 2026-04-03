import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db_session
from src.models import Dispute
from src.auth.dependencies import get_current_user_token_payload, require_role
from src.disputes.schemas import DisputeCreate, DisputeResponse
from src.disputes.services import resolve_dispute

router = APIRouter(prefix="/disputes", tags=["disputes"])

@router.post("", response_model=DisputeResponse)
async def create_dispute(
    req: DisputeCreate,
    session: AsyncSession = Depends(get_db_session),
    payload: dict[str, Any] = Depends(get_current_user_token_payload)
) -> DisputeResponse:
    user_id = payload.get("sub")
    
    async with session.begin():
        dispute = Dispute(
            transaction_id=req.transaction_id,
            status="open",
            reason=req.reason
        )
        session.add(dispute)
    
    # Needs explicit DB query to get back populated obj or use flush over commit above.
    return DisputeResponse(
        id=dispute.id, # type: ignore
        transaction_id=dispute.transaction_id, # type: ignore
        status=str(dispute.status),
        reason=str(dispute.reason)
    )

@router.get("", response_model=list[DisputeResponse])
async def list_disputes(
    session: AsyncSession = Depends(get_db_session),
    payload: dict[str, Any] = Depends(require_role("admin"))
) -> list[DisputeResponse]:
    result = await session.execute(select(Dispute).order_by(Dispute.created_at.desc()))
    disputes = result.scalars().all()
    
    return [DisputeResponse.model_validate(d) for d in disputes]

@router.post("/{dispute_id}/resolve")
async def execute_resolve_dispute(
    dispute_id: str,
    session: AsyncSession = Depends(get_db_session),
    payload: dict[str, Any] = Depends(require_role("admin"))
) -> dict[str, str]:
    await resolve_dispute(session, uuid.UUID(dispute_id))
    return {"status": "resolved"}
