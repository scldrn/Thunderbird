#!/usr/bin/env python3
"""Comprobaciones locales del coordinador con un ejecutable simulado."""

import json
from pathlib import Path
import tempfile
import threading
import time
import unittest

import orquestar


class OrquestadorTest(unittest.TestCase):
    def test_rechaza_identificadores_duplicados(self):
        with self.assertRaises(ValueError):
            orquestar.validate_tasks({"tareas": [
                {"id": "a", "instruccion": "uno"},
                {"id": "a", "instruccion": "dos"},
            ]})

    def test_rechaza_ruta_como_identificador(self):
        with self.assertRaises(ValueError):
            orquestar.validate_tasks({"tareas": [
                {"id": "../salida", "instruccion": "uno"},
            ]})

    def test_procesa_exito_y_error_en_paralelo(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake = root / "agy-falso"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys, time\n"
                "time.sleep(0.15)\n"
                "error = 'FALLAR' in sys.argv[2]\n"
                "if 'AVISO' in sys.argv[2]:\n"
                "    print(json.dumps({'event':'step_update','step_update':{'step_type':'tool','state':'ERROR','tool_name':'fake','tool_info':{'error':{'message':'denegado'}}}}))\n"
                "print(json.dumps({'event':'result','result':{'status': 'ERROR' if error else 'SUCCESS', "
                "'response': 'ok', 'conversation_id': 'test'}}))\n"
                "sys.exit(1 if error else 0)\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)
            tasks = [
                {"id": "ok", "instruccion": "hola"},
                {"id": "error", "instruccion": "FALLAR"},
                {"id": "aviso", "instruccion": "AVISO"},
            ]
            results = orquestar.run_batch(tasks, root, 10, 2, root / "salida", fake)
            by_id = {item["tarea"]: item for item in results}
            self.assertTrue(by_id["ok"]["exito_tecnico"])
            self.assertFalse(by_id["error"]["exito_tecnico"])
            self.assertTrue(by_id["aviso"]["exito_tecnico"])
            self.assertTrue(by_id["aviso"]["requiere_revision"])
            self.assertEqual(len(by_id["aviso"]["errores_herramientas"]), 1)
            self.assertLess(by_id["ok"]["inicio_utc"], by_id["error"]["fin_utc"])
            self.assertLess(by_id["error"]["inicio_utc"], by_id["ok"]["fin_utc"])
            self.assertEqual(json.loads((root / "salida/ok.json").read_text())["tarea"], "ok")
            self.assertEqual(json.loads((root / "salida/RESUMEN.json").read_text())["estado"], "completado")

    def test_detecta_flujo_truncado(self):
        events, errors, parse_errors, result = orquestar.parse_stream('{"event":"init"}\n{')
        self.assertEqual(len(events), 1)
        self.assertFalse(errors)
        self.assertTrue(parse_errors)
        self.assertIsNone(result)

    def test_detecta_comando_que_termina_con_error(self):
        stream = json.dumps({"event": "step_update", "step_update": {
            "step_type": "tool", "state": "DONE", "tool_name": "run_command",
            "tool_info": {"output": "Command exited with code 128.\nfalló"}}})
        stream += "\n" + json.dumps({"event": "result", "result": {"status": "SUCCESS"}})
        _, errors, parse_errors, result = orquestar.parse_stream(stream)
        self.assertFalse(parse_errors)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(errors[0]["codigo_salida"], 128)

    def test_cancelacion_detiene_un_proceso_propio(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake = root / "agy-lento"
            fake.write_text("#!/usr/bin/env python3\nimport time\ntime.sleep(30)\n", encoding="utf-8")
            fake.chmod(0o755)
            registry = orquestar.ProcessRegistry()
            holder = []
            thread = threading.Thread(target=lambda: holder.append(orquestar.execute_task(
                {"id": "lento", "instruccion": "prueba"}, root, 10, fake, registry)))
            thread.start()
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                with registry.lock:
                    if registry.processes:
                        break
                time.sleep(0.01)
            registry.cancel()
            thread.join(timeout=5)
            self.assertFalse(thread.is_alive())
            self.assertFalse(holder[0]["exito_tecnico"])


if __name__ == "__main__":
    unittest.main()
