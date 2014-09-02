#!/usr/bin/env python
from setuptools import setup

required = [line for line in open('requirements/base.txt').read().split("\n")]

setup(
    name='withings',
    version='0.3',
    description="Library for the Withings API",
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    url="https://github.com/maximebf/python-withings",
    license = "MIT License",
    packages = ['withings'],
    install_requires = required,
    test_suite='tests.all_tests',
    scripts=['bin/withings'],
    keywords="withings",
    zip_safe = True
)
