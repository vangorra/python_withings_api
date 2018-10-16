#!/usr/bin/env python
from setuptools import setup

required = [line for line in open('requirements/base.txt').read().split("\n")]

setup(
    name='nokia',
    version='1.1.0',
    description="Library for the Nokia Health API",
    author='ORCAS',
    author_email='developer@orcasinc.com',
    url="https://github.com/orcasgit/python-nokia",
    license = "MIT License",
    packages = ['nokia'],
    install_requires = required,
    test_suite='tests.all_tests',
    scripts=['bin/nokia'],
    keywords="withings nokia",
    zip_safe = True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ]
)
