"""NASA 20230017299, wind-off 2F polynomial benchmark; not a C02 model.

Inputs rpm; coefficients use n [rev/s] centred at the run 116 median.
Outputs force N and measured-supply power model W; see accompanying report.
The rpm gate is an intentionally conservative exploratory subset read from
figure 14, NOT a proven multidimensional DOE validity hull.
"""
from dataclasses import dataclass
import math

LBF_TO_N = 4.4482216152605
CENTRE_REV_S = 285.94
RPM_MIN = 8000.0
RPM_MAX = 24000.0
G_STANDARD = 9.80665

@dataclass(frozen=True)
class Prediction:
    rpm: float
    thrust_N: float
    dc_power_W: float


def predict(rpm: float) -> Prediction:
    if not math.isfinite(rpm) or not RPM_MIN <= rpm <= RPM_MAX:
        raise ValueError('rpm fuera del intervalo exploratorio 8000–24000')
    dn = rpm / 60.0 - CENTRE_REV_S
    thrust_lbf = 9.806 + 0.06922 * dn + 0.0001204 * dn ** 2
    power_kw = 1.998 + 0.02040 * dn + 0.00007476 * dn ** 2 + 0.0000001119 * dn ** 3
    if thrust_lbf <= 0 or power_kw <= 0:
        raise ValueError('prediccion no fisica en intervalo de exploracion')
    return Prediction(rpm, thrust_lbf * LBF_TO_N, power_kw * 1000.0)


def rpm_for_thrust(thrust_N: float) -> float:
    if not math.isfinite(thrust_N):
        raise ValueError('empuje no finito')
    lo, hi = RPM_MIN, RPM_MAX
    if not predict(lo).thrust_N <= thrust_N <= predict(hi).thrust_N:
        raise ValueError('empuje fuera del intervalo exploratorio')
    for _ in range(70):
        mid = (lo + hi) / 2
        if predict(mid).thrust_N < thrust_N:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def hypothetical_hover(mass_kg: float, fans: int = 4) -> dict:
    if not math.isfinite(mass_kg) or mass_kg <= 0 or not isinstance(fans, int) or isinstance(fans, bool) or fans <= 0:
        raise ValueError('masa y numero de ventiladores invalidos')
    required_N = mass_kg * G_STANDARD / fans
    try:
        p = predict(rpm_for_thrust(required_N))
        result = {'status': 'modelo_condicional', 'rpm': p.rpm,
                  'per_fan_power_W': p.dc_power_W, 'total_power_W': fans * p.dc_power_W}
    except ValueError:
        result = {'status': 'fuera_intervalo_exploratorio', 'rpm': None,
                  'per_fan_power_W': None, 'total_power_W': None}
    return {'mass_kg': mass_kg, 'fans': fans, 'thrust_per_fan_N': required_N,
            'motor_mass_kg': fans * 1.1, 'mass_left_before_other_components_kg': mass_kg - fans * 1.1, **result}
