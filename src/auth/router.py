import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from src.database import get_db_session
from src.models import User, Account, UpiId, RefreshToken
from src.auth.schemas import UserRegister, UserLogin, Token, RefreshRequest, UserResponse
from src.auth.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from src.upi.services import generate_default_vpa

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["auth"])

def _generate_account_number() -> str:
    # Just a simple deterministic placeholder for demo purposes
    return str(uuid.uuid4().int)[:14]

@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
async def register(request: Request, user_in: UserRegister, session: AsyncSession = Depends(get_db_session)) -> User:
    # Check if phone exists
    result = await session.execute(select(User).where(User.phone == user_in.phone))
    if result.first():
        raise HTTPException(status_code=400, detail="Phone number already registered")
        
    async with session.begin():
        # Create User
        new_user = User(
            phone=user_in.phone,
            email=user_in.email,
            full_name=user_in.full_name,
            password_hash=get_password_hash(user_in.password),
        )
        session.add(new_user)
        await session.flush()
        
        # Create Account
        new_account = Account(
            user_id=new_user.id,
            account_number=_generate_account_number(),
        )
        session.add(new_account)
        await session.flush()
        
        # Create Default VPA
        vpa_str = generate_default_vpa(new_user.phone, new_user.full_name)
        # Handle collision gracefully (simplified approach)
        vpa_check = await session.execute(select(UpiId).where(UpiId.vpa == vpa_str))
        if vpa_check.first():
            vpa_str = f"{vpa_str.split('@')[0]}{new_user.id.hex[:4]}@payfast" # type: ignore
            
        new_upi = UpiId(
            user_id=new_user.id,
            account_id=new_account.id,
            vpa=vpa_str,
            is_primary=True
        )
        session.add(new_upi)
        
    return new_user

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, credentials: UserLogin, session: AsyncSession = Depends(get_db_session)) -> Token:
    result = await session.execute(select(User).where(User.phone == credentials.phone))
    user = result.scalar_one_or_none()
    
    # Needs async transaction to push failed attempts properly
    async with session.begin():
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
            
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is temporarily locked")
            
        if not verify_password(credentials.password, user.password_hash):
            user.failed_attempts += 1 # type: ignore
            if user.failed_attempts >= 5: # type: ignore
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30) # type: ignore
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
            
        # Success
        user.failed_attempts = 0 # type: ignore
        user.locked_until = None # type: ignore
        
        token_data = {"sub": str(user.id), "phone": user.phone, "role": user.role}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        
        # Save refresh token in DB
        rt_record = RefreshToken(
            user_id=user.id,
            token_hash=get_password_hash(refresh_token), # simplified hash of token
            family_id=uuid.uuid4(),
            ip_address=request.client.host if request.client else None
        )
        session.add(rt_record)

    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=Token)
async def refresh_token(req: RefreshRequest, session: AsyncSession = Depends(get_db_session)) -> Token:
    try:
        payload = decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    async with session.begin():
        # Look up valid token
        result = await session.execute(
            select(RefreshToken).where(RefreshToken.user_id == uuid.UUID(user_id)).where(RefreshToken.is_revoked == False)
        )
        tokens = result.scalars().all()
        
        valid_record = None
        for rt in tokens:
            if verify_password(req.refresh_token, str(rt.token_hash)):
                valid_record = rt
                break
                
        if not valid_record:
            raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")
            
        # Rotate
        valid_record.is_revoked = True # type: ignore
        
        # Issue new
        token_data = {"sub": user_id, "phone": payload.get("phone"), "role": payload.get("role")}
        new_access = create_access_token(data=token_data)
        new_refresh = create_refresh_token(data=token_data)
        
        new_rt_record = RefreshToken(
            user_id=uuid.UUID(user_id),
            token_hash=get_password_hash(new_refresh),
            family_id=valid_record.family_id,
        )
        session.add(new_rt_record)
        
    return Token(access_token=new_access, refresh_token=new_refresh)
