from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.database import engine
from src.exceptions import PayFastError

logger = structlog.get_logger()


from typing import AsyncGenerator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: e.g. check DB connection
    logger.info("Starting PayFast API")
    yield
    # Shutdown: e.g. close DB pool
    logger.info("Shutting down PayFast API")
    await engine.dispose()


app = FastAPI(
    title="PayFast API",
    description="Deep Technical Engineering Specification Implementation",
    version="0.1.0",
    lifespan=lifespan,
)


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
