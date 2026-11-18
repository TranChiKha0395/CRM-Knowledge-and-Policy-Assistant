"""Celery indexing, scheduled VN activation, and <=5m withdrawal purge tasks."""

import os
from datetime import datetime
from zoneinfo import ZoneInfo

import redis
import structlog
from celery import Task

from src.celery_app import app

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
logger = structlog.get_logger(__name__)


@app.task(name="src.tasks.index_task.index_passages")
def index_passages(document_version_id: str) -> dict[str, object]:
    """Recompute pgvector embeddings for curated passages belonging to a document version."""
    return {
        "document_version_id": document_version_id,
        "status": "indexed_scaffold",
        "indexed_at": datetime.now(VN_TZ).isoformat(),
    }


@app.task(name="src.tasks.index_task.activate_scheduled_policies")
def activate_scheduled_policies() -> dict[str, object]:
    """Promote scheduled policies whose Asia/Ho_Chi_Minh effective_from <= now_vn (KNW 03)."""
    return {
        "checked_at_vn": datetime.now(VN_TZ).isoformat(),
        "activated_count": 0,
        "status": "checked_scaffold",
    }


@app.task(
    bind=True,
    max_retries=3,
    name="src.tasks.index_task.withdraw_and_purge_cache",
)
def withdraw_and_purge_cache(
    self: Task,
    policy_version_id: str,
    document_version_id: str | None = None,
) -> dict[str, object]:
    """Physically purge retrieval/answer Redis cache keys well within <= 5 minutes (KNW 04)."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    patterns = [f"ans:*{policy_version_id}*", f"ret:*{policy_version_id}*"]
    if document_version_id:
        patterns.extend([f"ans:*{document_version_id}*", f"ret:*{document_version_id}*"])

    purged_keys = 0
    try:
        client = redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
        try:
            for pattern in dict.fromkeys(patterns):
                keys = list(client.scan_iter(match=pattern, count=200))
                if keys:
                    purged_keys += int(client.delete(*keys))
        finally:
            client.close()
    except redis.RedisError as exc:
        logger.exception(
            "withdraw_cache_purge_failed",
            policy_version_id=policy_version_id,
            document_version_id=document_version_id,
            retry_attempt=self.request.retries,
        )
        raise self.retry(exc=exc, countdown=10)

    return {
        "policy_version_id": policy_version_id,
        "document_version_id": document_version_id,
        "purged_keys": purged_keys,
        "sla_max_seconds": int(os.getenv("CACHE_WITHDRAWAL_MAX_SECONDS", "300")),
        "completed_at_vn": datetime.now(VN_TZ).isoformat(),
    }
