#!/usr/bin/env bash
set -euf -o pipefail

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SELF_DIR/.."

VENV_DIR="venv"
PYTHON_BIN="python3"

BLACK_ARGS=""
if [[ -n "${CI:-}" ]]; then
  BLACK_ARGS="--check"
fi

if ! [[ `which "$PYTHON_BIN"` ]]; then
  echo "Error: '$PYTHON_BIN' is not in your path."
  exit 1
fi

# Not sure why I couldn't use "if ! [[ `"$PYTHON_BIN" -c 'import venv'` ]]" below. It just never worked when venv was
# present.
VENV_NOT_INSTALLED=$("$PYTHON_BIN" -c 'import venv' 2>&1 | grep -ic ' No module named' || true)
if [[ "$VENV_NOT_INSTALLED" -gt "0" ]]; then
  echo "Error: The $PYTHON_BIN 'venv' module is not installed."
  exit 1
fi

if ! [[ -e "$VENV_DIR" ]]; then
  echo "Creating venv."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

if ! [[ `env | grep VIRTUAL_ENV` ]]; then
  echo "Entering venv."
  source "$VENV_DIR/bin/activate"
fi

echo "Installing build dependencies."
pip install -r "$SELF_DIR/../requirements.txt"

echo "Running module dependencies."
python setup.py install

echo "Formatting code."
python setup.py format

echo "Running tests."
python setup.py test

echo "Running pylint";
python setup.py lint

echo "Build complete."
