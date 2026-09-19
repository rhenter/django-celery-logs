Documentation
=============

Update or add new pages
-----------------------

Documentation source files live in ``docs_src/source`` and use RST format.

.. note::

   If you add a new page, include it in ``docs_src/source/index.rst`` or in a
   child toctree.

Generating the documentation
----------------------------

Build the HTML documentation locally:

.. code-block:: bash

   cd docs_src
   uv run --extra dev sphinx-build -b html source build/html

You can also use the Sphinx Makefile:

.. code-block:: bash

   cd docs_src
   uv run --extra dev make html

Cleaning generated documentation
--------------------------------

.. code-block:: bash

   rm -rf docs_src/build
