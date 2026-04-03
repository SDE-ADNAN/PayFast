from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from src.database import get_db_session
from src.redis_client import get_redis
from src.upi.services import resolve_vpa
from src.auth.dependencies import get_current_user_token_payload

router = APIRouter(prefix="/upi", tags=["upi"])

@router.get("/resolve")
async def resolve_upi_identifier(
    vpa: str,
    session: AsyncSession = Depends(get_db_session),
    redis: aioredis.Redis = Depends(get_redis),
    payload: dict = Depends(get_current_user_token_payload) # type: ignore
) -> dict[str, str]:
    return await resolve_vpa(vpa, session, redis)
