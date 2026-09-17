#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 || "$(id -u)" == 0 ]]; then
  printf '%s\n' 'Run as your normal account on native Apple Silicon macOS, without sudo or Rosetta.' >&2
  exit 1
fi
if ! /usr/bin/xcode-select -p >/dev/null 2>&1; then
  printf '%s\n' 'Install Command Line Tools with xcode-select --install, finish the installer, then retry.' >&2
  exit 1
fi
if [[ ! -x /opt/homebrew/bin/brew ]]; then
  installer="$(mktemp -t ansible-mac-homebrew)"
  trap 'rm -f "$installer"' EXIT
  curl --fail --show-error --location --retry 3 https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh -o "$installer"
  /bin/bash "$installer"
fi
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
export HOMEBREW_NO_AUTO_UPDATE=1
export HOMEBREW_NO_INSTALL_UPGRADE=1
if [[ ! -x /opt/homebrew/bin/python3.13 ]]; then
  brew install python@3.13
fi
bash scripts/deps.sh
bash scripts/run.sh apply "$@"
