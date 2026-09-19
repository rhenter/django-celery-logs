Changelog
=========

All notable changes to this project will be documented in this file.

The project follows semantic versioning while the public API stabilizes.

0.2.0
-----

Released on 2026-09-19.

Added
~~~~~

* Added PyPI-ready package metadata, project URLs, classifiers, and package
  data configuration.
* Added ``uv``-based development workflow with Makefile targets for
  dependencies, tests, Django checks, documentation, builds, and releases.
* Added Sphinx documentation source with installation, settings, admin, usage,
  development, release, changelog, and API pages.
* Added documentation dependencies for local docs development:
  ``sphinx-autobuild``, ``sphinx-intl``, and
  ``sphinxjp.themes.basicstrap``.
* Added badges for PyPI, supported Python versions, license, GitHub Actions,
  coverage, documentation, and open-source status.
* Added English and Portuguese README files.

Changed
~~~~~~~

* Improved README guidance for installing with both ``pip`` and ``uv``.
* Clarified required Celery settings:
  ``CELERY_TASK_IGNORE_RESULT = True`` and
  ``CELERY_RESULT_SERIALIZER = "json"``.
* Clarified that other Celery result apps, such as
  ``django_celery_results``, should not be enabled together with this app.
* Clarified that ``CELERY_RESULT_BACKEND`` and ``CELERY_CACHE_BACKEND`` should
  be removed unless another part of the project explicitly requires them.
* Removed duplicated ``INSTALLED_APPS`` examples from the README and settings
  documentation.
* Documented that Django automatically loads
  ``django_celery_logs.apps.CeleryLogsConfig`` when ``django_celery_logs`` is
  added to ``INSTALLED_APPS``.

Packaging
~~~~~~~~~

* Removed legacy requirements-file workflow in favor of ``pyproject.toml`` and
  ``uv.lock``.
* Kept runtime dependencies in package metadata so installs from PyPI include
  Django, Celery, and boltons automatically.

0.1.0
-----

Released on 2026-09-19.

Added
~~~~~

* Added reusable Django app for storing Celery task execution logs.
* Added Celery signal handlers for successful and failed task executions.
* Added ``TaskLog`` model with task id, task name, queue, worker, args, kwargs,
  result, error message, traceback, timestamp, duration, periodic task flag,
  and traceback context data.
* Added ``TaskConfig`` model for configuring task rerun behavior from Django
  admin.
* Added Django admin task log list with filters, search, pagination controls,
  auto-refresh, and task rerun action.
* Added task detail page with formatted JSON and traceback context.
* Added statistics admin page with charts for throughput, failures, queues,
  workers, periodic tasks, slow tasks, and common errors.
* Added ``clear_celery_task_logs`` cleanup task.
* Added ``acquire_lock_or_fail`` helper for cache-backed task de-duplication.
* Added test project and initial pytest coverage.
