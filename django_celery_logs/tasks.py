import time
from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps as django_apps
from django.db import transaction
from django.utils import timezone

logger = get_task_logger(__name__)


@shared_task(name="clear_celery_task_logs")
def clear_celery_task_logs():
    start_time = time.perf_counter()
    logger.debug("Starting clear_celery_task_logs")

    TaskLog = django_apps.get_model("celery_log", "TaskLog")
    TaskConfig = django_apps.get_model("celery_log", "TaskConfig")
    config = TaskConfig.get_solo()
    cutoff = timezone.now() - timedelta(days=config.logs_expiration_days)

    total_deleted = 0
    batch_size = 1000

    try:
        with transaction.atomic():
            queryset = TaskLog.objects.filter(timestamp__lte=cutoff)
            while True:
                batch_ids = list(queryset.values_list("id", flat=True)[:batch_size])
                if not batch_ids:
                    break
                deleted, _details = TaskLog.objects.filter(id__in=batch_ids).delete()
                total_deleted += deleted
    except Exception:
        logger.exception("clear_celery_task_logs failed during batch delete")

    duration = time.perf_counter() - start_time
    logger.info("clear_celery_task_logs completed: removed %s entries in %.2fs", total_deleted, duration)

    return {
        "status": "Celery task logs cleaned",
        "deleted": total_deleted,
        "duration_s": round(duration, 2),
    }
