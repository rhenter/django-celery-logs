Settings
========

Celery result backend
---------------------

Django Celery Logs is intended to replace Celery result-backend storage for
task inspection. Configure Celery to ignore the default result backend and
serialize task data as JSON:

.. code-block:: python

   CELERY_TASK_IGNORE_RESULT = True
   CELERY_RESULT_SERIALIZER = "json"

Do not enable other Celery result apps in ``INSTALLED_APPS`` for the same
purpose. For example, remove ``django_celery_results`` if it is installed:

.. code-block:: python

   INSTALLED_APPS = [
       ...
       # "django_celery_results",
       "django_celery_logs",
       ...
   ]

If these settings exist, remove them unless another part of your project really
depends on them:

.. code-block:: python

   CELERY_RESULT_BACKEND = "..."
   CELERY_CACHE_BACKEND = "..."

Django app
----------

Add the app to ``INSTALLED_APPS``:

.. code-block:: python

   INSTALLED_APPS = [
       ...
       "django_celery_logs",
       ...
   ]

Django 4.2+ automatically loads ``django_celery_logs.apps.CeleryLogsConfig``
for this app. The app config imports ``django_celery_logs.signals`` in
``ready()``, which registers the Celery signal handlers.

Run migrations:

.. code-block:: bash

   python manage.py migrate

Log retention
-------------

Optionally configure how many days logs are retained by the cleanup task:

.. code-block:: python

   CELERY_TASK_LOGS_EXPIRES = 7

If this setting is not defined, the app uses ``2`` days by default.
