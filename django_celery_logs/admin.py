import json
from datetime import timedelta

from celery import current_app
from django.conf import settings
from django.contrib import admin, messages
from django.db.models import Avg, Count, JSONField, Max, Min, Q
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import TaskConfig, TaskLog, TaskLogStatistics
from .utils import sort_dict_recursively
from .widgets import PrettyJSONWidget


@admin.register(TaskConfig)
class TaskConfigAdmin(admin.ModelAdmin):
    list_display = ("logs_expiration_days",)

    def has_add_permission(self, request):
        return not TaskConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    model = TaskLog
    date_hierarchy = "timestamp"
    list_display = ("id", "task_name", "_timestamp", "status", "result_snippet")
    list_filter = ("status", "timestamp", "task_name", "queue_name")
    readonly_fields = (
        "timestamp",
        "worker",
        "status",
        "task_id",
        "task_name",
        "periodic_task_name",
        "queue_name",
        "exc_type",
        "exc_msg",
        "result_pretty",
        "traceback_pretty",
    )
    search_fields = ("task_name", "task_id", "worker")
    fieldsets = (
        (
            None,
            {
                "fields": ("task_id", "task_name", "periodic_task_name", "queue_name", "status", "worker"),
                "classes": ("extrapretty", "wide"),
            },
        ),
        (_("Parameters"), {"fields": ("task_args", "task_kwargs"), "classes": ("extrapretty", "wide")}),
        (
            _("Result"),
            {
                "fields": ("result_pretty", "timestamp", "exc_type", "exc_msg", "traceback_pretty"),
                "classes": ("extrapretty", "wide"),
            },
        ),
    )
    formfield_overrides = {JSONField: {"widget": PrettyJSONWidget}}
    list_per_page = 25

    def get_changelist_instance(self, request):
        list_per_page_options = [25, 50, 75, 100]
        selected_per_page = request.GET.get("list_per_page", "25")

        try:
            selected_per_page = int(selected_per_page)
            self.list_per_page = selected_per_page if selected_per_page in list_per_page_options else 25
        except (ValueError, TypeError):
            self.list_per_page = 25

        if "list_per_page" in request.GET:
            get_params = request.GET.copy()
            del get_params["list_per_page"]
            request.GET = get_params

        return super().get_changelist_instance(request)

    def changelist_view(self, request, extra_context=None):
        list_per_page_options = [25, 50, 75, 100]
        selected_per_page = request.GET.get("list_per_page", "25")

        try:
            selected_per_page = int(selected_per_page)
            if selected_per_page not in list_per_page_options:
                selected_per_page = 25
        except (ValueError, TypeError):
            selected_per_page = 25

        extra_context = extra_context or {}
        extra_context.update(
            {
                "list_per_page_options": list_per_page_options,
                "selected_per_page": selected_per_page,
            }
        )
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_urls(self):
        custom_urls = [
            path(
                "<path:object_id>/rerun/",
                self.admin_site.admin_view(self.rerun_task_view),
                name="celery_log_tasklog_rerun",
            ),
        ]
        return custom_urls + super().get_urls()

    def rerun_task_view(self, request, object_id):
        task_log = self.get_object(request, object_id)
        if not task_log:
            messages.error(request, _("Task log not found."))
            return HttpResponseRedirect(reverse("admin:celery_log_tasklog_changelist"))

        try:
            result = current_app.send_task(
                task_log.task_name,
                args=task_log.task_args or [],
                kwargs=task_log.task_kwargs or {},
                queue=task_log.queue_name,
            )
            messages.success(request, _("Task '%(task)s' has been re-queued with ID: %(task_id)s") % {
                "task": task_log.task_name,
                "task_id": result.id,
            })
        except Exception as exc:
            messages.error(request, _("Failed to re-run task '%(task)s': %(error)s") % {
                "task": task_log.task_name,
                "error": exc,
            })

        return HttpResponseRedirect(reverse("admin:celery_log_tasklog_change", args=[object_id]))

    def exc_type(self, obj):
        return (obj.traceback or {}).get("exc_type", "")

    exc_type.short_description = _("Exception Type")

    def exc_msg(self, obj):
        return (obj.traceback or {}).get("exc_msg", "")

    exc_msg.short_description = _("Exception Message")

    def result_pretty(self, obj):
        data = obj.result or {}
        safe = escape(json.dumps(data, indent=2, sort_keys=True, default=str))
        return mark_safe(
            '<pre style="background:#f7f7f7;padding:8px;border:1px solid #ddd;'
            'white-space:pre-wrap;word-break:break-all;max-height:500px;overflow:auto;">'
            f"{safe}</pre>"
        )

    result_pretty.short_description = _("Result")

    def result_snippet(self, obj):
        data = obj.result or {}
        if not data and obj.status == TaskLog.Status.FAILURE:
            data = {"error": obj.error_message}

        data = sort_dict_recursively(data)
        compact = escape(json.dumps(data, separators=(",", ":"), default=str))
        pretty = escape(json.dumps(data, indent=2, sort_keys=True, default=str))
        return mark_safe(
            '<details style="display:inline-block;max-width:500px;vertical-align:top;">'
            '<summary style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer;">'
            f"{compact}</summary>"
            '<pre style="background:#f7f7f7;padding:4px;border:1px solid #ddd;margin:4px 0;'
            f'white-space:pre-wrap;word-wrap:break-word;max-height:500px;overflow:auto;">{pretty}</pre>'
            "</details>"
        )

    result_snippet.short_description = _("Result")

    def traceback_pretty(self, obj):
        frames = (obj.traceback or {}).get("exc_tb", {}).get("frames", [])
        html_chunks = []
        total = len(frames)

        for index, frame in enumerate(frames):
            details_attr = " open" if index == total - 1 else ""
            header = "Frame {index}: {func} @ {module}:{line}".format(
                index=index,
                func=frame.get("func_name"),
                module=frame.get("module_name"),
                line=frame.get("lineno"),
            )
            payload = escape(json.dumps(frame, indent=2, sort_keys=True, default=str))
            html_chunks.append(
                f'<details{details_attr} style="margin-bottom:8px;">'
                f'<summary style="font-weight:bold;">{escape(header)}</summary>'
                '<pre style="background:#f7f7f7;padding:8px;border:1px solid #ddd;'
                f'white-space:pre-wrap;word-break:break-all;max-height:300px;overflow:auto;">{payload}</pre>'
                "</details>"
            )

        return mark_safe("".join(html_chunks)) if html_chunks else _("No traceback available.")

    traceback_pretty.short_description = _("Traceback details")

    def _timestamp(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M")

    _timestamp.short_description = _("Timestamp")
    _timestamp.admin_order_field = "timestamp"


@admin.register(TaskLogStatistics)
class TaskLogStatisticsAdmin(admin.ModelAdmin):
    model = TaskLogStatistics

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        days_to_show = getattr(settings, "CELERY_TASK_LOGS_EXPIRES", 2)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days_to_show)
        base_queryset = TaskLog.objects.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)

        messages_per_day = (
            base_queryset.extra(select={"day": "date(timestamp)"})
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )
        failures_per_day = (
            base_queryset.filter(status=TaskLog.Status.FAILURE)
            .extra(select={"day": "date(timestamp)"})
            .values("day")
            .annotate(failures=Count("id"))
            .order_by("day")
        )
        success_failure_stats = base_queryset.aggregate(
            total_success=Count("id", filter=Q(status=TaskLog.Status.SUCCESS)),
            total_failure=Count("id", filter=Q(status=TaskLog.Status.FAILURE)),
        )
        top_tasks = list(
            base_queryset.values("task_name")
            .annotate(
                execution_count=Count("id"),
                success_count=Count("id", filter=Q(status=TaskLog.Status.SUCCESS)),
                failure_count=Count("id", filter=Q(status=TaskLog.Status.FAILURE)),
                success_rate=Count("id", filter=Q(status=TaskLog.Status.SUCCESS)) * 100.0 / Count("id"),
                avg_duration=Avg("duration_secs", filter=Q(duration_secs__gt=0)),
                max_duration=Max("duration_secs", filter=Q(duration_secs__gt=0)),
            )
            .order_by("-execution_count")[:10]
        )
        top_queues = list(
            base_queryset.values("queue_name")
            .annotate(
                message_count=Count("id"),
                success_count=Count("id", filter=Q(status=TaskLog.Status.SUCCESS)),
                failure_count=Count("id", filter=Q(status=TaskLog.Status.FAILURE)),
            )
            .order_by("-message_count")[:10]
        )
        worker_distribution = list(
            base_queryset.values("worker")
            .annotate(
                task_count=Count("id"),
                success_count=Count("id", filter=Q(status=TaskLog.Status.SUCCESS)),
                failure_count=Count("id", filter=Q(status=TaskLog.Status.FAILURE)),
            )
            .order_by("-task_count")[:10]
        )
        periodic_task_distribution = list(
            base_queryset.filter(periodic_task_name__isnull=False)
            .values("periodic_task_name")
            .annotate(
                execution_count=Count("id"),
                success_count=Count("id", filter=Q(status=TaskLog.Status.SUCCESS)),
                failure_count=Count("id", filter=Q(status=TaskLog.Status.FAILURE)),
            )
            .order_by("-execution_count")[:10]
        )
        error_analysis = list(
            base_queryset.filter(status=TaskLog.Status.FAILURE, error_message__isnull=False)
            .exclude(error_message="")
            .values("error_message")
            .annotate(error_count=Count("id"))
            .order_by("-error_count")[:10]
        )
        slowest_tasks = list(
            base_queryset.filter(duration_secs__gt=0)
            .values("task_name")
            .annotate(message_count=Count("id"), avg_duration=Avg("duration_secs"), max_duration=Max("duration_secs"))
            .order_by("-avg_duration", "-max_duration")[:10]
        )
        performance_stats = base_queryset.filter(duration_secs__gt=0).aggregate(
            avg_duration=Avg("duration_secs"),
            min_duration=Min("duration_secs"),
            max_duration=Max("duration_secs"),
            total_with_duration=Count("id"),
        )

        for task in top_tasks + slowest_tasks:
            task["avg_duration"] = int(round(task.get("avg_duration") or 0))

        chart_data = {
            "messages_per_day": list(messages_per_day),
            "failures_per_day": list(failures_per_day),
            "success_failure_stats": success_failure_stats,
            "top_queues": top_queues,
            "top_tasks": top_tasks,
            "worker_distribution": worker_distribution,
            "periodic_task_distribution": periodic_task_distribution,
            "error_analysis": error_analysis,
            "slowest_tasks": slowest_tasks,
            "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        }

        total_messages = success_failure_stats["total_success"] + success_failure_stats["total_failure"]
        days = max((end_date - start_date).days + 1, 1)
        extra_context = extra_context or {}
        extra_context.update(
            {
                "chart_data": json.dumps(chart_data, default=str),
                "days_to_show": days_to_show,
                "top_tasks": top_tasks,
                "slowest_tasks": slowest_tasks,
                "statistics": {
                    "total_messages": total_messages,
                    "total_success": success_failure_stats["total_success"],
                    "total_failure": success_failure_stats["total_failure"],
                    "success_rate": round((success_failure_stats["total_success"] / max(total_messages, 1)) * 100, 2),
                    "avg_messages_per_day": int(round(total_messages / days)),
                    "avg_messages_per_hour": int(round(total_messages / max(days * 24, 1))),
                    "avg_messages_per_minute": int(round(total_messages / max(days * 24 * 60, 1))),
                    "avg_duration": int(round(performance_stats["avg_duration"] or 0)),
                    "max_duration": performance_stats["max_duration"] or 0,
                    "min_duration": performance_stats["min_duration"] or 0,
                    "total_with_duration": performance_stats["total_with_duration"],
                },
            }
        )
        return super().changelist_view(request, extra_context=extra_context)
