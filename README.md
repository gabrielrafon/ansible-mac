# Personal Mac setup

Ansible configuration for a personal Apple Silicon Mac running macOS 14 or newer.
Installs declared Homebrew packages, deploys pinned dotfiles, and configures the desktop.
Individual apps may require a newer macOS release. This is a setup recipe, not a disk image
or a lockfile for Homebrew application versions.

## Fresh Mac

1. Complete macOS Setup Assistant and log into the desktop with your normal admin account.
2. Run `xcode-select --install` and finish Apple's installer.
3. Clone this repository and enter its directory.
4. Review `group_vars/all/vars.yml`, including the manual application list.
5. Run:

   ```sh
   make bootstrap
   ```

Bootstrap installs Homebrew if needed, ensures Python 3.13 is available, creates
`.venv`, installs pinned Ansible/lint tools and the pinned collection, then applies
the playbook. Homebrew's installer may ask for your admin password. When casks need
installing or updating, a separate hidden prompt accepts an optional admin password
for their installers. Press Enter to skip if it is not needed. The playbook itself
does not run as root or grant passwordless sudo. For unattended runs, supply
`homebrew_sudo_password` through Ansible Vault or your secret manager; never commit it
or put it in command-line arguments. Ansible's `-K` alone does not supply this variable.

Do not run bootstrap or Ansible under `sudo`. Existing dotfile conflicts intentionally
stop deployment; use the backup procedure in [onboarding](docs/onboarding.md).

## Commands

| Command | Behavior |
| --- | --- |
| `make bootstrap` | Prepare prerequisites and apply the configuration |
| `make deps` | Install pinned project tooling only |
| `make apply` | Install missing declared packages and apply configuration |
| `make check` | Preview changes using Ansible check/diff mode |
| `make update` | Refresh Homebrew metadata and upgrade declared packages only |
| `make lint` | YAML lint, Ansible lint, syntax and shell parsing checks |
| `make test` | Run isolated package validation and real Ansible/Stow regression tests |

`make check` requires Homebrew and project tooling. It does not install missing taps,
Stow, dotfiles or apps; a first-run preview may be incomplete or fail on missing
dependencies. Read-only probes still run and may fetch metadata. It is not a substitute
for testing a fresh installation. Once bootstrapped, preview a subset with
`make check ARGS="--tags finder,dock"`.

Normal apply does not request package upgrades. Homebrew can still install dependency
versions required by a new package, and applications may update themselves.
Unlisted applications are never automatically uninstalled.

## Configuration and ownership

- `group_vars/all/vars.yml` is the shared source of truth: feature flags, packages,
  dotfile revision and explicit source/target mappings.
- Copy `local.yml.example` to ignored `local.yml` for machine-specific overrides.
  Lists replace their defaults completely. Do not put credentials in this file.
- Username and home directory come from the account running on the target.
- Homebrew owns packages; Stow owns the listed dotfile links.
- AeroSpace is the exception: Ansible renders its pinned config under
  `~/.config/aerospace/aerospace.toml`, enabling login startup and removing its
  duplicate SketchyBar startup command. Homebrew services owns SketchyBar.
- Dotfile conflicts and dirty checkouts fail rather than overwrite local files.
  Edit and commit changes in the dotfiles repository, then update the full
  `dotfiles_revision` SHA here deliberately. Removed Stow mappings are not
  automatically unlinked.
- No extra fonts or obsolete Blender 3.5 preferences are copied from the dotfiles
  checkout. Fonts come from Homebrew. The old assets remain available in the checkout.

The old `scirons/dotfiles` URL redirects to `gabrielrafon/dotfiles`; the latter is
now pinned at `9ba95dd4d13b0420c50bf897ed1d886c87503379`.
The unused creative-suite tap is no longer installed. Add it together with explicit
package selections if needed.

### Package catalog changes

The requested applications are retained, with verified identifier corrections:
`whisprflow → wispr-flow`, `tailscale → tailscale-app`,
`todoist → todoist-app`, `trezor-bridge → trezor-bridge-app`.
Terraform comes from `hashicorp/tap`; AeroSpace from `nikitabobko/tap`.

Four requests remain explicit manual actions: Neofetch and `obsidian-cli` were not
found in Homebrew core; Bisq and qBittorrent casks were disabled for Gatekeeper failures
when inspected. They are not replaced or installed through bypasses. The playbook
reports these outstanding items. Speedtest CLI is retained, with a deprecation warning.

## Dependency updates

Ansible, lint tooling, and the collection have exact direct version pins; Python and
transitive Python dependencies are not fully locked. Homebrew packages track available
releases. To update project tooling, edit the requirements files, run `make deps`,
then run `make lint test` and the VM acceptance checks before committing the pins.
`make update` never changes these files or advances the dotfiles revision.

## Test VM

Copy `inventory/test.ini.example` to `inventory/test.ini`, set its real address and
account, and establish SSH trust manually. Prepare Command Line Tools, Homebrew and
Python 3.13 in the VM. The VM must have an active desktop session for UI/services;
otherwise disable both with explicit extra variables.

```sh
make apply ARGS="-i inventory/test.ini"
```

The default inventory contains localhost only. CI performs static validation and
isolated regression tests, never desktop provisioning.
See [VM acceptance tests](docs/testing.md) and the [onboarding checklist](docs/onboarding.md).
