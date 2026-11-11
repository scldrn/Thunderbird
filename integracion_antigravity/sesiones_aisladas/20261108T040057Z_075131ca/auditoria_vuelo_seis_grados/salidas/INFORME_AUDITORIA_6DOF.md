# INFORME DE AUDITORÍA TÉCNICA: SIMULACIÓN DE VUELO 6DOF Y SCRIPT DE VERIFICACIÓN

**Proyecto**: Plataforma de Vuelo 6DOF con Cuatro Ventiladores Internos Vectorizados  
**Identificador de Configuración Evaluada**: `C02_COMPACTA_x160_5kg_2026-11-03_r2` (Ref: `C02_CANDIDATA.json`)  
**Archivos Auditados (en `entradas/`)**:
- `entradas/investigacion-aeronautica/simulacion_vuelo_A/simular.py` (77 líneas, solo lectura)
- `entradas/investigacion-aeronautica/simulacion_vuelo_A/verificar.py` (18 líneas, solo lectura)
- `entradas/investigacion-aeronautica/simulacion_vuelo_A/INFORME.md` (50 líneas, solo lectura)
- `entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json` (142 líneas, solo lectura)  
**Modalidad de Auditoría**: Auditoría analítica y por lectura de código de dinámica de vuelo, cinemática, leyes de control, integración y verificación numérica, con separación formal entre HECHO, HIPÓTESIS y RECOMENDACIÓN.

---

## 1. RESUMEN EJECUTIVO Y DICTAMEN TÉCNICO

### 1.1 Dictamen Técnico General
La simulación implementada en `simular.py` es un **demostrador numérico cinemático e idealizado en lazo cerrado** para un cuerpo rígido puntual gobernado por cuatro vectores de fuerza teóricos. **No constituye un modelo de vuelo validado, predictivo ni certificado para el vehículo real**, ni refleja las características físicas instaladas descritas en el archivo de arquitectura `C02_CANDIDATA.json`.

El script de verificación `verificar.py` únicamente evalúa tres casos canónicos desacoplados de 1 grado de libertad con integración numérica elemental y un ensayo de medio paso sobre una ejecución previa. Dichas pruebas no abarcan el acoplamiento no lineal de Euler, no verifican la estabilidad física del asignador SLSQP ante perturbaciones severas y no satisfacen la batería metodológica de verificación de dinámicas 6DOF según estándares como NASA/TM-2015-218675.

### 1.2 Declaración Epistémica de Datos (Clasificación de Rigor)
- **Datos Medidos**: **0%**. En todo el conjunto de archivos adjuntos no existe una sola medición física de empuje, par, corriente, consumo, coeficiente aerodinámico, centro de gravedad real o tensor de inercia real (`actual_mass_kg: null`, `actual_CG_m: null`, `actual_inertia_kgm2: null`, `installed_map_available: false` en `C02_CANDIDATA.json#L119-L123`).
- **Datos Supuestos (Hipótesis)**: Centro de gravedad coincidente con el origen $(0,0,0)$; tensor de inercia diagonal obtenido de un elipsoide macizo homogéneo de referencia externa ($1.341 \times 0.321821 \times 0.194110$ m); brazos de fuerza vertical en $Z$ de $-0.039$ m para $F_x$ y $-0.021$ m para $F_y$; empuje máximo escalable linealmente con la masa ($21$ N a $5$ kg); deflexión cónica máxima simétrica de $35^\circ$; dinámica de actuadores modelada como filtro lineal de primer orden ($\tau = 0.08$ s) con límite de tasa ($50$ N/s); ausencia total de resistencia aerodinámica de avance, sustentación de fuselaje/aletas y efecto giroscópico o reactivo de los rotores.
- **Datos Calculados**: Integración RK4 a $\Delta t = 0.005$ s; asignación cuadrática secuencial SLSQP a 50 Hz; aceleraciones y velocidades del perfil predefinido de 24 s; errores residuales respecto a soluciones analíticas uniparamétricas.

---

## 2. AUDITORÍA LÍNEA POR LÍNEA DEL SIMULADOR 6DOF (`simular.py`)

A continuación se detallan las ecuaciones, convenciones, integrador, control, saturaciones y supuestos verificados línea a línea en `entradas/investigacion-aeronautica/simulacion_vuelo_A/simular.py`:

### 2.1 Ecuaciones de Movimiento Implementadas
El estado del vehículo está parametrizado por un vector de 13 estados:
$$y = \begin{bmatrix} r^T & v^T & q^T & \omega^T \end{bmatrix}^T \in \mathbb{R}^{13}$$
donde $r = [x, y, z]^T$ es la posición inercial (m), $v = [\dot{x}, \dot{y}, \dot{z}]^T$ es la velocidad inercial (m/s), $q = [q_x, q_y, q_z, q_w]^T$ es el cuaternión de actitud (convención SciPy, parte vectorial primero y escalar al final), y $\omega = [\omega_x, \omega_y, \omega_z]^T$ es la velocidad angular expresada en el marco de cuerpo (rad/s).

1. **Dinámica de Traslación (Segunda Ley de Newton)**:
   - **Línea de código**: `simular.py#L9`:
     ```python
     acc = (rot.apply(F.sum(axis=0)) + ext) / mass - np.array([0, 0, G])
     ```
   - **Ecuación matemática**:
     $$\ddot{r} = \frac{1}{m} \left( R(q) \sum_{i=0}^3 F_i + F_{\text{ext}} \right) - \begin{bmatrix} 0 \\ 0 \\ g \end{bmatrix}$$
   - **Detalle de términos**:
     - $F_i = [F_{i,x}, F_{i,y}, F_{i,z}]^T \in \mathbb{R}^3$ es el vector de fuerza ejercido por el actuador $i$ en el marco del cuerpo (N).
     - $R(q)$ es la matriz de rotación del cuerpo al marco inercial (`rot = R.from_quat(q)` en `simular.py#L8`).
     - $F_{\text{ext}} \in \mathbb{R}^3$ es la perturbación inercial externa programada ($[3, -2, 0]^T \frac{m}{5}$ N durante $12 \le t < 13$ s; $0$ en otro caso, `simular.py#L46`).
     - $g = 9.80665$ m/s² (`simular.py#L5`).
     - $m$ es la masa supuesta (`mass = 5.0` kg por defecto, `simular.py#L18`).
   - **Evaluación**: [HECHO] No existe término de arrastre aerodinámico ($F_D = -\frac{1}{2}\rho C_D S \|v\| v$), sustentación aerodinámica ($F_L$), momento de toma de aire (*ram drag*) ni interacción aerodinámica entre chorros.

2. **Dinámica de Rotación (Ecuaciones de Euler para cuerpo rígido)**:
   - **Líneas de código**: `simular.py#L9`, `L11`:
     ```python
     torque = (A @ F.ravel())[3:] + et
     ...
     return np.r_[y[3:6], acc, qdot, (torque - np.cross(om, I * om)) / I]
     ```
   - **Ecuación matemática**:
     $$I \dot{\omega} + \omega \times (I \omega) = \tau \implies \dot{\omega} = I^{-1} \left( \tau - \omega \times (I \omega) \right)$$
   - **Detalle de términos**:
     - $I = \text{diag}(I_{xx}, I_{yy}, I_{zz})$ es un vector diagonal de momentos principales de inercia (`simular.py#L19`). La operación en código divide directamente por el vector $I$ (`/ I`), lo que asume rígidamente un tensor diagonal sin productos de inercia ($I_{xy} = I_{xz} = I_{yz} = 0$).
     - $\tau \in \mathbb{R}^3$ es el par resultante en el marco de cuerpo.
     - $\tau_{\text{ext}} = [0.03, 0.02, 0.01]^T \frac{m}{5} \text{scale}$ N·m durante $12 \le t < 13$ s; $0$ en otro caso (`simular.py#L46`).
   - **Evaluación**: [HECHO] No se incluyen los pares de reacción aerodinámica de los rotores ($Q_{\text{rotor}}$) ni los pares giroscópicos inducidos por los rotores en rotación ($I_{\text{prop}} \omega \times \Omega_{\text{rotor}} = 0$).

3. **Cinemática de Actitud por Cuaterniones**:
   - **Líneas de código**: `simular.py#L8`, `L10`, `L16`:
     ```python
     q = y[6:10]; q = q / np.linalg.norm(q); om = y[10:13]; rot = R.from_quat(q)
     qdot = .5 * np.r_[q[3] * om + np.cross(q[:3], om), -np.dot(q[:3], om)]
     ...
     y[6:10] /= np.linalg.norm(y[6:10]); return y
     ```
   - **Ecuación matemática**:
     Con $q = [q_v^T, q_w]^T = [q_x, q_y, q_z, q_w]^T$:
     $$\dot{q}_v = \frac{1}{2} \left( q_w \omega + q_v \times \omega \right)$$
     $$\dot{q}_w = -\frac{1}{2} (q_v \cdot \omega)$$
   - **Evaluación**: [HECHO] La convención de SciPy coloca la parte vectorial en las primeras tres componentes y la parte escalar en la cuarta. La ecuación implementa correctamente la cinemática para $\omega$ en el marco del cuerpo. Se normaliza el cuaternión al evaluar las derivadas y al finalizar el paso RK4.

4. **Matriz de Asignación Geométrica ($A$) y Brazos de Palanca**:
   - **Líneas de código**: `simular.py#L20-L24`:
     ```python
     xy = np.array([[-.2, -.076], [-.2, .076], [.2, -.076], [.2, .076]]) * scale
     A = np.zeros((6, 12))
     for i, (x, y) in enumerate(xy):
         A[:3, 3*i:3*i+3] = np.eye(3)
         A[3:, 3*i:3*i+3] = np.array([[0, .021*scale, y], [-.039*scale, 0, -x], [-y, x, 0]])
     ```
   - **Ecuación matemática**:
     $$\begin{bmatrix} F_{\text{net}} \\ \tau_{\text{net}} \end{bmatrix} = A \begin{bmatrix} F_0 \\ F_1 \\ F_2 \\ F_3 \end{bmatrix}, \quad A \in \mathbb{R}^{6 \times 12}$$
     Para el módulo $i$ en posición $[x_i, y_i]^T$:
     $$\begin{bmatrix} F_{x,\text{net}} \\ F_{y,\text{net}} \\ F_{z,\text{net}} \end{bmatrix} = \sum_{i=0}^3 \begin{bmatrix} F_{i,x} \\ F_{i,y} \\ F_{i,z} \end{bmatrix}$$
     $$\begin{bmatrix} \tau_{x,i} \\ \tau_{y,i} \\ \tau_{z,i} \end{bmatrix} = \begin{bmatrix} 0.021 \cdot \text{scale} \cdot F_{i,y} + y_i F_{i,z} \\ -0.039 \cdot \text{scale} \cdot F_{i,x} - x_i F_{i,z} \\ x_i F_{i,y} - y_i F_{i,x} \end{bmatrix}$$
   - **Evaluación**: [HECHO / HIPÓTESIS]
     - El producto cruz clásico $r \times F$ es $[r_y F_z - r_z F_y, r_z F_x - r_x F_z, r_x F_y - r_y F_x]^T$.
     - Al comparar con el código, se deduce que se asumen brazos axiales verticales "virtuales":
       $$-r_{z,y} = 0.021 \cdot \text{scale} \implies r_{z,y} = -0.021 \cdot \text{scale} \text{ m (para } F_y)$$
       $$r_{z,x} = -0.039 \cdot \text{scale} \implies r_{z,x} = -0.039 \cdot \text{scale} \text{ m (para } F_x)$$
     - Estos brazos en $Z$ difieren entre los ejes $X$ e $Y$ para un mismo conducto físico. El propio `INFORME.md#L18` declara que son "brazos efectivos HIPOTÉTICOS... no centros de presión verificados".

### 2.2 Convenciones de Marcos de Referencia y Discrepancias
- **Marco Inercial (Mundo)**: $Z$ apunta verticalmente hacia arriba; vector gravitatorio $g_{\text{world}} = [0, 0, -9.80665]^T$ m/s². Ejes $X, Y$ definen el plano horizontal.
- **Marco del Cuerpo (Simulador)**: Origen en el CG $(0,0,0)$; $+Z$ hacia arriba (empuje de sustentación positivo $F_z > 0$); $+X$ longitudinal hacia adelante; $+Y$ lateral. La rotación `rot.apply(v_body)` transforma vectores de cuerpo a mundo, y `rot.inv().apply(v_world)` transforma de mundo a cuerpo (`simular.py#L50`).
- **Discrepancia Crítica frente a CAD (`C02_CANDIDATA.json`)**:
  - En `C02_CANDIDATA.json#L13-L41`, el marco CAD sitúa la nariz en $X$ negativo, requiriendo la transformación formal:
    $$R_{\text{flight\_from\_CAD}} = \begin{bmatrix} -1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
  - En `C02_CANDIDATA.json#L86-L103`, las posiciones de los 4 ventiladores están expresadas respecto al datum CAD como:
    $$x = \pm 0.160 \text{ m}, \quad y = \pm 0.076 \text{ m}$$
    indicando explícitamente: `"centres_frame": "CAD datum, not physical CG frame"`.
  - En `simular.py#L20`, la simulación ubica los ventiladores en:
    $$x = \pm 0.200 \cdot \text{scale} \text{ m}, \quad y = \pm 0.076 \cdot \text{scale} \text{ m}$$
  - **Dictamen**: [HECHO] Existe una discrepancia de $40$ mm por semieje longitudinal ($0.200$ m vs $0.160$ m a escala 1:1), lo que sobreestima la autoridad de momento en cabeceo en un $+25\%$ ($0.200 / 0.160 = 1.25$). Además, `simular.py` no aplica la transformación $R_{\text{flight\_from\_CAD}}$ ni corrige la posición del datum respecto a un CG real.

### 2.3 Esquema de Integración Numérica
- **Algoritmo**: Runge-Kutta explícito clásico de 4º orden (RK4) implementado en `simular.py#L13-L16`:
  $$k_1 = f(y_n)$$
  $$k_2 = f\left(y_n + \frac{\Delta t}{2} k_1\right)$$
  $$k_3 = f\left(y_n + \frac{\Delta t}{2} k_2\right)$$
  $$k_4 = f(y_n + \Delta t k_3)$$
  $$y_{n+1} = y_n + \frac{\Delta t}{6} (k_1 + 2 k_2 + 2 k_3 + k_4)$$
- **Paso temporal**: $\Delta t = 0.005$ s ($200$ Hz) para el escenario nominal de 24 s ($4800$ pasos de integración, `simular.py#L18`, `L43`).
- **Acoplamiento de Actuadores**: [HECHO] Las fuerzas $F$, la perturbación exterior `ext` y el momento exterior `et` se evalúan fuera del paso RK4 y se mantienen estrictamente constantes durante las 4 etapas intermedias de evaluación de la derivada (`def f(y): return rigid_rhs(y, F, A, I, mass, ext, et)` en `simular.py#L14`). Esto introduce un comportamiento de muestreo y retención de orden cero (Zero-Order Hold) a nivel de la subetapa de integración.
- **Normalización**: Se re-normaliza el cuaternión tras la combinación lineal de etapas: `y[6:10] /= np.linalg.norm(y[6:10])` (`simular.py#L16`).

### 2.4 Control, Saturación y Asignación de Esfuerzos
- **Frecuencia de Control**: Ejecutado cada 4 pasos de integración ($\Delta t_{\text{ctrl}} = 0.02$ s, es decir, a $50$ Hz, `stride = round(.02/dt) = 4` en `simular.py#L43`, `L47`).
- **Lazo Externo (Posición - PD)**:
  - Línea: `simular.py#L48`:
    $$a_c = 3 (r_{\text{ref}}(t) - r) - 3 v \quad (K_{p,\text{pos}} = 3.0 \text{ s}^{-2}, K_{d,\text{pos}} = 3.0 \text{ s}^{-1})$$
  - **Saturación de aceleración adicional solicitada**: Línea `simular.py#L49`:
    $$\text{si } \|a_c\| > 0.5 g \implies a_c \leftarrow 0.5 g \frac{a_c}{\|a_c\|} \quad (0.5 g = 4.903325 \text{ m/s}^2)$$
  - **Conversión a Fuerza en Marco de Cuerpo**: Línea `simular.py#L50`:
    $$F_{\text{des}} = R(q)^{-1} \left[ m \left( a_c + \begin{bmatrix} 0 \\ 0 \\ g \end{bmatrix} \right) \right]$$
- **Lazo Interno (Actitud - PD)**:
  - Línea: `simular.py#L51`:
    $$\Phi_{\text{err}} = \text{rot.as\_rotvec}() \quad (\text{referencia implícita de actitud horizontal } R_{\text{ref}} = I)$$
    $$\alpha = -8 \Phi_{\text{err}} - 5 \omega \quad (K_{p,\text{att}} = 8.0 \text{ s}^{-2}, K_{d,\text{att}} = 5.0 \text{ s}^{-1})$$
    $$\tau_{\text{des}} = I \alpha + \omega \times (I \omega)$$
  - **Saturación de torque**: Línea `simular.py#L51`:
    Recorte escalar por componente (box clip):
    $$\tau_{\text{des}, k} = \text{clip}\left(\tau_{\text{des}, k}, -0.4 \frac{m}{5} \text{scale}, +0.4 \frac{m}{5} \text{scale}\right) \text{ N}\cdot\text{m}$$
    A 5 kg ($\text{scale} = 1.0$), el límite es $[-0.4, +0.4]$ N·m en cada eje.
- **Asignación por Optimización (SLSQP)**:
  - Vector de optimización: $v = [F_0^T, F_1^T, F_2^T, F_3^T]^T \in \mathbb{R}^{12}$ (`simular.py#L52-L58`).
  - Ponderación: $W = [1/m, 1/m, 1/m, 4/(m/5)^{4/3}, 4/(m/5)^{4/3}, 4/(m/5)^{4/3}]^T$, $H = W[:, \text{None}] \odot A$, $b = W \odot [F_{\text{des}}^T, \tau_{\text{des}}^T]^T$.
  - Función objetivo cuadrática regularizada:
    $$J(v) = \frac{1}{2} \| H v - b \|_2^2 + \frac{1}{2} \times 10^{-5} \| v - v_{\text{anchor}} \|_2^2$$
    donde $v_{\text{anchor}}$ es el comando del paso anterior (`previous.ravel().copy()`).
  - Cotas de caja sobre variables:
    $$F_{i,x} \in [-T, T], \quad F_{i,y} \in [-T, T], \quad F_{i,z} \in [m/5, T]$$
    donde $T = 21 \frac{m}{5} \times \text{capacity}$ N, y la cota inferior en $Z$ es $m/5 = 1.0$ N a 5 kg.
  - Restricciones no lineales de desigualdad:
    1. Límite de norma de empuje total por módulo (4 desigualdades):
       $$c_{1..4}(v) = T^2 - (F_{i,x}^2 + F_{i,y}^2 + F_{i,z}^2) \ge 0$$
    2. Límite de semicono de deflexión efectiva de chorro (4 desigualdades):
       $$c_{5..8}(v) = (\tan(35^\circ) F_{i,z})^2 - (F_{i,x}^2 + F_{i,y}^2) \ge 0$$
  - Configuración del optimizador: SLSQP con tolerancia `ftol = 1e-9`, máximo 100 iteraciones, suministrando gradiente y Jacobiano exactos (`simular.py#L37-L41`, `L55`).

### 2.5 Dinámica y Saturación de Actuadores
- **Líneas de código**: `simular.py#L25`, `L62`:
  ```python
  T = 21 * mass / 5 * capacity; cone = np.tan(np.deg2rad(35)); rate = 50 * mass / 5; tau = .08
  ...
  df = (command - f) * (1 - np.exp(-dt / tau))
  dn = np.linalg.norm(df, axis=1)
  df *= np.minimum(1, rate * dt / np.maximum(dn, 1e-12))[:, None]
  f = f + df
  ```
- **Formulación matemática**:
  - Filtro pasabajas de primer orden con paso temporal $\Delta t$:
    $$\Delta F_{\text{lineal}} = (F_{\text{cmd}} - F) \left( 1 - e^{-\Delta t / \tau} \right), \quad \tau = 0.08 \text{ s}$$
  - Saturación de tasa vectorial de fuerza:
    $$\text{si } \|\Delta F_{\text{lineal}, i}\| > \text{rate} \cdot \Delta t \implies \Delta F_i = \Delta F_{\text{lineal}, i} \frac{\text{rate} \cdot \Delta t}{\|\Delta F_{\text{lineal}, i}\|}$$
    donde $\text{rate} = 50 \frac{m}{5}$ N/s.
  - Estado del actuador actualizado: $F \leftarrow F + \Delta F$.

### 2.6 Tabla Resumen de Supuestos Físicos vs Implementación en Código

| Parámetro / Efecto | Supuesto en `simular.py` | Implementación en Código (Ruta/Línea) | Estado Real en `C02_CANDIDATA.json` |
|---|---|---|---|
| **Masa total** | Escalar fijo ($2, 5, 10$ kg) | `simular.py#L18` | `actual_mass_kg: null` (`L121`), `mass_targets_are_actual_masses: false` (`L62`) |
| **Centro de Gravedad (CG)** | Idénticamente $(0, 0, 0)$ m | `simular.py#L9`, `L19` | `actual_CG_m: null` (`L122`) |
| **Tensor de Inercia** | Diagonal elipsoide homogéneo: $(0.0353, 0.4590, 0.4755)$ kg·m² | `simular.py#L19` ($I \propto m^{5/3}$) | `actual_inertia_kgm2: null` (`L123`) |
| **Posición ventiladores en X** | $x = \pm 0.200 \cdot \text{scale}$ m | `simular.py#L20` | $x = \pm 0.160$ m datum CAD (`L86-L103`) |
| **Brazos axiales en Z** | $z_x = -0.039$ m, $z_y = -0.021$ m | `simular.py#L24` | Sin verificar; `effective_jet_cone_deg: null` (`L132`) |
| **Aerodinámica de avance** | Inexistente ($C_D = 0, C_L = 0$) | `simular.py#L9` (no hay términos de velocidad relativa) | Entorno de referencia $\rho = 1.225$ kg/m³ (`L43`), pero sin modelo instalado |
| **Par reactivo y giroscópico** | Omitidos ($Q = 0, M_{\text{gyro}} = 0$) | `simular.py#L9`, `L11` | 4 rotores (CCW, CW, CW, CCW, `L113-L118`), pero sin mapas instalados |
| **Deflexión máxima de chorro** | Cono ideal simétrico $35^\circ$ | `simular.py#L25`, `L36` | Rango mecánico de álabes $[-45^\circ, +45^\circ]$ (`L127-L130`), cono efectivo nulo |
| **Sensores y Estado** | Observación perfecta instantánea | `simular.py#L45`, `L48` | Sin modelo de ruido, bias, retardo ni filtro de Kalman |
| **Perturbación externa** | Escalón sintético 1 s ($3, -2, 0$ N) | `simular.py#L46` | Sin modelo de turbulencia continua ni ráfagas normalizadas |

---

## 3. AUDITORÍA LÍNEA POR LÍNEA DEL SCRIPT DE VERIFICACIÓN (`verificar.py`)

### 3.1 Análisis de los Casos de Prueba Implementados
El archivo `verificar.py` (18 líneas) contiene dos bloques principales de comprobación:

1. **Casos Analíticos Desacoplados (1000 pasos a $\Delta t = 0.001$ s, $T = 1.0$ s)**:
   - **Caso `caida_libre`** (`verificar.py#L6`, `L9`):
     - Fuerzas $F = 0$, perturbaciones $0$.
     - Solución analítica evaluada: $z(1) = z_0 - \frac{1}{2} g t^2 = 10 - \frac{9.80665}{2} = 5.096675$ m; $v_z(1) = -g t = -9.80665$ m/s.
     - Error: $\max(|z - (10 - g/2)|, |v_z + g|) < 10^{-9}$ (`verificar.py#L12`).
   - **Caso `estacionario`** (`verificar.py#L6`, `L10`):
     - Aplica fuerza vertical $F_{0,z} = 5 g$ únicamente en el actuador 0 para equilibrar el peso ($m=5$ kg).
     - **Hallazgo Crítico**: En la línea 3 (`verificar.py#L3`), el script define:
       ```python
       A = np.zeros((6, 12)); A[:3, :3] = np.eye(3); I = np.array([.1, .2, .3]); F = np.zeros((4, 3))
       ```
       [HECHO] El script **anula intencionalmente las filas 3 a 5 de la matriz de asignación $A$**, eliminando todos los brazos de palanca ($A[3:, :] = 0$). De este modo, aplicar $5 g$ exclusivamente en el ventilador 0 no genera ningún momento de cabeceo o alabeo. La prueba no evalúa la matriz geométrica real del vehículo ni el acoplamiento momento-fuerza.
   - **Caso `par_constante`** (`verificar.py#L7`, `L11`):
     - Aplica un par externo en $Z$: $\tau_z = 0.03$ N·m con $I_{zz} = 0.3$ kg·m² y fuerza equilibrada $F_{0,z} = 5 g$.
     - Aceleración angular teórica: $\dot{\omega}_z = \tau_z / I_{zz} = 0.03 / 0.3 = 0.1$ rad/s².
     - Valores evaluados a $t = 1.0$ s: $\omega_z(1) = 0.1$ rad/s; ángulo $\theta_z(1) = \frac{1}{2} \dot{\omega}_z t^2 = 0.05$ rad ($2.86^\circ$).
     - Comprueba: $\max(|\omega_z - 0.1|, |\text{rotvec}_z - 0.05|) < 10^{-9}$ (`verificar.py#L12`).
     - **Hallazgo Crítico**: [HECHO] La rotación se restringe exclusivamente al eje principal $Z$ ($\omega = [0, 0, \omega_z]^T$). El término no lineal giroscópico $\omega \times (I \omega)$ se anula de forma trivial ($[0, 0, \omega_z] \times [0, 0, I_{zz}\omega_z] = 0$). La prueba **no verifica el acoplamiento cruzado de Euler en 3D**.

2. **Comprobación de Medio Paso (Convergencia Numérica Temporal)** (`verificar.py#L13-L16`):
   - Ejecuta `run(5, dt=0.0025, save=False)` y submuestrea cada dos pasos (`fine = h[::2]`).
   - Compara contra una ejecución nominal base:
     ```python
     baseline = np.load(P / '5kg_nominal.npz')['history']
     ```
   - Evalúa diferencias máximas de posición y actitud, exigiendo que la diferencia de posición sea $< 0.02$ m (`verificar.py#L16`).

### 3.2 Deficiencias Operacionales y Bloqueos de Ejecución
- **Falta del archivo baseline**: [HECHO] En `entradas/` **no existe el archivo `5kg_nominal.npz`** (únicamente están `INFORME.md`, `simular.py`, `verificar.py` y `C02_CANDIDATA.json`). La ejecución directa de `verificar.py` de forma aislada se aborta con `FileNotFoundError: 5kg_nominal.npz`.
- **Conflicto de permisos en el directorio de entrada**: [HECHO] Tanto `simular.py#L68-L69, L77` como `verificar.py#L18` (`(P / 'VERIFICACION.json').write_text(...)`) intentan escribir directamente en la ruta del archivo `P` (`entradas/...`). Dado que el directorio de entrada es de solo lectura (`-r--r--r--`), cualquier ejecución no modificada genera una denegación de permisos (`PermissionError`).
- **Alcance declarado**: El propio script admite en su línea 17:
  `'Numerical checks only, not physical validation or full NASA check-case suite.'`
  No valida la asignación SLSQP, ni los límites de saturación, ni la dinámica de actuadores, ni la estabilidad del sistema físico.

---

## 4. LAS MÁXIMO CINCO PRUEBAS FALTANTES PRIORIZADAS

Conforme a las directrices de verificación de simuladores 6DOF (NASA/TM-2015-218675) y teoría de dinámica de vuelo, se definen y priorizan las cinco pruebas faltantes esenciales:

### Prioridad 1: Verificación de Acoplamiento Dinámico 3D y Término Giroscópico No Lineal (Caso Dzhanibekov / Eje Intermedio / Conservación de Invariantes)
- **Categoría**: Verificación del resolvedor dinámico cuerpo rígido (NASA 6DOF Dynamics Check-Case).
- **Deficiencia que mitiga**: `verificar.py` únicamente prueba aceleración sobre un eje principal, donde $\omega \times (I \omega) \equiv 0$. En un vuelo real con perturbaciones, el vehículo experimenta rotación simultánea en los tres ejes. Además, `rigid_rhs` asume un tensor diagonal sin verificar productos de inercia ($I_{xy}, I_{xz}, I_{yz}$).
- **Objetivo**: Verificar que el resolvedor de integración numérica conserve rigurosamente las invariantes fundamentales de la mecánica clásica en rotación libre de pares exteriores:
  1. Conservación de la energía cinética rotacional: $T_{\text{rot}} = \frac{1}{2} \omega^T I \omega = \text{const}$.
  2. Conservación de la norma del vector momento angular inercial: $\|H_{\text{inertial}}\| = \|R(q) I \omega\| = \text{const}$.
- **Configuración**: $F = 0$, $\tau = 0$, $g = 0$, tensor de inercia asimétrico triaxial ($I_{xx} \ne I_{yy} \ne I_{zz}$), condición inicial multiaxial con energía desbalanceada (e.g., $\omega_0 = [0.2, 5.0, 0.2]$ rad/s) integrada durante 100 s.

### Prioridad 2: Consistencia Cinemática Global y Maniobras de Gran Ángulo (Conservación de Ortogonalidad y Continuidad en $360^\circ$)
- **Categoría**: Verificación de cinemática de actitud (NASA Attitude Kinematics Check-Case).
- **Deficiencia que mitiga**: Las pruebas analíticas actuales solo evalúan $0.05$ rad ($2.86^\circ$). No evalúan rotaciones completas de $360^\circ$, inversiones de actitud acrobática, ni la doble cobertura del espacio de cuaterniones ($q \equiv -q$). El cálculo del error de rotación en `simular.py#L51` (`rot.as_rotvec()`) presenta discontinuidades topológicas en $\pm \pi$.
- **Objetivo**: Evaluar la cinemática integrando perfiles angulares cónicos de precesión pura cerrados con solución analítica exacta:
  $$\omega(t) = \begin{bmatrix} \Omega_0 \sin(\theta) \cos(\omega_p t) \\ \Omega_0 \sin(\theta) \sin(\omega_p t) \\ \Omega_0 \cos(\theta) \end{bmatrix}$$
- **Configuración**: Giros completos continuos sobre múltiples ejes a altas tasas angulares ($180^\circ$/s), evaluando la deriva de normalización pre-filtro y el error de cierre tras $N$ revoluciones completas.

### Prioridad 3: Robustez de la Asignación SLSQP ante Inviabilidad, Saturación Simultánea y Contingencia (Fallback)
- **Categoría**: Verificación del sistema de guiado, navegación y control (Control Allocation Failure & Saturation).
- **Deficiencia que mitiga**: A 5 kg, el módulo nominal alcanza una deflexión de $34.920^\circ$, a solo $0.08^\circ$ del límite de $35.0^\circ$. En `simular.py#L56-L57`, si el optimizador no converge (`optfail += 1`) o la restricción se viola (`bad += 1`), el código ignora el fallo y entrega la solución numérica al sistema. En vuelo real esto induce divergencia inmediata.
- **Objetivo**: Someter el asignador SLSQP a demandas inalcanzables (aceleraciones horizontales $> 0.5 g$, momentos combinados que excedan la capacidad física instalada de los 4 ventiladores) y verificar la existencia de un mecanismo de contingencia (*fallback* o degradación admisible) que priorice el equilibrio de momentos sobre las fuerzas de traslación.

### Prioridad 4: Análisis de Sensibilidad y Estabilidad ante Desplazamiento del Centro de Gravedad (CG Offset) e Incertidumbre de Inercia
- **Categoría**: Verificación de robustez paramétrica y masa (Mass Properties Robustness).
- **Deficiencia que mitiga**: `simular.py` asume rígidamente CG en $(0, 0, 0)$. En `C02_CANDIDATA.json`, los ventiladores están referenciados al datum CAD ($x = \pm 0.160$ m) y el CG real es desconocido (`null`). Cualquier desplazamiento del CG respecto a la simetría de empuje genera un momento constante por peso propio que consume autoridad de control.
- **Objetivo**: Evaluar la estabilidad en lazo cerrado y el consumo de margen de deflexión mediante un barrido tridimensional del CG: $\Delta x_{\text{CG}} \in [-20, +20]$ mm, $\Delta y_{\text{CG}} \in [-10, +10]$ mm, $\Delta z_{\text{CG}} \in [-30, +30]$ mm, y dispersión de masa de $\pm 20\%$. Identificar el límite de estabilidad estática antes de saturar los actuadores en estacionario.

### Prioridad 5: Respuesta Dinámica ante Flujo de Avance, Momento Inducido en Conductos y Viento Cruzado Continuo
- **Categoría**: Verificación de aerodinámica acoplada y entorno atmosférico (Aero-propulsive Crosswind Check-Case).
- **Deficiencia que mitiga**: El simulador asume resistencia nula ($C_D = 0$). A velocidades de $3.27$ m/s, un conducto propulsivo genera arrastre de flujo incidente (*ram drag*) y un momento desestabilizante de cabeceo en la embocadura (*inlet lip pitching moment*). La perturbación actual de 1 s es puramente heurística y carece de base física.
- **Objetivo**: Incorporar un modelo de arrastre de avance y sustentación aerodinámica representativo del fuselaje, acoplado a un campo de viento con ráfagas normalizadas discretas (perfil de ráfaga 1-coseno según estándar militar MIL-F-8785C) de hasta $5$ m/s, verificando el ángulo de inclinación requerido para mantener posición y la no saturación de los ventiladores.

---

## 5. MÍNIMA INTERFAZ NECESARIA PARA SUSTITUIR PLANTA HIPOTÉTICA POR MAPAS INSTALADOS CON MASA Y CG

Para transicionar de la planta hipotética a una planta física identificada, la simulación debe desacoplarse del resolvedor ideal y conectarse mediante una interfaz estandarizada con unidades canónicas SI.

```
       +-------------------------------------------------------------+
       |             ESTADO CINEMÁTICO Y ATMOSFÉRICO                 |
       |  r (m), v (m/s), q (cuat), omega (rad/s), rho, v_wind (m/s) |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |             PROPIEDADES DE MASA E INERCIA REALES            |
       |  m_total (kg), r_CG/CAD (m), I_CG (3x3 kg*m^2)             |
       |  Brazos de palanca: r_i/CG = r_fan_i/CAD - r_CG/CAD         |
       +-------------------------------------------------------------+
                                      |
                   +------------------+------------------+
                   |                                     |
                   v                                     v
+-------------------------------------+ +-------------------------------------+
|      MAPAS INSTALADOS PROPULSIÓN    | |     MAPA AERODINÁMICO DE CÉLULA     |
| Entradas: Omega_cmd, delta_cmd      | | Entradas: v_rel, omega, rho, alpha  |
| - Dinámica de rotor (tau_rpm)       | | - Fuerzas: F_aero (N)               |
| - Servos álabes (+-45 deg, dot_max) | | - Momentos: M_aero (N*m)            |
| - Empuje instalado: F_i (N)         | |                                     |
| - Par reactivo conducto: M_aero_i   | |                                     |
| - Par giroscópico rotor: M_gyro_i   | |                                     |
| - Potencia consumida: P_elec (W)    | |                                     |
+-------------------------------------+ +-------------------------------------+
                   |                                     |
                   +------------------+------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |             CIERRE DINÁMICO DE FUERZAS Y MOMENTOS           |
       | F_net = sum(F_i) + F_aero                                   |
       | tau_net = sum(r_i/CG x F_i + M_aero_i + M_gyro_i) + M_aero  |
       | a_iner = (R(q) * F_net) / m - [0, 0, g]^T                   |
       | dot_omega = I_CG^-1 * (tau_net - omega x (I_CG * omega))    |
       +-------------------------------------------------------------+
```

### 5.1 Estructura Formal de la Interfaz Técnica (Unidades SI Canónicas)

#### 1. Datos de Propiedades de Masa e Inercia Instaladas (`InstalledMassProperties`)
- `mass_total_kg` [float]: Masa total real del vehículo en kg (fuente: pesaje o modelo CAD consolidado).
- `cg_cad_m` [vector 3 float]: Coordenadas $[x_{\text{cg}}, y_{\text{cg}}, z_{\text{cg}}]^T$ en metros con respecto al datum CAD (marco `CAD_longitudinal_nose_at_negative_x`).
- `cg_flight_flu_m` [vector 3 float]: Coordenadas del CG transformadas al marco FLU:
  $$r_{\text{cg, FLU}} = R_{\text{flight\_from\_CAD}} \cdot r_{\text{cg, CAD}}$$
- `inertia_tensor_cg_kgm2` [matriz 3x3 simétrica]: Tensor de inercia real calculado o medido en el marco de vuelo FLU alrededor del CG real:
  $$I_{\text{CG}} = \begin{bmatrix} I_{xx} & -I_{xy} & -I_{xz} \\ -I_{xy} & I_{yy} & -I_{yz} \\ -I_{xz} & -I_{yz} & I_{zz} \end{bmatrix} \text{ kg}\cdot\text{m}^2$$
- `fan_centres_cad_m` [array 4x3 float]: Posiciones de los centros de los conductos en el datum CAD (según `C02_CANDIDATA.json#L86-L103`: $[-0.16, -0.076, z_0]$, $[-0.16, 0.076, z_0]$, $[0.16, -0.076, z_0]$, $[0.16, 0.076, z_0]$).
- **Cálculo dinámico de brazos de palanca**:
  $$r_{i/\text{CG, FLU}} = \left( R_{\text{flight\_from\_CAD}} \cdot r_{\text{fan}, i/\text{CAD}} \right) - r_{\text{cg, FLU}}$$

#### 2. Vector de Comandos Físicos de Actuación (`ActuatorCommands`)
Para cada módulo propulsivo $i \in \{0, 1, 2, 3\}$:
- `rotor_speed_cmd_rad_s` [float]: Velocidad angular comandada del rotor $\Omega_{\text{cmd}, i}$ en rad/s (o RPM).
- `vane_angle_x_cmd_rad` [float]: Ángulo mecánico del álabe longitudinal $\delta_{x,\text{cmd}, i}$, con cota física $[-45^\circ, +45^\circ]$ ($\approx [-0.7854, +0.7854]$ rad) según `C02_CANDIDATA.json#L128-L130`.
- `vane_angle_y_cmd_rad` [float]: Ángulo mecánico del álabe lateral $\delta_{y,\text{cmd}, i}$, con cota física $[-45^\circ, +45^\circ]$.

#### 3. Modelo Dinámico de Actuadores y Servomotores (`ActuatorDynamics`)
- Dinámica del motor/ESC:
  $$\dot{\Omega}_i = \frac{1}{\tau_{\text{motor}}} (\Omega_{\text{cmd}, i} - \Omega_i), \quad \text{con } 0 \le \Omega_i \le \Omega_{\max}$$
- Dinámica de los servomotores de deflexión de álabes:
  $$\dot{\delta}_k = \text{clip}\left(\frac{1}{\tau_{\text{servo}}} (\delta_{k,\text{cmd}} - \delta_k), -\dot{\delta}_{\max}, +\dot{\delta}_{\max}\right)$$

#### 4. Mapas Instalados de Propulsión (`InstalledPropulsionMap`)
Función calibrada experimentalmente en banco de ensayos o CFD validado para cada módulo $i$:
- Fuerza vectorial en marco cuerpo:
  $$F_{i,\text{body}} = f_{\text{thrust}}\left(\Omega_i, \delta_{x,i}, \delta_{y,i}, v_{\text{local}, i}, \rho, p_\infty, T_\infty\right) \in \mathbb{R}^3 \text{ [N]}$$
- Momento aerodinámico/reactivo del conducto:
  $$M_{\text{aero}, i} = f_{\text{duct\_torque}}\left(\Omega_i, \delta_{x,i}, \delta_{y,i}, v_{\text{local}, i}, \rho\right) \in \mathbb{R}^3 \text{ [N}\cdot\text{m]}$$
- Par giroscópico del rotor (incorporando el sentido de rotación de `C02_CANDIDATA.json#L113-L118`):
  $$M_{\text{gyro}, i} = I_{\text{rotor}} \left( \omega \times \begin{bmatrix} 0 \\ 0 \\ \sigma_i \Omega_i \end{bmatrix} \right), \quad \sigma = [+1, -1, -1, +1] \text{ para [CCW, CW, CW, CCW]}$$
- Potencia eléctrica consumida:
  $$P_{\text{elec}, i} = f_{\text{power}}(\Omega_i, \delta_i, v_{\text{local}, i}) \text{ [W]}$$

#### 5. Mapa Aerodinámico de Célula (`InstalledAeroMap`)
Modelo aerodinámico global del fuselaje con aletas y tapas:
- Velocidad relativa del aire: $v_\infty = v_{\text{body}} - R(q)^{-1} v_{\text{wind, world}}$.
- Fuerza aerodinámica neta:
  $$F_{\text{aero, body}} = \frac{1}{2} \rho \|v_\infty\|^2 S_{\text{ref}} \begin{bmatrix} C_X(\alpha, \beta, \omega) \\ C_Y(\alpha, \beta, \omega) \\ C_Z(\alpha, \beta, \omega) \end{bmatrix} \text{ [N]}$$
- Momento aerodinámico neto respecto al CG real:
  $$M_{\text{aero, body}} = \frac{1}{2} \rho \|v_\infty\|^2 S_{\text{ref}} \begin{bmatrix} b \cdot C_l(\alpha, \beta, \omega) \\ c \cdot C_m(\alpha, \beta, \omega) \\ b \cdot C_n(\alpha, \beta, \omega) \end{bmatrix} \text{ [N}\cdot\text{m]}$$

#### 6. Ecuaciones Integradas de Síntesis Dinámica
- Fuerza neta en marco inercial:
  $$\ddot{r} = \frac{1}{m_{\text{total}}} R(q) \left( \sum_{i=0}^3 F_{i,\text{body}} + F_{\text{aero, body}} \right) - \begin{bmatrix} 0 \\ 0 \\ g \end{bmatrix}$$
- Momento neto total en marco cuerpo respecto al CG real:
  $$\tau_{\text{net}} = \sum_{i=0}^3 \left( r_{i/\text{CG, FLU}} \times F_{i,\text{body}} + M_{\text{aero}, i} + M_{\text{gyro}, i} \right) + M_{\text{aero, body}}$$
- Aceleración angular en marco cuerpo (utilizando el tensor $3 \times 3$ completo):
  $$\dot{\omega} = I_{\text{CG}}^{-1} \left( \tau_{\text{net}} - \omega \times (I_{\text{CG}} \omega) \right)$$

---

## 6. TESTS CONCEPTUALES DETALLADOS

A continuación se formulan los cinco tests conceptuales con rigor matemático, condiciones de entrada, observables y umbrales cuantitativos de aceptación:

### Test Conceptual 1: Conservación de Invariantes en Giro Libre Asimétrico 3D (Dzhanibekov / Euler)
- **Hipótesis bajo prueba**: El resolvedor numérico integra con precisión simpléctica/conservativa la dinámica rotacional no lineal libre de fuerzas y momentos exteriores con acoplamiento multiaxial no diagonal.
- **Ecuaciones de referencia**:
  $$\dot{\omega} = I^{-1} (-\omega \times (I \omega)), \quad \dot{q} = \frac{1}{2} q \otimes [\omega, 0]$$
  $$T_{\text{rot}}(t) = \frac{1}{2} \omega(t)^T I \omega(t) \equiv T_0$$
  $$H_{\text{inertial}}(t) = R(q(t)) I \omega(t) \equiv H_0$$
- **Condiciones de entrada**:
  - Masa $m = 5.0$ kg, $g = 0$, $F_i = 0$, $F_{\text{ext}} = 0$, $\tau_{\text{ext}} = 0$.
  - Tensor de inercia triaxial con productos de inercia:
    $$I = \begin{bmatrix} 0.04 & 0.002 & 0.001 \\ 0.002 & 0.45 & 0.005 \\ 0.001 & 0.005 & 0.48 \end{bmatrix} \text{ kg}\cdot\text{m}^2$$
  - Velocidad angular inicial: $\omega_0 = [0.5, 6.0, 0.5]^T$ rad/s.
  - Tiempo de simulación: $T_{\text{sim}} = 60.0$ s; $\Delta t = 0.002$ s.
- **Métricas evaluadas**:
  - Deriva relativa de energía: $\epsilon_E(t) = \frac{|T_{\text{rot}}(t) - T_{\text{rot}}(0)|}{T_{\text{rot}}(0)}$.
  - Deriva relativa de momento angular: $\epsilon_H(t) = \frac{\|H_{\text{inertial}}(t) - H_{\text{inertial}}(0)\|}{\|H_{\text{inertial}}(0)\|}$.
- **Criterio de aceptación (Pass/Fail)**:
  $$\max_{t \in [0, 60]} \epsilon_E(t) < 1.0 \times 10^{-6}, \quad \max_{t \in [0, 60]} \epsilon_H(t) < 1.0 \times 10^{-6}$$

### Test Conceptual 2: Invarianza Cinemática de Cuaterniones en Giros Cónicos de $360^\circ$ e Inversión Topológica
- **Hipótesis bajo prueba**: El integrador cinemático mantiene la ortogonalidad estricta de la matriz de actitud sin derivas numéricas de norma y procesa sin singularidad giros completos con inversión de signo de cuaternión ($q \to -q$).
- **Ecuaciones de referencia**:
  Trayectoria analítica de rotación cónica pura a velocidad angular constante $\omega_p = 2\pi / T_p$:
  $$\omega(t) = \begin{bmatrix} \omega_0 \sin(\theta) \cos(\omega_p t) \\ \omega_0 \sin(\theta) \sin(\omega_p t) \\ \omega_0 \cos(\theta) \end{bmatrix}, \quad q_{\text{analítico}}(t) = \exp_q\left(\int_0^t \frac{1}{2} \omega(\tau) d\tau\right)$$
- **Condiciones de entrada**:
  - Ángulo de cono $\theta = 45^\circ$, velocidad angular $\omega_0 = \pi$ rad/s ($180^\circ$/s), período $T_p = 4.0$ s.
  - Número de ciclos: 10 ciclos completos ($T = 40.0$ s); paso $\Delta t = 0.001$ s.
- **Métricas evaluadas**:
  - Deriva de norma antes de normalización: $\Delta n(t) = |\|q_{\text{pre-norm}}(t)\| - 1|$.
  - Distancia geodésica de actitud: $\Phi_{\text{err}}(t) = 2 \arccos(|q(t) \cdot q_{\text{analítico}}(t)|)$.
- **Criterio de aceptación (Pass/Fail)**:
  $$\max_t \Delta n(t) < 1.0 \times 10^{-8}, \quad \max_t \Phi_{\text{err}}(t) < 1.0 \times 10^{-5} \text{ rad}$$

### Test Conceptual 3: Prueba de Saturación Extrema del Asignador SLSQP y Degradación Admisible (Fallback)
- **Hipótesis bajo prueba**: Ante comandos de aceleración que sobrepasen el techo vectorial físico ($4 \times 21$ N a 5 kg) o el semicono ($35^\circ$), el optimizador no aborta ni viola restricciones, y el control prioriza el equilibrio de actitud sacrificando seguimiento de posición.
- **Condiciones de entrada**:
  - Demanda escalón de fuerza lateral desmedida: $a_{c,\text{cmd}} = [0, 2.5 g, 0]^T$ ($24.5$ m/s²), manteniendo demanda de par nulo $\tau_{\text{cmd}} = [0, 0, 0]^T$.
  - Duración del pulso: 2.0 s.
- **Métricas evaluadas**:
  - Violación de restricciones de empuje: $\max_i (\|F_i\| - T)$.
  - Violación de restricción de cono: $\max_i (\theta_{\text{cone}, i} - 35^\circ)$.
  - Tasa de éxito del optimizador y tiempo de cómputo por paso.
  - Error residual de momento: $\|\tau_{\text{real}} - \tau_{\text{cmd}}\|$.
- **Criterio de aceptación (Pass/Fail)**:
  - Cero violaciones de cotas: $\|F_i\| \le 21.0001$ N, $\theta_{\text{cone}, i} \le 35.0001^\circ$.
  - Tiempo de ejecución determinista $< 5$ ms por ciclo en CPU estándar.
  - Priorización de momento: $\|\tau_{\text{real}}\| < 0.05$ N·m (estabilidad angular garantizada durante la saturación de fuerza).

### Test Conceptual 4: Envolvente de Estabilidad Estática ante Desplazamiento Tridimensional de CG
- **Hipótesis bajo prueba**: La arquitectura de cuatro ventiladores vectorizados puede mantener el vuelo a punto fijo estacionario compensando el momento estático por desalineación de CG sin superar el 70% del ángulo de cono admisible ($24.5^\circ$).
- **Condiciones de entrada**:
  - Malla de desplazamiento de CG:
    $$\Delta x_{\text{CG}} \in \{-20, -10, 0, 10, 20\} \text{ mm}$$
    $$\Delta y_{\text{CG}} \in \{-15, 0, 15\} \text{ mm}$$
    $$\Delta z_{\text{CG}} \in \{-30, 0, 30\} \text{ mm}$$
  - Masa $m = 5.0$ kg; condición de vuelo estacionario a $z = 2.0$ m.
- **Métricas evaluadas**:
  - Ángulo de deflexión estacionario máximo por módulo: $\theta_{\max,\text{trim}} = \max_i \arctan\left(\frac{\sqrt{F_{x,i}^2 + F_{y,i}^2}}{F_{z,i}}\right)$.
  - Consumo de empuje nominal: $F_{\text{margin}} = 21.0 - \max_i \|F_i\|$.
- **Criterio de aceptación (Pass/Fail)**:
  - Para todo $\Delta x \le \pm 10$ mm y $\Delta y \le \pm 7.6$ mm:
    $$\theta_{\max,\text{trim}} \le 24.5^\circ \quad (70\% \text{ del semicono de } 35^\circ)$$
    $$F_{\text{margin}} \ge 5.0 \text{ N}$$

### Test Conceptual 5: Rechazo de Ráfaga de Viento Normalizada (Perfil 1-Coseno) con Modelo de Arrastre
- **Hipótesis bajo prueba**: El sistema en lazo cerrado rechaza una ráfaga de viento cruzado continuo manteniendo la desviación lateral acotada y sin inducir oscilaciones de control (PIO).
- **Ecuaciones de referencia**:
  Perfil de ráfaga normalizada MIL-F-8785C / FAA:
  $$v_{\text{wind}, y}(t) = \begin{cases} 0 & t < t_{\text{start}} \\ \frac{V_{\text{gust}}}{2} \left( 1 - \cos\left(\frac{2\pi (t - t_{\text{start}})}{T_{\text{gust}}}\right) \right) & t_{\text{start}} \le t \le t_{\text{start}} + T_{\text{gust}} \\ 0 & t > t_{\text{start}} + T_{\text{gust}} \end{cases}$$
  Fuerza de arrastre aerodinámico: $F_D = -\frac{1}{2} \rho C_D S \|v - v_{\text{wind}}\| (v - v_{\text{wind}})$ con $C_D S = 0.04$ m², $\rho = 1.225$ kg/m³.
- **Condiciones de entrada**:
  - $V_{\text{gust}} = 4.0$ m/s, $T_{\text{gust}} = 2.5$ s, $t_{\text{start}} = 5.0$ s.
- **Métricas evaluadas**:
  - Desviación máxima de posición lateral: $\Delta y_{\max} = \max_t |y(t) - y_{\text{ref}}|$.
  - Ángulo máximo de inclinación (roll): $\phi_{\max} = \max_t |\text{roll}(t)|$.
  - Tiempo de re-estabilización al 95% del valor de referencia: $t_{\text{settling}}$.
- **Criterio de aceptación (Pass/Fail)**:
  $$\Delta y_{\max} \le 0.35 \text{ m}, \quad \phi_{\max} \le 12.0^\circ, \quad t_{\text{settling}} \le 3.0 \text{ s tras fin de ráfaga}$$

---

## 7. LIMITACIONES Y ALCANCE DE LA AUDITORÍA

1. **Naturaleza Analítica y Documental**: Esta auditoría se ha efectuado mediante lectura rigurosa de código, inspección matricial y trazabilidad analítica de los archivos suministrados en `entradas/`. No se ha ejecutado código que altere o sobreescriba los ficheros de referencia ni se atribuye certificación de vuelo o validación física experimental.
2. **Ausencia de Archivos No Copiados**: Conforme a las instrucciones del usuario, no se infiere que archivos no copiados (tales como reportes de masa parcial o archivos STEP citados en `C02_CANDIDATA.json`) no existan en repositorios externos, ni que reservas volumétricas sin masa asignada tengan masa real nula o no nula.
3. **Inexistencia de Mapas Instalados en la Entrada**: La investigación aerodinámica global permanece no validada (`installed_map_available: false`, `predictive_flight_plant_accepted: false` en `C02_CANDIDATA.json`). Por consiguiente, cualquier extrapolación de estos resultados al vehículo físico constituiría una conjetura carente de sustento experimental.
