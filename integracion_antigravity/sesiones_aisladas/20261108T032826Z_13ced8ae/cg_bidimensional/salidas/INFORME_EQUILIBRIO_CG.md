# INFORME TÉCNICO: DERIVACIÓN Y VERIFICACIÓN ANALÍTICA DE EQUILIBRIO VERTICAL 2D PARA CONFIGURACIÓN C02

**Fecha de cálculo:** 7 de noviembre de 2026  
**Entorno de ejecución:** Espacio aislado `salidas/` en sandbox  
**Referencia arquitectónica:** Candidata C02 (`C02_CANDIDATA.json`, `INFORME-VERTICAL.md`)  

---

## 1. Declaración Formal del Modelo y Supuestos

El presente trabajo implementa y verifica un chequeo analítico riguroso del equilibrio estático de sustentación vertical pura para una arquitectura de cuatro propulsores rectangulares.

### 1.1 Declaración del Modelo
- **Modelo estático ideal:** Cuatro fuerzas propulsoras puntuales verticales $f_1, f_2, f_3, f_4 \ge 0$, limitadas superiormente por un empuje máximo $F_{\text{máx}}$ ($0 \le f_i \le F_{\text{máx}}$).
- **Sin mapa instalado:** No se modelan curvas de flujo aerodinámico instalado, pérdidas en conducto/labios, efecto suelo, ni degradación por ángulo de ataque de álabes (`installed_map_available: false`).
- **Sistema de coordenadas CAD oficial:**
  - Eje $+x$: Longitudinal orientado hacia la cola (nariz en $-x$, cola en $+x$).
  - Eje $+y$: Lateral orientado hacia la izquierda (babor).
  - Eje $+z$: Vertical orientado hacia arriba.
  *(Nota: En el sistema de vuelo FLU de aeronavegabilidad, los ejes $x$ e $y$ invierten signo respecto a CAD).*
- **Ausencia de fuerzas horizontales y momentos parásitos:** Modelo estrictamente vertical ($F_x = 0$, $F_y = 0$, $M_z = 0$). Se asume actitud nivelada estacionaria sin perturbaciones de viento exterior.

### 1.2 Distinción Metodológica de Datos
Para garantizar la integridad y trazabilidad técnica, se clasifican estrictamente los parámetros:

| Categoría | Parámetro | Valor y Unidades | Fuente / Justificación |
| :--- | :--- | :--- | :--- |
| **Datos Medidos** | *Ninguno* | — | El vehículo C02 se encuentra en fase conceptual de integración. En `C02_CANDIDATA.json`: `actual_mass_kg: null`, `actual_CG_m: null`, `actual_inertia_kgm2: null`. |
| **Supuestos de Referencia** | Semibrazo longitudinal $L_x$ | $0.160\text{ m}$ ($160\text{ mm}$) | Coordenadas nominales CAD de centros de ventilador (`centres_xy_m`: $x = \pm 0.160\text{ m}$). |
| **Supuestos de Referencia** | Semibrazo lateral $L_y$ | $0.076\text{ m}$ ($76\text{ mm}$) | Coordenadas nominales CAD de centros de ventilador (`centres_xy_m`: $y = \pm 0.076\text{ m}$). |
| **Supuestos de Referencia** | Masa de integración $m$ | $5.0\text{ kg}$ | Meta de integración C02 (`integration_reference_mass_target_kg: 5`). |
| **Supuestos de Referencia** | Gravedad estándar $g$ | $9.80665\text{ m/s}^2$ | Entorno de referencia atmósfera estándar (`operating_reference.g_m_s2`). |
| **Supuestos de Referencia** | Empuje máximo base $F_{\text{máx}, 1}$ | $20.58\text{ N}$ | Valor procedente de caso ideal previo no calificado (`INFORME-VERTICAL.md`). |
| **Supuestos de Referencia** | Empuje máximo alternativo $F_{\text{máx}, 2}$ | $25.00\text{ N}$ | Hipótesis complementaria de dimensionamiento motriz. |
| **Cálculos** | Peso estático de referencia $W$ | $49.03325\text{ N}$ | $W = m \cdot g = 5.0 \times 9.80665\text{ N}$. |
| **Cálculos** | Intervalo analítico de $f_4$ | $[f_{4,\min}, f_{4,\max}]\text{ N}$ | Derivación formal a partir de las 3 ecuaciones de equilibrio y 8 cotas de actuador. |
| **Cálculos** | Asignación y comprobación de fuerzas | $f_1, f_2, f_3, f_4\text{ N}$ | Solución analítica centrada en el intervalo y pseudo-inversa proyectada. |

---

## 2. Derivación Matemática del Chequeo Analítico

### 2.1 Coordenadas de los Módulos de Propulsión
En concordancia con `centres_xy_m` de `C02_CANDIDATA.json`, los cuatro ventiladores se ubican en:
- Módulo 1: $(x_1, y_1) = (-L_x, -L_y) = (-0.160, -0.076)\text{ m}$ (Nariz / Derecha)
- Módulo 2: $(x_2, y_2) = (-L_x, +L_y) = (-0.160, +0.076)\text{ m}$ (Nariz / Izquierda)
- Módulo 3: $(x_3, y_3) = (+L_x, -L_y) = (+0.160, -0.076)\text{ m}$ (Cola / Derecha)
- Módulo 4: $(x_4, y_4) = (+L_x, +L_y) = (+0.160, +0.076)\text{ m}$ (Cola / Izquierda)

Cada módulo ejerce una fuerza vertical ascendente $\vec{F}_i = f_i\,\hat{k}$ con $0 \le f_i \le F_{\text{máx}}$. El peso del vehículo es $\vec{W} = -W\,\hat{k} = -m g\,\hat{k}$, aplicado en el centro de gravedad arbitrario $(x_{cg}, y_{cg})$.

### 2.2 Ecuaciones de Equilibrio Estático
Las condiciones necesarias y suficientes de reposo estacionario son:
1. **Equilibrio de fuerzas verticales ($\sum F_z = 0$):**
   $$\sum_{i=1}^4 f_i = W = mg$$
2. **Equilibrio de momento de cabeceo (alrededor del eje $y$, $\sum M_y = 0$):**
   $$\sum_{i=1}^4 x_i f_i = x_{cg} W \implies -L_x (f_1 + f_2) + L_x (f_3 + f_4) = x_{cg} W$$
3. **Equilibrio de momento de alabeo (alrededor del eje $x$, $\sum M_x = 0$):**
   $$\sum_{i=1}^4 y_i f_i = y_{cg} W \implies -L_y (f_1 + f_3) + L_y (f_2 + f_4) = y_{cg} W$$

En forma matricial $A\,\mathbf{f} = \mathbf{b}$:
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

### 2.3 Espacio Nulo y Grado de Libertad Interno
Las tres filas de la matriz $A$ son ortogonales entre sí. Dado que hay 4 variables y 3 ecuaciones independientes, existe un espacio nulo de dimensión 1 generado por el vector de torsión (modo warp):
$$\mathbf{v}_{\text{null}} = \begin{bmatrix} +1 \\ -1 \\ -1 \\ +1 \end{bmatrix}$$
Cualquier solución puede parametrizarse unívocamente mediante la cuarta fuerza $f_4$ (o mediante un escalar $t$ a lo largo de $\mathbf{v}_{\text{null}}$).

### 2.4 Desacoplamiento por Totales Marginales
Dividiendo las ecuaciones de momento por $L_x$ y $L_y$, y combinando con la suma total, se obtienen directamente los totales requeridos en cada borde:
- **Total en la cola (trasero, $+x$):**
  $$S_{\text{rear}} \equiv f_3 + f_4 = \frac{W}{2}\left(1 + \frac{x_{cg}}{L_x}\right)$$
- **Total en la nariz (delantero, $-x$):**
  $$S_{\text{front}} \equiv f_1 + f_2 = \frac{W}{2}\left(1 - \frac{x_{cg}}{L_x}\right)$$
- **Total a la izquierda (babor, $+y$):**
  $$S_{\text{left}} \equiv f_2 + f_4 = \frac{W}{2}\left(1 + \frac{y_{cg}}{L_y}\right)$$
- **Total a la derecha (estribor, $-y$):**
  $$S_{\text{right}} \equiv f_1 + f_3 = \frac{W}{2}\left(1 - \frac{y_{cg}}{L_y}\right)$$

Nótese que por construcción:
$$S_{\text{rear}} + S_{\text{front}} = W, \quad S_{\text{left}} + S_{\text{right}} = W$$

### 2.5 Expresión de las Fuerzas en Función de $f_4$
Tomando $f_4$ como la variable libre:
$$
\begin{aligned}
f_3 &= S_{\text{rear}} - f_4 \\
f_2 &= S_{\text{left}} - f_4 \\
f_1 &= S_{\text{front}} - f_2 = S_{\text{front}} - S_{\text{left}} + f_4
\end{aligned}
$$
Comprobamos $f_1 + f_3$:
$$f_1 + f_3 = (S_{\text{front}} - S_{\text{left}} + f_4) + (S_{\text{rear}} - f_4) = S_{\text{front}} + S_{\text{rear}} - S_{\text{left}} = W - S_{\text{left}} = S_{\text{right}}$$
El sistema es algebraicamente cerrado y consistente.

### 2.6 Condición de Intersección de Intervalos para $f_4$
Imponiendo la restricción de capacidad $0 \le f_i \le F_{\text{máx}}$ a cada una de las 4 fuerzas:

1. **Para $f_4$:**
   $$0 \le f_4 \le F_{\text{máx}}$$
2. **Para $f_3$:**
   $$0 \le S_{\text{rear}} - f_4 \le F_{\text{máx}} \iff S_{\text{rear}} - F_{\text{máx}} \le f_4 \le S_{\text{rear}}$$
3. **Para $f_2$:**
   $$0 \le S_{\text{left}} - f_4 \le F_{\text{máx}} \iff S_{\text{left}} - F_{\text{máx}} \le f_4 \le S_{\text{left}}$$
4. **Para $f_1$:**
   $$0 \le f_4 + (S_{\text{front}} - S_{\text{left}}) \le F_{\text{máx}} \iff S_{\text{left}} - S_{\text{front}} \le f_4 \le S_{\text{left}} - S_{\text{front}} + F_{\text{máx}}$$

Definiendo las cuatro cotas inferiores $\{L_1, L_2, L_3, L_4\}$ y las cuatro cotas superiores $\{U_1, U_2, U_3, U_4\}$:
$$
\begin{aligned}
L_1 &= S_{\text{left}} - S_{\text{front}} = \frac{W}{2}\left(\frac{x_{cg}}{L_x} + \frac{y_{cg}}{L_y}\right) & U_1 &= L_1 + F_{\text{máx}} \\
L_2 &= S_{\text{left}} - F_{\text{máx}} & U_2 &= S_{\text{left}} \\
L_3 &= S_{\text{rear}} - F_{\text{máx}} & U_3 &= S_{\text{rear}} \\
L_4 &= 0 & U_4 &= F_{\text{máx}}
\end{aligned}
$$

El intervalo de valores físicamente admisibles para $f_4$ es la intersección:
$$f_4 \in [f_{4,\min},\; f_{4,\max}]$$
donde:
$$
\begin{aligned}
f_{4,\min} &= \max\left( 0,\; S_{\text{rear}} - F_{\text{máx}},\; S_{\text{left}} - F_{\text{máx}},\; S_{\text{left}} - S_{\text{front}} \right) \\
f_{4,\max} &= \min\left( F_{\text{máx}},\; S_{\text{rear}},\; S_{\text{left}},\; S_{\text{left}} - S_{\text{front}} + F_{\text{máx}} \right)
\end{aligned}
$$

### 2.7 Teorema de Factibilidad
> **Teorema:** El sistema de 4 fuerzas verticales puede equilibrar el peso $W$ en la posición $(x_{cg}, y_{cg})$ satisfaciendo $0 \le f_i \le F_{\text{máx}}$ **si y solo si**:
> $$f_{4,\min} \le f_{4,\max} \quad \text{y} \quad W \ge 0$$

La holgura analítica de factibilidad se define como:
$$\Delta f_4 = f_{4,\max} - f_{4,\min}$$
- Si $\Delta f_4 > 0$: El equilibrio es factible y subdeterminado (infinitas combinaciones admisibles de fuerzas).
- Si $\Delta f_4 = 0$: El equilibrio es factible y único (solución estrictamente determinada).
- Si $\Delta f_4 < 0$: El equilibrio es físicamente imposible bajo el empuje $F_{\text{máx}}$ (déficit de empuje igual a $|\Delta f_4|$).

### 2.8 Polígono Admisible de CG en 2D (Octógono de Sustentación)
La condición $f_{4,\min} \le f_{4,\max}$ equivale a que todas las 16 desigualdades cruzadas $L_i \le U_j$ se cumplan simultáneamente. Eliminando identidades triviales, esto define un **octógono convexo** en el plano $(x_{cg}, y_{cg})$ acotado por:
1. **Límites rectangulares de apoyo geométrico:**
   $$|x_{cg}| \le L_x, \quad |y_{cg}| \le L_y$$
2. **Límites de par delantero/trasero y lateral:**
   $$|x_{cg}| \le L_x \left( \frac{4 F_{\text{máx}}}{W} - 1 \right), \quad |y_{cg}| \le L_y \left( \frac{4 F_{\text{máx}}}{W} - 1 \right)$$
3. **Cortes diagonales (saturación de esquinas individuales):**
   $$\left| \frac{x_{cg}}{L_x} + \frac{y_{cg}}{L_y} \right| \le \frac{2 F_{\text{máx}}}{W}, \quad \left| \frac{x_{cg}}{L_x} - \frac{y_{cg}}{L_y} \right| \le \frac{2 F_{\text{máx}}}{W}$$

Nótese la concordancia exacta con `INFORME-VERTICAL.md`: para $y_{cg} = 0$, la capacidad vertical máxima analítica es:
$$F_{z,\max}(x_{cg}) = \frac{4 F_{\text{máx}}}{1 + \frac{|x_{cg}|}{L_x}}$$
y en 2D, con acoplamiento diagonal:
$$F_{z,\max}(x_{cg}, y_{cg}) = \min\left( 4 F_{\text{máx}},\; \frac{4 F_{\text{máx}}}{1 + \frac{|x_{cg}|}{L_x}},\; \frac{4 F_{\text{máx}}}{1 + \frac{|y_{cg}|}{L_y}},\; \frac{2 F_{\text{máx}}}{\frac{|x_{cg}|}{L_x} + \frac{|y_{cg}|}{L_y}} \right)$$

---

## 3. Construcción y Verificación de Soluciones de Fuerza

Cuando $\Delta f_4 \ge 0$, se implementaron dos métodos constructivos:

1. **Solución centrada en el intervalo admisible (recomendada para control):**
   $$f_4 = \frac{f_{4,\min} + f_{4,\max}}{2}$$
   Maximiza la distancia simétrica a los límites de saturación, otorgando máxima robustez frente a perturbaciones.
2. **Solución pseudo-inversa proyectada (mínima norma euclídea):**
   La solución de mínimos cuadrados sin restricciones de caja es:
   $$f_{\text{LS}, i} = \frac{W}{4}\left(1 + \frac{x_i x_{cg}}{L_x^2} + \frac{y_i y_{cg}}{L_y^2}\right)$$
   Al proyectar ortogonalmente sobre el intervalo admisible:
   $$f_4 = \operatorname{clip}(f_{\text{LS}, 4},\; f_{4,\min},\; f_{4,\max})$$
   se obtiene la solución admisible que minimiza el esfuerzo cuadrático total $\sum f_i^2$.

En todas las construcciones factibles, el algoritmo comprueba y reporta residuales de equilibrio:
$$\text{res}_W = \left|\sum f_i - W\right| < 10^{-12}\text{ N}, \quad \text{res}_{M_x} < 10^{-12}\text{ N}\cdot\text{m}, \quad \text{res}_{M_y} < 10^{-12}\text{ N}\cdot\text{m}$$

---

## 4. Batería de Pruebas Ejecutadas

Las pruebas fueron ejecutadas con el script unitario automatizado `salidas/test_equilibrio.py` (13 pruebas, 100% exitosas en 0.001 s).

### Resumen de Pruebas Ejecutadas

| Categoría | Caso de Prueba | Parámetros | Resultado Esperado | Resultado Obtenido | Estado |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Simetría** | Invariancia en los 4 cuadrantes | $(\pm 0.04, \pm 0.02)\text{ m}$, $(\pm 0.08, \pm 0.03)\text{ m}$ | Factibilidad y holgura $\Delta f_4$ idénticas | Factibilidad idéntica, residual holgura $< 10^{-9}\text{ N}$ | **PASS** |
| **Simetría** | Permutación por reflexión longitudinal | $x \to -x$ | $f_1 \leftrightarrow f_3, \; f_2 \leftrightarrow f_4$ | Coincidencia numérica exacta ($< 10^{-7}\text{ N}$) | **PASS** |
| **Simetría** | Permutación por reflexión lateral | $y \to -y$ | $f_1 \leftrightarrow f_2, \; f_3 \leftrightarrow f_4$ | Coincidencia numérica exacta ($< 10^{-7}\text{ N}$) | **PASS** |
| **Centrado** | 5 kg CG centrado con $F_{\text{máx}} = 20.58\text{ N}$ | $(0, 0)\text{ m}$, $W = 49.033\text{ N}$ | $f_i = 12.2583\text{ N}$, margen $8.32\text{ N}$ | $f_i = 12.2583125\text{ N}$, margen $8.3217\text{ N}$, residuales $0.00\text{ N}$ | **PASS** |
| **Centrado** | 5 kg CG centrado con $F_{\text{máx}} = 25.00\text{ N}$ | $(0, 0)\text{ m}$, $W = 49.033\text{ N}$ | $f_i = 12.2583\text{ N}$, margen $12.74\text{ N}$ | $f_i = 12.2583125\text{ N}$, margen $12.7417\text{ N}$ | **PASS** |
| **Borde** | Borde longitudinal 5 kg, $F_{\text{máx}} = 20.58\text{ N}$ | $(0.160, 0.000)\text{ m}$ | No Factible (falta $7.87\text{ N}$, $2 F_{\text{máx}} = 41.16 < 49.03\text{ N}$) | No Factible, holgura $\Delta f_4 = -7.87325\text{ N}$ | **PASS** |
| **Borde** | Borde longitudinal 5 kg, $F_{\text{máx}} = 25.00\text{ N}$ | $(0.160, 0.000)\text{ m}$ | Factible en límite ($2 F_{\text{máx}} = 50.0 \ge 49.03\text{ N}$) | Factible, $f_1=f_2=0$, $f_3=f_4=24.5166\text{ N}$, holgura $0.000\text{ N}$ | **PASS** |
| **Borde** | Borde lateral 5 kg | $(0.000, 0.076)\text{ m}$ | No Factible con 20.58 N, Factible con 25.00 N | No Factible (20.58 N) / Factible (25.00 N) | **PASS** |
| **Borde** | Esquina extrema 5 kg | $(0.160, 0.076)\text{ m}$ | No Factible en ambos (un solo ventilador requiere $49.03\text{ N}$) | No Factible en ambos ($f_4$ requeriría $49.033\text{ N} > F_{\text{máx}}$) | **PASS** |
| **Borde** | Borde con masa reducida (3.5 kg) | $(0.160, 0.000)\text{ m}$, $W = 34.32\text{ N}$ | Factible con $F_{\text{máx}} = 20.58\text{ N}$ | Factible, $f_3=f_4=17.1616\text{ N} \le 20.58\text{ N}$ | **PASS** |
| **Referencia** | Comparación `INFORME-VERTICAL.md` | $x = 0.096\text{ m}$ | Factible ("Sí, con poco margen ideal", $F_{z,\max} = 51.45\text{ N}$) | Factible, Capacidad $= 51.45\text{ N}$, holgura $1.93\text{ N}$ | **PASS** |
| **Referencia** | Comparación `INFORME-VERTICAL.md` | $x = 0.120\text{ m}$ | No Factible ($F_{z,\max} = 47.04\text{ N} < 49.03\text{ N}$) | No Factible, Capacidad $= 47.04\text{ N}$, holgura $-1.74\text{ N}$ | **PASS** |
| **Fuerza Total** | Empuje insuficiente ($4 F_{\text{máx}} < W$) | $m = 5\text{ kg}, F_{\text{máx}} = 10.0\text{ N}$ ($4 F_{\text{máx}} = 40 < 49.03\text{ N}$) | No Factible en todo el espacio | No Factible en $(0,0)$, holgura negativa | **PASS** |
| **Fuerza Total** | Masa pesada (10 kg, $W = 98.07\text{ N}$) | $m = 10\text{ kg}$, $F_{\text{máx}} = 20.58\text{ N}$ ($82.32\text{ N}$) vs $25\text{ N}$ ($100\text{ N}$) | 20.58 N imposible; 25 N factible solo cerca de $(0,0)$ | Infeasible en 20.58 N; Factible en (0,0) para 25 N con margen $0.48\text{ N}$ | **PASS** |

---

## 5. Análisis de la Matriz de Posiciones Hipotéticas (5 kg)

Se evaluó una malla estructurada de **945 posiciones hipotéticas de CG** distribuidas en $[-0.160, +0.160]\text{ m} \times [-0.076, +0.076]\text{ m}$, comparando $F_{\text{máx}} = 20.58\text{ N}$ frente a $F_{\text{máx}} = 25.00\text{ N}$.

### 5.1 Estadísticas Globales de Factibilidad

| Métrica | $F_{\text{máx}} = 20.58\text{ N}$ (Base Ideal) | $F_{\text{máx}} = 25.00\text{ N}$ (Dimensionamiento) | Impacto / Diferencia |
| :--- | :---: | :---: | :---: |
| **Total de posiciones evaluadas** | 945 | 945 | — |
| **Posiciones factibles** | **291** (30.8%) | **473** (50.1%) | **+182 posiciones (+62.5% de área útil)** |
| **Posiciones no factibles** | 654 (69.2%) | 472 (49.9%) | -182 posiciones |
| **Capacidad vertical en $(0,0)$** | $82.32\text{ N}$ | $100.00\text{ N}$ | $+17.68\text{ N}$ |
| **Aceleración neta en $(0,0)$** | $+0.679\text{ g}$ | $+1.039\text{ g}$ | $+0.360\text{ g}$ |
| **Margen motriz en $(0,0)$** | $8.32\text{ N}$ | $12.74\text{ N}$ | $+4.42\text{ N}$ |

### 5.2 Comparación en Puntos Notables del Eje Longitudinal ($y = 0$)

| $x_{cg}$ CAD | $F_{\text{máx}} = 20.58\text{ N}$ Factible | Holgura $\Delta f_4$ (20.58 N) | $F_{z,\max}$ (20.58 N) | $F_{\text{máx}} = 25.00\text{ N}$ Factible | Holgura $\Delta f_4$ (25.00 N) | $F_{z,\max}$ (25.00 N) | Estado Comparativo |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **$0.000\text{ m}$** | **SÍ** | $+16.64\text{ N}$ | $82.32\text{ N}$ | **SÍ** | $+24.52\text{ N}$ | $100.00\text{ N}$ | Amplía margen motriz (+53%) |
| **$+0.040\text{ m}$** | **SÍ** | $+10.51\text{ N}$ | $65.86\text{ N}$ | **SÍ** | $+18.39\text{ N}$ | $80.00\text{ N}$ | Amplía margen motriz |
| **$+0.080\text{ m}$** | **SÍ** | $+4.39\text{ N}$ | $54.88\text{ N}$ | **SÍ** | $+12.26\text{ N}$ | $66.67\text{ N}$ | Amplía margen motriz |
| **$+0.096\text{ m}$** | **SÍ** | $+1.93\text{ N}$ | $51.45\text{ N}$ | **SÍ** | $+9.81\text{ N}$ | $62.50\text{ N}$ | Convierte caso marginal en holgado |
| **$+0.120\text{ m}$** | **NO** | $-1.74\text{ N}$ | $47.04\text{ N}$ | **SÍ** | $+6.13\text{ N}$ | $57.14\text{ N}$ | **Recupera factibilidad (+10.1 N capacidad)** |
| **$+0.160\text{ m}$** | **NO** | $-7.87\text{ N}$ | $41.16\text{ N}$ | **SÍ** | $0.00\text{ N}$ | $50.00\text{ N}$ | **Alcanza el límite geométrico exacto** |

---

## 6. Limitaciones del Modelo

1. **Modelo estático puro:** No modela derivadas de estabilidad dinámica, efectos inerciales, amortiguamiento ni respuesta transitoria del control.
2. **Ausencia de mapa instalado:** No incluye pérdidas aerodinámicas inducidas por conductos, distorsión en la entrada de aire, soplado sobre el fuselaje o interacción suelo/pared.
3. **Ausencia de fuerzas horizontales:** No contempla maniobras en plano horizontal, viento incidente ni inclinación de conos de empuje.
4. **Desacoplamiento giroscópico:** No considera el momento angular residual de los 4 rotores (aunque la rotación nominal es CCW/CW/CW/CCW, desaceleraciones asimétricas inducen pares de guiñada).
5. **Datos de integración preliminares:** La masa objetivo de 5 kg y la posición nominal son metas de diseño conceptual, no mediciones de un prototipo físicamente integrado.

---

## 7. Entregables Generados en `salidas/`

Todos los archivos han sido generados autónomamente dentro de este directorio:

1. **`salidas/equilibrio_cg.py`**:
   Módulo principal en Python que contiene la geometría, la derivación analítica del intervalo de $f_4$, el resolvedor de factibilidad, la asignación de fuerzas (centro y pseudo-inversa) y el cálculo de capacidades máximas.
2. **`salidas/test_equilibrio.py`**:
   Suite de pruebas automatizadas en `unittest` que ejecuta y valida las 13 pruebas obligatorias (simetría, masa 5 kg, borde longitudinal/lateral/esquina, falta de fuerza total, coherencia con `INFORME-VERTICAL.md` y residuales numéricos).
3. **`salidas/generar_matrices_csv.py`**:
   Script de generación que muestrea la malla bidimensional de 945 puntos y calcula los estados analíticos para ambas hipótesis de empuje.
4. **`salidas/matriz_posiciones_cg_Fmax20_58N.csv`**:
   Matriz CSV detallada con las 945 posiciones evaluadas para $F_{\text{máx}} = 20.58\text{ N}$, indicando cotas $[f_{4,\min}, f_{4,\max}]$, holgura, fuerzas individuales, residuales y capacidad máxima.
5. **`salidas/matriz_posiciones_cg_Fmax25_00N.csv`**:
   Matriz CSV homóloga para $F_{\text{máx}} = 25.00\text{ N}$.
6. **`salidas/matriz_posiciones_cg_comparativa.csv`**:
   Matriz consolidada punto a punto que clasifica cada posición hipotética de CG según su ganancia de factibilidad (`AMPLIA_MARGEN`, `NUEVA_FACTIBLE`, `AMBAS_NO_FACTIBLE`).
7. **`salidas/INFORME_EQUILIBRIO_CG.md`**:
   Este informe técnico exhaustivo en Markdown.
