"""CAD dimensions and ideal-disk lower-bound sensitivity, not installed power."""
from pathlib import Path
import json,math
import numpy as np
import cadquery as cq
ROOT=Path(__file__).resolve().parent
rows=[]
configs=[('A','A_integracion_interna/diseno_industrial_v2.step',40,65,58),('B_guardado','B_retractil_guardado/B_retractil_guardado.step',52,70,-4),('B_desplegado','B_retractil_desplegado/B_retractil_desplegado.step',52,235,-4),('C','C_conductos_integrados/C_conductos_integrados.step',57,155,10)]
for name,file,r,y,z in configs:
 a=cq.Assembly.load(str(ROOT/file));ss=[s.moved(loc) for s,label,loc,col in a];bb=cq.Compound.makeCompound(ss).BoundingBox()
 radii=[]
 for shape,label,loc,col in a:
  if 'rotor_representativo_' in label or 'palas_representativas_' in label:
   shape=shape.moved(loc);cc=shape.Center();radii.append(max(math.hypot(v.Center().x-cc.x,v.Center().y-cc.y) for v in shape.Vertices()))
 assert len(radii)==4
 nominal=r;r=sum(radii)/len(radii);area=sum(math.pi*(rr/1000)**2 for rr in radii)
 p=np.array([[x,sy*y/1000,z/1000] for x in [-.280,.285] for sy in [-1,1]]);n=np.tile([0.,0.,1.],(4,1));B=np.vstack([n.T,np.cross(p,n).T]);Bp=B.copy();Bp[5]+=.02*np.array([1,-1,-1,1])
 rows.append(dict(variant=name,step=file,bounds_mm=[bb.xlen,bb.ylen,bb.zlen],reference_duct_or_rotor_radius_mm=nominal,rotor_radius_mm=r,total_disk_area_m2=area,force_rank=int(np.linalg.matrix_rank(n.T)),wrench_rank_no_reaction=int(np.linalg.matrix_rank(B)),illustrative_rank_with_alternating_reaction=int(np.linalg.matrix_rank(Bp)),ideal_static_hover_power_W=[dict(mass_kg=m,power_W=(m*9.80665)**1.5/math.sqrt(2*1.225*area)) for m in [2,5,10]]))
out=dict(rows=rows,load_examples=[dict(speed_kmh=v,q_Pa=.5*1.225*(v/3.6)**2,force_N_on_0_01m2_at_delta_Cp_1=.5*1.225*(v/3.6)**2*.01,turn_radius_m_at_10g_lateral=(v/3.6)**2/(10*9.80665)) for v in [600,1000]],assumptions=['4 identical vertical fixed-axis rotors as illustrated; no hidden vectoring','Ideal disk theory: isolated non-overlapping free-air disks; no duct augmentation, blockage, profile losses, electric losses or ground effect','Not an installed lower bound if a duct changes effective streamtube: only a common bare-disk comparator','CAD bounding box is not frontal area or drag coefficient','Reaction coefficient0.02m is illustrative for rank, not a measured rotor map'])
(ROOT/'comparacion_cuantitativa.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
