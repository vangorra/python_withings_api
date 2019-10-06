#!/usr/bin/env bash

# Clean workspace.
find . -regex '^.*\(__pycache__\|\.py[co]\)$' -delete
rm .tox withings*.egg-info dist build -rf

# Build and test.
tox

# Create dist.
python3 setup.py sdist bdist_wheel

# Update twine to latest version.
python3 -m pip install --upgrade twine

# Upload to pypi.
python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
