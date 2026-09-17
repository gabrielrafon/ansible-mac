"""Verify the actual config template preserves bindings and avoids double startup."""
import base64
from pathlib import Path
import tomllib
import unittest

from ansible.plugins.filter.core import FilterModule
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]


class AeroSpaceTemplateTests(unittest.TestCase):
    def test_login_startup_has_one_owner_and_bindings_survive(self):
        source = '''start-at-login = false
after-startup-command = ['exec-and-forget sketchybar']
exec-on-workspace-change = ['/bin/bash', '-c', 'sketchybar --trigger changed']
[mode.main.binding]
alt-enter = 'exec-and-forget open -n -a Kitty'
'''
        environment = Environment(
            loader=FileSystemLoader(ROOT / "templates"), undefined=StrictUndefined
        )
        environment.filters.update(FilterModule().filters())
        template = environment.get_template("aerospace.toml.j2")
        rendered = template.render(aerospace_source={
            "content": base64.b64encode(source.encode()).decode()
        })
        parsed = tomllib.loads(rendered)
        self.assertTrue(rendered.startswith("# Managed by ansible-mac"))
        self.assertTrue(parsed["start-at-login"])
        self.assertEqual([], parsed["after-startup-command"])
        self.assertEqual(
            "exec-and-forget open -n -a Kitty", parsed["mode"]["main"]["binding"]["alt-enter"]
        )
        self.assertEqual("sketchybar --trigger changed", parsed["exec-on-workspace-change"][-1])
