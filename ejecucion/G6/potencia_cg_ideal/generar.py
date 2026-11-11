"""Generate a reproducible conditional sensitivity matrix; no real fan map."""
import hashlib
import itertools
import json
from pathlib import Path
from modelo import scenario

HERE = Path(__file__).resolve().parent

def main():
    rows = []
    for mass, cx, cy, ax, az, cone in itertools.product(
        (2, 5, 10), (0, .25, .5, .6, .75), (0, .4),
        (0, .25, .5, 1, 2), (0, .5), (35, 45)
    ):
        for cap in (None, 20.58) if mass == 5 else (None,):
            rows.append(scenario(mass, cx, cy, ax, az, cone, cap))
    files = ('modelo.py', 'generar.py', 'verificar.py')
    result = {
        'descripcion': 'Referencia ideal de discos libres y reparto de empuje paralelo; no prestaciones instaladas',
        'numero_escenarios': len(rows),
        'sha256_codigo': {p: hashlib.sha256((HERE / p).read_bytes()).hexdigest() for p in files},
        'escenarios': rows,
    }
    (HERE / 'RESULTADOS.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(f'{len(rows)} escenarios escritos')

if __name__ == '__main__':
    main()
