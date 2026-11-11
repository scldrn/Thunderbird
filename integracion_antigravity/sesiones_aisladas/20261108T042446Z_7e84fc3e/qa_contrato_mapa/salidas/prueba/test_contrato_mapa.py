#!/usr/bin/env python3
"""
Módulo de pruebas unitarias: test_contrato_mapa.py
Pruebas exhaustivas con unittest estándar para verificar:
  1. Aceptación de datasets válidos (ejemplo sintético).
  2. Rechazo de unidades ausentes o inválidas.
  3. Rechazo de valores NaN e infinitos.
  4. Rechazo de geometría o ejes desconocidos / inconsistentes.
  5. Rechazo de muestras duplicadas en el espacio de entradas físicas.
  6. Rechazo de extrapolación declarada o fuera de dominio.
  7. Aceptación de marcas explícitas de datos faltantes.
  8. NO coerción de datos faltantes a cero (preservación de nulidad e indicación).
  9. Consistencia de transformaciones de coordenadas y reducción de momentos.
"""

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from contrato_mapa_ventilador import (
    CONTRATO_VERSION,
    CodigoErrorValidacion,
    DominioValidez,
    ErrorValidacionContrato,
    GeometriaReferencia,
    MapaInstaladoFan,
    RangoDominio,
    RegistroDatoFaltante,
    ValidadorMapaInstalado,
    cargar_mapa_json,
    guardar_mapa_json,
    rotacion_cad_a_flu,
    rotacion_flu_a_cad,
    transferir_momento,
)

DIR_ACTUAL = Path(__file__).resolve().parent
RUTA_EJEMPLO_SINTETICO = DIR_ACTUAL / "ejemplo_sintetico_mapa.json"


class TestContratoMapaVentilador(unittest.TestCase):
    """Batería completa de pruebas del contrato de datos de mapa instalado."""

    def setUp(self):
        self.validador = ValidadorMapaInstalado()
        with open(RUTA_EJEMPLO_SINTETICO, "r", encoding="utf-8") as f:
            self.base_datos = json.load(f)

    # -------------------------------------------------------------------------
    # 1. Aceptación del ejemplo sintético
    # -------------------------------------------------------------------------
    def test_aceptacion_ejemplo_sintetico(self):
        """Verifica que el archivo de ejemplo sintético sea completamente válido."""
        mapa = cargar_mapa_json(RUTA_EJEMPLO_SINTETICO)
        self.assertIsInstance(mapa, MapaInstaladoFan)
        self.assertEqual(mapa.contrato_version, CONTRATO_VERSION)
        self.assertTrue(mapa.metadatos_origen.es_sintetico)
        self.assertEqual(mapa.metadatos_origen.categoria, "supuesto")
        self.assertEqual(len(mapa.muestras), 4)

    # -------------------------------------------------------------------------
    # 2. Rechazo de Unidades Ausentes o Vacías
    # -------------------------------------------------------------------------
    def test_rechazo_unidades_bloque_ausente(self):
        """Rechaza cuando el bloque 'unidades' no existe."""
        datos = copy.deepcopy(self.base_datos)
        del datos["unidades"]
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.UNIDADES_AUSENTES)

    def test_rechazo_unidad_dimension_faltante(self):
        """Rechaza cuando falta la unidad de una dimensión física requerida (ej. fuerza)."""
        datos = copy.deepcopy(self.base_datos)
        del datos["unidades"]["fuerza"]
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.UNIDADES_AUSENTES)

    def test_rechazo_unidad_vacia(self):
        """Rechaza cuando la unidad declarada es una cadena vacía o espacios."""
        datos = copy.deepcopy(self.base_datos)
        datos["unidades"]["densidad"] = "   "
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.UNIDADES_AUSENTES)

    def test_rechazo_unidad_no_permitida(self):
        """Rechaza unidades que no pertenecen al sistema canónico permitido."""
        datos = copy.deepcopy(self.base_datos)
        datos["unidades"]["potencia"] = "caballos_de_fuerza_hp"
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.UNIDADES_AUSENTES)

    # -------------------------------------------------------------------------
    # 3. Rechazo de Valores NaN e Infinitos
    # -------------------------------------------------------------------------
    def test_rechazo_nan_en_flujo_densidad(self):
        """Rechaza NaN en la densidad del flujo local."""
        datos = copy.deepcopy(self.base_datos)
        datos["muestras"][0]["flujo_local"]["densidad_kg_m3"] = float("nan")
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.VALOR_NAN_DETECTADO)

    def test_rechazo_nan_en_flujo_velocidad(self):
        """Rechaza NaN en componentes del vector de velocidad."""
        datos = copy.deepcopy(self.base_datos)
        datos["muestras"][0]["flujo_local"]["velocidad_vectorial_m_s"][0] = float("nan")
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.VALOR_NAN_DETECTADO)

    def test_rechazo_nan_en_fuerza_vectorial(self):
        """Rechaza NaN en las salidas de fuerza."""
        datos = copy.deepcopy(self.base_datos)
        datos["muestras"][0]["fuerza_vectorial_N"][2] = float("nan")
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.VALOR_NAN_DETECTADO)

    def test_rechazo_nan_en_incertidumbre(self):
        """Rechaza NaN en el vector de incertidumbre."""
        datos = copy.deepcopy(self.base_datos)
        datos["muestras"][0]["incertidumbre"]["fuerza_vectorial_N"][1] = float("nan")
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.VALOR_NAN_DETECTADO)

    def test_rechazo_string_nan(self):
        """Rechaza cadenas literales 'NaN' o 'nan' en campos numéricos."""
        datos = copy.deepcopy(self.base_datos)
        datos["muestras"][0]["mando_estado"]["rpm"] = "NaN"
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.VALOR_NAN_DETECTADO)

    # -------------------------------------------------------------------------
    # 4. Rechazo de Geometría o Ejes Desconocidos
    # -------------------------------------------------------------------------
    def test_rechazo_marco_referencia_desconocido(self):
        """Rechaza marco primario de referencia no registrado."""
        datos = copy.deepcopy(self.base_datos)
        datos["marcos_referencia"]["marco_primario"] = "SISTEMA_LOCAL_DESCONOCIDO"
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS)

    def test_rechazo_punto_aplicacion_marco_invalido(self):
        """Rechaza marco no válido para el punto de aplicación."""
        datos = copy.deepcopy(self.base_datos)
        datos["punto_aplicacion"]["marco_referencia"] = "MARCO_INVENTADO"
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS)

    def test_rechazo_geometria_id_desconocida(self):
        """Rechaza cuando el id de la geometría es 'desconocido' o vacío."""
        datos = copy.deepcopy(self.base_datos)
        datos["geometria_referencia"]["geometria_id"] = "desconocido"
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS)

    def test_rechazo_geometria_dimensiones_invalidas(self):
        """Rechaza cuando el diámetro de paso nominal es <= 0."""
        datos = copy.deepcopy(self.base_datos)
        datos["geometria_referencia"]["diametro_paso_nominal_m"] = -0.084
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS)

    def test_rechazo_sentido_giro_desconocido(self):
        """Rechaza sentido de giro distinto de 'CW' o 'CCW'."""
        datos = copy.deepcopy(self.base_datos)
        datos["geometria_referencia"]["sentido_giro"] = "HORIZONTAL"
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS)

    def test_rechazo_estado_compuerta_desconocido(self):
        """Rechaza un estado de compuerta en muestra que no coincide con los soportados."""
        datos = copy.deepcopy(self.base_datos)
        datos["muestras"][0]["mando_estado"]["estado_compuerta"] = "posicion_invalida"
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.GEOMETRIA_O_EJES_DESCONOCIDOS)

    # -------------------------------------------------------------------------
    # 5. Rechazo de Muestras Duplicadas
    # -------------------------------------------------------------------------
    def test_rechazo_muestras_duplicadas_exactas(self):
        """Rechaza dos muestras con idénticas entradas físicas."""
        datos = copy.deepcopy(self.base_datos)
        # Clonamos la muestra 0 con un ID diferente pero mismas entradas físicas
        muestra_dup = copy.deepcopy(datos["muestras"][0])
        muestra_dup["id_muestra"] = "SINT_0001_CLON"
        # Aunque tenga una fuerza de salida ligeramente editada, las entradas son iguales: DEBE RECHAZARSE
        muestra_dup["fuerza_vectorial_N"] = [0.0, 0.0, 12.30]
        datos["muestras"].append(muestra_dup)

        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.MUESTRAS_DUPLICADAS)

    # -------------------------------------------------------------------------
    # 6. Rechazo de Extrapolación Declarada o Fuera de Dominio
    # -------------------------------------------------------------------------
    def test_rechazo_flag_extrapolacion_declarada(self):
        """Rechaza cuando una muestra tiene declarada explícitamente extrapolación ('es_extrapolacion': true)."""
        datos = copy.deepcopy(self.base_datos)
        datos["muestras"][0]["es_extrapolacion"] = True
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.EXTRAPOLACION_DECLARADA)

    def test_rechazo_muestra_fuera_de_dominio_rpm(self):
        """Rechaza muestra cuyas RPM exceden el límite del dominio cuando la política es RECHAZAR."""
        datos = copy.deepcopy(self.base_datos)
        # Dominio máximo es 32000 RPM en el ejemplo sintético
        datos["muestras"][0]["mando_estado"]["rpm"] = 42000.0
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.EXTRAPOLACION_DECLARADA)

    def test_rechazo_muestra_fuera_de_dominio_velocidad(self):
        """Rechaza muestra con velocidad mayor que el máximo permitido en el dominio."""
        datos = copy.deepcopy(self.base_datos)
        # Dominio máximo es 40 m/s
        datos["muestras"][0]["flujo_local"]["velocidad_vectorial_m_s"] = [55.0, 0.0, 0.0]
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.EXTRAPOLACION_DECLARADA)

    # -------------------------------------------------------------------------
    # 7 y 8. Aceptación de Marcas de Datos Faltantes y NO Coerción a Cero
    # -------------------------------------------------------------------------
    def test_aceptacion_y_no_coercion_de_datos_faltantes(self):
        """
        Comprueba rigurosamente:
          a) Aceptación de null con marca explícita en potencia eléctrica y mecánica.
          b) Que los datos faltantes NO sean transformados silenciosamente en 0.0 o 0.
          c) Que un 0.0 real (rotor en reposo) se conserve legítimamente como 0.0.
        """
        mapa = cargar_mapa_json(RUTA_EJEMPLO_SINTETICO)

        # Muestra 1: potencias medidas y conocidas
        m1 = mapa.muestras[0]
        self.assertEqual(m1.potencia_electrica_W, 310.5)
        self.assertEqual(m1.potencia_mecanica_W, 248.4)

        # Muestra 2: potencia eléctrica no medida con marca explícita
        m2 = mapa.muestras[1]
        self.assertIsInstance(m2.potencia_electrica_W, RegistroDatoFaltante)
        self.assertTrue(m2.potencia_electrica_W.es_dato_faltante)
        self.assertEqual(m2.potencia_electrica_W.estado, "NO_MEDIDO")
        # COMPROBACIÓN CRÍTICA: NO es 0.0
        self.assertNotEqual(m2.potencia_electrica_W, 0.0)
        self.assertNotEqual(m2.potencia_electrica_W, 0)
        # Potencia mecánica sí está disponible en muestra 2
        self.assertEqual(m2.potencia_mecanica_W, 254.2)

        # Muestra 3: ambas potencias ausentes con marcas explícitas
        m3 = mapa.muestras[2]
        self.assertIsInstance(m3.potencia_electrica_W, RegistroDatoFaltante)
        self.assertIsInstance(m3.potencia_mecanica_W, RegistroDatoFaltante)
        self.assertTrue(m3.potencia_electrica_W.es_dato_faltante)
        self.assertTrue(m3.potencia_mecanica_W.es_dato_faltante)
        self.assertNotEqual(m3.potencia_electrica_W, 0.0)
        self.assertNotEqual(m3.potencia_mecanica_W, 0.0)

        # Muestra 4: compuerta cerrada, rotor inactivo (potencia 0.0 real verificada)
        m4 = mapa.muestras[3]
        self.assertEqual(m4.potencia_electrica_W, 0.0)
        self.assertEqual(m4.potencia_mecanica_W, 0.0)

    def test_persistencia_serializacion_preserva_null_sin_cero(self):
        """Verifica que al serializar a JSON se guarden nulls y no 0.0."""
        mapa = cargar_mapa_json(RUTA_EJEMPLO_SINTETICO)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            guardar_mapa_json(mapa, tmp_path)
            with open(tmp_path, "r", encoding="utf-8") as f:
                recargado = json.load(f)

            # Muestra 1 recargada: debe tener 310.5
            self.assertEqual(recargado["muestras"][0]["potencia_electrica_W"], 310.5)
            # Muestra 2 recargada: debe ser estrictamente None (null en json), NO 0.0
            self.assertIsNone(recargado["muestras"][1]["potencia_electrica_W"])
            self.assertNotEqual(recargado["muestras"][1]["potencia_electrica_W"], 0.0)
            # Muestra 3 recargada: ambos null
            self.assertIsNone(recargado["muestras"][2]["potencia_electrica_W"])
            self.assertIsNone(recargado["muestras"][2]["potencia_mecanica_W"])
            # Muestra 4 recargada: es 0.0 legítimo
            self.assertEqual(recargado["muestras"][3]["potencia_electrica_W"], 0.0)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_rechazo_dato_faltante_en_campo_mandatorio(self):
        """Rechaza cuando un campo que NO admite nulidad (ej. densidad o fuerza) se declara null."""
        datos = copy.deepcopy(self.base_datos)
        datos["muestras"][0]["flujo_local"]["densidad_kg_m3"] = None
        with self.assertRaises(ErrorValidacionContrato) as ctx:
            self.validador.validar_dict(datos)
        self.assertEqual(ctx.exception.codigo, CodigoErrorValidacion.CAMPO_OBLIGATORIO_FALTANTE)

    # -------------------------------------------------------------------------
    # 9. Consistencia Cinemática y Reducción de Momentos
    # -------------------------------------------------------------------------
    def test_transformaciones_cad_y_flu(self):
        """Verifica la rotación de vectores entre CAD y FLU según C02_CANDIDATA."""
        # Un vector hacia proa en FLU [1, 0, 0] debe ser [-1, 0, 0] en CAD
        v_flu = [1.0, 0.0, 0.0]
        v_cad = rotacion_flu_a_cad(v_flu)
        self.assertEqual(v_cad, [-1.0, -0.0, 0.0])

        # Conversión inversa
        v_flu_rec = rotacion_cad_a_flu(v_cad)
        self.assertEqual(v_flu_rec, [1.0, 0.0, 0.0])

    def test_transferencia_de_momentos(self):
        """
        Verifica la reducción de momentos:
        M_cg = M_app + (r_app - r_cg) x F
        """
        fuerza = [0.0, 0.0, 10.0]  # 10 N vertical
        momento_en_app = [0.0, 0.0, -0.1]  # -0.1 Nm de par de reacción
        r_app = [0.2, 0.0, 0.0]  # ubicado 0.2 m por delante del CG
        r_cg = [0.0, 0.0, 0.0]  # CG en el origen

        # Brazo (r_app - r_cg) = [0.2, 0.0, 0.0]
        # Brazo x F = [0.2, 0, 0] x [0, 0, 10] = [0, -2.0, 0]
        # M_cg = [0, 0, -0.1] + [0, -2.0, 0] = [0.0, -2.0, -0.1]
        m_cg = transferir_momento(fuerza, momento_en_app, r_app, r_cg)
        self.assertAlmostEqual(m_cg[0], 0.0)
        self.assertAlmostEqual(m_cg[1], -2.0)
        self.assertAlmostEqual(m_cg[2], -0.1)


if __name__ == "__main__":
    unittest.main()
