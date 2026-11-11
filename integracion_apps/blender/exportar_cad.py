from pathlib import Path
import cadquery as cq,json,gzip,hashlib
P=Path(__file__).resolve().parent;root=P.parents[1];source=root/'modelos_integrados/producto_A07/5kg/A07_cerrado.step'
meta=json.loads((source.parent/'manifest.json').read_text());lookup={r['name']:r for r in meta['parts']};parts=[]
for s,n,l,c in cq.Assembly.load(str(source)):
 name=n.split('/')[-1];s=s.moved(l);v,f=s.tessellate(.35,angularTolerance=.15)
 parts.append(dict(name=name,vertices_m=[[a/1000 for a in p.toTuple()] for p in v],triangles=f,color=lookup[name]['color'],exterior=lookup[name]['exterior'],scope=lookup[name]['scope']))
rules=json.loads((source.parents[1]/'propuesta_elevacion.json').read_text())
data=dict(source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),parts=parts,rules=rules,units='m',physical_performance_validated=False)
with gzip.open(P/'cad_A07.json.gz','wt') as out:json.dump(data,out)
print('EXPORTED',len(parts),'parts',flush=True)
