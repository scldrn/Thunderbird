"""Conditional high-speed screening from measured CAD; no installed drag claim."""
from pathlib import Path
import json,math,csv,hashlib
import numpy as np

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'aerodinamica_A'
geo=json.loads((OUT/'METROLOGIA.json').read_text())
rho=1.225;mu=1.7894e-5;gamma=1.4;R=287.05287;temperature=288.15
sound=math.sqrt(gamma*R*temperature);g=9.80665
def turbulent_cf(Re,M):return .455/(math.log10(Re)**2.58*(1+.144*M*M)**.65)
def plate(a,t,p,E=70e9,nu=.33,support='clamped'):
    D=E*t**3/(12*(1-nu**2));factor=1 if support=='clamped' else (5+nu)/(1+nu)
    w=factor*p*a**4/(64*D)
    stress=(3/4 if support=='clamped' else 3*(3+nu)/8)*p*a*a/(t*t)
    return dict(deflection_m=w,maximum_absolute_bending_stress_Pa=stress,deflection_over_thickness=w/t,linear_screen_applicable=w/t<=.2)
# Published Ansys/Roark verification example, in internally consistent inch/psi.
benchmark=plate(15,.25,3,E=30e6,nu=.3)
center_stress=3*(1+.3)*3*15**2/(8*.25**2)
assert abs(benchmark['deflection_m']/.0553-1)<.001 and abs(center_stress-5265)<1e-8
flight=[];panels=[];sizing=[]
for mass in [2,5,10]:
    scale=(mass/5)**(1/3);L=geo['bounds_m']['length']*scale
    area=geo['closed_surface_area_m2']*scale**2;Aref=geo['max_sampled_section_area_m2']*scale**2
    radius=.042*scale
    for speed in [600,800,1000]:
        v=speed/3.6;M=v/sound;q=.5*rho*v*v;Re=rho*v*L/mu;cf=turbulent_cf(Re,M)
        drag=q*area*cf;cpstar=2/(gamma*M*M)*(((1+(gamma-1)*M*M/2)/(1+(gamma-1)/2))**(gamma/(gamma-1))-1)
        flight.append(dict(mass_assumed_kg=mass,speed_kmh=speed,scale=scale,Mach=M,Reynolds_length=Re,q_Pa=q,closed_envelope_area_m2=area,reference_max_section_m2=Aref,Cf_turbulent_flat_plate=cf,skin_friction_reference_N=drag,skin_friction_reference_over_weight=drag/(mass*g),skin_friction_reference_power_W=drag*v,Cd_reference_for_drag_equals_weight=mass*g/(q*Aref),sonic_pressure_coefficient_isentropic=cpstar,stagnation_temperature_rise_K=temperature*(gamma-1)*M*M/2,scope='Smooth fully turbulent flat-plate correlation times closed hull area; no form factor, wave, base, trim, intake, jet or installation drag. Not a rigorous lower bound or measured drag.'))
        for dcp in [.05,.1,.5,1.]:
            pressure=q*dcp;A=math.pi*radius**2
            for support in ['clamped','simply_supported']:
                E=70e9;nu=.33;allowable=100e6;limit=.2
                ks=3/4 if support=='clamped' else 3*(3+nu)/8
                kw=1 if support=='clamped' else (5+nu)/(1+nu)
                tstress=radius*math.sqrt(ks*pressure/allowable)
                tdef=(kw*3*(1-nu**2)*pressure*radius**4/(16*E*limit))**.25
                tscreen=max(tstress,tdef)
                sizing.append(dict(mass_assumed_kg=mass,speed_kmh=speed,delta_Cp_assumed=dcp,support=support,screen_thickness_m=tscreen,stress_screen_thickness_m=tstress,deflection_screen_thickness_m=tdef,eight_flat_disc_material_mass_kg=8*A*tscreen*2700,scope='Hypothetical isotropic flat disc supported all around. Not a CAD curved door or manufacturing thickness; excludes hinges, seats, locks, seals, flutter and fatigue.'))
                for tmm in [.5,1.,1.5,2.]:
                    p=plate(radius,tmm/1000,pressure,support=support)
                    panels.append(dict(mass_assumed_kg=mass,speed_kmh=speed,delta_Cp_assumed=dcp,support=support,thickness_mm=tmm,pressure_difference_Pa=pressure,normal_force_on_flat_disc_N=pressure*A,equivalent_moment_about_tangent_axis_Nm=pressure*A*radius,**p))
positions=np.array(json.loads((ROOT/'vectorizacion_A/RESUMEN.json').read_text())['position_m'])
half_pitch=float(min(abs(positions[:,1])));bore_radius=.042;outside_radius=.044;axial_wall=.002
route=dict(geometry='Straight x-axis tube at y=z=0 crossing all four vertical fan channels.',fan_lateral_half_pitch_m=half_pitch,fan_bore_radius_m=bore_radius,fan_outer_sleeve_radius_m=outside_radius,max_axial_air_diameter_without_bore_intersection_m=2*(half_pitch-bore_radius),max_axial_outer_diameter_without_sleeve_intersection_m=2*(half_pitch-outside_radius),max_axial_inner_diameter_with_assumed_2mm_wall_m=2*(half_pitch-outside_radius-axial_wall),assumed_axial_wall_m=axial_wall,conclusion='Necessary local clearance bound at fan stations; does not prove a continuous intake/engine/nozzle installation. An aft-only engine or routed ducts require separate geometry.',tested_axial_outer_diameters=[])
for diameter in [.04,.05,.06,.08,.1]:
    gap=half_pitch-outside_radius-diameter/2
    route['tested_axial_outer_diameters'].append(dict(diameter_m=diameter,radial_gap_to_fan_outer_sleeve_m=gap,intersects_ideal_perpendicular_cylinders=gap<0))
result=dict(CAD_metrology_sha256=hashlib.sha256((OUT/'METROLOGIA.json').read_bytes()).hexdigest(),atmosphere_assumed=dict(rho_kgm3=rho,mu_Pas=mu,temperature_K=temperature,gamma=gamma,R_JkgK=R),plate_material_assumed=dict(E_Pa=70e9,nu=.33,rho_kgm3=2700,allowable_bending_stress_Pa=100e6,chosen_small_deflection_screen_w_over_t=.2),external_benchmark=dict(source='Ansys VM-Discovery-STRUCT-004 / Roark 1975',calculated_center_deflection_in=benchmark['deflection_m'],published_rounded_center_deflection_in=.0553,calculated_center_stress_psi=center_stress,published_center_stress_psi=5265),flight_screen=flight,panel_linear_raw_scenarios=panels,panel_thickness_screens=sizing,axial_route_clearance=route,installed_speed_or_structure_validated=False)
(OUT/'AVANCE_Y_TAPAS.json').write_text(json.dumps(result,indent=2))
for name,data in [('friccion_cerrada',flight),('tapas_escenarios',panels),('tapas_espesor_cribado',sizing)]:
    with (OUT/(name+'.csv')).open('w') as f:
        w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
lines=['# A: envolvente, avance rápido, tapas y conducto axial','',
'**Estado: cribado computacional; no valida vuelo, velocidad máxima, arrastre total ni estructura fabricable.** Las masas 2/5/10 kg siguen siendo objetivos supuestos. Se conserva la arquitectura A elegida.','',
'## Geometría medida en CAD','',
f"La envolvente cerrada de referencia mide {geo['bounds_m']['length']:.3f} × {geo['bounds_m']['width']:.3f} × {geo['bounds_m']['height']:.3f} m, encierra {1000*geo['gross_enclosed_volume_m3']:.2f} litros y tiene {geo['closed_surface_area_m2']:.4f} m² de superficie. Su sección máxima muestreada es {geo['max_sampled_section_area_m2']:.5f} m², equivalente a un círculo de diámetro {geo['max_equivalent_diameter_m']:.4f} m; L/D equivalente={geo['length_over_max_equivalent_diameter']:.3f}. Ese cociente no predice su Mach crítico.",'',
'Se reconstruyó el loft original anterior a los recortes, insertos, detalles y puerto posterior. Es una referencia aerodinámica cerrada: no representa puertas funcionales instaladas. El conjunto visual completo mide 1,345 m por sus piezas adicionales. No se trasladan aquí coeficientes de los husos circulares anteriores.','',
'La metrología usa integración adaptativa OCCT. Se comprobó la extracción de secciones contra un elipsoide analítico y el volumen mediante integración independiente de 135 y 269 secciones. También se compararon tres triangulaciones con el área y volumen del CAD. Los residuos numéricos no son tolerancias de fabricación. Datos: `METROLOGIA.json` y `secciones_envolvente.csv`.','',
f"Si se asignan 5 kg a esta envolvente, su densidad media respecto al volumen bruto sería {geo['mean_density_if_5kg_over_gross_envelope_kgm3']:.1f} kg/m³, distinta de los 200 kg/m³ supuestos en los primeros husos. No es densidad material ni prueba de que el volumen interior esté disponible después de instalar los componentes.",'',
'## Fricción de referencia','',
'Se aplica Cf=0,455 / [(log10 Re)^2,58 (1+0,144 M²)^0,65] y D_f=q Cf S. La ecuación se revisó visualmente en la página 5 del informe oficial [DLR IB 124-2010/3](https://elib.dlr.de/65162/1/DLR_IB_124-2010-3_-_BLWF_Evaluation.pdf). Se usa solo la correlación de placa lisa turbulenta; no se ha ejecutado BLWF ni se importa el factor de forma de su avión.','',
'**Son estimaciones condicionadas a esa correlación y al área cerrada.** No incluyen onda, separación, presión de base, sustentación/trimado, interferencias, tapas, tomas o empuje instalado. Tampoco son una cota inferior rigurosa: transición, presión local y geometría pueden cambiar la fricción. No se calcula una velocidad máxima con estas cifras.','',
'| Masa supuesta | Velocidad | Mach | Re por longitud | Fricción de referencia | D_f/peso | Potencia D_f V |','|---:|---:|---:|---:|---:|---:|---:|']
for a in flight:
    if a['speed_kmh'] in [600,1000]:lines.append(f"| {a['mass_assumed_kg']} kg | {a['speed_kmh']} km/h | {a['Mach']:.3f} | {a['Reynolds_length']:.2e} | {a['skin_friction_reference_N']:.1f} N | {a['skin_friction_reference_over_weight']:.2f} | {a['skin_friction_reference_power_W']/1000:.1f} kW |")
lines+=['',
'El Mach crítico y el de divergencia de arrastre permanecen sin determinar para esta forma. Se tabula Cp sónico isentrópico como criterio para futuras presiones CFD; no se calcula un Mach crítico a partir de L/D. NASA ensayó cuerpos elípticos y su equivalente circular de igual distribución de áreas a Mach 0,6, 0,9, 1,2, 1,5 y 2,0, y encontró dependencia de la sección y el ángulo de alabeo. Esto impide tratar ambas secciones como aerodinámicamente idénticas. [NASA TM-X-3129](https://ntrs.nasa.gov/citations/19750008439).','',
'El registro NASA se pudo verificar; la descarga local del PDF no transfirió datos y el lector web rechazó su tamaño. No se han extraído números de sus figuras ni se afirma una comparación cuantitativa de arrastre basada en ellas. El contraste anterior de Sears–Haack sigue siendo de otra geometría.','',
'## Tapas y aberturas','',
'Se midieron cuatro pasos verticales de radio 42 mm. Hay ocho extremos que cerrar si se sellan ambas caras en avance. Los pasos abiertos añaden paredes interiores; su área total no se usa como superficie exterior de la correlación anterior.','',
'La carga de tapa depende de Δp=p_interior−p_exterior, no de q por identidad. Se exploran |ΔCp|=0,05 / 0,1 / 0,5 / 1 con |Δp|=q|ΔCp|. Para un disco plano de radio a, F=|Δp|πa²; el momento equivalente respecto a un eje tangente es F a. Un asiento y cierre perimetral pueden transmitir esa carga sin que el servo sostenga todo ese momento. No se ha diseñado ese camino de cargas.','',
'El cribado estructural usa discos planos isotrópicos, E=70 GPa, ν=0,33 y densidad 2700 kg/m³ SUPUESTOS. No se selecciona un metal o laminado. Se comparan bordes empotrados y simplemente apoyados. La solución de placa empotrada w0=p a⁴/(64D), D=Et³/[12(1−ν²)], se contrasta con el caso analítico de [NASA/AIAA 2014](https://ntrs.nasa.gov/api/citations/20140004248/downloads/20140004248.pdf). El cálculo reproduce el benchmark externo [Ansys STRUCT-004](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/Ansys_3D_VM/Discovery/VM_3D_Design/disco_vm/topics/r_VM_3D_disco_004.html): 0,0553 pulgadas de flecha redondeada y 5265 psi de tensión central con sus propios datos.','',
'Se marca fuera del cribado lineal cualquier caso con w0/t>0,2, umbral conservador elegido para este estudio. Los valores lineales en esos casos se conservan como diagnósticos, no como tensiones reales ni fallo estructural demostrado. El espesor de cribado exige además tensión de flexión ≤100 MPa, límite hipotético, sin certificación de material.','',
'| 5 kg, 1000 km/h: ΔCp supuesto | Fuerza por disco | Momento tangente equivalente | Espesor de cribado empotrado / apoyado | Masa de ocho discos, empotrado / apoyado |','|---:|---:|---:|---:|---:|']
for cp in [.1,.5,1.]:
    a=next(x for x in panels if x['mass_assumed_kg']==5 and x['speed_kmh']==1000 and x['delta_Cp_assumed']==cp)
    z=[next(x for x in sizing if x['mass_assumed_kg']==5 and x['speed_kmh']==1000 and x['delta_Cp_assumed']==cp and x['support']==s) for s in ['clamped','simply_supported']]
    lines.append(f"| {cp} | {a['normal_force_on_flat_disc_N']:.1f} N | {a['equivalent_moment_about_tangent_axis_Nm']:.2f} N·m | {z[0]['screen_thickness_m']*1000:.2f} / {z[1]['screen_thickness_m']*1000:.2f} mm | {z[0]['eight_flat_disc_material_mass_kg']:.3f} / {z[1]['eight_flat_disc_material_mass_kg']:.3f} kg |")
lines+=['',
'Estas masas excluyen bisagras, cierres, asientos, actuadores, sellos y refuerzos. Los discos planos no reproducen las tapas curvas del loft. Se requieren un modelo de pared/material, apoyos reales, presiones, fatiga y aeroelasticidad; una comprobación estática no acredita ausencia de flutter.','',
'## Conflicto de espacio del conducto axial','',
f"En las estaciones de ventiladores, sus ejes verticales están en y=±{half_pitch*1000:.0f} mm, con radio interior 42 mm y exterior de camisa 44 mm. Un conducto recto coaxial con x solo deja diámetro exterior máximo {route['max_axial_outer_diameter_without_sleeve_intersection_m']*1000:.0f} mm antes de intersectar esas camisas. Con pared axial SUPUESTA de 2 mm, el diámetro de aire baja a {route['max_axial_inner_diameter_with_assumed_2mm_wall_m']*1000:.0f} mm. No se ha añadido margen de montaje.",'',
'Se contrastó la cota con intersecciones sobre las cuatro camisas del STEP integrado: los cilindros axiales exteriores de 40 y 42 mm no intersectan sus sólidos; 46, 50, 60, 80 y 100 mm sí los intersectan. El contacto límite no es holgura de montaje. Los volúmenes y la huella del STEP están en `VERIFICACION_RUTA_AXIAL.json`. Es una condición geométrica necesaria para esa ruta concreta. No demuestra una toma–motor–tobera continua, caudal suficiente o rendimiento de toma. Un motor instalado solo por detrás de los ventiladores, tomas laterales o una redistribución de estaciones pueden cambiar la restricción y deben compararse con geometría y flujo propios. El puerto posterior del diseño es representativo, no una tobera dimensionada.','',
'## Consecuencia para continuar el objetivo completo','',
'Hay que cerrar conjuntamente área de rotor, masa, energía y control de estacionario con la ruta de propulsión rápida y sus tapas. El próximo modelo aerodinámico debe representar una instalación única, no sumar coeficientes de cuerpos y mecanismos incompatibles. Siguen pendientes presiones y arrastre compresible verificados, rotor instalado, tomas/toberas, cierre de masa e inercias y validación estructural/dinámica. No se declara óptimo global ni imposibilidad física del concepto.','',
'Código: `medir_aerodinamica_A.py` y `evaluar_avance_y_tapas_A.py`. Resultados: JSON y CSV de esta carpeta; los STEP son referencias de envolvente y pasos, no planos de puertas.']
(OUT/'INFORME-AVANCE-Y-TAPAS.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(report=str(OUT/'INFORME-AVANCE-Y-TAPAS.md'),flight_cases=len(flight),panel_cases=len(panels),thickness_screens=len(sizing),axial_clear_air_diameter_mm=route['max_axial_inner_diameter_with_assumed_2mm_wall_m']*1000)))
