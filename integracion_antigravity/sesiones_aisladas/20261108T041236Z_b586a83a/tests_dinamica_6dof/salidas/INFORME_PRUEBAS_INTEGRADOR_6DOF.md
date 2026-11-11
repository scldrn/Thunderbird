# INFORME DE PRUEBAS INDEPENDIENTES DE BAJO COSTO PARA EL INTEGRADOR RÍGIDO 6DOF

**Ubicación de trabajo**: `/private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/tests_dinamica_6dof`  
**Directorio de referencia (solo lectura)**: `entradas/`  
**Directorio de entregables**: `salidas/`  
**Fecha de evaluación**: 2026-11-08  

---

## 1. RESUMEN EJECUTIVO Y DECLARACIÓN METODOLÓGICA FORMAL

En cumplimiento estricto de las directrices recibidas:
1. **Preservación del archivo original**: Se copió `entradas/investigacion-aeronautica/simulacion_vuelo_A/simular.py` a `salidas/simular.py` mediante `shutil.copyfile` sin alterar el original (el cual conserva sus permisos de solo lectura `-r--r--r--`).
2. **Dependencias del entorno y ejecución de pruebas**:
   - El entorno de ejecución en el sandbox dispone de Python 3.9.6 estándar, pero **carece de las bibliotecas `numpy` y `scipy`**.
   - Conforme a la instrucción mandataria (*"usa numpy/scipy solo si están disponibles y si no, declara explícitamente que no se ejecutaron y evita afirmar éxito"*), se ha implementado la suite `salidas/test_integrador_rigido.py` con detección automática de dependencias. Al no estar disponibles `numpy` y `scipy`, el script declara formalmente la no ejecución de las pruebas directas sobre `salidas/simular.py` y **se evita explícitamente afirmar éxito** sobre dicho módulo en este entorno.
   - Para verificar los fundamentos matemáticos y computacionales de los algoritmos de forma autónoma sin romper dicha regla epistémica, se desarrolló la suite `salidas/test_integrador_analitico_puro.py` en Python estándar (sin dependencias externas). Esta suite ejecuta y valida los tres casos de prueba canónicos requeridos sobre la formulación analítica exacta de cuerpo rígido 6DOF.
3. **No extrapolación a validación física**: Todos los ensayos constituyen comprobaciones numéricas y cinemáticas del resolvedor matemático. No representan validación física del vehículo, ni de la planta instalada, ni sustituyen una campaña experimental de túnel de viento o banco de ensayos.
4. **No ejecución de simulación completa**: No se ejecutó la rutina `run()` de `simular.py`, evitando sobreescrituras de artefactos de simulación o resultados globales.

---

## 2. CLASIFICACIÓN EPISTÉMICA DE DATOS

Conforme al principio de rigor científico, se discriminan formalmente las tres categorías de información:

### 2.1 Datos Medidos (0%)
- **Estado**: **Ninguno**. En el repositorio de entrada no existen datos experimentales medidos de empuje en banco, par aerodinámico, corriente eléctrica, consumo energético, ubicación física real del centro de gravedad ni tensor de inercia experimental ponderado.
- **Fuentes**: `C02_CANDIDATA.json#L119-L123` (`actual_mass_kg: null`, `actual_CG_m: null`, `actual_inertia_kgm2: null`).

### 2.2 Datos Supuestos (Hipótesis de Trabajo)
- **Masa supuesta nominal**: $m = 5.0$ kg (fuente: `simular.py#L18`). No se asume que reservas volumétricas sin masa asignada tengan masa nula o no nula.
- **Centro de gravedad (CG)**: Coincidente con el origen de coordenadas $[0, 0, 0]^T$ m (fuente: `simular.py#L9`, `L19`).
- **Tensor de inercia nominal ($I$)**: Diagonal puro, derivado analíticamente de un elipsoide macizo homogéneo de semiejes $[1.341, 0.321821, 0.194110]$ m:
  $$I_{xx} \approx 0.035314 \text{ kg}\cdot\text{m}^2, \quad I_{yy} \approx 0.458994 \text{ kg}\cdot\text{m}^2, \quad I_{zz} \approx 0.475459 \text{ kg}\cdot\text{m}^2$$
  (fuente: `simular.py#L19`). Se asumen productos de inercia nulos ($I_{xy} = I_{xz} = I_{yz} = 0$).
- **Ubicación de actuadores (marco cuerpo)**:
  Ventilador 0: $[-0.200, -0.076, 0.0]^T$ m  
  Ventilador 1: $[-0.200, +0.076, 0.0]^T$ m  
  Ventilador 2: $[+0.200, -0.076, 0.0]^T$ m  
  Ventilador 3: $[+0.200, +0.076, 0.0]^T$ m  
  (fuente: `simular.py#L20`).
- **Brazos axiales virtuales en Z**: $z_x = -0.039$ m (para $F_x$), $z_y = +0.021$ m (para $F_y$) (fuente: `simular.py#L24`).
- **Aceleración gravitatoria inercial**: $g = 9.80665 \text{ m/s}^2$ en $-Z$ (fuente: `simular.py#L5`).

### 2.3 Datos Calculados
- Estados cinemáticos integrados en el tiempo $r(t), v(t), q(t), \omega(t)$ mediante Runge-Kutta de 4º orden (RK4).
- Invariantes dinámicos evaluados: energía cinética rotacional $T_{\text{rot}}(t)$ y momento angular inercial $H_{\text{inertial}}(t)$.
- Derivas relativas y absolutas comparadas frente a soluciones analíticas en forma cerrada.

---

## 3. OBJETIVOS Y COMANDOS DE EJECUCIÓN

### 3.1 Comandos de Ejecución

```bash
# 1. Comprobación del script para simular.py (requiere numpy/scipy):
python3 salidas/test_integrador_rigido.py

# 2. Comprobación matemática analítica pura en Python estándar (sin dependencias):
python3 salidas/test_integrador_analitico_puro.py
```

### 3.2 Objetivos de las Pruebas

1. **Objetivo 1 (Conservación de Invariantes)**:
   Verificar que en ausencia de fuerzas y momentos exteriores ($F = 0, \tau = 0$), el resolvedor numérico RK4 preserve las dos integrales primeras de la mecánica clásica para un sólido rígido asimétrico triaxial ($I_{xx} \ne I_{yy} \ne I_{zz}$):
   - Conservación de energía cinética rotacional: $T_{\text{rot}} = \frac{1}{2} \omega^T I \omega \equiv \text{const}$.
   - Conservación del vector momento angular inercial: $H_{\text{inertial}} = R(q) (I \omega) \equiv \text{const}$.
   Evaluar además que la reducción sucesiva del paso temporal ($\Delta t = 0.02, 0.01, 0.005, 0.0025$ s) reduzca monótonamente los errores de conservación conforme a la tasa de convergencia teórica $\mathcal{O}(\Delta t^4)$ de RK4.

2. **Objetivo 2 (Cinemática de Cuaterniones vs Solución Analítica)**:
   Evaluar la integración cinemática del cuaternión bajo giro a velocidad angular constante $\Omega = \pi$ rad/s sobre un eje principal, comparando la actitud paso a paso con la solución exacta en forma cerrada:
   $$q_{\text{analítico}}(t) = \left[ \mathbf{u} \sin\left(\frac{\Omega t}{2}\right), \cos\left(\frac{\Omega t}{2}\right) \right]^T$$
   Comprobar adicionalmente la propiedad espinorial de los cuaterniones (doble cobertura del grupo $SO(3)$), donde tras una revolución completa de $360^\circ$ ($t = 2.0$ s), el cuaternión invierte su signo ($q \to -q_0 = [0, 0, 0, -1]^T$) preservando la matriz de rotación identidad $R = I_{3\times 3}$.

3. **Objetivo 3 (Par de Fuerzas Opuestas y Momento Resultante $r \times F$)**:
   Verificar la consistencia estática y dinámica de la matriz de asignación geométrica $A$:
   - Comprobar que un par de fuerzas iguales y opuestas produce una fuerza neta nula ($F_{\text{net}} = \sum F_i = 0$).
   - Comprobar que el par resultante $(A \cdot F)[3:]$ coincide de forma exacta con la suma vectorial de momentos $\sum (r_i \times F_i)$.
   - Comprobar que en la integración dinámica, la traslación queda desacoplada de la rotación (aceleración lineal idéntica a la gravedad pura y aceleración angular exactamente igual a $\dot{\omega} = I^{-1}\tau$).

---

## 4. FORMULACIÓN MATEMÁTICA Y JUSTIFICACIÓN DE TOLERANCIAS

### 4.1 Caso 1: Giro Libre Asimétrico con Pasos Decrecientes

- **Ecuaciones de movimiento**:
  $$\dot{\omega} = -I^{-1} (\omega \times (I \omega))$$
  $$\dot{q} = \frac{1}{2} \left[ q_w \omega + q_v \times \omega, -q_v \cdot \omega \right]^T$$
- **Condición inicial**:
  $\omega_0 = [1.5, 3.0, 0.8]^T$ rad/s (tres componentes no nulas para excitar completamente los acoplamientos no lineales de Euler).
  $I = [0.035314, 0.458994, 0.475459]^T \text{ kg}\cdot\text{m}^2$.
- **Métricas**:
  $$\Delta E_{\text{rel}} = \max_t \frac{|T_{\text{rot}}(t) - T_{\text{rot}}(0)|}{T_{\text{rot}}(0)}$$
  $$\Delta H_{\text{rel}} = \max_t \frac{\|H_{\text{inertial}}(t) - H_{\text{inertial}}(0)\|_2}{\|H_{\text{inertial}}(0)\|_2}$$
- **Justificación de tolerancias**:
  El método Runge-Kutta clásico de orden 4 posee un error de truncamiento local $\mathcal{O}(\Delta t^5)$ y global $\mathcal{O}(\Delta t^4)$.
  Para una simulación de $T = 2.0$ s (aproximadamente una rotación completa multiaxial):
  - A $\Delta t = 0.005$ s (paso nominal del modelo), el error global acumulado se acota analíticamente por debajo de $10^{-5}$.
  - Tolerancia cuantitativa: $\Delta E_{\text{rel}} \le 1.0 \times 10^{-5}$ y $\Delta H_{\text{rel}} \le 1.0 \times 10^{-5}$.
  - Tolerancia de consistencia: Monotonía estricta en el refinamiento de malla: $\Delta E(\Delta t_{k+1}) < \Delta E(\Delta t_k)$.

### 4.2 Caso 2: Cinemática de Cuaternión vs Solución Analítica

- **Ecuaciones y solución cerrada**:
  Con $\boldsymbol{\omega} = [0, 0, \pi]^T$ rad/s y $q_0 = [0, 0, 0, 1]^T$:
  $$q_{\text{exacto}}(t) = \left[ 0, 0, \sin\left(\frac{\pi t}{2}\right), \cos\left(\frac{\pi t}{2}\right) \right]^T$$
- **Métrica geodésica en $SO(3)$**:
  $$\Phi_{\text{err}}(t) = 2 \arccos\left( \min\left(1.0, |q_{\text{num}}(t) \cdot q_{\text{exacto}}(t)|\right) \right)$$
- **Justificación de tolerancias**:
  A $200$ Hz ($\Delta t = 0.005$ s), la integración de una función trigonométrica armónica pura durante una vuelta completa ($400$ pasos) introduce una dispersión numérica $< 10^{-7}$ rad ($\approx 5.7 \times 10^{-6}$ grados).
  - Tolerancia geodésica máxima: $\Phi_{\text{err}} \le 1.0 \times 10^{-7}$ rad.
  - Tolerancia de cierre espinorial a $360^\circ$ ($t = 2.0$ s): $\|q_{\text{num}} - [0, 0, 0, -1]^T\|_2 \le 1.0 \times 10^{-6}$.
  - Tolerancia de deriva de norma: $|\|q\| - 1| \le 1.0 \times 10^{-12}$.

### 4.3 Caso 3: Par de Fuerzas Opuestas y Momento $r \times F$

- **Configuración de par en cabeceo**:
  Fuerza en ventilador 0 ($x_0 = -0.2$ m): $F_0 = [0, 0, +10.0]^T$ N.  
  Fuerza en ventilador 2 ($x_2 = +0.2$ m): $F_2 = [0, 0, -10.0]^T$ N.  
  Ventiladores 1 y 3 apagados ($F_1 = F_3 = 0$).
- **Valores teóricos esperados**:
  - Fuerza neta: $F_{\text{net}} = F_0 + F_2 = [0, 0, 0]^T$ N.
  - Par geométrico:
    $$\tau_{\text{geom}} = r_0 \times F_0 + r_2 \times F_2 = \begin{bmatrix} -0.2 \\ -0.076 \\ 0 \end{bmatrix} \times \begin{bmatrix} 0 \\ 0 \\ 10 \end{bmatrix} + \begin{bmatrix} +0.2 \\ -0.076 \\ 0 \end{bmatrix} \times \begin{bmatrix} 0 \\ 0 \\ -10 \end{bmatrix} = \begin{bmatrix} -0.76 \\ 2.0 \\ 0 \end{bmatrix} + \begin{bmatrix} +0.76 \\ 2.0 \\ 0 \end{bmatrix} = \begin{bmatrix} 0 \\ 4.0 \\ 0 \end{bmatrix} \text{ N}\cdot\text{m}$$
  - Par por matriz $A$: $\tau_A = (A \cdot F_{\text{ravel}})[3:]$.
  - Aceleración lineal neta: $\ddot{r} = [0, 0, -9.80665]^T \text{ m/s}^2$.
  - Aceleración angular: $\dot{\omega} = \tau / I = [0, 4.0 / I_{yy}, 0]^T \approx [0, 8.7147, 0]^T \text{ rad/s}^2$.
- **Justificación de tolerancias**:
  - Operaciones algebraicas de fuerza neta y par matriz vs $r \times F$: Tolerancia de precisión de coma flotante de doble precisión: $1.0 \times 10^{-12}$ N y $1.0 \times 10^{-12}$ N·m.
  - Desacoplamiento dinámico a nivel de derivadas en `rigid_rhs`: $\|a - g_{\text{vec}}\| \le 1.0 \times 10^{-12} \text{ m/s}^2$ y $\|\dot{\omega} - \tau/I\| \le 1.0 \times 10^{-12} \text{ rad/s}^2$.

---

## 5. RESULTADOS EXPERIMENTALES DE LAS PRUEBAS NUMÉRICAS

### 5.1 Ejecución de `test_integrador_rigido.py` (Módulo original `simular.py`)

- **Comando**: `python3 salidas/test_integrador_rigido.py`
- **Resultado registrado**:
  ```
  DECLARACIÓN FORMAL: Dependencias requeridas no disponibles: ['numpy', 'scipy'].
  El integrador rígido original en 'simular.py' requiere numpy y scipy.
  Por consiguiente, las pruebas directas sobre 'simular.py' NO SE EJECUTARON.
  Se evita formalmente afirmar éxito en la ejecución de estas pruebas en este entorno.
  ```
- **Archivo emitido**: `salidas/REPORTE_PRUEBAS_SIMULAR.json` (`estado_global: "NO_EJECUTADO"`).

### 5.2 Ejecución de `test_integrador_analitico_puro.py` (Formulación matemática en Python estándar)

- **Comando**: `python3 salidas/test_integrador_analitico_puro.py`
- **Resultados cuantitativos**:

| Prueba / Métrica | Paso temporal ($\Delta t$) | Valor Calculado | Tolerancia Justificada | Dictamen |
|---|---|---|---|---|
| **Caso 1: Error energía $T_{\text{rot}}$** | $0.0200$ s | $1.612 \times 10^{-8}$ | - | Monótono |
| | $0.0100$ s | $7.990 \times 10^{-10}$ | - | Monótono |
| | $0.0050$ s | $4.345 \times 10^{-11}$ | $\le 1.0 \times 10^{-5}$ | **APROBADO** |
| | $0.0025$ s | $2.512 \times 10^{-12}$ | $\le 1.0 \times 10^{-6}$ | **APROBADO** |
| **Caso 1: Error momento inercial $H$** | $0.0200$ s | $2.917 \times 10^{-7}$ | - | Monótono |
| | $0.0100$ s | $1.828 \times 10^{-8}$ | - | Monótono |
| | $0.0050$ s | $1.144 \times 10^{-9}$ | $\le 1.0 \times 10^{-5}$ | **APROBADO** |
| | $0.0025$ s | $7.152 \times 10^{-11}$ | $\le 1.0 \times 10^{-6}$ | **APROBADO** |
| **Caso 2: Error geodésico actitud** | $0.0050$ s ($400$ pasos) | $4.215 \times 10^{-8}$ rad ($2.415 \times 10^{-6}$ deg) | $\le 1.0 \times 10^{-7}$ rad | **APROBADO** |
| **Caso 2: Cierre espinorial $q(360^\circ)$** | $t = 2.0$ s ($2\pi$ rad) | Diferencia frente a $-q_0$: $3.736 \times 10^{-11}$ | $\le 1.0 \times 10^{-6}$ | **APROBADO** |
| **Caso 3: Fuerza neta par cabeceo** | Estático | $0.00 \times 10^{0}$ N | $\le 1.0 \times 10^{-12}$ N | **APROBADO** |
| **Caso 3: Par matriz A vs $r \times F$** | Estático | $\Delta \tau = 0.00 \times 10^{0}$ N·m ($[0, 4.0, 0]$ N·m) | $\le 1.0 \times 10^{-12}$ N·m | **APROBADO** |
| **Caso 3: Aceleración traslacional** | Dinámico (`rigid_rhs`) | Error vs $-g$: $0.00 \times 10^{0}$ m/s² | $\le 1.0 \times 10^{-12}$ m/s² | **APROBADO** |
| **Caso 3: Aceleración angular** | Dinámico (`rigid_rhs`) | Error vs $\tau / I$: $0.00 \times 10^{0}$ rad/s² | $\le 1.0 \times 10^{-12}$ rad/s² | **APROBADO** |

- **Archivo emitido**: `salidas/REPORTE_VERIFICACION_ANALITICA.json`.

---

## 6. LIMITACIONES IDENTIFICADAS Y ALCANCE

1. **Dependencia de software de terceros en el código original**:
   El módulo original `simular.py` está fuertemente acoplado a `numpy` y `scipy` (`scipy.spatial.transform.Rotation`). Al no estar disponibles en el entorno de pruebas, no fue posible ejecutar directamente `salidas/simular.py`. Por consiguiente, se declara formalmente que dicho archivo no fue ejecutado y no se afirma éxito directo sobre su código en este entorno.
2. **Naturaleza de las pruebas (No validación física)**:
   Las pruebas implementadas son exclusivamente verificaciones matemáticas de consistencia interna del integrador numérico (conservación de invariantes hamiltonianos, cinemática de rotación cerrada y álgebra de momentos). No constituyen validación física de la aeronave, ni de los ventiladores, ni de la interacción aerodinámica entre chorros o resistencia al avance del fuselaje.
3. **Ausencia de términos no modelados**:
   El resolvedor analizado asume un cuerpo rígido no deformable, tensor de inercia rígidamente diagonal y ausencia total de arrastre aerodinámico ($C_D = 0$), par reactivo por rotación de hélices ($Q_{\text{rotor}} = 0$) y efectos giroscópicos inducidos por el momento angular de los ventiladores.
4. **Archivos de referencia no alterados**:
   No se modificó ningún archivo en `entradas/` ni se infirió que archivos no copiados no existan, manteniendo la trazabilidad absoluta de las copias de referencia.
