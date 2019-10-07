#!/usr/bin/env bash
set -euf -o pipefail

echo "Installing package dependencies."
python setup.py install

# Needs separate install before next line otherwise the next line will fail.
echo "Installing wheel."
pip install wheel

# Cannot be included in setup.py as setuptools doesn't support coverage. Sigh.
echo "Intalling coverage and coveralls."
pip install coverage coveralls
