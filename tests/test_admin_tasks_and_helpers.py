from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.utils import timezone

from django_celery_logs.admin import TaskConfigAdmin, TaskLogAdmin, TaskLogStatisticsAdmin
from django_celery_logs.models import TaskConfig, TaskLog, TaskLogStatistics
from django_celery_logs.tasks import clear_celery_task_logs
from django_celery_logs.templatetags.celery_logs_admin import seconds_to_verbose
from django_celery_logs.utils import (
    acquire_lock_or_fail,
    clean_locals,
    create_task_log,
    get_periodic_task_name,
    parse_duration_to_seconds,
)
from django_celery_logs.widgets import PrettyJSONWidget


def make_sender(task_id="task-id", headers=None, delivery_info=None, args=None, kwargs=None):
    return SimpleNamespace(
        name="tests.tasks.example",
        request=SimpleNamespace(
            id=task_id,
            delivery_info=delivery_info or {},
            headers=headers or {},
            hostname="worker-1",
            args=[] if args is None else args,
            kwargs={} if kwargs is None else kwargs,
        ),
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (object(), None),
        ("abc", None),
        ("1 hour, 2.5 secs", 12.5),
        ("broken sec", None),
        ('broken" secs', None),
        ("1 min and broken secs", 1.0),
    ],
)
def test_parse_duration_to_seconds_edge_cases(value, expected):
    assert parse_duration_to_seconds(value) == expected


def test_clean_locals_hides_private_names_and_reprs_unsafe_values():
    cleaned = clean_locals({"name": "task", "_hidden": "secret", "items": [1, 2], "In": ["visible"]})

    assert cleaned == {
        "name": "task",
        "items": "[1, 2]",
        "In": "['visible']",
    }


def test_get_periodic_task_name_falls_back_through_headers():
    assert get_periodic_task_name(SimpleNamespace(headers=None)) is None
    assert get_periodic_task_name(SimpleNamespace(headers={"periodic_task_name": "nightly"})) == "nightly"
    assert get_periodic_task_name(SimpleNamespace(headers={"task": "tasks.cleanup"})) == "tasks.cleanup"
    assert get_periodic_task_name(SimpleNamespace(headers={"origin": "worker@example"})) == "worker@example"


@pytest.mark.django_db
def test_create_task_log_handles_missing_sender_or_task_id():
    assert create_task_log(result={"ok": True}) is None
    assert create_task_log(sender=make_sender(task_id=None), result={"ok": True}) is None
    assert TaskLog.objects.count() == 0


@pytest.mark.django_db
def test_create_task_log_serializes_result_duration_and_headers():
    task_log = create_task_log(
        sender=make_sender(
            task_id="task-with-duration",
            headers={"task": "fallback-periodic-name"},
            delivery_info={"routing_key": "critical"},
        ),
        result={"duration": "2 min and 5 secs", "payload": object()},
    )

    assert task_log.status == TaskLog.Status.SUCCESS
    assert task_log.duration_secs == 125.0
    assert task_log.periodic_task_name == "fallback-periodic-name"
    assert task_log.queue_name == "critical"
    assert isinstance(task_log.result["payload"], str)


@pytest.mark.django_db
def test_create_task_log_records_failures_with_contextual_traceback(monkeypatch):
    monkeypatch.setattr(
        "django_celery_logs.utils.get_contextual_traceback",
        lambda: {"exc_type": "ValueError", "exc_msg": "boom", "exc_tb": {"frames": []}},
    )

    task_log = create_task_log(sender=make_sender(task_id="failed-task"), exception=ValueError("boom"))

    assert task_log.status == TaskLog.Status.FAILURE
    assert task_log.result is None
    assert task_log.error_message == "ValueError: boom"
    assert task_log.traceback["exc_type"] == "ValueError"


def test_acquire_lock_or_fail_uses_cache_lock(cache):
    task_instance = SimpleNamespace(request=SimpleNamespace(id="task-1"))

    assert acquire_lock_or_fail(task_instance, "lock:test", timeout=30) is None

    logger = SimpleNamespace(warnings=[])
    logger.warning = lambda *args: logger.warnings.append(args)

    skipped = acquire_lock_or_fail(task_instance, "lock:test", timeout=30, logger=logger)

    assert skipped == {
        "status": "skipped",
        "reason": "already_processing",
        "lock_key": "lock:test",
        "ignore_task_log": True,
    }
    assert logger.warnings


def test_pretty_json_widget_formats_json_values():
    widget = PrettyJSONWidget()

    assert widget.format_value(None) == ""
    assert widget.format_value("") == ""
    assert widget.format_value('{"b": 2, "a": 1}') == '{\n  "a": 1,\n  "b": 2\n}'
    assert widget.format_value({"b": 2, "a": 1}) == '{\n  "a": 1,\n  "b": 2\n}'
    assert widget.format_value("{invalid") == "{invalid"


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (None, ""),
        (0, ""),
        (5, "5 secs"),
        (65, "1 min and 5 secs"),
    ],
)
def test_seconds_to_verbose(seconds, expected):
    assert seconds_to_verbose(seconds) == expected


@pytest.mark.django_db
def test_clear_celery_task_logs_removes_expired_rows(monkeypatch):
    TaskConfig.objects.update_or_create(pk=1, defaults={"logs_expiration_days": 2})
    old_log = TaskLog.objects.create(
        task_id="old",
        task_name="tests.old",
        worker="worker-1",
        status=TaskLog.Status.SUCCESS,
    )
    fresh_log = TaskLog.objects.create(
        task_id="fresh",
        task_name="tests.fresh",
        worker="worker-1",
        status=TaskLog.Status.SUCCESS,
    )
    TaskLog.objects.filter(pk=old_log.pk).update(timestamp=timezone.now() - timedelta(days=5))
    TaskLog.objects.filter(pk=fresh_log.pk).update(timestamp=timezone.now())
    times = iter([10.0, 11.234])
    monkeypatch.setattr("django_celery_logs.tasks.time.perf_counter", lambda: next(times))

    result = clear_celery_task_logs.run()

    assert result == {
        "status": "Celery task logs cleaned",
        "deleted": 1,
        "duration_s": 1.23,
    }
    assert list(TaskLog.objects.values_list("task_id", flat=True)) == ["fresh"]


@pytest.mark.django_db
def test_task_config_admin_permissions():
    model_admin = TaskConfigAdmin(TaskConfig, AdminSite())
    request = RequestFactory().get("/")

    assert model_admin.has_add_permission(request) is True
    TaskConfig.objects.create(pk=1)
    assert model_admin.has_add_permission(request) is False
    assert model_admin.has_delete_permission(request) is False


@pytest.mark.django_db
def test_task_log_admin_render_helpers():
    model_admin = TaskLogAdmin(TaskLog, AdminSite())
    task_log = TaskLog.objects.create(
        task_id="render-task",
        task_name="tests.render",
        worker="worker-1",
        status=TaskLog.Status.FAILURE,
        result={"b": 2, "a": "<tag>"},
        error_message="ValueError: boom",
        traceback={
            "exc_type": "ValueError",
            "exc_msg": "boom",
            "exc_tb": {
                "frames": [
                    {"func_name": "first", "module_name": "tests", "lineno": 1, "locals": {"x": 1}},
                    {"func_name": "last", "module_name": "tests", "lineno": 2, "locals": {"y": "<tag>"}},
                ]
            },
        },
    )

    assert model_admin.has_add_permission(None) is False
    assert model_admin.has_change_permission(None) is False
    assert model_admin.exc_type(task_log) == "ValueError"
    assert model_admin.exc_msg(task_log) == "boom"
    assert "&lt;tag&gt;" in model_admin.result_pretty(task_log)
    assert "<details" in model_admin.result_snippet(task_log)
    assert "Frame 1: last @ tests:2" in model_admin.traceback_pretty(task_log)
    assert " open" in model_admin.traceback_pretty(task_log)
    assert model_admin._timestamp(task_log)
    assert model_admin.traceback_pretty(SimpleNamespace(traceback={})) == "No traceback available."


@pytest.mark.django_db
def test_task_log_admin_result_snippet_uses_error_for_failed_empty_result():
    model_admin = TaskLogAdmin(TaskLog, AdminSite())
    task_log = TaskLog.objects.create(
        task_id="failed-empty-result",
        task_name="tests.failure",
        worker="worker-1",
        status=TaskLog.Status.FAILURE,
        error_message="RuntimeError: nope",
    )

    assert "RuntimeError: nope" in model_admin.result_snippet(task_log)


@pytest.mark.django_db
def test_task_log_admin_rerun_task_view_success(monkeypatch):
    model_admin = TaskLogAdmin(TaskLog, admin.site)
    task_log = TaskLog.objects.create(
        task_id="rerun-source",
        task_name="tests.rerun",
        worker="worker-1",
        status=TaskLog.Status.SUCCESS,
        task_args=[1],
        task_kwargs={"force": True},
        queue_name="critical",
    )
    request = RequestFactory().get("/")
    sent = {}
    monkeypatch.setattr("django_celery_logs.admin.messages.success", lambda *args, **kwargs: sent.update(success=args))
    monkeypatch.setattr("django_celery_logs.admin.current_app.send_task", lambda *args, **kwargs: SimpleNamespace(id="new-task-id"))

    response = model_admin.rerun_task_view(request, str(task_log.pk))

    assert response.status_code == 302
    assert sent["success"][0] is request


@pytest.mark.django_db
def test_task_log_admin_rerun_task_view_handles_missing_object(monkeypatch):
    model_admin = TaskLogAdmin(TaskLog, admin.site)
    request = RequestFactory().get("/")
    sent = {}
    monkeypatch.setattr("django_celery_logs.admin.messages.error", lambda *args, **kwargs: sent.update(error=args))

    response = model_admin.rerun_task_view(request, "999")

    assert response.status_code == 302
    assert sent["error"][0] is request


@pytest.mark.django_db
def test_task_log_admin_changelist_view_adds_page_size_context(monkeypatch):
    model_admin = TaskLogAdmin(TaskLog, AdminSite())
    request = RequestFactory().get("/", {"list_per_page": "50"})

    monkeypatch.setattr(admin.ModelAdmin, "changelist_view", lambda self, req, extra_context=None: extra_context)

    context = model_admin.changelist_view(request)

    assert context["list_per_page_options"] == [25, 50, 75, 100]
    assert context["selected_per_page"] == 50


@pytest.mark.django_db
def test_task_log_statistics_admin_builds_dashboard_context(monkeypatch):
    model_admin = TaskLogStatisticsAdmin(TaskLogStatistics, AdminSite())
    request = RequestFactory().get("/")
    now = timezone.now()
    TaskLog.objects.create(
        task_id="stat-success",
        task_name="tests.stats",
        queue_name="default",
        worker="worker-1",
        status=TaskLog.Status.SUCCESS,
        duration_secs=12,
        periodic_task_name="nightly",
    )
    TaskLog.objects.create(
        task_id="stat-failure",
        task_name="tests.stats",
        queue_name="default",
        worker="worker-1",
        status=TaskLog.Status.FAILURE,
        duration_secs=30,
        error_message="ValueError: boom",
    )
    TaskLog.objects.update(timestamp=now)

    monkeypatch.setattr(admin.ModelAdmin, "changelist_view", lambda self, req, extra_context=None: extra_context)

    context = model_admin.changelist_view(request)

    assert model_admin.has_add_permission(request) is False
    assert model_admin.has_change_permission(request) is False
    assert model_admin.has_delete_permission(request) is False
    assert context["statistics"]["total_messages"] == 2
    assert context["statistics"]["total_success"] == 1
    assert context["statistics"]["total_failure"] == 1
    assert context["statistics"]["success_rate"] == 50.0
    assert context["top_tasks"][0]["task_name"] == "tests.stats"
    assert context["slowest_tasks"][0]["avg_duration"] == 21
    assert '"success_failure_stats"' in context["chart_data"]
