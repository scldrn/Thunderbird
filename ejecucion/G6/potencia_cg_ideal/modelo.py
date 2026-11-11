"""Quasistatic four-ideal-disk reference, NOT an installed C02 plant.

All four force vectors are parallel. Application points and CG are coplanar,
weights nonnegative, no aerodynamics, reaction torque or motor dynamics.
The free-rotor hover power formula is a comparison, not a ducted-fan bound.
"""
from dataclasses import dataclass
import math

G=9.80665
RHO=1.225
D5_M=.082

class Infeasible(ValueError):pass

@dataclass(frozen=True)
class Allocation:
    weights: tuple
    fractions_x_y: tuple
    max_weight: float
    weighted_power_factor: float


def allocate(cx_fraction, cy_fraction, cap_fraction=None):
    """Minimize sum(w**1.5) for 2x2 force grid and optional per-unit cap.

    Order ++,+-,-+,--. This is an exact one-variable convex problem up to
    floating-point/bisection error, within the common-direction assumption.
    """
    vals=(cx_fraction,cy_fraction)
    if not all(math.isfinite(v) and -1<=v<=1 for v in vals):raise Infeasible('CG fuera del rectangulo o no finito')
    a=(1+cx_fraction)/2;b=(1+cy_fraction)/2
    low=max(0.,a+b-1);high=min(a,b)
    if cap_fraction is not None:
        if not math.isfinite(cap_fraction) or cap_fraction<0:raise Infeasible('limite invalido')
        k=cap_fraction
        low=max(low,a-k,b-k);high=min(high,k,k-1+a+b)
    if low>high+1e-12:raise Infeasible('sin reparto paralelo con ese limite')
    if low>high:low=high=(low+high)/2
    def deriv(t):
        return math.sqrt(max(t,0))-math.sqrt(max(a-t,0))-math.sqrt(max(b-t,0))+math.sqrt(max(1-a-b+t,0))
    lo,hi=low,high
    for _ in range(90):
        mid=(lo+hi)/2
        if deriv(mid)<0:lo=mid
        else:hi=mid
    t=(lo+hi)/2
    w=(t,a-t,b-t,1-a-b+t)
    if min(w)<-1e-10 or (cap_fraction is not None and max(w)>cap_fraction+1e-10):raise ArithmeticError('reparto fuera de limites')
    w=tuple(max(0.,v) for v in w)
    factor=sum(v**1.5 for v in w)/.5
    return Allocation(w,(a,b),max(w),factor)


def scenario(mass_kg,cx_fraction,cy_fraction,ax_g,az_g=0.,cone_deg=45.,per_fan_limit_N=None):
    v=(mass_kg,cx_fraction,cy_fraction,ax_g,az_g,cone_deg)
    if not all(math.isfinite(x) for x in v) or mass_kg<=0 or ax_g<0 or 1+az_g<=0 or not 0<=cone_deg<90:raise ValueError('entrada fuera del dominio')
    scale=(mass_kg/5.)**(1/3)
    dia=D5_M*scale
    thrust=mass_kg*G*math.hypot(ax_g,1+az_g)
    angle=math.degrees(math.atan2(ax_g,1+az_g))
    in_cone=angle<=cone_deg+1e-10
    alloc=allocate(cx_fraction,cy_fraction)
    p_uniform=thrust**1.5/math.sqrt(2*RHO*4*(math.pi*dia*dia/4))
    cap=per_fan_limit_N/thrust if per_fan_limit_N is not None else None
    try:
        bounded=allocate(cx_fraction,cy_fraction,cap) if cap is not None else alloc
        feasible_cap=True
    except Infeasible:
        bounded=None;feasible_cap=False
    return {'mass_kg':mass_kg,'scaled_diameter_m':dia,'cx_fraction':cx_fraction,'cy_fraction':cy_fraction,
            'ax_g':ax_g,'az_g':az_g,'cone_deg':cone_deg,'angle_deg':angle,'cone_possible':in_cone,
            'total_thrust_N':thrust,'unconstrained_weights':alloc.weights,
            'max_individual_thrust_N':thrust*alloc.max_weight,'uniform_ideal_W':p_uniform,
            'min_ideal_W':p_uniform*alloc.weighted_power_factor,'power_factor':alloc.weighted_power_factor,
            'per_fan_limit_N':per_fan_limit_N,'cap_feasible_common_direction':feasible_cap,
            'bounded_weights':bounded.weights if bounded else None,
            'bounded_ideal_W':p_uniform*bounded.weighted_power_factor if bounded else None,
            'joint_scenario_feasible_in_this_model':in_cone and feasible_cap}
