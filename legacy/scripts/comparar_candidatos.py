"""Published pack mass plus explicit engineering assumptions; no C-rating validation."""
import json
from pathlib import Path
P=Path(__file__).resolve().parents[2]/'resultados'
r=json.loads((P/'potencia_5kg_resumen.json').read_text());hover=r['summary'][0]['sample_max_W'];agile=r['summary'][2]['sample_max_W']
rows=[]
for count in [2,4]:
 mass=count*.357+.04;energy=count*22.2*2.2;usable=.7*energy
 avg=.9*hover+.1*agile
 rows.append(dict(packs=count,arrangement='12S1P' if count==2 else '12S2P',nominal_Wh=energy,mass_with_allowance_kg=mass,mass_tolerance_kg=count*.01,usable_energy_assumed_Wh=usable,hover_only_energy_minutes=usable/hover*60,mixed_energy_minutes=usable/avg*60,peak_energy_minutes=usable/agile*60,current_total_at_40V_A=agile/40,remaining_per_module_g=(5-3.46-mass)/8*1000))
# Find allowable combined battery resistance for chosen terminal voltage at peak.
limits=[]
for voltage in [40,42,44]:
 current=agile/voltage;limits.append(dict(terminal_V=voltage,current_A=current,max_total_pack_R_ohm_at_44_4V_open=(44.4-voltage)/current))
result=dict(candidates=rows,resistance_acceptance_sensitivity=limits,not_verified=['usable energy at current','voltage sag','continuous discharge','connector temperature','VP profile losses','aircraft mass closure'])
(P/'comparacion_baterias_concretas.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
