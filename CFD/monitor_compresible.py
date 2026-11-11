"""Read completed solver log blocks; not a live-process or acceptance proof."""
from pathlib import Path
import argparse,json,re,math
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--case',default='avance_A_compresible_600kmh_Euler_diag_v3');a=p.parse_args();case=ROOT/a.case
m=json.loads((case/'compressible_assumptions.json').read_text());s=(case/'log.foamRun').read_text();completed=[];diagnostics=[]
for chunk in re.split(r'\nTime = ',s)[1:]:
 match=re.match(r'([\deE.+-]+)',chunk)
 if not match:continue
 counter=float(match[1]);clock=re.search(r'ClockTime = ([\deE.+-]+)',chunk)
 if clock:completed.append(dict(counter=counter,clock_s=float(clock[1])))
 def value(pattern):
  found=re.findall(pattern,chunk)
  return float(found[-1]) if found else None
 u=value(r'maxMag\(all\) of U = ([\deE.+-]+)');temp=value(r'min\(all\) of T = ([\deE.+-]+)');pressure=value(r'min\(all\) of p = ([\deE.+-]+)')
 if clock and all(x is not None for x in (u,temp,pressure)):
  diagnostics.append(dict(counter=counter,max_U_m_s=u,min_T_K=temp,min_p_Pa=pressure))
physical=m['time_counter_is_physical_seconds'];target=m.get('target_physical_time_s',m.get('target_steady_iterations'))
out=dict(case=case.name,counter_kind=m.get('counter_kind','physical_seconds' if physical else 'steady_iterations'),completed_log_blocks=len(completed),last_completed_counter=completed[-1]['counter'] if completed else None,target_counter=target,last_clock_s=completed[-1]['clock_s'] if completed else None,diagnostics=diagnostics[-1] if diagnostics else None,physical_loads_accepted=False,live_process_confirmed_by_this_script=False)
if diagnostics:
 d=diagnostics[-1];out['positive_finite_latest_diagnostics']=all(math.isfinite(d[x]) and d[x]>0 for x in ('min_T_K','min_p_Pa','max_U_m_s'))
 out['Mach_upper_bound_from_same_block_separate_extrema']=d['max_U_m_s']/math.sqrt(m['gamma']*m['R_J_kgK']*d['min_T_K']) if d['min_T_K']>0 else None
 out['Mach_note']='Bound from separate Umax and Tmin; not measured pointwise Mach or critical Mach.'
(case/'progress_audit.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,indent=2))
