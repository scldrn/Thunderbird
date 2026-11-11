"""Same-mesh pointwise changes; no physical-time interpretation for LTS."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from foam_fields import read_internal
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path);p.add_argument('--case',default='avance_A_compresible_600kmh_LTS_diag');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
case=ROOT/a.case;m=json.loads((case/'compressible_assumptions.json').read_text());mesh=json.loads((Path(m['source_mesh_case'])/'mesh_metadata.json').read_text());N=mesh['cells']
assert m['counter_kind']=='local_pseudo_iterations'
results={};hashes={}
scales={'U':m['velocity_m_s'],'p':.5*m['rho_kg_m3']*m['velocity_m_s']**2,'T':m['velocity_m_s']**2/(2*m['Cp_J_kgK'])}
for field in ('U','p','T'):
 x=read_internal(a.first/field,N,3 if field=='U' else 1);y=read_internal(a.second/field,N,3 if field=='U' else 1)
 delta=np.linalg.norm(y-x,axis=1) if field=='U' else abs(y-x)
 if field!='U':assert x.min()>0 and y.min()>0
 results[field]=dict(maximum_absolute_change=float(delta.max()),cell_arithmetic_rms_change=float(np.sqrt(np.mean(delta**2))),normalizing_scale=scales[field],max_normalized_change=float(delta.max()/scales[field]))
 hashes[field]=[hashlib.sha256((folder/field).read_bytes()).hexdigest() for folder in (a.first,a.second)]
out=dict(case=case.name,counter_kind='local_pseudo_iterations',first_field=str(a.first.resolve()),second_field=str(a.second.resolve()),cells=N,changes=results,field_sha256=hashes,
 physical_drag_accepted=False,field_change_convergence_proven=False,note='Pointwise same-mesh changes. RMS is cell-arithmetic, not volume-weighted. Needs repeated intervals and mesh/domain/scheme sensitivity.')
a.output.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
