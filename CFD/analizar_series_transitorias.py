"""Time-weighted diagnostic statistics, not a physical acceptance certificate.

Run against CASE/postProcessing (or a separate snapshot using --post-processing).
Adaptive timesteps must not count as equally weighted independent samples.
Piecewise-linear interpolation is used between available output samples.
"""
from pathlib import Path
import argparse,json,re
import numpy as np

NUM=re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')

def read_series(root,name,filename,columns):
    rows={};discarded=0;duplicates=0
    for p in sorted((root/name).glob('*/'+filename),key=lambda p:float(p.parent.name)):
        # A live writer can leave a partial last line; do not treat it as a row.
        for line in p.read_text().splitlines(keepends=True):
            if not line.strip() or line.lstrip().startswith('#'):continue
            values=[float(x) for x in NUM.findall(line)]
            if not line.endswith('\n') or len(values)!=columns or not np.isfinite(values).all():
                discarded+=1;continue
            if values[0] in rows:duplicates+=1
            rows[values[0]]=values
    a=np.array([rows[t] for t in sorted(rows)],dtype=float)
    if len(a)<2:raise ValueError(f'{name}: fewer than two complete output times')
    return a,dict(discarded_rows=discarded,overwritten_duplicate_times=duplicates)

def interval(t,y,start,end):
    if not t[0]<=start<end<=t[-1]:raise ValueError('Statistics require interpolation inside recorded range.')
    y=np.asarray(y,dtype=float)
    if y.ndim==1:y=y[:,None]
    inside=(t>start)&(t<end)
    times=np.r_[start,t[inside],end]
    left=np.array([np.interp(start,t,c) for c in y.T])
    right=np.array([np.interp(end,t,c) for c in y.T])
    values=np.vstack([left,y[inside],right])
    dt=np.diff(times)[:,None]
    mean=np.sum(dt*(values[:-1]+values[1:])/2,axis=0)/(end-start)
    # Exact second moment of the piecewise-linear interpolant; subtracting
    # two large nearly equal squares is avoided by centering first.
    v=values-mean
    variance=np.sum(dt*(v[:-1]**2+v[:-1]*v[1:]+v[1:]**2)/3,axis=0)/(end-start)
    return dict(time_weighted_mean=mean.tolist(),time_weighted_rms_fluctuation=np.sqrt(np.maximum(variance,0)).tolist(),min=values.min(axis=0).tolist(),max=values.max(axis=0).tolist(),duration_s=end-start)

def report_series(t,y,discard,tau):
    if t[-1]<=discard:
        return dict(statistics_withheld=True,reason='Initial discard interval not reached.',last_recorded_time_s=float(t[-1]))
    start=max(discard,float(t[0]));end=float(t[-1])
    result=interval(t,y,start,end)
    n=int(np.floor((end-start)/tau+1e-10));blocks=[]
    for i in range(n):
        a=start+i*tau;b=min(start+(i+1)*tau,end)
        blocks.append(dict(start_s=a,end_s=b,**interval(t,y,a,b)))
    result.update(statistics_withheld=False,complete_flow_through_blocks=n,blocks=blocks,physical_loads_accepted=False,confidence_interval=None,confidence_note='No confidence interval: blocks may remain correlated; independence and stationarity are unverified.')
    if n>=2:
        result['last_two_block_mean_difference']=(np.array(blocks[-1]['time_weighted_mean'])-np.array(blocks[-2]['time_weighted_mean'])).tolist()
    return result

def analyze(case,pp):
    meta=json.loads((case/'transient_assumptions.json').read_text())
    tau=meta['flow_through_time_s'];discard=meta['discard_before_s']
    result=dict(case=case.name,source_post_processing=str(pp.resolve()),discard_before_s=discard,flow_through_time_s=tau,method='Time-weighted piecewise-linear interpolation; exact interpolant variance. No extrapolation, no independent-sample assumption.',physical_loads_accepted=False,per_vane={},row_generalized_torques={})
    row_data={'X':[],'Y':[]}
    for name in sorted(p.name for p in pp.glob('force_vane*') if p.is_dir()):
        a,parse=read_series(pp,name,'forces.dat',13)
        force=a[:,1:4]+a[:,4:7];moment=a[:,7:10]+a[:,10:13]
        row='X' if 'vaneX' in name else 'Y';axis=0 if row=='X' else 1
        row_data[row].append((a[:,0],moment[:,axis]))
        result['per_vane'][name]=dict(parsing=parse,force_N=report_series(a[:,0],force,discard,tau),moment_about_vane_center_Nm=report_series(a[:,0],moment,discard,tau),hinge_axis=row,hinge_torque_Nm=report_series(a[:,0],moment[:,axis],discard,tau))
    if len(result['per_vane'])!=6:
        raise ValueError('Incomplete snapshot: expected six vane force histories.')
    for row,data in row_data.items():
        if len(data)!=3:raise ValueError(f'Expected three vanes in row {row}')
        start=max(t[0] for t,_ in data);end=min(t[-1] for t,_ in data)
        t=np.unique(np.concatenate([a[(a>=start)&(a<=end)] for a,_ in data]+[[start,end]]))
        total=sum(np.interp(t,a,y) for a,y in data)
        result['row_generalized_torques'][row]=dict(interpretation='Sum of signed local hinge torques for synchronous equal-angle row motion, before linkage ratio, friction, inertia or mechanical efficiency. Not a common-axis body moment.',torque_Nm=report_series(t,total,discard,tau))
    qi,di=read_series(pp,'flow_inlet','surfaceFieldValue.dat',2)
    qo,do=read_series(pp,'flow_outlet','surfaceFieldValue.dat',2)
    start=max(qi[0,0],qo[0,0]);end=min(qi[-1,0],qo[-1,0])
    t=np.unique(np.r_[qi[(qi[:,0]>=start)&(qi[:,0]<=end),0],qo[(qo[:,0]>=start)&(qo[:,0]<=end),0],start,end])
    inlet=np.interp(t,qi[:,0],qi[:,1]);outlet=np.interp(t,qo[:,0],qo[:,1])
    if np.any(abs(inlet)<1e-14):raise ValueError('Undefined relative mass imbalance: near-zero inlet flow.')
    rel=(inlet+outlet)/abs(inlet)
    result['mass_balance']=dict(inlet_parsing=di,outlet_parsing=do,max_abs_relative_imbalance_recorded=float(max(abs(rel))),after_discard=report_series(t,rel,discard,tau))
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('case',type=Path);parser.add_argument('--post-processing',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();pp=args.post_processing or args.case/'postProcessing'
    result=analyze(args.case,pp);out=args.output or args.case/'force_statistics_audit.json'
    out.write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps(dict(output=str(out),physical_loads_accepted=False,vanes=len(result['per_vane']),statistics_withheld=all(v['force_N']['statistics_withheld'] for v in result['per_vane'].values()))))

if __name__=='__main__':main()
