# INFORME TÉCNICO: DERIVACIÓN Y VERIFICACIÓN ANALÍTICA DE EQUILIBRIO VERTICAL 2D PARA CONFIGURACIÓN C02

**Fecha de emisión:** Noviembre de 2026  
**Entorno:** Directorio aislado `salidas/`  
**Referencia arquitectónica:** Candidata C02 (`C02_CANDIDATA.json`, `INFORME-VERTICAL.md`)  
**Convención de coordenadas:** CAD oficial (+x hacia cola, -x hacia nariz, +y hacia derecha, -y hacia izquierda, +z hacia arriba; conversión a FLU: x e y invierten de signo).

---

## 1. Declaración Formal del Modelo y Clasificación de Datos

El presente informe documenta la versión autónoma y reproducible del análisis y verificación analítica del equilibrio estático vertical ideal en dos dimensiones (2D) para la configuración propulsora de cuatro módulos independientes rectangulares del vehículo C02.

### 1.1 Declaración del Modelo
- **Modelo estático ideal:** Cuatro fuerzas propulsoras verticales puras $f_1, f_2, f_3, f_4 \ge 0$, acotadas por la capacidad máxima de cada actuador ($0 \le f_i \le F_{\text{máx}}$).
- **Alcance estricto:** El modelo cubre únicamente el equilibrio estático vertical con posiciones de actuadores y CG supuestos. No infiere ni asume mapa instalado (`installed_map_available: false` en `C02_CANDIDATA.json`), sin pérdidas de labio/conducto, sin interacción aerodinámica con el fuselaje y sin efectos de compresibilidad o suelo.
- **Sistemas de coordenadas y convenio de signos:**
  - **Sistema CAD oficial de C02:**
    - Eje $+x_{\text{CAD}}$: Longitudinal orientado hacia la cola (nariz en $-x_{\text{CAD}}$, cola en $+x_{\text{CAD}}$).
    - Eje $+y_{\text{CAD}}$: Lateral orientado hacia la derecha / estribor (izquierda en $-y_{\text{CAD}}$, derecha en $+y_{\text{CAD}}$).
    - Eje $+z_{\text{CAD}}$: Vertical orientado hacia arriba.
  - **Sistema de vuelo FLU (Forward-Left-Up, ISO 1151 / aeronavegabilidad):**
    - Eje $+x_{\text{FLU}}$: Hacia adelante / hacia la nariz (forward).
    - Eje $+y_{\text{FLU}}$: Hacia la izquierda / babor (left).
    - Eje $+z_{\text{FLU}}$: Hacia arriba (up).
    - **Regla de transformación ($\mathbf{R}_{\text{flight/CAD}}$):**
      $$x_{\text{FLU}} = -x_{\text{CAD}}, \quad y_{\text{FLU}} = -y_{\text{CAD}}, \quad z_{\text{FLU}} = +z_{\text{CAD}}$$
      FLU invierte simultáneamente los signos de las componentes longitudinal ($x$) y lateral ($y$).
- **Hipótesis de fuerzas:** Actitud estacionaria puramente nivelada. Ausencia de fuerzas horizontales ($F_x = 0, F_y = 0$), sin momentos parásitos aerodinámicos ni giroscópicos externos.

### 1.2 Distinción Metodológica de Datos
Se mantiene una estricta distinción entre datos medidos, datos supuestos y cálculos analíticos:

| Categoría | Parámetro | Valor y Unidades | Fuente / Justificación |
| :--- | :--- | :--- | :--- |
| **Datos Medidos** | *Ninguno* | — | No existen datos medidos en banco ni vuelo. En `C02_CANDIDATA.json`: `actual_mass_kg: null`, `actual_CG_m: null`, `actual_inertia_kgm2: null`, `installed_map_available: false`. |
| **Supuestos de Referencia** | Semibrazo longitudinal $L_x$ | $0.160\text{ m}$ ($160\text{ mm}$) | Coordenadas nominales CAD en `centres_xy_m` de `C02_CANDIDATA.json`. |
| **Supuestos de Referencia** | Semibrazo lateral $L_y$ | $0.076\text{ m}$ ($76\text{ mm}$) | Coordenadas nominales CAD en `centres_xy_m` de `C02_CANDIDATA.json`. |
| **Supuestos de Referencia** | Masa de integración $m$ | $5.0\text{ kg}$ | Meta nominal de diseño de C02 (`integration_reference_mass_target_kg: 5`). |
| **Supuestos de Referencia** | Aceleración de la gravedad $g$ | $9.80665\text{ m/s}^2$ | Estándar terrestre en `operating_reference.g_m_s2`. |
| **Supuestos de Referencia** | Empuje máximo base $F_{\text{máx}, 1}$ | $20.58\text{ N}$ | Hipótesis previa no calificada de referencia (`INFORME-VERTICAL.md`). |
| **Supuestos de Referencia** | Empuje máximo alternativo $F_{\text{máx}, 2}$ | $25.00\text{ N}$ | Hipótesis complementaria de dimensionamiento motriz. |
| **Cálculos** | Peso estático de referencia $W$ | $49.03325\text{ N}$ | $W = m \cdot g = 5.0\text{ kg} \times 9.80665\text{ m/s}^2$. |
| **Cálculos** | Totales marginales en bordes | $S_{\text{cola}}, S_{\text{nariz}}, S_{\text{derecha}}, S_{\text{izquierda}}\text{ N}$ | Derivados analíticamente de las 3 ecuaciones de equilibrio. |
| **Cálculos** | Intervalo admisible para $f_4$ | $[f_{4,\min}, f_{4,\max}]\text{ N}$ | Intersección analítica exacta de las 8 desigualdades de actuador. |
| **Cálculos** | Fuerzas asignadas | $f_1, f_2, f_3, f_4\text{ N}$ | Soluciones por centro de intervalo y pseudo-inversa proyectada. |
| **Cálculos** | Capacidad vertical máxima | $F_{z,\max}(x_{cg}, y_{cg})\text{ N}$ | Capacidad límite analítica antes de saturación de actuadores. |

---

## 2. Derivación Matemática Rigurosa

### 2.1 Identificación y Posicionamiento de Módulos Propulsores
Con base en `centres_xy_m` de `C02_CANDIDATA.json`, las ubicaciones geométricas de los cuatro ventiladores en el sistema CAD oficial y su correspondencia física unívoca son:

- **Módulo 1:** $(x_1, y_1) = (-L_x, -L_y) = (-0.160, -0.076)\text{ m} \implies$ **Nariz / Izquierda** ($-x_{\text{CAD}}, -y_{\text{CAD}}$).
  - En FLU: $(x_{1,\text{FLU}}, y_{1,\text{FLU}}) = (+L_x, +L_y) = (+0.160, +0.076)\text{ m}$ (Forward / Left).
- **Módulo 2:** $(x_2, y_2) = (-L_x, +L_y) = (-0.160, +0.076)\text{ m} \implies$ **Nariz / Derecha** ($-x_{\text{CAD}}, +y_{\text{CAD}}$).
  - En FLU: $(x_{2,\text{FLU}}, y_{2,\text{FLU}}) = (+L_x, -L_y) = (+0.160, -0.076)\text{ m}$ (Forward / Right).
- **Módulo 3:** $(x_3, y_3) = (+L_x, -L_y) = (+0.160, -0.076)\text{ m} \implies$ **Cola / Izquierda** ($+x_{\text{CAD}}, -y_{\text{CAD}}$).
  - En FLU: $(x_{3,\text{FLU}}, y_{3,\text{FLU}}) = (-L_x, +L_y) = (-0.160, +0.076)\text{ m}$ (Aft / Left).
- **Módulo 4:** $(x_4, y_4) = (+L_x, +L_y) = (+0.160, +0.076)\text{ m} \implies$ **Cola / Derecha** ($+x_{\text{CAD}}, +y_{\text{CAD}}$).
  - En FLU: $(x_{4,\text{FLU}}, y_{4,\text{FLU}}) = (-L_x, -L_y) = (-0.160, -0.076)\text{ m}$ (Aft / Right).

Cada módulo ejerce una fuerza puntual puramente vertical $\vec{F}_i = f_i\,\hat{k}_{\text{CAD}}$ con $0 \le f_i \le F_{\text{máx}}$. El peso del vehículo es $\vec{W} = -W\,\hat{k}_{\text{CAD}} = -m g\,\hat{k}_{\text{CAD}}$, aplicado en la posición hipotética de centro de gravedad $(x_{cg}, y_{cg})$.

### 2.2 Ecuaciones de Equilibrio Estático en CAD
Las condiciones de equilibrio estático de traslación vertical y momentos respecto al origen CAD son:

1. **Equilibrio de fuerzas verticales ($\sum F_z = 0$):**
   $$f_1 + f_2 + f_3 + f_4 = W$$

2. **Equilibrio de cabeceo (momento alrededor del eje $y_{\text{CAD}}$, $\sum M_y = 0$):**
   $$\sum_{i=1}^4 x_i f_i = x_{cg} W \iff -L_x (f_1 + f_2) + L_x (f_3 + f_4) = x_{cg} W$$

3. **Equilibrio de alabeo (momento alrededor del eje $x_{\text{CAD}}$, $\sum M_x = 0$):**
   $$\sum_{i=1}^4 y_i f_i = y_{cg} W \iff -L_y (f_1 + f_3) + L_y (f_2 + f_4) = y_{cg} W$$

En formulación matricial lineal $\mathbf{A}\,\mathbf{f} = \mathbf{b}$:
$$
\begin{bmatrix}
1 & 1 & 1 & 1 \\
-L_x & -L_x & L_x & L_x \\
-L_y & L_y & -L_y & L_y
\end{bmatrix}
\begin{bmatrix}
f_1 \\ f_2 \\ f_3 \\ f_4
\end{bmatrix}
=
\begin{bmatrix}
W \\ x_{cg} W \\ y_{cg} W
\end{bmatrix}
$$

### 2.3 Espacio Nulo y Grado de Libertad Interno (Modo Warp)
Las tres filas de la matriz $\mathbf{A}$ son mutuamente ortogonales. Como hay 4 variables y 3 restricciones independientes, existe un espacio nulo de dimensión 1 generado por el vector de torsión (modo warp):
$$\mathbf{v}_{\text{null}} = \begin{bmatrix} +1 \\ -1 \\ -1 \\ +1 \end{bmatrix}$$
Se comprueba analíticamente:
$$\mathbf{A} \cdot \mathbf{v}_{\text{null}} = \begin{bmatrix} 1 - 1 - 1 + 1 \\ -L_x + L_x - L_x + L_x \\ -L_y - L_y + L_y + L_y \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ 0 \end{bmatrix}$$
Cualquier variación a lo largo de $\mathbf{v}_{\text{null}}$ no altera en absoluto la sustentación neta ni los momentos de cabeceo y alabeo.

### 2.4 Totales Marginales en Bordes
A partir de las ecuaciones de momento y la suma total de fuerzas, se desacoplan los totales requeridos en cada uno de los cuatro bordes del cuadrilátero:

- **Empuje total en la Cola ($+x_{\text{CAD}}$, motores 3 y 4):**
  $$S_{\text{cola}} \equiv f_3 + f_4 = \frac{W}{2}\left(1 + \frac{x_{cg}}{L_x}\right)$$
- **Empuje total en la Nariz ($-x_{\text{CAD}}$, motores 1 y 2):**
  $$S_{\text{nariz}} \equiv f_1 + f_2 = \frac{W}{2}\left(1 - \frac{x_{cg}}{L_x}\right)$$
- **Empuje total a la Derecha ($+y_{\text{CAD}}$, motores 2 y 4):**
  $$S_{\text{derecha}} \equiv f_2 + f_4 = \frac{W}{2}\left(1 + \frac{y_{cg}}{L_y}\right)$$
- **Empuje total a la Izquierda ($-y_{\text{CAD}}$, motores 1 y 3):**
  $$S_{\text{izquierda}} \equiv f_1 + f_3 = \frac{W}{2}\left(1 - \frac{y_{cg}}{L_y}\right)$$

Se verifica por construcción que:
$$S_{\text{cola}} + S_{\text{nariz}} = W, \quad S_{\text{derecha}} + S_{\text{izquierda}} = W$$

### 2.5 Parametrización de Fuerzas en Función de $f_4$
Eligiendo la fuerza del Módulo 4 ($f_4$, Cola/Derecha) como variable libre del espacio afín:
$$
\begin{aligned}
f_3 &= S_{\text{cola}} - f_4 \\
f_2 &= S_{\text{derecha}} - f_4 \\
f_1 &= S_{\text{nariz}} - f_2 = S_{\text{nariz}} - S_{\text{derecha}} + f_4
\end{aligned}
$$
Comprobación para $f_1 + f_3$:
$$f_1 + f_3 = (S_{\text{nariz}} - S_{\text{derecha}} + f_4) + (S_{\text{cola}} - f_4) = S_{\text{nariz}} + S_{\text{cola}} - S_{\text{derecha}} = W - S_{\text{derecha}} = S_{\text{izquierda}}$$
Nótese además que:
$$S_{\text{derecha}} - S_{\text{nariz}} = \frac{W}{2}\left(1 + \frac{y_{cg}}{L_y}\right) - \frac{W}{2}\left(1 - \frac{x_{cg}}{L_x}\right) = \frac{W}{2}\left(\frac{x_{cg}}{L_x} + \frac{y_{cg}}{L_y}\right)$$

### 2.6 Intersección de Intervalos y Teorema de Factibilidad
Imponiendo las cotas de saturación $0 \le f_i \le F_{\text{máx}}$ para cada actuador:

1. **Restricción de $f_4$ ($0 \le f_4 \le F_{\text{máx}}$):**
   $$L_4 = 0, \quad U_4 = F_{\text{máx}}$$
2. **Restricción de $f_3$ ($0 \le S_{\text{cola}} - f_4 \le F_{\text{máx}}$):**
   $$L_3 = S_{\text{cola}} - F_{\text{máx}}, \quad U_3 = S_{\text{cola}}$$
3. **Restricción de $f_2$ ($0 \le S_{\text{derecha}} - f_4 \le F_{\text{máx}}$):**
   $$L_2 = S_{\text{derecha}} - F_{\text{máx}}, \quad U_2 = S_{\text{derecha}}$$
4. **Restricción de $f_1$ ($0 \le S_{\text{nariz}} - S_{\text{derecha}} + f_4 \le F_{\text{máx}}$):**
   $$L_1 = S_{\text{derecha}} - S_{\text{nariz}}, \quad U_1 = S_{\text{derecha}} - S_{\text{nariz}} + F_{\text{máx}}$$

El intervalo admisible para $f_4$ es la intersección de todas las condiciones:
$$f_4 \in [f_{4,\min},\; f_{4,\max}]$$
donde:
$$
\begin{aligned}
f_{4,\min} &= \max\left( 0,\; S_{\text{derecha}} - S_{\text{nariz}},\; S_{\text{derecha}} - F_{\text{máx}},\; S_{\text{cola}} - F_{\text{máx}} \right) \\
f_{4,\max} &= \min\left( F_{\text{máx}},\; S_{\text{derecha}},\; S_{\text{cola}},\; S_{\text{derecha}} - S_{\text{nariz}} + F_{\text{máx}} \right)
\end{aligned}
$$

> **Teorema de Factibilidad:** El equilibrio estático vertical ideal 2D con actuadores acotados es físicamente realizable si y solo si:
> $$\Delta f_4 \equiv f_{4,\max} - f_{4,\min} \ge 0 \quad \text{y} \quad W \ge 0$$

- Si $\Delta f_4 > 0$: El equilibrio es factible con holgura estricta (infinitas combinaciones admisibles).
- Si $\Delta f_4 = 0$: El equilibrio es factible y estrictamente único (caso límite o saturación de borde).
- Si $\Delta f_4 < 0$: El equilibrio es físicamente irrealizable (déficit de empuje igual a $|\Delta f_4|$).

### 2.7 Polígono Admisible 2D y Capacidad Vertical Máxima
Las 16 desigualdades cruzadas $L_i \le U_j$ definen un octógono convexo en el plano $(x_{cg}, y_{cg})$ limitado por:
1. **Límites rectangulares de apoyo:** $|x_{cg}| \le L_x$ y $|y_{cg}| \le L_y$.
2. **Capacidad de pares:** $|x_{cg}| \le L_x (4 F_{\text{máx}} / W - 1)$ y $|y_{cg}| \le L_y (4 F_{\text{máx}} / W - 1)$.
3. **Saturación en esquinas individuales (cortes diagonales):**
   $$\left| \frac{x_{cg}}{L_x} + \frac{y_{cg}}{L_y} \right| \le \frac{2 F_{\text{máx}}}{W}, \quad \left| \frac{x_{cg}}{L_x} - \frac{y_{cg}}{L_y} \right| \le \frac{2 F_{\text{máx}}}{W}$$

La capacidad vertical admisible máxima para cualquier posición de CG es:
$$F_{z,\max}(x_{cg}, y_{cg}) = \min\left( 4 F_{\text{máx}},\; \frac{4 F_{\text{máx}}}{1 + \frac{|x_{cg}|}{L_x}},\; \frac{4 F_{\text{máx}}}{1 + \frac{|y_{cg}|}{L_y}},\; \frac{2 F_{\text{máx}}}{\frac{|x_{cg}|}{L_x} + \frac{|y_{cg}|}{L_y}} \right)$$

---

## 3. Verificación Analítica de Límites y Singularidades

Se comprobaron formalmente los siguientes regímenes singulares y de contorno:

1. **Singularidad de Masa Nula ($W = 0$):**
   - $S_{\text{cola}} = S_{\text{nariz}} = S_{\text{derecha}} = S_{\text{izquierda}} = 0$.
   - $f_{4,\min} = \max(0, 0, -F_{\text{máx}}, -F_{\text{máx}}) = 0$.
   - $f_{4,\max} = \min(F_{\text{máx}}, 0, 0, F_{\text{máx}}) = 0$.
   - La holgura analítica es estrictamente $\Delta f_4 = 0.0\text{ N}$. Las cuatro fuerzas se colapsan unívocamente a $f_1 = f_2 = f_3 = f_4 = 0\text{ N}$. Cualquier empuje positivo rompería el equilibrio vertical ascendente.
2. **Límite de Sustentación Máxima en Hover ($W = 4 F_{\text{máx}}$ en $(0, 0)$):**
   - $S_{\text{cola}} = S_{\text{nariz}} = S_{\text{derecha}} = S_{\text{izquierda}} = 2 F_{\text{máx}}$.
   - $f_{4,\min} = \max(0, 0, F_{\text{máx}}, F_{\text{máx}}) = F_{\text{máx}}$.
   - $f_{4,\max} = \min(F_{\text{máx}}, 2 F_{\text{máx}}, 2 F_{\text{máx}}, F_{\text{máx}}) = F_{\text{máx}}$.
   - Solución única $f_1 = f_2 = f_3 = f_4 = F_{\text{máx}}$ con $\Delta f_4 = 0.0\text{ N}$ y margen $0.0\text{ N}$.
3. **Singularidad en las Cuatro Esquinas ($(\pm L_x, \pm L_y)$):**
   - Si el CG se coloca exactamente sobre uno de los motores, por equilibrio de momentos los otros 3 motores deben ejercer fuerza nula, y el motor correspondiente debe soportar todo el peso: $f_k = W, \; f_{j \ne k} = 0$.
   - Para $m = 5.0\text{ kg}$ ($W = 49.03\text{ N}$), dado que $F_{\text{máx}} \le 25.0\text{ N} < 49.03\text{ N}$, ninguna de las cuatro esquinas es factible.
   - Para $m \le 2.098\text{ kg}$ ($W \le 20.58\text{ N}$), las cuatro esquinas se vuelven factibles, concentrando el 100% del empuje en el ventilador de la esquina.
4. **Bordes Longitudinales y Laterales ($(\pm L_x, 0)$ y $(0, \pm L_y)$):**
   - En $x = +L_x$ (Cola), los motores de la nariz aportan 0 ($f_1 = f_2 = 0$) y los dos traseros se reparten el peso ($f_3 = f_4 = W/2 = 24.5166\text{ N}$).
   - Con $F_{\text{máx}} = 20.58\text{ N}$, el límite es $2 F_{\text{máx}} = 41.16\text{ N} < 49.03\text{ N} \implies$ NO FACTIBLE ($\Delta f_4 = -7.87\text{ N}$).
   - Con $F_{\text{máx}} = 25.00\text{ N}$, el límite es $2 F_{\text{máx}} = 50.00\text{ N} \ge 49.03\text{ N} \implies$ FACTIBLE ($\Delta f_4 = 0.00\text{ N}$).
5. **Exterior del Polígono de Soporte ($|x_{cg}| > L_x$ o $|y_{cg}| > L_y$):**
   - Como no se admiten fuerzas negativas (tracción hacia abajo), es físicamente imposible equilibrar momentos fuera del rectángulo de apoyo. La capacidad vertical es analíticamente $F_{z,\max} = 0.0\text{ N}$.

---

## 4. Métodos Constructivos de Asignación de Fuerza

Cuando el sistema es admisible ($\Delta f_4 \ge 0$), se proveen dos estrategias analíticas de selección de $f_4$:

1. **Centro de Intervalo (estrategia recomendada para control):**
   $$f_4 = \frac{f_{4,\min} + f_{4,\max}}{2}$$
   Maximiza la distancia simétrica a los límites de saturación física, proporcionando la máxima autoridad de control dinámica ante ráfagas.
2. **Pseudo-Inversa Proyectada (mínima norma euclídea):**
   Solución de mínimos cuadrados sin cotas:
   $$f_{\text{LS}, i} = \frac{W}{4}\left(1 + \frac{x_i x_{cg}}{L_x^2} + \frac{y_i y_{cg}}{L_y^2}\right)$$
   Proyección ortogonal al intervalo admisible:
   $$f_4 = \operatorname{clip}(f_{\text{LS}, 4},\; f_{4,\min},\; f_{4,\max})$$
   Minimiza el consumo de energía eléctrica total aproximado ($\sum f_i^2$).

En todas las evaluaciones, los residuales numéricos se verifican con precisión de máquina:
$$\text{res}_W = \left|\sum_{i=1}^4 f_i - W\right| < 10^{-11}\text{ N}, \quad \text{res}_{M_x} < 10^{-11}\text{ N}\cdot\text{m}, \quad \text{res}_{M_y} < 10^{-11}\text{ N}\cdot\text{m}$$

---

## 5. Resultados de la Suite de Pruebas Automatizadas

La suite `salidas/test_equilibrio.py` implementa 21 pruebas analíticas unitarias independientes. Todas fueron ejecutadas en el sandbox, obteniendo **21/21 exitosas (100% PASS) en 0.001 s**.

### Tabla Consolidada de Pruebas Ejecutadas

| ID | Clase de Prueba | Caso / Condiciones | Parámetros Evaluados | Criterio de Éxito | Resultado Obtenido | Estado |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | `TestSimetria` | Invariancia en 4 cuadrantes | Malla de 5 puntos en $\pm x, \pm y$ | Factibilidad y holgura idénticas | Coincidencia $< 10^{-9}\text{ N}$ | **PASS** |
| 2 | `TestSimetria` | Permutación por reflexión longitudinal | $x \to -x$ | $f_1 \leftrightarrow f_3, \; f_2 \leftrightarrow f_4$ | Error $< 10^{-7}\text{ N}$ | **PASS** |
| 3 | `TestSimetria` | Permutación por reflexión lateral | $y \to -y$ | $f_1 \leftrightarrow f_2, \; f_3 \leftrightarrow f_4$ | Error $< 10^{-7}\text{ N}$ | **PASS** |
| 4 | `TestMasa5kgCGCentrado` | CG centrado nominal (20.58 N) | $(0, 0)\text{ m}, W = 49.033\text{ N}$ | $f_i = 12.2583\text{ N}$, margen $8.32\text{ N}$ | Residuales $= 0.00\text{ N}$, margen $8.3217\text{ N}$ | **PASS** |
| 5 | `TestMasa5kgCGCentrado` | CG centrado nominal (25.00 N) | $(0, 0)\text{ m}, W = 49.033\text{ N}$ | $f_i = 12.2583\text{ N}$, margen $12.74\text{ N}$ | Residuales $= 0.00\text{ N}$, margen $12.7417\text{ N}$ | **PASS** |
| 6 | `TestCGenBorde` | Borde Cola ($+x$) 5 kg (20.58 N) | $(+0.160, 0.0)\text{ m}$ | No Factible ($\Delta f_4 = -7.87\text{ N}$) | Holgura $=-7.87325\text{ N}$ | **PASS** |
| 7 | `TestCGenBorde` | Borde Cola ($+x$) 5 kg (25.00 N) | $(+0.160, 0.0)\text{ m}$ | Factible, $f_1=f_2=0, f_3=f_4=W/2$ | $f_3=f_4=24.5166\text{ N}, \Delta f_4=0$ | **PASS** |
| 8 | `TestCGenBorde` | Borde Nariz ($-x$) 5 kg (25.00 N) | $(-0.160, 0.0)\text{ m}$ | Factible, $f_3=f_4=0, f_1=f_2=W/2$ | $f_1=f_2=24.5166\text{ N}$ | **PASS** |
| 9 | `TestCGenBorde` | Borde Derecha ($+y$) 5 kg | $(0.0, +0.076)\text{ m}$ | Infeasible 20.58 N / Factible 25 N | $f_2=f_4=W/2$ con 25 N | **PASS** |
| 10 | `TestCGenBorde` | Borde Izquierda ($-y$) 5 kg | $(0.0, -0.076)\text{ m}$ | Infeasible 20.58 N / Factible 25 N | $f_1=f_3=W/2$ con 25 N | **PASS** |
| 11 | `TestCGenBorde` | Las 4 Esquinas con 5 kg | $(\pm 0.160, \pm 0.076)\text{ m}$ | Infeasible en ambos $F_{\text{máx}}$ | No factible en las 4 esquinas | **PASS** |
| 12 | `TestCGenBorde` | Las 4 Esquinas con masa 2 kg | $m = 2.0\text{ kg}, W = 19.61\text{ N}$ | Un solo motor activo con $f_k = W$ | $f_k = 19.6133\text{ N}, f_{j \ne k}=0$ | **PASS** |
| 13 | `TestCGenBorde` | Consistencia INFORME-VERTICAL | $x = 0.096\text{ m}$ | Factible, Capacidad $51.45\text{ N}$ | Capacidad $= 51.45\text{ N} > W$ | **PASS** |
| 14 | `TestCGenBorde` | Consistencia INFORME-VERTICAL | $x = 0.120\text{ m}$ | No Factible, Capacidad $47.04\text{ N}$ | Capacidad $= 47.04\text{ N} < W$ | **PASS** |
| 15 | `TestFaltaDeFuerzaTotal` | Empuje global insuficiente | $F_{\text{máx}} = 10.0\text{ N} < W/4$ | No factible en $(0,0)$ | Holgura negativa | **PASS** |
| 16 | `TestFaltaDeFuerzaTotal` | Masa excesiva 10 kg | $m = 10.0\text{ kg}, W = 98.07\text{ N}$ | 20.58 N no factible; 25 N factible estrecho | Margen $0.48\text{ N}$ con 25 N | **PASS** |
| 17 | `TestTransformacionFLU` | Conversión de coordenadas | Vector $(0.120, -0.050, 0.010)$ | $x_{\text{FLU}} = -x, y_{\text{FLU}} = -y$ | Inversión exacta bidireccional | **PASS** |
| 18 | `TestTransformacionFLU` | Consistencia evaluación FLU | Muestra de 4 puntos interiores | Solución idéntica CAD y FLU | Coincidencia $< 10^{-9}\text{ N}$ | **PASS** |
| 19 | `TestLimitesYSingularidades` | Masa nula ($W = 0$) | $m = 0.0\text{ kg}, W = 0.0\text{ N}$ | $f_i = 0\text{ N}$, holgura $\Delta f_4 = 0$ | $f_i = 0.00\text{ N}, \Delta f_4 = 0.00\text{ N}$ | **PASS** |
| 20 | `TestLimitesYSingularidades` | Saturación exacta en hover | $W = 4 F_{\text{máx}}$ en $(0,0)$ | $f_i = F_{\text{máx}}$, holgura $\Delta f_4 = 0$ | $f_i = 20.00\text{ N}, \Delta f_4 = 0.00\text{ N}$ | **PASS** |
| 21 | `TestLimitesYSingularidades` | Puntos exteriores al soporte | $|x| > L_x$ o $|y| > L_y$ | Capacidad $F_{z,\max} = 0.0\text{ N}$ | Capacidad $= 0.00\text{ N}$, No factible | **PASS** |

---

## 6. Análisis Comparativo de la Matriz de Posiciones Hipotéticas (5 kg)

Se evaluó una malla estructurada de **945 posiciones hipotéticas de CG** en el rango $[-0.160, +0.160]\text{ m} \times [-0.076, +0.076]\text{ m}$, comparando el empuje base $F_{\text{máx}} = 20.58\text{ N}$ frente al de dimensionamiento $F_{\text{máx}} = 25.00\text{ N}$.

### 6.1 Estadísticas Globales de Factibilidad

| Indicador | $F_{\text{máx}} = 20.58\text{ N}$ (Base Ideal) | $F_{\text{máx}} = 25.00\text{ N}$ (Dimensionamiento) | Variación Absoluta / Relativa |
| :--- | :---: | :---: | :---: |
| **Total de posiciones evaluadas** | 945 | 945 | — |
| **Posiciones factibles** | **291** (30.8%) | **473** (50.1%) | **+182 posiciones (+62.5% de área útil)** |
| **Posiciones no factibles** | 654 (69.2%) | 472 (49.9%) | -182 posiciones (-27.8%) |
| **Capacidad vertical en $(0,0)$** | $82.32\text{ N}$ | $100.00\text{ N}$ | $+17.68\text{ N}$ ($+21.5\%$) |
| **Margen motriz por módulo en $(0,0)$** | $8.32\text{ N}$ | $12.74\text{ N}$ | $+4.42\text{ N}$ ($+53.1\%$) |
| **Aceleración vertical máxima neta en $(0,0)$** | $+0.679\text{ g}$ | $+1.039\text{ g}$ | $+0.360\text{ g}$ ($T/W$ pasa de 1.68 a 2.04) |

### 6.2 Comportamiento en Puntos Clave del Eje Longitudinal ($y_{\text{CAD}} = 0$)

| $x_{\text{CAD}}$ | Región Física | $F_{\text{máx}} = 20.58\text{ N}$ Factible | Holgura $\Delta f_4$ (20.58 N) | $F_{z,\max}$ (20.58 N) | $F_{\text{máx}} = 25.00\text{ N}$ Factible | Holgura $\Delta f_4$ (25.00 N) | $F_{z,\max}$ (25.00 N) | Diagnóstico |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **$0.000\text{ m}$** | Centro | **SÍ** | $+16.64\text{ N}$ | $82.32\text{ N}$ | **SÍ** | $+24.52\text{ N}$ | $100.00\text{ N}$ | Amplía margen (+53%) |
| **$+0.040\text{ m}$** | Cola (+x) | **SÍ** | $+10.51\text{ N}$ | $65.86\text{ N}$ | **SÍ** | $+18.39\text{ N}$ | $80.00\text{ N}$ | Amplía margen |
| **$+0.080\text{ m}$** | Cola (+x) | **SÍ** | $+4.39\text{ N}$ | $54.88\text{ N}$ | **SÍ** | $+12.26\text{ N}$ | $66.67\text{ N}$ | Amplía margen |
| **$+0.096\text{ m}$** | Cola (+x) | **SÍ** | $+1.93\text{ N}$ | $51.45\text{ N}$ | **SÍ** | $+9.81\text{ N}$ | $62.50\text{ N}$ | Caso crítico se vuelve holgado |
| **$+0.120\text{ m}$** | Cola (+x) | **NO** | $-1.74\text{ N}$ | $47.04\text{ N}$ | **SÍ** | $+6.13\text{ N}$ | $57.14\text{ N}$ | **Recupera factibilidad (+10.1 N)** |
| **$+0.160\text{ m}$** | Borde Cola | **NO** | $-7.87\text{ N}$ | $41.16\text{ N}$ | **SÍ** | $0.00\text{ N}$ | $50.00\text{ N}$ | **Alcanza el límite geométrico exacto** |

---

## 7. Limitaciones del Modelo

1. **Modelo estático puro:** No modela derivadas de estabilidad dinámica, efectos de momentos de inercia ($I_{xx}, I_{yy}, I_{zz}$), amortiguamiento aerodinámico ni la dinámica de actuadores/servos.
2. **Ausencia de mapa instalado de conducto/álabes:** No modela pérdidas de admisión, distorsión por incidencia cruzada, efecto suelo ni estator de recuperación (`installed_map_available: false`).
3. **Ausencia de fuerzas en el plano horizontal:** No contempla empujes vectorizados ($F_x, F_y = 0$), viento incidente ni la inclinación de las tapas/conductos.
4. **Desacoplamiento giroscópico:** No considera el momento angular residual de los rotores durante aceleraciones transitorias diferenciales.
5. **Carácter hipotético del CG y masa:** Los valores analizados (5 kg, CG centrado o desplazado) son supuestos paramétricos de diseño, no medidas físicas de un prototipo construido.

---

## 8. Relación de Entregables Generados en `salidas/`

Los archivos colocados en `salidas/` son autónomos y reproducibles:

1. **`salidas/equilibrio_cg.py`**: Módulo base en Python con las clases `PropulsionGeometry`, `IntervalBounds`, `EquilibriumSolution`, la derivación analítica de cotas, los resolvedores de equilibrio y transformaciones CAD/FLU.
2. **`salidas/test_equilibrio.py`**: Suite de pruebas unitarias automatizadas (`unittest`) que ejecuta las 21 pruebas analíticas independientes.
3. **`salidas/generar_matrices_csv.py`**: Generador reproducible de las tablas de datos para las 945 posiciones hipotéticas de CG.
4. **`salidas/matriz_posiciones_cg_Fmax20_58N.csv`**: Matriz CSV con 945 filas evaluadas bajo $F_{\text{máx}} = 20.58\text{ N}$.
5. **`salidas/matriz_posiciones_cg_Fmax25_00N.csv`**: Matriz CSV con 945 filas evaluadas bajo $F_{\text{máx}} = 25.00\text{ N}$.
6. **`salidas/matriz_posiciones_cg_comparativa.csv`**: Matriz comparativa punto a punto que clasifica cada punto según la ganancia de factibilidad.
7. **`salidas/INFORME_EQUILIBRIO_CG.md`**: El presente informe técnico detallado.
8. **`salidas/README.md`**: Guía técnica de uso, ejecución y referencia metodológica.
