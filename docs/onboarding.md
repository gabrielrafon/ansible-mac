# Onboarding and recovery

## Existing dotfiles

The playbook never uses Stow adoption or forced Git checkout. Before applying to an
existing account, inspect any paths listed in Stow's conflict report. Back up each
conflicting file or directory and move it aside only after reviewing it. For example,
to preserve a conflicting regular `.zshrc`:

```sh
backup_dir="$(mktemp -d "$HOME/ansible-mac-backup.XXXXXX")"
cp -p "$HOME/.zshrc" "$backup_dir/.zshrc"
cmp "$HOME/.zshrc" "$backup_dir/.zshrc"
# After confirming the backup matches:
mv "$HOME/.zshrc" "$backup_dir/.zshrc.original"
make apply ARGS="--tags dotfiles"
```

For a directory use an appropriate recursive backup and inspect it before moving the
original. For symlinks, inspect both the link and its destination; preserve the link
and back up destination contents before any changes. Do not bulk-remove your home or
`.config` directory. To adopt wanted settings, merge them into the dotfiles repository,
commit and push them, and explicitly update the pinned SHA in this repository.

A dirty checkout stops setup before Git updates or links. This includes changes made
by apps through symlinks. Review `git -C ~/.dotfiles status` and preserve those changes
before retrying. Updating a pin does not automatically remove obsolete Stow links;
review and unstow removed packages using the previous checkout first.

AeroSpace refuses an existing `~/.aerospace.toml`, a symlinked destination, or an
unmanaged `~/.config/aerospace/aerospace.toml`. Back up and move those paths explicitly.
Ansible backs up subsequent changes to its own generated AeroSpace file. Customize
the pinned source or template rather than the generated file.

## Finish setup

- [ ] Resolve the `manual_applications` list: Neofetch, the intended Obsidian CLI,
      Bisq and qBittorrent. Review their official installation options; no security
      bypass is included in this playbook.
- [ ] Approve Accessibility for AeroSpace and any other apps that need it.
- [ ] Approve Automation access to System Events for the terminal/controller when
      prompted for wallpaper changes. If denied, enable it in System Settings and retry.
- [ ] Review Login Items / background permissions for AeroSpace and SketchyBar.
- [ ] Sign into Apple/iCloud and selected apps; activate licenses where needed.
- [ ] Set up Tailscale and other account-bound services interactively.
- [ ] Restore SSH/GPG access from your chosen secure source. Secretive keys tied to a
      previous device may require creating and authorizing a new device key.
- [ ] Restore documents, vaults, projects and app data from your chosen backup/sync source.
- [ ] Configure backup credentials and destinations for restic/rclone, then verify a
      small restore. Installing their executables does not configure backups.
- [ ] Review the pinned shell config: it still references Brave and Neofetch even
      though Brave is not requested and Neofetch needs manual resolution. Update those
      preferences in the dotfiles repository if desired; this setup does not re-add Brave.
- [ ] Restart or log out/in, then verify terminal, window manager and bar behavior.
- [ ] Run `make check` and investigate remaining drift.

Record credential locations and recovery instructions in your password manager or
another private recovery record, not Git. This repository does not know your backup
location or secret store and does not invent one.

## Existing passwordless sudo

Removing the old provisioning task does not revoke rules it previously installed.
If you ran the old playbook, inspect `/etc/sudoers` and `/etc/sudoers.d` with `sudo visudo`
and remove only the rule that the old setup added, after confirming normal admin
access still works. The new playbook does not rewrite unrelated sudo policy.
