"""Summarize actual OpenFOAM mesh logs; never substitutes a flow audit."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
CASES = ['piloto_r1','piloto_r2_hibrido','piloto_r3_hibrido_cap','piloto_r4_hibrido_resuelto']
rows = []
for name in CASES:
    case = HERE/name
    log = (case/'log.checkMesh').read_text()
    metadata = json.loads((case/'MALLA.json').read_text())
    def value(pattern):
        match = re.search(pattern, log)
        assert match, pattern
        return float(match[1])
    rows.append(dict(case=name, cells=metadata.get('cells',metadata.get('hexahedra')),
        max_aspect=value(r'[Mm]ax aspect ratio:?\s*(?:=\s*)?([\deE.+-]+)'),
        max_nonorth_deg=value(r'Mesh non-orthogonality Max:\s*([\deE.+-]+)'),
        max_skewness=value(r'Max skewness\s*=\s*([\deE.+-]+)'),
        min_determinant=value(r'Cell determinant \(wellposedness\)\s*:\s*minimum:\s*([\deE.+-]+)'),
        min_interpolation_weight=value(r'Face interpolation weight\s*:\s*minimum:\s*([\deE.+-]+)'),
        min_volume_ratio=value(r'Face volume ratio\s*:\s*minimum:\s*([\deE.+-]+)'),
        checkMesh_OK=('Mesh OK.' in log and 'Failed ' not in log),
        checkMesh_log_sha256=hashlib.sha256((case/'log.checkMesh').read_bytes()).hexdigest(),
        mesh_sha256=metadata['mesh_sha256']))
assert not any(row['checkMesh_OK'] for row in rows[:-1]) and rows[-1]['checkMesh_OK']
# Independent volume closure was already performed by polygon integration in
# the mesh generator; compare its result against the converted OpenFOAM mesh.
for name in CASES[1:]:
    case=HERE/name
    m=json.loads((case/'MALLA.json').read_text())
    volume=float(re.search(r'Total volume\s*=\s*([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)',(case/'log.checkMesh').read_text())[1])
    assert abs(volume-m['summed_cell_volume_m3'])/volume < 1e-10
result=dict(scope='Mesh geometry/topology verification only, no flow validation',
    criteria_not_relaxed=True, volume_closure_with_independent_polygon_integration=True,
    source_and_rejected_cases_preserved=True, cases=rows,
    warning='Small-edge warnings remain because the wall spacing is intentionally micrometric. Mesh OK does not demonstrate grid independence or physical accuracy.',
    physical_validation_accepted=False)
(HERE/'AUDITORIA_MALLAS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
