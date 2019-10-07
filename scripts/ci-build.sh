#!/usr/bin/env bash
set -euf -o pipefail

# setuptools does not support coverage, so we have to use coverage to run setuptools. Yuck.
echo "Running tests and coverage report."
coverage run setup.py test
