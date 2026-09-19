import json
import re
from typing import Any, Dict, Optional

from boltons.tbutils import ContextualExceptionInfo
from django.core.cache import cache


def clean_locals(locals_dict, safe_types=(str, int, float, bool, type(None))):
    return {
        key: value if isinstance(value, safe_types) else repr(value)
        for key, value in locals_dict.items()
        if not key.startswith("_") or key in ["In", "Out"]
    }


def get_contextual_traceback():
    exception_data = ContextualExceptionInfo.from_current().to_dict()
    frames = exception_data.get("exc_tb", {}).get("frames") or []
    for index, frame in enumerate(frames):
        frame.pop("pre_lines", None)
        frame.pop("post_lines", None)

        if index == 0:
            frame["locals"] = {}
            continue

        locals_data = frame.get("locals")
        frame["locals"] = clean_locals(locals_data) if isinstance(locals_data, dict) else {}

    return exception_data


def get_periodic_task_name(request):
    if not getattr(request, "headers", None):
        return None

    return (
        request.headers.get("periodic_task_name")
        or request.headers.get("task")
        or request.headers.get("origin")
    )


def sort_dict_recursively(obj):
    if isinstance(obj, dict):
        return {key: sort_dict_recursively(value) for key, value in sorted(obj.items())}
    if isinstance(obj, list):
        return [sort_dict_recursively(item) for item in obj]
    return obj


def parse_duration_to_seconds(value):
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        pass

    if not isinstance(value, str):
        return None

    normalized = value.strip().lower()
    if '"' in normalized and "'" in normalized:
        try:
            minutes = normalized.split('"')[0].strip()
            seconds = normalized.split('"', 1)[1].split("'", 1)[0].strip()
            return float(minutes) * 60.0 + float(seconds)
        except (IndexError, ValueError):
            pass

    if "min" in normalized and "and" in normalized and "sec" in normalized:
        try:
            minutes = normalized.split("min")[0].strip()
            seconds = normalized.split("min", 1)[1].split("and", 1)[1].split("sec")[0].strip()
            return float(minutes) * 60.0 + float(seconds)
        except (IndexError, ValueError):
            pass

    if "sec" in normalized:
        try:
            return float(normalized.split("sec")[0].strip())
        except ValueError:
            pass

    number = re.sub(r"[^0-9.]", "", normalized)
    try:
        return float(number) if number else None
    except ValueError:
        return None


def create_task_log(sender=None, exception=None, result=None, **kwargs):
    from .models import TaskLog

    if sender is None or not getattr(sender, "request", None):
        return None

    request = sender.request
    delivery_info = getattr(request, "delivery_info", None) or {}
    result_serialized = None

    task_log_data = {
        "task_id": getattr(request, "id", None),
        "task_name": getattr(sender, "name", sender.__class__.__name__),
        "periodic_task_name": get_periodic_task_name(request),
        "queue_name": delivery_info.get("routing_key"),
        "worker": getattr(request, "hostname", "") or "",
        "task_args": getattr(request, "args", None),
        "task_kwargs": getattr(request, "kwargs", None),
    }

    if not task_log_data["task_id"]:
        return None

    if exception is None:
        if isinstance(result, dict) and result.get("ignore_task_log"):
            return None

        try:
            result_serialized = json.loads(json.dumps(result, default=str))
        except (TypeError, ValueError):
            result_serialized = None

        duration_secs = None
        if isinstance(result_serialized, dict):
            raw_secs = result_serialized.get("duration_secs") or result_serialized.get("duration_s")
            duration_secs = (
                float(raw_secs)
                if isinstance(raw_secs, (int, float))
                else parse_duration_to_seconds(result_serialized.get("duration"))
            )
        elif isinstance(result_serialized, (int, float, str)):
            duration_secs = parse_duration_to_seconds(result_serialized)

        task_log_data.update(
            {
                "status": TaskLog.Status.SUCCESS,
                "result": result_serialized
                if isinstance(result_serialized, (str, dict, list, int, float, bool, type(None)))
                else None,
                "duration_secs": duration_secs,
            }
        )
    else:
        task_log_data.update(
            {
                "status": TaskLog.Status.FAILURE,
                "result": None,
                "error_message": f"{type(exception).__name__}: {exception}",
                "traceback": get_contextual_traceback(),
            }
        )

    return TaskLog.objects.create(**task_log_data)


def acquire_lock_or_fail(task_instance: Any, lock_key: str, timeout: int = 270, logger: Any = None) -> Optional[Dict]:
    if cache.add(lock_key, task_instance.request.id, timeout=timeout):
        return None

    existing_task_id = cache.get(lock_key)
    if logger:
        logger.warning("Task for %s is already being processed by task %s. Skipping.", lock_key, existing_task_id)

    return {
        "status": "skipped",
        "reason": "already_processing",
        "lock_key": lock_key,
        "ignore_task_log": True,
    }
