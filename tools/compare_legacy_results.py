#!/usr/bin/env python3
"""Compare historical numeric outputs with isolated regenerations, not validate physics."""
import csv
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
CASES = {
    'cierre_masa.py': ['candidato_dinamica_CONDICIONAL.json', 'cierre_masa_iterativo_CONDICIONAL.csv', 'verificacion_cierre_masa.json'],
    'dinamica.py': ['dinamica_6DOF_CONDICIONAL.csv', 'verificacion_dinamica.json'],
    'estructura_preliminar.py': ['estructura_preliminar_RESUMEN.json'],
}
RTOL, ATOL = 1e-9, 1e-10


def number(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float, str)):
        try:
            result = float(value)
            return result if math.isfinite(result) else None
        except ValueError:
            pass
    return None


def compare(old, new):
    result = {'numeric_compared': 0, 'numeric_outside_tolerance': 0,
              'max_absolute_difference': None, 'max_relative_difference': None,
              'added_fields': [], 'removed_fields': [], 'other_differences': []}

    def visit(a, b, path):
        if isinstance(a, dict) and isinstance(b, dict):
            result['added_fields'].extend(path + '/' + k for k in sorted(b.keys() - a.keys()))
            result['removed_fields'].extend(path + '/' + k for k in sorted(a.keys() - b.keys()))
            for key in sorted(a.keys() & b.keys()):
                visit(a[key], b[key], path + '/' + key)
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                result['other_differences'].append({'path': path, 'old_length': len(a), 'new_length': len(b)})
            for index, (left, right) in enumerate(zip(a, b)):
                visit(left, right, path + '/' + str(index))
        else:
            left, right = number(a), number(b)
            if left is not None and right is not None:
                result['numeric_compared'] += 1
                absolute = abs(left - right)
                relative = absolute / max(abs(left), abs(right), 1e-12)
                for key, delta in [('max_absolute_difference', absolute), ('max_relative_difference', relative)]:
                    if result[key] is None or delta > result[key]['difference']:
                        result[key] = {'path': path, 'old': left, 'new': right, 'difference': delta}
                if not math.isclose(left, right, rel_tol=RTOL, abs_tol=ATOL):
                    result['numeric_outside_tolerance'] += 1
            elif a != b or type(a) is not type(b):
                result['other_differences'].append({'path': path, 'old': a, 'new': b})
    visit(old, new, '')
    return result


def read(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream)) if path.suffix == '.csv' else json.load(stream)


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix='thunderbird-numeric-') as temp:
        work = Path(temp)
        (work / 'legacy').mkdir()
        shutil.copytree(ROOT / 'legacy/scripts', work / 'legacy/scripts')
        shutil.copytree(ROOT / 'resultados', work / 'resultados')
        (work / 'fuentes').mkdir()
        shutil.copytree(ROOT / 'fuentes/uiuc', work / 'fuentes/uiuc')
        env = os.environ.copy()
        env.update({'PYTHONDONTWRITEBYTECODE': '1', 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MPLBACKEND': 'Agg'})
        for script, files in CASES.items():
            subprocess.run([sys.executable, str(work / 'legacy/scripts' / script)], cwd=work, env=env,
                           capture_output=True, text=True, timeout=45, check=True)
            for name in files:
                results[name] = compare(read(ROOT / 'resultados' / name), read(work / 'resultados' / name))
    print(json.dumps({'scope': 'isolated historical output comparison; not physical validation',
                      'relative_tolerance': RTOL, 'absolute_tolerance': ATOL, 'files': results}, indent=2))


if __name__ == '__main__':
    main()
