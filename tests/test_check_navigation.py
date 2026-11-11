"""Regression checks for the repository navigation validator."""

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("check_navigation", ROOT / "tools/check_navigation.py")
navigation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(navigation)


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="thunderbird-navigation-")
        self.root = Path(self.directory.name)
        (self.root / "tools").mkdir()
        shutil.copy(ROOT / "tools/check_navigation.py", self.root / "tools/check_navigation.py")
        names = list(navigation.DOCUMENTS) + [f"{area}/README.md" for area in navigation.AREAS]
        for name in names + list(navigation.CORE_EVIDENCE):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Example\n", encoding="utf-8")

    def tearDown(self):
        self.directory.cleanup()

    def run_check(self):
        return subprocess.run(
            [sys.executable, str(self.root / "tools/check_navigation.py")],
            capture_output=True, text=True, check=False,
        )

    def test_valid_navigation(self):
        (self.root / "README.md").write_text(
            "[local](docs/research_context.md) [external](https://example.com)\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_check().returncode, 0)

    def test_broken_local_link_is_rejected(self):
        (self.root / "README.md").write_text("[broken](missing.md)\n", encoding="utf-8")
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Broken link", result.stderr)

    def test_missing_core_evidence_is_rejected(self):
        (self.root / navigation.CORE_EVIDENCE[0]).unlink()
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing required file", result.stderr)


if __name__ == "__main__":
    unittest.main()
