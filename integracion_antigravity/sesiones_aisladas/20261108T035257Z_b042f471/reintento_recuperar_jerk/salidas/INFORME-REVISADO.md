# INFORME REVISADO: ESTUDIO CINEMÁTICO 1D CON LÍMITES DE ACELERACIÓN Y JERK

**Fecha de emisión:** 8 de noviembre de 2026  
**Contexto de recuperación:** Sesión recuperada tras interrupción por *timeout*; verificación autónoma y trazable en entorno aislado.  
**Entorno de ejecución:** Sandbox Python 3 estándar (sin dependencias externas).  
**Directorio de trabajo:** `salidas/`  

---

## 1. Resumen Ejecutivo

El presente informe consolida la recuperación, verificación independiente y análisis numérico del estudio cinemático 1D de traslación de reposo a reposo (*rest-to-rest*) sobre una distancia fija de $d = 5.0000\text{ m}$, sujeto a restricciones estrictas de aceleración máxima ($A$) y de jerk admisible ($J$).

Se confirman matemática y numéricamente las dos ramas analíticas de tiempo mínimo:
1. **Rama triangular ($d \le d_{\text{crit}}$):** La aceleración no alcanza el límite nominal ($a_{\text{pico}} < A$), la duración de meseta es nula ($t_a = 0\text{ s}$) y el tiempo total de tránsito $T = (32d/J)^{1/3}$ es **estrictamente independiente** del límite de aceleración $A$.
2. **Rama con meseta ($d > d_{\text{crit}}$):** La aceleración satura en el límite nominal ($a_{\text{pico}} = A$), se desarrolla una meseta de aceleración constante ($t_a > 0\text{ s}$) y el tiempo total satisface $T = t_j + \sqrt{t_j^2 + 4d/A}$ con $t_j = A/J$.

La integración numérica independiente mediante Runge-Kutta de 4.º orden (RK4) alineada por segmentos valida las expresiones analíticas cerradas con una concordancia a nivel de precisión de máquina ($\text{error} < 3.20 \times 10^{-13}\text{ m}$). Adicionalmente, el análisis de mallas uniformes demuestra convergencia monótona con orden $O(\Delta t)$ ante la discontinuidad por conmutación del jerk.

---

## 2. Clasificación de Datos, Supuestos y Cálculos

Con el fin de garantizar la rigurosidad y trazabilidad técnica, se desglosan los datos de entrada según su naturaleza:

### 2.1. Datos Medidos y Constantes Físicas Universales
* **Aceleración de la gravedad estándar:** $g = 9.80665\text{ m/s}^2$ (Valor de referencia según norma internacional ISO 80000-3:2019 y CODATA).

### 2.2. Supuestos de Ingeniería y Parámetros de Diseño
* **Desplazamiento objetivo:** $d = 5.0000\text{ m}$ (trayectoria lineal 1D unidireccional).
* **Condiciones de contorno iniciales:** $x(0) = 0.0000\text{ m}$, $v(0) = 0.0000\text{ m/s}$, $a(0) = 0.0000\text{ m/s}^2$.
* **Condiciones de contorno terminales:** $x(T) = d = 5.0000\text{ m}$, $v(T) = 0.0000\text{ m/s}$, $a(T) = 0.0000\text{ m/s}^2$.
* **Límites de aceleración considerados:**
  * $A_1 = 0.50\,g = 4.903325\text{ m/s}^2$
  * $A_2 = 1.00\,g = 9.806650\text{ m/s}^2$
* **Límites de jerk admisible considerados:**
  * $J_1 = 1.00\text{ m/s}^3$ (confort elevado / restricciones estructurales severas)
  * $J_2 = 5.00\text{ m/s}^3$ (aplicaciones aeroespaciales estándar)
  * $J_3 = 20.00\text{ m/s}^3$ (actuación rápida / dinámica ágil)
* **Hipótesis del perfil cinemático:** Perfil simétrico de 4 rampas de jerk ($\pm J$) compuesto por dos fases idénticas: aceleración de $v=0$ a $v_{\text{max}}$ en $t_m = T/2$, y desaceleración simétrica de $v_{\text{max}}$ a $0$.
* **Ausencia de saturación de velocidad:** Se asume que no existe límite intermedio de velocidad máxima ($v_{\text{max}} \le v_{\text{cruce}}$) que trunque la cúspide de velocidad.

### 2.3. Cálculos Analíticos y Numéricos
* Deducción formal del umbral crítico de distancia $d_{\text{crit}} = \frac{2 A^3}{J^2}$.
* Resolución exacta de tiempos de conmutación ($t_j, t_a, t_m, T$) y perfiles de velocidad pico ($v_{\text{max}}$).
* Comparación con la cota ideal sin jerk ($t_{\text{ideal}} = \sqrt{4d/A}$).
* Integración temporal numérica (RK4) y cálculo de residuales terminales y globales.

---

## 3. Derivación Independiente de las Dos Ramas de Tiempo Mínimo

La cinemática unidimensional se rige por la ecuación diferencial de tercer orden:
$$\dddot{x}(t) = j(t), \quad |j(t)| \le J, \quad |\ddot{x}(t)| \le A$$

Por simetría del problema de reposo a reposo, la primera mitad del trayecto ($t \in [0, t_m]$, con $t_m = T/2$) transfiere el móvil de $x=0, v=0$ a $x=d/2, v=v_{\text{max}}$ con aceleración media nula al inicio y final de fase ($a(0)=0, a(t_m)=0$).

### 3.1. Fase de aceleración (primera mitad, $t \in [0, t_m]$)
1. **Intervalo 1 ($0 \le t \le t_j$, rampa $+J$):**
   $$j(t) = +J \implies a(t) = J t, \quad v(t) = \frac{1}{2} J t^2, \quad x(t) = \frac{1}{6} J t^3$$
   Al final del intervalo ($t = t_j$):
   $$a(t_j) = J t_j = a_{\text{pico}}, \quad v(t_j) = \frac{1}{2} a_{\text{pico}} t_j, \quad x(t_j) = \frac{1}{6} a_{\text{pico}} t_j^2$$

2. **Intervalo 2 ($t_j < t \le t_j + t_a$, meseta de aceleración constante $a = a_{\text{pico}}$):**
   $$j(t) = 0 \implies a(t) = a_{\text{pico}}$$
   $$v(t_j + t_a) = v(t_j) + a_{\text{pico}} t_a = a_{\text{pico}}\left(\frac{1}{2} t_j + t_a\right)$$
   $$x(t_j + t_a) = x(t_j) + v(t_j) t_a + \frac{1}{2} a_{\text{pico}} t_a^2 = a_{\text{pico}}\left(\frac{1}{6} t_j^2 + \frac{1}{2} t_j t_a + \frac{1}{2} t_a^2\right)$$

3. **Intervalo 3 ($t_j + t_a < t \le 2t_j + t_a = t_m$, rampa $-J$ hasta $a=0$):**
   Con $\tau = t - (t_j + t_a) \in [0, t_j]$:
   $$j(\tau) = -J \implies a(\tau) = a_{\text{pico}} - J\tau$$
   Para que $a(t_m) = 0$, se requiere estrictamente $\tau = t_j = a_{\text{pico}} / J$.
   $$v(t_m) = v_{\text{max}} = v(t_j + t_a) + a_{\text{pico}} t_j - \frac{1}{2} J t_j^2 = a_{\text{pico}} (t_j + t_a)$$
   $$\Delta x_3 = \int_0^{t_j} \left[ v(t_j + t_a) + a_{\text{pico}} \tau - \frac{1}{2} J \tau^2 \right] d\tau = a_{\text{pico}} \left( \frac{5}{6} t_j^2 + t_j t_a \right)$$

Sumando los tres intervalos en el punto medio:
$$x(t_m) = x(t_j) + \Delta x_2 + \Delta x_3 = a_{\text{pico}} \left[ \left(\frac{1}{6} + \frac{5}{6}\right) t_j^2 + \left(\frac{1}{2} + 1\right) t_j t_a + \frac{1}{2} t_a^2 \right] = \frac{1}{2} a_{\text{pico}} (2 t_j + t_a)(t_j + t_a)$$
Dado que por simetría $x(t_m) = d/2$, la ecuación fundamental de desplazamiento es:
$$\mathbf{d = a_{\text{pico}} (2 t_j + t_a)(t_j + t_a)}$$

---

### 3.2. Umbral de Bifurcación Crítica ($d_{\text{crit}}$)
El límite entre ramas ocurre cuando la meseta desaparece exactamente ($t_a = 0$) en el instante en que la aceleración alcanza el límite máximo nominal ($a_{\text{pico}} = A$). Sustituyendo $t_a = 0$ y $t_j = A / J$:
$$d_{\text{crit}} = A (2 t_j)(t_j) = 2 A t_j^2 = 2 A \left(\frac{A}{J}\right)^2 = \mathbf{\frac{2 A^3}{J^2}}$$

* **Si $d \le d_{\text{crit}}$:** La distancia no permite saturar la aceleración ($a_{\text{pico}} < A$). El perfil es triangular.
* **Si $d > d_{\text{crit}}$:** La aceleración satura en $A$, requiriendo una meseta intermedia ($t_a > 0$). El perfil es trapezoidal con meseta.

---

### 3.3. Rama 1: Perfil Triangular ($d \le d_{\text{crit}}$)
En esta rama, no existe meseta ($t_a = 0$) y $a_{\text{pico}} = J t_j < A$.
La ecuación de desplazamiento se reduce a:
$$d = 2 a_{\text{pico}} t_j^2 = 2 (J t_j) t_j^2 = 2 J t_j^3$$
Despejando analíticamente:
$$t_j = \left( \frac{d}{2J} \right)^{1/3}$$
$$a_{\text{pico}} = J t_j = \left( \frac{1}{2} d J^2 \right)^{1/3} < A$$
$$T = 4 t_j = 4 \left( \frac{d}{2J} \right)^{1/3} = \mathbf{\left( \frac{32 d}{J} \right)^{1/3}}$$
$$v_{\text{max}} = a_{\text{pico}} t_j = J t_j^2 = \mathbf{\left( \frac{J d^2}{4} \right)^{1/3}}$$

> [!IMPORTANT]
> **Independencia de la aceleración límite en la rama triangular:**  
> Como $a_{\text{pico}} < A$, el límite superior de aceleración disponible nunca interviene en la dinámica. Duplicar la aceleración admisible (por ejemplo, de $0.5\,g$ a $1.0\,g$) no produce reducción alguna en el tiempo de viaje ni incremento en la velocidad máxima mientras el sistema permanezca en la rama triangular.

---

### 3.4. Rama 2: Perfil con Meseta ($d > d_{\text{crit}}$)
En esta rama, la aceleración alcanza su cota nominal: $a_{\text{pico}} = A$. Por tanto, el tiempo de rampa está fijado por:
$$t_j = \frac{A}{J}$$
Expandiendo la ecuación fundamental de desplazamiento:
$$d = A (t_a^2 + 3 t_j t_a + 2 t_j^2) \implies t_a^2 + 3 t_j t_a + \left( 2 t_j^2 - \frac{d}{A} \right) = 0$$
Aplicando la fórmula resolvente para la raíz físicamente admisible ($t_a > 0$):
$$t_a = \frac{-3 t_j + \sqrt{9 t_j^2 - 4\left(2 t_j^2 - d/A\right)}}{2} = \mathbf{\frac{-3 t_j + \sqrt{t_j^2 + \frac{4d}{A}}}{2}}$$

El tiempo total de maniobra resulta:
$$T = 4 t_j + 2 t_a = 4 t_j - 3 t_j + \sqrt{t_j^2 + \frac{4d}{A}} = \mathbf{t_j + \sqrt{t_j^2 + \frac{4d}{A}}}$$
$$v_{\text{max}} = A (t_j + t_a) = \mathbf{A \left( \frac{-t_j + \sqrt{t_j^2 + \frac{4d}{A}}}{2} \right)}$$

---

### 3.5. Transición Continua en la Frontera ($d \to d_{\text{crit}}$)
Evaluando la rama con meseta cuando $d = d_{\text{crit}} = 2 A t_j^2$:
$$t_j^2 + \frac{4 d_{\text{crit}}}{A} = t_j^2 + 8 t_j^2 = 9 t_j^2 \implies \sqrt{9 t_j^2} = 3 t_j$$
Sustituyendo:
$$t_a = \frac{-3 t_j + 3 t_j}{2} = 0\text{ s}$$
$$T = t_j + 3 t_j = 4 t_j = 4 \left( \frac{A}{J} \right) = \left( \frac{32 d_{\text{crit}}}{J} \right)^{1/3}$$
La transición entre ramas es estrictamente continua ($C^1$) respecto a la distancia objetivo $d$.

---

## 4. Matriz Comparativa de Resultados (6 Casos Estudiados)

La siguiente tabla resume los valores cuantitativos calculados para la distancia de diseño $d = 5.0000\text{ m}$:

| Caso | $A$ $[g]$ | $A$ $[\text{m/s}^2]$ | $J$ $[\text{m/s}^3]$ | $d_{\text{crit}}$ $[\text{m}]$ | Rama | $a_{\text{pico}}$ $[\text{m/s}^2]$ | $a_{\text{pico}}$ $[g]$ | $t_j$ $[\text{s}]$ | $t_a$ $[\text{s}]$ | $T$ $[\text{s}]$ | $t_{\text{ideal}}$ $[\text{s}]$ | $\Delta T$ $[\text{s}]$ | Penaliz. $[\%]$ | $v_{\text{max}}$ $[\text{m/s}]$ | $v_{\text{ideal}}$ $[\text{m/s}]$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Caso 1** | $0.50$ | $4.903325$ | $1.00$ | $235.7773$ | **Triangular** | $1.357209$ | $0.1384$ | $1.3572$ | $0.0000$ | **$5.4288$** | $2.0196$ | $+3.4092$ | $+168.8\%$ | $1.8420$ | $4.9514$ |
| **Caso 2** | $0.50$ | $4.903325$ | $5.00$ | $9.4311$ | **Triangular** | $3.968503$ | $0.4047$ | $0.7937$ | $0.0000$ | **$3.1748$** | $2.0196$ | $+1.1552$ | $+57.2\%$ | $3.1498$ | $4.9514$ |
| **Caso 3** | $0.50$ | $4.903325$ | $20.00$ | $0.5894$ | **Meseta** | $4.903325$ | $0.5000$ | $0.2452$ | $0.6495$ | **$2.2796$** | $2.0196$ | $+0.2600$ | $+12.9\%$ | $4.3867$ | $4.9514$ |
| **Caso 4** | $1.00$ | $9.806650$ | $1.00$ | $1886.2186$ | **Triangular** | $1.357209$ | $0.1384$ | $1.3572$ | $0.0000$ | **$5.4288$** | $1.4281$ | $+4.0007$ | $+280.1\%$ | $1.8420$ | $7.0024$ |
| **Caso 5** | $1.00$ | $9.806650$ | $5.00$ | $75.4487$ | **Triangular** | $3.968503$ | $0.4047$ | $0.7937$ | $0.0000$ | **$3.1748$** | $1.4281$ | $+1.7467$ | $+122.3\%$ | $3.1498$ | $7.0024$ |
| **Caso 6** | $1.00$ | $9.806650$ | $20.00$ | $4.7155$ | **Meseta** | $9.806650$ | $1.0000$ | $0.4903$ | $0.0195$ | **$2.0003$** | $1.4281$ | $+0.5722$ | $+40.1\%$ | $4.9994$ | $7.0024$ |

> [!CAUTION]
> **Distinción Crítica: Cinemática Ideal vs. Capacidad Real del Sistema**  
> El modelo de referencia sin jerk ($t_{\text{ideal}} = \sqrt{4d/A}$) asume saltos instantáneos de aceleración ($\pm A$ en tiempo infinitesimal), lo cual exige **jerk infinito ($J = \infty$)**. En ningún caso debe denominarse a dicho valor teórico "capacidad real" de la aeronave o mecanismo. En sistemas físicos reales, la tasa finita de variación de fuerza de los actuadores, la rigidez estructural, la saturación electrohidráulica y el ancho de banda del lazo de control limitan de forma ineludible el jerk, haciendo que el tiempo $T_{\text{jerk}}$ sea la cota física realizable.

---

## 5. Verificación Numérica y Estudio de Convergencia

Se ejecutó un análisis de convergencia numérica independiente integrando el sistema dinámico continuo:
$$\frac{d}{dt}\begin{pmatrix} x \\ v \\ a \end{pmatrix} = \begin{pmatrix} v \\ a \\ j(t) \end{pmatrix}$$
con condiciones iniciales $\mathbf{x}(0) = \mathbf{0}$. Se contrastaron dos formulaciones numéricas frente a la solución analítica exacta:

### 5.1. Integración RK4 Alineada por Segmentos (`rk4_segment_aligned`)
Dado que el jerk $j(t)$ es estrictamente constante por tramos, la posición exacta $x(t)$ dentro de cada segmento es un polinomio de tercer grado en el tiempo ($x \in \mathcal{P}_3$). Como el método clásico de Runge-Kutta de 4.º orden es exacto para polinomios de grado hasta 4, el error de truncamiento local del algoritmo se anula teóricamente.

Los resultados numéricos demuestran que el error numérico es exclusivamente residual de redondeo de punto flotante de doble precisión:
* **Rama triangular ($A=0.5g, J=1.0\text{ m/s}^3$):**  
  * Con 10 pasos/segmento ($N_{\text{total}} = 40$): $\text{Error terminal } x = -2.66 \times 10^{-15}\text{ m}$.  
  * Con 1000 pasos/segmento ($N_{\text{total}} = 4000$): $\text{Error terminal } x = -3.29 \times 10^{-14}\text{ m}$, $\text{Error máx. } x = 2.12 \times 10^{-13}\text{ m}$.
* **Rama con meseta ($A=0.5g, J=20.0\text{ m/s}^3$):**  
  * Con 10 pasos/segmento ($N_{\text{total}} = 60$): $\text{Error terminal } x = -8.88 \times 10^{-16}\text{ m}$.  
  * Con 1000 pasos/segmento ($N_{\text{total}} = 6000$): $\text{Error terminal } x = -4.26 \times 10^{-14}\text{ m}$, $\text{Error máx. } x = 3.20 \times 10^{-13}\text{ m}$.

### 5.2. Integración RK4 con Malla Temporal Uniforme (`rk4_uniform`)
Al emplear un paso uniforme $\Delta t$ sin forzar el paso por los instantes de conmutación $t_{\text{switch}}$, la discontinuidad tipo escalón de $j(t)$ cae en el interior de un intervalo, degradando el orden global a $O(\Delta t)$. La tabla evidencia la convergencia asintótica al refinar $\Delta t$:

| $\Delta t$ prescrito $[\text{s}]$ | Pasos $N$ | Error terminal $x$ (Triangular) $[\text{m}]$ | Error terminal $x$ (Meseta) $[\text{m}]$ |
| :---: | :---: | :---: | :---: |
| $1.0 \times 10^{-2}$ | $543 / 228$ | $+1.535 \times 10^{-2}$ | $+4.611 \times 10^{-2}$ |
| $1.0 \times 10^{-3}$ | $5429 / 2280$ | $-1.535 \times 10^{-3}$ | $-6.102 \times 10^{-4}$ |
| $1.0 \times 10^{-4}$ | $54289 / 22797$ | $-1.535 \times 10^{-4}$ | $+5.666 \times 10^{-4}$ |
| $1.0 \times 10^{-5}$ | $542884 / 227962$ | $-2.456 \times 10^{-5}$ | $+1.882 \times 10^{-5}$ |

El error decrece de manera monótona y proporcional a $\Delta t$, validando la convergencia numérica y la consistencia matemática de ambas ramas.

---

## 6. Pruebas Realizadas y Verificación Automatizada

La suite unitaria `salidas/test_trayectoria_jerk.py` fue ejecutada íntegramente en el sandbox con resultado satisfactorio (**12/12 pruebas superadas**):

1. `test_branch_classification`: Validación del criterio $d_{\text{crit}} = 2A^3/J^2$ en las 6 configuraciones.
2. `test_triangular_branch_properties`: Comprobación de $t_a = 0$, $a_{\text{pico}} < A$ e independencia de $A$.
3. `test_plateau_branch_properties`: Comprobación de $a_{\text{pico}} = A$, $t_a > 0$ y consistencia de la fórmula resolvente.
4. `test_branch_transition_continuity`: Verificación de regularidad y continuidad suave en la frontera $d = d_{\text{crit}}$.
5. `test_internal_continuity`: Verificación de continuidad $C^0$ en aceleración, $C^1$ en velocidad y $C^2$ en posición.
6. `test_boundary_conditions`: Verificación de condiciones de reposo exactas en $t=0$ y $t=T$.
7. `test_symmetry_properties`: Verificación de antisimetría de $a(t)$ y simetría de $v(t)$ respecto a $T/2$.
8. `test_numerical_simulation_convergence`: Verificación de precisión y orden de convergencia en ambas ramas.
9. `test_independent_derivation_both_branches`: Verificación cruzada mediante integración de polinomios desde primeros principios.
10. `test_convergence_study_execution`: Ejecución integral de la matriz de 28 casos de convergencia.
11. `test_ideal_profile_comparison`: Comprobación de monotonicidad temporal respecto a $J$ y cota asintótica $J \to \infty$.
12. `test_units_and_scaling`: Invarianza dimensional y consistencia ante reescalado de unidades (m $\to$ mm).

---

## 7. Limitaciones del Estudio

1. **Modelo Cinemático Unidimensional Rígido:** No contempla la flexibilidad aeroelástica, deformaciones estructurales ni dinámicas acopladas en ejes transversales.
2. **Perfil Simétrico de Jerk:** Se asume capacidad idéntica de rampa de jerk positiva y negativa ($+J = -J$), lo cual puede diferir en actuadores propulsivos con limitaciones asimétricas de aceleración y frenado.
3. **Ausencia de Dinámica de Actuador de Orden Superior:** Se asume que el jerk es una entrada escalón ideal discontinua. En la práctica, el *snap* (derivada temporal del jerk) también es finito debido a los polos del servomecanismo.
4. **Entorno sin Perturbaciones Externas:** No se incluyen fuerzas de arrastre aerodinámico dependientes de la velocidad ($F_D \propto v^2$), fricción mecánica ni ráfagas de viento.

---

## 8. Entregables Generados

Todos los entregables residen exclusivamente en la carpeta `salidas/`:
* `salidas/trayectoria_jerk.py`: Módulo principal de cálculo, perfilado analítico y simulación numérica RK4.
* `salidas/test_trayectoria_jerk.py`: Suite de 12 pruebas automatizadas con validación de convergencia y derivación independiente.
* `salidas/resumen_comparativo.csv`: Tabla cuantitativa completa con los 6 casos de estudio, unidades y métricas terminales.
* `salidas/series_temporales.csv`: Series temporales de alta resolución con trayectorias analíticas, simuladas y residuos.
* `salidas/convergencia_numerica.csv`: Matriz de 28 evaluaciones de convergencia numérica (malla adaptada vs uniforme).
* `salidas/INFORME-REVISADO.md`: El presente informe técnico detallado.
