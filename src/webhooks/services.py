import hmac
import hashlib
import json
import logging
import httpx
from datetime import datetime, timezone
import asyncio

from src.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

# NOTE: In reality, each partner/webhook uses their specific pre-shared secret.
def generate_signature(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

async def _dispatch_webhook_async(endpoint: str, payload_dict: dict, secret: str) -> None:
    payload_str = json.dumps(payload_dict)
    signature = generate_signature(payload_str, secret)
    
    headers = {
        "Content-Type": "application/json",
        "X-PayFast-Signature": signature,
        "X-PayFast-Timestamp": str(int(datetime.now(timezone.utc).timestamp()))
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(endpoint, content=payload_str, headers=headers)
        response.raise_for_status()

@celery_app.task(bind=True, acks_late=True, max_retries=7)
def dispatch_webhook(self, endpoint: str, payload_dict: dict, secret: str) -> None:
    """
    Dispatches a signed webhook sequentially.
    If it fails, Celery retries up to 7 times with exponential backoff (handled by conf or exception raise).
    """
    logger.info(f"Dispatching Webhook to {endpoint}")
    try:
        asyncio.run(_dispatch_webhook_async(endpoint, payload_dict, secret))
        logger.info(f"Webhook delivered successfully to {endpoint}")
        # Note: Depending on true scale, updating a `webhook_delivery` table would occur here.
    except Exception as exc:
        logger.warning(f"Webhook delivery failed for {endpoint}. Retrying... Error: {exc}")
        # Exponential backoff retry via celery
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
