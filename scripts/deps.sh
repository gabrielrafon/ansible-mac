#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python_bin="${MAC_SETUP_PYTHON:-/opt/homebrew/bin/python3.13}"
if [[ ! -x "$python_bin" ]]; then
  printf '%s\n' "Missing $python_bin. Run bootstrap or set MAC_SETUP_PYTHON to Python 3.13+." >&2
  exit 1
fi
"$python_bin" -c 'import sys; assert sys.version_info >= (3, 13), "Python 3.13+ is required"'
if [[ ! -x .venv/bin/python ]]; then
  "$python_bin" -m venv .venv
fi
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/ansible-galaxy collection install -r requirements.yml -p .ansible/collections
