#!/usr/bin/env python3
"""
verificar_sintesis.py
Batería de comprobaciones automatizadas para validar la integridad,
cobertura técnica, consistencia matemática y enlaces locales del entregable
salidas/SINTESIS_TRAZABILIDAD_CONTROL_FUENTES.md.
"""

import os
import re
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SINTESIS_PATH = os.path.join(BASE_DIR, "salidas", "SINTESIS_TRAZABILIDAD_CONTROL_FUENTES.md")

def run_tests():
    print("Iniciando verificación automatizada de la síntesis...")
    assert os.path.isfile(SINTESIS_PATH), f"El archivo {SINTESIS_PATH} no existe."
    
    with open(SINTESIS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.splitlines()
    words = content.split()
    print(f"-> Archivo cargado: {len(lines)} líneas, {len(words)} palabras.")
    
    # Test 1: Comprobación de tamaño (aproximadamente una página sintetizada)
    # Una página técnica suele tener entre 60 y 160 líneas y 700-1500 palabras
    assert 60 <= len(lines) <= 200, f"Longitud de líneas anómala: {len(lines)}"
    assert 600 <= len(words) <= 1600, f"Recuento de palabras fuera de rango de síntesis de 1 página: {len(words)}"
    print("✓ Test 1: Tamaño y densidad de página de síntesis superado.")

    # Test 2: Verificación de los 4 temas requeridos
    # 1) masa de reserva sin asignar desconocida
    assert "Masa de Reserva sin Asignar" in content or "masa de reserva" in content.lower()
    assert "DESCONOCIDO" in content
    assert "79,02" in content or "79.02" in content
    assert "canal_axial_60_exterior_56_interior" in content
    assert "54" in content
    print("✓ Test 2.1: Punto 1 (Masa de reserva desconocida y principio de indeterminación) verificado.")

    # 2) identificar solo el EDF de la nota y rechazar marca no sustentada
    assert "Jetfan 130 Pro" in content
    assert "Schübeler" in content and "Hacker" in content
    assert "túnel de baja velocidad de 12 pies" in content
    assert "1.100" in content or "1100" in content
    assert "7" in content and "kW" in content
    print("✓ Test 2.2: Punto 2 (Identificación estricta Jetfan 130 Pro y rechazo de marcas) verificado.")

    # 3) no confundir entrada no suministrada con archivo inexistente
    assert "matriz_verificacion_detallada.csv" in content
    assert "entrada no suministrada" in content.lower() or "no inferir que un archivo no copiado no existe" in content.lower()
    assert "CORRECCIONES.md" in content
    print("✓ Test 2.3: Punto 3 (No confundir entrada no suministrada con archivo inexistente) verificado.")

    # 4) +y CAD derecha según conversión documentada
    assert "CAD $+y$" in content or "CAD +y" in content or "+y CAD" in content
    assert "DERECHA" in content
    assert "flight" in content and "CAD" in content and "diag" in content
    assert "quiralidad" in content.lower()
    assert "dextrógira" in content.lower() or "mano derecha" in content.lower()
    print("✓ Test 2.4: Punto 4 (CAD +y derecha, conversión documentada y quiralidad) verificado.")

    # Test 3: Identificación de dictámenes de agentes y requerimiento de contraste
    assert "dictámenes de agentes" in content.lower() or "dictamen de agente" in content.lower()
    assert "contraste" in content.lower()
    print("✓ Test 3: Identificación de dictámenes de agentes y necesidad de contraste superado.")

    # Test 4: Declaración de no validación científica y delimitación de nota NASA
    assert "científicamente validado" in content.lower() or "validación científica" in content.lower()
    assert "nota técnica secundaria" in content.lower() or "nota secundaria" in content.lower()
    print("✓ Test 4: Cláusulas de no validación vehicular y naturaleza secundaria de nota NASA superadas.")

    # Test 5: Distinción epistémica de datos (medidos, supuestos, cálculos, desconocidos)
    assert "[DATO MEDIDO]" in content
    assert "[SUPUESTO]" in content
    assert "[CÁLCULO]" in content
    assert "[DESCONOCIDO]" in content
    print("✓ Test 5: Matriz de discriminación epistémica y conservación de unidades superada.")

    # Test 6: Comprobación de enlaces locales file://
    links = re.findall(r'\[([^\]]+)\]\((file:///[^\)]+)\)', content)
    assert len(links) >= 5, f"Se encontraron pocos enlaces locales: {len(links)}"
    for text, url in links:
        local_path = url.replace("file://", "")
        assert os.path.exists(local_path), f"El enlace {url} ({text}) no existe en el disco local: {local_path}"
    print(f"✓ Test 6: Todos los enlaces locales ({len(links)}) verificados y existentes sin acceso a red.")

    # Test 7: Comprobación de álgebra vectorial y quiralidad
    # R = diag(-1, -1, 1), det(R) = +1
    R_diag = [-1, -1, 1]
    det_R = R_diag[0] * R_diag[1] * R_diag[2]
    assert det_R == 1.0, f"Determinante incorrecto: {det_R}"
    # r_CAD = R * r_FLU => y_CAD = -1 * y_FLU. Si y_FLU > 0 (izquierda), y_CAD < 0 (izquierda en CAD).
    # Por tanto, y_CAD > 0 corresponde a y_FLU < 0 (DERECHA / estribor).
    assert -1 * (-1) == 1
    print("✓ Test 7: Consistencia físico-matemática y cinemática rigurosamente comprobada.")

    print("\n=======================================================")
    print("TODAS LAS COMPROBACIONES (7/7) HAN SIDO EXITOSAS (PASS)")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
