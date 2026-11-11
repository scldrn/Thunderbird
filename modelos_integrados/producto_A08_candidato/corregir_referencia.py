"""Subtractive local corrections only; preserves A07 and does not approve its joints."""
from pathlib import Path
import cadquery as cq,json,hashlib
P=Path(__file__).resolve().parent;source=P.parent/'producto_A07/5kg/A07_cerrado.step'
records=[(n.split('/')[-1],s.moved(l),c) for s,n,l,c in cq.Assembly.load(str(source))]
original={n:s for n,s,c in records};parts=original.copy();changes=[]
for cover,styling in [('panel_sensor_nariz','sculpture_capot_-1'),('panel_sensor_nariz','sculpture_capot_1'),('cubierta_lateral_-1','epaule_arriere_-1'),('cubierta_lateral_1','epaule_arriere_1')]:
 parts[cover]=parts[cover].cut(parts[styling]);changes.append(dict(part=cover,method='subtract duplicate styling insert',other=styling))
for part,fastener in [('sculpture_capot_-1','vis_encastree_0'),('sculpture_capot_1','vis_encastree_1'),('cuaderna_0','vis_encastree_2'),('cuaderna_0','vis_encastree_3')]:
 s=parts[fastener];bb=s.BoundingBox();c=s.Center();cut=cq.Solid.makeCylinder(2.3,bb.zlen+2,cq.Vector(c.x,c.y,bb.zmin-1.5),cq.Vector(0,0,1));parts[part]=parts[part].cut(cut)
 changes.append(dict(part=part,method='nominal counterbore envelope',other=fastener,diameter_mm_ASSUMED=4.6))
parts['carenado_raiz_0']=parts['carenado_raiz_0'].cut(parts['carroceria_superior']);changes.append(dict(part='carenado_raiz_0',method='recompute nominal root contact subtraction',other='carroceria_superior'))
assert all(s.isValid() and s.Volume()>0 for s in parts.values())
changed=sorted({c['part'] for c in changes});checks=[]
for name in changed:
 s=parts[name];checks.append(dict(name=name,removed_nominal_volume_mm3=original[name].Volume()-s.Volume(),outside_original_mm3=s.cut(original[name]).Volume()))
assembly=cq.Assembly(name='A08_local_corrections_candidate_5kg_TARGET')
for name,s,col in records:assembly.add(parts[name],name=name,color=col)
file=P/'A08_cerrado_5kg_candidato.step';assembly.save(str(file))
reimport={n.split('/')[-1]:s.moved(l) for s,n,l,c in cq.Assembly.load(str(file))}
assert len(reimport)==208 and all(s.isValid() for s in reimport.values())
post=[]
for change in changes:
 a,b=change['part'],change['other'];post.append(dict(a=a,b=b,overlap_mm3=reimport[a].intersect(reimport[b]).Volume()))
result=dict(source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
            changes=changes,subset_checks=checks,corrected_pair_checks_after_STEP_reimport=post,
            parts=208,geometric_candidate_only=True,manufacturing_clearances_approved=False,
            unaddressed='48 shaft/vane, 12 support attachment and 4 shaft/actuator-reserve overlaps remain engineering interface decisions, not automatically approved.',
            canonical_configuration_changed=False)
(P/'CORRECCIONES.json').write_text(json.dumps(result,indent=2))
print('CANDIDATE_EXPORTED',len(changed),'changed parts; max corrected-pair overlap',max(r['overlap_mm3'] for r in post),flush=True)
