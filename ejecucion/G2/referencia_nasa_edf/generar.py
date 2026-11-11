"""Generate reproducible NASA comparison, no C02 flight predictions."""
from pathlib import Path
from dataclasses import asdict
import hashlib,json
from modelo import predict,hypothetical_hover,RPM_MIN,RPM_MAX
H=Path(__file__).resolve().parent
source=H.parent.parent.parent/'fuentes/uiuc_propdb/NASA_EDF_20230017299.pdf'
h=hashlib.sha256()
with source.open('rb') as f:
 for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
out={'source':'https://ntrs.nasa.gov/citations/20230017299','pdf_sha256':h.hexdigest(),
     'scope':'Modelo NASA 2F sin viento; referencia de software, no mapa C02 ni prueba de vuelo',
     'rpm_gate_provisional':[RPM_MIN,RPM_MAX],
     'assumptions':['4 ventiladores NASA iguales','empuje vertical igual y sin perdidas de instalacion','masa total hipotetica y gravedad estandar','sin control, reserva, sustentacion adicional ni transicion'],
     'illustrative_model_points':[asdict(predict(rpm)) for rpm in (8000,10000,17156.4,20000,24000)],
     'hypothetical_hover':[hypothetical_hover(m) for m in (2,5,10)],
     'geometry_comparison_mm':{'NASA_rotor_diameter':5.11*25.4,'C02_rotor_nominal':82,'NASA_motor_diameter':56,'C02_motor_envelope_diameter':21.8},
     'interpretation':'Modelo ajustado no equivale a mediciones puntuales ni a un ventilador instalado; evitar extrapolacion'}
(H/'RESULTADOS.json').write_text(json.dumps(out,indent=2)+'\n')
print('RESULTADOS_NASA_GENERADOS',flush=True)
