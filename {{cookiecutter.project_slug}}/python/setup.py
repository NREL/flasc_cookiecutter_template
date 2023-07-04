#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

requirements = ["floris>=3.4", "openpyxl", "flasc==1.3.1", "jupyter"]

test_requirements = []

setup(
    author="{{cookiecutter.full_name}}",
    author_email="{{cookiecutter.email}}",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="{{cookiecutter.project_name}}",
    install_requires=requirements,
    long_description="{{cookiecutter.project_description}}",
    include_package_data=True,
    keywords="{{cookiecutter.project_slug}}",
    name="{{cookiecutter.project_name}}",
    packages=find_packages(include=["{{cookiecutter.project_slug}}", "{{cookiecutter.project_slug}}.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    version="0.1.0",
    zip_safe=False,
)
