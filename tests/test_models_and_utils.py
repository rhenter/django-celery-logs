from types import SimpleNamespace

import pytest

from django_celery_logs.models import TaskConfig, TaskLog
from django_celery_logs.utils import create_task_log, parse_duration_to_seconds, sort_dict_recursively


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("12", 12.0),
        ("5 secs", 5.0),
        ("2 min and 3 secs", 123.0),
        ("2\" 3'", 123.0),
        (None, None),
    ],
)
def test_parse_duration_to_seconds(value, expected):
    assert parse_duration_to_seconds(value) == expected


def test_sort_dict_recursively():
    assert sort_dict_recursively({"b": 2, "a": {"d": 4, "c": 3}}) == {"a": {"c": 3, "d": 4}, "b": 2}


@pytest.mark.django_db
def test_task_config_get_solo():
    assert TaskConfig.get_solo().pk == 1
    assert TaskConfig.objects.count() == 1


@pytest.mark.django_db
def test_create_task_log_success():
    sender = SimpleNamespace(
        name="tests.tasks.example",
        request=SimpleNamespace(
            id="task-id",
            delivery_info={"routing_key": "default"},
            headers={"periodic_task_name": "nightly"},
            hostname="worker-1",
            args=[1],
            kwargs={"force": True},
        ),
    )

    task_log = create_task_log(sender=sender, result={"duration_s": 1.5, "ok": True})

    assert task_log.status == TaskLog.Status.SUCCESS
    assert task_log.duration_secs == 1.5
    assert task_log.queue_name == "default"
    assert task_log.periodic_task_name == "nightly"


@pytest.mark.django_db
def test_create_task_log_can_ignore_result():
    sender = SimpleNamespace(
        name="tests.tasks.example",
        request=SimpleNamespace(
            id="task-id",
            delivery_info={},
            headers={},
            hostname="worker-1",
            args=[],
            kwargs={},
        ),
    )

    assert create_task_log(sender=sender, result={"ignore_task_log": True}) is None
    assert TaskLog.objects.count() == 0
