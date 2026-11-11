"""Hover-area screening of A, explicitly NOT a ducted-fan or motor prediction."""
from pathlib import Path
import math,json,hashlib

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'vectorizacion_A'/'area_y_escala';OUT.mkdir(exist_ok=True)
rho=1.225;g=9.80665;n=4
ref=json.loads((ROOT/'diseno_industrial_v2/verificacion.json').read_text())
# Farthest blade vertex in the styling script is 41*radial + 1*tangential mm.
diameter_mm=2*math.hypot(41,1)
def benchmark(m,d):
    area=n*math.pi*(d/2000)**2;t=m*g
    v=math.sqrt(t/(2*rho*area));p=t*v
    return dict(mass_assumed_kg=m,rotor_diameter_mm=d,total_geometric_disk_area_m2=area,weight_N=t,disk_loading_Pa=t/area,isolated_free_rotor_ideal_induced_velocity_ms=v,isolated_free_rotor_ideal_induced_power_W=p,reference_energy_Wh={str(s):p*s/3600 for s in [30,120,300]})

scales=[]
for mass in [2,5,10]:
    scale=(mass/5)**(1/3)
    scales.append(dict(scale=scale,envelope_mm=[v*scale for v in ref['bounds_mm']],**benchmark(mass,diameter_mm*scale)))
sweep=[benchmark(5,d) for d in [diameter_mm,100,120,160,200]]
for a in sweep:
    # Pair pitch from the four parallel fan centers. This is only a necessary
    # disk-interference check; not sufficient installed or hull clearance.
    a['disk_only_gap_at_unchanged_130mm_pair_pitch_mm']=130-a['rotor_diameter_mm']
    a['disk_pair_overlap_at_original_centers']=a['rotor_diameter_mm']>130
source=ROOT/'diseno_industrial_v2.py'
result=dict(method='Equal-loading isolated ideal free-rotor momentum theory reference: P=(mg)^(3/2)/sqrt(2*rho*sum(A)). Not installed fan power or a universal lower bound for a shrouded system.',rho_kgm3=rho,g_ms2=g,n_rotors=n,reference_mass_assumed_kg=5,reference_rotor_diameter_mm=diameter_mm,source_script_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),scale_basis='Algebraic similar-geometry envelopes at fixed mean density, not newly validated CAD or closed mass budgets.',scales=scales,diameter_sweep_5kg=sweep,geometric_warning='The illustrative original sleeve bore radius is 41 mm; the farthest blade vertex is at sqrt(41^2+1) mm. No running/tolerance clearance was designed in that styling model. The preliminary integration retained those sleeves; CAD_integracion_coherente replaces them with consolidated 42 mm bores, without validating operating clearance.',limitations=['No duct thrust augmentation, installed capture area or fan characteristic is supplied.','No inlet, vane, grille, shaft, swirl, profile, motor, ESC or battery losses are included.','An assumed efficiency multiplier cannot close missing fan data.','Hover zero-moment equal-loading benchmark does not include actual CG, torque control or lateral acceleration.','Positive-power reserve, response time, thermal limits and flight endurance remain unknown.'],sources=['https://ntrs.nasa.gov/api/citations/20170011656/downloads/20170011656.pdf','https://ntrs.nasa.gov/api/citations/20230003601/downloads/NASA%20TP-20220000355%20appxA.pdf'])
(OUT/'CALCULOS.json').write_text(json.dumps(result,indent=2))
lines=['# Arquitectura A: área, escala y referencia de potencia de estacionario','',
'**Estimaciones de cribado; no son prestaciones verificadas ni selección de motor.** Se conserva el diseño A aprobado. Masa de referencia 5 kg supuesta; cuatro rotores ilustrativos de diámetro de barrido calculado 82,024 mm a partir de sus vértices en el script CAD. Las escalas de 2 y 10 kg son operaciones algebraicas a densidad media constante, no presupuestos de masa cerrados.','',
'La referencia usa cuatro rotores libres ideales con carga igual, aire de 1,225 kg/m³, g=9,80665 m/s² y P=(mg)^(3/2)/√(2ρA_total). No incluye pérdidas ni maniobra. Un conducto puede contribuir al empuje y cambiar el flujo: esta referencia no se presenta como cota inferior universal del sistema con conductos ni como potencia eléctrica instalada. NASA NDARC diferencia explícitamente el rotor libre y el ventilador carenado.','',
'| Masa supuesta | Escala | Envolvente algebraica L × ancho × alto, mm | Ø de cada rotor, mm | Área total, m² | Potencia inducida ideal de referencia, W | Energía de referencia en 120 s, Wh |','|---:|---:|---|---:|---:|---:|---:|']
for a in scales:
    lines.append(f"| {a['mass_assumed_kg']} kg | {a['scale']:.3f} | {' × '.join(f'{x:.0f}' for x in a['envelope_mm'])} | {a['rotor_diameter_mm']:.1f} | {a['total_geometric_disk_area_m2']:.5f} | {a['isolated_free_rotor_ideal_induced_power_W']:.0f} | {a['reference_energy_Wh']['120']:.1f} |")
lines+=['','Las energías no equivalen a capacidad de batería ni autonomía: faltan potencia real, energía utilizable, reserva, refrigeración y masa de esa batería. A semejanza geométrica, área ∝ m^(2/3), carga de disco ∝ m^(1/3) y esta potencia de referencia ∝ m^(7/6). No se infiere que el mismo ventilador o mapa escale sin cambiar Reynolds, velocidad de punta y límites térmicos.','',
'| Ø rotor para 5 kg, mm | Potencia ideal de referencia, W | Separación entre discos al mantener el paso lateral original de 130 mm, mm |','|---:|---:|---:|']
for a in sweep:
    lines.append(f"| {a['rotor_diameter_mm']:.1f} | {a['isolated_free_rotor_ideal_induced_power_W']:.0f} | {a['disk_only_gap_at_unchanged_130mm_pair_pitch_mm']:.1f} |")
lines+=['','Una separación negativa implica solapamiento geométrico de los discos coplanares a los centros actuales. Una separación positiva no demuestra alojamiento: faltan camisas, holguras, espesores, estructura, conductos, motores y secciones locales de la carrocería. La tabla permite estudiar más área sin prometer que quepa dentro de la envolvente elegida.','',
'El CAD de estilo original tiene radio de taladro de camisa de 41 mm, frente a un vértice de hélice a √(41²+1²)=41,012 mm: no tenía holgura funcional definida. La rama preliminar retenía esas camisas. Se corrigió en `../CAD_integracion_coherente/A_integracion_conductos_coherentes.step`: cuatro conductos consolidados con radio interior de 42 mm y separación radial geométrica aproximada de 0,988 mm. Las comprobaciones locales están en su `VERIFICACION.json`; no declaran suficiente la holgura de operación ni cierran deformaciones o tolerancias.','',
'La CFD de entrada impuesta de 40 m/s solo ensaya un conducto sin rotor: no garantiza que el ventilador genere ese caudal o presión, ni demuestra el empuje útil exigido por el análisis de control. El dimensionamiento siguiente requiere una curva presión–caudal–potencia y un balance integrado de entrada/salida/carcasa.','',
'Fuentes primarias: [NASA NDARC Theory 2017](https://ntrs.nasa.gov/api/citations/20170011656/downloads/20170011656.pdf) y [NASA NDARC, apéndice teórico](https://ntrs.nasa.gov/api/citations/20230003601/downloads/NASA%20TP-20220000355%20appxA.pdf). Las cifras de las tablas proceden de `CALCULOS.json`, regenerable con `escala_area_potencia_A.py`.']
(OUT/'INFORME.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(output=str(OUT),reference_diameter_mm=diameter_mm,reference_powers_W={a['mass_assumed_kg']:a['isolated_free_rotor_ideal_induced_power_W'] for a in scales})))
