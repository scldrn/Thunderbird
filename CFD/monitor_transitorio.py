"""Read an actual transient log; progress data does not prove a live process."""
from pathlib import Path
import argparse,json,re
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--case',default='transitorio_X35_Y-35_h0.006');args=parser.parse_args()
case=(ROOT/args.case).resolve();text=(case/'log.foamRun').read_text();chunks=re.split(r'\nTime = ',text);records=[]
for chunk in chunks[1:]:
 m=re.match(r'([\d.eE+-]+)',chunk)
 if not m:continue
 time=float(m[1]);clock=re.search(r'ClockTime = ([\d.eE+-]+)',chunk)
 if clock:records.append((time,float(clock[1])))
co=[float(x) for x in re.findall(r'Courant Number mean: [\deE.+-]+ max: ([\deE.+-]+)',text)]
dt=[float(x) for x in re.findall(r'deltaT = ([\deE.+-]+)',text)]
continuity=[float(x) for x in re.findall(r'time step continuity errors : sum local = [\deE.+-]+, global = ([\deE.+-]+)',text)]
max_velocity=[float(x) for x in re.findall(r'maxMag\(all\) of U = ([\deE.+-]+)',text)]
min_k=[float(x) for x in re.findall(r'min\(all\) of k = ([\deE.+-]+)',text)]
meta=json.loads((case/'transient_assumptions.json').read_text());result=dict(completed_logged_steps=len(records),last_completed_physical_time_s=records[-1][0] if records else 0,clock_time_s_last=records[-1][1] if records else 0,target_physical_time_s=meta['end_time_s'],elapsed_flow_through_times=(records[-1][0]/meta['flow_through_time_s']) if records else 0,latest_deltaT_s=dt[-1] if dt else None,initial_to_latest_dt_ratio=dt[0]/dt[-1] if dt and dt[-1]>0 else None,dt_collapsed_by_factor_1000=bool(dt and dt[-1]<dt[0]/1000),max_reported_Courant=max(co) if co else None,latest_reported_Courant=co[-1] if co else None,max_abs_global_continuity_error_last_100_corrections=max(map(abs,continuity[-100:])) if continuity else None,mean_loads_ready=False,note='Progress audit only. Check the live exec handle and docker top/ps for running state. A collapsed timestep flags numerical pathology despite small continuity errors. Completion requires physical-time span, force statistics and sensitivity audits.')
result.update(latest_reported_max_velocity_ms=max_velocity[-1] if max_velocity else None,max_reported_velocity_ms=max(max_velocity) if max_velocity else None,latest_reported_min_k=min_k[-1] if min_k else None,initial_field_physical_age_s=meta.get('initial_physical_age_s',0),source_age_plus_restart_time_s=meta.get('initial_physical_age_s',0)+(records[-1][0] if records else 0))
(case/'progress_audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
