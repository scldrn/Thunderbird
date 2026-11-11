"""Check moved historical modules without running their generators."""

import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "legacy" / "scripts"


class LegacyReconnectionTests(unittest.TestCase):
    def test_core_imports_use_repository_root(self):
        code = (
            "from pathlib import Path; import calcular, control, trimado_superficies; "
            "root=Path.cwd(); "
            "assert calcular.ROOT == root and control.ROOT == root "
            "and trimado_superficies.ROOT == root; "
            "assert calcular.geometry(0.025, 6, 'esferoide')['L_m'] > 0"
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SCRIPTS)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [sys.executable, "-c", code], cwd=ROOT, env=env,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

if __name__ == "__main__":
    unittest.main()
