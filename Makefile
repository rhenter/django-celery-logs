clean: clean-eggs clean-build clean-htmlcov clean-docs
	@find . -iname '*.pyc' -delete
	@find . -iname '*.pyo' -delete
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '__pycache__' -delete
	@rm -rf .coverage .pytest_cache

clean-htmlcov:
	@rm -fr htmlcov

clean-docs:
	@rm -fr docs_src/build/

clean-eggs:
	@find . -name '*.egg' -print0 | xargs -0 rm -rf --
	@rm -rf .eggs/

clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

lint:
	uv run --extra dev pre-commit run -av

deps:
	uv sync --extra dev

uv-dev: deps

test:
	uv run --extra dev pytest

check:
	PYTHONPATH=test-django-project:. DJANGO_SETTINGS_MODULE=test_django_project.settings uv run --extra dev python -m django check

docs:
	cd docs_src && uv run --extra dev sphinx-build -b html source build/html

build: clean
	uv build

release: build
	git tag `uv run python setup.py -q version`
	git push origin `uv run python setup.py -q version`
	uv run --extra dev twine upload dist/*
