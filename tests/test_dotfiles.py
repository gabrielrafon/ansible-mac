"""Exercise the real Ansible/Stow tasks in disposable directories, never $HOME."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
ANSIBLE = ROOT / ".venv/bin/ansible-playbook"
STOW = shutil.which("stow")


@unittest.skipUnless(STOW and ANSIBLE.exists(), "Requires make deps and GNU Stow")
class DotfileDeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ansible-mac-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.target = self.base / "another account"
        self.checkout = self.base / "checkout"
        self.source.mkdir()
        self.target.mkdir()
        for name, filename in (("zsh", ".zshrc"), ("tmux", ".tmux.conf")):
            (self.source / name).mkdir()
            (self.source / name / filename).write_text(f"# {name} configuration\n")
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
        revision = self.git("rev-parse", "HEAD").stdout.strip()
        play = [{
            "name": "Test isolated dotfile deployment",
            "hosts": "localhost", "gather_facts": False, "connection": "local",
            "vars": {
                "ansible_python_interpreter": sys.executable,
                "ansible_remote_tmp": str(self.base / "remote-tmp"),
                "dotfiles_dir": str(self.checkout), "dotfiles_repo": str(self.source),
                "dotfiles_revision": revision, "stow_executable": STOW,
                "dotfiles_packages": [
                    {"name": name, "target": str(self.target)} for name in ("zsh", "tmux")
                ],
            },
            "pre_tasks": yaml.safe_load((ROOT / "main.yml").read_text())[0]["pre_tasks"][:1],
            "tasks": [{"name": "Deploy dotfiles", "ansible.builtin.import_tasks": str(ROOT / "tasks/dotfiles.yml")}],
        }]
        self.playbook = self.base / "fixture.yml"
        self.playbook.write_text(yaml.safe_dump(play))

    def git(self, *args, directory=None):
        return subprocess.run(
            ["git", "-C", str(directory or self.source), *args],
            text=True, capture_output=True, check=True,
        )

    def run_play(self, *args, success=True):
        result = subprocess.run(
            [str(ANSIBLE), "-i", "localhost,", str(self.playbook), *args],
            cwd=ROOT, text=True, capture_output=True,
            env={**os.environ, "ANSIBLE_NOCOLOR": "1"}, check=False,
        )
        output = result.stdout + result.stderr
        if success:
            self.assertEqual(0, result.returncode, output)
        else:
            self.assertNotEqual(0, result.returncode, output)
        return output

    def test_fresh_install_then_no_changes_on_second_run(self):
        self.run_play()
        self.assertTrue((self.target / ".zshrc").is_symlink())
        self.assertTrue((self.target / ".tmux.conf").is_symlink())
        output = self.run_play()
        self.assertRegex(output, r"changed=0\s")

    def test_conflict_prevents_all_links_and_preserves_existing_file(self):
        conflict = self.target / ".tmux.conf"
        conflict.write_text("local configuration\n")
        output = self.run_play(success=False)
        self.assertIn("conflict", output.lower())
        self.assertTrue(self.checkout.exists())
        self.assertFalse((self.target / ".zshrc").exists())
        self.assertEqual("local configuration\n", conflict.read_text())
        self.assertFalse(conflict.is_symlink())

    def test_dirty_checkout_fails_without_discarding_edits(self):
        self.run_play()
        changed = self.checkout / "zsh/.zshrc"
        changed.write_text("local edits\n")
        output = self.run_play(success=False)
        self.assertIn("contains local changes", output)
        self.assertEqual("local edits\n", changed.read_text())

    def test_check_mode_does_not_clone_or_link(self):
        self.run_play("--check")
        self.assertFalse(self.checkout.exists())
        self.assertFalse((self.target / ".zshrc").exists())

    def test_local_overrides_replace_default_mapping(self):
        (self.base / "local.yml").write_text("---\ndotfiles_packages: []\n")
        self.run_play()
        self.assertTrue(self.checkout.exists())
        self.assertFalse((self.target / ".zshrc").exists())
