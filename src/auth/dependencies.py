from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import ValidationError
from typing import Any

from src.auth.security import decode_token

security = HTTPBearer()

def get_current_user_token_payload(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict[str, Any]:
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token used where access token is expected",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(required_role: str) -> Any:
    def role_dependency(payload: dict[str, Any] = Depends(get_current_user_token_payload)) -> dict[str, Any]:
        user_role = payload.get("role")
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role} role",
            )
        return payload
    return role_dependency
