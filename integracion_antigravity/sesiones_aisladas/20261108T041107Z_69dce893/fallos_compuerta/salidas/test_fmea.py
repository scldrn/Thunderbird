#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_fmea.py
Suite de pruebas unitarias y de integración para la validación del FMEA
conceptual de compuertas A07.

Comprueba:
1. Existencia de todos los entregables requeridos en salidas/.
2. Ejecución limpia y sin errores de validar_fmea.py.
3. Integridad estructural y de esquema del CSV.
4. Cobertura de los 7 modos de fallo y de los estados de bajo y alto avance.
5. Verificación de restricciones obligatorias (no probabilidades cuantificadas,
   no empuje proporcional a área, no garantía de vuelo seguro).
6. Casos negativos: comprueba que el validador rechaza activamente violaciones.
"""

import csv
import os
import subprocess
import sys
import tempfile
import unittest

# Importar validador directamente para pruebas unitarias
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from validar_fmea import (
    CABECERAS_REQUERIDAS,
    MODOS_REQUERIDOS,
    ESTADOS_PERMITIDOS,
    SEVERIDADES_PERMITIDAS,
    validar_archivo_csv,
    FMEAValidationError,
)


class TestFMEACompuertasA07(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.salidas_dir = SCRIPT_DIR
        cls.csv_path = os.path.join(cls.salidas_dir, "fmea_compuertas_a07.csv")
        cls.validator_path = os.path.join(cls.salidas_dir, "validar_fmea.py")
        cls.readme_path = os.path.join(cls.salidas_dir, "README.md")
        cls.test_path = os.path.join(cls.salidas_dir, "test_fmea.py")

    def test_01_archivos_entregables_existen(self):
        """Verifica que todos los archivos entregables existen en salidas/."""
        self.assertTrue(os.path.isfile(self.csv_path), "Falta fmea_compuertas_a07.csv en salidas/")
        self.assertTrue(os.path.isfile(self.validator_path), "Falta validar_fmea.py en salidas/")
        self.assertTrue(os.path.isfile(self.readme_path), "Falta README.md en salidas/")
        self.assertTrue(os.path.isfile(self.test_path), "Falta test_fmea.py en salidas/")

    def test_02_ejecucion_script_validador(self):
        """Ejecuta el script validador mediante subprocess y verifica salida exitosa (código 0)."""
        resultado = subprocess.run(
            [sys.executable, self.validator_path, self.csv_path],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            resultado.returncode,
            0,
            f"validar_fmea.py falló con código {resultado.returncode}.\nSalida: {resultado.stdout}\nError: {resultado.stderr}",
        )
        self.assertIn("VALIDACIÓN EXITOSA", resultado.stdout)

    def test_03_estructura_csv(self):
        """Verifica cabeceras, número de filas y ausencia de celdas vacías."""
        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            self.assertEqual(lector.fieldnames, CABECERAS_REQUERIDAS)
            filas = list(lector)
            
        self.assertGreaterEqual(len(filas), 14, "Deben existir al menos 14 registros (7 modos x 2 estados)")
        
        for idx, fila in enumerate(filas, start=1):
            for col in CABECERAS_REQUERIDAS:
                val = (fila.get(col) or "").strip()
                self.assertTrue(
                    len(val) > 0,
                    f"Fila {idx} tiene la columna '{col}' vacía.",
                )

    def test_04_cobertura_modos_y_estados(self):
        """Verifica que los 7 modos de fallo requeridos están presentes en Bajo y Alto avance."""
        reporte = validar_archivo_csv(self.csv_path)
        self.assertTrue(reporte["valido"], f"El reporte de validación contiene errores: {reporte['errores']}")
        
        modos_encontrados = set(reporte["modos_analizados"])
        self.assertEqual(modos_encontrados, MODOS_REQUERIDOS)
        
        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
            
        for modo in MODOS_REQUERIDOS:
            estados_modo = {f["estado_vuelo"] for f in filas if f["modo_fallo"] == modo}
            self.assertIn("Bajo avance", estados_modo, f"Modo '{modo}' no cubierto en Bajo avance")
            self.assertIn("Alto avance", estados_modo, f"Modo '{modo}' no cubierto en Alto avance")

    def test_05_restriccion_probabilidad_no_cuantificada(self):
        """Verifica que ninguna fila contenga probabilidades numéricas o RPNs calculados."""
        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
            
        for fila in filas:
            prob = fila["probabilidad_cuantificada"]
            self.assertIn("No cuantificada", prob)
            # Asegurar que no hay números flotantes o notación científica
            self.assertNotIn("1e-", prob)
            self.assertNotIn("10^-", prob)
            self.assertNotIn("%", prob)

    def test_06_restriccion_empuje_proporcional_a_area(self):
        """Verifica que no se atribuya empuje proporcional a área."""
        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
            
        for fila in filas:
            texto = " ".join(fila.values()).lower()
            if "proporcional a" in texto and "área" in texto:
                # Debe estar explícitamente negado
                tiene_negacion = any(
                    neg in texto for neg in [
                        "no se atribuye empuje proporcional",
                        "se rechaza explícitamente asumir empuje proporcional",
                        "el empuje no es proporcional",
                        "se excluye asumir empuje proporcional",
                        "no es proporcional",
                    ]
                )
                self.assertTrue(
                    tiene_negacion,
                    f"Fila {fila['id_caso']} menciona proporcionalidad a área sin negarla explícitamente.",
                )

    def test_07_restriccion_garantia_vuelo_seguro(self):
        """Verifica que ninguna mitigación o efecto afirme garantía de vuelo seguro."""
        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
            
        for fila in filas:
            texto = " ".join(fila.values()).lower()
            if "vuelo seguro" in texto:
                tiene_deslinde = any(
                    neg in texto for neg in [
                        "sin garantía de vuelo seguro",
                        "no existe garantía de vuelo seguro",
                        "no confiere garantía de vuelo seguro",
                        "no garantiza vuelo seguro",
                        "no se garantiza la capacidad de mantener el vuelo seguro",
                        "no se garantiza vuelo seguro",
                    ]
                )
                self.assertTrue(
                    tiene_deslinde,
                    f"Fila {fila['id_caso']} menciona 'vuelo seguro' sin deslinde explícito.",
                )

    def test_08_separacion_hipotesis_de_evidencia(self):
        """Verifica que se distingan hipótesis de implementación de la evidencia necesaria."""
        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
            
        for fila in filas:
            hip = fila["hipotesis_implementacion"].lower()
            evi = fila["evidencia_necesaria"].lower()
            
            # Hipótesis debe declarar que no está en el CAD actual
            self.assertTrue(
                any(p in hip for p in ["no implementado", "no existen actuadores", "no existen", "hipótesis de diseño"]),
                f"Fila {fila['id_caso']} no declara que la hipótesis de implementación no está en el CAD A07",
            )
            
            # Evidencia debe especificar métodos de prueba
            self.assertTrue(
                any(p in evi for p in ["ensayo", "banco", "túnel", "cfd", "cálculo", "fsi"]),
                f"Fila {fila['id_caso']} no especifica evidencia técnica adecuada",
            )

    def test_09_distincion_datos_y_fuentes(self):
        """Verifica distinción de datos [CÁLCULO], [SUPUESTO], [NO MEDIDO] y citas de fuentes."""
        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
            
        for fila in filas:
            base = fila["supuestos_y_datos_base"].lower()
            self.assertIn("[cálculo", base)
            self.assertIn("[supuesto", base)
            self.assertIn("[no medido", base)

    def test_10_casos_negativos_validador(self):
        """Prueba que el validador rechaza datos corruptos o no conformes."""
        # 1. Archivo inexistente
        with self.assertRaises(FMEAValidationError):
            validar_archivo_csv("/ruta/inexistente/archivo_fantasma.csv")

        # 2. Archivo temporal con celda vacía
        with tempfile.NamedTemporaryFile("w+", suffix=".csv", delete=False) as tf:
            tf_name = tf.name
            writer = csv.writer(tf)
            writer.writerow(CABECERAS_REQUERIDAS)
            # Fila con celda vacía
            fila_invalida = ["FMEA-A07-001", "Fallo al cerrar", "Subsistema", "Bajo avance", "", "", "", "", "Crítica", "", "", "", "", "No cuantificada", ""]
            writer.writerow(fila_invalida)
            
        try:
            reporte = validar_archivo_csv(tf_name)
            self.assertFalse(reporte["valido"], "El validador debió fallar ante celdas vacías")
            self.assertGreater(len(reporte["errores"]), 0)
        finally:
            if os.path.exists(tf_name):
                os.remove(tf_name)

        # 3. Archivo temporal con probabilidad numérica indebida
        with tempfile.NamedTemporaryFile("w+", suffix=".csv", delete=False) as tf:
            tf_name = tf.name
            writer = csv.writer(tf)
            writer.writerow(CABECERAS_REQUERIDAS)
            fila_con_num = [
                "FMEA-A07-001", "Fallo al cerrar", "Subsistema", "Bajo avance", "Cond", "Causa", "Efecto loc",
                "Efecto veh no se atribuye empuje proporcional a área sin garantía de vuelo seguro",
                "Crítica", "Det", "Mit sin garantía de vuelo seguro",
                "Hipótesis de diseño no implementado en A07", "Ensayos en túnel",
                "1e-6 por hora de vuelo",  # PROHIBIDO
                "[CÁLCULO CAD] x [SUPUESTO] y [NO MEDIDO] z LEEME.md"
            ]
            writer.writerow(fila_con_num)
            
        try:
            reporte = validar_archivo_csv(tf_name)
            self.assertFalse(reporte["valido"], "El validador debió fallar ante probabilidad numérica cuantificada")
            self.assertTrue(any("probabilidad cuantificada numérica no permitida" in err for err in reporte["errores"]))
        finally:
            if os.path.exists(tf_name):
                os.remove(tf_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
