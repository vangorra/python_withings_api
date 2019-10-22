#!/usr/bin/env bash
set -euf -o pipefail

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PUBLISH_PASSWORD="$1"

"$SELF_DIR/build.sh"

echo
echo "===Publishing package==="
poetry publish --username __token__ --password "$PUBLISH_PASSWORD"
