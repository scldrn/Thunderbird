#!/usr/bin/env python3
"""Prueba demostrativa de falsos positivos en detección de patrones inseguros."""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "entradas" / "investigacion-aeronautica" / "integracion_antigravity"))
import orquestar_aislado as isolated

def test_unsafe_false_positive():
    # Una herramienta legítima de auditoría busca si existe verify=False en un repositorio:
    # comando: grep -rn "verify=False" .
    event = {
        "event": "step_update",
        "step_update": {
            "step_type": "tool",
            "state": "ACTIVE",
            "tool_info": {
                "tool_name": "run_command",
                "parameters": {
                    "CommandLine": 'grep -rn "verify=False" .'
                }
            }
        }
    }
    script = (
        "import json, sys, time\n"
        "print(sys.argv[1], flush=True)\n"
        "time.sleep(2)\n"
        "print('terminado con exito', flush=True)\n"
    )
    proc = subprocess.Popen(
        [sys.executable, "-u", "-c", script, json.dumps(event)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True
    )
    stdout, stderr, reason = isolated.monitor_process(proc, 5)
    print("False Positive Reason:", reason)
    # Demostrado: La sesión es detenida violentamente ante un comando legítimo de búsqueda!
    assert "desactivación de certificados" in reason
    assert "terminado con exito" not in stdout
    print("DEMOSTRACIÓN EXITOSA: monitor_process mata procesos legítimos de auditoría por falso positivo en unsafe_pattern.")

if __name__ == "__main__":
    test_unsafe_false_positive()
