"""Create an identified research baseline without promoting assumptions to specifications."""
from pathlib import Path
import csv, hashlib, json, sys, importlib.metadata

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
source = ROOT/'modelos_integrados/producto_A07'

baseline = {
    'id': 'A07_RESEARCH_BASE_2026-11-03_r1',
    'date': '2026-11-03',
    'architecture': 'A_internal_fans',
    'scope': 'Research reference, not manufacturing or physically validated vehicle',
    'canonical_units': {'length': 'm', 'mass': 'kg', 'time': 's', 'force': 'N', 'torque': 'N m', 'temperature': 'K'},
    'cad_units': 'mm', 'cad_to_SI_length_factor': 0.001,
    'coordinate_frame': {'x': 'CAD longitudinal, nose at negative x', 'y': 'CAD lateral', 'z': 'up'},
    'flight_body_frame': {'name':'FLU', 'x':'forward towards nose', 'y':'left', 'z':'up',
                          'R_flight_from_CAD': [[-1,0,0],[0,-1,0],[0,0,1]],
                          'rule':'Transform vectors, CG and inertia consistently; apply CAD-to-FLU before flight attitude in visualization'},
    'mass_targets_kg': [2,5,10], 'integration_reference_mass_target_kg': 5,
    'mass_targets_are_actual_masses': False,
    'fan_reference': {'count': 4, 'axes': [0,0,1],
                      'centres_xy_m': [[-.2,-.076],[-.2,.076],[.2,-.076],[.2,.076]],
                      'nominal_bore_diameter_m': .084,
                      'scope': 'Geometric reference; effective throat, force/power maps and rotation hardware pending'},
    'geometry': {},
    'door_reference': {'translation_m': .01, 'rotation_deg': 110,
                       'scope': 'Two-coordinate sampled kinematic proposal; hardware not designed'},
    'tail_reference': {'count': 4, 'angles_about_x_deg': [45,135,225,315],
                       'scope': 'Candidate all-moving surfaces; aerodynamic/structural sizing pending'},
    'operating_reference': {'rho_kg_m3': 1.225, 'p_Pa': 101325, 'T_K': 288.15,
                            'mu_Pa_s': 1.7894e-5, 'g_m_s2': 9.80665, 'gamma': 1.4, 'R_J_kg_K': 287.05287,
                            'scope': 'Reference atmosphere for comparable calculations, not entire operating envelope'},
    'unidentified': ['installed force/moment/power maps', 'rotor/motor/ESC', 'axial engine and net thrust map',
                     'component mass/CG/inertia', 'door hardware', 'structural materials/laminates',
                     'thermal/energy installation', 'full aerodynamic derivatives', 'physical validation'],
    'historical_assumptions_not_specifications': {'fan_max_useful_N_at_5kg':21,'force_cone_deg':35,
                                               'actuator_tau_s':.08,'force_rate_N_s_at_5kg':50,
                                               'body_inertia_kgm2':[.035311862,.458989923,.475462439]},
    'physical_performance_validated': False,
}
for mass in (2,5,10):
    folder=source/f'{mass}kg'
    records={}
    for state in ('cerrado','elevado','abierto'):
        file=folder/f'A07_{state}.step'
        records[state]={'path':str(file.relative_to(ROOT)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
    meta=json.loads((folder/'manifest.json').read_text())
    baseline['geometry'][str(mass)]={'states':records,'nominal_part_records':len(meta['parts']),
                                   'scale_from_5kg':meta['scale'],
                                   'scope':'Nominal geometric similarity only; components must be redimensioned'}
(ROOT/'configuraciones/A07_BASE.json').write_text(json.dumps(baseline,indent=2,ensure_ascii=False))

reconciliation=[
    ['D01','Architecture A internal fans','User confirmation and modelos_integrados/DECISION-ARQUITECTURA.md','current','Do not substitute retractable B'],
    ['D02','A07 reference','modelos_integrados/producto_A07/LEEME.md','current_geometric','208 nominal parts; door/casing correction; mechanism incomplete'],
    ['D03','No CAD/tools found','DATOS-PARA-CERRAR-VALIDACION.md','superseded_availability_only','Data categories remain useful; availability claim is historical'],
    ['D04','Eight external rotors/457mm blades','REVISION-POTENCIA-Y-ESPACIO.md','historical_other_configuration','Do not transfer consumption, mass or thrust to four internal 84mm bores'],
    ['D05','21 N, cone35°, tau80ms','simulacion_vuelo_A/INFORME.md','assumed','Not motor specs or installed flow map'],
    ['D06','High-speed video 3/6/10g','vuelo_rapido_visual/INFORME.md','inverse_demand','Not prediction or achieved acceleration/speed'],
    ['D07','CFD 200 pseudoiterations','CFD/INFORME-CONVERGENCIA-AVANCE-A.md','failed_convergence','Finite fields are not accepted drag; slip wall omits skin friction'],
    ['D08','Door motion 61 nodes','modelos_integrados/producto_A07/VERIFICACION_RECORRIDO.json','sampled_geometry','Not continuous sweep, hardware or aerodynamic opening validation'],
    ['D09','FreeCAD 293 shapes','integracion_apps/freecad/IMPORTACION.json','import_hierarchy_count','Do not equate shape objects with 208 design part records'],
    ['D10','Closed styling loft CFD','CFD/avance_A_compresible_600kmh_LTS_cont_1000/compressible_assumptions.json','diagnostic_other_geometry','Not installed A07 with ports, fins and propulsion'],
    ['D11','Research paused','ESTADO-VERIFICACION-GLOBAL.md','historical_user_request_superseded_for_plan_execution','2026-11-03 active goal authorizes plan execution; audit before resuming each specific case'],
    ['D12','Mass-scaling dimensions','modelos_integrados/producto_A07/5kg/manifest.json','geometry_only','Actual mass, CG and inertia not closed in any variant'],
    ['D13','CAD nose -X versus flight +X','product CAD section coordinates and simular.py/calcular.py flight conventions','frame_mismatch_requires_transform','Use proper rotation diag(-1,-1,1) from CAD to FLU before assigning velocity/attitude'],
]
with (OUT/'REGISTRO-RECONCILIACION.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['id','item','source','evidence_status','execution_rule']);w.writerows(reconciliation)

scenarios={'revision':'REQUIREMENTS_RESEARCH_v1','date':'2026-11-03',
           'user_fixed':{'architecture':'internal fans','mass_targets_kg':[2,5,10],'speed_targets_kmh':[600,1000]},
           'mission_duration_scenarios_s':{'hover':[30,120,300],'fast_flight':[30,120,300]},
           'agility_investigation_levels_g':[.5,1,2],
           'kinematic_stress_demands_g':[3,6,10],
           'attitude_change_tests_deg':[30,90],
           'unfixed_acceptance_targets':{'position_error_m':None,'attitude_error_deg':None,'settling_time_s':None,
                                        'payload_kg':None,'jerk_m_s3':None,'maximum_body_rate_rad_s':None,
                                        'weather_envelope':None,'failure_recovery_class':None},
           'rule':'Levels are analysis scenarios, not agreed or demonstrated performance. Do not silently reduce the goal to .5g.'}
(ROOT/'configuraciones/ESCENARIOS_INVESTIGACION.json').write_text(json.dumps(scenarios,indent=2,ensure_ascii=False))
versions={'python':sys.version,'packages':{}}
for package in ('numpy','scipy','cadquery','gmsh','mitsuba','matplotlib','vtk','imageio-ffmpeg'):
    try:versions['packages'][package]=importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:versions['packages'][package]=None
(OUT/'ENTORNO_PYTHON.json').write_text(json.dumps(versions,indent=2))

assert baseline['architecture']=='A_internal_fans'
for m in ('2','5','10'):
    assert baseline['geometry'][m]['nominal_part_records']==208
    assert abs(baseline['geometry'][m]['scale_from_5kg']-(int(m)/5)**(1/3))<1e-10
print('Baseline, 9 STEP hashes, 13 reconciliations and research scenarios created')
