Django Celery Logs documentation
================================

Django Celery Logs is a reusable Django app for projects that want Celery task
observability without keeping Celery's result backend enabled. It records task
successes and failures through Celery signals, stores structured JSON data, and
exposes logs, tracebacks, task reruns, and statistics in Django admin.

Features
--------

.. include:: features.rst

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
