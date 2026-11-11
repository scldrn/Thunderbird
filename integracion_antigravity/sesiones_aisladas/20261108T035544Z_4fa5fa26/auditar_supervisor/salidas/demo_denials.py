#!/usr/bin/env python3
"""Prueba demostrativa de fallos en detección de denegaciones."""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "entradas" / "investigacion-aeronautica" / "integracion_antigravity"))
import orquestar_aislado as isolated

def test_denial_detection_shortcomings():
    # Caso 1: Mensaje de error estándar "Permission denied" (sin "check failed")
    # El supervisor NO lo detecta como denegación y NO detiene la sesión
    with tempfile.TemporaryDirectory() as directory:
        marker = Path(directory) / "archivo_creado"
        event = {
            "event": "step_update",
            "step_update": {
                "step_type": "tool",
                "state": "ERROR",
                "tool_info": {
                    "error": {"message": "Permission denied: /workspace/entradas/archivo.txt"}
                }
            }
        }
        # Script que emite el evento, espera 1 segundo y crea el marcador
        # Si monitor_process funcionara adecuadamente ante denegación, mataría el proceso antes de crear el marcador
        script = (
            "import json, pathlib, sys, time\n"
            "print(sys.argv[1], flush=True)\n"
            "time.sleep(0.5)\n"
            "pathlib.Path(sys.argv[2]).write_text('creado tras denegacion')\n"
        )
        proc = subprocess.Popen(
            [sys.executable, "-u", "-c", script, json.dumps(event), str(marker)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True
        )
        stdout, stderr, reason = isolated.monitor_process(proc, 5)
        print("Caso 1 - Reason:", reason)
        print("Caso 1 - Marker exists?:", marker.exists())
        # Demostrado: reason es None, y el proceso siguió ejecutándose y creó el marcador!
        assert reason is None, f"Se esperaba None pero fue {reason}"
        assert marker.exists(), "El marcador debería haberse creado porque monitor_process ignoró la denegación"

    # Caso 2: El error está en step["error"] en lugar de step["tool_info"]["error"]
    with tempfile.TemporaryDirectory() as directory:
        marker2 = Path(directory) / "archivo_creado_caso2"
        event2 = {
            "event": "step_update",
            "step_update": {
                "step_type": "tool",
                "state": "ERROR",
                "error": {"message": "permission check failed: rule triggered"}
            }
        }
        proc2 = subprocess.Popen(
            [sys.executable, "-u", "-c", script, json.dumps(event2), str(marker2)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True
        )
        stdout2, stderr2, reason2 = isolated.monitor_process(proc2, 5)
        print("Caso 2 - Reason:", reason2)
        print("Caso 2 - Marker2 exists?:", marker2.exists())
        assert reason2 is None
        assert marker2.exists()

    # Caso 3: Estado "DENIED" o "BLOCKED" en lugar de "ERROR"
    with tempfile.TemporaryDirectory() as directory:
        marker3 = Path(directory) / "archivo_creado_caso3"
        event3 = {
            "event": "step_update",
            "step_update": {
                "step_type": "tool",
                "state": "DENIED",
                "tool_info": {
                    "error": {"message": "permission check failed"}
                }
            }
        }
        proc3 = subprocess.Popen(
            [sys.executable, "-u", "-c", script, json.dumps(event3), str(marker3)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True
        )
        stdout3, stderr3, reason3 = isolated.monitor_process(proc3, 5)
        print("Caso 3 - Reason:", reason3)
        print("Caso 3 - Marker3 exists?:", marker3.exists())
        assert reason3 is None
        assert marker3.exists()

    print("DEMOSTRACIÓN EXITOSA: monitor_process ignora denegaciones por formatos comunes y variantes de estado.")

if __name__ == "__main__":
    test_denial_detection_shortcomings()
