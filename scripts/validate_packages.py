#!/usr/bin/env python3
"""Read Homebrew metadata without installing or upgrading packages."""
import json
import os
import subprocess
import sys


def validate(manifest, runner=subprocess.run):
    errors, warnings = [], []
    for kind, flag in (("formulae", "--formula"), ("casks", "--cask")):
        names = manifest[kind]
        if not names:
            continue
        result = runner(
            ["/opt/homebrew/bin/brew", "info", "--json=v2", flag, *names],
            capture_output=True, text=True, check=False,
            env={**os.environ, "HOMEBREW_NO_AUTO_UPDATE": "1"},
        )
        if result.returncode:
            errors.append(f"Cannot resolve {kind}: {result.stderr.strip()}")
            continue
        try:
            packages = json.loads(result.stdout)[kind]
        except (ValueError, KeyError, TypeError):
            errors.append(f"Invalid Homebrew metadata for {kind}")
            continue
        if len(packages) != len(names):
            errors.append(f"Homebrew returned an incomplete or duplicate {kind} inventory")
        for package in packages:
            name = package.get("full_name", package.get("token", package.get("name")))
            if package.get("disabled"):
                errors.append(f"{name}: disabled ({package.get('disable_reason', 'unknown reason')})")
            elif package.get("deprecated"):
                warnings.append(f"{name}: deprecated ({package.get('deprecate_reason', 'unknown reason')})")
    return errors, warnings


def main():
    errors, warnings = validate(json.loads(sys.argv[1]))
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("Correct the package declarations or explicitly document a manual installation before retrying.", file=sys.stderr)
        return 1
    print("All declared Homebrew packages resolved and are enabled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
