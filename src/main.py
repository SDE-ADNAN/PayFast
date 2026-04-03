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

logger = structlog.get_logger()

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
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router)
app.include_router(upi_router)


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
