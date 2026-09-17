#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -x .venv/bin/ansible-playbook ]]; then
  printf '%s\n' 'Missing pinned Ansible environment. Run make deps or make bootstrap first.' >&2
  exit 1
fi
action="${1:-apply}"
shift || true
case "$action" in
  apply) exec .venv/bin/ansible-playbook main.yml "$@" ;;
  check) exec .venv/bin/ansible-playbook main.yml --check --diff "$@" ;;
  update) exec .venv/bin/ansible-playbook main.yml --tags brew "$@" -e '{"update_packages": true}' ;;
  *) printf 'Unknown action: %s\n' "$action" >&2; exit 2 ;;
esac
