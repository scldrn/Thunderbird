#!/usr/bin/env python3
"""
test_verificar_manifiesto.py
----------------------------
Batería de pruebas unitarias automatizadas con unittest (Python estándar)
para verificar la integridad criptográfica y comprobar la detección infalible
de cambios de contenido (manipulación de datos, cambios de tamaño, sustituciones,
y archivos faltantes), además de las políticas de integridad metodológica.

Uso:
    python3 salidas/test_verificar_manifiesto.py
    python3 -m unittest salidas/test_verificar_manifiesto.py -v
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Asegurar que el directorio de salidas/ esté en sys.path para importar verificar_manifiesto
salidas_dir = str(Path(__file__).resolve().parent)
if salidas_dir not in sys.path:
    sys.path.insert(0, salidas_dir)

# Importar funciones directamente desde el módulo de verificación
from verificar_manifiesto import (
    calcular_sha256,
    obtener_tamano_bytes,
    verificar_archivo,
    verificar_manifiesto,
)


class TestVerificacionIntegridadFuentes(unittest.TestCase):
    """Pruebas sobre los archivos originales de referencia en entradas/."""

    @classmethod
    def setUpClass(cls):
        cls.ruta_raiz = Path(__file__).resolve().parent.parent
        cls.ruta_manifiesto = cls.ruta_raiz / "salidas" / "manifiesto_fuentes.json"

        with open(cls.ruta_manifiesto, "r", encoding="utf-8") as f:
            cls.manifiesto = json.load(f)

    def test_manifiesto_existe_y_es_valido(self):
        """Verifica que el archivo JSON del manifiesto exista y contenga 4 archivos."""
        self.assertTrue(self.ruta_manifiesto.is_file(), "El manifiesto JSON debe existir en salidas/")
        self.assertIn("archivos", self.manifiesto)
        self.assertEqual(len(self.manifiesto["archivos"]), 4, "Debe contener exactamente las 3 tablas UIUC y la nota NASA")

    def test_archivos_reales_pasan_verificacion(self):
        """Verifica que todos los archivos originales en entradas/ pasan con estado OK."""
        codigo_retorno, resultados = verificar_manifiesto(
            self.ruta_manifiesto, self.ruta_raiz, verboso=False
        )
        self.assertEqual(codigo_retorno, 0, "La verificación de los archivos de entrada debe retornar 0")
        for res in resultados:
            self.assertEqual(res["estado"], "OK", f"El archivo {res['nombre']} debe estar OK")
            self.assertIsNotNone(res["tamano_real"])
            self.assertIsNotNone(res["sha256_real"])
            self.assertEqual(res["tamano_real"], res["tamano_esperado"])
            self.assertEqual(res["sha256_real"], res["sha256_esperado"])


class TestReglasIntegridadYMetadatos(unittest.TestCase):
    """Pruebas de cumplimiento de políticas: no inventar datos, licencias ni llamar fuente primaria a la nota."""

    @classmethod
    def setUpClass(cls):
        ruta_raiz = Path(__file__).resolve().parent.parent
        ruta_manifiesto = ruta_raiz / "salidas" / "manifiesto_fuentes.json"
        with open(ruta_manifiesto, "r", encoding="utf-8") as f:
            cls.manifiesto = json.load(f)

    def test_nota_nasa_no_es_fuente_primaria(self):
        """Regla estricta: La nota NASA NO debe ser llamada fuente primaria."""
        archivos = {a["nombre"]: a for a in self.manifiesto["archivos"]}
        self.assertIn("NOTA-NASA-EDF.md", archivos)
        nota = archivos["NOTA-NASA-EDF.md"]

        self.assertFalse(nota["es_fuente_primaria"], "NOTA-NASA-EDF.md no debe ser clasificada como fuente primaria")
        self.assertTrue(nota["es_resumen_derivado"], "NOTA-NASA-EDF.md debe ser identificada como resumen derivado")
        self.assertIsNotNone(nota.get("fuente_primaria_referenciada"), "Debe citar la fuente primaria real (Weinstein et al., 2024)")

    def test_tablas_uiuc_son_primarias(self):
        """Las tablas de datos brutos de UIUC sí son fuentes primarias de datos experimentales/geométricos."""
        archivos = {a["nombre"]: a for a in self.manifiesto["archivos"]}
        for nombre in ["mi_3.2x2.2_geom.txt", "mi_3.2x2.2_static_0519rd.txt", "mi_3.2x2.2_0544rd_20051.txt"]:
            self.assertTrue(archivos[nombre]["es_fuente_primaria"], f"{nombre} debe ser fuente primaria")
            self.assertFalse(archivos[nombre]["es_resumen_derivado"], f"{nombre} no es un resumen derivado")

    def test_no_inventar_licencias_ni_fechas(self):
        """Regla estricta: No inventar licencias ni fechas de descarga."""
        for a in self.manifiesto["archivos"]:
            licencia = a.get("licencia", "").lower()
            fecha = a.get("fecha_descarga", "").lower()
            self.assertIn("no declarada", licencia, f"En {a['nombre']}, la licencia debe constar como no declarada")
            self.assertIn("no registrada", fecha, f"En {a['nombre']}, la fecha de descarga debe constar como no registrada")

    def test_distincion_metodologica_y_unidades_presentes(self):
        """Regla estricta: Distinguir datos medidos, supuestos y cálculos, conservando unidades."""
        for a in self.manifiesto["archivos"]:
            dm = a.get("distincion_metodologica", {})
            self.assertIn("datos_medidos", dm, f"{a['nombre']} debe detallar datos medidos")
            self.assertIn("datos_calculados", dm, f"{a['nombre']} debe detallar datos calculados")
            self.assertIn("supuestos", dm, f"{a['nombre']} debe detallar supuestos")
            self.assertIn("unidades", dm, f"{a['nombre']} debe detallar unidades")
            self.assertTrue(len(dm["unidades"]) > 0, f"{a['nombre']} debe contener diccionario de unidades")

    def test_limites_transferencia_documentados(self):
        """Regla estricta: Debe incluir límites de transferencia explícitos para cada archivo."""
        for a in self.manifiesto["archivos"]:
            lt = a.get("limites_transferencia", {})
            self.assertIn("descripcion", lt, f"{a['nombre']} debe tener descripción de límites de transferencia")
            self.assertIn("restricciones_aplicabilidad", lt, f"{a['nombre']} debe tener lista de restricciones")
            self.assertTrue(len(lt["restricciones_aplicabilidad"]) >= 3, f"{a['nombre']} debe listar al menos 3 restricciones")


class TestDeteccionCambiosContenido(unittest.TestCase):
    """
    Pruebas rigurosas que simulan alteraciones y manipulación de contenido en un entorno aislado,
    usando shutil.copyfile conforme a las instrucciones (para evitar heredar permisos de solo lectura).
    """

    def setUp(self):
        self.ruta_raiz = Path(__file__).resolve().parent.parent
        self.ruta_manifiesto = self.ruta_raiz / "salidas" / "manifiesto_fuentes.json"

        with open(self.ruta_manifiesto, "r", encoding="utf-8") as f:
            self.manifiesto = json.load(f)

        # Crear directorio temporal aislado para pruebas de manipulación
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_temp = Path(self.temp_dir.name)

        # Replicar estructura usando shutil.copyfile (permite escritura)
        for a in self.manifiesto["archivos"]:
            src = self.ruta_raiz / a["ruta_relativa_referencia"]
            dst = self.base_temp / a["ruta_relativa_referencia"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)

        # Copiar manifiesto al directorio temporal
        self.temp_manifest = self.base_temp / "manifiesto_test.json"
        shutil.copyfile(self.ruta_manifiesto, self.temp_manifest)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_verificacion_base_en_copia_limpia_retorna_cero(self):
        """Verifica que la copia prístina en el directorio temporal pasa con 0."""
        codigo, resultados = verificar_manifiesto(self.temp_manifest, self.base_temp)
        self.assertEqual(codigo, 0)
        self.assertTrue(all(r["estado"] == "OK" for r in resultados))

    def test_deteccion_alteracion_byte_en_tabla_geometrica(self):
        """Detecta una alteración de contenido (mismo tamaño exacto, hash alterado) en mi_3.2x2.2_geom.txt."""
        target_file = (
            self.base_temp
            / "entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_geom.txt"
        )
        with open(target_file, "rb") as f:
            data = f.read()

        # Reemplazar 20.359 por 20.360 (exactamente 6 bytes por 6 bytes)
        self.assertIn(b"20.359", data)
        data_alterada = data.replace(b"20.359", b"20.360")
        self.assertEqual(len(data), len(data_alterada), "El tamaño en bytes debe mantenerse exacto")

        with open(target_file, "wb") as f:
            f.write(data_alterada)

        codigo, resultados = verificar_manifiesto(self.temp_manifest, self.base_temp)
        self.assertEqual(codigo, 1, "Debe retornar 1 al detectar discrepancia de hash")
        res_geom = next(r for r in resultados if r["nombre"] == "mi_3.2x2.2_geom.txt")
        self.assertEqual(res_geom["estado"], "DISCREPANCIA_HASH")
        self.assertEqual(res_geom["tamano_real"], res_geom["tamano_esperado"])
        self.assertNotEqual(res_geom["sha256_real"], res_geom["sha256_esperado"])

    def test_deteccion_alteracion_en_tabla_estatica(self):
        """Detecta alteración de RPM (mismo tamaño exacto, hash alterado) en mi_3.2x2.2_static_0519rd.txt."""
        target_file = (
            self.base_temp
            / "entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_static_0519rd.txt"
        )
        with open(target_file, "rb") as f:
            data = f.read()

        # Reemplazar 2950.000 por 2950.001 (exactamente 8 bytes por 8 bytes)
        self.assertIn(b"2950.000", data)
        data_alterada = data.replace(b"2950.000", b"2950.001")
        self.assertEqual(len(data), len(data_alterada))

        with open(target_file, "wb") as f:
            f.write(data_alterada)

        codigo, resultados = verificar_manifiesto(self.temp_manifest, self.base_temp)
        self.assertEqual(codigo, 1)
        res = next(r for r in resultados if r["nombre"] == "mi_3.2x2.2_static_0519rd.txt")
        self.assertEqual(res["estado"], "DISCREPANCIA_HASH")
        self.assertEqual(res["tamano_real"], res["tamano_esperado"])
        self.assertNotEqual(res["sha256_real"], res["sha256_esperado"])

    def test_deteccion_alteracion_en_tabla_dinamica(self):
        """Detecta alteración en coeficiente (mismo tamaño exacto, hash alterado) en mi_3.2x2.2_0544rd_20051.txt."""
        target_file = (
            self.base_temp
            / "entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_0544rd_20051.txt"
        )
        with open(target_file, "rb") as f:
            data = f.read()

        # Reemplazar 0.044195 por 0.044196 (exactamente 8 bytes)
        self.assertIn(b"0.044195", data)
        data_alterada = data.replace(b"0.044195", b"0.044196")
        self.assertEqual(len(data), len(data_alterada))

        with open(target_file, "wb") as f:
            f.write(data_alterada)

        codigo, resultados = verificar_manifiesto(self.temp_manifest, self.base_temp)
        self.assertEqual(codigo, 1)
        res = next(r for r in resultados if r["nombre"] == "mi_3.2x2.2_0544rd_20051.txt")
        self.assertEqual(res["estado"], "DISCREPANCIA_HASH")
        self.assertEqual(res["tamano_real"], res["tamano_esperado"])
        self.assertNotEqual(res["sha256_real"], res["sha256_esperado"])

    def test_deteccion_alteracion_en_nota_nasa(self):
        """Detecta alteración en NOTA-NASA-EDF.md (ej. alterando empuje o potencia)."""
        target_file = (
            self.base_temp
            / "entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md"
        )
        with open(target_file, "r", encoding="utf-8") as f:
            contenido = f.read()

        contenido_alterado = contenido.replace("1.100 g", "1.250 g")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(contenido_alterado)

        codigo, resultados = verificar_manifiesto(self.temp_manifest, self.base_temp)
        self.assertEqual(codigo, 1)
        res = next(r for r in resultados if r["nombre"] == "NOTA-NASA-EDF.md")
        self.assertEqual(res["estado"], "DISCREPANCIA_HASH")

    def test_deteccion_cambio_tamano_por_adicion(self):
        """Detecta adición de bytes extra al final de un archivo."""
        target_file = (
            self.base_temp
            / "entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_geom.txt"
        )
        with open(target_file, "a", encoding="utf-8") as f:
            f.write("\n# Linea espuria no autorizada\n")

        codigo, resultados = verificar_manifiesto(self.temp_manifest, self.base_temp)
        self.assertEqual(codigo, 1)
        res = next(r for r in resultados if r["nombre"] == "mi_3.2x2.2_geom.txt")
        self.assertEqual(res["estado"], "DISCREPANCIA_TAMANO")

    def test_deteccion_archivo_faltante(self):
        """Detecta la eliminación o ausencia de un archivo listado."""
        target_file = (
            self.base_temp
            / "entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md"
        )
        target_file.unlink()

        codigo, resultados = verificar_manifiesto(self.temp_manifest, self.base_temp)
        self.assertEqual(codigo, 2, "Debe retornar 2 cuando hay archivos faltantes")
        res = next(r for r in resultados if r["nombre"] == "NOTA-NASA-EDF.md")
        self.assertEqual(res["estado"], "NO_ENCONTRADO")

    def test_deteccion_violacion_metadato_fuente_primaria_nasa(self):
        """Detecta intento de declarar indebidamente la nota NASA como fuente primaria en el manifiesto."""
        with open(self.temp_manifest, "r", encoding="utf-8") as f:
            datos = json.load(f)

        for arch in datos["archivos"]:
            if arch["nombre"] == "NOTA-NASA-EDF.md":
                arch["es_fuente_primaria"] = True

        with open(self.temp_manifest, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2)

        codigo, resultados = verificar_manifiesto(self.temp_manifest, self.base_temp)
        self.assertEqual(codigo, 2, "Debe retornar código 2 ante error en metadatos obligatorios")
        res = next(r for r in resultados if r["nombre"] == "NOTA-NASA-EDF.md")
        self.assertEqual(res["estado"], "ERROR_METADATOS")


if __name__ == "__main__":
    unittest.main()
