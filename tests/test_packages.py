"""Ensure broken package declarations cannot be reported as successful."""
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

SPEC = importlib.util.spec_from_file_location(
    "validate_packages", Path(__file__).resolve().parents[1] / "scripts/validate_packages.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class PackageValidationTests(unittest.TestCase):
    def test_disabled_cask_is_an_error_and_deprecated_formula_is_a_warning(self):
        def runner(argv, **kwargs):
            if "--formula" in argv:
                data = {"formulae": [{"name": "old-cli", "deprecated": True}]}
            else:
                data = {"casks": [{"token": "blocked-app", "disabled": True}]}
            return subprocess.CompletedProcess(argv, 0, json.dumps(data), "")

        errors, warnings = validator.validate(
            {"formulae": ["old-cli"], "casks": ["blocked-app"]}, runner
        )
        self.assertIn("blocked-app", errors[0])
        self.assertIn("old-cli", warnings[0])

    def test_nonzero_exit_without_word_error_still_fails(self):
        def runner(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 1, "", "not found")

        errors, _ = validator.validate({"formulae": ["missing"], "casks": []}, runner)
        self.assertIn("not found", errors[0])

    def test_invalid_or_incomplete_metadata_fails(self):
        for response in ("not json", '{"formulae": []}'):
            with self.subTest(response=response):
                def runner(argv, **kwargs):
                    return subprocess.CompletedProcess(argv, 0, response, "")
                errors, _ = validator.validate({"formulae": ["git"], "casks": []}, runner)
                self.assertTrue(errors)

    def test_empty_inventory_does_not_call_brew(self):
        def runner(*args, **kwargs):
            self.fail("Empty lists must not invoke brew")
        self.assertEqual(([], []), validator.validate({"formulae": [], "casks": []}, runner))
