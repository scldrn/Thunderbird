#!/usr/bin/env python3
"""
extraccion_areas_secciones.py
=============================
Herramienta de extracción y cálculo verificable de propiedades geométricas
transversales de la envolvente aerodinámica A07 (referencia 5 kg) a partir
de las estaciones paramétricas definidas en `crear_A07.py`.

Calcula de forma exacta mediante la biblioteca estándar de Python:
- Vértices del polígono exterior de 10 lados y del polígono interior desplazado (inset).
- Área transversal exterior e interior (fórmula de Shoelace / Gauss).
- Perímetro mojado.
- Centroide transversal (Ycg, Zcg), evidenciando la asimetría/curvatura vertical.
- Anchura total (2w) y altura total (1.78h), así como relación de aspecto W/H.
- Diámetro y radio equivalente de Whitcomb para la regla de las áreas.
- Integración longitudinal del volumen por tramos prismoidales/trapezoidales.

Salida: Guarda el resultado estructurado en `salidas/AREAS_TRANSVERSALES_A07.json`.
"""

import math
import json
from pathlib import Path

# Definición canónica de las 8 estaciones de sección de crear_A07.py (línea 15)
# Cada tupla representa: (x_station_mm, half_width_w_mm, half_height_h_mm)
SECTIONS_A07 = [
    (-680, 7, 6),
    (-580, 58, 36),
    (-400, 127, 80),
    (-140, 160, 107),
    (160, 150, 103),
    (400, 112, 78),
    (570, 63, 47),
    (660, 25, 25)
]

def get_outer_polygon_vertices(w, h):
    """
    Genera los 10 vértices del contorno exterior en el plano YZ (crear_A07.py, línea 18).
    Ordenación antihoraria (CCW).
    """
    w = float(w)
    h = float(h)
    return [
        (w, 0.0),
        (0.79 * w, 0.67 * h),
        (0.37 * w, h),
        (-0.37 * w, h),
        (-0.79 * w, 0.67 * h),
        (-w, 0.0),
        (-0.75 * w, -0.62 * h),
        (-0.32 * w, -0.78 * h),
        (0.32 * w, -0.78 * h),
        (0.75 * w, -0.62 * h)
    ]

def solve_2x2(a11, a12, a21, a22, b1, b2):
    """Resuelve un sistema de 2 ecuaciones con 2 incógnitas."""
    det = a11 * a22 - a12 * a21
    if abs(det) < 1e-12:
        return None
    return (b1 * a22 - b2 * a12) / det, (a11 * b2 - a21 * b1) / det

def get_inset_polygon_vertices(w, h):
    """
    Calcula los 10 vértices del contorno desplazado d mm hacia el interior,
    según la formulación exacta de crear_A07.py (líneas 19-21).
    d = min(2.0, min(w, h) * 0.38)
    """
    yz = get_outer_polygon_vertices(w, h)
    n_pts = len(yz)
    normals = []
    for i in range(n_pts):
        p1 = yz[i]
        p2 = yz[(i + 1) % n_pts]
        dy = p2[0] - p1[0]
        dz = p2[1] - p1[1]
        length = math.hypot(dy, dz)
        # Normal hacia el interior (a la izquierda del vector borde en recorrido CCW)
        ny = -dz / length
        nz = dy / length
        normals.append((ny, nz))
    
    d = min(2.0, min(w, h) * 0.38)
    inset_pts = []
    for i in range(n_pts):
        n_prev = normals[(i - 1) % n_pts]
        n_curr = normals[i]
        b1 = n_prev[0] * yz[i][0] + n_prev[1] * yz[i][1] + d
        b2 = n_curr[0] * yz[i][0] + n_curr[1] * yz[i][1] + d
        pt = solve_2x2(n_prev[0], n_prev[1], n_curr[0], n_curr[1], b1, b2)
        inset_pts.append(pt)
    return inset_pts, d

def polygon_area(pts):
    """Calcula el área de un polígono 2D mediante la fórmula del agrimensor (Shoelace)."""
    n = len(pts)
    a = 0.0
    for i in range(n):
        j = (i + 1) % n
        a += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
    return abs(a) * 0.5

def polygon_perimeter(pts):
    """Calcula el perímetro sumando las longitudes euclidianas de los bordes."""
    p = 0.0
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        p += math.hypot(pts[j][0] - pts[i][0], pts[j][1] - pts[i][1])
    return p

def polygon_centroid(pts):
    """Calcula el centroide geométrico (Ycg, Zcg) del polígono cerrado."""
    n = len(pts)
    a2 = 0.0
    cy = 0.0
    cz = 0.0
    for i in range(n):
        j = (i + 1) % n
        cross = pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
        a2 += cross
        cy += (pts[i][0] + pts[j][0]) * cross
        cz += (pts[i][1] + pts[j][1]) * cross
    a = a2 * 0.5
    if abs(a) < 1e-12:
        return 0.0, 0.0
    return cy / (6.0 * a), cz / (6.0 * a)

def main():
    stations_output = []
    total_len = SECTIONS_A07[-1][0] - SECTIONS_A07[0][0]
    
    for x, w, h in SECTIONS_A07:
        outer_pts = get_outer_polygon_vertices(w, h)
        inset_pts, d_offset = get_inset_polygon_vertices(w, h)
        
        a_outer = polygon_area(outer_pts)
        a_inset = polygon_area(inset_pts)
        p_outer = polygon_perimeter(outer_pts)
        p_inset = polygon_perimeter(inset_pts)
        
        cy_out, cz_out = polygon_centroid(outer_pts)
        cy_in, cz_in = polygon_centroid(inset_pts)
        
        width = 2.0 * w
        h_top = float(h)
        h_bottom = -0.78 * h
        h_tot = h_top - h_bottom
        aspect_ratio = width / h_tot if h_tot > 0 else 0.0
        
        # Diámetro equivalente de Whitcomb
        d_equiv = 2.0 * math.sqrt(a_outer / math.pi)
        
        stations_output.append({
            "estacion_x_mm": x,
            "semi_ancho_w_mm": w,
            "semi_alto_h_mm": h,
            "ancho_total_mm": width,
            "alto_total_mm": round(h_tot, 3),
            "relacion_aspecto_W_H": round(aspect_ratio, 3),
            "area_exterior_mm2": round(a_outer, 2),
            "area_exterior_cm2": round(a_outer / 100.0, 2),
            "area_exterior_m2": round(a_outer / 1e6, 6),
            "perimetro_exterior_mm": round(p_outer, 2),
            "centroide_exterior_y_mm": round(cy_out, 3),
            "centroide_exterior_z_mm": round(cz_out, 3),
            "diametro_equivalente_mm": round(d_equiv, 2),
            "offset_recorte_d_mm": round(d_offset, 3),
            "area_interior_recorte_mm2": round(a_inset, 2),
            "area_interior_recorte_cm2": round(a_inset / 100.0, 2),
            "perimetro_interior_recorte_mm": round(p_inset, 2),
            "centroide_interior_z_mm": round(cz_in, 3),
            "vertices_exterior_10": [[round(p[0], 3), round(p[1], 3)] for p in outer_pts],
            "vertices_interior_10": [[round(p[0], 3), round(p[1], 3)] for p in inset_pts]
        })
    
    # Integración volumétrica por tramos trapezoidales
    volumen_trapezoidal_mm3 = 0.0
    for i in range(len(stations_output) - 1):
        s0 = stations_output[i]
        s1 = stations_output[i+1]
        dx = s1["estacion_x_mm"] - s0["estacion_x_mm"]
        vol_tramo = 0.5 * (s0["area_exterior_mm2"] + s1["area_exterior_mm2"]) * dx
        volumen_trapezoidal_mm3 += vol_tramo
    
    resumen = {
        "modelo": "A07_RESEARCH_BASE_2026-11-03_r1",
        "fuente_codigo": "entradas/investigacion-aeronautica/modelos_integrados/producto_A07/crear_A07.py",
        "escala_referencia_masa_kg": 5,
        "longitud_total_fuselaje_mm": total_len,
        "longitud_total_fuselaje_m": total_len / 1000.0,
        "estacion_nariz_x_mm": SECTIONS_A07[0][0],
        "estacion_cola_x_mm": SECTIONS_A07[-1][0],
        "area_maxima_transversal_mm2": max(s["area_exterior_mm2"] for s in stations_output),
        "area_maxima_transversal_cm2": max(s["area_exterior_cm2"] for s in stations_output),
        "estacion_area_maxima_x_mm": -140,
        "volumen_trapezoidal_litros": round(volumen_trapezoidal_mm3 / 1e6, 3),
        "volumen_loft_bruto_cad_litros": 40.09,
        "fuente_volumen_cad": "DECISION-ARQUITECTURA.md línea 37",
        "observacion_simetria": (
            "El cuerpo NO posee simetría circular (revolución). "
            "Presenta aplanamiento (W/H entre 1.12 y 1.81) y curvatura asimétrica en Z "
            "(Zcg positivo en todas las secciones debido a que la cota superior alcanza +1.0*h "
            "mientras la cota inferior solo alcanza -0.78*h)."
        ),
        "estaciones": stations_output
    }
    
    out_path = Path("salidas/AREAS_TRANSVERSALES_A07.json")
    out_path.write_text(json.dumps(resumen, indent=2, ensure_ascii=False))
    print(f"Archivo generado exitosamente: {out_path}")
    print(f"Longitud: {total_len} mm | Area max: {resumen['area_maxima_transversal_cm2']} cm2 | Vol trap: {resumen['volumen_trapezoidal_litros']} L")

if __name__ == "__main__":
    main()
