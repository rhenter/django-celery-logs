from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CeleryLogsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_celery_logs"
    label = "celery_log"
    verbose_name = _("Celery Task Logs")

    def ready(self):
        from . import signals  # noqa: F401
