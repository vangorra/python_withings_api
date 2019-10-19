#!/usr/bin/env bash
set -euf -o pipefail

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SELF_DIR/.."

VENV_DIR="venv"
PYTHON_BIN="python3"
FORMAT_PYTHON_VERSION="Python 3.7"

if ! [[ `which "$PYTHON_BIN"` ]]; then
  echo "Error: '$PYTHON_BIN' is not in your path."
  exit 1
fi

CODE_FORMATTING_ENABLED=$("$PYTHON_BIN" --version | grep -Ec "^$FORMAT_PYTHON_VERSION" || true)

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

if ! [[ `env | grep VIRTUAL_ENV` ]]; then
  echo "Entering venv."
  source "$VENV_DIR/bin/activate"
else
  echo Already in venv.
fi


echo
echo "===Installing dependencies==="
python setup.py install


echo
echo "===Setting up black==="
# This runs  reliably on python 3.7, haven't testest python 3.6 and black won't install on python 3.5. So we're
# conditionally running these checks. Any bad formatting will be cause in the 3.7 build in CI.
if [[ "$CODE_FORMATTING_ENABLED" > "0" ]]; then
  # Run check only on ci builds. Format code on local builds.
  BLACK_ARGS=""
  if [[ -n "${CI:-}" ]]; then
    BLACK_ARGS="--check"
  fi

  echo "Installing black."
  pip install setuptools-black==0.1.4

  echo "Formatting code with args '$BLACK_ARGS'."
  python setup.py format $BLACK_ARGS
else
  echo "Skipping code format checks as black doesn't work well python versions less than $FORMAT_PYTHON_VERSION."
fi


echo
echo "===Running tests==="
python setup.py test

echo "Build complete."
