Django Celery Logs
==================

|PyPI latest| |PyPI Version| |PyPI License| |Django Packages| |GitHub Actions Status| |Coverage| |Docs| |Open Source? Yes!|

README em ingles: `README.rst <README.rst>`_.

Django Celery Logs e um app Django reutilizavel que registra sucessos e falhas
de tasks Celery, armazena resultados estruturados e dados de traceback, e expoe
os registros no Django admin.

Ele foi pensado para projetos que precisam de observabilidade de tasks sem
manter o result backend padrao do Celery ativado. Ao executar o Celery com
``CELERY_TASK_IGNORE_RESULT = True``, os payloads de tasks com sucesso nao
precisam ser armazenados por um result backend, o que pode reduzir pressao de
memoria/storage e acelerar o processamento. Django Celery Logs mantem o
historico operacional necessario no banco da sua aplicacao: metadados de task,
resultados JSON estruturados, falhas, duracoes, filas, workers e estatisticas no
admin.

Documentacao
------------

A documentacao esta disponivel no GitHub Pages:

https://rhenter.github.io/django-celery-logs/

As notas de release estao disponiveis no changelog:

`CHANGES <CHANGES.rst>`_.

Requisitos
----------

* Python 3.10 ou superior
* Django 4.2 ou superior
* Celery 5.3 ou superior

Funcionalidades
---------------

* Registra automaticamente execucoes Celery com sucesso e falha por meio de
  signals do Celery.
* Armazena task id, nome, fila, worker, args, kwargs, resultado, mensagem de
  erro, traceback, timestamp e duracao em segundos.
* Captura tracebacks ricos de falha com contexto por frame e variaveis locais
  para acelerar o debug.
* Adiciona telas no Django admin para inspecao de logs e reexecucao de tasks.
* Adiciona modulo administrativo de estatisticas com graficos e metricas de
  throughput, falhas, filas, workers, tasks periodicas, tasks lentas e erros
  comuns.
* Adiciona auto-refresh e paginacao configuravel na listagem de logs para
  monitoramento quase em tempo real.
* Inclui a task de limpeza ``clear_celery_task_logs``.
* Inclui ``acquire_lock_or_fail`` para evitar execucao duplicada usando cache.

Listagem de tasks
-----------------

A listagem de logs mostra metadados da task e um preview do resultado
diretamente na tabela, permitindo analisar execucoes recentes sem abrir o
detalhe de cada task. Ela tambem inclui controles de auto-refresh e filtros
retrateis, mantendo mais espaco de tela disponivel para a lista durante o
monitoramento operacional.

.. image:: https://raw.githubusercontent.com/rhenter/django-celery-logs/main/docs_src/source/_static/images/task-list-preview.png
   :alt: Listagem de tasks do Django Celery Logs com preview do resultado

Stacktrace interativo
---------------------

O detalhe de uma task com falha inclui o stacktrace completo e as variaveis de
contexto sanitizadas capturadas no momento do erro, acelerando o debug em
producao.

.. image:: https://raw.githubusercontent.com/rhenter/django-celery-logs/main/docs_src/source/_static/images/interactive-stacktrace.png
   :alt: Stacktrace interativo do Django Celery Logs com variaveis de contexto

Dashboard de estatisticas
-------------------------

O admin de estatisticas oferece uma visao operacional rapida do throughput do
Celery, falhas, filas, workers, tasks lentas, tasks periodicas e erros comuns.

.. image:: https://raw.githubusercontent.com/rhenter/django-celery-logs/main/docs_src/source/_static/images/statistics.png
   :alt: Dashboard de estatisticas do Django Celery Logs

Instalacao
----------

Instale pelo PyPI:

.. code-block:: bash

    pip install django-celery-logs

Se voce usa ``uv``:

.. code-block:: bash

    uv pip install django-celery-logs

Instale pelo codigo-fonte:

.. code-block:: bash

    git clone git@github.com:rhenter/django-celery-logs.git
    cd django-celery-logs
    pip install .

Se voce usa ``uv``:

.. code-block:: bash

    uv pip install .

Configuracoes
-------------

Configuracoes de resultado do Celery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Django Celery Logs foi pensado para substituir o armazenamento do result backend
do Celery para inspecao de tasks. Configure o Celery para ignorar o backend de
resultado padrao e serializar os dados da task como JSON:

.. code-block:: python

    CELERY_TASK_IGNORE_RESULT = True
    CELERY_RESULT_SERIALIZER = "json"

Nao habilite outros apps de resultado do Celery em ``INSTALLED_APPS`` para o
mesmo objetivo. Por exemplo, remova ``django_celery_results`` se ele estiver
instalado. Somente ``django_celery_logs`` deve ser adicionado, como mostrado na
secao do app Django abaixo.

Se estas configuracoes existirem, remova-as, a menos que outra parte do projeto
realmente dependa delas:

.. code-block:: python

    CELERY_RESULT_BACKEND = "..."
    CELERY_CACHE_BACKEND = "..."

App Django
~~~~~~~~~~

Adicione o app ao ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "django_celery_logs",
        ...
    ]

Execute as migrations:

.. code-block:: bash

    python manage.py migrate

Opcionalmente, configure por quantos dias os logs serao mantidos pela task de
limpeza:

.. code-block:: python

    CELERY_TASK_LOGS_EXPIRES = 7

Admin
-----

O pacote inclui templates e assets estaticos para o Django admin:

* Listagem de logs de tasks com auto-refresh, filtros colapsaveis, tamanho de
  pagina configuravel, preview do resultado JSON e atalho para estatisticas.
* Detalhe do log com acao de reexecucao.
* Estatisticas de tasks com cards, graficos, top tasks, tasks mais lentas,
  distribuicao por fila/worker, distribuicao de tasks periodicas e principais
  mensagens de erro.

Auto-refresh
~~~~~~~~~~~~

A listagem de logs inclui controle de auto-refresh para monitoramento
operacional. Voce pode manter o admin aberto enquanto os workers processam
tasks e atualizar a lista a cada 5, 10, 30 ou 60 segundos. O intervalo
selecionado fica salvo no navegador, entao a pagina mantem o mesmo
comportamento apos recarregar.

Uso
---

Quando o Django carrega o app, os signals ``task_success`` e ``task_failure``
do Celery criam registros em ``TaskLog`` automaticamente.

Para remover logs antigos, agende a task incluida no Celery beat ou chame-a
diretamente:

.. code-block:: python

    from django_celery_logs.tasks import clear_celery_task_logs

    clear_celery_task_logs.delay()

Para evitar o log de uma task com sucesso que foi intencionalmente ignorada,
retorne um dicionario com ``ignore_task_log``:

.. code-block:: python

    return {"status": "skipped", "ignore_task_log": True}

Contribuindo
------------

Pull requests sao bem-vindos.

Desenvolvimento
---------------

Este projeto usa ``uv`` para comandos de desenvolvimento local. Instale as
dependencias de desenvolvimento com:

.. code-block:: bash

    make deps

Execute a suite de testes:

.. code-block:: bash

    make test

Execute os system checks do Django contra o projeto de teste incluido:

.. code-block:: bash

    make check

Gere o source distribution e o wheel:

.. code-block:: bash

    make build

Targets uteis do Makefile:

* ``make deps`` instala o projeto e as dependencias de desenvolvimento com
  ``uv sync --extra dev``.
* ``make test`` executa ``uv run --extra dev pytest``.
* ``make check`` executa ``django check`` com as settings do projeto de teste.
* ``make lint`` executa os hooks do pre-commit.
* ``make docs`` gera a documentacao Sphinx.
* ``make clean`` remove arquivos de build, cache, coverage e bytecode.
* ``make build`` cria ``sdist`` e ``wheel`` com ``uv build``.
* ``make release`` cria a tag da versao atual e envia ``dist/*`` com twine.

Licenca
-------

MIT

.. |PyPI latest| image:: https://img.shields.io/pypi/pyversions/django_celery_logs.svg
   :target: https://pypi.org/project/django-celery-logs/
   :alt: Versoes de Python suportadas

.. |PyPI Version| image:: https://img.shields.io/pypi/v/django_celery_logs.svg
   :target: https://pypi.org/project/django-celery-logs/
   :alt: Versao no PyPI

.. |PyPI License| image:: https://img.shields.io/pypi/l/django_celery_logs.svg
   :target: https://pypi.org/project/django-celery-logs/
   :alt: Licenca

.. |Django Packages| image:: https://img.shields.io/badge/PyPI-django--celery--logs--tags-8c3c26.svg
   :target: https://djangopackages.org/packages/p/django-celery-logs/
   :alt: Latest on Django Packages

.. |GitHub Actions Status| image:: https://github.com/rhenter/django-celery-logs/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/rhenter/django-celery-logs/actions/workflows/ci.yml
   :alt: Status do GitHub Actions

.. |Coverage| image:: https://codecov.io/gh/rhenter/django-celery-logs/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/rhenter/django-celery-logs
   :alt: Cobertura

.. |Docs| image:: https://img.shields.io/static/v1?label=DOC&message=GitHub%20Pages&color=blue
   :target: https://rhenter.github.io/django-celery-logs/
   :alt: Documentacao

.. |Open Source? Yes!| image:: https://badgen.net/badge/Open%20Source%3F/Yes%21/blue
   :target: https://github.com/rhenter/django-celery-logs
   :alt: Open Source? Yes!
