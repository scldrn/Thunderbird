"""Apply the broader acceleration objectives to the relocated packaging cases."""
from pathlib import Path
import json
import numpy as np
import reversibilidad_6dof_A as control
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'empaquetado_axial_A';control.OUT=OUT/'control'
source=json.loads((OUT/'RESUMEN.json').read_text());rows=[]
signs=np.array([1.,-1.,-1.,1.]);zx=np.where(signs>0,-.039,.037);zy=np.where(signs>0,-.021,.019)
for selected in source['selected_finite_search_candidates']:
    for mode,acc,centered in [('cualquier_actitud_0p5g',.5,False),('horizontal_5g',5,True)]:
        name=f"b{int(selected['half_pitch_mm'])}_{mode}"
        case=control.certificate(name,positions_m=selected['positions_m'],z=.007,lever_z_fx=zx,lever_z_fy=zy,additional_acceleration_g=acc,center_at_hover=centered,resolution=2)
        data=np.load(control.OUT/(name+'.npz'));f=data['force_vectors_N'];p=data['positions_m'];target=data['targets_N_Nm']
        moment=np.column_stack([(p[:,1]*f[:,:,2]-zy*f[:,:,1]).sum(1),(zx*f[:,:,0]-p[:,0]*f[:,:,2]).sum(1),(p[:,0]*f[:,:,1]-p[:,1]*f[:,:,0]).sum(1)])
        error=float(np.max(abs(np.c_[f.sum(1),moment]-target)));assert error<2e-7
        assert np.max(np.linalg.norm(f,axis=2)-case['positive_force_capacity_sufficient_N'])<2e-7
        assert np.min(signs*f[:,:,2])>=1-2e-7
        assert np.max(np.linalg.norm(f[:,:,:2],axis=2)-signs*f[:,:,2])<2e-7
        rows.append(dict(half_pitch_mm=selected['half_pitch_mm'],mode=mode,capacity_sufficient_in_each_direction_N=case['positive_force_capacity_sufficient_N'],independent_wrench_error_N_or_Nm=error,vertices_checked=len(target),case=name))
(OUT/'CONTROL_REVERSIBLE.json').write_text(json.dumps(dict(cases=rows,installed_performance_validated=False,scope='Same ideal effective cones, per-sign CAD row-center lever assumptions and 5 kg/CG=0 assumptions. Required capacities are sufficient conservative bounds; they do not demonstrate these accelerations.'),indent=2))
path=OUT/'INFORME.md';text=path.read_text().split('\n## Extensión reversible de las estaciones')[0]
text+='\n## Extensión reversible de las estaciones\n\nSe conserva el objetivo de máxima agilidad: además del dominio horizontal inicial se evaluó la capacidad adicional de cualquier actitud con 0,5 g y una esfera de aceleraciones de 5 g con cuerpo horizontal. Se usan signos diagonales fijos, fuerza útil simétrica, bancos de salida de cada sentido y las mismas reservas de ±0,5 N·m. Estas son exigencias del modelo, no prestaciones del rotor de dibujo.\n\n| Reserva axial exterior | Cualquier actitud, 0,5 g | Cuerpo horizontal, 5 g |\n|---:|---:|---:|\n'
for selected in source['selected_finite_search_candidates']:
    r=[a for a in rows if a['half_pitch_mm']==selected['half_pitch_mm']]
    text+=f"| {selected['axial_diameter_with_2mm_radial_margin_mm']:.0f} mm | ±{r[0]['capacity_sufficient_in_each_direction_N']:.2f} N/fan | ±{r[1]['capacity_sufficient_in_each_direction_N']:.2f} N/fan |\n"
text+='\nCada condición añade 1536 solicitudes de comprobación y una cobertura continua suficiente por convexidad. La caracterización real de fuerza/momento, potencia, inversión y dinámica sigue pendiente. No se reinterpreta el paso geométrico reservado como motor capaz de proporcionar estas fuerzas. Código: `control_reversible_estaciones_A.py`.\n'
path.write_text(text);print(json.dumps(dict(cases=len(rows),vertices=sum(r['vertices_checked'] for r in rows))))
