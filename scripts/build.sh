#!/usr/bin/env bash
set -euf -o pipefail

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SELF_DIR/.."

VENV_DIR="venv"

if ! [[ -e "$VENV_DIR" ]]; then
  echo "Creating venv."
  python3 -m venv "$VENV_DIR"
fi

if ! [[ `env | grep VIRTUAL_ENV` ]]; then
  echo "Entering venv."
  source "$VENV_DIR/bin/activate"
fi

echo "Installing dependencies."
python setup.py install

#echo "Linting with flake8."
#python setup.py flake8
#
#echo "Linting with pylint."
#python setup.py lint

echo "Running tests."
python setup.py test

echo "Build complete."
