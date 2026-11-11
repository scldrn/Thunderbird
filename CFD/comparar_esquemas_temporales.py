"""Compare paired histories over their common physical-time interval.

Numerical scheme sensitivity only: agreement cannot validate physical loads.
"""
from pathlib import Path
import argparse
import json
import numpy as np
from analizar_series_transitorias import read_series, interval


def compare(t0, y0, t1, y1, start, end):
    a=max(start, float(t0[0]), float(t1[0]))
    b=min(end, float(t0[-1]), float(t1[-1]))
    if b <= a:
        raise ValueError('No common interval after the requested startup exclusion.')
    t=np.unique(np.r_[a, t0[(t0>a)&(t0<b)], t1[(t1>a)&(t1<b)], b])
    y0=np.asarray(y0); y1=np.asarray(y1)
    if y0.ndim==1:y0=y0[:,None]
    if y1.ndim==1:y1=y1[:,None]
    x=np.column_stack([np.interp(t,t0,c) for c in y0.T])
    y=np.column_stack([np.interp(t,t1,c) for c in y1.T])
    delta=interval(t,y-x,a,b)
    bias=np.array(delta['time_weighted_mean'])
    rms=np.sqrt(bias**2+np.array(delta['time_weighted_rms_fluctuation'])**2)
    # Symmetric normalization avoids selecting one scheme as ground truth.
    reference=[]
    for z in (x,y):
        s=interval(t,z,a,b)
        reference.append(np.array(s['time_weighted_mean'])**2+
                         np.array(s['time_weighted_rms_fluctuation'])**2)
    norm=np.sqrt((reference[0]+reference[1])/2)
    return dict(start_s=a,end_s=b,interpolation_nodes=len(t),
                signed_mean_difference=bias.tolist(),rms_difference=rms.tolist(),
                max_absolute_difference=np.max(abs(y-x),axis=0).tolist(),
                relative_rms_difference=[float(r/n) if n>1e-12 else None for r,n in zip(rms,norm)],
                normalization='RMS difference / symmetric RMS magnitude; null near zero.')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('euler',type=Path);p.add_argument('backward',type=Path)
    p.add_argument('--start',type=float,required=True)
    p.add_argument('--end',type=float,default=float('inf'))
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.start<=0:raise ValueError('Explicit positive startup exclusion required.')
    result=dict(purpose='Numerical sensitivity, not load acceptance or temporal convergence.',
                physical_loads_accepted=False,temporal_order_verified=False,
                start_requested_s=a.start,sources=[str(a.euler.resolve()),str(a.backward.resolve())],
                per_vane={},flow={})
    names0={x.name for x in a.euler.glob('force_vane*') if x.is_dir()}
    names1={x.name for x in a.backward.glob('force_vane*') if x.is_dir()}
    if names0!=names1 or len(names0)!=6:raise ValueError('Expected the same six vane histories.')
    for name in sorted(names0):
        x,px=read_series(a.euler,name,'forces.dat',13)
        y,py=read_series(a.backward,name,'forces.dat',13)
        result['per_vane'][name]=dict(parsing=[px,py])
        for label,values0,values1 in [
            ('force_N',x[:,1:4]+x[:,4:7],y[:,1:4]+y[:,4:7]),
            ('local_moment_Nm',x[:,7:10]+x[:,10:13],y[:,7:10]+y[:,10:13])]:
            result['per_vane'][name][label]=compare(x[:,0],values0,y[:,0],values1,a.start,a.end)
    for name in ('flow_inlet','flow_outlet'):
        x,px=read_series(a.euler,name,'surfaceFieldValue.dat',2)
        y,py=read_series(a.backward,name,'surfaceFieldValue.dat',2)
        result['flow'][name]=dict(parsing=[px,py],comparison_m3_s=compare(x[:,0],x[:,1],y[:,0],y[:,1],a.start,a.end))
    result['limitations']=[
        'Adaptive times are interpolated on their union, never compared by step index.',
        'No time-step refinement or mesh-independence proof; two schemes may share bias.',
        'Startup exclusion is explicit, not proof that the initial physical transient has ended.',
        'Local vane loads omit duct walls and rotor; not net installed propulsive force.',
        'Live snapshots may end at different times; only common recorded intervals are used.']
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps(dict(output=str(a.output),vanes=len(names0),physical_loads_accepted=False)))


if __name__=='__main__':main()
