"""Bounded compressible startup pilot after strict mesh audit; no restarts."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
DOCKER = '/Users/sam/.docker/bin/docker'


def run(*args, check=True, **kwargs):
    return subprocess.run([DOCKER, *args], text=True, check=check, **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--container', required=True)
    parser.add_argument('--guard-near-vacuum', action='store_true')
    args = parser.parse_args()
    case, container = args.case.resolve(), args.container
    state_file = case/'EJECUCION.json'
    assert not state_file.exists(), 'Inspect existing execution; do not duplicate'
    mesh = json.loads((case/'MALLA_OPENFOAM.json').read_text())
    assert mesh['checkMesh_OK']
    inputs = json.loads((case/'ENTRADAS.json').read_text())
    start_counter = int(inputs.get('iteration_start', 0))
    for rel, digest in inputs['input_sha256'].items():
        assert hashlib.sha256((case/rel).read_bytes()).hexdigest() == digest, rel
    recorded = json.loads((case/'CONTENEDOR.json').read_text())
    actual = json.loads(run('inspect', container, capture_output=True).stdout)[0]
    assert actual['Id'] == recorded['container_id']
    assert actual['State']['Running'] and not actual['State']['Paused']
    assert run('exec', container, 'test', '-f', '/case/log.foamRun', check=False).returncode == 1
    state = dict(container=container, container_id=actual['Id'], image_id=actual['Image'],
                 stage='preflight_running', started_UTC=datetime.now(timezone.utc).isoformat(),
                 iteration_target=inputs['iteration_target'], counter_is_physical_time=False,
                 historical_solvers_resumed=False, physical_validation_accepted=False)
    def save():
        state_file.write_text(json.dumps(state, indent=2)+'\n')
    save()
    # Initial field evaluation constructs the actual thermophysical/turbulence
    # models. It is not an iteration or convergence test.
    pre = run('exec', '--workdir', '/case', container, '/bin/bash', '-c',
              f'source /opt/openfoam13/etc/bashrc && foamPostProcess -solver fluid -time {start_counter} > log.preflight 2>&1', check=False)
    run('cp', container+':/case/log.preflight', str(case/'log.preflight'))
    state['preflight_exit_code'] = pre.returncode
    log = (case/'log.preflight').read_text()
    if pre.returncode != 0 or 'FOAM FATAL' in log:
        state['stage'] = 'preflight_failed_no_solver'
        run('stop', container, capture_output=True)
        save()
        raise RuntimeError('Inspect preserved preflight failure; no automatic retry')
    # Keep initial-state function output separate from the flow solve.
    if run('exec', container, 'test', '-d', '/case/postProcessing', check=False).returncode == 0:
        (case/'postProcessing_preflight').mkdir()
        run('cp', container+':/case/postProcessing/.', str(case/'postProcessing_preflight'))
        run('exec', container, 'mv', '/case/postProcessing', '/case/postProcessing_preflight')
    state.update(stage='solver_running', preflight_models_constructed=True)
    save()
    start = time.monotonic()
    command = [DOCKER,'exec','--workdir','/case',container,'/bin/bash','-c',
               'source /opt/openfoam13/etc/bashrc && foamRun > log.foamRun 2>&1']
    process = subprocess.Popen(command,text=True)
    state['near_vacuum_guard_enabled'] = args.guard_near_vacuum
    state['near_vacuum_guard_triggered'] = False
    guard_requested_mono = None
    save()
    while process.poll() is None:
        time.sleep(5)
        if args.guard_near_vacuum and not state['near_vacuum_guard_triggered']:
            observed = run('exec',container,'tail','-n','150','/case/log.foamRun',check=False,capture_output=True)
            if observed.returncode == 0:
                pv = re.findall(r'min\(all\) of p = ([\deE.+-]+)',observed.stdout)
                rv = re.findall(r'min\(all\) of rho = ([\deE.+-]+)',observed.stdout)
                bad_p = bool(pv and float(pv[-1]) < .05*inputs['p_Pa'])
                bad_rho = bool(rv and float(rv[-1]) < .05*inputs['rho_kg_m3'])
                nonfinite = bool(re.search(r'(?:residual\s*=|of\s+(?:U|p|T|rho)\s*=)\s*[-+]?(?:nan|inf)\b',observed.stdout,re.I))
                if bad_p or bad_rho or nonfinite:
                    run('exec',container,'sed','-i','s/stopAt endTime;/stopAt writeNow;/', '/case/system/controlDict')
                    run('cp',container+':/case/system/controlDict',str(case/'controlDict_guard_requested'))
                    state.update(near_vacuum_guard_triggered=True,
                        guard_stop_request_UTC=datetime.now(timezone.utc).isoformat(),
                        guard_observed_min_p_Pa=float(pv[-1]) if pv else None,
                        guard_observed_min_rho_kg_m3=float(rv[-1]) if rv else None,
                        guard_nonfinite_detected=nonfinite,
                        guard_action='Requested stopAt writeNow; original host input unchanged, actual control snapshot preserved')
                    guard_requested_mono = time.monotonic()
                    if nonfinite:
                        killed = run('exec',container,'pkill','-TERM','-x','foamRun',check=False,capture_output=True)
                        state.update(guard_SIGTERM_requested=True,guard_SIGTERM_exit_code=killed.returncode,
                                     guard_action='Nonfinite solver state: requested SIGTERM for this container foamRun only; preserve logs')
                    save()
        if guard_requested_mono is not None and process.poll() is None:
            elapsed_guard = time.monotonic()-guard_requested_mono
            if elapsed_guard > 30 and not state.get('guard_SIGTERM_requested'):
                killed = run('exec',container,'pkill','-TERM','-x','foamRun',check=False,capture_output=True)
                state.update(guard_SIGTERM_requested=True,guard_SIGTERM_exit_code=killed.returncode,
                             guard_action='No timely response to writeNow: requested SIGTERM for this container foamRun only')
                save()
            if elapsed_guard > 60 and not state.get('guard_SIGKILL_requested'):
                killed = run('exec',container,'pkill','-KILL','-x','foamRun',check=False,capture_output=True)
                state.update(guard_SIGKILL_requested=True,guard_SIGKILL_exit_code=killed.returncode,
                             guard_action='Solver unresponsive to SIGTERM: requested SIGKILL for this container foamRun only')
                save()
    exit_code = process.wait()
    state.update(stage='solver_exited', exit_code=exit_code, elapsed_wall_s=time.monotonic()-start)
    save()
    run('cp', container+':/case/log.foamRun', str(case/'log.foamRun'))
    log = (case/'log.foamRun').read_text()
    done = [float(re.match(r'([\deE.+-]+)', block)[1]) for block in re.split(r'\nTime = ', log)[1:]
            if re.match(r'([\deE.+-]+)', block) and 'ClockTime =' in block]
    state['last_completed_counter'] = done[-1] if done else None
    state['target_reached'] = bool(done and done[-1] == inputs['iteration_target'])
    state['copied_output_directories'] = []
    names = ['postProcessing', str(inputs['iteration_target']-20), str(inputs['iteration_target'])]
    if done:
        names.append(f'{done[-1]:g}')
    for name in dict.fromkeys(names):
        if run('exec', container, 'test', '-d', '/case/'+name, check=False).returncode == 0:
            (case/name).mkdir(exist_ok=True)
            run('cp', container+':/case/'+name+'/.', str(case/name))
            state['copied_output_directories'].append(name)
    state['container_oom_killed'] = json.loads(run('inspect', container, capture_output=True).stdout)[0]['State']['OOMKilled']
    run('stop', container, capture_output=True)
    state.update(container_stopped_after_solver=True, finished_UTC=datetime.now(timezone.utc).isoformat())
    save()
    print(json.dumps(state, indent=2))
    assert exit_code == 0, 'Preserve terminal failure and diagnose'


if __name__ == '__main__':
    main()
