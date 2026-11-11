#!/usr/bin/env python3
"""Run moved historical scripts in separate temporary copies of their inputs.

This verifies execution only. Changed output hashes are reported, not accepted
as updated research evidence. The checkout and paused CFD cases are not edited.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent.parent
TIMEOUT_SECONDS = 45


def hashes(directory):
    values = {}
    for path in directory.rglob("*"):
        if not path.is_file() or path.is_symlink() or "mpl-cache" in path.parts:
            continue
        values[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return values


def check(script):
    with tempfile.TemporaryDirectory(prefix="thunderbird-legacy-check-") as temporary:
        work = Path(temporary)
        (work / "legacy").mkdir()
        shutil.copytree(ROOT / "legacy/scripts", work / "legacy/scripts")
        shutil.copytree(ROOT / "resultados", work / "resultados")
        (work / "fuentes").mkdir()
        shutil.copytree(ROOT / "fuentes/uiuc", work / "fuentes/uiuc")
        before = hashes(work / "resultados")
        env = os.environ.copy()
        env.update({"PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MPLBACKEND": "Agg"})
        try:
            result = subprocess.run(
                [sys.executable, str(work / "legacy/scripts" / script.name)], cwd=work,
                env=env, capture_output=True, text=True, timeout=TIMEOUT_SECONDS, check=False,
            )
            status = "passed" if result.returncode == 0 else "failed"
            error = (result.stdout + "\n" + result.stderr)[-4000:] if result.returncode else None
        except subprocess.TimeoutExpired:
            status, error = "timeout", f"Exceeded {TIMEOUT_SECONDS} seconds"
        after = hashes(work / "resultados")
        return {
            "script": script.name, "status": status,
            "changed_existing": sorted(n for n in after if n in before and after[n] != before[n]),
            "new_outputs": sorted(n for n in after if n not in before), "error": error,
        }


def main():
    scripts = sorted((ROOT / "legacy/scripts").glob("*.py"))
    if not scripts:
        raise RuntimeError("No historical scripts found")
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = [future.result() for future in as_completed(pool.submit(check, path) for path in scripts)]
    results.sort(key=lambda item: item["script"])
    print(json.dumps({"scope": "isolated execution, not physical validation", "results": results}, indent=2))
    return int(any(item["status"] != "passed" for item in results))


if __name__ == "__main__":
    raise SystemExit(main())
