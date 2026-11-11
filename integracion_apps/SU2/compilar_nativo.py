"""Build only official SU2_CFD, native ARM64, entirely within the workspace."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
SOURCE = Path(json.loads((HERE/'FUENTE_VERIFICADA.json').read_text())['source_dir'])


def main():
    status = HERE/'COMPILACION_NATIVA.json'
    assert not status.exists(), 'Inspect existing build/process rather than duplicate'
    assert (SOURCE/'externals/eigen/Eigen/Core').exists()
    state = dict(stage='native_build_preparing',source_dir=str(SOURCE),version='8.6.0',
        started_UTC=datetime.now(timezone.utc).isoformat(),architecture_target='arm64',
        global_system_settings_changed=False,compiler_jobs=2,flow_solver_executed=False)
    def save():
        status.write_text(json.dumps(state,indent=2)+'\n')
    save()
    env = os.environ.copy()
    env['NINJA'] = str(SOURCE/'ninja')
    # Trust the installed CA bundle; do not disable TLS verification.
    try:
        import certifi
        env['SSL_CERT_FILE'] = certifi.where()
    except ImportError:
        pass
    def command(args, logname, stage):
        state.update(stage=stage,command=args)
        save()
        start=time.monotonic()
        with (HERE/logname).open('w') as log:
            p=subprocess.Popen(args,cwd=SOURCE,env=env,stdout=log,stderr=subprocess.STDOUT,text=True)
            state['active_pid']=p.pid
            save()
            code=p.wait()
        state.update(last_exit_code=code,last_stage_wall_s=time.monotonic()-start)
        save()
        if code:
            state['stage']='failed_'+stage
            save()
            raise RuntimeError(f'Build step failed; inspect {logname}, no automatic retry')
    # An archive nested in this workspace is misdetected as a git checkout by
    # upstream auto-detection. Select its documented URL path explicitly.
    preconfigure_code = ('import sys; from pathlib import Path; sys.path[0]='+repr(str(SOURCE))+'; '
        'import preconfigure; preconfigure.init_submodules(method="url", own_meson=True, '
        'own_codi=False, own_medi=False, own_opdi=False, own_mpp=False, own_cool=False, '
        'own_cantera=False, own_mel=True, own_fado=False, own_mlpcpp=False, own_eigen=False); '
        'preconfigure.build_ninja(); Path("su2preconfig.timestamp").touch()')
    command([sys.executable,'-c',preconfigure_code],
            'preconfigure-native.log','preconfigure_running')
    options=['setup','build-native-r2','--buildtype=release','--prefix='+str(HERE/'native-v8.6.0'),
        '-Dwith-mpi=disabled','-Dwith-omp=false','-Denable-autodiff=false','-Denable-directdiff=false',
        '-Denable-pywrapper=false','-Denable-cgns=false','-Denable-tecio=false',
        '-Denable-mixedprec=false','-Denable-singleprec=false']
    command([sys.executable,'externals/meson/meson.py',*options], 'meson-native.log','configure_running')
    command([str(SOURCE/'ninja'),'-C','build-native-r2','-j2','SU2_CFD/src/SU2_CFD'],
            'ninja-native.log','compilation_running')
    binary=SOURCE/'build-native-r2/SU2_CFD/src/SU2_CFD'
    assert binary.is_file()
    state.update(stage='compiled_not_yet_flow_verified',binary=str(binary),
        binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
        file_description=subprocess.run(['file',str(binary)],capture_output=True,text=True,check=True).stdout.strip(),
        finished_UTC=datetime.now(timezone.utc).isoformat())
    state.pop('active_pid',None)
    save()
    print(json.dumps(state,indent=2))


if __name__ == '__main__':
    main()
