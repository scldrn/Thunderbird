#!/usr/bin/env python3
"""Prueba demostrativa de cuelgue de tubería (pipe) cuando un subproceso hijo mantiene stdout abierto."""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Añadir entradas al path para importar orquestar_aislado
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "entradas" / "investigacion-aeronautica" / "integracion_antigravity"))
import orquestar_aislado as isolated

def test_pipe_hang_demonstration():
    # Proceso que emite resultado, spawnea un hijo que retiene stdout/stderr por 4s, y el proceso padre termina de inmediato (0.1s)
    script = (
        "import subprocess, sys, time, json\n"
        "event = {'event': 'result', 'result': {'status': 'SUCCESS'}}\n"
        "print(json.dumps(event), flush=True)\n"
        "# Hijo en background retiene pipes\n"
        "sub = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(3)'], stdout=None, stderr=None)\n"
        "sys.exit(0)\n"
    )
    start = time.monotonic()
    proc = subprocess.Popen(
        [sys.executable, "-u", "-c", script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True
    )
    # Ejecutamos monitor_process con timeout de 2 segundos
    stdout, stderr, reason = isolated.monitor_process(proc, timeout_s=2)
    elapsed = time.monotonic() - start
    print(f"Elapsed: {elapsed:.2f}s, Returncode: {proc.returncode}, Reason: {reason}")
    # El proceso principal terminó casi instantáneamente, pero monitor_process se colgó hasta el timeout (2s + SIGTERM + SIGKILL)
    assert reason == "Tiempo de espera agotado.", f"Esperado timeout pero fue: {reason}"
    assert elapsed >= 2.0, f"Debería haber tardado al menos el timeout: {elapsed}"
    print("DEMOSTRACIÓN EXITOSA: monitor_process se cuelga por descriptor heredado a pesar de que el proceso principal ya finalizó.")

if __name__ == "__main__":
    test_pipe_hang_demonstration()
