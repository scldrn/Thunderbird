#!/usr/bin/env python3
"""Prueba demostrativa de condición de carrera en cancelación y ProcessRegistry."""

import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "entradas" / "investigacion-aeronautica" / "integracion_antigravity"))
import orquestar as common
import orquestar_aislado as isolated

def test_cancellation_race_condition():
    registry = common.ProcessRegistry()
    registry.cancel()  # Marcamos cancelado como si hubiera ocurrido un KeyboardInterrupt
    
    # Proceso que ignora SIGTERM (simula un proceso con máscara de señales o manejador de cleanup)
    script = (
        "import signal, sys, time\n"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        "print('ignoring_sigterm', flush=True)\n"
        "time.sleep(10)\n"
        "sys.exit(0)\n"
    )
    proc = subprocess.Popen(
        [sys.executable, "-u", "-c", script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True
    )
    # Esperamos a que el proceso haya instalado el manejador
    line = proc.stdout.readline()
    assert b"ignoring_sigterm" in line
    
    # Se agrega al registry que ya está cancelado
    registry.add("tarea_tardia", proc)
    
    # 1. El proceso NO está en registry.processes
    assert "tarea_tardia" not in registry.processes, "No debió agregarse al diccionario"
    
    # 2. El proceso sigue vivo a pesar de que registry.cancel() ya ocurrió
    time.sleep(0.2)
    assert proc.poll() is None, "El proceso sigue vivo porque solo recibió un SIGTERM que ignoró"
    
    # 3. Si se llama a registry.cancel() de nuevo, ¡sigue sin matar al proceso porque no está registrado!
    registry.cancel()
    time.sleep(0.1)
    assert proc.poll() is None, "El proceso sigue sin morir porque cancel() no lo conoce"
    
    # Limpiamos nosotros el proceso de prueba
    common.signal_process_group(proc, signal.SIGKILL)
    proc.wait()
    print("DEMOSTRACIÓN EXITOSA: ProcessRegistry.add no escala a SIGKILL ni retiene procesos cancelados tardíos, dejándolos huérfanos.")

if __name__ == "__main__":
    test_cancellation_race_condition()
