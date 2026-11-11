"""Document one synthetic wind-on input and high-speed screening."""
from pathlib import Path
from dataclasses import asdict
import hashlib,json
from modelo_viento import PSF_TO_PA,exploratory,Rejected
H=Path(__file__).resolve().parent
source=H.parent.parent.parent/'fuentes/uiuc_propdb/NASA_EDF_20230017299.pdf'
h=hashlib.sha256()
with source.open('rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
rho=1.225;sound=340.3
synthetic=exploratory(3*PSF_TO_PA,15,15000,rho,sound,75)
checks=[]
for speed in (600,1000):
 q=.5*rho*(speed/3.6)**2
 try:
  exploratory(q,0,15000,rho,sound,75)
  status='ERROR_FUE_ACEPTADO'
 except Rejected as e:status='RECHAZADO: '+str(e)
 checks.append({'speed_km_h':speed,'q_pa':q,'q_psf':q/PSF_TO_PA,'ratio_to_6psf':q/(6*PSF_TO_PA),'status':status})
if any(not c['status'].startswith('RECHAZADO') for c in checks):raise RuntimeError('no se rechazo alta velocidad')
out={'source_pdf_sha256':h.hexdigest(),'source':'https://ntrs.nasa.gov/citations/20230017299',
     'scope':'Reproduccion tentativa de ajuste 3F para ventilador NASA aislado, no validada ni aplicable a C02',
     'centering':'interpretado de seccion V.A y tabla 8; modelo dimensional 3F; no confirmado contra datos originales',
     'assumed_air':{'rho_kg_m3':rho,'speed_of_sound_m_s':sound},
     'synthetic_case_not_a_measured_point':asdict(synthetic),
     'high_speed_external_free_stream_checks':checks,
     'q6_speed_kmh_assumed_rho':(2*6*PSF_TO_PA/rho)**.5*3.6,
     'joint_coverage_proven':False,'flight_simulation_use_allowed':False}
(H/'RESULTADOS_VIENTO.json').write_text(json.dumps(out,indent=2)+'\n')
print('REFERENCIA_3F_GENERADA',flush=True)
