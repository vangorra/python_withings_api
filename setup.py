#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='withings',
    version='0.1',
    description="Library for the Withings API",
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    url="https://github.com/maximebf/python-withings",
    license = "MIT License",
    packages = find_packages(),
    keywords="withings",
    zip_safe = True
)
