# Versión Autónoma Reproducible del Equilibrio Vertical Ideal 2D (Candidata C02)

Este directorio contiene la implementación analítica, suite de pruebas automatizadas y matrices tabulares de resultados para el modelo de equilibrio vertical ideal en 2D de la configuración propulsora de cuatro ventiladores independientes para el vehículo conceptual **C02**.

---

## 1. Convención de Sistemas de Coordenadas

### Sistema CAD Oficial de C02
- **$+x_{\text{CAD}}$**: Longitudinal hacia la cola (cola en $+x$, nariz en $-x$).
- **$+y_{\text{CAD}}$**: Lateral hacia la derecha / estribor (derecha en $+y$, izquierda en $-y$).
- **$+z_{\text{CAD}}$**: Vertical hacia arriba.

### Sistema de Vuelo Aeronáutico FLU (Forward-Left-Up)
- **$+x_{\text{FLU}}$**: Longitudinal hacia adelante / nariz (Forward).
- **$+y_{\text{FLU}}$**: Lateral hacia la izquierda / babor (Left).
- **$+z_{\text{FLU}}$**: Vertical hacia arriba (Up).

### Regla de Transformación CAD $\leftrightarrow$ FLU
$$\begin{bmatrix} x_{\text{FLU}} \\ y_{\text{FLU}} \\ z_{\text{FLU}} \end{bmatrix} = \begin{bmatrix} -1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} x_{\text{CAD}} \\ y_{\text{CAD}} \\ z_{\text{CAD}} \end{bmatrix}$$
El sistema FLU invierte simultáneamente los signos de las componentes longitudinal ($x$) y lateral ($y$):
$$x_{\text{FLU}} = -x_{\text{CAD}}, \quad y_{\text{FLU}} = -y_{\text{CAD}}, \quad z_{\text{FLU}} = +z_{\text{CAD}}$$

---

## 2. Asignación y Coordenadas de los Módulos de Empuje

Con los semibrazos geométricos nominales de C02 ($L_x = 0.160\text{ m}, L_y = 0.076\text{ m}$):

| Módulo | Coordenadas CAD $(x, y)$ | Región Física CAD | Coordenadas FLU $(x, y)$ | Región Física FLU |
| :---: | :---: | :---: | :---: | :---: |
| **Módulo 1** | $(-0.160, -0.076)\text{ m}$ | **Nariz / Izquierda** | $(+0.160, +0.076)\text{ m}$ | **Forward / Left** |
| **Módulo 2** | $(-0.160, +0.076)\text{ m}$ | **Nariz / Derecha** | $(+0.160, -0.076)\text{ m}$ | **Forward / Right** |
| **Módulo 3** | $(+0.160, -0.076)\text{ m}$ | **Cola / Izquierda** | $(-0.160, +0.076)\text{ m}$ | **Aft / Left** |
| **Módulo 4** | $(+0.160, +0.076)\text{ m}$ | **Cola / Derecha** | $(-0.160, -0.076)\text{ m}$ | **Aft / Right** |

---

## 3. Formulación Analítica

### Ecuaciones de Equilibrio Estático
1. **Fuerza vertical ($\sum F_z = W$):**
   $$f_1 + f_2 + f_3 + f_4 = W = m \cdot g$$
2. **Momento de cabeceo ($\sum M_y = 0$):**
   $$-L_x (f_1 + f_2) + L_x (f_3 + f_4) = x_{cg} W$$
3. **Momento de alabeo ($\sum M_x = 0$):**
   $$-L_y (f_1 + f_3) + L_y (f_2 + f_4) = y_{cg} W$$

### Totales Marginales
- Empuje en Cola ($+x_{\text{CAD}}$): $S_{\text{cola}} \equiv f_3 + f_4 = \frac{W}{2}\left(1 + \frac{x_{cg}}{L_x}\right)$
- Empuje en Nariz ($-x_{\text{CAD}}$): $S_{\text{nariz}} \equiv f_1 + f_2 = \frac{W}{2}\left(1 - \frac{x_{cg}}{L_x}\right)$
- Empuje a la Derecha ($+y_{\text{CAD}}$): $S_{\text{derecha}} \equiv f_2 + f_4 = \frac{W}{2}\left(1 + \frac{y_{cg}}{L_y}\right)$
- Empuje a la Izquierda ($-y_{\text{CAD}}$): $S_{\text{izquierda}} \equiv f_1 + f_3 = \frac{W}{2}\left(1 - \frac{y_{cg}}{L_y}\right)$

### Intervalo Admisible para $f_4$
$$f_4 \in [f_{4,\min},\; f_{4,\max}]$$
$$
\begin{aligned}
f_{4,\min} &= \max\left( 0,\; S_{\text{derecha}} - S_{\text{nariz}},\; S_{\text{derecha}} - F_{\text{máx}},\; S_{\text{cola}} - F_{\text{máx}} \right) \\
f_{4,\max} &= \min\left( F_{\text{máx}},\; S_{\text{derecha}},\; S_{\text{cola}},\; S_{\text{derecha}} - S_{\text{nariz}} + F_{\text{máx}} \right)
\end{aligned}
$$
Condición de factibilidad: $\Delta f_4 \equiv f_{4,\max} - f_{4,\min} \ge 0$ y $W \ge 0$.

Reconstrucción exacta de fuerzas:
$$f_3 = S_{\text{cola}} - f_4, \quad f_2 = S_{\text{derecha}} - f_4, \quad f_1 = S_{\text{nariz}} - S_{\text{derecha}} + f_4$$

---

## 4. Distinción Metodológica de Datos

- **Datos Medidos:** *Ninguno*. El prototipo no ha sido fabricado ni ensayado. En `C02_CANDIDATA.json`: `actual_mass_kg: null`, `actual_CG_m: null`, `actual_inertia_kgm2: null`, `installed_map_available: false`.
- **Supuestos de Referencia:**
  - Semibrazos CAD: $L_x = 0.160\text{ m}, L_y = 0.076\text{ m}$ (`centres_xy_m`).
  - Masa de integración: $m = 5.0\text{ kg}$ (`integration_reference_mass_target_kg: 5`).
  - Gravedad: $g = 9.80665\text{ m/s}^2$ (`operating_reference.g_m_s2`).
  - Empujes máximos por módulo: $F_{\text{máx}} = 20.58\text{ N}$ (caso ideal previo de referencia) y $F_{\text{máx}} = 25.00\text{ N}$ (hipótesis complementaria de dimensionamiento).
- **Cálculos:** Peso $W = 49.03325\text{ N}$, intervalos de $f_4$, fuerzas individuales, residuales y tablas de factibilidad.

---

## 5. Instrucciones de Reproducción y Ejecución

Todos los scripts son reproducibles con la biblioteca estándar de Python 3 (sin dependencias externas):

```bash
# 1. Ejecución del resolvedor analítico base:
python3 salidas/equilibrio_cg.py

# 2. Ejecución de la suite completa de pruebas unitarias (21 tests):
python3 salidas/test_equilibrio.py

# 3. Regeneración de las matrices tabulares CSV (945 posiciones evaluadas):
python3 salidas/generar_matrices_csv.py
```

---

## 6. Inventario de Entregables Generados

Todos los entregables se encuentran en `salidas/`:

1. **`equilibrio_cg.py`**: Módulo base con las clases de geometría, cotas de intervalo, resolvedores de equilibrio, funciones de capacidad y utilidades de conversión CAD $\leftrightarrow$ FLU.
2. **`test_equilibrio.py`**: Suite de 21 pruebas unitarias independientes automatizadas (`unittest`).
3. **`generar_matrices_csv.py`**: Script de generación de matrices tabulares con muestreo de 945 posiciones de CG.
4. **`matriz_posiciones_cg_Fmax20_58N.csv`**: Evaluación de las 945 posiciones bajo $F_{\text{máx}} = 20.58\text{ N}$.
5. **`matriz_posiciones_cg_Fmax25_00N.csv`**: Evaluación de las 945 posiciones bajo $F_{\text{máx}} = 25.00\text{ N}$.
6. **`matriz_posiciones_cg_comparativa.csv`**: Matriz consolidada de ganancias de factibilidad y márgenes entre ambas hipótesis de empuje.
7. **`INFORME_EQUILIBRIO_CG.md`**: Informe técnico exhaustivo con derivaciones analíticas, análisis de singularidades y resultados comparativos.
8. **`README.md`**: Este documento de referencia y guía metodológica.

---

## 7. Limitaciones del Alcance

- **Alcance estático ideal 2D:** No incluye dinámica de vuelo, momentos de inercia ni respuesta de control.
- **Sin mapa instalado:** No incluye pérdidas aerodinámicas de conductos, labios ni álabes (`installed_map_available: false`).
- **Sin fuerzas horizontales:** No contempla maniobras en el plano $XY$, viento lateral ni vectorización del empuje.
- **Sin efectos giroscópicos:** No considera la dinámica de aceleración angular de los rotores.
- **Parámetros conceptuales:** Los valores de masa y CG son hipótesis de diseño preliminares, no mediciones reales.
