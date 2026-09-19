import django_celery_logs.models
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TaskConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "logs_expiration_days",
                    models.PositiveIntegerField(
                        default=django_celery_logs.models.get_default_logs_expiration_days,
                        help_text="Number of days to keep celery task logs.",
                        verbose_name="Logs Expiration Days",
                    ),
                ),
            ],
            options={
                "verbose_name": "Task Configuration",
                "verbose_name_plural": "Task Configurations",
            },
        ),
        migrations.CreateModel(
            name="TaskLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("task_id", models.CharField(max_length=255, unique=True)),
                ("task_name", models.CharField(max_length=255)),
                ("periodic_task_name", models.CharField(blank=True, max_length=255, null=True)),
                ("queue_name", models.CharField(blank=True, max_length=255, null=True)),
                ("worker", models.CharField(max_length=255)),
                ("status", models.CharField(choices=[("SUCCESS", "Success"), ("FAILURE", "Failure")], max_length=10)),
                ("task_args", models.JSONField(blank=True, null=True)),
                ("task_kwargs", models.JSONField(blank=True, null=True)),
                ("result", models.JSONField(blank=True, null=True)),
                ("duration_secs", models.FloatField(blank=True, null=True, verbose_name="Duration (Seconds)")),
                ("error_message", models.TextField(blank=True)),
                ("traceback", models.JSONField(blank=True, null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Task Log",
                "verbose_name_plural": "Task Logs",
                "ordering": ["-timestamp"],
            },
        ),
        migrations.CreateModel(
            name="TaskLogStatistics",
            fields=[],
            options={
                "verbose_name": "Task Log Statistics",
                "verbose_name_plural": "Task Log Statistics",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("celery_log.tasklog",),
        ),
    ]
