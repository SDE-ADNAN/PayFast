import re
import json
from uuid import UUID
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from src.models import UpiId, User

VPA_REGEX = re.compile(r"^[a-zA-Z0-9.\-_]{3,100}@[a-zA-Z]{3,50}$")

def validate_vpa_format(vpa: str) -> bool:
    return bool(VPA_REGEX.match(vpa))

def generate_default_vpa(phone: str, full_name: str) -> str:
    """Generates a default VPA like john.doe@payfast or 9876543210@payfast"""
    clean_name = re.sub(r'[^a-zA-Z0-9.\-_]', '', full_name.lower().replace(' ', '.'))
    if len(clean_name) >= 3:
        return f"{clean_name}@payfast"
    return f"{phone}@payfast"

async def resolve_vpa(vpa: str, session: AsyncSession, redis: aioredis.Redis) -> dict[str, str]:
    if not validate_vpa_format(vpa):
        raise HTTPException(status_code=400, detail="Invalid VPA format")

    cache_key = f"vpa:{vpa}"
    cached_info = await redis.get(cache_key)
    if cached_info:
        return json.loads(str(cached_info)) # type: ignore

    # DB Lookup
    stmt = (
        select(UpiId, User)
        .join(User, UpiId.user_id == User.id)
        .where(UpiId.vpa == vpa)
        .where(UpiId.is_active == True)
    )
    result = await session.execute(stmt)
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="VPA not found")
        
    upi_record, user_record = row
    
    info = {
        "vpa": upi_record.vpa,
        "account_id": str(upi_record.account_id),
        "user_name": user_record.full_name
    }
    
    # Cache for 5 minutes
    await redis.setex(cache_key, 300, json.dumps(info))
    return info
