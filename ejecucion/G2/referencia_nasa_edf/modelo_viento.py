"""Tentative NASA 3F polynomial interpretation; NOT a verified DOE map.

Factor limits are necessary screening checks, not proof of joint coverage.
All returned values explicitly carry unverified status; never feed C02 flight
simulation. Pressure is free-stream dynamic pressure; output T is axial EDF
thrust per the NASA force definition, not a complete six-component load.
"""
import math
from dataclasses import dataclass

PSF_TO_PA = 47.88025898033584
D_M = 5.11 * .0254
RPM_MIN_PROVISIONAL = 8000.
RPM_MAX_PROVISIONAL = 24000.

class Rejected(ValueError):
    pass

@dataclass(frozen=True)
class Estimate:
    status: str
    q_pa: float
    velocity_m_s: float
    incidence_deg: float
    rpm: float
    advance_ratio: float
    jx: float
    jz: float
    tip_mach: float
    ct: float
    thrust_N: float
    power_W: float


def ct_from_centered(x: float, z: float, m: float) -> float:
    return 1.248 - .9675*x - .1164*z + .3700*x*m + 1.372*x*x*m


def power_w_from_centered(j: float, m: float) -> float:
    return 1000.0*(2.552 - .2934*j + 20.15*m - 1.566*j*m + 54.59*m*m + 52.54*m*m*m)


def exploratory(q_pa: float, incidence_deg: float, rpm: float, rho_kg_m3: float, sound_m_s: float, voltage_V: float) -> Estimate:
    values=(q_pa,incidence_deg,rpm,rho_kg_m3,sound_m_s,voltage_V)
    if not all(math.isfinite(v) for v in values):raise Rejected('entrada no finita')
    if rho_kg_m3<=0 or sound_m_s<=0:raise Rejected('atmosfera no fisica')
    if not .25*PSF_TO_PA<=q_pa<=6*PSF_TO_PA:raise Rejected('presion fuera de los limites de factores DOE 3F')
    if not 0<=incidence_deg<=30:raise Rejected('incidencia fuera de los limites de factores DOE 3F')
    if abs(voltage_V-75.)>1e-9:raise Rejected('DOE 3F usa 75 V')
    if not RPM_MIN_PROVISIONAL<=rpm<=RPM_MAX_PROVISIONAL:raise Rejected('rpm fuera de la ventana numerica provisional')
    n=rpm/60.;speed=math.sqrt(2*q_pa/rho_kg_m3);j=speed/(n*D_M);angle=math.radians(incidence_deg)
    jx=j*math.cos(angle);jz=j*math.sin(angle);tip=math.pi*n*D_M/sound_m_s
    ct=ct_from_centered(jx-.313,jz-.074,tip-.374)
    power=power_w_from_centered(j-.324,tip-.374)
    thrust=ct*rho_kg_m3*n*n*D_M**4
    if not all(math.isfinite(v) for v in (ct,power,thrust)) or power<=0:raise Rejected('salida numerica no fisica')
    return Estimate('EXPLORATORIO_COBERTURA_CONJUNTA_NO_DEMOSTRADA',q_pa,speed,incidence_deg,rpm,j,jx,jz,tip,ct,thrust,power)
