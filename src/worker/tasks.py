import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import update

from src.worker.celery_app import celery_app
from src.database import async_session_maker
from src.models import PaymentRequest

logger = logging.getLogger(__name__)

async def _expire_collect_requests_async() -> int:
    async with async_session_maker() as session:
        async with session.begin():
            stmt = (
                update(PaymentRequest)
                .where(PaymentRequest.status == "PENDING")
                .where(PaymentRequest.expires_at < datetime.now(timezone.utc))
                .values(status="EXPIRED")
            )
            result = await session.execute(stmt)
            return result.rowcount # type: ignore

@celery_app.task
def expire_collect_requests() -> str:
    """
    Finds all PENDING collect requests where expires_at has passed and sets them to EXPIRED.
    """
    logger.info("Executing expire_collect_requests task")
    try:
        count = asyncio.run(_expire_collect_requests_async())
        logger.info(f"Expired {count} collect requests")
        return f"Expired {count}"
    except Exception as e:
        logger.error(f"Failed to run expire_collect_requests: {e}")
        raise
