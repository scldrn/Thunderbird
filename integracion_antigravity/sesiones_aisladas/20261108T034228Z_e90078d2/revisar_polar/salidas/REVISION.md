# REVISIÓN TÉCNICA: CONDICIÓN CINEMÁTICA, LECTURA DE POLARES DRG Y COBERTURA AERODINÁMICA

**Fecha:** 8 de noviembre de 2026  
**Directorio de trabajo:** `salidas/`  
**Referencia de origen:** `entradas/investigacion-aeronautica/`  
**Estado:** Verificado y validado  

---

## 1. Resumen Ejecutivo y Alcance de la Revisión

El presente documento constituye la revisión técnica, dimensional y aerodinámica formal solicitada sobre la condición cinemática de cuerda mínima para la pala del rotor con perfil SD8020:

$$c \ge \frac{Re_{\min} \cdot \nu}{M_{\lim} \cdot a} = c_{\min}$$

Se verificaron rigurosamente:
1. Las unidades y el análisis dimensional en el Sistema Internacional (SI).
2. La lectura e integridad de los bloques de número de Reynolds a partir del archivo fuente medido [`SD8020.DRG`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/entradas/investigacion-aeronautica/fuentes/uiuc/SD8020.DRG).
3. La reproducción matemática exacta del ejemplo canónico de referencia ($Re_{\min} = 61.400$, $M_{\lim} = 0,3 \implies c_{\min} = 8,781\text{ mm}$).
4. La distinción crítica entre los archivos `SD8020.DRG` (polar completa con sustentación y arrastre) y `SD8020.LFT` (sustentación pura sin arrastre).
5. La justificación física de que $M = 0,3$ representa una **convención ingenieril de cribado de incompresibilidad** y **no un umbral físico universal**.
6. La ejecución y validación de la suite de pruebas automatizadas y scripts exportados a [`salidas/`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/).

---

## 2. Taxonomía de Datos: Medidos, Supuestos y Cálculos

Siguiendo el principio de integridad y trazabilidad, se clasifica cada variable según su origen metodológico, indicando valores, unidades SI y fuentes:

| Categoría | Variable / Parámetro | Símbolo | Valor(es) | Unidades SI | Fuente / Justificación |
|---|---|---|---|---|---|
| **Dato Medido (Experimental)** | Reynolds medios de bloques DRG | $Re$ | $61.400$, $101.500$, $203.300$, $304.800$ | Adimensional $[-]$ | Ensayos en túnel de viento UIUC LSAT Vol. 1 (Selig et al.), archivados en [`entradas/investigacion-aeronautica/fuentes/uiuc/SD8020.DRG`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/entradas/investigacion-aeronautica/fuentes/uiuc/SD8020.DRG). Polar 2D completa ($C_l, C_d$). |
| **Dato Medido (Experimental)** | Ángulos y coeficientes polares | $\alpha, C_l, C_d$ | Rangos tabulados por bloque | $[^\circ], [-], [-]$ | Mediciones aerodinámicas en túnel UIUC; el rango angular de arrastre es restringido (e.g., $[-6,45^\circ, +7,40^\circ]$ a $Re=61.400$). |
| **Supuesto Físico** | Viscosidad cinemática del aire | $\nu$ | $1,46 \times 10^{-5}$ | $\text{m}^2/\text{s}$ | Propiedad supuesta para aire estándar aproximado a nivel del mar (ISA, $T \approx 288,15\text{ K}$, $p = 101.325\text{ Pa}$). |
| **Supuesto Físico** | Velocidad acústica en aire | $a$ | $340,3$ | $\text{m}/\text{s}$ | Supuesto para velocidad del sonido en aire seco ($a = \sqrt{\gamma R T}$, con $\gamma=1,4$ y $R=287,05\text{ J/(kg}\cdot\text{K)}$ a $T \approx 288,15\text{ K}$). |
| **Supuesto de Diseño / Cribado** | Límites de Mach operacional | $M_{\lim}$ | $0,2$, $0,3$, $0,4$ | Adimensional $[-]$ | **Criterio de ingeniería de cribado preliminar**. No es una barrera física natural. |
| **Cálculo Deducido** | Velocidad relativa admisible | $W_{\max}$ | $68,06$, $102,09$, $136,12$ | $\text{m}/\text{s}$ | Obtenido de $W_{\max} = M_{\lim} \cdot a$. |
| **Cálculo Deducido** | Cuerda mínima admisible | $c_{\min}$ | $6,586$ a $65,385$ | $\text{mm}$ ($\text{m}$) | Obtenido analíticamente de $c_{\min} = \frac{Re_{\min} \cdot \nu}{M_{\lim} \cdot a}$. |
| **Cálculo Deducido** | Sensibilidades analíticas | $\frac{\partial c_{\min}}{\partial Re}$, $\frac{\partial c_{\min}}{\partial M}$ | Analíticas exactas | $\frac{\text{m}}{\text{Re}}$, $\frac{\text{m}}{\text{Mach}}$ | Gradientes matemáticos del modelo cinemático. |

---

## 3. Revisión de Unidades y Análisis Dimensional

### 3.1. Deducción Analítica

A partir de las definiciones fundamentales de similitud en una sección de pala bidimensional con cuerda local $c$ y velocidad relativa local $W$:

1. Número de Reynolds:
   $$Re = \frac{W \cdot c}{\nu} \implies W = \frac{Re \cdot \nu}{c}$$

2. Número de Mach:
   $$M = \frac{W}{a} = \frac{Re \cdot \nu}{c \cdot a}$$

Para garantizar simultáneamente que el flujo opere dentro de la envolvente de ensayo inferior ($Re \ge Re_{\min}$) sin exceder la cota superior de velocidad de cribado ($M \le M_{\lim}$):

$$M_{\lim} \ge M = \frac{Re \cdot \nu}{c \cdot a} \ge \frac{Re_{\min} \cdot \nu}{c \cdot a}$$

Despejando $c$, dado que $c > 0$, $M_{\lim} > 0$ y $a > 0$:

$$c \ge \frac{Re_{\min} \cdot \nu}{M_{\lim} \cdot a} = c_{\min}$$

### 3.2. Homogeneidad Dimensional en el Sistema Internacional (SI)

Evaluando las dimensiones fundamentales en el sistema longitud-tiempo $[L, T]$:
* $[Re_{\min}] = [1]$ (adimensional)
* $[\nu] = \frac{\text{m}^2}{\text{s}} = [L^2 T^{-1}]$
* $[M_{\lim}] = [1]$ (adimensional)
* $[a] = \frac{\text{m}}{\text{s}} = [L T^{-1}]$

Sustituyendo en la expresión de $c_{\min}$:

$$[c_{\min}] = \frac{[Re_{\min}] \cdot [\nu]}{[M_{\lim}] \cdot [a]} = \frac{[1] \cdot [L^2 T^{-1}]}{[1] \cdot [L T^{-1}]} = \frac{L^2 \cdot T}{L \cdot T} = L \quad [\text{metros}]$$

Para obtener el valor en milímetros:

$$c_{\min}\text{ [mm]} = c_{\min}\text{ [m]} \times 1.000\text{ mm/m}$$

La ecuación es rigurosamente homogénea y consistente.

---

## 4. Validación del Ejemplo de Referencia (8,781 mm)

Evaluando la condición cinemática para los valores canónicos del informe previo:
* $Re_{\min} = 61.400$
* $M_{\lim} = 0,3$
* $\nu = 1,46 \times 10^{-5}\text{ m}^2/\text{s}$
* $a = 340,3\text{ m/s}$

Cálculo paso a paso:

1. Numerador:
   $$\text{Num} = Re_{\min} \cdot \nu = 61.400 \times 1,46 \times 10^{-5}\text{ m}^2/\text{s} = 0,89644\text{ m}^2/\text{s}$$

2. Denominador:
   $$\text{Den} = M_{\lim} \cdot a = 0,3 \times 340,3\text{ m/s} = 102,09\text{ m/s}$$

3. Cuerda mínima en metros:
   $$c_{\min} = \frac{0,89644\text{ m}^2/\text{s}}{102,09\text{ m/s}} = 0,008780879616025077...\text{ m}$$

4. Conversión a milímetros y redondeo:
   $$c_{\min} = 8,780879616...\text{ mm} \xrightarrow{\text{redondeo a 3 decimales}} 8,781\text{ mm}$$

**Conclusión:** La reproducción matemática del ejemplo canónico de **8,781 mm** es exacta y carece de desviación analítica.

---

## 5. Lectura y Validación de Reynolds en UIUC DRG vs. LFT

### 5.1. Lectura del Archivo `SD8020.DRG`

El parser implementado en [`salidas/sensibilidad_cinematica.py`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/sensibilidad_cinematica.py) inspecciona directamente el archivo experimental [`entradas/investigacion-aeronautica/fuentes/uiuc/SD8020.DRG`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/entradas/investigacion-aeronautica/fuentes/uiuc/SD8020.DRG). La lectura extrae con fidelidad los cuatro bloques tabulados:

1. **Bloque 1:** Average Reynolds #: `61400` (10 ángulos, $\alpha \in [-6,45^\circ, +7,40^\circ]$)
2. **Bloque 2:** Average Reynolds #: `101500` (11 ángulos, $\alpha \in [-6,55^\circ, +8,90^\circ]$)
3. **Bloque 3:** Average Reynolds #: `203300` (11 ángulos, $\alpha \in [-6,41^\circ, +8,87^\circ]$)
4. **Bloque 4:** Average Reynolds #: `304800` (11 ángulos, $\alpha \in [-6,78^\circ, +8,87^\circ]$)

### 5.2. Distinción Fundamental: LFT (Sustentación sin Arrastre) vs. DRG (Polar Completa)

Es crucial para el modelado aerodinámico del rotor no confundir la naturaleza de ambos conjuntos de datos de UIUC:

| Característica | Archivo `SD8020.DRG` | Archivo `SD8020.LFT` |
|---|---|---|
| **Contenido Físico** | Sustentación ($C_l$) **y Arrastre ($C_d$)** combinados | **Únicamente Sustentación ($C_l$)** |
| **Arrastre ($C_d$)** | **Disponible** (medido mediante peine de estela / wake rake) | **Ausente** (sin medición de arrastre) |
| **Rango de Reynolds** | $Re \in \{61.400, 101.500, 203.300, 304.800\}$ | $Re \in \{30.500, 40.700, 61.100, \dots\}$ |
| **Rango Angular** | Reducido ($\approx -6^\circ$ a $+8^\circ$) | Extendido (hasta $\approx 17,7^\circ$, con ramas creciente y decreciente) |
| **Aplicabilidad en BEM de Rotor** | **Apto para balance completo**: permite calcular empuje y potencia/par | **Incompleto para rotor**: la ley de potencia y par exige indefectiblemente $C_d$ |

> [!WARNING]
> **No confundir LFT con DRG**: El archivo `SD8020.LFT` aporta datos experimentales a Reynolds más bajos ($Re \approx 30.500$), pero **carece de arrastre**. No es admisible emplear `LFT` para el cálculo de potencia, rendimiento o pérdidas de perfil sin inventar o extrapolar un arrastre no medido. La condición cinemática $c_{\min} = 8,781\text{ mm}$ aplica a la polar `DRG`, que es la única que contiene la información de arrastre necesaria para el rotor.

---

## 6. Naturaleza del Límite Mach: Criterio de Cribado vs. Umbral Físico Universal

> [!IMPORTANT]
> **$M = 0,3$ NO es un umbral físico universal**: En fluidodinámica no ocurre ninguna discontinuidad termodinámica, salto de estado o singularidad en $M = 0,3$. Denominar a $M = 0,3$ "límite físico universal" constituiría un error conceptual.

### 6.1. Justificación Matemática del Criterio $M = 0,3$

La elección de $M \approx 0,3$ es una **convención de ingeniería clásica** para determinar cuándo es aceptable tratar un flujo como incompresible ($\rho \approx \text{cte}$). 

A partir de la relación de flujo compresible isentrópico en un punto de estancamiento:

$$\frac{\rho_0}{\rho} = \left(1 + \frac{\gamma - 1}{2} M^2\right)^{\frac{1}{\gamma - 1}}$$

Expandiendo en serie de Taylor de primer orden para gases diatómicos ($\gamma = 1,4$):

$$\frac{\rho_0 - \rho}{\rho} \approx \frac{1}{2} M^2$$

Evaluando en diferentes límites de Mach:
* Para $M = 0,2$: $\frac{\Delta \rho}{\rho} \approx \frac{1}{2}(0,2)^2 = 2,0\%$ de variación de densidad.
* Para $M = 0,3$: $\frac{\Delta \rho}{\rho} \approx \frac{1}{2}(0,3)^2 = 4,5\%$ de variación de densidad.
* Para $M = 0,4$: $\frac{\Delta \rho}{\rho} \approx \frac{1}{2}(0,4)^2 = 8,0\%$ de variación de densidad.

En la práctica ingenieril, variaciones relativas de densidad inferiores al $5\%$ se consideran despreciables frente a otras incertidumbres experimentales. Por tanto, $M_{\lim} = 0,3$ es un **criterio de cribado preliminar de incompresibilidad**, adoptado para no requerir correcciones compresibles (e.g., Prandtl-Glauert o Kármán-Tsien).

---

## 7. Matriz de Sensibilidad Cinemática y Elasticidades

Se calculó la matriz para los 4 bloques de Reynolds de `SD8020.DRG` y los límites de Mach de cribado $M_{\lim} \in \{0,2, 0,3, 0,4\}$:

### 7.1. Tabla Pivote de Cuerda Mínima ($c_{\min}$ en mm)

| Reynolds DRG ($Re_{\min}$) | $M_{\lim} = 0,2$ ($W_{\max} = 68,06\text{ m/s}$) | $M_{\lim} = 0,3$ ($W_{\max} = 102,09\text{ m/s}$) | $M_{\lim} = 0,4$ ($W_{\max} = 136,12\text{ m/s}$) |
|:---:|:---:|:---:|:---:|
| **$61.400$** | $13,171\text{ mm}$ | **$8,781\text{ mm}$** (caso canónico) | $6,586\text{ mm}$ |
| **$101.500$** | $21,773\text{ mm}$ | $14,516\text{ mm}$ | $10,887\text{ mm}$ |
| **$203.300$** | $43,611\text{ mm}$ | $29,074\text{ mm}$ | $21,806\text{ mm}$ |
| **$304.800$** | $65,385\text{ mm}$ | $43,590\text{ mm}$ | $32,692\text{ mm}$ |

### 7.2. Elasticidades y Proporcionalidades Exactas

1. **Sensibilidad respecto a $Re_{\min}$:**
   $$\frac{\partial c_{\min}}{\partial Re_{\min}} = \frac{\nu}{M_{\lim} \cdot a} > 0$$
   - Elasticidad: $\varepsilon_{Re} = \frac{\partial c_{\min} / c_{\min}}{\partial Re / Re} = +1,0$ (crecimiento lineal directo).

2. **Sensibilidad respecto a $M_{\lim}$:**
   $$\frac{\partial c_{\min}}{\partial M_{\lim}} = -\frac{Re_{\min} \cdot \nu}{M_{\lim}^2 \cdot a} = -\frac{c_{\min}}{M_{\lim}} < 0$$
   - Elasticidad: $\varepsilon_M = \frac{\partial c_{\min} / c_{\min}}{\partial M / M} = -1,0$ (decrecimiento hiperbólico inverso).

3. **Relaciones fijas:**
   - Para cualquier Reynolds, $\frac{c_{\min}(M=0,2)}{c_{\min}(M=0,4)} = \frac{0,4}{0,2} = 2,0$ exacto.
   - Para cualquier Reynolds, $\frac{c_{\min}(M=0,3)}{c_{\min}(M=0,2)} = \frac{0,2}{0,3} = \frac{2}{3} \approx 0,6667$.

---

## 8. Verificación de Scripts y Pruebas Unitarias

Se copiaron a [`salidas/`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/) los ejecutables:
* [`salidas/sensibilidad_cinematica.py`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/sensibilidad_cinematica.py)
* [`salidas/test_sensibilidad.py`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/test_sensibilidad.py)

### 8.1. Ejecución del Script Principal
```bash
python3 salidas/sensibilidad_cinematica.py
```
**Salida obtenida:**
```
[OK] Reynolds extraidos de SD8020.DRG: [61400, 101500, 203300, 304800]
[OK] Benchmark Re=61400, M=0.3: c_min=8.781 mm (esperado: 8.781 mm, match=True)
[OK] CSV detallado generado en: salidas/matriz_sensibilidad_cmin.csv
[OK] CSV tabla pivote generada en: salidas/matriz_sensibilidad_cmin_tabla.csv
[OK] Resumen JSON generado en: salidas/matriz_sensibilidad_resumen.json
```

### 8.2. Ejecución de la Suite de Pruebas Unitarias
```bash
python3 salidas/test_sensibilidad.py -v
```
**Salida de las pruebas:**
```
test_01_analisis_dimensional_y_unidades (__main__.TestCondicionCinematica) ... ok
test_02_extraccion_reynolds_drg (__main__.TestCondicionCinematica) ... ok
test_03_reproduccion_ejemplo_benchmark (__main__.TestCondicionCinematica) ... ok
test_04_monotonia_y_elasticidad (__main__.TestCondicionCinematica) ... ok
test_05_matriz_sensibilidad_y_derivadas (__main__.TestCondicionCinematica) ... ok
test_06_generacion_y_formato_csv (__main__.TestCondicionCinematica) ... ok
test_07_manejo_errores_entradas_invalidas (__main__.TestCondicionCinematica) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK
```
Todas las pruebas pasaron satisfactoriamente.

---

## 9. Limitaciones Físicas y Aerodinámicas

Es imprescindible señalar las limitaciones de esta formulación para evitar deducciones erróneas en el diseño del rotor:

1. **Carácter Estrictamente Cinemático y Unidimensional:**  
   La desigualdad $c \ge c_{\min}$ vincula magnitudes escalares locales ($W, c, \nu, a$). Cumplir la condición cinemática no garantiza ni valida el funcionamiento aerodinámico del rotor completo.
2. **Efectos Rotacionales Tridimensionales:**  
   En la pala real giratoria existen fuerzas centrífugas y de Coriolis que inducen un gradiente de bombeo radial en la capa límite (efecto Himmelskamp / *stall delay*), alterando la separación de flujo respecto a los ensayos estáticos en túnel 2D de UIUC.
3. **Flujo Inducido y Downwash Helicoidal:**  
   La velocidad relativa real $W$ depende del campo de velocidades inducidas (axiales y tangenciales) del vórtice helicoidal de estela. No puede fijarse $W$ puramente con la velocidad geométrica periférica $\Omega r$ sin un balance BEM convergente.
4. **Ausencia de Validación del Coeficiente de Arrastre ($C_d$):**  
   Cumplir $c \ge c_{\min}$ asegura únicamente que $Re \ge Re_{\min}$ para una velocidad $W \le M_{\lim} a$. **No valida el valor de $C_d$ si el ángulo de ataque local $\alpha$ excede el estrecho rango de ensayo** (e.g., $\alpha > 7,4^\circ$ a $Re = 61.400$), caso en el cual cualquier código aerodinámico recurrirá a extrapolaciones matemáticas sintéticas (Viterna, etc.).
5. **Región de Punta y Bajo Reynolds ($c < 8,781\text{ mm}$):**  
   Para la geometría nominal C01 ($R = 41\text{ mm}$, cubo $0,315R$), el tramo de punta entre $r/R = 0,9205$ y $1,0$ presenta cuerdas inferiores a $8,781\text{ mm}$. Para operar en esa región sin exceder $M=0,3$, el flujo se sitúa inevitablemente en $Re < 61.400$. Ni el archivo `DRG` ni `LFT` (que carece de arrastre) resuelven la polar completa en este régimen. Se requerirán ensayos complementarios o simulación numérica Navier-Stokes laminar-turbulenta de alta resolución.

---

## 10. Inventario de Entregables Generados

Todos los archivos entregables residen exclusivamente en [`salidas/`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/):

1. [`salidas/REVISION.md`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/REVISION.md): El presente informe técnico detallado de revisión.
2. [`salidas/sensibilidad_cinematica.py`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/sensibilidad_cinematica.py): Script en Python 3 para análisis cinemático, extracción de Reynolds DRG y exportación de datos.
3. [`salidas/test_sensibilidad.py`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/test_sensibilidad.py): Suite de 7 pruebas unitarias automatizadas con verificación dimensional y de consistencia.
4. [`salidas/matriz_sensibilidad_cmin.csv`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/matriz_sensibilidad_cmin.csv): Matriz completa detallada en formato tidy con derivadas analíticas.
5. [`salidas/matriz_sensibilidad_cmin_tabla.csv`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/matriz_sensibilidad_cmin_tabla.csv): Matriz pivoteada de consulta rápida para $c_{\min}\text{ [mm]}$.
6. [`salidas/matriz_sensibilidad_resumen.json`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_polar/salidas/matriz_sensibilidad_resumen.json): Registro serializado de metadatos, parámetros y validación de benchmark.
