"""Manually verified minima from NASA19660003947 TableIII, printed pp13-14.
Only measured taps, not proof of entire surface/subsonic flow or drag divergence.
"""
import json
from scipy.optimize import brentq
from pathlib import Path
gamma=1.4
DATA={7:[(.6,-.086),(.8,-.107),(.9,-.135),(.95,-.182)],10:[(.6,-.048),(.8,-.069),(.9,-.085),(.95,-.099)]}
def cpstar(M):return 2/(gamma*M*M)*(((1+(gamma-1)*M*M/2)/(1+(gamma-1)/2))**(gamma/(gamma-1))-1)
def localmach(M,cp):
 p_ratio=1+gamma*M*M/2*cp
 return ((2/(gamma-1))*((1+(gamma-1)*M*M/2)*p_ratio**(-(gamma-1)/gamma)-1))**.5
rows=[]
for f,points in DATA.items():
 for M,cp in points:rows.append(dict(fineness=f,Mach_freestream=M,min_Cp_measured=cp,sonic_Cp=cpstar(M),local_Mach_isentropic=localmach(M,cp)))
 a,b=points[-2:]
 crossing=brentq(lambda M:a[1]+(b[1]-a[1])*(M-a[0])/(b[0]-a[0])-cpstar(M),a[0],b[0])
 rows.append(dict(fineness=f,interpolated_sonic_crossing_estimate=crossing,warning='Linear Cp interpolation and measured taps only; not measured critical Mach or drag divergence'))
p=Path(__file__).resolve().parents[2]/'resultados/nasa_presiones_contraste.json';p.write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
