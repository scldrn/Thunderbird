"""Conditional mass/energy screening using the static candidate. Not mass closure.
Rotor-specific thrust, disk size, efficiency, battery power are assumed independently;
combinations are sensitivity cases, NOT purchasable hardware claims.
"""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'resultados'
os.environ['MPLCONFIGDIR']=str(OUT/'mpl-cache')
import numpy as np
from scipy.optimize import linprog,minimize
from itertools import product
import json,csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from calcular import G,RHO

def main():
    data=json.loads((OUT/'configuracion_control_HIPOTESIS.json').read_text());B=np.array(data['B_normalized']);rec=data['record']
    T=rec['per_rotor_limit_for_1g_N'];mass=10.
    directions=np.array([v for v in product([-1.,0.,1.],repeat=3) if any(v)])
    directions=directions/np.linalg.norm(directions,axis=1)[:,None]
    allocations=[];maxres=0.
    for magnitude in [mass*G,2*mass*G]:
      for d in directions:
        target=np.r_[magnitude*d,np.zeros(3)]
        feasible=linprog(np.zeros(8),A_eq=B,b_eq=target,bounds=[(-T,T)]*8,method='highs')
        assert feasible.success
        objective=lambda f:np.sum(np.abs(f)**1.5)
        jac=lambda f:1.5*np.sign(f)*np.sqrt(np.abs(f))
        sol=minimize(objective,feasible.x,jac=jac,bounds=[(-T,T)]*8,constraints={'type':'eq','fun':lambda f:B@f-target,'jac':lambda f:B},method='SLSQP',options={'ftol':1e-9,'maxiter':500})
        assert sol.success,sol.message
        err=np.max(np.abs(B@sol.x-target));maxres=max(maxres,float(err));assert err<1e-6
        allocations.append(dict(force_magnitude_N=magnitude,direction=d.tolist(),force_rotors_N=sol.x.tolist(),sum_abs_f15=objective(sol.x)))
    (OUT/'asignaciones_minima_potencia_IDEAL.json').write_text(json.dumps(allocations,indent=2))
    cost_hover=max(r['sum_abs_f15'] for r in allocations if r['force_magnitude_N']==mass*G)
    cost_agile=max(r['sum_abs_f15'] for r in allocations if r['force_magnitude_N']==2*mass*G)
    rows=[]
    for diam in [.15,.20,.25,.30]:
      area=np.pi*diam**2/4
      for eff in [.5,.65,.8]:
        hover=cost_hover/np.sqrt(2*RHO*area)/eff
        agile=cost_agile/np.sqrt(2*RHO*area)/eff
        for specific in [50/.448,150.,200.]:
         motor_mass=8*T/specific
         for other in [2.,3.]:
          for minutes in [.5,2.,5.]:
            for bpower in [2000.,4000.,8000.]:
             # 10% agility duty assumed; acceleration-power evaluated with stationary disk formula.
             avg=.9*hover+.1*agile
             battery_energy=avg*minutes/60/200
             battery_power=agile/bpower
             battery=max(battery_energy,battery_power)
             residual=mass-2.155-motor_mass-other-battery
             rows.append(dict(rotor_diameter_m=diam,effective_electric_efficiency=eff,motor_specific_thrust_Nkg=specific,motors_rotors_mass_kg=motor_mass,other_system_mass_kg=other,hover_mode_min=minutes,battery_specific_power_Wkg=bpower,hover_W=hover,agility_sample_W=agile,battery_energy_kg=battery_energy,battery_power_kg=battery_power,battery_required_kg=battery,fuel_mass_available_kg=max(0,residual),mass_deficit_kg=max(0,-residual),full_throttle_fuel_budget_min=max(0,residual)/(.820*.8),status='necessary_mass_screen_not_validated_aircraft'))
    with (OUT/'masa_energia_10kg_CONDICIONAL.csv').open('w') as f:
      wr=csv.DictWriter(f,fieldnames=rows[0]);wr.writeheader();wr.writerows(rows)
    base=[r for r in rows if r['rotor_diameter_m']==.25 and r['effective_electric_efficiency']==.65 and r['motor_specific_thrust_Nkg']==50/.448 and r['other_system_mass_kg']==2 and r['battery_specific_power_Wkg']==4000]
    (OUT/'ejemplo_masa_energia.json').write_text(json.dumps(dict(cases=base,allocation_max_residual=maxres,sampled_directions=26,continuous_direction_power_bound=False,notes='No time at 1000km/h can be deduced: missing installed engine thrust map and full drag. Module mass differs from inertia hypothesis; iterate mass distribution before physical conclusions.'),indent=2))
    fig,ax=plt.subplots(figsize=(8,4.5))
    for dia in [.15,.2,.25,.3]:
      sub=[r for r in rows if r['rotor_diameter_m']==dia and r['effective_electric_efficiency']==.65 and r['motor_specific_thrust_Nkg']==50/.448 and r['other_system_mass_kg']==2 and r['battery_specific_power_Wkg']==4000]
      ax.plot([r['hover_mode_min'] for r in sub],[r['full_throttle_fuel_budget_min'] for r in sub],'o-',label=f'Rotor Ø {dia*100:.0f} cm')
    ax.set_xlabel('Duración eléctrica supuesta [min]');ax.set_ylabel('Combustible restante / consumo máximo [min]');ax.legend();ax.grid(alpha=.2)
    ax.set_title('Cribado de masa de 10 kg · no demuestra vuelo rápido')
    fig.text(.5,.015,'200 Wh/kg utilizables; 4 kW/kg; 2 kg otros sistemas; motores extrapolados de referencia.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(OUT/'frontera_masa_CONDICIONAL.png',dpi=170)
    print(json.dumps(base,indent=2))
if __name__=='__main__':main()
