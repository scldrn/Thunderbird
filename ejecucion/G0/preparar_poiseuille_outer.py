from pathlib import Path
import shutil,json,re
P=Path(__file__).resolve().parent;source=P/'poiseuille_newtonian_40'
for ny in (20,40,80):
 case=P/f'poiseuille_{ny}_outer15';case.mkdir(exist_ok=True)
 for folder in ('0','constant','system'):
  shutil.copytree(source/folder,case/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('polyMesh'))
 b=(case/'system/blockMeshDict').read_text().replace('(1 40 1)',f'(1 {ny} 1)');(case/'system/blockMeshDict').write_text(b)
 f=case/'system/fvSolution';s=f.read_text().replace('nOuterCorrectors    2;','nOuterCorrectors    15;');f.write_text(s)
 meta=json.loads((source/'benchmark_inputs.json').read_text());meta.update(Ny=ny,nOuterCorrectors=15,parent_case='poiseuille_newtonian_40',input_sha256={})
 (case/'benchmark_inputs.json').write_text(json.dumps(meta,indent=2))
print('Prepared three grids, changing only outer correctors from the first family')
