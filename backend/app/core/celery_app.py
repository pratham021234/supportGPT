from celery import Celery
import os
import ssl

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "supportgpt_worker",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
)

# Optional: Disable SSL verification for local dev if needed
if "rediss://" in redis_url:
    celery_app.conf.broker_use_ssl = {
        'ssl_cert_reqs': ssl.CERT_NONE
    }
    celery_app.conf.redis_backend_use_ssl = {
        'ssl_cert_reqs': ssl.CERT_NONE
    }
