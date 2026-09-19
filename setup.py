import codecs
import os
import re
from typing import List

from setuptools import Command, find_namespace_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def get_version_from_changelog():
    with codecs.open(os.path.join(here, "CHANGES.rst"), encoding="utf-8") as file_obj:
        changelog_content = file_obj.read()

    match = re.search(r"^(\d+\.\d+\.\d+)\n-+\n", changelog_content, re.MULTILINE)
    if not match:
        raise RuntimeError("Unable to find a release version in CHANGES.rst.")

    return match.group(1)


version = get_version_from_changelog()

with codecs.open(os.path.join(here, "README.rst"), encoding="utf-8") as file_obj:
    long_description = file_obj.read()

with codecs.open(os.path.join(here, "CHANGES.rst"), encoding="utf-8") as file_obj:
    changelog = file_obj.read()

install_requires = [
    "boltons>=24.0",
    "celery>=5.3",
    "django>=4.2",
]


class VersionCommand(Command):
    """Custom command to print the library version."""

    description = "print library version"
    user_options: List = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print(version)


setup(
    author="Rafael Henter",
    author_email="rafael@henter.com.br",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 5.2",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    cmdclass={"version": VersionCommand},
    description="Reusable Django app to store and inspect Celery task logs in Django admin.",
    install_requires=install_requires,
    keywords="django celery logs admin task monitoring",
    license="MIT",
    long_description=f"{long_description}\n\n{changelog}",
    long_description_content_type="text/x-rst",
    name="django-celery-logs",
    package_data={
        "django_celery_logs": [
            "static/django_celery_logs/css/*.css",
            "static/django_celery_logs/js/*.js",
            "templates/admin/celery_log/tasklog/*.html",
            "templates/admin/celery_log/tasklogstatistics/*.html",
        ]
    },
    include_package_data=False,
    packages=find_namespace_packages(include=["django_celery_logs", "django_celery_logs.*"]),
    project_urls={
        "Source": "https://github.com/rhenter/django-celery-logs",
        "Issues": "https://github.com/rhenter/django-celery-logs/issues",
    },
    python_requires=">=3.10",
    url="https://github.com/rhenter/django-celery-logs",
    version=version,
)
