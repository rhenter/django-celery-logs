Documentation
=============

Update or add new pages
-----------------------

Documentation source files live in ``docs_src/source`` and use RST format.
Translations live in ``docs_src/source/locale/<language>/LC_MESSAGES`` as
gettext ``.po`` files.

.. note::

   If you add a new page, include it in ``docs_src/source/index.rst`` or in a
   child toctree, then run ``make docs`` to update translation catalogs.

Generating the documentation
----------------------------

Build the bilingual HTML documentation locally:

.. code-block:: bash

   make docs

The generated documentation is written to ``docs``:

* ``docs/index.html`` is the language selector.
* ``docs/en/`` contains the English documentation.
* ``docs/pt-br/`` contains the Portuguese documentation.
* ``docs/.nojekyll`` and ``docs/.buildinfo`` are created at the root for
  GitHub Pages.

Cleaning generated documentation
--------------------------------

.. code-block:: bash

   make clean-docs
