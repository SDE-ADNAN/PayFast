from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.auth.router import router as auth_router
from src.database import engine
from src.exceptions import PayFastError
from src.redis_client import close_redis_pool, init_redis_pool
from src.upi.router import router as upi_router
from src.accounts.router import router as accounts_router
from src.payments.router import router as payments_router
from src.ws.router import router as ws_router
from src.transactions.router import router as transactions_router
from src.disputes.router import router as disputes_router
from src.admin.router import router as admin_router
from src.qr.router import router as qr_router
from src.middleware.idempotency import IdempotencyMiddleware
from src.middleware.tracing import TraceIDMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = structlog.get_logger()

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

# Limit configuration
limiter = Limiter(key_func=get_remote_address)


from typing import AsyncGenerator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: e.g. check DB connection
    logger.info("Starting PayFast API")
    await init_redis_pool()
    yield
    # Shutdown: e.g. close DB pool
    logger.info("Shutting down PayFast API")
    await close_redis_pool()
    await engine.dispose()


app = FastAPI(
    title="PayFast API",
    description="Deep Technical Engineering Specification Implementation",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "auth", "description": "Authentication and User setup"},
        {"name": "payments", "description": "Core P2P logic and Collection routes"},
        {"name": "transactions", "description": "Read-replica metrics streams"}
    ],
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["payfast.io", "*.payfast.io", "localhost", "127.0.0.1"]
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(IdempotencyMiddleware)
app.add_middleware(TraceIDMiddleware)

app.include_router(auth_router)
app.include_router(upi_router)
app.include_router(accounts_router)
app.include_router(payments_router)
app.include_router(ws_router)
app.include_router(transactions_router)
app.include_router(disputes_router)
app.include_router(admin_router)
app.include_router(qr_router)


@app.exception_handler(PayFastError)
async def payfast_exception_handler(
    request: Request, exc: PayFastError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.code,
            "message": exc.message,
            "details": getattr(exc, "details", {}),
        },
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok"}
