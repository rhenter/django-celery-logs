Django Celery Logs
==================

|PyPI latest| |PyPI Version| |PyPI License| |GitHub Actions Status| |Coverage| |Docs| |Open Source? Yes!|

Django Celery Logs is a reusable Django app that records Celery task successes
and failures, stores structured results and traceback data, and exposes the
records in Django admin.

It is designed for projects that want task observability without keeping
Celery's default result backend enabled. By running Celery with
``CELERY_TASK_IGNORE_RESULT = True``, successful task payloads do not need to be
stored by a result backend, which can reduce memory/storage pressure and speed
up task processing. Django Celery Logs keeps the operational history you need in
your Django database instead: task metadata, structured JSON results, failures,
durations, queues, workers, and admin statistics.

Documentation
-------------

The documentation is available on GitHub Pages:

https://rhenter.github.io/django-celery-logs/

Requirements
------------

* Python 3.10 or later
* Django 4.2 or later
* Celery 5.3 or later

Features
--------

* Logs successful and failed Celery task executions through Celery signals.
* Stores task id, name, queue, worker, args, kwargs, result, error message,
  traceback, timestamp, and duration in seconds.
* Captures rich failure tracebacks with frame-by-frame context and local
  variables to make debugging failed tasks faster.
* Adds Django admin pages for log inspection and task re-run.
* Adds an admin statistics module with charts and metrics for throughput,
  failures, queues, workers, periodic tasks, slow tasks, and common errors.
* Adds auto-refresh and configurable pagination controls to the admin task log
  list for near real-time monitoring.
* Includes a cleanup task named ``clear_celery_task_logs``.
* Includes ``acquire_lock_or_fail`` for cache-backed task de-duplication.

Installation
------------

Install from PyPI:

.. code-block:: bash

    pip install django-celery-logs

If you use ``uv``:

.. code-block:: bash

    uv pip install django-celery-logs

Install from source:

.. code-block:: bash

    git clone git@github.com:rhenter/django-celery-logs.git
    cd django-celery-logs
    pip install .

If you use ``uv``:

.. code-block:: bash

    uv pip install .

Settings
--------

Celery result settings
~~~~~~~~~~~~~~~~~~~~~~

Django Celery Logs is intended to replace Celery result-backend storage for task
inspection. Configure Celery to ignore the default result backend and serialize
task data as JSON:

.. code-block:: python

    CELERY_TASK_IGNORE_RESULT = True
    CELERY_RESULT_SERIALIZER = "json"

Do not enable other Celery result apps in ``INSTALLED_APPS`` for the same
purpose. For example, remove ``django_celery_results`` if it is installed.
Only ``django_celery_logs`` should be added, as shown in the Django app section
below.

If these settings exist, remove them unless another part of your project really
depends on them:

.. code-block:: python

    CELERY_RESULT_BACKEND = "..."
    CELERY_CACHE_BACKEND = "..."

Django app
~~~~~~~~~~

Add the app to ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "django_celery_logs",
        ...
    ]

Run migrations:

.. code-block:: bash

    python manage.py migrate

Optionally configure how many days logs are retained by the cleanup task:

.. code-block:: python

    CELERY_TASK_LOGS_EXPIRES = 7

Admin
-----

The package includes Django admin templates and static assets for:

* Task log list with auto-refresh, collapsible filters, configurable page size,
  JSON result preview, and a shortcut to statistics.
* Task log detail with a re-run action.
* Task statistics with cards, charts, top tasks, slowest tasks, queue/worker
  distribution, periodic task distribution, and top error messages.

Failure tracebacks are stored as structured JSON and rendered interactively in
the admin, including exception type, message, stack frames, and sanitized local
variables from the frame context.

Auto-refresh
~~~~~~~~~~~~

The task log list includes an auto-refresh control for operational monitoring.
You can keep the admin open while workers are processing tasks and refresh the
list every 5, 10, 30, or 60 seconds. The selected interval is saved in the
browser, so the page keeps the same refresh behavior after reloads.

Usage
-----

Once Django loads the app, Celery's ``task_success`` and ``task_failure``
signals create ``TaskLog`` records automatically.

To remove old logs, schedule the bundled task in Celery beat or call it
directly:

.. code-block:: python

    from django_celery_logs.tasks import clear_celery_task_logs

    clear_celery_task_logs.delay()

To avoid logging an intentionally skipped successful task, return a dictionary
with ``ignore_task_log``:

.. code-block:: python

    return {"status": "skipped", "ignore_task_log": True}

Contributing
------------

Pull requests are welcome.

Development
-----------

This project uses ``uv`` for local development commands. Install development
dependencies with:

.. code-block:: bash

    make deps

Run the test suite:

.. code-block:: bash

    make test

Run Django's system checks against the bundled test project:

.. code-block:: bash

    make check

Build the source distribution and wheel:

.. code-block:: bash

    make build

Useful Makefile targets:

* ``make deps`` installs the project and development dependencies with
  ``uv sync --extra dev``.
* ``make test`` runs ``uv run --extra dev pytest``.
* ``make check`` runs ``django check`` with the test project settings.
* ``make lint`` runs pre-commit hooks.
* ``make docs`` builds the Sphinx documentation.
* ``make clean`` removes build, cache, coverage, and bytecode files.
* ``make build`` creates ``sdist`` and ``wheel`` with ``uv build``.
* ``make release`` tags the current version and uploads ``dist/*`` with twine.

License
-------

MIT

.. |PyPI latest| image:: https://img.shields.io/pypi/pyversions/django-celery-logs.svg
   :target: https://pypi.org/project/django-celery-logs/
   :alt: Supported Python versions

.. |PyPI Version| image:: https://img.shields.io/pypi/v/django-celery-logs.svg
   :target: https://pypi.org/project/django-celery-logs/
   :alt: PyPI version

.. |PyPI License| image:: https://img.shields.io/pypi/l/django-celery-logs.svg
   :target: https://pypi.org/project/django-celery-logs/
   :alt: License

.. |GitHub Actions Status| image:: https://github.com/rhenter/django-celery-logs/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/rhenter/django-celery-logs/actions/workflows/ci.yml
   :alt: GitHub Actions status

.. |Coverage| image:: https://codecov.io/gh/rhenter/django-celery-logs/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/rhenter/django-celery-logs
   :alt: Coverage

.. |Docs| image:: https://img.shields.io/static/v1?label=DOC&message=GitHub%20Pages&color=blue
   :target: https://rhenter.github.io/django-celery-logs/
   :alt: Documentation

.. |Open Source? Yes!| image:: https://badgen.net/badge/Open%20Source%3F/Yes%21/blue
   :target: https://github.com/rhenter/django-celery-logs
   :alt: Open Source? Yes!
