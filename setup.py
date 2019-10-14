#!/usr/bin/env python
"""Setup functions for the project."""
from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='withings_api',
    version='2.0.0',
    description="Library for the Withings API",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Robbie Van Gorkom',
    author_email='robbie.van.gorkom@protonmail.com',
    url="https://github.com/vangorra/python_withings_api",
    license="MIT License",
    packages=['withings_api'],
    install_requires=[
        'arrow>=0.15.2',
        'requests-oauth>=0.4.1',
        'requests-oauthlib>=1.2',
    ],
    tests_require=[
        'responses>=0.10.6',
    ],
    setup_requires=[
        'wheel>=0.33.6',  # Needed for successful compile of other modules.
        'pytest-runner>=5.1',
        'pytest-cov>=2.8.1',
        'pytest-docstyle>=1.5.0',
        'pytest-mypy>=0.4.1',
        'pytest-flake8>=1.0.4',
        'setuptools-lint>=0.6.0',
    ],
    test_suite='tests.all_tests',
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
    ]
)
