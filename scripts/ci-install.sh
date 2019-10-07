#!/usr/bin/env bash
set -euf -o pipefail

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SELF_DIR/.."

# Needs separate install before next line otherwise the next line will fail.
echo "Installing wheel."
pip install wheel

echo "Installing package dependencies."
python setup.py install
