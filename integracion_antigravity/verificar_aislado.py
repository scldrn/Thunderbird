#!/usr/bin/env python3
"""Pruebas del aislamiento y la vigilancia del coordinador local."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import orquestar_aislado as isolated


class IsolatedTest(unittest.TestCase):
    def test_red_y_salida_del_sandbox_denegadas(self):
        policy = isolated.settings_for(Path("/private/tmp/ejemplo"))
        rules = policy["permissions"]["deny"]
        self.assertIn("read_url(*)", rules)
        self.assertIn("unsandboxed(*)", rules)
        self.assertIn("command(docker)", rules)
        self.assertFalse(policy["allowNonWorkspaceAccess"])

    def test_rechaza_entrada_fuera_del_proyecto(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                isolated.prepare_task({"id": "prueba", "entradas": ["../externo"]}, Path(directory))

    def test_detecta_entrada_anadida_o_modificada(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            input_root = workspace / "entradas"
            input_root.mkdir()
            original = input_root / "dato.txt"
            original.write_text("original")
            hashes = {"dato.txt": isolated.digest(original)}
            self.assertEqual(isolated.verify_inputs(workspace, hashes), [])
            (input_root / "extra.txt").write_text("añadido")
            original.write_text("cambiado")
            changes = isolated.verify_inputs(workspace, hashes)
            self.assertIn("dato.txt", changes)
            self.assertIn("Añadido: extra.txt", changes)

    def test_detiene_proceso_tras_permiso_denegado(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "no_debe_crearse"
            event = {"event": "step_update", "step_update": {"step_type": "tool", "state": "ERROR",
                     "tool_info": {"error": {"message": "permission check failed: Permission denied for command"}}}}
            script = ("import json, pathlib, sys, time\n"
                      "print(sys.argv[1], flush=True)\n"
                      "time.sleep(2)\n"
                      "pathlib.Path(sys.argv[2]).write_text('fallo')\n")
            process = subprocess.Popen([sys.executable, "-u", "-c", script, json.dumps(event), str(marker)],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            stdout, _, reason = isolated.monitor_process(process, 5)
            self.assertIn("permiso denegado", reason)
            self.assertIn("Permission denied", stdout)
            self.assertFalse(marker.exists())

    def test_denegacion_de_senal_preserva_eventos_y_no_reintenta(self):
        event = {"event": "step_update", "step_update": {"step_type": "tool", "state": "ERROR",
                 "tool_info": {"error": {"message": "permission check failed"}}}}
        script = "import sys,time; print(sys.argv[1],flush=True); time.sleep(.15)"
        process = subprocess.Popen([sys.executable, "-u", "-c", script, json.dumps(event)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        with patch.object(isolated.common, "signal_process_group", side_effect=PermissionError("denegada")) as send:
            stdout, _, reason = isolated.monitor_process(process, 5)
        self.assertIn("permission check failed", stdout)
        self.assertIn("interrupción no confirmada", reason)
        self.assertEqual(send.call_count, 1)

    def test_detecta_denegacion_en_salida_de_comando(self):
        event = {"event": "step_update", "step_update": {"step_type": "tool", "state": "DONE",
                 "tool_name": "run_command", "tool_info": {"output":
                 "Command exited with code 126.\nzsh: permission denied: archivo"}}}
        script = "import sys,time; print(sys.argv[1],flush=True); time.sleep(2)"
        process = subprocess.Popen([sys.executable, "-u", "-c", script, json.dumps(event)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        stdout, _, reason = isolated.monitor_process(process, 5)
        self.assertIn("permission denied", stdout)
        self.assertIn("permiso denegado", reason)

    def test_espera_salida_normal_tras_cierre_de_tuberias(self):
        script = "import sys,time; sys.stdout.close(); sys.stderr.close(); time.sleep(.15)"
        process = subprocess.Popen([sys.executable, "-u", "-c", script], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        with patch.object(isolated.common, "signal_process_group", side_effect=PermissionError("denegada")) as send:
            _, _, reason = isolated.monitor_process(process, 5)
        self.assertIsNone(reason)
        self.assertEqual(process.returncode, 0)
        send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
