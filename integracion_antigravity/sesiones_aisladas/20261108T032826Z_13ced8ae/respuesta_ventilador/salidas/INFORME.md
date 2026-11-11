# Informe Técnico: Comparación Dinámica de Respuestas de Actuador de Primer Orden y Segundo Orden Críticamente Amortiguado

**Proyecto:** Análisis de Dinámica y Respuesta Temporal de Ventiladores / Actuadores  
**Entorno de ejecución:** Espacio de trabajo aislado (`respuesta_ventilador`)  
**Fecha:** Noviembre 2026  
**Autor:** Antigravity (Ingeniería de Sistemas y Dinámica de Vuelo)

---

## 1. Resumen Ejecutivo

En este estudio se evalúa y compara el comportamiento temporal dinámico de dos modelos normalizados de respuesta al escalón para actuadores propulsores (ventiladores canalizados / EDFs):
1. **Modelo de Primer Orden:**
   $$y_1(t) = 1 - e^{-t/\tau}$$
2. **Modelo de Segundo Orden Críticamente Amortiguado ($\zeta = 1$):**
   $$y_2(t) = 1 - \left(1 + \frac{t}{\tau}\right) e^{-t/\tau}$$

El análisis se lleva a cabo evaluando tres constantes de tiempo supuestas: $\tau \in \{0.08, 0.20, 0.50\}\text{ s}$. Se calculan con precisión analítica y numérica de alta fidelidad los tiempos característicos al 10%, 50% y 90% de la consigna ($t_{10\%}, t_{50\%}, t_{90\%}$), así como el tiempo de subida $t_{10\to 90\%}$. Asimismo, se realiza un control riguroso de límites matemáticos y físicos ($t \to 0^+$, $t \to \infty$, $\tau \to 0^+$, $\tau \to \infty$, puntos de inflexión y cotas de pendiente máxima).

Adicionalmente, en consonancia con las observaciones del artículo de la NASA (*Weinstein et al., AIAA SciTech 2024*), se incorpora el análisis de **limitación de rampa (slew-rate) de variadores electrónicos de velocidad (ESC)**, demostrando cómo una cota máxima de cambio (como los $50\text{ N/s}$ supuestos en simulaciones previas para un ventilador de $21\text{ N}$) altera drásticamente los tiempos de respuesta reales frente a un modelo puramente lineal.

---

## 2. Distinción Metodológica: Datos Medidos, Supuestos y Cálculos

Para garantizar la integridad y trazabilidad técnica del proyecto, se establece la distinción taxativa entre datos medidos, datos supuestos y cálculos matemáticos:

```
+---------------------------------------------------------------------------------------------------+
|                                     DISTINCIÓN METODOLÓGICA                                       |
+-----------------------------------+--------------------------------+------------------------------+
| DATOS MEDIDOS                     | SUPUESTOS TÉCNICOS             | CÁLCULOS Y SIMULACIONES      |
+-----------------------------------+--------------------------------+------------------------------+
| • Cero datos medidos para C02.    | • Constantes tau in {0.08,     | • Tiempos t10, t50, t90      |
| • Los datos del artículo NASA       0.20, 0.50} s.                 |   analíticos y numéricos.    |
|   Weinstein et al. (SciTech 2024) | • tau = 0.08 s heredado de     | • Factores u = t/tau         |
|   corresponden a un banco de        hipótesis en INFORME.md        |   invariantes de escala.     |
|   ensayos estático de un EDF        (simulacion_vuelo_A).          | • Raíces de 2do orden vía    |
|   distinto de 130 mm.             | • tau = 0.20 s y 0.50 s como   |   Halley y Lambert W_-1      |
| • NO se toman los tiempos ni        hipótesis de sensibilidad.     |   (|error| < 1e-15).         |
|   los valores de tau del paper    | • Tasa vectorial max 50 N/s    | • Solución exacta de rampa   |
|   como mediciones de C02.           (R ~ 2.381 s^-1 para 21 N).    |   ESC y transición a exp.    |
|                                   | • Escalón ideal sin retraso    | • Integración numérica       |
|                                   |   puro de transporte.          |   Runge-Kutta 4 (RK4).       |
+-----------------------------------+--------------------------------+------------------------------+
```

1. **Datos Medidos:**
   - **No existen mediciones experimentales para el vehículo C02.** No se dispone de curvas de empuje dinámico en banco, caracterización de motor ni mediciones instaladas de los conductos.
   - El artículo de la NASA [*Weinstein et al., AIAA SciTech 2024*](https://ntrs.nasa.gov/api/citations/20230017299/downloads/Weinstein_SciTech2024_Final.pdf?attachment=true) describe la caracterización estática y dinámica de un EDF de **$130\text{ mm}$ de diámetro** (conjunto Schübeler / Hacker con ESC comercial) en un banco de ensayos dinamométrico de la NASA. Sus mediciones pertenecen a una planta física completamente ajena a C02. **No se toman sus tiempos ni sus constantes de tiempo como mediciones de C02.**
2. **Supuestos Técnicos:**
   - Las constantes de tiempo $\tau = 0.08\text{ s}$, $\tau = 0.20\text{ s}$ y $\tau = 0.50\text{ s}$ son **hipótesis de trabajo**. El valor $\tau = 0.08\text{ s}$ fue introducido como supuesto analítico en el informe de referencia `entradas/investigacion-aeronautica/simulacion_vuelo_A/INFORME.md` ("Constante de respuesta de primer orden 0,08 s y tasa máxima de cambio vectorial 50 N/s por módulo a 5 kg, ambos supuestos"). Los valores de $0.20\text{ s}$ y $0.50\text{ s}$ se asumen para evaluar el impacto de dinámicas propulsoras más lentas.
   - Se asume un escalón normalizado unitario en $t=0$, amortiguamiento crítico exacto ($\zeta = 1.0$) para el segundo orden, y ausencia de juego mecánico o retardo puro de paquetes digitales.
   - Para el análisis de limitación de rampa, se toma la tasa máxima supuesta en `INFORME.md` de $50\text{ N/s}$ normalizada contra la fuerza máxima de un módulo ($21\text{ N}$), resultando en una cota de rampa admisible de $R = \frac{50\text{ N/s}}{21\text{ N}} \approx 2.38095\text{ s}^{-1}$.
3. **Cálculos Realizados:**
   - Ecuaciones analíticas cerradas, inversión numérica hiper-precisa mediante el método de Halley de tercer orden ($|\text{residuo}| < 10^{-14}$), análisis asintótico de límites, y simulación temporal por integración numérica Runge-Kutta 4 (RK4) y Euler modificada.

---

## 3. Fundamento Matemático y Modelos Dinámicos

### 3.1. Modelo de Primer Orden
Representa un sistema gobernado por una única constante de tiempo $\tau$, descrito por la función de transferencia lineal:
$$G_1(s) = \frac{1}{\tau s + 1}$$

- **Respuesta temporal al escalón unitario:**
  $$y_1(t) = 1 - e^{-t/\tau}, \quad t \ge 0$$
- **Primera derivada (tasa de respuesta):**
  $$\dot{y}_1(t) = \frac{1}{\tau} e^{-t/\tau}$$
  En $t = 0^+$, la pendiente es máxima e instantánea: $\dot{y}_1(0^+) = \frac{1}{\tau}\text{ s}^{-1}$. Físicamente, esto implica un "salto" de derivada (jerk infinito en la entrada) que exigiría aceleración infinita del rotor si no existieran inercias.
- **Segunda derivada (aceleración de salida / curvatura):**
  $$\ddot{y}_1(t) = -\frac{1}{\tau^2} e^{-t/\tau} < 0 \quad \forall t \ge 0$$
  La curva es estrictamente cóncava hacia abajo desde $t=0$. No presenta fase de arranque suave ni puntos de inflexión.
- **Cálculo analítico del tiempo al porcentaje $p \in (0, 1)$:**
  $$1 - e^{-t/\tau} = p \implies e^{-t/\tau} = 1 - p \implies t_1(p) = -\tau \ln(1 - p)$$
  Definiendo la variable adimensional universal $u = t/\tau$:
  $$u_1(p) = -\ln(1 - p)$$

### 3.2. Modelo de Segundo Orden Críticamente Amortiguado
Representa un sistema con dos polos reales idénticos en $s = -1/\tau$ ($\zeta = 1$, frecuencia natural $\omega_n = 1/\tau$), típico de un motor con inercia de rotor $J$ acoplado a un lazo de corriente o velocidad con retardo inductivo/filtro:
$$G_2(s) = \frac{1}{(\tau s + 1)^2} = \frac{\omega_n^2}{(s + \omega_n)^2}$$

- **Respuesta temporal al escalón unitario:**
  $$y_2(t) = 1 - \left(1 + \frac{t}{\tau}\right) e^{-t/\tau}, \quad t \ge 0$$
- **Primera derivada:**
  $$\dot{y}_2(t) = \frac{t}{\tau^2} e^{-t/\tau}$$
  En $t = 0^+$, la pendiente es nula: $\dot{y}_2(0^+) = 0$. Modela la inercia rotacional física del ventilador, donde la velocidad angular no puede cambiar instantáneamente y debe acelerar desde cero.
- **Segunda derivada:**
  $$\ddot{y}_2(t) = \frac{1}{\tau^2} \left(1 - \frac{t}{\tau}\right) e^{-t/\tau}$$
  En $t = 0^+$, $\ddot{y}_2(0^+) = \frac{1}{\tau^2} > 0$ (aceleración positiva inicial, curva convexa).
  En $t = \tau$, $\ddot{y}_2(\tau) = 0$: **punto de inflexión exacto**.
  Para $t < \tau$, la aceleración de salida es positiva (fase de lanzamiento/aceleración).
  Para $t > \tau$, la aceleración es negativa (fase de frenado hacia el estado estacionario).
- **Máxima tasa de cambio:**
  Ocurre exactamente en el punto de inflexión $t = \tau$:
  $$\dot{y}_{2,\max} = \dot{y}_2(\tau) = \frac{\tau}{\tau^2} e^{-1} = \frac{1}{e \cdot \tau} \approx \frac{0.367879}{\tau}\text{ s}^{-1}$$
  Nótese que la pendiente máxima de segundo orden representa apenas un **$36.79\%$** de la pendiente inicial máxima del modelo de primer orden.
- **Valor en el punto de inflexión:**
  $$y_2(\tau) = 1 - (1 + 1) e^{-1} = 1 - \frac{2}{e} \approx 0.264241 \quad (26.42\%)$$
- **Cálculo analítico del tiempo al porcentaje $p \in (0, 1)$:**
  Debemos resolver para $u = t/\tau$:
  $$(1 + u) e^{-u} = 1 - p \implies -(1 + u) e^{-(1 + u)} = -\frac{1 - p}{e}$$
  Haciendo $w = -(1 + u) < -1$ para $u > 0$:
  $$w = W_{-1}\left(-\frac{1 - p}{e}\right) \implies u_2(p) = -1 - W_{-1}\left(-\frac{1 - p}{e}\right)$$
  donde $W_{-1}$ denota la rama principal negativa de la función $W$ de Lambert. Numéricamente, esta raíz se resuelve mediante el método de Halley cúbico con una precisión de máquina superior a $10^{-15}$.

---

## 4. Tablas Comparativas de Resultados

### 4.1. Tiempos de Respuesta Dimensionales Lineales (Sin Limitación de Rampa)

En la siguiente tabla se presentan los tiempos característicos para cada combinación de modelo dinámico y constante $\tau$ supuesta:

| Modelo Dinámico | $\tau$ (s) | $t_{10\%}$ (ms) | $t_{50\%}$ (ms) | $t_{90\%}$ (ms) | $t_{10\to 90\%}$ (ms) | Pendiente Máx ($s^{-1}$) | $t_{\text{inflex}}$ (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **1er orden** | **0.08** | 8.43 | 55.45 | 184.21 | 175.78 | 12.50 | N/A |
| **2do orden crít.** | **0.08** | **42.54** | **134.27** | **311.18** | **268.63** | 4.60 | 0.08 |
| **1er orden** | **0.20** | 21.07 | 138.63 | 460.52 | 439.44 | 5.00 | N/A |
| **2do orden crít.** | **0.20** | **106.36** | **335.67** | **777.94** | **671.58** | 1.84 | 0.20 |
| **1er orden** | **0.50** | 52.68 | 346.57 | 1151.29 | 1098.61 | 2.00 | N/A |
| **2do orden crít.** | **0.50** | **265.91** | **839.17** | **1944.86** | **1678.95** | 0.74 | 0.50 |

*Archivo CSV generado:* [`tabla_comparativa.csv`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/respuesta_ventilador/salidas/tabla_comparativa.csv)  
*Archivo Markdown generado:* [`tabla_comparativa.md`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/respuesta_ventilador/salidas/tabla_comparativa.md)

### 4.2. Ratios y Retardos Relativos (2do Orden frente a 1er Orden)

La comparación porcentual y en tiempo absoluto revela el impacto drástico del orden dinámico:

| $\tau$ (s) | $\Delta t_{10\%}$ (ms) | Ratio $t_{10\%}$ | $\Delta t_{50\%}$ (ms) | Ratio $t_{50\%}$ | $\Delta t_{90\%}$ (ms) | Ratio $t_{90\%}$ | $\Delta t_{10\to 90}$ (ms) | Ratio Subida |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **0.08** | +34.12 ms (+404.8%) | **5.0475x** | +78.82 ms (+142.1%) | **2.4213x** | +126.97 ms (+68.9%) | **1.6893x** | +92.85 ms (+52.8%) | **1.5283x** |
| **0.20** | +85.29 ms (+404.8%) | **5.0475x** | +197.04 ms (+142.1%) | **2.4213x** | +317.43 ms (+68.9%) | **1.6893x** | +232.14 ms (+52.8%) | **1.5283x** |
| **0.50** | +213.23 ms (+404.8%) | **5.0475x** | +492.60 ms (+142.1%) | **2.4213x** | +793.57 ms (+68.9%) | **1.6893x** | +580.34 ms (+52.8%) | **1.5283x** |

### 4.3. Coeficientes Adimensionales Universales ($u = t/\tau$)

Al normalizar por la constante de tiempo $\tau$, los coeficientes son propiedades geométricas universales de las ecuaciones diferenciales correspondientes:

| Métrica | 1er Orden ($u_1$) | 2do Orden Crítico ($u_2$) | Ratio Universal ($u_2 / u_1$) | Expresión Analítica |
|---|---:|---:|---:|---|
| **$u_{10\%}$** | 0.105361 | 0.531812 | **5.0475x (+404.75%)** | $u_1 = -\ln(0.9)$, $u_2 = -1 - W_{-1}(-0.9/e)$ |
| **$u_{50\%}$** | 0.693147 | 1.678347 | **2.4213x (+142.13%)** | $u_1 = \ln(2)$, $u_2 = -1 - W_{-1}(-0.5/e)$ |
| **$u_{90\%}$** | 2.302585 | 3.889720 | **1.6893x (+68.93%)** | $u_1 = \ln(10)$, $u_2 = -1 - W_{-1}(-0.1/e)$ |
| **$u_{10\to 90\%}$** | 2.197225 | 3.357909 | **1.5283x (+52.83%)** | $\Delta u_1 = \ln(9)$, $\Delta u_2 = u_{2,90} - u_{2,10}$ |

> **Hallazgo fundamental:** El mayor desfase ocurre en el tramo inicial de la respuesta ($10\%$). En segundo orden, el tiempo para alcanzar el $10\%$ es **más de 5 veces superior** ($+404.8\%$) al de primer orden debido al inicio tangencial horizontal ($\dot{y}_2(0) = 0$), lo que introduce un tiempo muerto efectivo significativo en la planta propulsora.

---

## 5. Control de Límites Físicos y Matemáticos

En el diseño e implementación del código (`comparar_respuestas.py`) y sus pruebas unitarias (`test_respuestas.py`), se comprobó el control riguroso de los siguientes límites:

### 5.1. Límite cuando $t \to 0^+$ (Comportamiento Inicial e Inercia)
- **Primer Orden:**
  $$\lim_{t \to 0^+} y_1(t) = 0, \quad \lim_{t \to 0^+} \dot{y}_1(t) = \frac{1}{\tau}, \quad \lim_{t \to 0^+} \ddot{y}_1(t) = -\frac{1}{\tau^2}$$
  Desarrollo de Taylor: $y_1(t) \approx \frac{t}{\tau} - \frac{t^2}{2\tau^2} + O(t^3)$.
  *Implicación física:* Respuesta instantánea de pendiente finita pero no nula. No refleja la inercia del fluido ni la inercia del rotor.
- **Segundo Orden Críticamente Amortiguado:**
  $$\lim_{t \to 0^+} y_2(t) = 0, \quad \lim_{t \to 0^+} \dot{y}_2(t) = 0, \quad \lim_{t \to 0^+} \ddot{y}_2(t) = \frac{1}{\tau^2}$$
  Desarrollo de Taylor: $y_2(t) \approx \frac{t^2}{2\tau^2} - \frac{t^3}{3\tau^3} + O(t^4)$.
  *Implicación física:* Cero velocidad inicial. La respuesta se comporta parabólicamente cerca del origen ($\sim \frac{1}{2}(t/\tau)^2$). El actuador necesita un tiempo de aceleración $\Delta t \approx \tau \sqrt{2p}$ antes de generar una fuerza apreciable, lo que genera retraso de fase en bucles cerrados de actitud.

### 5.2. Límite cuando $t \to \infty$ (Convergencia y Error Asintótico)
- Ambos sistemas cumplen la estabilidad asintótica y convergencia al valor del escalón:
  $$\lim_{t \to \infty} y_1(t) = 1, \quad \lim_{t \to \infty} y_2(t) = 1$$
- Análisis del error residual $e(t) = 1 - y(t)$:
  $$e_1(t) = e^{-t/\tau}, \quad e_2(t) = \left(1 + \frac{t}{\tau}\right) e^{-t/\tau}$$
  $$\frac{e_2(t)}{e_1(t)} = 1 + \frac{t}{\tau}$$
  A medida que el tiempo avanza, la relación de error $e_2(t)/e_1(t)$ diverge linealmente. Para cuando el segundo orden alcanza el 90% ($t \approx 3.89\tau$), su error remanente es casi 5 veces mayor que el del primer orden al mismo tiempo.

### 5.3. Límites en Función de $\tau$
- **Límite $\tau \to 0^+$ (Actuador Instantáneo / Ideal):**
  Para cualquier $t > 0$: $\lim_{\tau \to 0^+} y_1(t) = 1$, $\lim_{\tau \to 0^+} y_2(t) = 1$.
  La respuesta colapsa a la función escalón de Heaviside $\Theta(t)$. Los tiempos de retardo $t_{10\%}, t_{50\%}, t_{90\%} \to 0$.
- **Límite $\tau \to \infty$ (Actuador Bloqueado / Congelado):**
  Para cualquier $t \ge 0$: $\lim_{\tau \to \infty} y_1(t) = 0$, $\lim_{\tau \to \infty} y_2(t) = 0$.
  Los tiempos de respuesta divergen a infinito ($t_p \to \infty$).

---

## 6. Análisis del Efecto de Rampas de ESC (Slew-Rate) y Artículo NASA

### 6.1. Evidencia del Estudio NASA (Weinstein et al., AIAA SciTech 2024)
El artículo de la NASA titulado *“Dynamic Characterization and Modeling of an Electric Ducted Fan for eVTOL Applications”* ensayó un EDF de $130\text{ mm}$ en banco estático con escalones de consigna de aceleración y desaceleración. Sus conclusiones clave destacan:
1. **Saturación por rampa de conmutación (ESC Ramp):** Los variadores electrónicos (ESC) comerciales y de grado industrial incorporan limitadores internos de tasa de aceleración (slew-rate en $\text{PWM/s}$ o $\text{d}\Omega/\text{dt}$) en su firmware para prevenir desincronizaciones de campo magnético (desync), sobrecorrientes destructivas en los MOSFETs y caídas bruscas de tensión de batería.
2. **Respuesta no lineal dominada por rampa:** Ante escalones de consigna de media o gran amplitud (ej. 20% a 80%, o escalones completos), la dinámica del actuador no sigue un filtro lineal puro (ni de 1er ni de 2do orden); en su lugar, se observa una **rampa lineal de pendiente constante** durante la mayor parte de la carrera de aceleración, seguida de una aproximación asintótica final.
3. **Dependencia de la amplitud:** El tiempo de subida real no es una constante $\tau$, sino que escala proporcionalmente a la magnitud del escalón comandado $\Delta u$.

### 6.2. Cuantificación sobre la Hipótesis del Proyecto C02
En el archivo de referencia `INFORME.md` (`entradas/investigacion-aeronautica/simulacion_vuelo_A/INFORME.md`), se asumió para el modelo de 5 kg:
- Fuerza máxima nominal por módulo: $F_{\max} = 21\text{ N}$.
- Tasa máxima de cambio vectorial supuesta: $\dot{F}_{\max} = 50\text{ N/s}$.

Esto define una cota de rampa máxima normalizada:
$$R = \frac{\dot{F}_{\max}}{F_{\max}} = \frac{50\text{ N/s}}{21\text{ N}} \approx 2.38095\text{ s}^{-1}$$

Comparando esta cota con las derivadas máximas de los modelos lineales:
- Para primer orden con $\tau = 0.08\text{ s}$, la pendiente inicial teórica es:
  $$\dot{y}_1(0^+) = \frac{1}{\tau} = \frac{1}{0.08} = 12.50\text{ s}^{-1}$$
  ¡La pendiente demandada por el modelo de primer orden ($12.50\text{ s}^{-1}$) es **5.25 veces mayor** que la cota admisible de $50\text{ N/s}$ ($2.381\text{ s}^{-1}$)!
- Para segundo orden con $\tau = 0.08\text{ s}$, la pendiente máxima en $t = \tau$ es:
  $$\dot{y}_{2,\max} = \frac{1}{e \cdot \tau} \approx 4.598\text{ s}^{-1} > 2.381\text{ s}^{-1}$$
  También excede la cota de rampa en un **$93\%$**.

### 6.3. Solución Analítica de Primer Orden con Rampa
Bajo una limitación $\left|\frac{dy}{dt}\right| \le R$, el sistema de primer orden opera en dos regímenes:
1. **Fase de rampa pura ($t \le t_{\text{sat}}$):**
   $$y(t) = R \cdot t$$
   La desaturación ocurre cuando $\frac{1 - y}{\tau} = R \implies y_{\text{sat}} = 1 - R \tau$.
   El tiempo en régimen saturado es:
   $$t_{\text{sat}} = \frac{1 - R\tau}{R} = \frac{1}{R} - \tau$$
   Para $\tau = 0.08\text{ s}$ y $R = 2.381\text{ s}^{-1}$:
   $$y_{\text{sat}} = 1 - 2.381 \times 0.08 = 0.8095 \quad (80.95\%)$$
   $$t_{\text{sat}} = \frac{1}{2.381} - 0.08 = 0.420 - 0.08 = 0.340\text{ s} \quad (340.0\text{ ms})$$
2. **Fase exponencial desaturada ($t > t_{\text{sat}}$):**
   $$y(t) = 1 - (R \tau) e^{-(t - t_{\text{sat}})/\tau}$$

### 6.4. Comparativa: Modelo Lineal vs Modelo con Rampa ESC ($R \approx 2.381\text{ s}^{-1}$)

| Modelo | $\tau$ (s) | $t_{10\%}$ Lineal (ms) | $t_{10\%}$ c/ Rampa (ms) | $t_{50\%}$ Lineal (ms) | $t_{50\%}$ c/ Rampa (ms) | $t_{90\%}$ Lineal (ms) | $t_{90\%}$ c/ Rampa (ms) | Incremento en $t_{90\%}$ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **1er orden** | **0.08** | 8.43 | **42.00** | 55.45 | **210.00** | 184.21 | **391.55** | **+207.34 ms (+112.6%)** |
| **2do orden crít.** | **0.08** | 42.54 | **50.87** | 134.27 | **218.87** | 311.18 | **432.14** | **+120.96 ms (+38.9%)** |
| **1er orden** | **0.20** | 21.07 | **42.00** | 138.63 | **210.00** | 460.52 | **532.13** | **+71.61 ms (+15.6%)** |
| **2do orden crít.** | **0.20** | 106.36 | **106.36** | 335.67 | **335.66** | 777.94 | **777.94** | **0.00 ms (No satura)** |
| **1er orden** | **0.50** | 52.68 | **52.68** | 346.57 | **346.57** | 1151.29 | **1151.29** | **0.00 ms (No satura)** |
| **2do orden crít.** | **0.50** | 265.91 | **265.90** | 839.17 | **839.16** | 1944.86 | **1944.86** | **0.00 ms (No satura)** |

> **Conclusión sobre el control de vuelo:** Asumir una constante $\tau = 0.08\text{ s}$ de primer orden sin limitación de rampa en una simulación de control (como el asignador SLSQP a 50 Hz de `simulacion_vuelo_A`) subestima el tiempo real al 90% en más de un **$112\%$** ($391.6\text{ ms}$ frente a $184.2\text{ ms}$). En un vehículo real, esta discrepancia introduce un desfase de control severo que puede inducir oscilaciones sostenidas (PIO) o inestabilidad si no se incluye compensación feedforward y ganancias adaptadas.

---

## 7. Pruebas Numéricas y Verificación

Se implementó una suite automatizada de pruebas unitarias y de convergencia en [`test_respuestas.py`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/respuesta_ventilador/salidas/test_respuestas.py), ejecutada sin dependencias externas sobre el entorno Python 3 del sandbox. La ejecución completa se encuentra registrada en [`pruebas_ejecutadas.txt`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/respuesta_ventilador/salidas/pruebas_ejecutadas.txt).

### 7.1. Batería de Pruebas Ejecutadas (19 Pruebas, 100% Superadas)
1. `test_initial_values`: Comprueba $y_1(0) = 0$ y $y_2(0) = 0$. *(Superada)*
2. `test_initial_derivatives`: Comprueba $\dot{y}_1(0^+) = 1/\tau$ y $\dot{y}_2(0^+) = 0$. *(Superada)*
3. `test_initial_curvature`: Comprueba $\ddot{y}_1(0^+) = -1/\tau^2$ y $\ddot{y}_2(0^+) = +1/\tau^2$. *(Superada)*
4. `test_asymptotic_limit_t_infinity`: Comprueba $y(\infty) \to 1$ y $e_2(t)/e_1(t) = 1 + t/\tau$. *(Superada)*
5. `test_second_order_inflection_point`: Comprueba $\ddot{y}_2(\tau) = 0$, $y_2(\tau) = 1 - 2/e$, y $\dot{y}_{2,\max} = 1/(e\tau)$. *(Superada)*
6. `test_limit_tau_zero_and_infinity`: Comprueba el comportamiento de frontera cuando $\tau \to 0^+$ y $\tau \to \infty$. *(Superada)*
7. `test_first_order_exact_formula`: Comprueba la fórmula de $t_1(p)$ con residuales $< 10^{-15}$. *(Superada)*
8. `test_second_order_solver_residual`: Comprueba que el método de Halley resuelve $y_2(t_p) = p$ con residual $< 10^{-14}$. *(Superada)*
9. `test_known_analytical_values`: Comprueba valores teóricos conocidos ($u_{1,50} = \ln 2$, $u_{1,90} = \ln 10$, etc.). *(Superada)*
10. `test_scaling_invariance`: Comprueba que $u_p = t_p / \tau$ es idéntico para cualquier $\tau$. *(Superada)*
11. `test_relative_delay_factors`: Comprueba los factores universales de retraso ($5.0475$, $2.4213$, $1.6893$). *(Superada)*
12. `test_strict_temporal_ordering`: Comprueba $t_{10\%} < t_{50\%} < t_{90\%}$ en todos los casos. *(Superada)*
13. `test_first_order_leads_second_order`: Comprueba $y_1(t) > y_2(t)$ para todo $t > 0$. *(Superada)*
14. `test_rk4_convergence_rate`: Comprueba que el integrador RK4 posee orden de convergencia $O(\Delta t^4)$ (reducción de error por factor $\approx 16$ al reducir el paso a la mitad). *(Superada)*
15. `test_rate_limit_inactive_when_R_large`: Comprueba que si $R \ge 1/\tau$, el límite de rampa es inactivo. *(Superada)*
16. `test_rate_limit_pure_ramp_phase`: Comprueba $t(p) = p/R$ en régimen lineal de rampa. *(Superada)*
17. `test_rate_limit_desaturation_continuity`: Comprueba la continuidad en $y_{\text{sat}} = 1 - R\tau$. *(Superada)*
18. `test_rate_limited_matches_simulation`: Comprueba la concordancia entre la solución analítica de rampa y la simulación numérica temporal. *(Superada)*
19. `test_second_order_rate_limit_thresholds`: Comprueba la activación condicional de la cota según $1/(e\tau) \gtrless R$. *(Superada)*

---

## 8. Limitaciones del Estudio

1. **Ausencia de Identificación Experimental para C02:**
   Todos los valores analizados ($\tau = 0.08, 0.20, 0.50\text{ s}$) y la tasa de $50\text{ N/s}$ son supuestos teóricos. Ninguno de estos valores ha sido validado en un banco de tiro real para la configuración de cuatro ventiladores de C02.
2. **Inaplicabilidad Directa de los Datos NASA de Weinstein et al.:**
   El artículo de Weinstein et al. (AIAA SciTech 2024) estudia un EDF comercial de $130\text{ mm}$ en banco abierto estático. Sus constantes temporales, inercias de rotor, curvas de avance y retardos de conmutación no son transferibles al ventilador de C02, cuyas dimensiones, ducto interno, toberas y masa motriz difieren sustancialmente.
3. **Amortiguamiento Crítico Idealizado ($\zeta = 1.0$):**
   El modelo de segundo orden se analizó bajo la hipótesis de amortiguamiento crítico exacto. Los sistemas propulsores reales pueden exhibir dinámicas subamortiguadas leves ($\zeta \in [0.7, 0.9]$) debido a dinámicas de acoplamiento motor-hélice, o sobreamortiguadas ($\zeta > 1$) por filtros RC o límites de potencia de la batería.
4. **Acoplamiento Aerodinámico y Tensión de Batería Omitidos:**
   No se modela la caída de tensión de las celdas LiPo bajo picos de demanda, la variación de densidad de aire, la distorsión del flujo de entrada en vuelo con avance ni las pérdidas de conducto.

---

## 9. Inventario de Entregables Generados

Todos los entregables solicitados han sido generados autónomamente dentro de la carpeta `salidas/`:

1. [`salidas/comparar_respuestas.py`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/respuesta_ventilador/salidas/comparar_respuestas.py): Script en Python 3 puro (sin dependencias externas) que implementa las soluciones analíticas, inversión numérica por Halley, simulación RK4, control de límites y modelado de rampas de ESC.
2. [`salidas/tabla_comparativa.csv`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/respuesta_ventilador/salidas/tabla_comparativa.csv): Tabla en formato CSV con todas las métricas dimensionales ($s$, $ms$, $s^{-1}$) y adimensionales ($u$), incluyendo regímenes lineales y con limitación de rampa.
3. [`salidas/tabla_comparativa.md`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/respuesta_ventilador/salidas/tabla_comparativa.md): Tablas comparativas formateadas en Markdown con notas metodológicas y desgloses por sección.
4. [`salidas/datos_respuestas.json`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/respuesta_ventilador/salidas/datos_respuestas.json): Estructura completa de datos y metadatos exportada en formato JSON para procesamiento por herramientas posteriores.
5. [`salidas/test_respuestas.py`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/respuesta_ventilador/salidas/test_respuestas.py): Suite automatizada de 19 pruebas unitarias con control de tolerancias, límites analíticos y convergencia de integradores.
6. [`salidas/pruebas_ejecutadas.txt`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/respuesta_ventilador/salidas/pruebas_ejecutadas.txt): Registro textual de la ejecución exitosa de las pruebas unitarias.
7. [`salidas/INFORME.md`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/respuesta_ventilador/salidas/INFORME.md): Presente informe técnico detallado.
