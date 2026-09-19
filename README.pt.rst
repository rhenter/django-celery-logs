Django Celery Logs
==================

Django Celery Logs e uma app Django reutilizavel para registrar execucoes do
Celery, guardar resultados e tracebacks estruturados, e consultar tudo pelo
Django admin.

A biblioteca foi pensada para observar tarefas sem manter o result backend
padrao do Celery. Use ``CELERY_TASK_IGNORE_RESULT = True`` para reduzir uso de
memoria/storage e manter o historico operacional no banco da aplicacao.

Funcionalidades
---------------

* Registro automatico de sucessos e falhas via signals do Celery.
* Stacktrace estruturado das falhas, com frames e variaveis locais sanitizadas.
* Admin com listagem de logs, preview JSON, re-execucao de tasks e paginacao configuravel.
* Auto refresh na listagem com intervalos de 5, 10, 30 e 60 segundos.
* Modulo de estatisticas com cards, graficos, top tasks, tasks lentas, filas, workers e erros comuns.

Instalacao
----------

.. code-block:: bash

    pip install django-celery-logs

Se voce usa ``uv``:

.. code-block:: bash

    uv pip install django-celery-logs

Configuracao
------------

Configure o Celery para ignorar o backend padrao de resultados:

.. code-block:: python

    CELERY_TASK_IGNORE_RESULT = True
    CELERY_RESULT_SERIALIZER = "json"

Nao use apps concorrentes de resultado do Celery, como ``django_celery_results``,
junto com esta biblioteca. Se existirem e nao forem exigidas por outra parte do
projeto, remova tambem:

.. code-block:: python

    CELERY_RESULT_BACKEND = "..."
    CELERY_CACHE_BACKEND = "..."

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "django_celery_logs",
        ...
    ]

Depois execute:

.. code-block:: bash

    python manage.py migrate

A configuracao opcional ``CELERY_TASK_LOGS_EXPIRES`` define por quantos dias os
logs serao mantidos pela task de limpeza.
