"""Check actual mechanism shapes versus C03 ring and gasket at three poses."""
from pathlib import Path
import json
import FreeCAD as App

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'producto_C03/5kg/C03_5kg_cerrado.FCStd'
MECH=HERE.parent/'producto_C04_estudio_bisagra_v2'
d=App.openDocument(str(BASE))
p={o.Label:o.Shape.copy() for o in d.Objects if o.Name.startswith('pieza_')}
obs={'aro':p['aro_C02_0_superior'],'junta':p['junta_C02_0_superior']}
output={'scope':'Tres posiciones discretas; pares de hardware contra aro y junta de C03. No verifica continuidad ni resto de piezas','states':[]}
for state in ('cerrado','elevado','abierto'):
 m=App.openDocument(str(MECH/f'C04_{state}.FCStd'))
 objs=list(m.getObject('Estudio_C04').Group)[3:]
 rows=[]
 for o in objs:
  for name,s in obs.items():
   try:
    intersection=o.Shape.common(s)
    rows.append({'elemento':o.Label,'obstaculo':name,'interseccion_mm3':intersection.Volume,'distancia_mm':o.Shape.distToShape(s)[0], 'valida':intersection.isNull() or intersection.isValid()})
   except Exception as e:
    rows.append({'elemento':o.Label,'obstaculo':name,'error':str(e)})
 output['states'].append({'estado':state,'pares':rows})
 print('AUDITADO',state,flush=True)
 App.closeDocument(m.Name)
(HERE/'ARO_Y_JUNTA.json').write_text(json.dumps(output,indent=2)+'\n')
App.closeDocument(d.Name)
