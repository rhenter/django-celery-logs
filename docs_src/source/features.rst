* Logs successful and failed Celery task executions automatically.
* Stores task id, task name, periodic task name, queue, worker, args, kwargs,
  JSON result, error message, traceback, timestamp, and duration.
* Captures structured failure tracebacks with frame-by-frame context and
  sanitized local variables.
* Adds Django admin pages for log inspection, JSON preview, task rerun, and
  configurable pagination.
* Adds auto-refresh to the task log list with 5, 10, 30, and 60 second
  intervals.
* Adds an admin statistics dashboard with totals, success rate, durations,
  throughput, queues, workers, periodic tasks, slow tasks, and common errors.
* Includes ``clear_celery_task_logs`` to remove old records.
* Includes ``acquire_lock_or_fail`` for cache-backed task de-duplication.
