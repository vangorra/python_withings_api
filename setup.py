#!/usr/bin/env python
"""Setup functions for the project."""
from setuptools import setup
import setuptools_black

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="withings_api",
    version="2.1.0",
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
    cmdclass={"build": setuptools_black.BuildCommand},
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
