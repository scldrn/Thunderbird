"""Audit the actual reference STEP. Material assignment and physical mass are not implied."""
from pathlib import Path
import csv, hashlib, json, time
import numpy as np
import cadquery as cq

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
cfg=json.loads((ROOT/'configuraciones/A07_BASE.json').read_text())
source=ROOT/cfg['geometry']['5']['states']['cerrado']['path']
assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['geometry']['5']['states']['cerrado']['sha256']
metadata=json.loads((source.parent/'manifest.json').read_text())
info={p['name']:p for p in metadata['parts']}
parts=[];rows=[]
start=time.monotonic()
for s,name,loc,col in cq.Assembly.load(str(source)):
    name=name.split('/')[-1];s=s.moved(loc);bb=s.BoundingBox();v=s.Volume(tol=1e-7)
    assert s.isValid() and v>0 and name in info
    delta=abs(v-info[name]['volume_mm3'])/v
    row=dict(name=name,scope=info[name]['scope'],volume_mm3=v,volume_litre=v/1e6,
             cx_m=s.Center().x/1000,cy_m=s.Center().y/1000,cz_m=s.Center().z/1000,
             dx_mm=bb.xlen,dy_mm=bb.ylen,dz_mm=bb.zlen,manifest_volume_relative_error=delta,
             actual_mass_kg=None,actual_material=None,
             mass_status='unidentified_not_zero')
    rows.append(row);parts.append((name,s,bb))
assert len(parts)==208 and len({n for n,s,b in parts})==208
with (OUT/'BOM_GEOMETRICA_5kg.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
compound=cq.Compound.makeCompound([s for n,s,b in parts]);bb=compound.BoundingBox()
summary=dict(config_id=cfg['id'],source=str(source.relative_to(ROOT)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
             valid_part_records=len(parts),assembly_dimensions_mm=[bb.xlen,bb.ylen,bb.zlen],
             nominal_sum_part_volume_litres=sum(r['volume_litre'] for r in rows),
             manifest_volume_discrepancies=[{'name':r['name'],'relative_error':r['manifest_volume_relative_error']} for r in rows if r['manifest_volume_relative_error']>1e-5],
             mass_closed=False,scope='Geometrical volume/centroid only. No material, hardware or physical mass established.')
(OUT/'METROLOGIA_BASE.json').write_text(json.dumps(summary,indent=2))
print('METROLOGY',json.dumps(summary),flush=True)

# AABB is a rejection filter; accepted candidates get an actual BRep intersection.
candidates=[]
for i,(n,s,a) in enumerate(parts):
    for j in range(i+1,len(parts)):
        b=parts[j][2]
        if all(max(getattr(a,k+'min'),getattr(b,k+'min'))<min(getattr(a,k+'max'),getattr(b,k+'max'))-1e-6 for k in 'xyz'):
            candidates.append((i,j))
print('AABB_CANDIDATES',len(candidates),flush=True)
collisions=[];failures=[]
with (OUT/'PARES_INTERSECCION.ndjson').open('w') as journal:
    for k,(i,j) in enumerate(candidates):
        n,s,a=parts[i];nn,t,b=parts[j]
        try:
            overlap=s.intersect(t).Volume(tol=1e-7)
            record=dict(a=n,b=nn,volume_overlap_mm3=overlap)
            if overlap>1e-4:collisions.append(record)
        except Exception as e:
            record=dict(a=n,b=nn,error=str(e));failures.append(record)
        journal.write(json.dumps(record)+'\n');journal.flush()
        if k%25==0:print('PAIRS',k+1,'/',len(candidates),'overlaps',len(collisions),flush=True)
result=dict(config_id=cfg['id'],possible_pairs=len(parts)*(len(parts)-1)//2,
            bbox_candidates=len(candidates),tested=len(candidates),intersection_threshold_mm3=1e-4,
            overlaps=collisions,boolean_failures=failures,complete=True,
            elapsed_seconds=time.monotonic()-start,
            note='All nominal closed-assembly pairs with positive AABB overlap tested. Intersections require engineering classification, not automatic acceptance/rejection. Not deformation, tolerances or door sweep.')
(OUT/'AUDITORIA_INTERFERENCIAS_CERRADO.json').write_text(json.dumps(result,indent=2))
print('AUDIT_COMPLETE',len(collisions),'overlaps',len(failures),'boolean failures',flush=True)
