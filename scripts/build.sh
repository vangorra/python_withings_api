#!/usr/bin/env bash
set -euf -o pipefail

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SELF_DIR/.."

VENV_DIR=".venv"
PYTHON_BIN="python3"
LINT_PATHS="./withings_api ./tests/ ./scripts/"

if ! [[ $(which "$PYTHON_BIN") ]]; then
  echo "Error: '$PYTHON_BIN' is not in your path."
  exit 1
fi


echo
echo "===Settting up venv==="
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
else
  echo Using existing venv.
fi

if ! [[ $(env | grep VIRTUAL_ENV) ]]; then
  echo "Entering venv."
  set +uf
  source "$VENV_DIR/bin/activate"
  set -uf
else
  echo Already in venv.
fi


echo
echo "===Installing poetry==="
pip install poetry


echo
echo "===Installing dependencies==="
poetry install


echo
echo "===Updating poetry lock file==="
poetry update --lock


echo
echo "===Formatting code==="
if [[ `which black` ]]; then
  black .
else
  echo "Warning: Skipping code formatting. You should use python >= 3.6."
fi


echo
echo "===Lint with flake8==="
flake8


echo
echo "===Lint with mypy==="
mypy .


echo
echo "===Lint with pylint==="
pylint $LINT_PATHS


echo
echo "===Test with pytest==="
pytest


echo
echo "===Building package==="
poetry build


echo "Build complete"
