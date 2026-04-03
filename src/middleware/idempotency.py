import hashlib
import json
from fastapi import Request, Response
from sqlalchemy import text, select
from starlette.middleware.base import BaseHTTPMiddleware
from src.database import async_session_maker
from src.models import IdempotencyKey

class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        idem_key = request.headers.get("Idempotency-Key")
        
        # Only apply to state-changing endpoints with the header
        if not idem_key or request.method not in ("POST", "PUT", "PATCH"):
            return await call_next(request)
            
        body = await request.body()
        request_hash = hashlib.sha256(body).hexdigest()
        
        # Get user id if authenticated (simplified for middleware scope)
        auth_header = request.headers.get("Authorization")
        user_id = None
        if auth_header and auth_header.startswith("Bearer "):
            from src.auth.security import decode_token
            try:
                payload = decode_token(auth_header.split(" ")[1])
                user_id = payload.get("sub")
            except Exception:
                pass
                
        if not user_id:
            # If not authenticated, let the auth middleware handle the 401 later
            return await call_next(request)
        
        async with async_session_maker() as session:
            async with session.begin():
                # Attempt to reserve execution slot atomically
                await session.execute(
                    text("""
                        INSERT INTO idempotency_keys (key, user_id, endpoint, request_hash)
                        VALUES (:key, :user_id, :endpoint, :hash)
                        ON CONFLICT (key) DO NOTHING
                    """),
                    {
                        "key": idem_key,
                        "user_id": user_id,
                        "endpoint": f"{request.method} {request.url.path}",
                        "hash": request_hash,
                    }
                )
                
                result = await session.execute(
                    select(IdempotencyKey).where(IdempotencyKey.key == idem_key)
                )
                record = result.scalar_one()
                
            # Conflict: same key, different request body
            if record.request_hash != request_hash:
                return Response(
                    status_code=422,
                    content=json.dumps({"error": "IDEMPOTENCY_CONFLICT",
                                        "detail": "Same key used with different request body"}),
                    media_type="application/json"
                )
                
            # Already processed — return cached response
            if record.response_status is not None:
                return Response(
                    status_code=record.response_status,
                    content=json.dumps(record.response_body),
                    media_type="application/json"
                )
                
            # Else, this is a fresh concurrent request that just grabbed the lock!
            # It will get routed through to the actual endpoint now.
            try:
                response = await call_next(request)
            except Exception as e:
                # If error happens, we don't save response so client can retry. (Except if it's caught normally)
                raise
                
            # Read response body to cache it
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
                
            try:
                body_json = json.loads(response_body)
            except Exception:
                body_json = {}
                
            async with async_session_maker() as session_update:
                async with session_update.begin():
                    record_update = await session_update.get(IdempotencyKey, record.id)
                    if record_update:
                        record_update.response_status = response.status_code
                        record_update.response_body = body_json
                        
            # Reconstruct response to return to client
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
