#!/usr/bin/env python
"""Setup functions for the project."""
from setuptools import setup

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()
setup(
    name="withings_api",
    version="2.1.1",
    description="Library for the Withings API",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Robbie Van Gorkom",
    author_email="robbie.van.gorkom@protonmail.com",
    url="https://github.com/vangorra/python_withings_api",
    license="MIT License",
    packages=["withings_api"],
    install_requires=[
        "arrow>=0.15.2",
        "requests-oauth>=0.4.1",
        "requests-oauthlib>=1.2",
    ],
    setup_requires=[
        "coverage==4.5.4",
        "flake8==3.7.8",
        "mypy==0.740",
        "pydocstyle==4.0.1",
        "pylint==2.4.3",
        "pytest==5.2.1",
        "pytest-cov==2.8.1",
        "pytest-docstyle==1.5.0",
        "pytest-flake8==1.0.4",
        "pytest-mypy==0.4.1",
        "pytest-pylint==0.14.1",
        "pytest-runner==5.1",
        "responses==0.10.6",
        "wheel==0.33.6",  # Needed for successful compile of other modules.
    ],
    keywords="withings api",
    zip_safe=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
