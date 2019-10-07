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
"$SELF_DIR/ci-install.sh"

echo "Building."
"$SELF_DIR/ci-build.sh"

echo "Build complete."
