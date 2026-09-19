from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


def get_default_logs_expiration_days():
    return getattr(settings, "CELERY_TASK_LOGS_EXPIRES", 2)


class TaskConfig(models.Model):
    logs_expiration_days = models.PositiveIntegerField(
        default=get_default_logs_expiration_days,
        verbose_name=_("Logs Expiration Days"),
        help_text=_("Number of days to keep celery task logs."),
    )

    class Meta:
        verbose_name = _("Task Configuration")
        verbose_name_plural = _("Task Configurations")

    def __str__(self):
        return str(_("Task Configuration"))

    @classmethod
    def get_solo(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


class TaskLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", _("Success")
        FAILURE = "FAILURE", _("Failure")

    task_id = models.CharField(max_length=255, unique=True)
    task_name = models.CharField(max_length=255)
    periodic_task_name = models.CharField(max_length=255, null=True, blank=True)
    queue_name = models.CharField(max_length=255, null=True, blank=True)
    worker = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=Status.choices)
    task_args = models.JSONField(null=True, blank=True)
    task_kwargs = models.JSONField(null=True, blank=True)
    result = models.JSONField(null=True, blank=True)
    duration_secs = models.FloatField(null=True, blank=True, verbose_name=_("Duration (Seconds)"))
    error_message = models.TextField(blank=True)
    traceback = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = _("Task Log")
        verbose_name_plural = _("Task Logs")

    def __str__(self):
        return f"{self.task_id} ({self.task_name}) -> {self.status}"


class TaskLogStatistics(TaskLog):
    class Meta:
        proxy = True
        verbose_name = _("Task Log Statistics")
        verbose_name_plural = _("Task Log Statistics")
