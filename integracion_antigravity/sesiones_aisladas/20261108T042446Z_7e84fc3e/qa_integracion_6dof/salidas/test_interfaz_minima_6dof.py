"""
test_interfaz_minima_6dof.py
============================
Suite de pruebas unitarias automatizadas para la interfaz mínima de integración 6-DOF.
Valida transformación de ejes, transporte de momentos, dinámica de Euler 3x3,
separación epistémica y consistencia energética.
"""

import math
import unittest
from salidas.interfaz_minima_6dof import (
    MarcoReferencia,
    NaturalezaEpistemica,
    SalidaMecanicaVentilador,
    EntradaElectricaVentilador,
    PropiedadesInercialesVehiculo,
    transformar_vector_cad_a_flu,
    transformar_vector_flu_a_cad,
    transformar_tensor_cad_a_flu,
    producto_vectorial,
    transportar_momento_a_cg,
    combinar_propulsion_en_cg,
    determinante_3x3,
    invertir_matriz_3x3,
    multiplicar_matriz_vector_3x3,
    calcular_aceleracion_angular_euler,
    derivada_cuaternion,
    rotar_vector_por_cuaternion,
    evaluar_rhs_6dof,
    comprobar_consistencia_energetica,
)
import sys
from pathlib import Path

# Configurar rutas para interoperabilidad con contratos de referencia
_BASE_ENTRADAS = Path(__file__).resolve().parent.parent / "entradas" / "investigacion-aeronautica" / "integracion_antigravity" / "sesiones_aisladas" / "20261108T041236Z_b586a83a"
if str(_BASE_ENTRADAS / "contrato_mapa_instalado" / "salidas") not in sys.path:
    sys.path.append(str(_BASE_ENTRADAS / "contrato_mapa_instalado" / "salidas"))
if str(_BASE_ENTRADAS / "contrato_masa_cg" / "salidas") not in sys.path:
    sys.path.append(str(_BASE_ENTRADAS / "contrato_masa_cg" / "salidas"))

try:
    import contrato_mapa_ventilador as cmv
    import contrato as cmc
    CONTRATOS_DISPONIBLES = True
except ImportError:
    CONTRATOS_DISPONIBLES = False



class TestTransformacionEjes(unittest.TestCase):
    """Pruebas de cambio de base entre marcos CAD y FLU."""

    def test_rotacion_vector_cad_a_flu(self):
        # CAD: Nariz en -X => FLU: Nariz en +X
        v_cad = [-0.16, -0.076, 0.05]
        v_flu = transformar_vector_cad_a_flu(v_cad)
        self.assertAlmostEqual(v_flu[0], 0.16)
        self.assertAlmostEqual(v_flu[1], 0.076)
        self.assertAlmostEqual(v_flu[2], 0.05)

    def test_involucion_transformacion_vector(self):
        # Dado que R = diag(-1, -1, 1), R * R = I
        v_orig = [1.25, -3.4, 7.8]
        v_flu = transformar_vector_cad_a_flu(v_orig)
        v_cad = transformar_vector_flu_a_cad(v_flu)
        self.assertAlmostEqual(v_cad[0], v_orig[0])
        self.assertAlmostEqual(v_cad[1], v_orig[1])
        self.assertAlmostEqual(v_cad[2], v_orig[2])

    def test_rechazo_vectores_invalidos(self):
        with self.assertRaises(ValueError):
            transformar_vector_cad_a_flu([1.0, 2.0])
        with self.assertRaises(ValueError):
            transformar_vector_cad_a_flu([1.0, float("nan"), 3.0])

    def test_transformacion_tensor_cad_a_flu(self):
        # I_FLU = R * I_CAD * R^T
        # Diagonal y xy permanecen invariantes; xz y yz invierten signo
        I_cad = [
            [0.05, 0.002, 0.003],
            [0.002, 0.06, -0.004],
            [0.003, -0.004, 0.08],
        ]
        I_flu = transformar_tensor_cad_a_flu(I_cad)
        self.assertAlmostEqual(I_flu[0][0], 0.05)
        self.assertAlmostEqual(I_flu[1][1], 0.06)
        self.assertAlmostEqual(I_flu[2][2], 0.08)
        self.assertAlmostEqual(I_flu[0][1], 0.002)
        self.assertAlmostEqual(I_flu[1][0], 0.002)
        # Cambio de signo en acoplamientos con Z
        self.assertAlmostEqual(I_flu[0][2], -0.003)
        self.assertAlmostEqual(I_flu[2][0], -0.003)
        self.assertAlmostEqual(I_flu[1][2], 0.004)
        self.assertAlmostEqual(I_flu[2][1], 0.004)


class TestTransporteMomentos(unittest.TestCase):
    """Pruebas de combinación de momento local M_app y brazo r x F."""

    def test_momento_puro_sin_brazo(self):
        # r_app == r_cg => brazo es nulo, solo queda M_app
        fuerza = [0.0, 0.0, 10.0]
        m_app = [0.1, -0.2, 0.3]
        r_app = [0.0, 0.0, 0.0]
        r_cg = [0.0, 0.0, 0.0]
        m_cg = transportar_momento_a_cg(fuerza, m_app, r_app, r_cg)
        self.assertEqual(m_cg, m_app)

    def test_fuerza_pura_con_brazo(self):
        # M_app nulo, brazo puro r = [0.2, 0.0, 0.0], F = [0, 0, 10]
        # r x F = [0, -0.2*10, 0] = [0, -2.0, 0]
        fuerza = [0.0, 0.0, 10.0]
        m_app = [0.0, 0.0, 0.0]
        r_app = [0.2, 0.0, 0.0]
        r_cg = [0.0, 0.0, 0.0]
        m_cg = transportar_momento_a_cg(fuerza, m_app, r_app, r_cg)
        self.assertAlmostEqual(m_cg[0], 0.0)
        self.assertAlmostEqual(m_cg[1], -2.0)
        self.assertAlmostEqual(m_cg[2], 0.0)

    def test_superposicion_completa(self):
        # M_app = [0.5, 0.0, -0.1]
        # r_app = [0.2, 0.1, 0.0], r_cg = [0.0, 0.0, 0.0] => r = [0.2, 0.1, 0.0]
        # F = [0, 0, 10]
        # r x F = [0.1*10, -0.2*10, 0] = [1.0, -2.0, 0.0]
        # M_cg = [0.5 + 1.0, 0.0 - 2.0, -0.1 + 0] = [1.5, -2.0, -0.1]
        m_cg = transportar_momento_a_cg(
            fuerza_N=[0.0, 0.0, 10.0],
            momento_app_Nm=[0.5, 0.0, -0.1],
            r_app_m=[0.2, 0.1, 0.0],
            r_cg_m=[0.0, 0.0, 0.0],
        )
        self.assertAlmostEqual(m_cg[0], 1.5)
        self.assertAlmostEqual(m_cg[1], -2.0)
        self.assertAlmostEqual(m_cg[2], -0.1)

    def test_combinar_propulsion_cuatro_ventiladores(self):
        # Configuración simétrica C02 en FLU:
        # F1: [+0.16, +0.076, 0.0], par CCW (+Q_z)
        # F2: [+0.16, -0.076, 0.0], par CW  (-Q_z)
        # F3: [-0.16, +0.076, 0.0], par CW  (-Q_z)
        # F4: [-0.16, -0.076, 0.0], par CCW (+Q_z)
        posiciones = [
            [0.16, 0.076, 0.0],
            [0.16, -0.076, 0.0],
            [-0.16, 0.076, 0.0],
            [-0.16, -0.076, 0.0],
        ]
        q_rotor = 0.05  # N*m
        salidas = [
            SalidaMecanicaVentilador(fuerza_vectorial_N=(0.0, 0.0, 10.0), momento_vectorial_Nm=(0.0, 0.0, q_rotor)),
            SalidaMecanicaVentilador(fuerza_vectorial_N=(0.0, 0.0, 10.0), momento_vectorial_Nm=(0.0, 0.0, -q_rotor)),
            SalidaMecanicaVentilador(fuerza_vectorial_N=(0.0, 0.0, 10.0), momento_vectorial_Nm=(0.0, 0.0, -q_rotor)),
            SalidaMecanicaVentilador(fuerza_vectorial_N=(0.0, 0.0, 10.0), momento_vectorial_Nm=(0.0, 0.0, q_rotor)),
        ]
        r_cg = [0.0, 0.0, 0.0]
        f_tot, m_tot = combinar_propulsion_en_cg(salidas, posiciones, r_cg)

        # Fuerza vertical total = 40 N
        self.assertAlmostEqual(f_tot[2], 40.0)
        self.assertAlmostEqual(f_tot[0], 0.0)
        self.assertAlmostEqual(f_tot[1], 0.0)

        # Momento total en Z debe anularse por balance de pares CCW/CW
        self.assertAlmostEqual(m_tot[2], 0.0)
        # Por simetría de empujes iguales, roll y pitch también son nulos
        self.assertAlmostEqual(m_tot[0], 0.0)
        self.assertAlmostEqual(m_tot[1], 0.0)


class TestAlgebraMatricialYDinamicaRotacional(unittest.TestCase):
    """Pruebas de inversión 3x3 y ecuación de Euler con tensor completo."""

    def test_inversion_matriz_3x3(self):
        mat = [
            [2.0, 0.1, 0.0],
            [0.1, 3.0, 0.2],
            [0.0, 0.2, 4.0],
        ]
        inv = invertir_matriz_3x3(mat)
        # Comprobar mat * inv == I
        for i in range(3):
            for j in range(3):
                val = sum(mat[i][k] * inv[k][j] for k in range(3))
                expected = 1.0 if i == j else 0.0
                self.assertAlmostEqual(val, expected, places=10)

    def test_aceleracion_angular_diagonal(self):
        # Para matriz diagonal, coincide con (tau - w x Iw) / I
        I_diag = [
            [0.1, 0.0, 0.0],
            [0.0, 0.2, 0.0],
            [0.0, 0.0, 0.3],
        ]
        omega = [1.0, 2.0, 0.5]
        torque = [0.5, -0.4, 0.2]
        # w x (I*w) = [1, 2, 0.5] x [0.1, 0.4, 0.15]
        # = [ 2*0.15 - 0.5*0.4, 0.5*0.1 - 1*0.15, 1*0.4 - 2*0.1 ]
        # = [ 0.30 - 0.20, 0.05 - 0.15, 0.40 - 0.20 ] = [ 0.10, -0.10, 0.20 ]
        # rhs = torque - w x Iw = [0.5 - 0.1, -0.4 - (-0.1), 0.2 - 0.2] = [0.4, -0.3, 0.0]
        # dw/dt = [0.4/0.1, -0.3/0.2, 0.0/0.3] = [4.0, -1.5, 0.0]
        alpha = calcular_aceleracion_angular_euler(I_diag, omega, torque)
        self.assertAlmostEqual(alpha[0], 4.0)
        self.assertAlmostEqual(alpha[1], -1.5)
        self.assertAlmostEqual(alpha[2], 0.0)

    def test_aceleracion_angular_tensor_acoplado(self):
        # Tensor no diagonal con productos de inercia
        I_acoplado = [
            [0.10, 0.01, 0.0],
            [0.01, 0.20, 0.0],
            [0.00, 0.00, 0.30],
        ]
        omega = [0.0, 0.0, 0.0]
        torque = [1.0, 0.0, 0.0]
        alpha = calcular_aceleracion_angular_euler(I_acoplado, omega, torque)
        # Como I_xy != 0, alpha_y != 0 aunque torque_y == 0
        self.assertNotEqual(alpha[1], 0.0)


class TestRHS6DOF(unittest.TestCase):
    """Prueba de integración del lado derecho 6-DOF (RHS)."""

    def test_evaluacion_rhs_completa(self):
        prop = PropiedadesInercialesVehiculo(
            masa_kg=5.0,
            posicion_cg_m=(0.0, 0.0, 0.0),
            tensor_inercia_cg_kgm2=(
                (0.05, 0.001, 0.0),
                (0.001, 0.05, 0.0),
                (0.0, 0.0, 0.08),
            ),
            marco=MarcoReferencia.FLU,
            naturaleza_masa=NaturalezaEpistemica.MEDIDO,
            naturaleza_inercia=NaturalezaEpistemica.CALCULADO,
            fuente="banco_sintetico_01",
        )
        # Cuatro ventiladores sustentando el peso (5 kg * 9.80665 m/s^2 = 49.03325 N => ~12.26 N c/u)
        f_z = 5.0 * 9.80665 / 4.0
        salidas = [
            SalidaMecanicaVentilador(fuerza_vectorial_N=(0.0, 0.0, f_z), momento_vectorial_Nm=(0.0, 0.0, 0.02)),
            SalidaMecanicaVentilador(fuerza_vectorial_N=(0.0, 0.0, f_z), momento_vectorial_Nm=(0.0, 0.0, -0.02)),
            SalidaMecanicaVentilador(fuerza_vectorial_N=(0.0, 0.0, f_z), momento_vectorial_Nm=(0.0, 0.0, -0.02)),
            SalidaMecanicaVentilador(fuerza_vectorial_N=(0.0, 0.0, f_z), momento_vectorial_Nm=(0.0, 0.0, 0.02)),
        ]
        posiciones = [
            [0.16, 0.076, 0.0],
            [0.16, -0.076, 0.0],
            [-0.16, 0.076, 0.0],
            [-0.16, -0.076, 0.0],
        ]
        # Estado en reposo, cuaternión identidad [0, 0, 0, 1]
        estado = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
        ydot = evaluar_rhs_6dof(
            estado_13=estado,
            prop_inerciales=prop,
            salidas_ventiladores=salidas,
            posiciones_fans_m=posiciones,
        )

        self.assertEqual(len(ydot), 13)
        # Velocidades lineales = 0
        self.assertAlmostEqual(ydot[0], 0.0)
        self.assertAlmostEqual(ydot[1], 0.0)
        self.assertAlmostEqual(ydot[2], 0.0)
        # Aceleraciones lineales = 0 (en equilibrio gravitatorio)
        self.assertAlmostEqual(ydot[3], 0.0)
        self.assertAlmostEqual(ydot[4], 0.0)
        self.assertAlmostEqual(ydot[5], 0.0, places=5)
        # Aceleración angular = 0 (pares balanceados)
        self.assertAlmostEqual(ydot[10], 0.0)
        self.assertAlmostEqual(ydot[11], 0.0)
        self.assertAlmostEqual(ydot[12], 0.0)


class TestConsistenciaEnergeticaYDatosFaltantes(unittest.TestCase):
    """Pruebas de distinción mecánica vs eléctrica y conservación de energía."""

    def test_operacion_nominal_consistente(self):
        mec = SalidaMecanicaVentilador(
            fuerza_vectorial_N=(0.0, 0.0, 12.0),
            momento_vectorial_Nm=(0.0, 0.0, 0.03),
            potencia_mecanica_W=240.0,
        )
        elec = EntradaElectricaVentilador(
            potencia_electrica_W=300.0,
            voltaje_bus_V=24.0,
            corriente_A=12.5,
        )
        res = comprobar_consistencia_energetica(mec, elec)
        self.assertTrue(res["valido"])
        self.assertEqual(res["estado"], "CONSISTENTE")
        self.assertAlmostEqual(res["eficiencia"], 0.8)

    def test_violacion_termodinamica_potencia_mecanica_mayor(self):
        mec = SalidaMecanicaVentilador(
            fuerza_vectorial_N=(0.0, 0.0, 12.0),
            momento_vectorial_Nm=(0.0, 0.0, 0.03),
            potencia_mecanica_W=350.0,
        )
        elec = EntradaElectricaVentilador(
            potencia_electrica_W=300.0,
        )
        res = comprobar_consistencia_energetica(mec, elec)
        self.assertFalse(res["valido"])
        self.assertEqual(res["estado"], "VIOLACION_TERMODINAMICA")

    def test_potencia_electrica_cero_con_mecanica_positiva(self):
        mec = SalidaMecanicaVentilador(
            fuerza_vectorial_N=(0.0, 0.0, 5.0),
            momento_vectorial_Nm=(0.0, 0.0, 0.01),
            potencia_mecanica_W=50.0,
        )
        elec = EntradaElectricaVentilador(
            potencia_electrica_W=0.0,
        )
        res = comprobar_consistencia_energetica(mec, elec)
        self.assertFalse(res["valido"])
        self.assertEqual(res["estado"], "VIOLACION_TERMODINAMICA")

    def test_preservacion_estricta_de_faltantes_sin_coercion_a_cero(self):
        # Si la potencia eléctrica no fue medida, se mantiene None y no se convierte a 0.0
        mec = SalidaMecanicaVentilador(
            fuerza_vectorial_N=(0.0, 0.0, 12.0),
            momento_vectorial_Nm=(0.0, 0.0, 0.03),
            potencia_mecanica_W=240.0,
        )
        elec = EntradaElectricaVentilador(
            potencia_electrica_W=None,  # NO MEDIDO
        )
        res = comprobar_consistencia_energetica(mec, elec)
        self.assertTrue(res["valido"])
        self.assertEqual(res["estado"], "ELECTRICA_NO_DISPONIBLE")
        self.assertIsNone(res["eficiencia"])
        self.assertIsNone(elec.potencia_electrica_W)
        self.assertNotEqual(elec.potencia_electrica_W, 0.0)


if __name__ == "__main__":
    unittest.main()
