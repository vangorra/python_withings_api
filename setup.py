#!/usr/bin/env python
from setuptools import setup

required = [line for line in open('requirements/base.txt').read().split("\n")]

setup(
    name='withings',
    version='1.1.0',
    description="Library for the Withings API",
    author='Robbie Van Gorkom',
    author_email='robbie.van.gorkom@protonmail.com',
    url="https://github.com/vangorra/python_withings_api",
    license = "MIT License",
    packages = ['withings_api'],
    install_requires = required,
    test_suite='tests.all_tests',
    keywords="withings withings",
    zip_safe = True,
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
