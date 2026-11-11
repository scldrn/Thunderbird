"""Run only after native SU2 build completion; preserve all terminal failures."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CASE = HERE/'su2_r1_oficial'
TOOLS = ROOT/'integracion_apps/SU2'


def main():
    global CASE
    parser=argparse.ArgumentParser()
    parser.add_argument('--case',type=Path,default=CASE)
    CASE=parser.parse_args().case.resolve()
    state_file = CASE/'EJECUCION.json'
    assert not state_file.exists(), 'Inspect existing native solver, do not duplicate'
    build = json.loads((TOOLS/'COMPILACION_NATIVA.json').read_text())
    assert build['stage'] == 'compiled_not_yet_flow_verified'
    binary = Path(build['binary'])
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == build['binary_sha256']
    assert 'arm64' in build['file_description']
    inputs = json.loads((CASE/'ENTRADAS.json').read_text())
    for path,digest in inputs['inputs_sha256'].items():
        assert hashlib.sha256((CASE/path).read_bytes()).hexdigest() == digest
    state=dict(stage='solver_starting',binary=str(binary),binary_sha256=build['binary_sha256'],
        iteration_limit=inputs['iteration_limit'],wall_time_limit_s=900,
        counter_is_physical_time=False,physical_validation_accepted=False,
        started_UTC=datetime.now(timezone.utc).isoformat(),historical_solvers_resumed=False)
    def save():
        state_file.write_text(json.dumps(state,indent=2)+'\n')
    save()
    start=time.monotonic()
    with (CASE/'log.SU2_CFD').open('w') as log:
        process=subprocess.Popen([str(binary),'case.cfg'],cwd=CASE,stdout=log,stderr=subprocess.STDOUT,text=True)
        state.update(stage='solver_running',native_pid=process.pid)
        save()
        try:
            code=process.wait(timeout=state['wall_time_limit_s'])
        except subprocess.TimeoutExpired:
            process.terminate()
            state['wall_time_guard_triggered']=True
            try:
                code=process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.kill();code=process.wait()
                state['unresponsive_solver_killed']=True
    state.update(stage='solver_exited',exit_code=code,elapsed_wall_s=time.monotonic()-start,
        finished_UTC=datetime.now(timezone.utc).isoformat(),
        output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CASE.iterdir()
                       if p.is_file() and p.name not in ('EJECUCION.json','ENTRADAS.json')})
    save()
    print(json.dumps({k:v for k,v in state.items() if k!='output_sha256'},indent=2))
    assert code == 0, 'Preserve terminal native solver failure and inspect log'


if __name__ == '__main__':
    main()
