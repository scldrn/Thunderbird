# REPORTE TÉCNICO: ANÁLISIS INDEPENDIENTE DE PERFILES TEMPORALES PARA TRASLACIÓN Y GIRO EN DOS FASES

**Documento:** Informe de Cinemática y Análisis Dinámico  
**Fecha:** 2026-11-07  
**Ubicación de Entregables:** `salidas/`  
**Fuentes de Entrada:** `entradas/investigacion-aeronautica/modelos_integrados/producto_A07/` y `entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json`  

---

## 1. RESUMEN EJECUTIVO

El presente informe constituye un análisis cinemático independiente de la maniobra de apertura y cierre conceptual de compuertas definida en los modelos de investigación aeronáutica A07 y configuración C02. La maniobra consta de dos fases secuenciales desacopladas temporalmente:
1. **Fase 1 (Traslación pura):** desplazamiento exterior nominal de $\Delta h = 10\text{ mm}$ ($0{,}010\text{ m}$) con ángulo de rotación nulo ($0^\circ$).
2. **Fase 2 (Giro puro):** rotación nominal exterior de $\Delta \theta = 110^\circ$ ($\approx 1{,}919862\text{ rad}$) alrededor del eje longitudinal trasladado, con elevación fija en $10\text{ mm}$.

La ley de movimiento asignada para cada fase es el polinomio quintico suave de vibración mínima (*minimum jerk*):
$$s(u) = 10 u^3 - 15 u^4 + 6 u^5, \quad u = \frac{t}{T} \in [0, 1]$$

Se han evaluado analíticamente y mediante muestreo numérico las velocidades y aceleraciones máximas para duraciones de fase $T \in \{0{,}25; 0{,}50; 1{,}00; 2{,}00\}\text{ s}$. 

### Conclusiones Principales:
- **Coeficientes adimensionales exactos:** El perfil quintico presenta un factor de velocidad máxima $c_v = \frac{15}{8} = 1{,}875$ exactamente en el centro de la fase ($u = 0{,}5$), y un factor de aceleración pico $c_a = \frac{10}{\sqrt{3}} \approx 5{,}77350269$ en $u_1 = \frac{1}{2} - \frac{\sqrt{3}}{6} \approx 0{,}211325$ (aceleración positiva máxima) y $u_2 = \frac{1}{2} + \frac{\sqrt{3}}{6} \approx 0{,}788675$ (frenado máximo).
- **Traslación (10 mm):** Las velocidades de pico oscilan entre $75{,}0\text{ mm/s}$ ($T=0{,}25\text{ s}$) y $9{,}375\text{ mm/s}$ ($T=2{,}0\text{ s}$). Las aceleraciones de pico varían entre $923{,}76\text{ mm/s}^2$ ($0{,}0942\text{ g}_0$ para $T=0{,}25\text{ s}$) y $14{,}43\text{ mm/s}^2$ ($0{,}00147\text{ g}_0$ para $T=2{,}0\text{ s}$).
- **Giro (110°):** Las velocidades angulares de pico van desde $825{,}0^\circ/\text{s}$ ($14{,}40\text{ rad/s} \approx 137{,}5\text{ rpm}$ para $T=0{,}25\text{ s}$) hasta $103{,}125^\circ/\text{s}$ ($1{,}80\text{ rad/s} \approx 17{,}19\text{ rpm}$ para $T=2{,}0\text{ s}$). Las aceleraciones angulares pico van de $10161{,}36^\circ/\text{s}^2$ ($177{,}35\text{ rad/s}^2$) a $158{,}77^\circ/\text{s}^2$ ($2{,}77\text{ rad/s}^2$).
- **Chequeo analítico vs muestreo:** Se demostró analítica y computacionalmente que el muestreo uniforme en mallas discretas reproduce exactamente el pico de velocidad para $N$ impar (debido a que $u=0{,}5$ es racional), pero subestima levemente la aceleración pico si no se utilizan mallas densas o refinamiento analítico, dado que el punto de máxima aceleración $u_1 = \frac{1}{2} - \frac{\sqrt{3}}{6}$ es algebraicamente irracional.
- **Separación tajante entre cinemática y dinámica:** La cinemática determina de forma rigurosa la posición, velocidad y aceleración en el espacio-tiempo. Sin embargo, **el cálculo de fuerzas reales, pares de actuación, potencia y energía, así como el dimensionamiento de motores o servos, es físicamente imposible en esta fase**, debido a que en los modelos de referencia (`C02_CANDIDATA.json` y A07) los campos de masa real (`actual_mass_kg: null`), centro de gravedad (`actual_CG_m: null`), tensor de inercia (`actual_inertia_kgm2: null`), rozamiento de guías y sellos, cargas aerodinámicas CFD y la propia síntesis física del mecanismo están completamente ausentes o no calificados (`rotor_motor_servo_and_cooling_qualified: false`).
- **No afirmación de existencia ni encaje:** No se afirma que los mecanismos existan, que los herrajes o actuadores quepan en el fuselaje, ni que las compuertas cierren o sellen herméticamente en condiciones de vuelo. Las referencias en A07 y C02 constituyen poses geométricas de cribado CAD preliminar, no mecanismos físicos resueltos.

---

## 2. FORMULACIÓN MATEMÁTICA Y DERIVACIÓN ANALÍTICA

### 2.1 Polinomio quintico normalizado $s(u)$
Para una coordenada temporal adimensional $u = \frac{t}{T} \in [0, 1]$, donde $T$ es la duración de la fase, la función de posición normalizada es:
$$s(u) = 10 u^3 - 15 u^4 + 6 u^5$$

Condiciones de contorno en los extremos:
- Posición: $s(0) = 0$, $s(1) = 10(1)^3 - 15(1)^4 + 6(1)^5 = 1$.
- Primera derivada (velocidad adimensional):
  $$s'(u) = \frac{ds}{du} = 30 u^2 - 60 u^3 + 30 u^4 = 30 u^2 (1 - u)^2$$
  Evaluando en extremos: $s'(0) = 0$, $s'(1) = 0$.
  Nótese que $(1 - u)^2 \ge 0$ y $u^2 \ge 0$, por lo que $s'(u) \ge 0$ en todo el intervalo $[0, 1]$ (trayectoria monótona creciente, sin inversiones de marcha).
- Segunda derivada (aceleración adimensional):
  $$s''(u) = \frac{d^2s}{du^2} = 60 u - 180 u^2 + 120 u^3 = 60 u (1 - u)(1 - 2u)$$
  Evaluando en extremos: $s''(0) = 0$, $s''(1) = 0$.
- Tercera derivada (jerk o sobreaceleración adimensional):
  $$s'''(u) = \frac{d^3s}{du^3} = 60 - 360 u + 360 u^2 = 60 (1 - 6 u + 6 u^2)$$
  Evaluando en extremos: $s'''(0) = 60$, $s'''(1) = 60$.
- Cuarta derivada:
  $$s^{(4)}(u) = \frac{d^4s}{du^4} = -360 + 720 u = 360 (2u - 1)$$

### 2.2 Puntos críticos y coeficientes analíticos de pico

#### Velocidad máxima ($c_v$):
Se anula la segunda derivada:
$$s''(u) = 0 \iff 60 u (1 - u)(1 - 2u) = 0$$
En el interior del intervalo abierto $(0, 1)$, la única raíz es $1 - 2u = 0 \implies u_{v\max} = 0{,}5$.
Sustituyendo en $s'(u)$:
$$c_v = s'(0{,}5) = 30 (0{,}5)^2 (1 - 0{,}5)^2 = 30 \left(\frac{1}{4}\right)\left(\frac{1}{4}\right) = \frac{30}{16} = \frac{15}{8} = 1{,}875$$
La segunda derivada de la velocidad respecto a $u$ en este punto es $s'''(0{,}5) = 60(1 - 3 + 1{,}5) = -30 < 0$, confirmando un máximo global único.

#### Aceleración y frenado máximos ($c_a$):
Se anula la tercera derivada (jerk):
$$s'''(u) = 0 \iff 6 u^2 - 6 u + 1 = 0$$
Resolviendo la ecuación cuadrática:
$$u = \frac{6 \pm \sqrt{36 - 24}}{12} = \frac{6 \pm \sqrt{12}}{12} = \frac{1}{2} \pm \frac{\sqrt{3}}{6}$$
- Punto de aceleración positiva máxima: $u_1 = \frac{1}{2} - \frac{\sqrt{3}}{6} \approx 0{,}2113248654$
- Punto de frenado (aceleración negativa) máxima: $u_2 = \frac{1}{2} + \frac{\sqrt{3}}{6} \approx 0{,}7886751346$

Evaluación de $s''(u_1)$:
Nótese que en $u_1$:
$$u_1 (1 - u_1) = \left(\frac{1}{2} - \frac{\sqrt{3}}{6}\right)\left(\frac{1}{2} + \frac{\sqrt{3}}{6}\right) = \frac{1}{4} - \frac{3}{36} = \frac{1}{4} - \frac{1}{12} = \frac{1}{6}$$
$$1 - 2 u_1 = 1 - \left(1 - \frac{\sqrt{3}}{3}\right) = \frac{\sqrt{3}}{3}$$
Sustituyendo en la expresión factorizada $s''(u) = 60 \cdot u(1-u) \cdot (1-2u)$:
$$s''(u_1) = 60 \left(\frac{1}{6}\right)\left(\frac{\sqrt{3}}{3}\right) = 10 \frac{\sqrt{3}}{3} = \frac{10}{\sqrt{3}} \approx 5{,}7735026919$$
Por simetría antisimétrica respecto a $u=0{,}5$ ($s''(u) = -s''(1-u)$):
$$s''(u_2) = - \frac{10}{\sqrt{3}} \approx -5{,}7735026919$$
Por tanto, el factor de aceleración adimensional de cresta es exactamente:
$$c_a = \frac{10}{\sqrt{3}} \approx 5{,}7735026919$$

### 2.3 Escalado temporal y dimensional
Para una magnitud física con recorrido total $\Delta q$ completado en un tiempo $T$:
$$q(t) = q_0 + \Delta q \cdot s\left(\frac{t}{T}\right)$$
$$\dot{q}(t) = \frac{\Delta q}{T} s'\left(\frac{t}{T}\right) \implies \dot{q}_{\max} = c_v \frac{\Delta q}{T} = 1{,}875 \frac{\Delta q}{T}$$
$$\ddot{q}(t) = \frac{\Delta q}{T^2} s''\left(\frac{t}{T}\right) \implies \ddot{q}_{\max} = c_a \frac{\Delta q}{T^2} = \frac{10}{\sqrt{3}} \frac{\Delta q}{T^2}$$
$$\dddot{q}(t) = \frac{\Delta q}{T^3} s'''\left(\frac{t}{T}\right) \implies \dddot{q}_{\max} = 60 \frac{\Delta q}{T^3}$$

Instantes temporales absolutos de los picos dentro de la fase:
- $t_{v\max} = 0{,}500000 \cdot T$
- $t_{a\max} = \left(0{,}5 - \frac{\sqrt{3}}{6}\right) T \approx 0{,}211325 \cdot T$
- $t_{a\min} = \left(0{,}5 + \frac{\sqrt{3}}{6}\right) T \approx 0{,}788675 \cdot T$

---

## 3. TABLAS DE RESULTADOS CINEMÁTICOS POR FASE

### 3.1 Fase 1: Traslación Pura ($\Delta h = 10\text{ mm} = 0{,}010\text{ m}$)
En esta fase, la compuerta se traslada exclusivamente hacia el exterior ($+Z$ en compuertas superiores, $-Z$ en compuertas inferiores) manteniendo su ángulo de inclinación fijo en $0^\circ$.

Valores para la referencia estándar de aceleración gravitatoria $g_0 = 9{,}80665\text{ m/s}^2$ (según `C02_CANDIDATA.json`):

| Duración $T$ (s) | $v_{\max}$ (mm/s) | $v_{\max}$ (m/s) | $a_{\max}$ (mm/s$^2$) | $a_{\max}$ (m/s$^2$) | Aceleración ($g_0$) | Jerk máx (mm/s$^3$) | Jerk máx (m/s$^3$) | $t_{v\max}$ (s) | $t_{a\max}$ (s) | Fuerza inercial específica ($a_{\max}$) [N/kg] |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.25** | 75.0000 | 0.075000 | 923.7604 | 0.923760 | 0.09420 | 38400.0 | 38.400 | 0.1250 | 0.0528 | 0.923760 |
| **0.50** | 37.5000 | 0.037500 | 230.9401 | 0.230940 | 0.02355 | 4800.0 | 4.800 | 0.2500 | 0.1057 | 0.230940 |
| **1.00** | 18.7500 | 0.018750 | 57.7350 | 0.057735 | 0.00589 | 600.0 | 0.600 | 0.5000 | 0.2113 | 0.057735 |
| **2.00** | 9.3750 | 0.009375 | 14.4338 | 0.014434 | 0.00147 | 75.0 | 0.075 | 1.0000 | 0.4227 | 0.014434 |

*Nota sobre la fuerza inercial específica:* Representa la aceleración $a(t) = \frac{F_{\text{inercial}}}{m}$ expresada en $\text{N/kg} \equiv \text{m/s}^2$. Es el único término inercial independiente de la masa real.

---

### 3.2 Fase 2: Giro Puro ($\Delta \theta = 110^\circ \approx 1{,}919862177\text{ rad}$)
En esta fase, la compuerta parte desde la cota elevada de $10\text{ mm}$ (que se mantiene constante) y gira hacia el exterior $110^\circ$ respecto a la línea de bisagra longitudinal.

| Duración $T$ (s) | $\omega_{\max}$ (deg/s) | $\omega_{\max}$ (rad/s) | $\omega_{\max}$ (rpm) | $\alpha_{\max}$ (deg/s$^2$) | $\alpha_{\max}$ (rad/s$^2$) | Jerk angular máx (deg/s$^3$) | Jerk angular máx (rad/s$^3$) | $t_{\omega\max}$ (s) | $t_{\alpha\max}$ (s) | Par inercial específico ($\alpha_{\max}$) [$\text{N}\cdot\text{m}/(\text{kg}\cdot\text{m}^2)$] |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.25** | 825.0000 | 14.398966 | 137.5000 | 10161.3647 | 177.349271 | 422400.0 | 7372.27 | 0.1250 | 0.0528 | 177.349271 |
| **0.50** | 412.5000 | 7.199483 | 68.7500 | 2540.3412 | 44.337318 | 52800.0 | 921.53 | 0.2500 | 0.1057 | 44.337318 |
| **1.00** | 206.2500 | 3.599742 | 34.3750 | 635.0853 | 11.084329 | 6600.0 | 115.19 | 0.5000 | 0.2113 | 11.084329 |
| **2.00** | 103.1250 | 1.799871 | 17.1875 | 158.7713 | 2.771082 | 825.0 | 14.40 | 1.0000 | 0.4227 | 2.771082 |

*Nota sobre el par inercial específico:* Representa la aceleración angular $\alpha(t) = \frac{\tau_{\text{inercial}}}{I_{xx}}$ expresada en $\text{N}\cdot\text{m}/(\text{kg}\cdot\text{m}^2) \equiv \text{rad/s}^2$.

---

### 3.3 Secuencia combinada en dos fases y continuidad en la frontera
Si ambas fases se concatenan secuencialmente con duraciones $T_1$ y $T_2$ (tiempo total de maniobra $T_{\text{total}} = T_1 + T_2$):
- Para $t \in [0, T_1]$: $h(t) = 10 \cdot s(t/T_1)\text{ mm}$, $\theta(t) \equiv 0^\circ$.
- En el instante de enlace $t = T_1$:
  - Posición: $h(T_1) = 10\text{ mm}$, $\theta(T_1) = 0^\circ$.
  - Velocidad: $\dot{h}(T_1^-) = 0\text{ mm/s}$, $\dot{\theta}(T_1^+) = 0^\circ/\text{s}$.
  - Aceleración: $\ddot{h}(T_1^-) = 0\text{ mm/s}^2$, $\ddot{\theta}(T_1^+) = 0^\circ/\text{s}^2$.
- Para $t \in [T_1, T_1 + T_2]$: $h(t) \equiv 10\text{ mm}$, $\theta(t) = 110 \cdot s((t - T_1)/T_2)^\circ$.

Gracias a que el polinomio quintico anula tanto la primera como la segunda derivada en los extremos ($s'(1) = 0$, $s''(1) = 0$, $s'(0) = 0$, $s''(0) = 0$), la transición entre traslación y giro es estrictamente de clase $C^2$. No existen saltos bruscos en las fuerzas inerciales ni impactos de choque al pasar de una fase a la otra.

---

## 4. CHEQUEO ANALÍTICO VS MUESTREO DISCRETO Y DIFERENCIAS FINITAS

Un aspecto metodológico crítico al procesar perfiles continuos en simulaciones o controladores digitales es la discrepancia entre el pico continuo analítico y el valor máximo observado en una malla de muestreo uniforme con paso $\Delta t = \frac{T}{N-1}$.

### 4.1 Comportamiento diferencial de velocidad vs aceleración
- **Velocidad máxima ($v_{\max}$):** El pico ocurre en $u = 0{,}5$. Si el número de puntos $N$ es impar, el punto medio de la malla uniforme $i = \frac{N-1}{2}$ coincide con $u = 0{,}5$. En consecuencia, el error de muestreo de velocidad es exactamente cero para cualquier $N$ impar.
- **Aceleración máxima ($a_{\max}$):** El pico ocurre en la abscisa irracional $u_1 = \frac{1}{2} - \frac{\sqrt{3}}{6} \approx 0{,}2113248654$. Debido a que este número no es racional, ningún paso de muestreo uniforme $\Delta u = \frac{1}{N-1}$ contiene exactamente el pico. El error en la malla sigue el desarrollo de Taylor alrededor del máximo:
  $$s''(u_1 + \delta u) \approx s''(u_1) + \frac{1}{2} s^{(4)}(u_1) (\delta u)^2$$
  Dado que $|\delta u| \le \frac{\Delta u}{2}$, una estimación ingenua mediante muestreo subestima sistemáticamente la aceleración máxima por un factor de orden $\mathcal{O}\left(\frac{1}{N^2}\right)$.

### 4.2 Tabla comparativa de sensibilidad de muestreo (Fase $T = 0{,}5\text{ s}$, Traslación $10\text{ mm}$)
Se evaluó el perfil para distintas densidades de malla $N$, comparando el valor muestreado en malla analítica, la derivada numérica obtenida mediante diferencias finitas centrales de la posición ($a_{\text{fd}}[i] = \frac{q[i+1] - 2q[i] + q[i-1]}{\Delta t^2}$), y el error en la integral numérica trapezoidal de velocidad ($\int v \, dt = \Delta h = 10\text{ mm}$) y aceleración ($\int a \, dt = 0$):

| $N$ (puntos) | Paso $\Delta t$ (ms) | $v_{\text{muestreada}}$ (mm/s) | Error $v$ (%) | $a_{\text{muestreada}}$ (mm/s$^2$) | Error $a$ (%) | $a_{\text{diferencias finitas}}$ (mm/s$^2$) | Error dif. finitas (mm/s$^2$) | Error $\int v dt$ (mm) | $\int a dt$ (mm/s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **21** | 25.00 | 37.5000 | 0.0000% | 230.4000 | 0.2339% | 228.6000 | 2.3401 | $6{,}25 \times 10^{-5}$ | $7{,}11 \times 10^{-15}$ |
| **51** | 10.00 | 37.5000 | 0.0000% | 230.6304 | 0.1341% | 230.3616 | 0.5785 | $1{,}60 \times 10^{-6}$ | $-3{,}05 \times 10^{-14}$ |
| **101** | 5.00 | 37.5000 | 0.0000% | 230.9328 | 0.0032% | 230.8632 | 0.0769 | $1{,}00 \times 10^{-7}$ | $-3{,}48 \times 10^{-15}$ |
| **501** | 1.00 | 37.5000 | 0.0000% | 230.9382 | 0.0008% | 230.9354 | 0.0047 | $1{,}60 \times 10^{-10}$ | $9{,}58 \times 10^{-15}$ |
| **1001** | 0.50 | 37.5000 | 0.0000% | 230.9397 | 0.0002% | 230.9390 | 0.0011 | $9{,}99 \times 10^{-12}$ | $1{,}37 \times 10^{-14}$ |
| **5001** | 0.10 | 37.5000 | 0.0000% | 230.9401 | 0.0000% | 230.9401 | 0.00005 | $< 10^{-14}$ | $2{,}44 \times 10^{-14}$ |
| **10001** | 0.05 | 37.5000 | 0.0000% | 230.9401 | 0.0000% | 230.9401 | 0.00001 | $< 10^{-14}$ | $1{,}82 \times 10^{-14}$ |

*Conclusiones de la verificación numérica:*
1. La velocidad converge de forma exacta para $N$ impar incluso en mallas muy gruesas ($N=21$).
2. La aceleración calculada por diferencias finitas centrales converge con error cuadrático $\mathcal{O}(\Delta t^2)$, requiriendo $\Delta t \le 1\text{ ms}$ ($N \ge 501$) para tener un error inferior a $0{,}005\text{ mm/s}^2$ ($< 0{,}002\%$).
3. La integral numérica de la aceleración se anula hasta el límite de precisión de la máquina en punto flotante ($10^{-14}\text{ mm/s}$), confirmando que no hay acumulación de velocidad residual al final de la maniobra.

---

## 5. SEPARACIÓN RIGUROSA DE CINEMÁTICA RESPECTO A DINÁMICA Y DIMENSIONAMIENTO DE MOTORES

Un requerimiento fundamental de este estudio es no confundir las derivadas geométricas de la posición con los requerimientos dinámicos reales de fuerza, par, potencia y energía.

### 5.1 Ecuaciones dinámicas reales

#### Para la Fase 1 (Traslación):
La fuerza requerida en el punto de actuación viene dada por:
$$F_{\text{actuador}}(t) = m_{\text{móvil}} \cdot a(t) + F_{\text{gravedad}} + F_{\text{fricción}}(\dot{h}) + F_{\text{aerodinámica}}(t) + F_{\text{sello}}$$
donde:
- $m_{\text{móvil}}$: masa física total del conjunto desplazable (tapa, herrajes de unión, vástagos de guía).
- $F_{\text{gravedad}} = \pm m_{\text{móvil}} \cdot g \cdot \cos(\phi)$: para las 4 tapas superiores que elevan en $+Z$, la gravedad actúa en contra ($+m g$); para las 4 tapas inferiores que descienden en $-Z$, la gravedad actúa a favor ($-m g$). En vuelo maniobrado, $g$ debe sustituirse por el vector de aceleración aparente total.
- $F_{\text{fricción}}$: fricción de Coulomb, fricción estática de despegue (*stiction*) y amortiguamiento viscoso en los elementos guía o casquillos.
- $F_{\text{aerodinámica}}$: carga resultante por diferencia de presión $\Delta p$ entre el exterior y el conducto del ventilador de $84\text{ mm}$ de diámetro, más las fuerzas de arrastre o succión por el flujo cruzado exterior:
  $$F_{\text{aero}} = \iint_{\text{tapa}} (p_{\text{int}} - p_{\text{ext}}) \, dA$$
- $F_{\text{sello}}$: fuerza de compresión o despegue del elastómero/labio de estanqueidad perimetral que evita fugas de aire con el ventilador presurizado.

#### Para la Fase 2 (Giro):
El par requerido en el eje de rotación es:
$$\tau_{\text{actuador}}(t) = I_{xx} \cdot \alpha(t) + \tau_{\text{gravedad}}(\theta) + \tau_{\text{fricción}}(\dot{\theta}) + \tau_{\text{aerodinámica}}(\theta, \dot{\theta})$$
donde:
- $I_{xx}$: momento de inercia másico respecto al eje longitudinal de giro trasladado.
- $\tau_{\text{gravedad}}(\theta) = m_{\text{móvil}} \cdot g \cdot r_{\text{CG}}(\theta)$: par de desequilibrio gravitatorio que varía trigonométricamente con el ángulo de apertura $\theta$.
- $\tau_{\text{fricción}}$: par resistente por fricción en cojinetes o pasadores de la bisagra.
- $\tau_{\text{aerodinámica}}$: momento aerodinámico generado sobre la superficie de la tapa cuando se expone como una placa inclinada frente a la corriente de aire incidente o el flujo expulsado por el rotor.

#### Potencia y energía:
$$P_{\text{mec}}(t) = F(t) \cdot \dot{h}(t) \quad \text{ó} \quad P_{\text{mec}}(t) = \tau(t) \cdot \dot{\theta}(t)$$
$$E_{\text{mec}} = \int_0^T \max(0, P_{\text{mec}}(t)) \, dt$$
La potencia eléctrica demandada al bus de alimentación requiere incorporar el rendimiento electromecánico $\eta$ y las pérdidas térmicas por efecto Joule en el devanado del motor:
$$P_{\text{eléctrica}}(t) = \frac{P_{\text{mec}}(t)}{\eta_{\text{transmisión}} \cdot \eta_{\text{motor}}} + R_{\text{fase}} \cdot I_{\text{motor}}^2(t)$$

---

### 5.2 Auditoría de las referencias: Datos disponibles vs ausentes

Al auditar los archivos de referencia disponibles en `entradas/`:
1. En `entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json`:
   - `actual_mass_kg`: `null` (explícitamente nulo).
   - `actual_CG_m`: `null` (explícitamente nulo).
   - `actual_inertia_kgm2`: `null` (explícitamente nulo).
   - `mass_targets_are_actual_masses`: `false`.
   - `rotor_motor_servo_and_cooling_qualified`: `false`.
   - `predictive_flight_plant_accepted`: `false`.
2. En `entradas/investigacion-aeronautica/modelos_integrados/producto_A07/LEEME.md`:
   - *"Es un estudio de recorrido geométrico, no un mecanismo fabricable resuelto."*
   - *"No hay todavía guías, bisagras, soportes, cierres, sellos, cableado o actuadores de compuerta dimensionados."*
   - *"La trayectoria impone dos coordenadas cinemáticas; falta sintetizar y alojar el mecanismo que las produzca."*
   - *"Los ejes de movimiento están documentados como geometría de construcción, no como herrajes instalados."*
   - *"No se afirma que todos los actuadores quepan, que las tapas no obstruyan el flujo, o que el dispositivo pueda volar."*
   - *"Los solvers CFD pausados no se reanudaron."*
3. En `entradas/investigacion-aeronautica/modelos_integrados/producto_A07/VERIFICACION_RECORRIDO.json`:
   - Las 61 poses discretas ensayadas son comprobaciones booleanas de solape en CAD estático ("Discrete nominal intersections against reference hull... No continuous sweep, tolerance/deformation, loads or mechanism validation").

### 5.3 Imposibilidad física de dimensionar motores en esta etapa
Intentar calcular un tamaño de motor (p. ej., par de parada, corriente, par nominal RMS o potencia) a partir exclusivamente de las aceleraciones calculadas ($\ddot{h}_{\max}$ o $\alpha_{\max}$) adolece de las siguientes indeterminaciones insalvables:
1. **Masa e inercia inexistentes:** Sin $m$ ni $I_{xx}$, la fuerza inercial pura es una variable libre que puede multiplicarse por cualquier factor. La directriz impone explícitamente: *"No infieras que una reserva sin masa asignada tenga masa real nula o no nula"*. No es admisible inventar una masa arbitraria de tapa.
2. **Ausencia de mecanismo físico de transmisión:** Las dos fases (traslación de 10 mm y giro de 110°) son coordenadas de estudio cinemático en el espacio. El mecanismo real que producirá este movimiento (p. ej., un varillaje de cuatro barras, un husillo con corredera y leva, un actuador lineal directo acoplado a una biela, o un mecanismo de ginebra/biela-manivela) **aún no ha sido sintetizado**. La relación cinemática de transmisión $i(q) = \frac{dq_{\text{motor}}}{dq_{\text{tapa}}}$ y el brazo de palanca son completamente desconocidos. Un motor no empuja directamente la coordenada abstracta $h$, sino un eje de entrada físico.
3. **Cargas aerodinámicas no resueltas:** Con ventiladores de $84\text{ mm}$ de diámetro, cualquier diferencia de presión estática entre el interior del conducto y el exterior (p. ej. $\Delta p \sim 500 - 2000\text{ Pa}$) genera una fuerza directa sobre el área de la tapa ($\approx 0{,}0055\text{ m}^2$) de varios Newtons, que muy probablemente superará las fuerzas inerciales en órdenes de magnitud a bajas aceleraciones ($T \ge 0{,}5\text{ s}$). Dado que los solvers CFD no se han reanudado y no se valida el uso en avance rápido, la fuerza de viento es indeterminada.
4. **Fuerzas de sello y fricción estática:** Para sellar adecuadamente un conducto presurizado se requiere precarga elástica en los labios de sellado. Esta fuerza de despegue (*breakaway force*) suele gobernar el par pico de los actuadores en aplicaciones aeroespaciales, independientemente de la aceleración cinemática.
5. **Criterio térmico RMS:** El dimensionamiento de un servomotor o actuador eléctrico depende del par eficaz térmico $\tau_{\text{RMS}} = \sqrt{\frac{1}{T_{\text{ciclo}}} \int \tau^2 dt}$. Sin un ciclo de trabajo de misión definido (número de aperturas por hora, tiempo de retención en posición abierta), no se puede seleccionar la clase térmica del bobinado.

**Conclusión:** La cinemática aquí reportada proporciona las aceleraciones específicas ($a = F/m$ en N/kg y $\alpha = \tau/I$ en $\text{N}\cdot\text{m}/(\text{kg}\cdot\text{m}^2)$). El dimensionamiento de actuadores queda formalmente bloqueado hasta que se sintetice el mecanismo físico, se cuantifique la masa real de los herrajes y se resuelvan las cargas aerodinámicas CFD y de estanqueidad.

---

## 6. MATRIZ DE TRAZABILIDAD Y CLASIFICACIÓN DE DATOS

| Elemento / Variable | Valor / Magnitud | Unidad | Clasificación | Fuente / Justificación |
| :--- | :---: | :---: | :---: | :--- |
| **Recorrido de traslación ($\Delta h$)** | 10.0 | mm | Supuesto de estudio | `LEEME.md` ("Trayectoria candidata, referencia 5 kg") |
| **Ángulo de giro ($\Delta \theta$)** | 110.0 | grados | Supuesto de estudio | `LEEME.md` ("Los 110° son una pose de estudio, no un recorrido especificado") |
| **Forma de perfil temporal $s(u)$** | $10u^3 - 15u^4 + 6u^5$ | — | Supuesto de estudio | Requerimiento de análisis (polinomio quintico clásico) |
| **Duraciones de fase ($T$)** | 0.25, 0.50, 1.00, 2.00 | s | Supuesto de estudio | Requerimiento de análisis independiente |
| **Gravedad estándar de referencia ($g_0$)** | 9.80665 | m/s$^2$ | Dato estándar de referencia | `C02_CANDIDATA.json` (`operating_reference.g_m_s2`) |
| **Densidad de aire de referencia ($\rho$)** | 1.225 | kg/m$^3$ | Dato estándar de referencia | `C02_CANDIDATA.json` (`operating_reference.rho_kg_m3`) |
| **Diámetro nominal de conducto** | 84.0 | mm | Dato geométrico nominal CAD | `C02_CANDIDATA.json` (`fan_reference.nominal_bore_diameter_m`) |
| **Coeficiente $c_v$ de velocidad** | 1.875 (15/8) | — | Cálculo analítico exacto | Derivación $\max(s'(u))$ en $u = 0{,}5$ |
| **Coeficiente $c_a$ de aceleración** | $10/\sqrt{3} \approx 5{,}773503$ | — | Cálculo analítico exacto | Derivación $\max(s''(u))$ en $u = 0{,}5 - \sqrt{3}/6$ |
| **Velocidades y aceleraciones pico** | Ver Tablas 3.1 y 3.2 | mm/s, m/s, deg/s, rad/s$^2$, etc. | Cálculo analítico exacto | Fórmulas derivadas de escalado temporal |
| **Errores de muestreo y diferencias finitas** | Ver Tabla 4.2 | %, mm/s$^2$ | Cálculo numérico | Muestreo sobre mallas discretas de $N=21$ a $10001$ |
| **Masa real de tapa y mecanismo** | `null` | kg | Indeterminado / Ausente | `C02_CANDIDATA.json` (`actual_mass_kg: null`) |
| **Inercia másica respecto al eje de giro** | `null` | kg$\cdot$m$^2$ | Indeterminado / Ausente | `C02_CANDIDATA.json` (`actual_inertia_kgm2: null`) |
| **Centro de gravedad real** | `null` | m | Indeterminado / Ausente | `C02_CANDIDATA.json` (`actual_CG_m: null`) |
| **Fuerzas y momentos aerodinámicos** | No resueltos | N, N$\cdot$m | Indeterminado / Ausente | `LEEME.md` ("CFD pausados no se reanudaron") |
| **Fricción de guías y sellos** | Desconocida | N, N$\cdot$m | Indeterminado / Ausente | `LEEME.md` ("No hay todavía guías, bisagras, soportes, cierres, sellos") |
| **Datos medidos físicamente** | Ninguno | — | Medición | No existen ensayos experimentales en banco ni prototipos fabricados |

---

## 7. ENTREGABLES GENERADOS, PRUEBAS Y LIMITACIONES TÉCNICAS

### 7.1 Archivos generados en `salidas/`
1. `salidas/perfil_cinematico.py`:
   - Módulo en Python 3 puro (librería estándar, sin dependencias externas).
   - Implementación de las clases `SmoothQuinticPolynomial`, `SinglePhaseKinematics`, `TwoPhaseMotionProfile` y `DynamicsIndeterminacyAnalysis`.
   - Evaluación continua, muestreo numérico, cálculo de diferencias finitas centrales, integración por regla trapezoidal y exportación estructurada.
2. `salidas/test_perfiles.py`:
   - Batería de pruebas automatizadas con el marco estándar `unittest` de Python.
   - 15 casos de prueba unitaria que validan condiciones de contorno, derivadas exactas, simetría, monotonía, valores en todas las duraciones $T$, convergencia numérica, transición $C^2$ e indeterminación dinámica.
3. `salidas/tablas_perfiles.json`:
   - Archivo JSON estructurado con todos los valores calculados de las tablas de traslación, rotación, sensibilidad de muestreo y auditoría de la configuración de referencia.
4. `salidas/tablas_perfiles.csv`:
   - Archivo CSV delimitado por comas con las tablas tabuladas de ambas fases y del estudio de sensibilidad.
5. `salidas/REPORTE_PERFILES_TIEMPO.md`:
   - Este informe técnico formal.

### 7.2 Pruebas realizadas
Se ejecutó la suite de pruebas unitarias en el entorno aislado:
```bash
python3 -m unittest salidas/test_perfiles.py
```
**Resultado:** 15 pruebas superadas con éxito (`Ran 15 tests in 0.074s - OK`).
Entre las verificaciones críticas ejecutadas:
- Validación de que $s(0)=0, s(1)=1, s'(0)=0, s'(1)=0, s''(0)=0, s''(1)=0$.
- Confirmación de $c_v = 1{,}875$ y $c_a = 10/\sqrt{3}$ frente a búsqueda computacional extrema.
- Verificación de que la integral numérica de la velocidad reproduce exactamente el desplazamiento ($\Delta h = 10\text{ mm}$) con error menor a $10^{-7}\text{ mm}$.
- Verificación de que la integral numérica de la aceleración se anula exactamente ($\le 10^{-12}\text{ mm/s}$).
- Verificación de continuidad $C^2$ en la unión de fases $t = T_1$.
- Verificación de detección de valores nulos (`actual_mass_kg: None`) en la configuración de referencia.

### 7.3 Limitaciones técnicas y alcance
1. **Carácter puramente cinemático:** Este estudio define la geometría del movimiento en el tiempo. No modela la elasticidad estructural, juego mecánico en articulaciones, deformaciones térmicas ni holguras de fabricación.
2. **No existencia de mecanismos:** No se afirma ni se presupone que el mecanismo de apertura esté resuelto físicamente. Las bisagras y ejes de elevación indicados en A07 son geometrías auxiliares de referencia CAD, no componentes mecánicos reales con cojinetes, tolerancias o capacidad de carga.
3. **No garantía de encaje o cierre hermético:** No se afirma que los actuadores quepan en el volumen interno del fuselaje, ni que las compuertas abiertas permitan un flujo de ventilador sin pérdidas o recirculaciones perjudiciales.
4. **Indeterminación de actuadores:** Ningún servomotor o actuador puede seleccionarse o validarse técnicamente a partir de este informe sin antes definir la masa física real de la compuerta, ensayar la fricción de los sellos perimetrales y reanudar las simulaciones aerodinámicas CFD en condiciones de avance y despegue.
