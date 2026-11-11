# INFORME TÉCNICO: PARAMETRIZACIÓN CINEMÁTICA 2-DOF PARA LA TRAYECTORIA CANDIDATA A07

**Referencia del proyecto:** Arquitectura A — Ventiladores Internos  
**Línea base:** Trayectoria candidata A07 (Escala de referencia: 5 kg)  
**Fecha:** 2026-11-08  
**Autor:** Antigravity (Entorno de ejecución autónomo en sandbox)  
**Directorio de trabajo:** `cinematica_compuertas/`  
**Entregables en:** `salidas/`  

---

## 1. RESUMEN EJECUTIVO Y OBJETIVOS

El presente documento establece la formulación matemática y cinemática de referencia de dos grados de libertad (2-DOF) para la maniobra secuencial de apertura de compuertas en la arquitectura de ventiladores internos (candidata A07). La cinemática de estudio consta de:
1. **Fase 1 (Traslación pura exterior):** Desplazamiento normal de $10\text{ mm}$ en la escala de $5\text{ kg}$ ($+Z$ para tapas superiores, $-Z$ para tapas inferiores en el marco CAD).
2. **Fase 2 (Rotación pura exterior):** Giro de $110^\circ$ ($1.919862\text{ rad}$) alrededor de un eje longitudinal transportado que se traslada solidariamente con la compuerta durante la Fase 1.

Se analiza la cinemática temporal con perfiles suaves para duraciones de **$0.5\text{ s}$, $1.0\text{ s}$ y $2.0\text{ s}$ por fase** (tiempos totales de apertura de $1.0\text{ s}$, $2.0\text{ s}$ y $4.0\text{ s}$), evaluando derivadas hasta aceleración (y jerk), continuidad $C^2$ en la transición inter-fase, y escalamiento geométrico/dinámico a **$2\text{ kg}$, $5\text{ kg}$ y $10\text{ kg}$**.

Asimismo, se contrastan técnica y funcionalmente dos alternativas mecánicas conceptuales:
* **Concepto 1:** Carro lineal + Bisagra transportada (Cadena serial Prismático-Revoluta).
* **Concepto 2:** Ranura / Cam con guiado de seguidor (Mecanismo de leva de ranura programada).

> **ADVERTENCIA FORMAL OBLIGATORIA:** No se afirma que ninguno de los dos conceptos mecánicos quepa en el espacio interior de las camisas o del fuselaje, ni se afirma su fabricabilidad, viabilidad de tolerancias o aptitud para vuelo.

---

## 2. DISTINCIÓN METODOLÓGICA: DATOS MEDIDOS, SUPUESTOS Y CÁLCULOS

Para garantizar la máxima integridad técnica y trazabilidad de acuerdo con las directrices operativas:

### 2.1 Datos Medidos (o Referencias Geométricas CAD en entradas/)
* **Geometría de compuertas y ejes:** Archivo `entradas/investigacion-aeronautica/modelos_integrados/producto_A07/propuesta_elevacion.json`.
  * Total de compuertas: 8 compuertas (4 superiores, 4 inferiores).
  * Elevación nominal a escala 5 kg: $10.0\text{ mm}$ (`lift_mm: 10`).
  * Posición de ejes en pose cerrada: Coordenadas nominales CAD $[X, Y, Z]$ en milímetros para las 8 tapas.
  * Signos de traslación (`out`): $+1$ para compuertas superiores ($+Z$), $-1$ para compuertas inferiores ($-Z$).
  * Signos de rotación (`sign`): $+1$ o $-1$ respecto al eje longitudinal $+X$ para abrir hacia el exterior del fuselaje.
* **Muestreo discreto de recorrido:** Archivo `entradas/investigacion-aeronautica/modelos_integrados/producto_A07/VERIFICACION_RECORRIDO.json`.
  * 61 poses nominales evaluadas (6 de elevación de 0 a 10 mm en pasos de 2 mm; 55 de giro de 0 a 110° en pasos de 2°).
  * 488 pares booleanos evaluados con $0.0\text{ mm}^3$ de interferencia nominal.
* **Marco de referencia del vehículo:** Archivo `entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json`.
  * Coordenadas CAD: $+X$ longitudinal hacia popa (nariz en $-X$), $+Y$ lateral, $+Z$ vertical hacia arriba.
  * Marco de vuelo FLU: $+X$ hacia nariz, $+Y$ hacia babor (izquierda), $+Z$ vertical hacia arriba.

### 2.2 Datos Supuestos (Claramente declarados)
* **Masa e inercia de compuerta:**
  * En los archivos de entrada, `actual_mass_kg: null`, `actual_CG_m: null`, `actual_inertia_kgm2: null` (en `C02_CANDIDATA.json`).
  * **Regla estricta:** No se infiere que un registro sin masa asignada tenga masa real nula o no nula.
  * Para propósitos exclusivos de ilustración de fuerzas inerciales paramétricas, se adopta un **supuesto de referencia** de $m_{\text{tapa, 5kg}} = 0.050\text{ kg}$ ($50\text{ g}$) y un radio de giro supuesto respecto al eje de bisagra de $r_g = 0.040\text{ m}$ ($40\text{ mm}$), con escalamiento volumétrico $m \propto (M/5)$ e inercia $I \propto (M/5)^{5/3}$.
  * Se proporcionan adicionalmente métricas normalizadas ($F/m = \ddot{q}_1$ en $\text{m/s}^2$ y $\tau/I = \ddot{q}_2$ en $\text{rad/s}^2$) independientes de cualquier supuesto de masa.
* **Condiciones de contorno dinámicas:** Se asume reposo dinámico en $t=0$, en la conmutación inter-fase $t=T_{\text{fase}}$ y al final del recorrido $t=2T_{\text{fase}}$ (velocidad, aceleración y jerk nulos en reposo estático).
* **Ausencia de cargas no inerciales en la cinemática de referencia:** No se incorporan fuerzas aerodinámicas de avance rápido ni fricción de sellos, conforme a lo establecido en `LEEME.md` ("apertura destinada al estudio de baja velocidad; no se valida su uso en avance rápido").

### 2.3 Cálculos Realizados
* Formulación matemática analítica del vector de coordenadas generalizadas $\mathbf{q}(t) = [q_1(t), q_2(t)]^T$.
* Perfil temporal polinómico quíntico (mínimo jerk) y comparación con perfil cicloidal.
* Derivadas analíticas de posición, velocidad, aceleración y jerk.
* Validación cruzada contra diferencias finitas centradas de alta precisión ($dt = 10^{-5}\text{ s}$).
* Pruebas de salto de continuidad en la conmutación de fase ($|q(T^+) - q(T^-)|$, $|\dot{q}(T^+) - \dot{q}(T^-)|$, $|\ddot{q}(T^+) - \ddot{q}(T^-)|$).
* Matriz de escalamiento geométrico de desplazamientos con factor $\lambda = (M/5)^{1/3}$ y escalamiento temporal de aceleraciones con $1/T^2$.
* Matriz de transformación espacial 3D para cada compuerta $\mathbf{r}(t)$.

---

## 3. FORMULACIÓN MATEMÁTICA DE LA PARAMETRIZACIÓN CINEMÁTICA 2-DOF

### 3.1 Coordenadas Generalizadas y Cinemática Espacial
Se definen dos grados de libertad independientes pero secuenciados temporalmente:
* $q_1(t) \in [0, d_{\max}(M)]$: Coordenada lineal de traslación normal exterior [$\text{m}$].
* $q_2(t) \in [0, \theta_{\max}]$: Coordenada angular de apertura exterior [$\text{rad}$], con $\theta_{\max} = 110^\circ = \frac{11\pi}{18}\text{ rad} \approx 1.919862177\text{ rad}$.

Para la compuerta $i \in \{0, \dots, 7\}$:
* Posición cerrada del eje: $\mathbf{p}_{\text{closed}, i} = [X_{a, i}, Y_{a, i}, Z_{a, i}]^T$ [$\text{mm}$].
* Dirección del eje de giro: Vector unitario longitudinal $\hat{\mathbf{u}} = [1, 0, 0]^T$ (paralelo al eje CAD $X$).
* Dirección de traslación exterior: $\hat{\mathbf{e}}_{z, i} = [0, 0, \text{out}_i]^T$, con $\text{out}_i \in \{+1, -1\}$.
* Sentido de rotación exterior: $\sigma_i = \text{sign}_i \in \{+1, -1\}$.

La posición instantánea del eje transportado en función de $q_1(t)$ es:
$$\mathbf{p}_{\text{axis}, i}(t) = \mathbf{p}_{\text{closed}, i} + \text{out}_i \cdot q_1(t) \, \hat{\mathbf{k}}$$

La posición de cualquier punto material $\mathbf{r}_{\text{closed}}$ de la compuerta en coordenadas CAD en el instante $t$ se calcula mediante:
$$\mathbf{r}_i(t) = \mathbf{p}_{\text{axis}, i}(t) + \mathbf{R}_x(\sigma_i \cdot q_2(t)) \cdot (\mathbf{r}_{\text{closed}} - \mathbf{p}_{\text{closed}, i})$$

donde $\mathbf{R}_x(\phi)$ es la matriz de rotación elemental alrededor del eje longitudinal $X$:
$$\mathbf{R}_x(\phi) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\phi & -\sin\phi \\ 0 & \sin\phi & \cos\phi \end{bmatrix}$$

* En la **Fase 1** ($q_2(t) \equiv 0$): $\mathbf{r}_i(t) = \mathbf{r}_{\text{closed}} + \text{out}_i \cdot q_1(t) \hat{\mathbf{k}}$ (traslación pura en $Z$).
* En la **Fase 2** ($q_1(t) \equiv d_{\max}$): el punto gira rígidamente alrededor del eje transportado $\mathbf{p}_{\text{elevated}, i} = \mathbf{p}_{\text{closed}, i} + \text{out}_i \cdot d_{\max} \hat{\mathbf{k}}$.

---

### 3.2 Perfiles Temporales Suaves (Polinomio Quíntico de Mínimo Jerk)

Para garantizar suavidad de movimiento, minimizar choques estructurales y asegurar que los actuadores no experimenten discontinuidades de aceleración (jerk acotado y aceleraciones nulas en las fronteras), se implementa una ley de escala normalizada basada en un polinomio quíntico $s(\tau)$ con $\tau \in [0, 1]$:

$$s(\tau) = 10\tau^3 - 15\tau^4 + 6\tau^5$$

Sus derivadas respecto a la variable temporal normalizada $\tau$ son:
$$\frac{ds}{d\tau} = 30\tau^2(1 - \tau)^2$$
$$\frac{d^2s}{d\tau^2} = 60\tau(1 - \tau)(1 - 2\tau)$$
$$\frac{d^3s}{d\tau^3} = 60(1 - 6\tau + 6\tau^2)$$

#### Propiedades del Perfil Quíntico:
1. **Condiciones de frontera exactas:**
   $$s(0) = 0, \quad s(1) = 1$$
   $$\left.\frac{ds}{d\tau}\right|_{\tau=0} = 0, \quad \left.\frac{ds}{d\tau}\right|_{\tau=1} = 0$$
   $$\left.\frac{d^2s}{d\tau^2}\right|_{\tau=0} = 0, \quad \left.\frac{d^2s}{d\tau^2}\right|_{\tau=1} = 0$$
2. **Velocidad máxima normalizada:** Ocurre en $\tau = 0.5$:
   $$\left.\frac{ds}{d\tau}\right|_{\max} = 1.875$$
3. **Aceleración máxima normalizada:** Ocurre en $\tau_1 = \frac{1}{2} - \frac{\sqrt{3}}{6} \approx 0.211325$ y $\tau_2 = \frac{1}{2} + \frac{\sqrt{3}}{6} \approx 0.788675$:
   $$\left|\frac{d^2s}{d\tau^2}\right|_{\max} = \frac{10\sqrt{3}}{3} \approx 5.7735027$$
4. **Jerk normalizado en extremos:** En $\tau = 0$ y $\tau = 1$, $\frac{d^3s}{d\tau^3} = 60$ (acotado y finito).

---

### 3.3 Función Temporal Secuencial por Fases

Sea $T$ la duración de cada fase individual ($T \in \{0.5, 1.0, 2.0\}\text{ s}$). El tiempo total de maniobra es $2T$.

#### Intervalo $t \in [0, T]$ (Fase 1: Elevación):
$$\tau = \frac{t}{T}$$
$$q_1(t) = d_{\max} \cdot s(\tau), \quad \dot{q}_1(t) = \frac{d_{\max}}{T} \frac{ds}{d\tau}, \quad \ddot{q}_1(t) = \frac{d_{\max}}{T^2} \frac{d^2s}{d\tau^2}$$
$$q_2(t) \equiv 0, \quad \dot{q}_2(t) \equiv 0, \quad \ddot{q}_2(t) \equiv 0$$

#### Intervalo $t \in [T, 2T]$ (Fase 2: Rotación):
$$\tau = \frac{t - T}{T}$$
$$q_1(t) \equiv d_{\max}, \quad \dot{q}_1(t) \equiv 0, \quad \ddot{q}_1(t) \equiv 0$$
$$q_2(t) = \theta_{\max} \cdot s(\tau), \quad \dot{q}_2(t) = \frac{\theta_{\max}}{T} \frac{ds}{d\tau}, \quad \ddot{q}_2(t) = \frac{\theta_{\max}}{T^2} \frac{d^2s}{d\tau^2}$$

---

## 4. PRUEBAS DE CONTINUIDAD Y DERIVADAS

### 4.1 Continuidad en la Conmutación de Fase ($t = T$)
En la transición entre la Fase 1 y la Fase 2 en $t = T$:
* **Límite por la izquierda ($t \to T^-$):**
  $$q_1(T^-) = d_{\max}, \quad \dot{q}_1(T^-) = 0, \quad \ddot{q}_1(T^-) = 0$$
  $$q_2(T^-) = 0, \quad \dot{q}_2(T^-) = 0, \quad \ddot{q}_2(T^-) = 0$$
* **Límite por la derecha ($t \to T^+$):**
  $$q_1(T^+) = d_{\max}, \quad \dot{q}_1(T^+) = 0, \quad \ddot{q}_1(T^+) = 0$$
  $$q_2(T^+) = 0, \quad \dot{q}_2(T^+) = 0, \quad \ddot{q}_2(T^+) = 0$$

Como los límites laterales y el valor exacto en $t = T$ coinciden estrictamente para la posición, velocidad y aceleración:
$$\lim_{t \to T^-} \mathbf{q}(t) = \lim_{t \to T^+} \mathbf{q}(t) = \mathbf{q}(T) \implies \text{Continuidad } C^0$$
$$\lim_{t \to T^-} \dot{\mathbf{q}}(t) = \lim_{t \to T^+} \dot{\mathbf{q}}(t) = \mathbf{0} \implies \text{Continuidad } C^1$$
$$\lim_{t \to T^-} \ddot{\mathbf{q}}(t) = \lim_{t \to T^+} \ddot{\mathbf{q}}(t) = \mathbf{0} \implies \text{Continuidad } C^2$$

### 4.2 Resultados Numéricos de Continuidad (Evaluados con $\epsilon = 10^{-7}\text{ s}$)
Ejecutados a través de `cinematica_A07.py` y `test_cinematica.py`:
* Salto de posición $\Delta q_1 = |q_1(T^+) - q_1(T^-)| < 3 \times 10^{-17}\text{ m}$ (precisión de máquina).
* Salto de velocidad $\Delta \dot{q}_1 = |\dot{q}_1(T^+) - \dot{q}_1(T^-)| < 4 \times 10^{-14}\text{ m/s}$.
* Salto de aceleración $\Delta \ddot{q}_1 = |\ddot{q}_1(T^+) - \ddot{q}_1(T^-)| < 7 \times 10^{-7}\text{ m/s}^2$.
* Salto de posición $\Delta q_2 < 10^{-16}\text{ rad}$.
* Salto de velocidad $\Delta \dot{q}_2 < 10^{-13}\text{ rad/s}$.
* Salto de aceleración $\Delta \ddot{q}_2 < 10^{-6}\text{ rad/s}^2$.

### 4.3 Validación Cruzada con Diferencias Finitas
Se compararon las derivadas analíticas frente a diferencias finitas centradas de paso $dt = 10^{-5}\text{ s}$ en 50 puntos muestreados a lo largo de la trayectoria:
* Error máximo en velocidad lineal $\dot{q}_1$: $8.91 \times 10^{-12}\text{ m/s}$.
* Error máximo en aceleración lineal $\ddot{q}_1$: $5.53 \times 10^{-11}\text{ m/s}^2$.
* Error máximo en velocidad angular $\dot{q}_2$: $1.70 \times 10^{-9}\text{ rad/s}$.
* Error máximo en aceleración angular $\ddot{q}_2$: $1.12 \times 10^{-8}\text{ rad/s}^2$.

---

## 5. ESCALAMIENTO GEOMÉTRICO Y DINÁMICO (2 kg, 5 kg, 10 kg x 0.5 s, 1 s, 2 s)

### 5.1 Regla de Escalamiento Geométrico
Conforme a `LEEME.md` ("Los desplazamientos se escalan geométricamente con $(m/5)^{1/3}$"):
* Factor de escala: $\lambda(M) = \left(\frac{M}{5.0}\right)^{1/3}$.
* Elevación escalada: $d_{\max}(M) = 10.0\text{ mm} \times \lambda(M)$.
  * Para $M = 2.0\text{ kg}$: $\lambda = (2/5)^{1/3} \approx 0.736806 \implies d_{\max} = 7.368\text{ mm} \approx 7.37\text{ mm}$.
  * Para $M = 5.0\text{ kg}$: $\lambda = 1.000000 \implies d_{\max} = 10.000\text{ mm}$.
  * Para $M = 10.0\text{ kg}$: $\lambda = (10/5)^{1/3} \approx 1.259921 \implies d_{\max} = 12.599\text{ mm} \approx 12.60\text{ mm}$.
* Recorrido angular $\theta_{\max}$: Al ser adimensional, permanece idéntico en las tres escalas ($110.0^\circ = 1.919862\text{ rad}$).

### 5.2 Matriz de Cinemática y Dinámica de Extremos
A continuación se presenta la matriz completa de valores pico para el perfil quíntico de referencia:

| Masa Dron (kg) | $T_{\text{fase}}$ (s) | $T_{\text{total}}$ (s) | Lift $d_{\max}$ (mm) | $v_{1, \max}$ (mm/s) | $a_{1, \max}$ ($\text{m/s}^2$) | $\omega_{2, \max}$ (rad/s) | $\alpha_{2, \max}$ ($\text{rad/s}^2$) | $F_{\text{in}} / m$ ($\text{N/kg}$) | $\tau_{\text{in}} / I$ ($\text{rad/s}^2$) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2.0** | 0.5 | 1.0 | 7.37 | 27.63 | **0.1702** | 7.20 | **44.3373** | 0.1702 | 44.3373 |
| **2.0** | 1.0 | 2.0 | 7.37 | 13.82 | **0.0425** | 3.60 | **11.0843** | 0.0425 | 11.0843 |
| **2.0** | 2.0 | 4.0 | 7.37 | 6.91 | **0.0106** | 1.80 | **2.7711** | 0.0106 | 2.7711 |
| **5.0** | 0.5 | 1.0 | 10.00 | 37.50 | **0.2309** | 7.20 | **44.3373** | 0.2309 | 44.3373 |
| **5.0** | 1.0 | 2.0 | 10.00 | 18.75 | **0.0577** | 3.60 | **11.0843** | 0.0577 | 11.0843 |
| **5.0** | 2.0 | 4.0 | 10.00 | 9.38 | **0.0144** | 1.80 | **2.7711** | 0.0144 | 2.7711 |
| **10.0** | 0.5 | 1.0 | 12.60 | 47.25 | **0.2910** | 7.20 | **44.3373** | 0.2910 | 44.3373 |
| **10.0** | 1.0 | 2.0 | 12.60 | 23.62 | **0.0727** | 3.60 | **11.0843** | 0.0727 | 11.0843 |
| **10.0** | 2.0 | 4.0 | 12.60 | 11.81 | **0.0182** | 1.80 | **2.7711** | 0.0182 | 2.7711 |

#### Observaciones Técnicas de la Matriz:
1. **Aceleraciones lineales bajas:** La aceleración lineal pico es notablemente modesta (menos de $0.3\text{ m/s}^2$, o aprox. $0.03\text{ g}$ incluso para $T_{\text{fase}} = 0.5\text{ s}$ en $10\text{ kg}$). Esto se debe a que la carrera de traslación ($7.37$ a $12.60\text{ mm}$) es pequeña.
2. **Aceleraciones angulares dominantes:** La aceleración angular alcanza **$44.34\text{ rad/s}^2$** en la maniobra rápida ($T = 0.5\text{ s}$), mientras que se reduce a **$2.77\text{ rad/s}^2$** en la apertura suave ($T = 2.0\text{ s}$), escalando exactamente con $1/T^2$ (reducción de un factor de 16).
3. **Comparación con Perfil Cicloidal:**
   * En el perfil cicloidal, $v_{1, \max} = 2.0 \cdot (d_{\max}/T)$ (un 6.7% superior al quíntico).
   * La aceleración máxima cicloidal es $a_{1, \max} = 2\pi \cdot (d_{\max}/T^2) \approx 6.283 \cdot (d_{\max}/T^2)$ (un 8.8% superior al quíntico).
   * El polinomio quíntico optimiza la suavidad y minimiza la aceleración pico y el jerk cuadrático integral.

---

## 6. VERIFICACIÓN DE EXTREMOS Y SIGNOS POR TAPA DESDE JSON

Se auditó el archivo `propuesta_elevacion.json` y se contrastó con las 61 poses discretas de `VERIFICACION_RECORRIDO.json`.

### 6.1 Tabla de Verificación de las 8 Compuertas (Escala 5 kg)

| ID Compuerta | $X_{\text{axis}}$ (mm) | $Y_{\text{axis}}$ (mm) | $Z_{\text{axis}}$ (mm) | `lift_mm` | Signo Traslación (`out`) | Signo Giro (`sign`) | Sentido Físico de Apertura | Estado Verificación |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|:---:|
| `compuerta_0_superior_enrasada` | -200.0 | -124.0 | +65.462 | 10.0 | **+1** | **+1** | Traslación $+Z$, Giro exterior hacia $-Y$ | **CORRECTO** |
| `compuerta_0_inferior_enrasada` | -200.0 | -124.0 | -51.813 | 10.0 | **-1** | **-1** | Traslación $-Z$, Giro exterior hacia $-Y$ | **CORRECTO** |
| `compuerta_1_superior_enrasada` | -200.0 | +124.0 | +65.462 | 10.0 | **+1** | **-1** | Traslación $+Z$, Giro exterior hacia $+Y$ | **CORRECTO** |
| `compuerta_1_inferior_enrasada` | -200.0 | +124.0 | -51.813 | 10.0 | **-1** | **+1** | Traslación $-Z$, Giro exterior hacia $+Y$ | **CORRECTO** |
| `compuerta_2_superior_enrasada` | +200.0 | -124.0 | +45.510 | 10.0 | **+1** | **+1** | Traslación $+Z$, Giro exterior hacia $-Y$ | **CORRECTO** |
| `compuerta_2_inferior_enrasada` | +200.0 | -124.0 | -34.382 | 10.0 | **-1** | **-1** | Traslación $-Z$, Giro exterior hacia $-Y$ | **CORRECTO** |
| `compuerta_3_superior_enrasada` | +200.0 | +124.0 | +45.510 | 10.0 | **+1** | **-1** | Traslación $+Z$, Giro exterior hacia $+Y$ | **CORRECTO** |
| `compuerta_3_inferior_enrasada` | +200.0 | +124.0 | -34.382 | 10.0 | **-1** | **+1** | Traslación $-Z$, Giro exterior hacia $+Y$ | **CORRECTO** |

### 6.2 Análisis Geométrico de Coherencia de Signos
* **Eje longitudinal $X$:** En el marco CAD, el vector unitario del eje de rotación es $\hat{\mathbf{u}} = [1, 0, 0]^T$.
* **Sentido de traslación (`out`):**
  * Para las compuertas superiores ($Z > 0$), $\text{out} = +1 \implies \Delta Z = +10\text{ mm}$ (eleva hacia arriba, saliendo del ducto).
  * Para las compuertas inferiores ($Z < 0$), $\text{out} = -1 \implies \Delta Z = -10\text{ mm}$ (desciende hacia abajo, saliendo del ducto).
* **Sentido de rotación (`sign`):**
  * Para tapas en el lado $Y = -124\text{ mm}$ (Compuertas 0 y 2):
    * Superior: Una rotación positiva ($+1$) alrededor de $+X$ traslada puntos en $+Z$ hacia $-Y$ ($\sin\phi > 0$), abriendo hacia el exterior lateral.
    * Inferior: Una rotación negativa ($-1$) alrededor de $+X$ traslada puntos en $-Z$ hacia $-Y$, abriendo hacia el exterior lateral.
  * Para tapas en el lado $Y = +124\text{ mm}$ (Compuertas 1 y 3):
    * Superior: Una rotación negativa ($-1$) alrededor de $+X$ traslada puntos en $+Z$ hacia $+Y$, abriendo hacia el exterior lateral.
    * Inferior: Una rotación positiva ($+1$) alrededor de $+X$ traslada puntos en $-Z$ hacia $+Y$, abriendo hacia el exterior lateral.
* **Concordancia con `VERIFICACION_RECORRIDO.json`:**
  * Poses 0 a 5: ángulo $= 0.0^\circ$, lift $= 0.0, 2.0, 4.0, 6.0, 8.0, 10.0\text{ mm}$.
  * Poses 5 a 60: lift $= 10.0\text{ mm}$, ángulo $= 0.0^\circ \to 110.0^\circ$ en pasos de $2.0^\circ$.
  * Coincidencia exacta del 100% en los 61 nodos.

---

## 7. DECLARACIÓN EXPLÍCITA DE VARIABLES NO VERIFICABLES

En estricto cumplimiento de la instrucción (*"si no se pueden verificar, decláralo"*), se declara que las siguientes variables **NO son verificables** a partir de los archivos provistos:

1. **Masa real, centro de gravedad y tensor de inercia de compuerta:**
   * En `C02_CANDIDATA.json` figura explícitamente:
     ```json
     "actual_mass_kg": null,
     "actual_CG_m": null,
     "actual_inertia_kgm2": null
     ```
   * No existe asignación de masa física en el modelo. No puede inferirse si la masa es nula o no nula.
2. **Dimensionamiento y volumen de mecanismos y actuadores:**
   * En `LEEME.md` se declara textualmente:
     > *"No hay todavía guías, bisagras, soportes, cierres, sellos, cableado o actuadores de compuerta dimensionados. La trayectoria impone dos coordenadas cinemáticas; falta sintetizar y alojar el mecanismo que las produzca."*
   * Ningún herraje, biela, motor o corredera está presente en el CAD ni en los archivos JSON.
3. **Respuesta dinámica del actuador:**
   * En `C02_CANDIDATA.json`, `"servo_response_s": null`. Se desconoce el tiempo de subida, ancho de banda o constante de tiempo real del servomotor.
4. **Interferencias elásticas bajo carga y tolerancias de fabricación:**
   * En `VERIFICACION_RECORRIDO.json` se declara:
     > *"No continuous sweep, tolerance/deformation, loads or mechanism validation."*
   * El cribado de 61 nodos es puramente geométrico nominal estático.
5. **Cargas aerodinámicas y viabilidad de vuelo:**
   * En `LEEME.md` se explicita: *"No se afirma que las tapas no obstruyan el flujo, o que el dispositivo pueda volar. La apertura está destinada al estudio de baja velocidad; no se valida su uso en avance rápido. Los solvers CFD pausados no se reanudaron."*

---

## 8. COMPARATIVA TÉCNICA DE CONCEPTOS MECÁNICOS

Se comparan dos conceptos cinemáticos para materializar la trayectoria A07.

> **DECLARACIÓN OBLIGATORIA:** No se afirma que ninguno de los dos conceptos mecánicos quepa en el espacio asignado ni se afirma su fabricabilidad.

### 8.1 Concepto 1: Carro Lineal + Bisagra Transportada (Cadena Serial $P \to R$)
* **Topología:** Par prismático ($P$) fijado a la estructura del conducto o fuselaje, cuyo elemento móvil (carro) aloja los cojinetes de un par revoluta ($R$).
* **Principio de operación:**
  1. El carro se desplaza guiado $10\text{ mm}$ en dirección normal ($+Z$ o $-Z$).
  2. Al alcanzar el tope de traslación, se activa el giro de $110^\circ$ alrededor del eje transportado en el carro.
* **Esquemas de accionamiento:**
  * *Accionamiento dual:* Un actuador lineal (husillo en miniatura o solenoide biestable) para la elevación, más un servomotor rotativo montado en el carro para el giro.
  * *Accionamiento único secuencial:* Servomotor rotativo conectado a una manivela con resorte de secuencia o pestillo de enclavamiento; la primera parte del recorrido empuja el carro hasta enclavar el tope, y el resto del recorrido rota la compuerta.
* **Ventajas Técnicas:**
  * Desacoplamiento cinemático perfecto: permite variar o recalibrar independientemente la elevación y el ángulo de apertura mediante topes ajustables o software.
  * Contacto superficial en guías lineales y casquillos de pivote cilíndricos, lo que resulta en bajas presiones de contacto comparadas con pares superiores.
  * Capacidad de operar o mantener la compuerta en modo de elevación parcial o total sin necesidad de girar.
* **Desventajas y Riesgos:**
  * Mayor peso y volumen debido a la masa no suspendida del actuador rotativo viajando en el carro.
  * Vulnerabilidad a encallamiento por ladeo (*cocking/binding*): si la fuerza aerodinámica genera un momento de flexión elevado con una relación desfavorable entre la distancia entre apoyos de la guía ($w$) y la carrera ($h$), el carro puede trabarse por fricción estática de Coulomb.
  * Dificultades de sellado contra el flujo y partículas de suciedad en las guías lineales expuestas al conducto del ventilador.

---

### 8.2 Concepto 2: Ranura / Cam con Guiado de Seguidor (Leva de Ranura Programada)
* **Topología:** Mecanismo de par superior de 1 grado de libertad cinemático. Una pista ranurada fija (mecanizada en la costilla o mampara del conducto) guía un rodillo seguidor o pasador solidario a un brazo de la compuerta.
* **Principio de operación:**
  * La ranura posee un perfil geométrico con dos tramos tangentes continuos:
    1. Tramo rectilíneo vertical de $10\text{ mm}$ normal al fuselaje.
    2. Tramo curvo circular de radio $R_{\text{cam}}$ subtendiendo un arco de $110^\circ$ centrado en la posición elevada del eje.
  * Un único actuador lineal o manivela empuja el seguidor a lo largo de la pista.
* **Ventajas Técnicas:**
  * Sincronización intrínseca garantizada geométricamente: es físicamente imposible que la compuerta gire antes de haber recorrido la elevación de $10\text{ mm}$, eliminando el riesgo de fallo de coordinación electrónica.
  * Actuador único y estático: el actuador permanece anclado a la estructura fija del fuselaje, reduciendo masa móvil y eliminando cables flexibles en movimiento.
  * Menor número de piezas estructurales discretas y potencial compacidad axial si la ranura se integra en las costillas existentes.
* **Desventajas y Riesgos:**
  * Contacto de línea o puntual de Hertz: elevadas concentraciones de tensión en el contacto seguidor-pared de ranura, con riesgo de deformación plástica local, desgaste por frotamiento (*fretting*) o picado (*pitting*).
  * Ángulo de presión crítico en la transición ("rodilla" entre tramo recto y curvo): si la tangente de la leva genera un ángulo de presión $\alpha > \arctan(1/\mu)$, el mecanismo se autoenclava irreversiblemente.
  * Rigidez nula de ajuste post-fabricación: cualquier cambio en la elevación o el ángulo de giro requiere rediseñar y mecanizar placas de levas completamente nuevas.
  * Holguras mecánicas indispensables para evitar el gripado térmico que pueden inducir traqueteo (*flutter/chatter*) de la compuerta bajo flujo turbulento.

---

### 8.3 Cuadro Comparativo de Compromisos Técnicos

| Criterio de Comparación | Concepto 1: Carro + Bisagra | Concepto 2: Ranura / Cam con Guiado |
|---|---|---|
| **Grados de libertad cinemáticos** | 2 independientes (o 1 con enclavamiento) | 1 acoplado por geometría |
| **Sincronización de fases** | Requiere control electrónico o pestillo mecánico | Intrínseca por restricción de contacto |
| **Tipo de contacto mecánico** | Superficial (guías prismáticas y casquillos) | Puntual/Lineal (Hertziano en paredes de ranura) |
| **Concentración de tensiones** | Bajas / moderadas | Altas en el pasador y zona de transición |
| **Riesgo primario de bloqueo** | Momento de vuelco (ladeo de carro) | Ángulo de presión excesivo en la rodilla |
| **Actuador y cableado** | Actuador móvil viaja con la compuerta | Actuador fijo a la estructura del fuselaje |
| **Ajustabilidad y calibración** | Alta (ajustable por software o topes de carrera) | Nula (inmutable sin remecanizado de leva) |
| **Piezas móviles y masa** | Mayor número de componentes y mayor inercia móvil | Menor número de piezas, menor inercia móvil |

---

## 9. CÓDIGO FUENTE REPRODUCIBLE Y SUITE DE PRUEBAS

Todos los scripts y suites de verificación se desarrollaron en Python 3 puro (estándar, sin dependencias externas):
* `salidas/cinematica_A07.py`: Motor cinemático analítico, evaluador de perfiles temporales, matriz de escalamiento y verificador de JSON.
* `salidas/test_cinematica.py`: Suite de 8 pruebas unitarias automatizadas (`unittest`).
* Archivos de datos generados en formato JSON:
  * `salidas/resultados_perfiles.json`: Matriz de cinemática temporal, saltos de continuidad y validación por diferencias finitas.
  * `salidas/verificacion_signos_tapas.json`: Auditoría de signos, coordenadas de ejes y estado de verificación por compuerta.
  * `salidas/comparativa_mecanismos.json`: Detalle estructurado de la comparativa conceptual de mecanismos.

### 9.1 Instrucciones de Reproducción
Para ejecutar las comprobaciones en el entorno sandbox:
```bash
# 1. Ejecutar el generador cinemático y comprobaciones principales
python3 salidas/cinematica_A07.py

# 2. Ejecutar la suite de pruebas unitarias automatizadas
python3 salidas/test_cinematica.py
```

---

## 10. CONCLUSIONES Y LIMITACIONES

### 10.1 Resumen de Entregables Generados
1. `salidas/cinematica_A07.py`: Script principal con formulación 2-DOF, perfiles quíntico/cicloidal, derivadas analíticas y verificador JSON.
2. `salidas/test_cinematica.py`: Suite de pruebas unitarias (`Ran 8 tests in 0.001s, OK`).
3. `salidas/resultados_perfiles.json`: Resultados de la matriz de escalamiento (2/5/10 kg x 0.5/1/2 s), continuidad y derivadas.
4. `salidas/verificacion_signos_tapas.json`: Verificación de signos y ejes para las 8 compuertas.
5. `salidas/comparativa_mecanismos.json`: Síntesis de los conceptos carro+bisagra y ranura/cam.
6. `salidas/INFORME_PARAMETRIZACION_A07.md`: El presente informe técnico detallado.

### 10.2 Pruebas Realizadas
* Verificación de condiciones de contorno de posición, velocidad y aceleración en extremos ($t=0$, $t=T_{\text{fase}}$, $t=2T_{\text{fase}}$).
* Verificación de continuidad $C^0$, $C^1$ y $C^2$ en la conmutación inter-fase con límites infinitesimales ($\epsilon = 10^{-7}\text{ s}$).
* Verificación analítica vs numérica (diferencias finitas) de derivadas hasta aceleración.
* Verificación de signos de traslación (`out`: $\pm 1$) y rotación (`sign`: $\pm 1$) de las 8 compuertas desde `propuesta_elevacion.json`.
* Comprobación de coincidencia con las 61 poses discretas de `VERIFICACION_RECORRIDO.json`.
* Comprobación del escalamiento temporal de aceleraciones inversamente proporcional a $T^2$.
* Comprobación del escalamiento geométrico de desplazamientos con $(M/5)^{1/3}$ ($7.37$, $10.00$, $12.60\text{ mm}$).

### 10.3 Limitaciones Técnicas Declaradas
* **Ausencia de masa de compuerta:** La masa de las compuertas no está definida en el modelo de entrada (`null`). Las fuerzas dinámicas calculadas son de naturaleza normalizada ($F/m$) o paramétrica bajo supuestos explícitos.
* **Modelo puramente cinemático:** No se incorporan deformaciones estructurales, holguras, tolerancias de mecanizado ni fuerzas aerodinámicas bajo flujo inducido o avance rápido.
* **Sin validación de empaquetamiento o actuadores:** Ningún actuador o mecanismo conceptual ha sido dimensionado físicamente ni se garantiza que quepa en el espacio libre interior entre camisas y fuselaje.
* **Sin resolución CFD o aeroelástica:** La viabilidad aerodinámica de la compuerta en posiciones intermedias o abiertas no ha sido resuelta ni validada en vuelo.
