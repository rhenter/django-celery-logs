Release
=======

To release a new version:

* Update ``CHANGES.rst``.
* Review ``setup.py`` metadata and dependencies.
* Review documentation.
* Run tests with ``make test``.
* Run Django checks with ``make check``.
* Build with ``make build``.
* Check distribution metadata with ``uv run --extra dev twine check dist/*``.
* Commit and push changes.
* Release with ``make release``.
