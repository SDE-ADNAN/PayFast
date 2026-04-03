import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import structlog

logger = structlog.get_logger()

class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Bind context variables for structured logging
        structlog.contextvars.bind_contextvars(
            trace_id=trace_id,
            client_ip=request.client.host if request.client else "unknown",
            method=request.method,
            path=request.url.path
        )
        
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = trace_id
            return response
        finally:
            structlog.contextvars.clear_contextvars()
