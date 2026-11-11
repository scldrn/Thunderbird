#!/usr/bin/env python3
"""
test_comprobaciones_centrifugas.py
==================================
Batería de pruebas unitarias y de verificación física para las comprobaciones
analíticas de escalado centrífugo, auditoría del rotor C02 y diferenciación
rigurosa entre anillo ideal y esfuerzo real de pala.

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
    uniform_blade_root_stress,
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
        # 60 rpm = 2 * pi rad/s = 6.2831853...
        self.assertAlmostEqual(rpm_to_rad_s(60.0), 2.0 * math.pi, places=7)
        self.assertAlmostEqual(rpm_to_rad_s(0.0), 0.0, places=7)
        # 3000 rpm = 100 * pi rad/s
        self.assertAlmostEqual(rpm_to_rad_s(3000.0), 100.0 * math.pi, places=7)

    def test_speed_of_sound_isa(self):
        # ISA nivel del mar: T0 = 288.15 K -> a0 = sqrt(1.4 * 287.05287 * 288.15) ~= 340.294 m/s
        a0 = speed_of_sound(T0_ISA_KELVIN)
        expected = math.sqrt(1.4 * 287.05287 * 288.15)
        self.assertAlmostEqual(a0, expected, places=5)
        self.assertTrue(340.28 < a0 < 340.31)

        # Temperatura negativa debe fallar
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

        # Ratio de velocidad periférica en hover (debe ser exactamente 0.80 = 1 / 1.25)
        self.assertAlmostEqual(v_tip_102 / v_tip, 0.80, places=6)

    def test_tip_mach_number(self):
        a0 = speed_of_sound(T0_ISA_KELVIN)
        # Hover D82
        v_tip_hover = tip_peripheral_velocity(46231.48148400444, 0.041)
        m_hover = tip_mach_number(v_tip_hover, a0)
        self.assertAlmostEqual(m_hover, 198.49526 / a0, places=4)
        self.assertTrue(0.58 < m_hover < 0.59)

        # Vertical +1g D82 (65375.7 rpm)
        v_tip_vert = tip_peripheral_velocity(65375.70291706148, 0.041)
        m_vert = tip_mach_number(v_tip_vert, a0)
        self.assertAlmostEqual(m_vert, 280.69087 / a0, places=4)
        # Mach transónico > 0.80
        self.assertTrue(m_vert > 0.82)

    def test_centrifugal_acceleration(self):
        # Aceleración en punta para D82 en hover: a_c = omega^2 * R
        omega = rpm_to_rad_s(46231.48148400444)
        ac = centrifugal_acceleration(46231.48148400444, 0.041)
        self.assertAlmostEqual(ac, (omega ** 2) * 0.041, places=3)
        # Representa más de 90.000 g en la punta
        g_units = ac / G0_M_S2
        self.assertTrue(g_units > 95000.0)


class TestCentrifugalLoads(unittest.TestCase):
    """Pruebas del modelo analítico de fuerza centrífuga radial."""

    def test_lumped_force_formula(self):
        # Masa 0.001 kg, r = 0.025 m, omega = 1000 rad/s -> F = 0.001 * 0.025 * 1e6 = 25.0 N
        f = centrifugal_radial_force(0.001, 0.025, 1000.0)
        self.assertAlmostEqual(f, 25.0, places=6)

    def test_omega_squared_proportionality(self):
        # La fuerza debe ser estrictamente proporcional a Omega^2
        m = 0.0005
        r = 0.030
        omega1 = 2000.0
        omega2 = 4000.0  # El doble
        f1 = centrifugal_radial_force(m, r, omega1)
        f2 = centrifugal_radial_force(m, r, omega2)
        # Al duplicar velocidad angular, la fuerza se cuadruplica
        self.assertAlmostEqual(f2 / f1, 4.0, places=7)

    def test_mass_and_radius_linearity(self):
        omega = 3000.0
        # Lineal respecto a masa
        f_m1 = centrifugal_radial_force(0.001, 0.02, omega)
        f_m2 = centrifugal_radial_force(0.002, 0.02, omega)
        self.assertAlmostEqual(f_m2 / f_m1, 2.0, places=7)
        # Lineal respecto a radio
        f_r1 = centrifugal_radial_force(0.001, 0.02, omega)
        f_r2 = centrifugal_radial_force(0.001, 0.04, omega)
        self.assertAlmostEqual(f_r2 / f_r1, 2.0, places=7)

    def test_analytical_uniform_beam(self):
        # Pala uniforme de 1 g entre r=10 mm y r=40 mm
        m = 0.001
        r0 = 0.010
        r1 = 0.040
        omega = 1500.0
        # r_cm = (10 + 40) / 2 = 25 mm = 0.025 m
        f_beam = analytical_uniform_blade_force(m, r0, r1, omega)
        f_lumped = centrifugal_radial_force(m, 0.025, omega)
        self.assertAlmostEqual(f_beam, f_lumped, places=7)

    def test_analytical_tapered_blade(self):
        # Pala ahusada con mu(r0) = 0.05 kg/m y mu(r1) = 0.01 kg/m
        r0 = 0.010
        r1 = 0.040
        omega = 2000.0
        f_taper, m_tot, r_cm = analytical_linearly_tapered_blade_force(0.05, 0.01, r0, r1, omega)
        # El centroide debe estar desplazado hacia la raíz respecto al punto medio (25 mm)
        self.assertTrue(r_cm < 0.025)
        # La fuerza calculada debe coincidir con m_tot * r_cm * omega^2
        f_check = centrifugal_radial_force(m_tot, r_cm, omega)
        self.assertAlmostEqual(f_taper, f_check, places=7)


class TestScalingLaws(unittest.TestCase):
    """Pruebas de leyes de escala analíticas entre D82 y D102,5."""

    def test_c01_speed_scaling_invariants(self):
        # Factor de escala geométrica lambda = 1.25
        # Escala de rpm en C01: rpm_102.5 = rpm_82 * (1 / 1.25^2) = rpm_82 * 0.64
        lambda_d = 1.25
        ratio_rpm = lambda_d ** -2  # 0.64
        ratio_vtip = ratio_rpm * lambda_d  # 0.64 * 1.25 = 0.80

        # Para geometría homóloga en 3D:
        # masa ~ lambda^3, r_cm ~ lambda
        # Fuerza F ~ masa * r_cm * omega^2 ~ (lambda^3) * (lambda) * (lambda^-2)^2 = lambda^4 * lambda^-4 = 1.00
        ratio_fuerza = (lambda_d ** 4) * (ratio_rpm ** 2)
        self.assertAlmostEqual(ratio_fuerza, 1.0, places=7)

        # Tensión axial sigma = F / Area
        # Area ~ lambda^2 -> sigma ~ 1.0 / lambda^2 = 0.64
        ratio_tension = ratio_fuerza / (lambda_d ** 2)
        self.assertAlmostEqual(ratio_tension, 0.64, places=7)

    def test_scaling_regimes_analysis(self):
        regimes = analyze_scaling_regimes()
        self.assertEqual(len(regimes), 3)

        # Régimen 1: C01
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
    Pruebas rigurosas de diferenciación entre el modelo de anillo ideal (hoop stress)
    y el esfuerzo real de pala de rotor con flexión no simétrica.
    """

    def test_ideal_ring_hoop_stress_formula(self):
        # rho = 1600 kg/m3, v = 200 m/s -> sigma = 1600 * 40000 = 64.0 MPa
        sigma = ideal_ring_hoop_stress(1600.0, 200.0)
        self.assertAlmostEqual(sigma, 64.0e6, places=1)

    def test_uniform_blade_root_stress_factor(self):
        # Para R_hub / R = 0.32:
        # sigma_uniform = 0.5 * rho * v^2 * (1 - 0.32^2) = 0.5 * 0.8976 * sigma_ring = 0.4488 * sigma_ring
        sigma_ring = ideal_ring_hoop_stress(1600.0, 200.0)
        sigma_blade = uniform_blade_root_stress(1600.0, 200.0, r_hub_over_R=0.32)
        ratio = sigma_blade / sigma_ring
        self.assertAlmostEqual(ratio, 0.4488, places=4)

    def test_c02_blade_bending_exceeds_ideal_ring(self):
        # En D82 Hover (rho = 1600 kg/m3, v_tip = 198.495 m/s):
        # sigma_anillo = 1600 * 198.495^2 = 63.04 MPa
        # sigma_axial_media = 41.85 MPa (0.66x del anillo)
        # sigma_normal_max (flexion real) = 116.75 MPa (1.85x del anillo!)
        v_tip = tip_peripheral_velocity(46231.48148400444, 0.041)
        comp = compare_ideal_ring_vs_real_blade(
            density_kg_m3=1600.0,
            tip_speed_m_s=v_tip,
            mean_axial_cad_pa=41.8535856e6,
            max_normal_cad_pa=116.75e6,
            r_hub_over_R=0.32
        )
        # El anillo sobreestima la tracción axial pura
        self.assertTrue(comp["ratio_cad_axial_to_ring"] < 0.70)
        # Pero el anillo SUBESTIMA severamente la tensión máxima real (por un factor de casi 2)
        self.assertTrue(comp["ratio_cad_max_to_ring"] > 1.80)
        self.assertAlmostEqual(comp["amplification_cad_bending"], 2.7895, places=3)

    def test_danger_of_ideal_ring_equating(self):
        # Si un ingeniero equiparara el esfuerzo de la pala con el anillo ideal:
        # A 65375.7 rpm (ascenso +1g, D82), v_tip = 280.69 m/s:
        # sigma_anillo = 126.1 MPa
        # Sin embargo, el esfuerzo real en la pala es 233.5 MPa!
        # La subestimación de tensión máxima es de (233.5 - 126.1) / 233.5 = 46%
        v_tip = tip_peripheral_velocity(65375.70291706148, 0.041)
        sigma_ring = ideal_ring_hoop_stress(1600.0, v_tip) / 1e6
        sigma_real_max = 233.46
        underestimation_pct = (sigma_real_max - sigma_ring) / sigma_real_max * 100.0
        self.assertTrue(underestimation_pct > 45.0)


class TestPreviousScreeningAudit(unittest.TestCase):
    """Pruebas de auditoría sobre las copias de referencia."""

    @classmethod
    def setUpClass(cls):
        root_dir = Path(__file__).resolve().parent.parent
        cls.json_path = root_dir / "entradas" / "investigacion-aeronautica" / "ejecucion" / "G5" / "rotor_C02" / "RESULTADOS.json"
        # RotorAuditor carga RESULTADOS.json si existe, o genera el dataset certificado si no existe
        cls.auditor = RotorAuditor(cls.json_path)

    def test_results_count_and_schema(self):
        self.assertEqual(len(self.auditor.results), 144)
        self.assertEqual(len(self.auditor.sections), 16)
        self.assertFalse(self.auditor.metadata.get("physical_stress_validation_accepted", True))

    def test_geometric_invariants_numerical_precision(self):
        invariants = self.auditor.verify_geometric_integral_invariance()
        self.assertEqual(len(invariants), 16)  # 2 rotores x 8 estaciones
        for key, data in invariants.items():
            spread = data["relative_numerical_spread"]
            self.assertTrue(spread < 1e-12, f"Dispersión numérica anómala {spread} en {key}")

    def test_similarity_pairs_consistency(self):
        sim = self.auditor.verify_similarity_pairs()
        self.assertEqual(sim["total_pairs"], 72)
        # Ratio de fuerza F(102.5)/F(82) = 1.000000 estricto
        self.assertAlmostEqual(sim["force_ratio_min"], 1.0, places=5)
        self.assertAlmostEqual(sim["force_ratio_max"], 1.0, places=5)
        # Ratio de tensión en rango [0.6399, 0.6400]
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
        # En demanda vertical +1g (65375.7 rpm), D82 alcanza Mach 0.825
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
        delta_r_elastic = (sigma_pa / e_modulus_pa) * length_m  # 0.135 mm
        fraction_clearance = delta_r_elastic / clearance_m
        self.assertTrue(fraction_clearance > 0.25)


if __name__ == "__main__":
    unittest.main()
