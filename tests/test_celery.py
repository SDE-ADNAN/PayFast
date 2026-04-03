from src.worker.tasks import expire_collect_requests
import pytest

def test_celery_task_registration() -> None:
    # Just verify that the task imported as a @celery_app.task properly
    assert hasattr(expire_collect_requests, "apply_async")
    assert hasattr(expire_collect_requests, "delay")
