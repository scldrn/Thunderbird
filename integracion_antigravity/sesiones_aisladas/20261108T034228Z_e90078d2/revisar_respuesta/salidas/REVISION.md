# REVISION.md: Revisión Técnica de Respuestas Temporales de Actuador (1er y 2do Orden), Tiempos 10/50/90, Unidades, Tratamiento de Tau y Efecto de Rampas de ESC

**Proyecto:** Revisión de Dinámica y Respuesta Temporal de Ventiladores / Actuadores  
**Entorno de trabajo:** Espacio aislado de ejecución (`salidas/`)  
**Fecha:** Noviembre 2026  
**Auditor / Revisor:** Antigravity (Entorno autónomo sandbox)

---

## 1. Resumen de la Revisión y Objetivos

Se ha completado la revisión exhaustiva de los modelos de respuesta temporal de actuadores normalizados de primer orden y segundo orden críticamente amortiguado, la exactitud de los tiempos característicos al 10%, 50% y 90% ($t_{10\%}, t_{50\%}, t_{90\%}$), el tiempo de subida $t_{10\to 90\%}$, el tratamiento dimensional de las unidades y de la constante de tiempo $\tau$, así como la distinción estricta entre el ensayo experimental de la NASA y los supuestos teóricos del escenario C02.

Como parte del encargo:
1. Se copiaron a `salidas/` los archivos `comparar_respuestas.py` y `test_respuestas.py`.
2. Se ejecutaron en el entorno Python 3 del sandbox, verificando la generación de `tabla_comparativa.csv`, `tabla_comparativa.md`, `datos_respuestas.json` y el registro de pruebas en `pruebas_ejecutadas.txt`.
3. Se corroboró la superación del 100% de la suite de pruebas unitarias (19 pruebas ejecutadas con éxito).

---

## 2. Distinción Metodológica Rigurosa: Datos Medidos, Supuestos y Cálculos

Se establece una delimitación formal entre las fuentes empíricas, los supuestos de ingeniería y los cálculos matemáticos:

```
+---------------------------------------------------------------------------------------------------------+
|                                         DISTINCIÓN METODOLÓGICA                                         |
+------------------------------------+------------------------------------+-------------------------------+
| DATOS MEDIDOS                      | SUPUESTOS TÉCNICOS (ESCENARIO C02) | CÁLCULOS Y SIMULACIONES       |
+------------------------------------+------------------------------------+-------------------------------+
| • Ensayo NASA Weinstein et al.     | • CERO datos medidos para C02.     | • Soluciones analíticas       |
|   (AIAA SciTech 2024):             | • tau in {0.08, 0.20, 0.50} s      |   exactas de 1er y 2do orden. |
|   - Banco estático dinamométrico     (valores arbitrarios / hipótesis). | • Inversión de raíces vía     |
|     de la NASA.                    | • tau = 0.08 s asumido en          |   Halley de 3er orden         |
|   - EDF comercial Schübeler de       INFORME.md (simulacion_vuelo_A).   |   (|residuo| < 1e-14).        |
|     130 mm con motor Hacker.       | • tau = 0.20 s y 0.50 s como       | • Factores universales        |
|   - ESC comercial con limitador de   análisis de sensibilidad.          |   adimensionales u = t/tau.   |
|     rampa interno (slew-rate).     | • Cota de rampa vectorial max:     | • Integración temporal        |
|   - NO APLICABLE DIRECTAMENTE        50 N/s para 21 N max               |   RK4 (orden 4, dt=1e-4 s).   |
|     A C02 (diferente geometría,      (R ~ 2.381 s^-1) en C02.           | • Modelo analítico y Euler    |
|     masa, ducto y potencia).       | • Escalón unitario ideal en t=0.   |   con saturación de rampa ESC.|
+------------------------------------+------------------------------------+-------------------------------+
```

### 2.1. El Ensayo NASA (Weinstein et al., AIAA SciTech 2024)
- **Referencia:** Weinstein et al., *“Dynamic Characterization and Modeling of an Electric Ducted Fan for eVTOL Applications”*, AIAA SciTech Forum 2024.
- **Naturaleza:** **Dato medido en laboratorio para una planta física concreta**.
- **Detalle de la planta ensayada:** Un ventilador canalizado eléctrico (EDF) comercial Schübeler de **130 mm de diámetro**, accionado por un motor brushless Hacker y controlado por un variador electrónico (ESC) comercial sobre un banco estático dinamométrico de la NASA.
- **Hallazgos empíricos del ensayo:**
  1. La respuesta real ante escalones de media y gran amplitud está dominada por el limitador interno de aceleración (rampa/slew-rate) programado en el firmware del ESC.
  2. La respuesta dinámica no es puramente exponencial ni lineal: presenta una etapa de subida lineal de pendiente constante seguida por una aproximación asintótica.
  3. El tiempo de subida depende de la amplitud del escalón comandado ($\Delta u$).
  4. Existe una clara asimetría dinámica entre aceleración y deceleración.
- **Distinción respecto a C02:** **Ninguno de los valores de tiempo, inercia o constantes $\tau$ del artículo de la NASA constituye una medición de C02**. C02 posee una geometría de cuatro toberas/conductos internos, motores, hélices y masas motrices distintas. El artículo de la NASA sirve como **evidencia física del fenómeno de rampa de ESC**, pero no provee parámetros numéricos para C02.

### 2.2. Parámetros y Constantes del Escenario C02
- **Naturaleza:** **Supuestos teóricos e hipótesis de diseño**.
- **Cero mediciones:** Para el vehículo C02 **no existen ensayos experimentales en banco de tracción ni curvas dinámicas medidas**.
- **Origen de $\tau = 0.08\text{ s}$:** Proviene explícitamente de una hipótesis supuesta en el informe de simulación previa `simulacion_vuelo_A/INFORME.md`: *"Constante de respuesta de primer orden 0,08 s y tasa máxima de cambio vectorial 50 N/s por módulo a 5 kg, ambos supuestos"*.
- **Origen de $\tau = 0.20\text{ s}$ y $\tau = 0.50\text{ s}$:** Son constantes supuestas introducidas con propósitos de **estudio de sensibilidad paramétrica**, representando actuadores más pesados o lazos de control más lentos.
- **Origen de la cota de rampa $R \approx 2.381\text{ s}^{-1}$:** Hipótesis de $50\text{ N/s}$ dividida entre el empuje máximo nominal de $21\text{ N}$ de un módulo propulsor: $R = 50 / 21 \approx 2.38095\text{ s}^{-1}$.

---

## 3. Revisión Matemática de las Respuestas Temporales

### 3.1. Modelo de Primer Orden
Función de transferencia:
$$G_1(s) = \frac{1}{\tau s + 1}$$

- **Respuesta al escalón unitario ($t \ge 0$):**
  $$y_1(t) = 1 - e^{-t/\tau}$$
- **Primera derivada (velocidad de cambio):**
  $$\dot{y}_1(t) = \frac{1}{\tau} e^{-t/\tau}$$
  En $t = 0^+$, la tasa es máxima: $\dot{y}_1(0^+) = \frac{1}{\tau}\text{ s}^{-1}$. Físicamente, asume una aceleración infinita del rotor en $t=0$, lo cual viola la inercia real.
- **Segunda derivada (curvatura / aceleración de salida):**
  $$\ddot{y}_1(t) = -\frac{1}{\tau^2} e^{-t/\tau} < 0 \quad \forall t \ge 0$$
  La función es estrictamente cóncava hacia abajo en todo su dominio. No posee punto de inflexión.

### 3.2. Modelo de Segundo Orden Críticamente Amortiguado ($\zeta = 1$)
Función de transferencia con polo real doble en $s = -1/\tau$ ($\omega_n = 1/\tau$):
$$G_2(s) = \frac{1}{(\tau s + 1)^2} = \frac{\omega_n^2}{(s + \omega_n)^2}$$

- **Respuesta al escalón unitario ($t \ge 0$):**
  $$y_2(t) = 1 - \left(1 + \frac{t}{\tau}\right) e^{-t/\tau}$$
- **Primera derivada:**
  $$\dot{y}_2(t) = \frac{t}{\tau^2} e^{-t/\tau}$$
  En $t = 0^+$, la pendiente es exactamente nula: $\dot{y}_2(0^+) = 0$. Modela con fidelidad la inercia del rotor, que arranca desde el reposo.
- **Segunda derivada:**
  $$\ddot{y}_2(t) = \frac{1}{\tau^2}\left(1 - \frac{t}{\tau}\right) e^{-t/\tau}$$
  En $t = 0^+$, $\ddot{y}_2(0^+) = \frac{1}{\tau^2} > 0$ (fase convexa de aceleración).
- **Punto de inflexión exacto:** Ocurre en $t = \tau$, donde $\ddot{y}_2(\tau) = 0$.
  - Valor en la inflexión:
    $$y_2(\tau) = 1 - \frac{2}{e} \approx 0.264241 \quad (26.42\%)$$
  - Tasa máxima de cambio (pendiente máxima):
    $$\dot{y}_{2,\max} = \dot{y}_2(\tau) = \frac{1}{e \cdot \tau} \approx \frac{0.367879}{\tau}\text{ s}^{-1}$$
  - Comparación de pendientes máximas:
    $$\frac{\dot{y}_{2,\max}}{\dot{y}_{1,\max}} = \frac{1}{e} \approx 0.367879 \quad (36.79\%)$$

---

## 4. Tiempos Característicos (10%, 50%, 90%) y Relaciones Universales

Definiendo la variable temporal adimensional invariante:
$$u = \frac{t}{\tau}$$

### 4.1. Coeficientes Adimensionales Universales ($u$)

| Métrica | 1er Orden ($u_1$) | 2do Orden Crítico ($u_2$) | Ratio Universal ($u_2 / u_1$) | Expresión Analítica Exacta |
|---|---:|---:|---:|---|
| **$u_{10\%}$** | 0.105361 | 0.531812 | **5.0475x (+404.75%)** | $u_1 = -\ln(0.9)$, $u_2 = -1 - W_{-1}(-0.9/e)$ |
| **$u_{50\%}$** | 0.693147 | 1.678347 | **2.4213x (+142.13%)** | $u_1 = \ln(2)$, $u_2 = -1 - W_{-1}(-0.5/e)$ |
| **$u_{90\%}$** | 2.302585 | 3.889720 | **1.6893x (+68.93%)** | $u_1 = \ln(10)$, $u_2 = -1 - W_{-1}(-0.1/e)$ |
| **$u_{10\to 90\%}$ (Subida)** | 2.197225 | 3.357909 | **1.5283x (+52.83%)** | $\Delta u_1 = \ln(9)$, $\Delta u_2 = u_{2,90} - u_{2,10}$ |

> **Observación técnica clave:** El mayor retardo introducido por el segundo orden se concentra en el **inicio de la maniobra** ($10\%$), donde el tiempo necesario se multiplica por más de **5 veces** ($+404.8\%$). En el tramo final ($90\%$), el ratio se modera a $1.6893\text{x}$ ($+68.9\%$).

### 4.2. Tiempos Dimensionales Lineales (Sin Limitación de Rampa)

A continuación se presentan los valores calculados para los $\tau$ supuestos:

| $\tau$ Supuesto (s) | Modelo | $t_{10\%}$ (ms) | $t_{50\%}$ (ms) | $t_{90\%}$ (ms) | $t_{10\to 90\%}$ (ms) | Pendiente Máx ($\text{s}^{-1}$) | Inflexión $t_{\text{inf}}$ (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| **$\tau = 0.08\text{ s}$** | 1er orden | 8.43 | 55.45 | 184.21 | 175.78 | 12.500 | N/A |
| (Hipótesis C02) | 2do orden crít. | **42.54** | **134.27** | **311.18** | **268.63** | 4.598 | 0.08 |
| | **Diferencia (2do - 1er)** | **+34.12 ms** | **+78.82 ms** | **+126.97 ms** | **+92.85 ms** | -7.902 | — |
| **$\tau = 0.20\text{ s}$** | 1er orden | 21.07 | 138.63 | 460.52 | 439.44 | 5.000 | N/A |
| (Sensibilidad) | 2do orden crít. | **106.36** | **335.67** | **777.94** | **671.58** | 1.839 | 0.20 |
| | **Diferencia (2do - 1er)** | **+85.29 ms** | **+197.04 ms** | **+317.43 ms** | **+232.14 ms** | -3.161 | — |
| **$\tau = 0.50\text{ s}$** | 1er orden | 52.68 | 346.57 | 1151.29 | 1098.61 | 2.000 | N/A |
| (Sensibilidad) | 2do orden crít. | **265.91** | **839.17** | **1944.86** | **1678.95** | 0.736 | 0.50 |
| | **Diferencia (2do - 1er)** | **+213.23 ms** | **+492.60 ms** | **+793.57 ms** | **+580.34 ms** | -1.264 | — |

---

## 5. Unidades y Tratamiento Conceptual de $\tau$

### 5.1. Sistema de Unidades y Coherencia Dimensional
- **Constante $\tau$:** Segundos ($\text{s}$). Representa la constante temporal del polo simple o doble ($s = -1/\tau$, frecuencia natural $\omega_n = 1/\tau\text{ rad/s}$).
- **Tiempos de respuesta ($t$):** Segundos ($\text{s}$) en cálculos y simulaciones; milisegundos ($\text{ms}$) para evaluación en lazos de control de vuelo.
- **Derivadas temporales:** $\text{s}^{-1}$ en la respuesta normalizada; $\text{N/s}$ en variables dimensionales de fuerza propulsora.
- **Variable adimensional ($u = t/\tau$):** Adimensional ($\text{adim}$), invariante respecto a la escala de tiempo.

### 5.2. Tratamiento Conceptual de $\tau$: Trampa Común de Modelado
Existe una confusión conceptual frecuente en ingeniería de sistemas al tratar $\tau$:
1. **En un sistema de 1er orden:** En $t = \tau$, la salida alcanza exactamente:
   $$y_1(\tau) = 1 - e^{-1} \approx 0.63212 \quad (63.21\%)$$
2. **En un sistema de 2do orden críticamente amortiguado:** En $t = \tau$, la salida alcanza **únicamente**:
   $$y_2(\tau) = 1 - (1 + 1)e^{-1} = 1 - \frac{2}{e} \approx 0.26424 \quad (26.42\%)$$
   Además, $t = \tau$ es el **punto de inflexión** de la curva (máxima aceleración superada, máxima velocidad alcanzada).
3. **¿Cuándo alcanza el 63.21% el sistema de 2do orden?**
   Resolviendo $(1 + u)e^{-u} = e^{-1}$:
   $$u \approx 2.14619 \implies t \approx 2.15 \tau$$
   El segundo orden requiere más del **doble de tiempo** ($2.15\text{x}$) para alcanzar el mismo nivel de salida ($63.2\%$).

> **Implicación crítica:** Si un diseñador sustituye un modelo de 1er orden por uno de 2do orden manteniendo el mismo valor nominal de $\tau$, el sistema real experimentará un retardo dinámico drásticamente superior al previsto, reduciendo el margen de fase del lazo de actitud.

---

## 6. Efecto de las Rampas de ESC (Slew-Rate) en C02

### 6.1. Cuantificación de la Saturación de Rampa
La tasa vectorial máxima supuesta en `simulacion_vuelo_A/INFORME.md` es de $50\text{ N/s}$ por módulo de $21\text{ N}$, lo que impone una cota normalizada:
$$R = \frac{50\text{ N/s}}{21\text{ N}} \approx 2.38095\text{ s}^{-1}$$

- Para 1er orden con $\tau = 0.08\text{ s}$, la pendiente demandada en $t=0^+$ es $\dot{y}_1(0^+) = 1/\tau = 12.50\text{ s}^{-1}$. Esto excede la cota $R$ en un **$425\%$** ($5.25\text{x}$). El sistema satura en régimen de rampa desde $t=0$ hasta alcanzar $y_{\text{sat}} = 1 - R\tau \approx 80.95\%$ en $t_{\text{sat}} = 340.0\text{ ms}$.
- Para 2do orden con $\tau = 0.08\text{ s}$, la pendiente máxima en el punto de inflexión es $\dot{y}_{2,\max} = 1/(e\tau) \approx 4.598\text{ s}^{-1}$. Excede la cota $R$ en un **$93\%$**, saturando la rampa durante el tramo central de la maniobra.

### 6.2. Impacto de la Rampa en los Tiempos de Respuesta ($R \approx 2.381\text{ s}^{-1}$)

| Modelo | $\tau$ (s) | $t_{10\%}$ Lineal | $t_{10\%}$ c/ Rampa | $t_{50\%}$ Lineal | $t_{50\%}$ c/ Rampa | $t_{90\%}$ Lineal | $t_{90\%}$ c/ Rampa | Variación en $t_{90\%}$ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **1er orden** | **0.08** | 8.43 ms | **42.00 ms** | 55.45 ms | **210.00 ms** | 184.21 ms | **391.55 ms** | **+207.34 ms (+112.6%)** |
| **2do orden crít.** | **0.08** | 42.54 ms | **50.87 ms** | 134.27 ms | **218.87 ms** | 311.18 ms | **432.14 ms** | **+120.96 ms (+38.9%)** |
| **1er orden** | **0.20** | 21.07 ms | **42.00 ms** | 138.63 ms | **210.00 ms** | 460.52 ms | **532.13 ms** | **+71.61 ms (+15.6%)** |
| **2do orden crít.** | **0.20** | 106.36 ms | **106.36 ms** | 335.67 ms | **335.66 ms** | 777.94 ms | **777.94 ms** | **0.00 ms (No satura)** |
| **1er orden** | **0.50** | 52.68 ms | **52.68 ms** | 346.57 ms | **346.57 ms** | 1151.29 ms | **1151.29 ms** | **0.00 ms (No satura)** |
| **2do orden crít.** | **0.50** | 265.91 ms | **265.90 ms** | 839.17 ms | **839.16 ms** | 1944.86 ms | **1944.86 ms** | **0.00 ms (No satura)** |

> **Conclusión sobre estabilidad y control:** En el caso de $\tau = 0.08\text{ s}$, el tiempo al 90% real con rampa de ESC alcanza **$391.6\text{ ms}$** (1er orden) y **$432.1\text{ ms}$** (2do orden), frente a los $184.2\text{ ms}$ del modelo puramente lineal. Un controlador de vuelo diseñado con la presunción de $184.2\text{ ms}$ sufrirá degradación severa por saturación de actuador, oscilaciones inducidas por el piloto/controlador (PIO) o pérdida de autoridad de actitud ante ráfagas.

---

## 7. Pruebas Realizadas y Verificación Numérica

Se ejecutó la batería completa de pruebas unitarias sobre `salidas/test_respuestas.py`. Las 19 pruebas se superaron sin fallos (`Ran 19 tests in 0.048s - OK`).

### Detalle de las Pruebas Realizadas:
1. `test_initial_values`: Comprueba $y(0) = 0$ para 1er y 2do orden en todos los $\tau$. *(OK)*
2. `test_initial_derivatives`: Comprueba $\dot{y}_1(0^+) = 1/\tau$ y $\dot{y}_2(0^+) = 0$. *(OK)*
3. `test_initial_curvature`: Comprueba $\ddot{y}_1(0^+) = -1/\tau^2$ y $\ddot{y}_2(0^+) = +1/\tau^2$. *(OK)*
4. `test_asymptotic_limit_t_infinity`: Comprueba $y(\infty) \to 1$ y relación de error $e_2/e_1 = 1 + t/\tau$. *(OK)*
5. `test_second_order_inflection_point`: Comprueba punto de inflexión en $t=\tau$, valor $1 - 2/e$ y pendiente $1/(e\tau)$. *(OK)*
6. `test_limit_tau_zero_and_infinity`: Comprueba colapso a Heaviside ($\tau \to 0$) y congelamiento ($\tau \to \infty$). *(OK)*
7. `test_first_order_exact_formula`: Comprueba fórmula de 1er orden con residual $< 10^{-15}$. *(OK)*
8. `test_second_order_solver_residual`: Comprueba que el solver Halley resuelve las raíces con residual $< 10^{-14}$. *(OK)*
9. `test_known_analytical_values`: Comprueba $u_{1,50} = \ln 2$, $u_{1,90} = \ln 10$ y raíces de Lambert $W_{-1}$. *(OK)*
10. `test_scaling_invariance`: Comprueba que $u_p = t_p / \tau$ es idéntico e invariante para cualquier $\tau$. *(OK)*
11. `test_relative_delay_factors`: Comprueba los ratios adimensionales universales de retraso (5.0475x, 2.4213x, 1.6893x). *(OK)*
12. `test_strict_temporal_ordering`: Comprueba $t_{10\%} < t_{50\%} < t_{90\%}$ en todas las condiciones. *(OK)*
13. `test_first_order_leads_second_order`: Comprueba que $y_1(t) > y_2(t)$ para todo $t > 0$. *(OK)*
14. `test_rk4_convergence_rate`: Comprueba orden de convergencia $O(\Delta t^4)$ de la integración Runge-Kutta 4. *(OK)*
15. `test_rate_limit_inactive_when_R_large`: Comprueba que la rampa no interfiere si $R \ge 1/\tau$. *(OK)*
16. `test_rate_limit_pure_ramp_phase`: Comprueba $t(p) = p/R$ en régimen puramente saturado. *(OK)*
17. `test_rate_limit_desaturation_continuity`: Comprueba continuidad $C^1$ en el punto de desaturación $y = 1 - R\tau$. *(OK)*
18. `test_rate_limited_matches_simulation`: Comprueba convergencia entre solución analítica y simulación temporal. *(OK)*
19. `test_second_order_rate_limit_thresholds`: Comprueba activación condicional de la cota según $1/(e\tau) \gtrless R$. *(OK)*

---

## 8. Limitaciones del Estudio

1. **Inexistencia de Datos Medidos para C02:** Ninguno de los valores de $\tau$ ni las cotas de rampa han sido contrastados empíricamente en el vehículo C02 ni en sus módulos propulsores reales.
2. **Incompatibilidad de Escala del Ensayo NASA:** Los datos de Weinstein et al. (SciTech 2024) corresponden a un EDF comercial de 130 mm en banco estático abierto, no transferible a la configuración de conductos internos, diámetro y empuje de C02.
3. **Hipótesis de Amortiguamiento Crítico Idealizado ($\zeta = 1.0$):** Los actuadores reales pueden presentar resonancias estructurales, acoplamientos elásticos o dinámicas subamortiguadas ($\zeta < 1$) o sobreamortiguadas por filtros electrónicos ($\zeta > 1$).
4. **Omisión de Efectos Acoplados de Batería y Flujo:** No se modela la caída de tensión en batería bajo picos de corriente, pérdidas aerodinámicas en ducto ni distorsiones de entrada en régimen de avance.

---

## 9. Inventario de Archivos Entregables en `salidas/`

| Archivo | Descripción | Estado |
|---|---|---|
| [`salidas/comparar_respuestas.py`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_respuesta/salidas/comparar_respuestas.py) | Script de cálculo analítico, Halley 3er orden, RK4 y modelado de rampas ESC | Copiado y ejecutado |
| [`salidas/test_respuestas.py`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_respuesta/salidas/test_respuestas.py) | Suite automatizada de 19 pruebas unitarias y convergencia numérica | Copiado y ejecutado |
| [`salidas/tabla_comparativa.csv`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_respuesta/salidas/tabla_comparativa.csv) | Tabla completa de resultados con unidades dimensionales y adimensionales | Generado |
| [`salidas/tabla_comparativa.md`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_respuesta/salidas/tabla_comparativa.md) | Tablas comparativas formateadas en Markdown con notas metodológicas | Generado |
| [`salidas/datos_respuestas.json`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_respuesta/salidas/datos_respuestas.json) | Exportación estructurada de datos y metadatos de límites | Generado |
| [`salidas/pruebas_ejecutadas.txt`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_respuesta/salidas/pruebas_ejecutadas.txt) | Registro de la ejecución detallada de las 19 pruebas unitarias (100% OK) | Generado |
| [`salidas/REVISION.md`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_respuesta/salidas/REVISION.md) | Informe técnico detallado de la revisión (presente documento) | Generado |
