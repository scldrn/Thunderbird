from pathlib import Path
import shutil,json,re
P=Path(__file__).resolve().parent;source=P/'poiseuille_newtonian_40'
for name,ny,dt in [('poiseuille_newtonian_20',20,.005),('poiseuille_newtonian_80',80,.005),('poiseuille_newtonian_40_dt_half',40,.0025)]:
 case=P/name;case.mkdir(exist_ok=True)
 for folder in ('0','constant','system'):
  shutil.copytree(source/folder,case/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('polyMesh'))
 b=(case/'system/blockMeshDict').read_text().replace('(1 40 1)',f'(1 {ny} 1)');(case/'system/blockMeshDict').write_text(b)
 c=(case/'system/controlDict').read_text();c=re.sub(r'deltaT\s+[^;]+;',f'deltaT {dt};',c);(case/'system/controlDict').write_text(c)
 meta=json.loads((source/'benchmark_inputs.json').read_text());meta.update(Ny=ny,dt_s=dt,parent_case='poiseuille_newtonian_40',input_sha256={})
 (case/'benchmark_inputs.json').write_text(json.dumps(meta,indent=2))
print('Prepared 20/80-cell spatial and 40-cell half-dt cases')
