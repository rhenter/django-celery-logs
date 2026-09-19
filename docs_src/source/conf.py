import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "test-django-project"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_django_project.settings")

try:
    import django

    django.setup()
except Exception:
    pass

project = "Django Celery Logs"
copyright = "2026, Rafael Henter"
author = "Rafael Henter"
version = "0.1.0"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = []
source_suffix = ".rst"
master_doc = "index"
language = "en"
pygments_style = None
todo_include_todos = True

html_theme = "alabaster"
html_static_path = ["_static"]
htmlhelp_basename = "DjangoCeleryLogsDoc"

autodoc_member_order = "bysource"
autodoc_typehints = "description"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": ("https://docs.djangoproject.com/en/stable/", None),
    "celery": ("https://docs.celeryq.dev/en/stable/", None),
}

latex_documents = [
    (master_doc, "DjangoCeleryLogs.tex", "Django Celery Logs Documentation", author, "manual"),
]

man_pages = [
    (master_doc, "django-celery-logs", "Django Celery Logs Documentation", [author], 1),
]

texinfo_documents = [
    (
        master_doc,
        "DjangoCeleryLogs",
        "Django Celery Logs Documentation",
        author,
        "DjangoCeleryLogs",
        "Reusable Django app to store and inspect Celery task logs in Django admin.",
        "Miscellaneous",
    ),
]
