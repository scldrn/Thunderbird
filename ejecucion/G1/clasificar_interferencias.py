"""Classify nominal overlaps for engineering disposition; no automatic joint approval."""
from pathlib import Path
import json,csv,collections
P=Path(__file__).resolve().parent
source=json.loads((P/'AUDITORIA_INTERFERENCIAS_CERRADO.json').read_text())
assert source['complete'] and not source['boolean_failures']
rows=[]
for r in source['overlaps']:
 a,b=r['a'],r['b']
 if b==a.replace('_alabe_','_eje_') and '_alabe_' in a:
  kind='shaft_vane_material_overlap';action='Choose fused manufacture or bore/retention interface; remove double material accounting';approval='joint_design_pending'
 elif a.startswith('eje_control_') and b.startswith('actuador_reserva_'):
  kind='shaft_enters_actuator_packaging';action='Reserve is not actual hardware; select motor/output coupling before collision acceptance';approval='packaging_not_physical_part'
 elif a.startswith(('cuaderna_','abrazadera_')) and b.startswith('soporte_canal_axial_'):
  kind='support_attachment_overlap';action='Define fused joint or hole/fastener/insert with loads and manufacturing method';approval='joint_design_pending'
 elif a.startswith(('panel_sensor_','cubierta_lateral_')) and b.startswith(('sculpture_','epaule_')):
  kind='unintended_styling_duplicate';action='Subtract styling insert volume from underlying cover, preserve external envelope';approval='correction_required'
 elif a.startswith('vis_') or b.startswith('vis_'):
  kind='fastener_seat_interference';action='Add proper seat/counterbore without duplicating head material; tolerance still pending';approval='correction_required'
 elif a=='carroceria_superior' and b.startswith('carenado_raiz_'):
  kind='root_contact_small_overlap';action='Recompute exact nominal subtraction and inspect tolerance/contact; no load acceptance inferred';approval='contact_precision_review'
 else:
  kind='unclassified';action='Engineering investigation required';approval='unresolved'
 rows.append({**r,'classification':kind,'disposition':action,'approval':approval})
assert not any(r['classification']=='unclassified' for r in rows)
with (P/'CLASIFICACION_INTERFERENCIAS.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=dict(pairs_tested=source['tested'],possible_pairs=source['possible_pairs'],nominal_overlaps=len(rows),
             by_classification=dict(collections.Counter(r['classification'] for r in rows)),
             closed_assembly_collision_free=False,
             scope='Nominal intersections classified, not joint/structure/tolerance approval. No assertion that all 73 are design defects.')
(P/'CLASIFICACION_RESUMEN.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
