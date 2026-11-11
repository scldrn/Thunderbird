# Informe Técnico: Modelos Normalizados de Respuesta Dinámica de Actuador (1er Orden vs 2do Orden Crítico)

**Proyecto:** Caracterización y Comparación Dinámica de Actuadores Propulsores  
**Entorno de ejecución:** Espacio de trabajo aislado (`salidas/`)  
**Fecha:** Noviembre 2026  
**Autor:** Antigravity (Ingeniería de Dinámica y Control)

---

## 1. Resumen Ejecutivo

En este documento se evalúan de forma analítica, numérica y experimental en código los modelos normalizados de respuesta al escalón para actuadores propulsores:
1. **Modelo de Primer Orden:**
   $$y_1(t) = 1 - e^{-t/\tau}, \quad t \ge 0$$
2. **Modelo de Segundo Orden Críticamente Amortiguado ($\zeta = 1$):**
   $$y_2(t) = 1 - \left(1 + \frac{t}{\tau}\right) e^{-t/\tau}, \quad t \ge 0$$

El estudio analiza tres constantes de tiempo supuestas: $\tau \in \{0.08, 0.20, 0.50\}\text{ s}$. Se calculan con precisión cerrada e hiper-precisión numérica los tiempos característicos al 10%, 50% y 90% de la consigna ($t_{10\%}, t_{50\%}, t_{90\%}$), así como el tiempo de subida $t_{10\to 90\%}$. Se efectúa un control exhaustivo de continuidad, regularidad y límites físicos y matemáticos en los dominios $t \ge 0$ y $\tau > 0$ ($t \to 0^+$, $t \to \infty$, $\tau \to 0^+$, $\tau \to \infty$).

Adicionalmente, se integra el efecto de saturación por rampa de aceleración de variadores electrónicos (ESC / *slew-rate*), motivado conceptualmente por las observaciones de dinámica de actuadores reportadas en la literatura técnica de la NASA (*Weinstein y colaboradores, AIAA SciTech 2024, NASA NTRS 20230017299*), demostrando cómo una cota máxima de rampa altera los tiempos transitorios reales frente a los modelos lineales puros.

---

## 2. Distinción Metodológica: Datos Medidos, Supuestos y Cálculos

Para preservar la integridad y trazabilidad técnica, se clasifica de manera estricta el origen de cada dato:

```
+---------------------------------------------------------------------------------------------------+
|                                     DISTINCIÓN METODOLÓGICA                                       |
+-----------------------------------+--------------------------------+------------------------------+
| DATOS MEDIDOS                     | SUPUESTOS TÉCNICOS             | CÁLCULOS Y SIMULACIONES      |
+-----------------------------------+--------------------------------+------------------------------+
| • Cero datos medidos para el      | • Constantes tau in {0.08,     | • Tiempos t10, t50, t90      |
|   vehículo analizado.             |   0.20, 0.50} s supuestas como |   analíticos y numéricos.    |
| • Ensayos NASA NTRS 20230017299   |   hipótesis de trabajo y       | • Factores u = t/tau         |
|   (Weinstein y col., 2024) sobre  |   análisis de sensibilidad.    |   invariantes de escala.     |
|   ventilador Jetfan 130 Pro en    | • NO se atribuyen los tau al   | • Inversión de 2do orden     |
|   túnel de 12 pies de Langley.    |   vehículo ni a NASA.          |   vía Halley (|res| < 1e-14).|
| • Mediciones de NASA pertenecen a | • Cota de rampa supuesta       | • Límites analíticos y cotas |
|   dicha unidad aislada; NO son    |   R ~ 2.381 s^-1 (derivada de  |   Lipschitz de continuidad.  |
|   calibración de este ejemplo ni  |   50 N/s para módulo de 21 N). | • Solución analítica y RK4   |
|   se transfieren al vehículo.     | • Escalón unitario ideal t=0.  |   de orden 4 con rampa.      |
+-----------------------------------+--------------------------------+------------------------------+
```

### 2.1. Datos Medidos
- **Vehículo bajo estudio:** No se dispone de mediciones experimentales directas para el vehículo (cero curvas en banco de pruebas ni caracterización instalada de conductos). No se asume que un archivo no copiado no exista, ni que una reserva sin masa asignada tenga masa real nula o no nula.
- **Referencia NASA NTRS 20230017299 (Weinstein y colaboradores, AIAA SciTech 2024):**
  - Unidad ensayada: Ventilador **Jetfan 130 Pro** probado aisladamente en el túnel de baja velocidad de 12 pies de NASA Langley.
  - Geometría: 10 palas de rotor y 7 álabes fijos de estator; diámetro de pala de 5,11 pulgadas (129,8 mm); diámetro exterior del conducto de 5,23 pulgadas (132,8 mm).
  - Motor: masa indicada de 1.100 g, diámetro de 56 mm y 7 kW de potencia continua máxima nominal.
  - Envolvente de ensayos: velocidad de rotación de 2.875 a 25.150 rpm, empuje estático de 0 a 21,25 lbf (0 a 94,5 N) y potencia eléctrica DC suministrada de 190 a 6.420 W. Estos extremos describen el conjunto de pruebas y **no se asumen medidos en un mismo punto de operación**. Incidencia de 0° a 30° y presión dinámica de 0 a 6 psf.
  - Comportamiento dinámico: Los autores ajustaron un modelo de segundo orden para la velocidad del motor, constatando que la rampa interna del controlador y la amplitud del escalón determinan el transitorio real.
  - **Función de la referencia:** Esta fuente sirve de motivación física sobre la existencia de dinámicas de orden superior y saturación por rampa en ventiladores canalizados, **no como calibración de este ejemplo ni del vehículo**.

### 2.2. Supuestos Técnicos
- **Constantes de tiempo:** $\tau = 0.08\text{ s}$, $\tau = 0.20\text{ s}$ y $\tau = 0.50\text{ s}$ son supuestos técnicos de análisis de sensibilidad; **no se atribuyen al vehículo ni a NASA**.
- **Entrada y amortiguamiento:** Escalón unitario normalizado en $t = 0$ con retardo puro cero de transporte digital. Amortiguamiento crítico idealizado ($\zeta = 1.0$) en el modelo de segundo orden.
- **Cota de rampa:** Tasa máxima supuesta de $50\text{ N/s}$ normalizada frente a una fuerza nominal de módulo de $21\text{ N}$, definiendo $R = \frac{50\text{ N/s}}{21\text{ N}} \approx 2.38095\text{ s}^{-1}$.

### 2.3. Cálculos
- Expresiones analíticas exactas para el modelo de 1er orden.
- Raíces del modelo de 2do orden mediante el método cúbico de Halley ($|\text{residual}| < 10^{-14}$) y formulación analítica vía función $W_{-1}$ de Lambert.
- Integración temporal Runge-Kutta de 4to orden (RK4) con paso $\Delta t = 10^{-5}\text{ s}$ para el régimen no lineal saturado por rampa.

---

## 3. Formulación de los Modelos Dinámicos Normalizados

### 3.1. Modelo de Primer Orden
Representa un sistema lineal de polo simple en $s = -1/\tau$:
$$G_1(s) = \frac{1}{\tau s + 1}$$

- **Respuesta temporal al escalón unitario causal ($t \ge 0$):**
  $$y_1(t) = 1 - e^{-t/\tau}, \quad t \ge 0 \quad (y_1(t) = 0 \text{ para } t < 0)$$
- **Primera derivada (velocidad de cambio):**
  $$\dot{y}_1(t) = \frac{1}{\tau} e^{-t/\tau}, \quad t > 0; \quad \lim_{t \to 0^+} \dot{y}_1(t) = \frac{1}{\tau}\text{ s}^{-1}$$
  Presenta un salto finito de pendiente en $t = 0$ (desde 0 para $t < 0$ hasta $1/\tau$ para $t > 0$), reflejando ausencia de inercia rotacional en el modelo.
- **Segunda derivada (curvatura):**
  $$\ddot{y}_1(t) = -\frac{1}{\tau^2} e^{-t/\tau} < 0 \quad \forall t \ge 0$$
  La respuesta es estrictamente cóncava hacia abajo desde el inicio. No posee punto de inflexión.
- **Tiempo analítico al porcentaje $p \in (0, 1)$:**
  $$1 - e^{-t/\tau} = p \implies t_1(p) = -\tau \ln(1 - p)$$
  Variable adimensional universal $u_1(p) = t_1(p)/\tau = -\ln(1 - p)$.

### 3.2. Modelo de Segundo Orden Críticamente Amortiguado ($\zeta = 1$)
Representa un sistema con polo doble real en $s = -1/\tau$ ($\omega_n = 1/\tau$):
$$G_2(s) = \frac{1}{(\tau s + 1)^2} = \frac{\omega_n^2}{(s + \omega_n)^2}$$

- **Respuesta temporal al escalón unitario causal ($t \ge 0$):**
  $$y_2(t) = 1 - \left(1 + \frac{t}{\tau}\right) e^{-t/\tau}, \quad t \ge 0 \quad (y_2(t) = 0 \text{ para } t < 0)$$
- **Primera derivada:**
  $$\dot{y}_2(t) = \frac{t}{\tau^2} e^{-t/\tau}, \quad t \ge 0$$
  En $t = 0$, $\dot{y}_2(0) = 0$. La función posee regularidad $C^1$ en el origen: parte tangencialmente horizontal, modelando la inercia del rotor.
- **Segunda derivada y punto de inflexión:**
  $$\ddot{y}_2(t) = \frac{1}{\tau^2}\left(1 - \frac{t}{\tau}\right) e^{-t/\tau}$$
  En $t = 0^+$, $\ddot{y}_2(0^+) = \frac{1}{\tau^2} > 0$ (aceleración positiva, convexidad).  
  En **$t = \tau$**, $\ddot{y}_2(\tau) = 0$: **punto de inflexión exacto**.  
  Valor en la inflexión: $y_2(\tau) = 1 - \frac{2}{e} \approx 0.264241$ ($26.42\%$).  
  Pendiente máxima: $\dot{y}_{2,\max} = \dot{y}_2(\tau) = \frac{1}{e \cdot \tau} \approx \frac{0.367879}{\tau}\text{ s}^{-1}$.
- **Tiempo característico al porcentaje $p \in (0, 1)$:**
  $$(1 + u) e^{-u} = 1 - p \implies -(1 + u) e^{-(1+u)} = -\frac{1 - p}{e}$$
  $$u_2(p) = -1 - W_{-1}\left(-\frac{1 - p}{e}\right)$$
  donde $W_{-1}$ representa la rama secundaria real de la función $W$ de Lambert.

---

## 4. Tablas Comparativas de Resultados

### 4.1. Tiempos de Respuesta Lineales (Sin Limitación de Rampa)

| Modelo Dinámico | $\tau$ (s) | $t_{10\%}$ (ms) | $t_{50\%}$ (ms) | $t_{90\%}$ (ms) | $t_{10\to 90\%}$ (ms) | Pendiente Máx ($\text{s}^{-1}$) | $t_{\text{inflex}}$ (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **1er orden** | **0.08** | 8.43 | 55.45 | 184.21 | 175.78 | 12.50 | N/A |
| **2do orden crít.** | **0.08** | **42.54** | **134.27** | **311.18** | **268.63** | 4.60 | 0.08 |
| **1er orden** | **0.20** | 21.07 | 138.63 | 460.52 | 439.44 | 5.00 | N/A |
| **2do orden crít.** | **0.20** | **106.36** | **335.67** | **777.94** | **671.58** | 1.84 | 0.20 |
| **1er orden** | **0.50** | 52.68 | 346.57 | 1151.29 | 1098.61 | 2.00 | N/A |
| **2do orden crít.** | **0.50** | **265.91** | **839.17** | **1944.86** | **1678.95** | 0.74 | 0.50 |

### 4.2. Ratios y Retardos Relativos (2do Orden frente a 1er Orden)

| $\tau$ (s) | $\Delta t_{10\%}$ (ms) | Ratio $t_{10\%}$ | $\Delta t_{50\%}$ (ms) | Ratio $t_{50\%}$ | $\Delta t_{90\%}$ (ms) | Ratio $t_{90\%}$ | $\Delta t_{10\to 90}$ (ms) | Ratio Subida |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **0.08** | +34.12 ms (+404.8%) | **5.0475x** | +78.82 ms (+142.1%) | **2.4213x** | +126.97 ms (+68.9%) | **1.6893x** | +92.85 ms (+52.8%) | **1.5283x** |
| **0.20** | +85.29 ms (+404.8%) | **5.0475x** | +197.04 ms (+142.1%) | **2.4213x** | +317.43 ms (+68.9%) | **1.6893x** | +232.14 ms (+52.8%) | **1.5283x** |
| **0.50** | +213.23 ms (+404.8%) | **5.0475x** | +492.60 ms (+142.1%) | **2.4213x** | +793.57 ms (+68.9%) | **1.6893x** | +580.34 ms (+52.8%) | **1.5283x** |

### 4.3. Coeficientes Adimensionales Universales ($u = t/\tau$)

Al adimensionalizar el tiempo ($u = t/\tau$), los coeficientes resultan estrictamente invariantes respecto a $\tau$:

| Métrica | 1er Orden ($u_1$) | 2do Orden Crítico ($u_2$) | Ratio Universal ($u_2 / u_1$) | Expresión Analítica |
|---|---:|---:|---:|---|
| **$u_{10\%}$** | 0.105361 | 0.531812 | **5.0475x (+404.75%)** | $u_1 = -\ln(0.9)$, $u_2 = -1 - W_{-1}(-0.9/e)$ |
| **$u_{50\%}$** | 0.693147 | 1.678347 | **2.4213x (+142.13%)** | $u_1 = \ln(2)$, $u_2 = -1 - W_{-1}(-0.5/e)$ |
| **$u_{90\%}$** | 2.302585 | 3.889720 | **1.6893x (+68.93%)** | $u_1 = \ln(10)$, $u_2 = -1 - W_{-1}(-0.1/e)$ |
| **$\Delta u_{10\to 90\%}$** | 2.197225 | 3.357909 | **1.5283x (+52.83%)** | $\Delta u_1 = \ln(9)$, $\Delta u_2 = u_{2,90} - u_{2,10}$ |

> **Hallazgo clave:** En el arranque de la respuesta ($10\%$), el modelo de segundo orden tarda **más de 5 veces más** que el de primer orden ($+404.8\%$). Esta latencia inicial representa un "tiempo muerto efectivo" producido por la inercia física, que degrada severamente el margen de fase en bucles rápidos de estabilización si se diseña asumiendo primer orden.

---

## 5. Control de Límites Físicos, Matemáticos y Continuidad

### 5.1. Continuidad en $t = 0$ y Regularidad $C^1$
- Para ambos modelos, la respuesta escalón causal satisface:
  $$\lim_{t \to 0^-} y(t) = y(0) = \lim_{t \to 0^+} y(t) = 0$$
  garantizando continuidad $C^0$ en el origen.
- **Contraste de regularidad de la primera derivada:**
  - En **segundo orden**, $\lim_{t \to 0^-} \dot{y}_2(t) = 0 = \dot{y}_2(0) = \lim_{t \to 0^+} \dot{y}_2(t)$. La derivada es continua en el origen (**regularidad $C^1$**).
  - En **primer orden**, $\lim_{t \to 0^-} \dot{y}_1(t) = 0 \ne \lim_{t \to 0^+} \dot{y}_1(t) = \frac{1}{\tau}$. Hay una discontinuidad de salto finito de magnitud $\frac{1}{\tau}$, no admisible físicamente para la velocidad de rotación de un rotor real.

### 5.2. Continuidad Uniforme y Propiedad de Lipschitz en $t \ge 0$
Ambas funciones satisfacen la condición de Lipschitz $|y(t_2) - y(t_1)| \le L |t_2 - t_1|$ en todo el semieje no negativo $[0, \infty)$:
- Para primer orden: $L_1 = \sup_{t \ge 0} |\dot{y}_1(t)| = \frac{1}{\tau}$.
- Para segundo orden: $L_2 = \sup_{t \ge 0} |\dot{y}_2(t)| = \dot{y}_2(\tau) = \frac{1}{e \cdot \tau}$.

### 5.3. Límites en el Dominio Temporal $t \ge 0$
- **Monotonía y acotamiento:** Para todo $t > 0$, $\dot{y}_1(t) > 0$ y $\dot{y}_2(t) > 0$, por lo que ambas funciones son estrictamente crecientes y acotadas en el intervalo $[0, 1)$.
- **Dominancia estricta:** Para cualquier $t > 0$ y mismo $\tau$:
  $$y_1(t) - y_2(t) = \frac{t}{\tau} e^{-t/\tau} > 0 \implies y_1(t) > y_2(t)$$
  El primer orden siempre lidera temporalmente al segundo orden.
- **Límite asintótico ($t \to \infty$):**
  $$\lim_{t \to \infty} y_1(t) = 1, \quad \lim_{t \to \infty} y_2(t) = 1$$
  Los errores remanentes $e_1(t) = e^{-t/\tau}$ y $e_2(t) = (1 + t/\tau)e^{-t/\tau}$ satisfacen:
  $$\frac{e_2(t)}{e_1(t)} = 1 + \frac{t}{\tau} \xrightarrow[t \to \infty]{} \infty$$

### 5.4. Límites en el Dominio de Parámetro $\tau > 0$
- **Requisito de estabilidad física:** $\tau > 0$ es estrictamente exigido; valores $\tau \le 0$ son rechazados con excepción `ValueError`.
- **Límite $\tau \to 0^+$ (Actuador ideal/instantáneo):**
  Para cualquier $t > 0$ fijo: $\lim_{\tau \to 0^+} y_1(t) = 1$ y $\lim_{\tau \to 0^+} y_2(t) = 1$.  
  Los tiempos característicos $t_{10\%}, t_{50\%}, t_{90\%} \to 0$.
- **Límite $\tau \to \infty$ (Actuador congelado):**
  Para cualquier $t \ge 0$ finito: $\lim_{\tau \to \infty} y_1(t) = 0$ y $\lim_{\tau \to \infty} y_2(t) = 0$.  
  Los tiempos característicos divergen a $+\infty$.
- **Escala lineal:** $\frac{\partial t_p}{\partial \tau} = u_p > 0$. Duplicar $\tau$ duplica con exactitud analítica todos los tiempos característicos.

---

## 6. Dinámica no Lineal: Rampas de ESC (Slew-Rate) y Motivación NASA

### 6.1. Observaciones en Ensayos de NASA (Weinstein y col., SciTech 2024, NTRS 20230017299)
En el informe de Weinstein y colaboradores sobre el ventilador **Jetfan 130 Pro**, los autores observaron que ante escalones de aceleración comandados, la respuesta en rpm del motor no responde a un filtro lineal simple, sino que está fuertemente dominada por la **rampa de aceleración programada en el microcódigo del variador electrónico (ESC)**. Dicha rampa limita deliberadamente la derivada de conmutación ($\text{d}\Omega/\text{dt}$) para prevenir pérdidas de sincronismo magnético (*desync*), sobrecorrientes en los transistores MOSFET y colapsos de tensión en la línea de continua.

### 6.2. Cuantificación sobre la Hipótesis de Simulación
Asumiendo la cota supuesta de rampa de $50\text{ N/s}$ frente a $21\text{ N}$ nominales:
$$R = \frac{50\text{ N/s}}{21\text{ N}} \approx 2.38095\text{ s}^{-1}$$

- Para **primer orden con $\tau = 0.08\text{ s}$**, la derivada inicial teórica es:
  $$\dot{y}_1(0^+) = \frac{1}{0.08} = 12.50\text{ s}^{-1} \gg 2.381\text{ s}^{-1} \quad (5.25\times \text{ la cota admisible})$$
  El sistema satura inmediatamente y opera en régimen de rampa pura $y(t) = R \cdot t$ durante $t_{\text{sat}} = \frac{1 - R\tau}{R} \approx 340.0\text{ ms}$ (hasta alcanzar el $80.95\%$ de consigna).
- Para **segundo orden con $\tau = 0.08\text{ s}$**, la pendiente máxima en $t = \tau$ es:
  $$\dot{y}_{2,\max} = \frac{1}{e \cdot 0.08} \approx 4.598\text{ s}^{-1} > 2.381\text{ s}^{-1} \quad (+93\% \text{ sobre la cota})$$
  También experimenta saturación por rampa en su tramo de máxima aceleración.

### 6.3. Comparativa: Modelo Lineal vs Modelo con Rampa ($R \approx 2.381\text{ s}^{-1}$)

| Modelo | $\tau$ (s) | $t_{10\%}$ Lineal (ms) | $t_{10\%}$ c/ Rampa (ms) | $t_{50\%}$ Lineal (ms) | $t_{50\%}$ c/ Rampa (ms) | $t_{90\%}$ Lineal (ms) | $t_{90\%}$ c/ Rampa (ms) | Incremento en $t_{90\%}$ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **1er orden** | **0.08** | 8.43 | **42.00** | 55.45 | **210.00** | 184.21 | **391.55** | **+207.34 ms (+112.6%)** |
| **2do orden crít.** | **0.08** | 42.54 | **50.87** | 134.27 | **218.87** | 311.18 | **432.14** | **+120.96 ms (+38.9%)** |
| **1er orden** | **0.20** | 21.07 | **42.00** | 138.63 | **210.00** | 460.52 | **532.13** | **+71.61 ms (+15.6%)** |
| **2do orden crít.** | **0.20** | 106.36 | **106.36** | 335.67 | **335.66** | 777.94 | **777.94** | **0.00 ms (No satura)** |
| **1er orden** | **0.50** | 52.68 | **52.68** | 346.57 | **346.57** | 1151.29 | **1151.29** | **0.00 ms (No satura)** |
| **2do orden crít.** | **0.50** | 265.91 | **265.90** | 839.17 | **839.16** | 1944.86 | **1944.86** | **0.00 ms (No satura)** |

---

## 7. Verificación Experimental en Sandbox y Pruebas Unitarias

Se diseñó e implementó la suite completa de pruebas unitarias en [`salidas/test_respuestas.py`](file:///private/tmp/aero_20261108T040057Z_075131ca_9_f47he_/entregable_dinamica_actuador/salidas/test_respuestas.py), ejecutada en Python 3 puro.

### 7.1. Resumen de Pruebas Ejecutadas (26 de 26 superadas, 100% éxito)
El registro de ejecución se encuentra en [`salidas/pruebas_ejecutadas.txt`](file:///private/tmp/aero_20261108T040057Z_075131ca_9_f47he_/entregable_dinamica_actuador/salidas/pruebas_ejecutadas.txt):
1. `test_tau_positive_constraint`: Verificación de rechazo con `ValueError` para $\tau \le 0$ ($0.0$, $-0.01$, $-0.5$, $-10.0$).
2. `test_percentage_open_interval_constraint`: Verificación de rechazo con `ValueError` para $p \notin (0, 1)$.
3. `test_rate_positive_constraint`: Verificación de rechazo para tasas de rampa $R \le 0$.
4. `test_first_order_exact_formula_and_residuals`: Residual analítico $|y_1(t_1(p)) - p| < 10^{-15}$.
5. `test_second_order_solver_residuals`: Residual numérico vía Halley $|y_2(t_2(p)) - p| < 10^{-14}$.
6. `test_known_analytical_values`: Coincidencia exacta con $\ln(2)$, $\ln(10)$, $-\ln(0.9)$ y raíces universales.
7. `test_scaling_invariance_u_dimensionless`: Invarianza estricta de $u_p = t_p / \tau$ sobre 6 órdenes de magnitud de $\tau$.
8. `test_universal_relative_delay_ratios`: Factores relativos universales ($5.0475$, $2.4213$, $1.6893$, $1.5283$).
9. `test_strict_temporal_ordering`: Comprobación de monotonía temporal $0 < t_{10\%} < t_{50\%} < t_{90\%}$.
10. `test_continuity_at_t_zero`: Comprobación de límites laterales $\lim_{t \to 0^-} y = y(0) = \lim_{t \to 0^+} y = 0$.
11. `test_derivative_continuity_contrast_at_t_zero`: Continuidad $C^1$ de $\dot{y}_2$ frente a discontinuidad de salto en $\dot{y}_1$.
12. `test_continuity_over_t_ge_0_lipschitz`: Verificación de cotas de Lipschitz $L_1 = 1/\tau$ y $L_2 = 1/(e\tau)$.
13. `test_rate_limited_continuity_at_switching_point`: Continuidad de valor y derivada en la transición $t_{\text{sat}}$.
14. `test_causality_for_t_negative`: Causalidad estricta ($y = 0$ para $t < 0$).
15. `test_initial_boundary_t_zero`: Valores iniciales de posición, velocidad y aceleración de respuesta en $t = 0$.
16. `test_monotonicity_and_bounds_for_t_positive`: Acotamiento en $(0, 1)$, $\dot{y} > 0$ y $y_1(t) > y_2(t)$ para $t > 0$.
17. `test_asymptotic_convergence_t_infinity`: Convergencia asintótica a 1 y ratio de error $e_2/e_1 = 1 + t/\tau$.
18. `test_second_order_inflection_point`: Comprobación de $\ddot{y}_2(\tau) = 0$, $y_2(\tau) = 1 - 2/e$ y $\dot{y}_{2,\max} = 1/(e\tau)$.
19. `test_limit_tau_approaching_zero_ultrafast`: Comprobación de colapso a escalón instantáneo para $\tau \to 0^+$.
20. `test_limit_tau_approaching_infinity_frozen`: Comprobación de respuesta nula para $\tau \to \infty$.
21. `test_linear_scaling_with_tau`: Comprobación de linealidad exacta $t_p(2\tau) = 2 t_p(\tau)$.
22. `test_rk4_convergence_rate_order_4`: Comprobación de orden 4 del integrador RK4 (reducción de error por factor $\approx 16$).
23. `test_rate_limit_inactive_when_R_large`: Coincidencia con lineal cuando $R \ge 1/\tau$.
24. `test_rate_limit_pure_ramp_phase`: Solución exacta $t(p) = p/R$ en régimen saturado.
25. `test_rate_limited_matches_simulation`: Coincidencia entre solución analítica y simulación temporal RK4.
26. `test_second_order_rate_limit_thresholds`: Umbrales de saturación condicional para segundo orden ($1/(e\tau) \gtrless R$).

---

## 8. Limitaciones Técnicas Respecto a Respuesta Real de Empuje y Control

Para evitar extrapolaciones indebidas en la síntesis de leyes de control, se enfatizan las siguientes limitaciones:

1. **No Linealidad Aerodinámica Cuadrática ($T \propto \Omega^2$):**  
   Los modelos analizados son lineales normalizados respecto a la consigna. En un propulsor real, el empuje estático generado escala cuadráticamente con la velocidad de giro ($\text{Empuje} \approx c_T \rho D^4 \Omega^2$). Un escalón de $0\%$ a $100\%$ de consigna produce una aceleración de empuje fuertemente no lineal, con baja ganancia de empuje inicial y muy alta al aproximarse a las rpm máximas.
2. **Efectos Aerodinámicos No Estacionarios:**  
   Durante transitorios rápidos de aceleración, la circulación alrededor de los perfiles de pala no se establece instantáneamente (efecto Wagner) y existe masa aparente de aire acelerada en el conducto, lo que introduce amortiguamientos y desfases adicionales no capturados por una función de transferencia lineal.
3. **Dinámica Eléctrica y Caída de Tensión de Batería (*Sag*):**  
   Bajo demandas bruscas de aceleración, las corrientes de pico demandadas provocan caídas transitorias de tensión en el bus de corriente continua por la resistencia interna de las celdas LiPo, reduciendo el par motor disponible ($Q = K_t I$) y dilatando el tiempo de respuesta real conforme disminuye el estado de carga (SoC).
4. **Retardos Puros de Transporte Digital:**  
   El modelo lineal continuo no incluye la latencia de muestreo del autopiloto (ej. 20 ms a 50 Hz), el retardo de serialización en el bus de control (PWM, DShot o CAN) ni el tiempo de filtrado digital en el ESC.
5. **No Transferibilidad de la Referencia NASA NTRS 20230017299:**  
   El estudio de Weinstein y colaboradores (AIAA SciTech 2024) evaluó un ventilador **Jetfan 130 Pro** (diámetro 130 mm, motor de 1.100 g y 7 kW nominal). Dicha planta propulsora posee una inercia rotacional ($J$) y escala aerodinámica completamente diferente a los módulos candidatos del vehículo analizado. Sus constantes de tiempo y curvas no se extrapolan ni transfieren a este ejemplo.
6. **Hipótesis de Amortiguamiento Crítico ($\zeta = 1$):**  
   Se asumió amortiguamiento crítico exacto para aislar la comparación teórica de orden. Los lazos de velocidad de variadores reales acoplados a rotores pueden presentar dinámicas subamortiguadas ($\zeta \in [0.7, 0.9]$) con sobreoscilaciones de corriente, o sobreamortiguadas ($\zeta > 1$) por filtros pasa-bajos.

---

## 9. Inventario de Archivos Generados

Todos los entregables solicitados se generaron autónomamente en `salidas/`:

1. [`salidas/comparar_respuestas.py`](file:///private/tmp/aero_20261108T040057Z_075131ca_9_f47he_/entregable_dinamica_actuador/salidas/comparar_respuestas.py): Módulo ejecutable en Python 3 puro con modelos analíticos, validaciones de dominio, cálculo de tiempos por Halley, simulación RK4 y generador de tablas.
2. [`salidas/test_respuestas.py`](file:///private/tmp/aero_20261108T040057Z_075131ca_9_f47he_/entregable_dinamica_actuador/salidas/test_respuestas.py): Suite automatizada de 26 pruebas unitarias que validan rigurosamente tiempos 10/50/90%, continuidad, límites $t \ge 0$ y $\tau > 0$, invarianza de escala y efectos de rampa.
3. [`salidas/tabla_comparativa.csv`](file:///private/tmp/aero_20261108T040057Z_075131ca_9_f47he_/entregable_dinamica_actuador/salidas/tabla_comparativa.csv): Tabla reproducible con todas las métricas dimensionales ($s$, $ms$, $s^{-1}$) y coeficientes adimensionales ($u$), incluyendo regímenes lineales y con limitación de rampa.
4. [`salidas/tabla_comparativa.md`](file:///private/tmp/aero_20261108T040057Z_075131ca_9_f47he_/entregable_dinamica_actuador/salidas/tabla_comparativa.md): Tablas comparativas formateadas en Markdown con notas metodológicas y desgloses de ratios.
5. [`salidas/datos_respuestas.json`](file:///private/tmp/aero_20261108T040057Z_075131ca_9_f47he_/entregable_dinamica_actuador/salidas/datos_respuestas.json): Base de datos estructurada con metadatos completos y clasificación taxativa de datos.
6. [`salidas/pruebas_ejecutadas.txt`](file:///private/tmp/aero_20261108T040057Z_075131ca_9_f47he_/entregable_dinamica_actuador/salidas/pruebas_ejecutadas.txt): Registro de ejecución de la suite de 26 pruebas unitarias (100% éxito).
7. [`salidas/INFORME.md`](file:///private/tmp/aero_20261108T040057Z_075131ca_9_f47he_/entregable_dinamica_actuador/salidas/INFORME.md): Presente informe técnico comprensivo.
