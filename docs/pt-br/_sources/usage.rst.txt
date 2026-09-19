Usage
=====

Automatic logging
-----------------

Once Django loads the app, Celery's ``task_success`` and ``task_failure``
signals create ``TaskLog`` records automatically.

Successful tasks
~~~~~~~~~~~~~~~~

Successful tasks store the serialized result when possible. If the result
contains ``duration_s``, ``duration_secs``, or a parseable ``duration`` value,
the app stores ``duration_secs`` for statistics.

Skip logging intentionally
~~~~~~~~~~~~~~~~~~~~~~~~~~

To avoid logging an intentionally skipped successful task, return a dictionary
with ``ignore_task_log``:

.. code-block:: python

   return {"status": "skipped", "ignore_task_log": True}

Failure tracebacks
~~~~~~~~~~~~~~~~~~

Failed tasks store:

* Exception type.
* Exception message.
* Stack frames.
* Sanitized local variables in frame context.

Cleanup task
------------

To remove old logs, schedule the bundled task in Celery beat or call it
directly:

.. code-block:: python

   from django_celery_logs.tasks import clear_celery_task_logs

   clear_celery_task_logs.delay()

Task lock helper
----------------

Use ``acquire_lock_or_fail`` to skip work when another task already owns a
cache-backed lock:

.. code-block:: python

   from celery.utils.log import get_task_logger
   from django_celery_logs.utils import acquire_lock_or_fail

   logger = get_task_logger(__name__)

   @app.task(bind=True)
   def import_items(self):
       skipped = acquire_lock_or_fail(self, "import-items", timeout=300, logger=logger)
       if skipped:
           return skipped

       # process the task here
       return {"status": "ok"}
