"""Index project documentation without inferring scientific validity from filenames."""
from pathlib import Path
import csv, hashlib, json, re
from collections import Counter

PLAN = Path(__file__).resolve().parent
ROOT = PLAN.parent
EXCLUDED = {'__pycache__', 'frames', 'render_meshes', '.git'}
REVIEWED = {
    'ESTADO-VERIFICACION-GLOBAL.md', 'DATOS-PARA-CERRAR-VALIDACION.md',
    'modelos_integrados/DECISION-ARQUITECTURA.md',
    'modelos_integrados/producto_A07/LEEME.md',
    'modelos_integrados/producto_A06/5kg/manifest.json',
    'CFD/INFORME-CONVERGENCIA-AVANCE-A.md',
    'CFD/ESTADO-COMPARACION-PAREADA.md',
    'CFD/PAUSA_SOLICITADA_USUARIO.json',
    'simulacion_vuelo_A/VERIFICACION.json',
    'simulacion_vuelo_A/5kg_nominal.json',
    'simulacion_vuelo_A/INFORME.md', 'vuelo_rapido_visual/INFORME.md',
    'ESTRUCTURA-PRELIMINAR.md', 'REVISION-POTENCIA-Y-ESPACIO.md',
    'integracion_apps/LEEME.md', 'LEEME.md',
}

rows = []
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or PLAN in path.parents:
        continue
    rel = path.relative_to(ROOT)
    if set(rel.parts) & EXCLUDED or path.suffix not in {'.md', '.json', '.py'}:
        continue
    raw = path.read_bytes()
    text = raw.decode('utf-8', errors='replace')
    headings = [line.lstrip('# ').strip() for line in text.splitlines() if line.startswith('#')][:8]
    json_state = ''
    if path.suffix == '.json':
        try:
            json.loads(text)
            json_state = 'parseable'
        except (ValueError, TypeError):
            json_state = 'parse_error_review'
    group = rel.parts[0] if len(rel.parts) > 1 else 'informes_y_scripts_raiz'
    warnings = []
    for pattern, name in ((r'no se ha demostrado|sin validar|no validado|not validated|physical_performance_validated.*false', 'limite_de_validacion'),
                          (r'hipot[eé]tic|supuest|assumed', 'supuestos'),
                          (r'pausad|paused', 'mencion_pausa'),
                          (r'rechazad|rejected|failed', 'mencion_fallo')):
        if re.search(pattern, text, re.I):
            warnings.append(name)
    rows.append(dict(path=str(rel),type=path.suffix,group=group,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                     headings=' | '.join(headings),json_syntax=json_state,
                     targeted_review='yes' if str(rel) in REVIEWED else 'catalogued_not_individually_validated',
                     lexical_flags=' | '.join(warnings)))

with (PLAN/'INVENTARIO-DOCUMENTAL.csv').open('w',newline='') as out:
    writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
summary=dict(date='2026-11-02',timezone='America/Bogota',total=len(rows),by_type=dict(Counter(r['type'] for r in rows)),
             by_group=dict(Counter(r['group'] for r in rows)),targeted_review_count=sum(r['targeted_review']=='yes' for r in rows),
             json_parse_errors=[r['path'] for r in rows if r['json_syntax']=='parse_error_review'],
             note='Exhaustive index of selected text types outside excluded caches/plan. Lexical flags are not evidence grades. Targeted sections reviewed; not every source scientifically revalidated.')
(PLAN/'INVENTARIO-RESUMEN.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))
