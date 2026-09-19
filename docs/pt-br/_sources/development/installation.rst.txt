Development Installation
========================

Requirements
------------

* Python 3.10 or later
* uv

Development install
-------------------

After forking or checking out:

.. code-block:: bash

   cd django-celery-logs/
   make deps
   uv run --extra dev pre-commit install

The project stores runtime metadata in ``setup.py`` for PyPI and uses
``pyproject.toml`` for the build backend and development extras.

Running tests
-------------

.. code-block:: bash

   make test

Run Django's system checks against the bundled test project:

.. code-block:: bash

   make check

Building the package
--------------------

.. code-block:: bash

   make build

Checking package metadata
-------------------------

.. code-block:: bash

   uv run --extra dev twine check dist/*
