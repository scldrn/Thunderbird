#!/usr/bin/env python3
"""
test_dependencias.py
====================
Suite de pruebas automatizadas con unittest para verificar la integridad del
grafo de dependencias del Plan Maestro de Investigación Aeronáutica.

Pruebas cubiertas:
1. Verificación del conjunto canónico: ausencia de dependencias inexistentes y aciclicidad (DAG).
2. Detección sintética de dependencias inexistentes (aisladas, múltiples, IDs inválidos).
3. Detección sintética de ciclos (autociclo, ciclo directo 2 nodos, ciclo indirecto 3+ nodos, componentes inconexos).
4. Verificación de reglas de negocio:
   - Tareas computacionales con dependencias abiertas (31 tareas).
   - Pasos paralelizables de preparación (15 tareas).
   - Tareas físicas (7 tareas en Hito F).
   - 40 tareas P0 y dependencias críticas P1 que las desbloquean.
   - Principio "sin declarar cierres".
   - Integridad y existencia de los entregables CSV en salidas/.
"""

import copy
import csv
import unittest
from pathlib import Path
import sys

# Asegurar importación del módulo analizador
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from analizar_dependencias import (
    cargar_datos,
    parsear_dependencias,
    validar_dependencias_existentes,
    detectar_ciclos,
    cruzar_y_clasificar,
    calcular_estadisticas,
    SALIDAS_DIR,
    TRABAJO_PATH,
    ESTADO_PATH,
)


class TestGrafoDependenciasCanonico(unittest.TestCase):
    """Pruebas sobre los archivos canónicos de referencia."""

    @classmethod
    def setUpClass(cls):
        cls.trabajo, cls.estado = cargar_datos(TRABAJO_PATH, ESTADO_PATH)

    def test_carga_48_tareas_exactas(self):
        """Verifica que ambos archivos canónicos contengan exactamente 48 tareas alineadas."""
        self.assertEqual(len(self.trabajo), 48)
        self.assertEqual(len(self.estado), 48)
        trabajo_ids = [r["id"].strip() for r in self.trabajo]
        estado_ids = list(self.estado.keys())
        self.assertEqual(trabajo_ids, estado_ids)

    def test_cero_dependencias_inexistentes_canonico(self):
        """Verifica que ninguna tarea del plan canónico apunte a un ID inexistente."""
        errores = validar_dependencias_existentes(self.trabajo)
        self.assertEqual(
            errores,
            {},
            f"El plan canónico contiene dependencias inexistentes: {errores}",
        )

    def test_grafo_canonico_es_dag_sin_ciclos(self):
        """Verifica que el grafo canónico sea un DAG estricto sin ciclos."""
        tiene_ciclo, orden, ciclo = detectar_ciclos(self.trabajo)
        self.assertFalse(
            tiene_ciclo,
            f"El plan canónico contiene un ciclo inesperado: {' -> '.join(ciclo)}",
        )
        self.assertEqual(len(orden), 48)
        # T01 debe ser la primera en orden topológico (única sin dependencias en G0)
        self.assertEqual(orden[0], "T01")


class TestDeteccionSinteticaDependenciasInexistentes(unittest.TestCase):
    """Pruebas sintéticas para inyección y detección de dependencias inexistentes."""

    def setUp(self):
        self.trabajo_base, _ = cargar_datos(TRABAJO_PATH, ESTADO_PATH)

    def test_detecta_dependencia_inexistente_simple(self):
        """Inyecta una dependencia a 'T99' inexistente y comprueba que se detecta."""
        sintetico = copy.deepcopy(self.trabajo_base)
        sintetico[1]["depende_de"] = "T01;T99"  # T02 depende de T01 y T99
        errores = validar_dependencias_existentes(sintetico)
        self.assertIn("T02", errores)
        self.assertEqual(errores["T02"], ["T99"])

    def test_detecta_multiples_dependencias_inexistentes(self):
        """Inyecta dependencias inexistentes en múltiples tareas."""
        sintetico = copy.deepcopy(self.trabajo_base)
        sintetico[0]["depende_de"] = "T_INVENTADA_1"
        sintetico[5]["depende_de"] = "T04;T_INVENTADA_2;T_INVENTADA_3"
        errores = validar_dependencias_existentes(sintetico)
        self.assertIn("T01", errores)
        self.assertIn("T06", errores)
        self.assertEqual(errores["T01"], ["T_INVENTADA_1"])
        self.assertEqual(errores["T06"], ["T_INVENTADA_2", "T_INVENTADA_3"])

    def test_tolerancia_espacios_y_puntos_y_coma(self):
        """Verifica que separadores vacíos o espacios no generen falsos positivos."""
        sintetico = copy.deepcopy(self.trabajo_base)
        sintetico[1]["depende_de"] = " T01 ; ; "
        errores = validar_dependencias_existentes(sintetico)
        self.assertEqual(errores, {})


class TestDeteccionSinteticaCiclos(unittest.TestCase):
    """Pruebas sintéticas para inyección y detección de ciclos en el grafo."""

    def setUp(self):
        self.trabajo_base, _ = cargar_datos(TRABAJO_PATH, ESTADO_PATH)

    def test_detecta_autociclo(self):
        """Inyecta una tarea que depende de sí misma (T05 depende de T05)."""
        sintetico = copy.deepcopy(self.trabajo_base)
        # T05 depende normalmente de T03;T04 -> inyectar T05
        sintetico[4]["depende_de"] = "T03;T04;T05"
        tiene_ciclo, orden, ciclo = detectar_ciclos(sintetico)
        self.assertTrue(tiene_ciclo, "No se detectó el autociclo.")
        self.assertIn("T05", ciclo)

    def test_detecta_ciclo_directo_dos_nodos(self):
        """Inyecta un ciclo mutuo directo entre T01 y T02 (T01 depende de T02 y viceversa)."""
        sintetico = copy.deepcopy(self.trabajo_base)
        sintetico[0]["depende_de"] = "T02"  # T01 depende de T02
        # T02 ya depende de T01
        tiene_ciclo, orden, ciclo = detectar_ciclos(sintetico)
        self.assertTrue(tiene_ciclo, "No se detectó el ciclo directo de 2 nodos.")
        self.assertTrue(
            ("T01" in ciclo and "T02" in ciclo),
            f"El ciclo detectado no contiene los nodos involucrados: {ciclo}",
        )

    def test_detecta_ciclo_indirecto_tres_o_mas_nodos(self):
        """Inyecta un ciclo triangular: T04 -> T06 -> T09 -> T04."""
        sintetico = copy.deepcopy(self.trabajo_base)
        # Normalmente T06 depende de T04, T09 depende de T06 y T08.
        # Hacemos que T04 dependa de T09:
        sintetico[3]["depende_de"] = "T02;T09"
        tiene_ciclo, orden, ciclo = detectar_ciclos(sintetico)
        self.assertTrue(tiene_ciclo, "No se detectó el ciclo indirecto de 3 nodos.")
        self.assertTrue(
            any(node in ciclo for node in ["T04", "T06", "T09"]),
            f"Ciclo detectado inesperado: {ciclo}",
        )

    def test_detecta_ciclo_en_subgrafo_aislado(self):
        """Crea un subgrafo pequeño aislado con ciclo y verifica detección."""
        subgrafo = [
            {"id": "A", "depende_de": "B"},
            {"id": "B", "depende_de": "C"},
            {"id": "C", "depende_de": "A"},
            {"id": "D", "depende_de": ""},
        ]
        tiene_ciclo, orden, ciclo = detectar_ciclos(subgrafo)
        self.assertTrue(tiene_ciclo, "No se detectó el ciclo en subgrafo aislado.")


class TestClasificacionYReglasNegocio(unittest.TestCase):
    """Verifica las reglas de negocio, clasificaciones y prioridades."""

    @classmethod
    def setUpClass(cls):
        cls.trabajo, cls.estado = cargar_datos(TRABAJO_PATH, ESTADO_PATH)
        cls.registros = cruzar_y_clasificar(cls.trabajo, cls.estado)
        cls.stats = calcular_estadisticas(cls.registros)

    def test_conteo_total_y_prioridades(self):
        """Verifica la distribución exacta de prioridades P0, P1, P2."""
        self.assertEqual(self.stats["total_tareas"], 48)
        self.assertEqual(self.stats["conteo_p0"], 40)
        self.assertEqual(self.stats["conteo_p1"], 7)
        self.assertEqual(self.stats["conteo_p2"], 1)

    def test_tareas_computacionales_con_dependencias_abiertas(self):
        """Verifica que existan exactamente 31 tareas computacionales con dependencias abiertas."""
        comp_abiertas = [r for r in self.registros if r["es_computacional_abierta"]]
        self.assertEqual(len(comp_abiertas), 31)

        # En P0 deben ser 26
        comp_abiertas_p0 = [r for r in comp_abiertas if r["prioridad"] == "P0"]
        self.assertEqual(len(comp_abiertas_p0), 26)

        # T01 es computacional pero no tiene dependencias abiertas (raíz)
        t01_reg = next(r for r in self.registros if r["id"] == "T01")
        self.assertTrue(t01_reg["es_computacional"])
        self.assertFalse(t01_reg["es_computacional_abierta"])

    def test_pasos_paralelizables_preparacion(self):
        """Verifica que los 15 pasos de preparación identificados sean concurrentes en el DAG."""
        prep_paralelos = [r for r in self.registros if r["es_preparacion_paralelizable"]]
        self.assertEqual(len(prep_paralelos), 15)
        # Todos deben tener al menos 1 tarea concurrente en el DAG
        for r in prep_paralelos:
            self.assertGreater(
                r["num_concurrentes"],
                0,
                f"El paso {r['id']} no tiene concurrencia en el DAG.",
            )

    def test_tareas_fisicas_hito_f(self):
        """Verifica las 7 tareas del Hito F (físicas y de contraste experimental)."""
        fisicas = [r for r in self.registros if r["es_tarea_fisica"]]
        self.assertEqual(len(fisicas), 7)
        fisica_ids = {r["id"] for r in fisicas}
        self.assertEqual(
            fisica_ids,
            {"T42", "T43", "T44", "T45", "T46", "T47", "T48"},
        )
        # 5 de ellas son P0
        fisicas_p0 = [r for r in fisicas if r["prioridad"] == "P0"]
        self.assertEqual(len(fisicas_p0), 5)

    def test_p1_criticos_desbloquean_p0(self):
        """Verifica que las tareas P1 que son prerequisito de P0 estén explícitamente rastreadas."""
        p1_bloquean = self.stats["p1_que_desbloquean_p0"]
        self.assertIn("T19", p1_bloquean)  # T19 (P1) -> T20 (P0)
        self.assertIn("T27", p1_bloquean)  # T27 (P1) -> T28 (P0)
        self.assertIn("T38", p1_bloquean)  # T38 (P1) -> T41 (P0)
        self.assertIn("T40", p1_bloquean)  # T40 (P1) -> T41 (P0)
        self.assertIn("T42", p1_bloquean)  # T42 (P1) -> T43 (P0), T44 (P0)

    def test_principio_sin_declarar_cierres(self):
        """
        Verifica que para toda tarea con dependencias, el número de dependencias
        abiertas sea igual al número total de dependencias declaradas.
        """
        for r in self.registros:
            if r["num_dependencias"] > 0:
                self.assertEqual(
                    r["num_dependencias_abiertas"],
                    r["num_dependencias"],
                    f"La tarea {r['id']} tiene cierres declarados prematuramente.",
                )


class TestExistenciaYConsistenciaCSVs(unittest.TestCase):
    """Verifica que los archivos CSV generados en salidas/ existan y sean reproducibles."""

    def test_archivos_csv_generados_existen(self):
        archivos_esperados = [
            SALIDAS_DIR / "matriz_tareas_dependencias.csv",
            SALIDAS_DIR / "tareas_computacionales_abiertas.csv",
            SALIDAS_DIR / "pasos_preparacion_paralelizables.csv",
            SALIDAS_DIR / "tareas_fisicas.csv",
            SALIDAS_DIR / "resumen_prioridades_P0.csv",
        ]
        for ruta in archivos_esperados:
            self.assertTrue(
                ruta.exists(),
                f"El archivo esperado no fue encontrado: {ruta}",
            )
            self.assertGreater(
                ruta.stat().st_size,
                0,
                f"El archivo generado está vacío: {ruta}",
            )

    def test_conteos_filas_csvs(self):
        """Verifica que el número de filas de cada CSV coincida con las métricas."""
        with open(SALIDAS_DIR / "matriz_tareas_dependencias.csv", encoding="utf-8") as f:
            filas_maestra = list(csv.DictReader(f))
            self.assertEqual(len(filas_maestra), 48)

        with open(SALIDAS_DIR / "tareas_computacionales_abiertas.csv", encoding="utf-8") as f:
            filas_comp = list(csv.DictReader(f))
            self.assertEqual(len(filas_comp), 31)

        with open(SALIDAS_DIR / "pasos_preparacion_paralelizables.csv", encoding="utf-8") as f:
            filas_prep = list(csv.DictReader(f))
            self.assertEqual(len(filas_prep), 15)

        with open(SALIDAS_DIR / "tareas_fisicas.csv", encoding="utf-8") as f:
            filas_fis = list(csv.DictReader(f))
            self.assertEqual(len(filas_fis), 7)

        with open(SALIDAS_DIR / "resumen_prioridades_P0.csv", encoding="utf-8") as f:
            filas_p0 = list(csv.DictReader(f))
            self.assertEqual(len(filas_p0), 40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
