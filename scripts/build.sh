#!/usr/bin/env bash

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SELF_DIR/.."

VENV_DIR="venv"

if ! [[ -e "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

if ! [[ `env | grep VIRTUAL_ENV` ]]; then
  source "$VENV_DIR/bin/activate"
fi

python setup.py install
pip install wheel
pip install coverage coveralls
coverage run setup.py test
