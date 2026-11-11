#!/usr/bin/env python3
"""Prueba demostrativa de fallos en el aislamiento de entradas/."""

import os
import shutil
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "entradas" / "investigacion-aeronautica" / "integracion_antigravity"))
import orquestar_aislado as isolated

def test_isolation_and_entradas_vulnerabilities():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        task = {
            "id": "tarea_test",
            "instruccion": "prueba",
            "entradas": []
        }
        workspace, originals = isolated.prepare_task(task, temp_root)
        input_root = workspace / "entradas"
        
        # 1. Demostración: La carpeta entradas/ es escribible
        new_file = input_root / "archivo_no_autorizado.txt"
        new_file.write_text("inyeccion de datos")
        assert new_file.exists(), "Se pudo crear un archivo dentro de entradas/"
        
        # 2. Demostración: run_one no detecta archivos nuevos en entradas/
        # Simulamos la verificación de entradas de run_one:
        changes = []
        for relative, original_hash in originals.items():
            path = workspace / "entradas" / relative
            if not path.is_file() or isolated.digest(path) != original_hash:
                changes.append(relative)
        
        print("Cambios detectados según lógica del coordinador:", changes)
        assert len(changes) == 0, "El coordinador reporta 0 cambios a pesar del nuevo archivo en entradas/"
        
        # 3. Demostración: Se puede borrar un archivo de solo lectura porque el directorio padre es escribible
        ro_file = input_root / "archivo_ro.txt"
        ro_file.write_text("contenido original")
        ro_file.chmod(0o444)
        # El archivo es de solo lectura (0o444)
        assert oct(ro_file.stat().st_mode)[-3:] == "444"
        # Pero podemos borrarlo porque el directorio tiene permisos de escritura:
        os.unlink(ro_file)
        assert not ro_file.exists(), "Se pudo eliminar el archivo de solo lectura"
        
    print("DEMOSTRACIÓN EXITOSA: entradas/ permite creación y borrado de archivos por permisos en el directorio, y el coordinador no detecta archivos añadidos.")

if __name__ == "__main__":
    test_isolation_and_entradas_vulnerabilities()
