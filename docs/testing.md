# Validation and VM acceptance

Run `make deps`, then `make lint test`. Python tools and Ansible collections are installed
inside ignored project directories. Tests exercise the actual dotfiles task file against
temporary Git repositories and temporary home directories with GNU Stow; no user settings,
applications or services are changed. Package tests use simulated Homebrew responses.

CI runs these checks on Linux. macOS desktop behavior still requires the following
acceptance run on a disposable Apple Silicon macOS VM, logged in as an admin account.
Do not use your working Mac for destructive fresh-install experiments.

1. Start from a clean macOS 14+ VM and install Command Line Tools. Clone the repository
   and run `make bootstrap`. Record the OS and app versions and any app-specific
   minimum OS requirements. Confirm packages, correct dotfile links, Finder/Dock settings,
   wallpaper and the manual-actions report.
2. Grant requested permissions and run `make apply` again. Expect no upgrades,
   no repeated Dock/Finder restarts, no wallpaper rewrite and no Stow changes.
3. Restart the VM. Verify AeroSpace and one SketchyBar instance start under the user account.
4. Repeat with a different username; no task edits should be necessary.
5. Snapshot the VM, introduce an unmanaged dotfile conflict and a dirty tracked dotfile,
   and apply separately. Verify actionable failure and unchanged local contents.
6. Temporarily request a nonexistent package in `local.yml`. Verify validation fails
   before package installation. Also test a disabled cask. Restore the override afterward.
7. Interrupt a package download and retry. Verify setup resumes without a reset or sudo-policy
   change. Run `make update` and confirm unrelated installed packages are not explicitly upgraded.
8. Run `make check` after provisioning. Document any check-mode limits rather than treating
   a preview as proof of successful installation.

The automation does not claim a fully reproducible GUI application version set, a
configured backup, or a restored account simply because Ansible finished successfully.
