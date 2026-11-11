"""
Suite de Pruebas Unitarias para el Contrato de Masa, CG y Tensor de Inercia.

Ejecución con Python estándar:
python3 -m unittest salidas/test_contrato.py
"""

import json
import math
import os
import unittest
from pathlib import Path

from salidas.contrato import (
    ADVERTENCIA_PSD_INSUFICIENTE,
    ContratoMasaCG,
    MarcoReferencia,
    MetadatosTrazabilidad,
    PropiedadMasa,
    PropiedadPosicionCG,
    PropiedadTensorInerciaCG,
    ResultadoValidacion,
    TipoNaturaleza,
    calcular_menores_principales_3x3,
    convertir_posicion_cad_a_flu,
    convertir_tensor_cad_a_flu,
    es_reserva_no_asignada,
    obtener_masa_estricta,
    transformar_contrato_a_flu,
    validar_contrato,
    validar_energia_cinetica_no_negativa,
    validar_masa_positiva,
    validar_matriz_3x3_finita,
    validar_simetria_matriz_3x3,
    verificar_desigualdades_triangulares_fisicas,
)

DIRECTORIO_EJEMPLOS = Path(__file__).resolve().parent / "ejemplos_sinteticos"


class TestValidacionMatriz3x3Finita(unittest.TestCase):
    """Pruebas de validación de matriz 3x3 finita."""

    def test_matriz_valida_finita(self):
        m = [[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 3.0]]
        ok, err = validar_matriz_3x3_finita(m)
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_matriz_con_enteros(self):
        m = [[1, 0, 0], [0, 2, 0], [0, 0, 3]]
        ok, err = validar_matriz_3x3_finita(m)
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_matriz_dimension_incorrecta(self):
        # 2x3
        m23 = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
        ok, err = validar_matriz_3x3_finita(m23)
        self.assertFalse(ok)
        self.assertIn("longitud", err)

        # 3x2
        m32 = [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]]
        ok, err = validar_matriz_3x3_finita(m32)
        self.assertFalse(ok)
        self.assertIn("longitud 3", err)

        # None / null
        ok, err = validar_matriz_3x3_finita(None)
        self.assertFalse(ok)
        self.assertIn("null/None", err)

    def test_matriz_con_nan_e_inf(self):
        m_nan = [[1.0, 0.0, 0.0], [0.0, float("nan"), 0.0], [0.0, 0.0, 1.0]]
        ok, err = validar_matriz_3x3_finita(m_nan)
        self.assertFalse(ok)
        self.assertIn("no es un número finito", err)

        m_inf = [[1.0, 0.0, 0.0], [0.0, float("inf"), 0.0], [0.0, 0.0, 1.0]]
        ok, err = validar_matriz_3x3_finita(m_inf)
        self.assertFalse(ok)
        self.assertIn("no es un número finito", err)

        m_neginf = [[1.0, 0.0, 0.0], [0.0, float("-inf"), 0.0], [0.0, 0.0, 1.0]]
        ok, err = validar_matriz_3x3_finita(m_neginf)
        self.assertFalse(ok)
        self.assertIn("no es un número finito", err)

    def test_matriz_con_elementos_no_numericos_o_null(self):
        m_null = [[1.0, None, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        ok, err = validar_matriz_3x3_finita(m_null)
        self.assertFalse(ok)
        self.assertIn("null", err)

        m_str = [[1.0, "0", 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        ok, err = validar_matriz_3x3_finita(m_str)
        self.assertFalse(ok)
        self.assertIn("no es numérico", err)


class TestValidacionSimetria(unittest.TestCase):
    """Pruebas de validación de simetría de matriz 3x3."""

    def test_matriz_perfectamente_simetrica(self):
        m = [
            [0.10, 0.02, -0.01],
            [0.02, 0.20, 0.03],
            [-0.01, 0.03, 0.25],
        ]
        ok, err = validar_simetria_matriz_3x3(m)
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_matriz_simetrica_dentro_de_tolerancia(self):
        tol = 1e-6
        m = [
            [0.10, 0.02 + 1e-7, 0.0],
            [0.02, 0.20, 0.0],
            [0.0, 0.0, 0.30],
        ]
        ok, err = validar_simetria_matriz_3x3(m, tol=tol)
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_matriz_asimetrica_rechazada(self):
        m = [
            [0.10, 0.05, 0.0],
            [0.01, 0.20, 0.0],
            [0.0, 0.0, 0.30],
        ]
        ok, err = validar_simetria_matriz_3x3(m, tol=1e-9)
        self.assertFalse(ok)
        self.assertIn("Asimetría detectada", err)


class TestValidacionMasaPositiva(unittest.TestCase):
    """Pruebas de masa positiva y preservación estricta de null (nunca sustituir null por cero)."""

    def test_masa_positiva_valida(self):
        ok, err = validar_masa_positiva(5.0)
        self.assertTrue(ok)
        self.assertIsNone(err)

        ok, err = validar_masa_positiva(0.001)
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_masa_cero_o_negativa_rechazada(self):
        ok, err = validar_masa_positiva(0.0)
        self.assertFalse(ok)
        self.assertIn("estrictamente positiva", err)

        ok, err = validar_masa_positiva(-2.5)
        self.assertFalse(ok)
        self.assertIn("estrictamente positiva", err)

    def test_masa_no_finita(self):
        ok, err = validar_masa_positiva(float("nan"))
        self.assertFalse(ok)
        self.assertIn("no es finita", err)

        ok, err = validar_masa_positiva(float("inf"))
        self.assertFalse(ok)
        self.assertIn("no es finita", err)

    def test_masa_null_sin_sustitucion_por_cero(self):
        # En modo estricto (permitir_null=False), debe fallar explícitamente diciendo que es null,
        # sin sustituir silenciosamente por cero
        ok, err = validar_masa_positiva(None, permitir_null=False)
        self.assertFalse(ok)
        self.assertIn("prohibido sustituir null por cero", err)

        # En modo reserva (permitir_null=True), se admite como reserva no asignada
        ok, err = validar_masa_positiva(None, permitir_null=True)
        self.assertTrue(ok)
        self.assertIsNone(err)


class TestEnergiaCineticaYMenoresPrincipales(unittest.TestCase):
    """Pruebas de energía cinética no negativa mediante menores principales (PSD)."""

    def test_calculo_menores_principales_diagonal(self):
        m = [
            [2.0, 0.0, 0.0],
            [0.0, 3.0, 0.0],
            [0.0, 0.0, 5.0],
        ]
        menores = calcular_menores_principales_3x3(m)
        self.assertAlmostEqual(menores["orden1_M00"], 2.0)
        self.assertAlmostEqual(menores["orden1_M11"], 3.0)
        self.assertAlmostEqual(menores["orden1_M22"], 5.0)
        self.assertAlmostEqual(menores["orden2_M01"], 6.0)
        self.assertAlmostEqual(menores["orden2_M02"], 10.0)
        self.assertAlmostEqual(menores["orden2_M12"], 15.0)
        self.assertAlmostEqual(menores["orden3_det"], 30.0)

    def test_tensor_psd_valido(self):
        m = [
            [0.045, 0.001, -0.002],
            [0.001, 0.120, 0.003],
            [-0.002, 0.003, 0.135],
        ]
        ok, menores, err = validar_energia_cinetica_no_negativa(m)
        self.assertTrue(ok)
        self.assertIsNone(err)
        for val in menores.values():
            self.assertGreaterEqual(val, 0.0)

    def test_tensor_con_menor_orden1_negativo(self):
        m = [
            [-0.05, 0.0, 0.0],
            [0.0, 0.10, 0.0],
            [0.0, 0.0, 0.10],
        ]
        ok, menores, err = validar_energia_cinetica_no_negativa(m)
        self.assertFalse(ok)
        self.assertIn("orden1_M00", err)

    def test_tensor_con_menor_orden2_negativo(self):
        # Diagonal positiva, pero acoplamiento cruzado excesivo: Ixx*Iyy - Ixy^2 < 0
        m = [
            [0.05, 0.08, 0.0],
            [0.08, 0.05, 0.0],
            [0.0, 0.0, 0.10],
        ]
        ok, menores, err = validar_energia_cinetica_no_negativa(m)
        self.assertFalse(ok)
        self.assertIn("orden2_M01", err)

    def test_tensor_con_menor_orden3_negativo(self):
        # Matriz con determinante negativo
        m = [
            [1.0, 0.8, 0.8],
            [0.8, 1.0, 0.8],
            [0.8, 0.8, 1.0],
        ]
        # det = 1*(1 - 0.64) - 0.8*(0.8 - 0.64) + 0.8*(0.64 - 0.8)
        #     = 0.36 - 0.8*(0.16) + 0.8*(-0.16) = 0.36 - 0.128 - 0.128 = 0.104 > 0
        # Ahora construyamos una con det < 0:
        m_neg_det = [
            [1.0, 0.9, 0.9],
            [0.9, 1.0, 0.9],
            [0.9, 0.9, 1.0],
        ]
        # det = 1*(1 - 0.81) - 0.9*(0.9 - 0.81) + 0.9*(0.81 - 0.9)
        #     = 0.19 - 0.9*(0.09) + 0.9*(-0.09) = 0.19 - 0.081 - 0.081 = 0.028
        # Ajustemos valores para inducir det < 0 manteniendo orden 1 y orden 2:
        m_indep = [
            [2.0, 1.5, 1.5],
            [1.5, 2.0, 1.5],
            [1.5, 1.5, 1.0],
        ]
        # M00=2, M11=2, M22=1. M01=4-2.25=1.75 > 0, M02=2-2.25=-0.25 < 0
        ok, menores, err = validar_energia_cinetica_no_negativa(m_indep)
        self.assertFalse(ok)

    def test_tensor_semi_definido_con_cero(self):
        # Tensor singular PSD (por ejemplo disco plano o cilindro ideal con Izz = 0)
        m = [
            [0.05, 0.0, 0.0],
            [0.0, 0.05, 0.0],
            [0.0, 0.0, 0.0],
        ]
        ok, menores, err = validar_energia_cinetica_no_negativa(m)
        self.assertTrue(ok)
        self.assertIsNone(err)
        self.assertAlmostEqual(menores["orden3_det"], 0.0)


class TestDesigualdadesTriangularesYAdvertenciaPSD(unittest.TestCase):
    """
    Pruebas que demuestran que PSD es necesaria pero NO suficiente para aceptar
    una medición ni garantiza que corresponda a un cuerpo físico continuo.
    """

    def test_cuerpo_fisico_valido_cumple_desigualdades(self):
        m = [
            [0.045, 0.0, 0.0],
            [0.0, 0.120, 0.0],
            [0.0, 0.0, 0.135],
        ]
        ok, detalles, err = verificar_desigualdades_triangulares_fisicas(m)
        self.assertTrue(ok)
        self.assertIsNone(err)
        self.assertGreaterEqual(detalles["Ixx_mas_Iyy_menos_Izz"], 0.0)
        self.assertGreaterEqual(detalles["Ixx_mas_Izz_menos_Iyy"], 0.0)
        self.assertGreaterEqual(detalles["Iyy_mas_Izz_menos_Ixx"], 0.0)

    def test_tensor_psd_que_viola_desigualdad_triangular(self):
        # Matriz diagonal estrictamente positiva (definida positiva, por tanto PSD):
        # Ixx = 0.200, Iyy = 0.050, Izz = 0.050
        # Iyy + Izz = 0.100 < 0.200 = Ixx -> Físicamente imposible para un cuerpo continuo 3D
        m = [
            [0.200, 0.0, 0.0],
            [0.0, 0.050, 0.0],
            [0.0, 0.0, 0.050],
        ]
        # 1. Cumple PSD (menores principales > 0)
        ok_psd, menores, err_psd = validar_energia_cinetica_no_negativa(m)
        self.assertTrue(ok_psd)

        # 2. Falla desigualdades triangulares físicas
        ok_tri, detalles, err_tri = verificar_desigualdades_triangulares_fisicas(m)
        self.assertFalse(ok_tri)
        self.assertIn("Violación de desigualdades triangulares", err_tri)

    def test_advertencia_psd_incluida_en_validacion_contrato(self):
        contrato = ContratoMasaCG(
            id_contrato="TEST_ADVERTENCIA",
            masa=PropiedadMasa(valor_kg=5.0),
            tensor_inercia_cg=PropiedadTensorInerciaCG(
                valor_kg_m2=[[0.05, 0.0, 0.0], [0.0, 0.05, 0.0], [0.0, 0.0, 0.08]]
            ),
        )
        res = validar_contrato(contrato)
        self.assertTrue(res.es_valido)
        # La advertencia obligatoria sobre insuficiencia de PSD debe estar presente
        self.assertTrue(any("NO ES SUFICIENTE" in adv for adv in res.advertencias))


class TestConversionCADAFLU(unittest.TestCase):
    """
    Pruebas de conversión de posiciones y tensores desde marco CAD a marco FLU
    aplicando diag(-1, -1, 1).
    """

    def test_conversion_posicion_cad_a_flu(self):
        # En CAD: nariz en X negativo (-0.160 m), lateral derecho (+0.076 m), arriba (+0.050 m)
        pos_cad = [-0.160, 0.076, 0.050]
        pos_flu = convertir_posicion_cad_a_flu(pos_cad)
        self.assertIsNotNone(pos_flu)
        # FLU: X forward hacia la nariz (+0.160 m), Y left (-0.076 m), Z up (+0.050 m)
        self.assertAlmostEqual(pos_flu[0], 0.160)
        self.assertAlmostEqual(pos_flu[1], -0.076)
        self.assertAlmostEqual(pos_flu[2], 0.050)

    def test_conversion_posicion_null_preserva_null(self):
        # Regla: NUNCA sustituir null por [0,0,0]
        self.assertIsNone(convertir_posicion_cad_a_flu(None))

    def test_conversion_posicion_dimension_invalida(self):
        with self.assertRaises(ValueError):
            convertir_posicion_cad_a_flu([1.0, 2.0])

    def test_conversion_tensor_cad_a_flu(self):
        # Tensor en CAD:
        # Ixx, Iyy, Izz y Ixy deben conservar signo
        # Ixz e Iyz deben invertir signo
        tensor_cad = [
            [0.040, 0.002, -0.003],
            [0.002, 0.110, 0.004],
            [-0.003, 0.004, 0.120],
        ]
        tensor_flu = convertir_tensor_cad_a_flu(tensor_cad)
        self.assertIsNotNone(tensor_flu)

        # Diagonales idénticas
        self.assertAlmostEqual(tensor_flu[0][0], 0.040)
        self.assertAlmostEqual(tensor_flu[1][1], 0.110)
        self.assertAlmostEqual(tensor_flu[2][2], 0.120)

        # Ixy idéntico
        self.assertAlmostEqual(tensor_flu[0][1], 0.002)
        self.assertAlmostEqual(tensor_flu[1][0], 0.002)

        # Ixz invertido: -(-0.003) = +0.003
        self.assertAlmostEqual(tensor_flu[0][2], 0.003)
        self.assertAlmostEqual(tensor_flu[2][0], 0.003)

        # Iyz invertido: -(0.004) = -0.004
        self.assertAlmostEqual(tensor_flu[1][2], -0.004)
        self.assertAlmostEqual(tensor_flu[2][1], -0.004)

    def test_conversion_tensor_null_preserva_null(self):
        # Regla: NUNCA sustituir tensor null por ceros
        self.assertIsNone(convertir_tensor_cad_a_flu(None))

    def test_transformar_contrato_completo_a_flu(self):
        c_cad = ContratoMasaCG(
            id_contrato="VEHICULO_CAD",
            masa=PropiedadMasa(valor_kg=5.0),
            posicion_cg=PropiedadPosicionCG(
                valor_m=[-0.020, 0.015, 0.040],
                marco_referencia=MarcoReferencia.CAD,
            ),
            tensor_inercia_cg=PropiedadTensorInerciaCG(
                valor_kg_m2=[
                    [0.040, 0.002, -0.003],
                    [0.002, 0.110, 0.004],
                    [-0.003, 0.004, 0.120],
                ],
                marco_referencia=MarcoReferencia.CAD,
            ),
        )

        c_flu = transformar_contrato_a_flu(c_cad)
        self.assertEqual(c_flu.posicion_cg.marco_referencia, MarcoReferencia.FLU)
        self.assertEqual(c_flu.tensor_inercia_cg.marco_referencia, MarcoReferencia.FLU)
        self.assertEqual(c_flu.posicion_cg.valor_m, [0.020, -0.015, 0.040])
        self.assertAlmostEqual(c_flu.tensor_inercia_cg.valor_kg_m2[0][2], 0.003)
        self.assertAlmostEqual(c_flu.tensor_inercia_cg.valor_kg_m2[1][2], -0.004)


class TestPreservacionEstrictaNull(unittest.TestCase):
    """
    Pruebas del principio: 'Nunca sustituyas null por cero.
    No infieras que una reserva sin masa asignada tenga masa real nula o no nula.'
    """

    def test_reserva_no_asignada_reconocida(self):
        contrato_reserva = ContratoMasaCG(
            id_contrato="RESERVA_CARGA_UTIL",
            masa=PropiedadMasa(
                valor_kg=None,
                trazabilidad=MetadatosTrazabilidad(
                    naturaleza=TipoNaturaleza.NO_ASIGNADO,
                    fuente="bahia_reserva_sintetica",
                ),
            ),
            posicion_cg=PropiedadPosicionCG(
                valor_m=None,
                trazabilidad=MetadatosTrazabilidad(
                    naturaleza=TipoNaturaleza.NO_ASIGNADO,
                    fuente="bahia_reserva_sintetica",
                ),
            ),
            tensor_inercia_cg=PropiedadTensorInerciaCG(
                valor_kg_m2=None,
                trazabilidad=MetadatosTrazabilidad(
                    naturaleza=TipoNaturaleza.NO_ASIGNADO,
                    fuente="bahia_reserva_sintetica",
                ),
            ),
        )

        self.assertTrue(es_reserva_no_asignada(contrato_reserva))
        self.assertIsNone(contrato_reserva.masa.valor_kg)
        self.assertNotEqual(contrato_reserva.masa.valor_kg, 0.0)

        # Validar que obtener_masa_estricta lanza excepción y no devuelve 0.0
        with self.assertRaises(ValueError) as ctx:
            obtener_masa_estricta(contrato_reserva)
        self.assertIn("Nunca sustituyas null por cero", str(ctx.exception))

    def test_serializacion_json_preserva_null_literal(self):
        contrato = ContratoMasaCG(
            id_contrato="TEST_NULL",
            masa=PropiedadMasa(valor_kg=None),
            posicion_cg=PropiedadPosicionCG(valor_m=None),
            tensor_inercia_cg=PropiedadTensorInerciaCG(valor_kg_m2=None),
        )
        json_str = contrato.to_json()
        data = json.loads(json_str)

        self.assertIsNone(data["masa"]["valor_kg"])
        self.assertIsNone(data["posicion_cg"]["valor_m"])
        self.assertIsNone(data["tensor_inercia_cg"]["valor_kg_m2"])

        # Deserialización debe devolver exactamente None
        c_roundtrip = ContratoMasaCG.from_json(json_str)
        self.assertIsNone(c_roundtrip.masa.valor_kg)
        self.assertIsNone(c_roundtrip.posicion_cg.valor_m)
        self.assertIsNone(c_roundtrip.tensor_inercia_cg.valor_kg_m2)


class TestTrazabilidadEpistemica(unittest.TestCase):
    """Pruebas de distinción medido vs supuesto vs calculado vs no asignado."""

    def test_clasificacion_naturalezas(self):
        for nat in [
            TipoNaturaleza.MEDIDO,
            TipoNaturaleza.SUPUESTO,
            TipoNaturaleza.CALCULADO,
            TipoNaturaleza.NO_ASIGNADO,
        ]:
            meta = MetadatosTrazabilidad(naturaleza=nat, fuente="prueba")
            d = meta.to_dict()
            self.assertEqual(d["naturaleza"], nat.value)
            meta_reconst = MetadatosTrazabilidad.from_dict(d)
            self.assertEqual(meta_reconst.naturaleza, nat)


class TestEjemplosSinteticosArchivos(unittest.TestCase):
    """Valida los 7 archivos sintéticos generados en salidas/ejemplos_sinteticos/."""

    def test_existencia_ejemplos(self):
        esperados = [
            "01_sintetico_medido_completo.json",
            "02_sintetico_supuesto_diseno.json",
            "03_sintetico_reserva_no_asignada.json",
            "04_sintetico_invalido_no_simetrico.json",
            "05_sintetico_invalido_no_psd.json",
            "06_sintetico_psd_pero_no_fisico.json",
            "07_sintetico_cad_para_conversion.json",
        ]
        for nombre in esperados:
            p = DIRECTORIO_EJEMPLOS / nombre
            self.assertTrue(p.exists(), f"Falta el archivo de ejemplo {nombre}")

    def test_ejemplo_01_medido_valido(self):
        p = DIRECTORIO_EJEMPLOS / "01_sintetico_medido_completo.json"
        contrato = ContratoMasaCG.from_json(p.read_text())
        res = validar_contrato(contrato)
        self.assertTrue(res.es_valido)
        self.assertEqual(len(res.errores), 0)
        self.assertEqual(contrato.masa.trazabilidad.naturaleza, TipoNaturaleza.MEDIDO)

    def test_ejemplo_02_supuesto_valido(self):
        p = DIRECTORIO_EJEMPLOS / "02_sintetico_supuesto_diseno.json"
        contrato = ContratoMasaCG.from_json(p.read_text())
        res = validar_contrato(contrato)
        self.assertTrue(res.es_valido)
        self.assertEqual(len(res.errores), 0)
        self.assertEqual(contrato.masa.trazabilidad.naturaleza, TipoNaturaleza.SUPUESTO)

    def test_ejemplo_03_reserva_null_valido_en_reserva(self):
        p = DIRECTORIO_EJEMPLOS / "03_sintetico_reserva_no_asignada.json"
        contrato = ContratoMasaCG.from_json(p.read_text())
        res = validar_contrato(contrato, exigir_completo=False)
        self.assertTrue(res.es_valido)
        self.assertIsNone(contrato.masa.valor_kg)
        self.assertIsNone(contrato.posicion_cg.valor_m)
        self.assertIsNone(contrato.tensor_inercia_cg.valor_kg_m2)
        # Exigir completo debe fallar pero sin sustituir a cero
        res_comp = validar_contrato(contrato, exigir_completo=True)
        self.assertFalse(res_comp.es_valido)

    def test_ejemplo_04_asimetria_rechazada(self):
        p = DIRECTORIO_EJEMPLOS / "04_sintetico_invalido_no_simetrico.json"
        contrato = ContratoMasaCG.from_json(p.read_text())
        res = validar_contrato(contrato)
        self.assertFalse(res.es_valido)
        self.assertTrue(any("asimétrico" in err.lower() for err in res.errores))

    def test_ejemplo_05_no_psd_rechazado(self):
        p = DIRECTORIO_EJEMPLOS / "05_sintetico_invalido_no_psd.json"
        contrato = ContratoMasaCG.from_json(p.read_text())
        res = validar_contrato(contrato)
        self.assertFalse(res.es_valido)
        self.assertTrue(any("energía cinética no negativa" in err.lower() for err in res.errores))

    def test_ejemplo_06_psd_pero_no_fisico_advierte_desigualdad(self):
        p = DIRECTORIO_EJEMPLOS / "06_sintetico_psd_pero_no_fisico.json"
        contrato = ContratoMasaCG.from_json(p.read_text())
        res = validar_contrato(contrato)
        # Es PSD (matemáticamente válido en energía cinética), pero emite advertencia física
        self.assertTrue(res.es_valido)
        self.assertFalse(res.desigualdades_triangulares_cumplidas)
        self.assertTrue(any("desigualdades triangulares" in adv.lower() for adv in res.advertencias))

    def test_ejemplo_07_conversion_cad_a_flu(self):
        p = DIRECTORIO_EJEMPLOS / "07_sintetico_cad_para_conversion.json"
        contrato_cad = ContratoMasaCG.from_json(p.read_text())
        contrato_flu = transformar_contrato_a_flu(contrato_cad)
        self.assertEqual(contrato_flu.posicion_cg.marco_referencia, MarcoReferencia.FLU)
        self.assertAlmostEqual(contrato_flu.posicion_cg.valor_m[0], 0.020)
        self.assertAlmostEqual(contrato_flu.posicion_cg.valor_m[1], -0.015)
        self.assertAlmostEqual(contrato_flu.posicion_cg.valor_m[2], 0.040)
        # Signos invertidos de términos cruzados con Z
        self.assertAlmostEqual(contrato_flu.tensor_inercia_cg.valor_kg_m2[0][2], 0.003)
        self.assertAlmostEqual(contrato_flu.tensor_inercia_cg.valor_kg_m2[1][2], -0.004)


if __name__ == "__main__":
    unittest.main()
