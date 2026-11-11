#!/usr/bin/env python3
"""
test_comprobaciones_centrifugas.py
==================================
Batería de pruebas unitarias y de verificación física para las comprobaciones
analíticas de escalado centrífugo, auditoría del rotor C02 y contraste
entre anillo ideal y esfuerzo de pala real.

Ejecutable mediante:
    python3 -m unittest salidas/test_comprobaciones_centrifugas.py
"""

import unittest
import math
from pathlib import Path

# Importar funciones y clases desde comprobaciones_centrifugas.py
from salidas.comprobaciones_centrifugas import (
    rpm_to_rad_s,
    speed_of_sound,
    tip_peripheral_velocity,
    tip_mach_number,
    centrifugal_acceleration,
    centrifugal_radial_force,
    analytical_uniform_blade_force,
    analytical_linearly_tapered_blade_force,
    ideal_ring_hoop_stress,
    uniform_blade_axial_stress,
    compare_ideal_ring_vs_real_blade,
    RotorAuditor,
    analyze_scaling_regimes,
    ROTOR_CONFIGS,
    OPERATING_SCENARIOS,
    T0_ISA_KELVIN,
    GAMMA_AIR,
    R_SPECIFIC_AIR,
    G0_M_S2,
)


class TestKinematicsAndAero(unittest.TestCase):
    """Pruebas de cinemática rotatoria y cálculo aerodinámico de punta."""

    def test_rpm_to_rad_s(self):
        self.assertAlmostEqual(rpm_to_rad_s(60.0), 2.0 * math.pi, places=7)
        self.assertAlmostEqual(rpm_to_rad_s(0.0), 0.0, places=7)
        self.assertAlmostEqual(rpm_to_rad_s(3000.0), 100.0 * math.pi, places=7)

    def test_speed_of_sound_isa(self):
        a0 = speed_of_sound(T0_ISA_KELVIN)
        expected = math.sqrt(1.4 * 287.05287 * 288.15)
        self.assertAlmostEqual(a0, expected, places=5)
        self.assertTrue(340.28 < a0 < 340.31)

        with self.assertRaises(ValueError):
            speed_of_sound(-10.0)

    def test_tip_peripheral_velocity(self):
        # D82: R = 0.041 m, 46231.48 rpm
        rpm = 46231.48148400444
        r = 0.041
        v_tip = tip_peripheral_velocity(rpm, r)
        expected_omega = rpm * math.pi / 30.0
        expected_vtip = expected_omega * r
        self.assertAlmostEqual(v_tip, expected_vtip, places=5)
        self.assertAlmostEqual(v_tip, 198.49526, places=3)

        # D102.5: R = 0.05125 m, 29588.15 rpm
        rpm_102 = 29588.148149762844
        r_102 = 0.05125
        v_tip_102 = tip_peripheral_velocity(rpm_102, r_102)
        self.assertAlmostEqual(v_tip_102, 158.79621, places=3)

        # Ratio de velocidad periférica en hover (debe ser 0.80 = 1 / 1.25)
        self.assertAlmostEqual(v_tip_102 / v_tip, 0.80, places=6)

    def test_tip_mach_number(self):
        a0 = speed_of_sound(T0_ISA_KELVIN)
        v_tip_hover = tip_peripheral_velocity(46231.48148400444, 0.041)
        m_hover = tip_mach_number(v_tip_hover, a0)
        self.assertAlmostEqual(m_hover, 198.49526 / a0, places=4)
        self.assertTrue(0.58 < m_hover < 0.59)

        # Demanda vertical +1g D82 (65375.7 rpm)
        v_tip_vert = tip_peripheral_velocity(65375.70291706148, 0.041)
        m_vert = tip_mach_number(v_tip_vert, a0)
        self.assertAlmostEqual(m_vert, 280.69087 / a0, places=4)
        self.assertTrue(m_vert > 0.82)

    def test_centrifugal_acceleration(self):
        omega = rpm_to_rad_s(46231.48148400444)
        ac = centrifugal_acceleration(46231.48148400444, 0.041)
        self.assertAlmostEqual(ac, (omega ** 2) * 0.041, places=3)
        g_units = ac / G0_M_S2
        self.assertTrue(g_units > 95000.0)


class TestCentrifugalLoads(unittest.TestCase):
    """Pruebas del modelo analítico de fuerza centrífuga radial."""

    def test_lumped_force_formula(self):
        f = centrifugal_radial_force(0.001, 0.025, 1000.0)
        self.assertAlmostEqual(f, 25.0, places=6)

    def test_omega_squared_proportionality(self):
        m = 0.0005
        r = 0.030
        omega1 = 2000.0
        omega2 = 4000.0
        f1 = centrifugal_radial_force(m, r, omega1)
        f2 = centrifugal_radial_force(m, r, omega2)
        self.assertAlmostEqual(f2 / f1, 4.0, places=7)

    def test_mass_and_radius_linearity(self):
        omega = 3000.0
        f_m1 = centrifugal_radial_force(0.001, 0.02, omega)
        f_m2 = centrifugal_radial_force(0.002, 0.02, omega)
        self.assertAlmostEqual(f_m2 / f_m1, 2.0, places=7)

        f_r1 = centrifugal_radial_force(0.001, 0.02, omega)
        f_r2 = centrifugal_radial_force(0.001, 0.04, omega)
        self.assertAlmostEqual(f_r2 / f_r1, 2.0, places=7)

    def test_analytical_uniform_beam(self):
        m = 0.001
        r0 = 0.010
        r1 = 0.040
        omega = 1500.0
        f_beam = analytical_uniform_blade_force(m, r0, r1, omega)
        f_lumped = centrifugal_radial_force(m, 0.025, omega)
        self.assertAlmostEqual(f_beam, f_lumped, places=7)

    def test_analytical_tapered_blade(self):
        r0 = 0.010
        r1 = 0.040
        omega = 2000.0
        f_taper, m_tot, r_cm = analytical_linearly_tapered_blade_force(0.05, 0.01, r0, r1, omega)
        self.assertTrue(r_cm < 0.025)
        f_check = centrifugal_radial_force(m_tot, r_cm, omega)
        self.assertAlmostEqual(f_taper, f_check, places=7)


class TestScalingLaws(unittest.TestCase):
    """Pruebas de leyes de escala analíticas entre D82 y D102,5."""

    def test_c01_speed_scaling_invariants(self):
        lambda_d = 1.25
        ratio_rpm = lambda_d ** -2
        ratio_fuerza = (lambda_d ** 4) * (ratio_rpm ** 2)
        self.assertAlmostEqual(ratio_fuerza, 1.0, places=7)

        ratio_tension = ratio_fuerza / (lambda_d ** 2)
        self.assertAlmostEqual(ratio_tension, 0.64, places=7)

    def test_scaling_regimes_analysis(self):
        regimes = analyze_scaling_regimes()
        self.assertEqual(len(regimes), 3)

        # Régimen 1: C01 (empuje constante)
        reg1 = regimes[0]
        self.assertAlmostEqual(reg1["ratio_rpm"], 0.64, places=5)
        self.assertAlmostEqual(reg1["ratio_vtip"], 0.80, places=5)
        self.assertAlmostEqual(reg1["ratio_fuerza_rad"], 1.00, places=5)
        self.assertAlmostEqual(reg1["ratio_tension_media"], 0.64, places=5)

        # Régimen 2: v_tip constante
        reg2 = regimes[1]
        self.assertAlmostEqual(reg2["ratio_rpm"], 0.80, places=5)
        self.assertAlmostEqual(reg2["ratio_vtip"], 1.00, places=5)
        self.assertAlmostEqual(reg2["ratio_fuerza_rad"], 1.5625, places=4)
        self.assertAlmostEqual(reg2["ratio_tension_media"], 1.00, places=5)

        # Régimen 3: rpm constante
        reg3 = regimes[2]
        self.assertAlmostEqual(reg3["ratio_rpm"], 1.00, places=5)
        self.assertAlmostEqual(reg3["ratio_vtip"], 1.25, places=5)
        self.assertAlmostEqual(reg3["ratio_fuerza_rad"], 2.44140625, places=4)
        self.assertAlmostEqual(reg3["ratio_tension_media"], 1.5625, places=4)


class TestIdealRingVsRealBlade(unittest.TestCase):
    """
    Pruebas de contraste físico y dimensional:
    Anillo ideal delgado (sigma = rho * v^2) vs Pala real en voladizo con flexión.
    """

    def test_ideal_ring_formula(self):
        rho = 1600.0
        v_tip = 200.0
        # sigma = rho * v^2 = 1600 * 40000 = 64.0 MPa
        sigma_ring = ideal_ring_hoop_stress(rho, v_tip)
        self.assertAlmostEqual(sigma_ring / 1e6, 64.0, places=5)

    def test_uniform_blade_formula(self):
        rho = 1600.0
        v_tip = 200.0
        r_root = 0.01353  # x/R = 0.33 para R = 41 mm
        r_tip = 0.041
        sigma_unif = uniform_blade_axial_stress(rho, v_tip, r_root, r_tip)
        expected = 0.5 * rho * (v_tip ** 2) * (1.0 - (0.33 ** 2))
        self.assertAlmostEqual(sigma_unif, expected, places=3)
        # La tensión en la raíz de una pala uniforme es menor que la del anillo ideal
        self.assertTrue(sigma_unif < ideal_ring_hoop_stress(rho, v_tip))

    def test_blade_bending_amplification_exceeds_ring(self):
        """
        Comprueba que, a pesar de que la tensión axial media es menor que la del anillo,
        la flexión no simétrica en una pala real eleva la tensión máxima por encima del anillo.
        """
        # Datos D82 Hover (rho = 1600)
        v_tip = 198.49526
        rho = 1600.0
        r_root = 0.01353
        r_tip = 0.041
        real_mean = 41.85e6
        real_max = 116.75e6

        comp = compare_ideal_ring_vs_real_blade(v_tip, rho, r_root, r_tip, real_mean, real_max)

        # 1. El anillo da 63.04 MPa
        self.assertAlmostEqual(comp["sigma_ring_MPa"], 63.04, places=1)

        # 2. La tensión media real (41.85 MPa) es MENOR que la del anillo (63.04 MPa)
        self.assertTrue(comp["sigma_blade_mean_real_MPa"] < comp["sigma_ring_MPa"])

        # 3. La tensión máxima real con flexión (116.75 MPa) es MAYOR que la del anillo
        self.assertTrue(comp["sigma_blade_max_real_MPa"] > comp["sigma_ring_MPa"])
        self.assertAlmostEqual(comp["ratio_blade_max_over_ring"], 1.85, places=1)

        # 4. Amplificación por flexión casi triplica la axial pura (2.79x)
        self.assertAlmostEqual(comp["ratio_bending_amplification"], 2.79, places=1)


class TestPreviousScreeningAudit(unittest.TestCase):
    """Pruebas de auditoría sobre el conjunto de datos de referencia (real o benchmark)."""

    @classmethod
    def setUpClass(cls):
        root_dir = Path(__file__).resolve().parent.parent
        cls.json_path = root_dir / "entradas" / "investigacion-aeronautica" / "ejecucion" / "G5" / "rotor_C02" / "RESULTADOS.json"
        cls.auditor = RotorAuditor(cls.json_path)

    def test_results_count_and_schema(self):
        self.assertEqual(len(self.auditor.results), 144)
        self.assertEqual(len(self.auditor.sections), 16)
        self.assertFalse(self.auditor.metadata.get("physical_stress_validation_accepted", True))

    def test_geometric_invariants_numerical_precision(self):
        invariants = self.auditor.verify_geometric_integral_invariance()
        self.assertEqual(len(invariants), 16)
        for key, data in invariants.items():
            spread = data["relative_numerical_spread"]
            self.assertTrue(spread < 1e-12, f"Dispersión anómala {spread} en {key}")

    def test_similarity_pairs_consistency(self):
        sim = self.auditor.verify_similarity_pairs()
        self.assertEqual(sim["total_pairs"], 72)
        self.assertAlmostEqual(sim["force_ratio_min"], 1.0, places=5)
        self.assertAlmostEqual(sim["force_ratio_max"], 1.0, places=5)
        self.assertTrue(sim["stress_ratio_min"] >= 0.63990)
        self.assertTrue(sim["stress_ratio_max"] <= 0.64001)

    def test_bending_amplification_at_root(self):
        hover_d82_1600 = [
            r for r in self.auditor.results
            if r["diameter_factor"] == 1.0
            and abs(r["x_over_R"] - 0.33) < 1e-4
            and r["operating_scenario"] == "hover"
            and abs(r["density_ASSUMED_kg_m3"] - 1600.0) < 1e-4
        ][0]
        sigma_mean = hover_d82_1600["mean_axial_Pa"]
        sigma_max = hover_d82_1600["sampled_abs_normal_max_Pa"]
        amplif = sigma_max / sigma_mean
        self.assertTrue(2.78 < amplif < 2.80)


class TestEngineeringBoundaries(unittest.TestCase):
    """Pruebas de límites físicos, aerodinámicos y holguras mecánicas."""

    def test_transonic_tip_mach_warning(self):
        v_tip = tip_peripheral_velocity(65375.70291706148, 0.041)
        a0 = speed_of_sound(T0_ISA_KELVIN)
        m_tip = tip_mach_number(v_tip, a0)
        self.assertTrue(m_tip > 0.80)

        a_cold = speed_of_sound(273.15)
        m_tip_cold = tip_mach_number(v_tip, a_cold)
        self.assertTrue(m_tip_cold > 0.84)

    def test_radial_clearance_fraction_consumed(self):
        clearance_m = 0.0005
        sigma_pa = 50e6
        length_m = 0.027
        e_modulus_pa = 10e9
        delta_r_elastic = (sigma_pa / e_modulus_pa) * length_m
        fraction_clearance = delta_r_elastic / clearance_m
        self.assertTrue(fraction_clearance > 0.25)


if __name__ == "__main__":
    unittest.main()
