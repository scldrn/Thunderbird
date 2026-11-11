"""Conservative axis-aligned bounds for the prescribed C04 rigid motions.

Inputs are axis-aligned bounds in mm. Rotation is about +x after +z lift.
The input solid must be entirely inside its input bounds. Box-corner extrema
are exact for this rigid motion, before accounting for kernel tolerances.
"""
import itertools
import math


def trig_extrema(a, b, lo, hi):
    """Bounds of a*cos(t)+b*sin(t), for radians lo<=t<=hi."""
    if lo > hi:
        raise ValueError('angle interval reversed')
    points = [lo, hi]
    phase = math.atan2(b, a)
    k0 = math.ceil((lo - phase) / math.pi)
    k1 = math.floor((hi - phase) / math.pi)
    points.extend(phase + k * math.pi for k in range(k0, k1 + 1))
    values = [a * math.cos(t) + b * math.sin(t) for t in points]
    return min(values), max(values)


def motion_bounds(bounds, axis, lift, angle_deg, kind, margin):
    """Return bounds of fixed, translating or translating+rotating boxes."""
    if kind not in ('fijo','traslacion','giro') or lift < 0 or margin < 0:
        raise ValueError('unsupported motion')
    lo = list(bounds[::2]); hi = list(bounds[1::2])
    if any(a > b for a,b in zip(lo,hi)):
        raise ValueError('invalid bounds')
    low = list(lo); high = list(hi)
    if kind in ('traslacion','giro'):
        high[2] += lift
    if kind == 'giro':
        t0,t1=sorted((0.0,math.radians(angle_deg)))
        for y,z in itertools.product((lo[1],hi[1]),(lo[2],hi[2])):
            dy=y-axis[1]
            dz=z+lift-(axis[2]+lift)
            ylo,yhi=trig_extrema(dy,-dz,t0,t1)
            zlo,zhi=trig_extrema(dz,dy,t0,t1)
            low[1]=min(low[1],axis[1]+ylo)
            high[1]=max(high[1],axis[1]+yhi)
            low[2]=min(low[2],axis[2]+lift+zlo)
            high[2]=max(high[2],axis[2]+lift+zhi)
    return tuple(v for pair in zip((v-margin for v in low),(v+margin for v in high)) for v in pair)
