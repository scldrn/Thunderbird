#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_resumen_lotes.py - Batería de pruebas unitarias y de integración para resumen_lotes.py.

Verifica:
  1. Manifiestos de referencia válidos (sesiones en entradas/).
  2. Detección y manejo controlado de manifiestos truncados (sintaxis incompleta, fin abrupto, archivos vacíos).
  3. Detección y reporte de identificadores duplicados (en 'tareas' y en 'requieren_revision').
  4. Cumplimiento de la regla metodológica: NO convertir estado 'completado' en aceptación científica.
  5. Casos borde: discrepancia de conteo de recolección, tareas huérfanas en revisión, y formatos JSON anormales.
  6. Formateo de tablas en texto plano, Markdown y serialización JSON.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import unittest

# Asegurar importación de resumen_lotes desde el mismo directorio
DIR_ACTUAL = Path(__file__).resolve().parent
if str(DIR_ACTUAL) not in sys.path:
    sys.path.insert(0, str(DIR_ACTUAL))

from resumen_lotes import (
    ADVERTENCIA_EPISTEMOLOGICA,
    ESTADO_ACEPTACION_NO_AVALADO,
    ESTADO_ACEPTACION_PENDIENTE,
    ESTADO_ACEPTACION_REVISION_REQUERIDA,
    ResumenLote,
    buscar_manifiestos_en_directorio,
    clasificar_aceptacion_cientifica,
    generar_salida_unificada,
    generar_tabla_markdown,
    generar_tabla_texto,
    leer_manifiesto_archivo,
    parsear_manifiesto_json,
    procesar_lotes,
)


class TestManifiestosReferencia(unittest.TestCase):
    """Pruebas sobre los manifiestos reales provistos en entradas/."""

    def setUp(self):
        self.ruta_lote_1 = Path(
            "entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/RESUMEN.json"
        )
        self.ruta_lote_2 = Path(
            "entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/RESUMEN.json"
        )

    def test_lote_1_integridad_y_metricas(self):
        """Verifica la lectura completa y métricas del primer lote de referencia."""
        self.assertTrue(self.ruta_lote_1.exists(), "El archivo de referencia 1 debe existir.")
        resumen = leer_manifiesto_archivo(self.ruta_lote_1)

        self.assertTrue(resumen.valido)
        self.assertFalse(resumen.es_truncado)
        self.assertIsNone(resumen.error_parseo)
        self.assertEqual(resumen.estado_lote, "completado")
        self.assertEqual(resumen.numero_recogido, 12)
        self.assertEqual(len(resumen.tareas_crudas), 12)
        self.assertEqual(len(resumen.requieren_revision_crudas), 4)

        # Verificar duración calculada preservando unidades (segundos)
        self.assertIsNotNone(resumen.duracion_segundos)
        self.assertAlmostEqual(resumen.duracion_segundos, 607.718557, places=4)

        # Tareas específicas que requieren revisión en lote 1
        esperadas_revision = {
            "uiuc_estatico",
            "dependencias_plan",
            "trayectoria_jerk",
            "auditoria_cfd",
        }
        self.assertEqual(set(resumen.requieren_revision_crudas), esperadas_revision)

        # No debe haber duplicados en el lote 1
        self.assertEqual(len(resumen.duplicados_tareas), 0)
        self.assertEqual(len(resumen.duplicados_revision), 0)

    def test_lote_2_integridad_y_metricas(self):
        """Verifica la lectura completa y métricas del segundo lote de referencia."""
        self.assertTrue(self.ruta_lote_2.exists(), "El archivo de referencia 2 debe existir.")
        resumen = leer_manifiesto_archivo(self.ruta_lote_2)

        self.assertTrue(resumen.valido)
        self.assertFalse(resumen.es_truncado)
        self.assertEqual(resumen.estado_lote, "completado")
        self.assertEqual(resumen.numero_recogido, 12)
        self.assertEqual(len(resumen.tareas_crudas), 12)
        self.assertEqual(len(resumen.requieren_revision_crudas), 6)

        # Duración calculada (segundos)
        self.assertIsNotNone(resumen.duracion_segundos)
        self.assertAlmostEqual(resumen.duracion_segundos, 584.707409, places=4)

        esperadas_revision = {
            "revisar_uiuc_estatico",
            "revisar_energia",
            "recuperar_jerk",
            "revisar_cg",
            "revisar_uiuc_avance",
            "revisar_estructura",
        }
        self.assertEqual(set(resumen.requieren_revision_crudas), esperadas_revision)


class TestReglaNoAceptacionCientifica(unittest.TestCase):
    """
    Verifica que el estado técnico 'completado' JAMÁS se convierta
    ni se interprete como aceptación científica o validación formal.
    """

    def test_clasificacion_tareas_lote_completado(self):
        """
        Para tareas dentro de un lote 'completado':
        - Si requiere revisión: ESTADO_ACEPTACION_REVISION_REQUERIDA.
        - Si NO requiere revisión: ESTADO_ACEPTACION_PENDIENTE.
        - En NINGÚN caso se declara 'aceptada', 'validada' o 'aprobada'.
        """
        estado_rev = clasificar_aceptacion_cientifica(requiere_revision=True, estado_lote="completado")
        estado_no_rev = clasificar_aceptacion_cientifica(requiere_revision=False, estado_lote="completado")

        self.assertEqual(estado_rev, ESTADO_ACEPTACION_REVISION_REQUERIDA)
        self.assertEqual(estado_no_rev, ESTADO_ACEPTACION_PENDIENTE)

        # Asegurar que ninguna cadena afirme aceptación científica
        for estado_str in (estado_rev, estado_no_rev):
            self.assertNotIn("ACEPTADA", estado_str.upper())
            self.assertNotIn("VALIDADA CIENTÍFICAMENTE", estado_str.upper())
            self.assertNotIn("APROBADA", estado_str.upper())

    def test_clasificacion_tareas_lote_no_completado(self):
        """Si el lote falló, está en ejecución o es parcial, no debe avalarse ninguna tarea."""
        for estado_invalido in ["fallido", "en_proceso", "parcial", "abortado", None]:
            resultado = clasificar_aceptacion_cientifica(requiere_revision=False, estado_lote=estado_invalido)
            self.assertEqual(resultado, ESTADO_ACEPTACION_NO_AVALADO)

    def test_tareas_analizadas_conservan_restriccion(self):
        """Revisa que en el lote real 1 ninguna tarea analizada tenga marca de aceptación científica."""
        ruta_lote = Path(
            "entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/RESUMEN.json"
        )
        resumen = leer_manifiesto_archivo(ruta_lote)
        for t in resumen.tareas_analizadas:
            self.assertNotEqual(t.estado_aceptacion_cientifica, "Aceptado")
            self.assertIn("pendiente", t.estado_aceptacion_cientifica.lower())


class TestManifiestosTruncados(unittest.TestCase):
    """Pruebas exhaustivas de manejo de archivos y cadenas de manifiestos truncados."""

    def test_manifiesto_truncado_desde_fixture(self):
        """Verifica la lectura del fixture truncado guardado en disco."""
        ruta_fixture = DIR_ACTUAL / "fixtures" / "manifiesto_truncado.json"
        self.assertTrue(ruta_fixture.exists(), "Fixture truncado debe existir en salidas/fixtures/")

        resumen = leer_manifiesto_archivo(ruta_fixture)
        self.assertFalse(resumen.valido)
        self.assertTrue(resumen.es_truncado)
        self.assertIsNotNone(resumen.error_parseo)
        self.assertIn("Error de decodificación JSON", resumen.error_parseo)

    def test_cadena_vacia(self):
        """Un manifiesto vacío debe considerarse truncado de forma controlada."""
        resumen = parsear_manifiesto_json("", ruta_origen="<vacio>")
        self.assertFalse(resumen.valido)
        self.assertTrue(resumen.es_truncado)
        self.assertIn("vacío", resumen.error_parseo.lower())

    def test_corte_abrupto_en_mitad_de_clave(self):
        """JSON cortado en mitad de una clave."""
        json_cortado = '{"inicio_utc": "2026-11-08", "estado": "comp'
        resumen = parsear_manifiesto_json(json_cortado)
        self.assertFalse(resumen.valido)
        self.assertTrue(resumen.es_truncado)

    def test_corte_en_array_de_tareas(self):
        """JSON cortado dentro de la lista de tareas."""
        json_cortado = '{"estado": "completado", "tareas": ["uiuc_estatico", "uiuc_'
        resumen = parsear_manifiesto_json(json_cortado)
        self.assertFalse(resumen.valido)
        self.assertTrue(resumen.es_truncado)

    def test_archivo_inexistente(self):
        """Intentar leer un archivo que no existe no debe lanzar excepción no controlada."""
        resumen = leer_manifiesto_archivo("ruta/completamente/inexistente/RESUMEN.json")
        self.assertFalse(resumen.valido)
        self.assertFalse(resumen.es_truncado)
        self.assertIn("no encontrado", resumen.error_parseo.lower())


class TestIDsDuplicados(unittest.TestCase):
    """Pruebas de detección, conteo y etiquetado de IDs duplicados."""

    def test_fixture_ids_duplicados(self):
        """Evalúa el fixture con duplicados tanto en 'tareas' como en 'requieren_revision'."""
        ruta_fixture = DIR_ACTUAL / "fixtures" / "manifiesto_duplicados.json"
        self.assertTrue(ruta_fixture.exists())

        resumen = leer_manifiesto_archivo(ruta_fixture)
        self.assertTrue(resumen.valido)

        # En 'tareas': uiuc_estatico aparece 2 veces, termica_motor aparece 2 veces
        self.assertEqual(resumen.duplicados_tareas.get("uiuc_estatico"), 2)
        self.assertEqual(resumen.duplicados_tareas.get("termica_motor"), 2)
        self.assertNotIn("uiuc_avance", resumen.duplicados_tareas)

        # En 'requieren_revision': uiuc_estatico aparece 2 veces
        self.assertEqual(resumen.duplicados_revision.get("uiuc_estatico"), 2)

        # Verificar que las tareas analizadas fueron anotadas con su ocurrencia
        tareas_estatico = [t for t in resumen.tareas_analizadas if t.id_tarea == "uiuc_estatico"]
        self.assertEqual(len(tareas_estatico), 2)
        self.assertTrue(tareas_estatico[0].es_duplicada)
        self.assertEqual(tareas_estatico[0].numero_ocurrencia, 1)
        self.assertEqual(tareas_estatico[0].total_ocurrencias, 2)
        self.assertEqual(tareas_estatico[1].numero_ocurrencia, 2)
        self.assertEqual(tareas_estatico[1].total_ocurrencias, 2)

        # Verificar alertas generadas
        alertas_texto = " ".join(resumen.advertencias_lote)
        self.assertIn("uiuc_estatico", alertas_texto)
        self.assertIn("termica_motor", alertas_texto)

    def test_duplicados_sinteticos_multiples(self):
        """Verifica una tarea repetida 4 veces."""
        datos = {
            "estado": "completado",
            "tareas": ["sensor_alfa", "sensor_alfa", "sensor_beta", "sensor_alfa", "sensor_alfa"],
            "recolectadas": 5,
            "requieren_revision": ["sensor_alfa"],
        }
        resumen = parsear_manifiesto_json(json.dumps(datos))
        self.assertEqual(resumen.duplicados_tareas["sensor_alfa"], 4)
        self.assertEqual(len(resumen.tareas_analizadas), 5)


class TestCasosBordeYDiscrepancias(unittest.TestCase):
    """Pruebas de casos borde: discrepancias en contadores, tareas huérfanas y raíces inválidas."""

    def test_fixture_discrepancia(self):
        """Verifica detección de discrepancia de conteo y tarea en revisión no listada."""
        ruta_fixture = DIR_ACTUAL / "fixtures" / "manifiesto_discrepancia.json"
        resumen = leer_manifiesto_archivo(ruta_fixture)

        self.assertTrue(resumen.valido)
        # Discrepancia: declara recolectadas 1, pero tareas tiene 2
        self.assertEqual(resumen.discrepancia_recogidas, (1, 2))
        # Tarea huérfana en revisión: tarea_inexistente
        self.assertIn("tarea_inexistente", resumen.revision_no_en_tareas)

    def test_raiz_json_no_es_objeto(self):
        """Un archivo JSON válido pero que contiene una lista en su raíz en lugar de un objeto."""
        resumen = parsear_manifiesto_json('["tarea_1", "tarea_2"]')
        self.assertFalse(resumen.valido)
        self.assertIn("Estructura raíz inválida", resumen.error_parseo)

    def test_campos_con_tipos_inesperados(self):
        """Manejo tolerante cuando campos opcionales tienen tipos no esperados."""
        datos = {
            "estado": 12345,
            "tareas": "no_es_lista",
            "requieren_revision": None,
            "recolectadas": "doce",
        }
        resumen = parsear_manifiesto_json(json.dumps(datos))
        self.assertTrue(resumen.valido)
        self.assertEqual(resumen.estado_lote, "12345")
        self.assertEqual(len(resumen.tareas_crudas), 0)


class TestFormateadoresYSalidas(unittest.TestCase):
    """Verifica que los generadores de tabla (texto, Markdown, JSON) contengan la información requerida."""

    def setUp(self):
        self.ruta_lote = Path(
            "entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/RESUMEN.json"
        )
        self.resumen = leer_manifiesto_archivo(self.ruta_lote)

    def test_generador_texto(self):
        texto = generar_tabla_texto(self.resumen)
        self.assertIn("uiuc_estatico", texto)
        self.assertIn("completado", texto)
        self.assertIn("Número Recogido (Métrica): 12", texto)
        self.assertIn("REGLA EPISTEMOLÓGICA", texto)
        self.assertIn(ADVERTENCIA_EPISTEMOLOGICA, texto)

    def test_generador_markdown(self):
        md = generar_tabla_markdown(self.resumen)
        self.assertIn("| # | ID de Tarea | Requiere Revisión | Estado de Aceptación Científica |", md)
        self.assertIn("`uiuc_estatico`", md)
        self.assertIn("Número recogido (tareas recolectadas):** `12`", md)
        self.assertIn("Principio de Rigor:", md)

    def test_generador_unificado_json(self):
        salida_json = generar_salida_unificada([self.resumen], formato="json")
        data = json.loads(salida_json)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["estado_lote"], "completado")
        self.assertEqual(data[0]["numero_recogido"], 12)
        self.assertIn("uiuc_estatico", data[0]["tareas_que_requieren_revision"])


if __name__ == "__main__":
    unittest.main()
