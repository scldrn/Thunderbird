"""
Módulo de conversiones metrológicas y comparación trazable entre Nota NASA EDF y Candidato C02.

Fuentes documentales:
- Nota NASA: entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md
  (Referencia primaria: Weinstein et al., NASA/AIAA 2024, NTRS 20230017299; no se dispone del PDF completo en sesión)
- Informe C02: entradas/investigacion-aeronautica/ejecucion/G3/C02/INFORME-C02.md
"""

from decimal import Decimal, ROUND_HALF_UP
import csv
import os

# Constantes metrológicas internacionales exactas
# 1 pulgada = 25.4 mm (Acuerdo Internacional de la Yarda y la Libra de 1959)
MM_PER_INCH = Decimal("25.4")

# 1 libra avoirdupois = 0.45359237 kg (Acuerdo Internacional de 1959)
KG_PER_LB = Decimal("0.45359237")

# Aceleración normal de la gravedad (3ª CGPM, 1901) g0 = 9.80665 m/s^2
G0 = Decimal("9.80665")

# 1 lbf = 0.45359237 * 9.80665 N = 4.4482216152605 N (exacto por definición)
N_PER_LBF = KG_PER_LB * G0


def inches_to_mm(inches: float, precision: int = None) -> float:
    """Convierte pulgadas a milímetros usando el factor exacto 25.4 mm/in."""
    val = Decimal(str(inches)) * MM_PER_INCH
    if precision is not None:
        return float(val.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP))
    return float(val)


def lbf_to_newtons(lbf: float, precision: int = None) -> float:
    """Convierte libras-fuerza a Newtons usando la definición internacional estándar."""
    val = Decimal(str(lbf)) * N_PER_LBF
    if precision is not None:
        return float(val.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP))
    return float(val)


def mm_to_inches(mm: float, precision: int = None) -> float:
    """Convierte milímetros a pulgadas."""
    val = Decimal(str(mm)) / MM_PER_INCH
    if precision is not None:
        return float(val.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP))
    return float(val)


def newtons_to_lbf(newtons: float, precision: int = None) -> float:
    """Convierte Newtons a libras-fuerza."""
    val = Decimal(str(newtons)) / N_PER_LBF
    if precision is not None:
        return float(val.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP))
    return float(val)


def get_comparison_data():
    """
    Retorna la estructura de datos comparativa con clasificación rigurosa:
    - Dato medido en túnel / banco
    - Especificación nominal / catálogo
    - Dimensión geométrica CAD
    - Requisito / Demanda calculada
    - Hipótesis / Supuesto de cálculo
    """
    # Conversiones clave
    pala_nasa_in = 5.11
    pala_nasa_mm = inches_to_mm(pala_nasa_in)

    ducto_ext_nasa_in = 5.23
    ducto_ext_nasa_mm = inches_to_mm(ducto_ext_nasa_in)

    empuje_max_nasa_lbf = 21.25
    empuje_max_nasa_n = lbf_to_newtons(empuje_max_nasa_lbf)

    rows = [
        {
            "Parametro": "Diámetro de pala / rotor",
            "NASA_Jetfan_130_Pro": f"{pala_nasa_in} in ({pala_nasa_mm:.3f} mm)",
            "C02_D82": "82,0 mm (R41 mm nominal; contención R41,5 mm)",
            "C02_D102_5": "102,5 mm nominal",
            "Tipo_Dato_NASA": "Dato de informe / catálogo (Tabla 1)",
            "Tipo_Dato_C02": "Dimensión geométrica CAD / modelo conceptual",
            "Fuente_NASA": "NOTA-NASA-EDF.md (Tabla 1; ref. Weinstein et al. 2024)",
            "Fuente_C02": "INFORME-C02.md (Sección 'Resultado materializado' y Tabla compromiso)",
            "Observaciones_Trazabilidad": "NASA es 58,3% mayor en diámetro que C02 D82 (área 2,50x superior). Diferente escala fluidodinámica."
        },
        {
            "Parametro": "Diámetro exterior de conducto",
            "NASA_Jetfan_130_Pro": f"{ducto_ext_nasa_in} in ({ducto_ext_nasa_mm:.3f} mm)",
            "C02_D82": "Taladro R42 mm (Ø84,0 mm interior; separación radial nominal 0,5 mm)",
            "C02_D102_5": "No especificado conducto final",
            "Tipo_Dato_NASA": "Dato de informe (Tabla 1)",
            "Tipo_Dato_C02": "Dimensión geométrica CAD",
            "Fuente_NASA": "NOTA-NASA-EDF.md (Tabla 1)",
            "Fuente_C02": "INFORME-C02.md (Sección 'Comprobado geométricamente')",
            "Observaciones_Trazabilidad": "NASA ensayado aislado en túnel 12 ft. C02 integrado en fuselaje cuádruple con tapas."
        },
        {
            "Parametro": "Diámetro de motor",
            "NASA_Jetfan_130_Pro": "56,0 mm",
            "C02_D82": "Reserva cilíndrica Ø21,8 mm (longitud 16,1 mm)",
            "C02_D102_5": "Reserva cilíndrica Ø27,5 mm (longitud 19,35 mm)",
            "Tipo_Dato_NASA": "Especificación de motor ensayado (Tabla 2)",
            "Tipo_Dato_C02": "Reserva volumétrica CAD vacía (no es motor seleccionado)",
            "Fuente_NASA": "NOTA-NASA-EDF.md (Tabla 2)",
            "Fuente_C02": "INFORME-C02.md (Tabla 'Requisitos de motor')",
            "Observaciones_Trazabilidad": "EL MOTOR NASA NO CABE EN C02: Ø56 mm supera por 2,57x la reserva de D82 y por 2,04x la de D102,5."
        },
        {
            "Parametro": "Masa del motor",
            "NASA_Jetfan_130_Pro": "1.100 g (1,10 kg)",
            "C02_D82": "Sin hardware asignado (registro vacío en BOM geométrica)",
            "C02_D102_5": "Sin hardware asignado (registro vacío en BOM geométrica)",
            "Tipo_Dato_NASA": "Especificación de catálogo de motor (Tabla 2)",
            "Tipo_Dato_C02": "Volumen reservado vacío (54 registros sin hardware)",
            "Fuente_NASA": "NOTA-NASA-EDF.md (Tabla 2)",
            "Fuente_C02": "INFORME-C02.md (Sección 'Masa e inercia')",
            "Observaciones_Trazabilidad": "4 motores NASA pesarían 4,40 kg, consumiendo el 88% de la masa total objetivo de C02 (5,0 kg)."
        },
        {
            "Parametro": "Masa global de referencia",
            "NASA_Jetfan_130_Pro": "No reportada masa total del conjunto en nota",
            "C02_D82": "Objetivo vehículo 5,0 kg. Masa geométrica: 2,046 kg (ligera), 2,784 kg (mixta), 4,421 kg (aluminio)",
            "C02_D102_5": "Evaluado en compromiso de envolvente para vehículo 5,0 kg",
            "Tipo_Dato_NASA": "Dato ausente en nota copiada (requiere PDF completo)",
            "Tipo_Dato_C02": "Hipótesis de densidad y cálculo adaptativo sobre CAD (316 piezas)",
            "Fuente_NASA": "NOTA-NASA-EDF.md (Sección final)",
            "Fuente_C02": "INFORME-C02.md (Tabla 'Masa e inercia')",
            "Observaciones_Trazabilidad": "C02 evalúa masa estructural + margen equipos (0,75 kg reserva provisional). Excluye 54 reservas."
        },
        {
            "Parametro": "Número de álabes / estatores",
            "NASA_Jetfan_130_Pro": "10 palas rotor, 7 álabes fijos (estatores)",
            "C02_D82": "Módulo cinemático con 4 filas, 3 álabes por fila sincronizados",
            "C02_D102_5": "Módulo cinemático similar",
            "Tipo_Dato_NASA": "Dato descriptivo de geometría ensayada",
            "Tipo_Dato_C02": "Definición cinemática y geométrica CAD",
            "Fuente_NASA": "NOTA-NASA-EDF.md (Líneas 8-9)",
            "Fuente_C02": "INFORME-C02.md (Secciones 'Comprobado geométricamente' y 'Qué cambió')",
            "Observaciones_Trazabilidad": "Arquitecturas completamente distintas: EDF convencional (NASA) vs rotor con álabes sincronizados/vectorización."
        },
        {
            "Parametro": "Empuje estático reportado",
            "NASA_Jetfan_130_Pro": f"Rango 0 a {empuje_max_nasa_lbf} lbf (0 a {empuje_max_nasa_n:.2f} N)",
            "C02_D82": "Requisito de diseño: ~12,26 N/módulo para estacionario de vehículo 5 kg (total ~49,03 N)",
            "C02_D102_5": "Requisito similar para estacionario de 5 kg",
            "Tipo_Dato_NASA": "Dato medido en túnel de viento (extremo de envolvente Tabla 6)",
            "Tipo_Dato_C02": "Cálculo de demanda de diseño (C01/A07 estacionario)",
            "Fuente_NASA": "NOTA-NASA-EDF.md (Tabla 6)",
            "Fuente_C02": "INFORME-C02.md (Sección 'Requisitos de motor')",
            "Observaciones_Trazabilidad": "Extremos del conjunto de pruebas; NO se asumen medidos en un mismo punto ni coincidentes. Curva no escalable a C02."
        },
        {
            "Parametro": "Potencia reportada",
            "NASA_Jetfan_130_Pro": "Rango 190 a 6.420 W (eléctrica DC suministrada al conjunto)",
            "C02_D82": "Demanda de cálculo: 668 W en eje por módulo (+ 74,2 W pérdida motor+ESC supuesta)",
            "C02_D102_5": "Demanda de cálculo: 534 W en eje por módulo (+ 59,4 W pérdida motor+ESC supuesta)",
            "Tipo_Dato_NASA": "Dato medido en banco/túnel (eléctrica DC, Tabla 6)",
            "Tipo_Dato_C02": "Demanda de diseño calculada de escenario C01 estacionario",
            "Fuente_NASA": "NOTA-NASA-EDF.md (Tablas 5 y 6)",
            "Fuente_C02": "INFORME-C02.md (Tabla 'Requisitos de motor')",
            "Observaciones_Trazabilidad": "NASA midió potencia eléctrica total DC. C02 expresa potencia mecánica de eje requerida más pérdidas supuestas."
        },
        {
            "Parametro": "Régimen de giro (RPM)",
            "NASA_Jetfan_130_Pro": "2.875 a 25.150 rpm",
            "C02_D82": "46.231 rpm (cálculo de punto estacionario)",
            "C02_D102_5": "29.588 rpm (cálculo de punto estacionario)",
            "Tipo_Dato_NASA": "Dato medido / rango ensayado (Tabla 6)",
            "Tipo_Dato_C02": "Cálculo de punto de diseño BEM/estacionario C01",
            "Fuente_NASA": "NOTA-NASA-EDF.md (Tabla 6)",
            "Fuente_C02": "INFORME-C02.md (Tabla 'Requisitos de motor')",
            "Observaciones_Trazabilidad": "C02 D82 opera a un régimen casi el doble del máximo de NASA Jetfan 130 debido a su menor diámetro."
        },
        {
            "Parametro": "Potencia nominal continua de motor",
            "NASA_Jetfan_130_Pro": "7 kW (7.000 W) nominal continua",
            "C02_D82": "No hay motor seleccionado (demanda de eje 668 W/módulo, 4 módulos = 2.672 W eje total)",
            "C02_D102_5": "No hay motor seleccionado (demanda de eje 534 W/módulo, 4 módulos = 2.136 W eje total)",
            "Tipo_Dato_NASA": "Especificación de motor (Tabla 2)",
            "Tipo_Dato_C02": "Requisito de cálculo, sin hardware comercial asignado",
            "Fuente_NASA": "NOTA-NASA-EDF.md (Tabla 2)",
            "Fuente_C02": "INFORME-C02.md (Sección 'Requisitos de motor')",
            "Observaciones_Trazabilidad": "La unidad NASA es un motor sobredimensionado para túnel aerodinámico (1,1 kg, 7 kW); ajeno a C02."
        }
    ]
    return rows


def generate_csv_table(output_path: str):
    """Genera la tabla comparativa en formato CSV trazable."""
    data = get_comparison_data()
    fieldnames = [
        "Parametro",
        "NASA_Jetfan_130_Pro",
        "C02_D82",
        "C02_D102_5",
        "Tipo_Dato_NASA",
        "Tipo_Dato_C02",
        "Fuente_NASA",
        "Fuente_C02",
        "Observaciones_Trazabilidad"
    ]
    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def generate_markdown_table(output_path: str):
    """Genera la tabla comparativa en formato Markdown estructurado."""
    data = get_comparison_data()
    headers = [
        "Parámetro",
        "NASA Jetfan 130 Pro",
        "C02 (D82)",
        "C02 (D102,5)",
        "Naturaleza de Datos (NASA / C02)",
        "Observaciones de Trazabilidad"
    ]
    md = []
    md.append("| " + " | ".join(headers) + " |")
    md.append("|" + "|".join(["---" for _ in headers]) + "|")
    for row in data:
        nat = f"**NASA:** {row['Tipo_Dato_NASA']} ({row['Fuente_NASA']})<br>**C02:** {row['Tipo_Dato_C02']} ({row['Fuente_C02']})"
        line = f"| **{row['Parametro']}** | {row['NASA_Jetfan_130_Pro']} | {row['C02_D82']} | {row['C02_D102_5']} | {nat} | {row['Observaciones_Trazabilidad']} |"
        md.append(line)

    with open(output_path, mode="w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def check_motor_fit():
    """
    Verifica matemáticamente si el motor de la nota NASA cabe en los alojamientos de C02.
    Retorna diccionario con resultados dimensionales y de masa.
    """
    nasa_motor_diam = 56.0  # mm
    nasa_motor_mass = 1100.0  # g
    c02_d82_cavity_diam = 21.8  # mm
    c02_d82_cavity_len = 16.1  # mm
    c02_d102_cavity_diam = 27.5  # mm
    c02_d102_cavity_len = 19.35  # mm
    c02_veh_mass_target = 5000.0  # g (5 kg total)

    fits_d82 = (nasa_motor_diam <= c02_d82_cavity_diam)
    fits_d102 = (nasa_motor_diam <= c02_d102_cavity_diam)
    
    diam_ratio_d82 = nasa_motor_diam / c02_d82_cavity_diam
    diam_ratio_d102 = nasa_motor_diam / c02_d102_cavity_diam
    
    mass_4_motors = 4 * nasa_motor_mass
    mass_fraction_veh = mass_4_motors / c02_veh_mass_target

    return {
        "nasa_motor_diam_mm": nasa_motor_diam,
        "nasa_motor_mass_g": nasa_motor_mass,
        "c02_d82_cavity_diam_mm": c02_d82_cavity_diam,
        "c02_d102_cavity_diam_mm": c02_d102_cavity_diam,
        "fits_d82": fits_d82,
        "fits_d102": fits_d102,
        "diam_ratio_d82": diam_ratio_d82,
        "diam_ratio_d102": diam_ratio_d102,
        "mass_4_motors_g": mass_4_motors,
        "mass_fraction_veh": mass_fraction_veh
    }


def main():
    print("=== SCRIPT DE CONVERSIONES METROLÓGICAS Y TRAZABILIDAD ===")
    
    # 1. Conversión de 5.11 pulgadas a mm
    pulgadas_test = 5.11
    mm_result_exact = inches_to_mm(pulgadas_test)
    mm_result_rounded = inches_to_mm(pulgadas_test, 3)
    print(f"1. Conversión de longitud:")
    print(f"   Entrada: {pulgadas_test} in")
    print(f"   Factor: 1 in = 25.4 mm (exacto)")
    print(f"   Resultado exacto: {mm_result_exact} mm")
    print(f"   Resultado redondeado: {mm_result_rounded} mm\n")

    # 2. Conversión de 21.25 lbf a N
    lbf_test = 21.25
    n_result_exact = lbf_to_newtons(lbf_test)
    n_result_rounded = lbf_to_newtons(lbf_test, 4)
    print(f"2. Conversión de fuerza:")
    print(f"   Entrada: {lbf_test} lbf")
    print(f"   Factor: 1 lbf = 0.45359237 kg * 9.80665 m/s^2 = {float(N_PER_LBF)} N")
    print(f"   Resultado exacto: {n_result_exact} N")
    print(f"   Resultado redondeado: {n_result_rounded} N\n")

    # 3. Comprobación de interferencia de motor
    fit = check_motor_fit()
    print("3. Comprobación geométrica y de masa del motor NASA vs reservas C02:")
    print(f"   Motor NASA: Ø{fit['nasa_motor_diam_mm']} mm, masa {fit['nasa_motor_mass_g']} g")
    print(f"   Reserva C02 D82: Ø{fit['c02_d82_cavity_diam_mm']} mm -> Cabe: {fit['fits_d82']} (Exceso diametral: {fit['diam_ratio_d82']:.2f}x)")
    print(f"   Reserva C02 D102,5: Ø{fit['c02_d102_cavity_diam_mm']} mm -> Cabe: {fit['fits_d102']} (Exceso diametral: {fit['diam_ratio_d102']:.2f}x)")
    print(f"   Masa de 4 motores NASA: {fit['mass_4_motors_g']/1000:.2f} kg ({fit['mass_fraction_veh']*100:.1f}% de los 5 kg del vehículo C02)")
    print("   CONCLUSIÓN OBLIGATORIA: El motor NASA NO cabe en C02 ni dimensional ni masivamente.\n")

    # 4. Generación de tablas
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "tabla_comparativa.csv")
    md_path = os.path.join(base_dir, "tabla_comparativa.md")
    
    generate_csv_table(csv_path)
    print(f"Tabla CSV generada en: {csv_path}")
    generate_markdown_table(md_path)
    print(f"Tabla Markdown generada en: {md_path}")


if __name__ == "__main__":
    main()
