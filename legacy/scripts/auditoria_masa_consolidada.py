"""Accounting audit at frozen5kg, not an iterative vehicle mass closure.
Retains previous reserve; added aero panels do not include new mechanisms.
"""
import csv,json
from trimado_superficies import hull,OUT

def main():
    fixed=dict(engine=1.08,motors=8*.128,fuel=.156,skin_old=.35,
               arms_locks=.25,avionics_wiring=.20,engine_installation=.15,contingency=.25)
    assert abs(sum(fixed.values())-3.46)<1e-12
    battery=.754
    # Blades30g, ESC20g, servo20g per station: assumptions, NOT verified BOM.
    station_without_hub=8*(.03+.02+.02)
    previous_remaining=5-sum(fixed.values())-battery-station_without_hub
    source=list(csv.DictReader((OUT/'comparacion_integrada_CONDICIONAL.csv').open()))
    rows=[]
    for f in [4,6,8]:
      design=next(r for r in source if float(r['mass_kg'])==5 and float(r['fineness'])==f)
      panelmass=float(design['panel_mass_ASSUMED_kg'])
      geo=hull(5,f)
      for label,skinmass in [('old_skin_allowance',.35),('isotropic_skin_02mm',geo['wet_m2']*2700*.0002),('isotropic_skin_05mm',geo['wet_m2']*2700*.0005)]:
        subtotal=sum(fixed.values())-.35+skinmass+battery+station_without_hub+panelmass
        rows.append(dict(fineness=f,skin_scenario=label,skin_kg=skinmass,
           aerodynamic_panels_kg=panelmass,subtotal_excluding_hubs_and_new_mechanisms_kg=subtotal,
           remaining_to_5kg_kg=5-subtotal,remaining_if_prior_025kg_reserve_removed_kg=5-subtotal+.25,
           warning='Frozen mass/power/CG and load-derived geometry; not self-consistent closure. Existing0.25kg reserve retained in subtotal.'))
    with (OUT/'masa_consolidada_5kg_ESCENARIOS.csv').open('w') as file:
      writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    result=dict(fixed_budget=fixed,battery_assumed_kg=battery,
        station_parts_excluding_hubs_assumed_kg=station_without_hub,
        previous_hub_and_missing_parts_margin_kg=previous_remaining,
        rows=rows,conclusion='These additions invalidate the old available-margin claim under retained allocations; not proof no5kg architecture can work.')
    (OUT/'masa_consolidada_5kg_RESUMEN.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
