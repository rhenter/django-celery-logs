Django Celery Logs documentation
================================

Django Celery Logs is a reusable Django app for projects that want Celery task
observability without keeping Celery's result backend enabled. It records task
successes and failures through Celery signals, stores structured JSON data, and
exposes logs, tracebacks, task reruns, and statistics in Django admin.

Features
--------

.. include:: features.rst

Task List
---------

The task log list shows task metadata and a result preview directly in the
table, so teams can scan recent executions without opening every task detail
page. It also includes auto-refresh controls and collapsible filters, keeping
more screen space available for the task list during operational monitoring.

.. image:: _static/images/task-list-preview.png
   :alt: Django Celery Logs task list with result preview

Interactive Stacktrace
----------------------

Failed task details include the full stacktrace and the sanitized context
variables captured at the moment of the error, making production debugging much
faster.

.. image:: _static/images/interactive-stacktrace.png
   :alt: Django Celery Logs interactive stacktrace with context variables

Statistics Dashboard
--------------------

The statistics admin gives teams a quick operational view of Celery throughput,
failures, queues, workers, slow tasks, periodic tasks, and common errors.

.. image:: _static/images/statistics.png
   :alt: Django Celery Logs statistics dashboard

Quickstart
----------

.. toctree::
   :maxdepth: 2

   quickstart/installation.rst
   settings.rst

User Guide
----------

.. toctree::
   :maxdepth: 2

   admin.rst
   usage.rst
   api/index.rst

Development
-----------

.. toctree::
   :maxdepth: 1

   development/installation.rst
   development/documentation.rst
   development/release.rst

Other
-----

.. toctree::
   :maxdepth: 1

   changelog.rst
