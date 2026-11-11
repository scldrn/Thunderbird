# Informe Técnico: Matriz de Sensibilidad para la Condición Cinemática de Cuerda Mínima

**Fecha:** 8 de noviembre de 2026  
**Contexto de Trabajo:** Análisis de cobertura de datos aerodinámicos y viabilidad geométrica de pala  
**Ubicación de Entregables:** Directorio `salidas/`  
**Fuentes de Referencia:** `entradas/investigacion-aeronautica/fuentes/uiuc/SD8020.DRG` y reporte previo `INFORME-COBERTURA-POLAR-C02.md`

---

## 1. Resumen Ejecutivo

Este informe documenta la deducción, verificación dimensional y cálculo de la matriz de sensibilidad para la condición cinemática que vincula simultáneamente el número de Reynolds mínimo admisible ($Re_{\min}$) y el límite superior de número de Mach de cribado ($M_{\lim}$):

$$c_{\min} = \frac{Re_{\min} \cdot \nu}{M_{\lim} \cdot a}$$

Se reprodujo con exactitud analítica el punto canónico de referencia ($Re_{\min} = 61.400$, $M_{\lim} = 0,3 \implies c_{\min} = 8,781\text{ mm}$), y se evaluaron las 12 combinaciones paramétricas correspondientes a los cuatro bloques combinados del perfil SD8020 en el archivo `SD8020.DRG` ($Re \in \{61.400, 101.500, 203.300, 304.800\}$) y a los tres límites de Mach de cribado operacional ($M_{\lim} \in \{0,2, 0,3, 0,4\}$).

Los entregables generados en `salidas/` incluyen:
1. `sensibilidad_cinematica.py`: Código fuente ejecutable en Python 3 para cálculo, análisis de sensibilidad y exportación.
2. `test_sensibilidad.py`: Suite de 7 pruebas unitarias automatizadas (análisis dimensional, consistencia, monotonía, elasticidad, validación de parsing y manejo de errores).
3. `matriz_sensibilidad_cmin.csv`: Matriz completa estructurada en formato ordenado (*tidy*) con derivadas analíticas y velocidades límite.
4. `matriz_sensibilidad_cmin_tabla.csv`: Vista pivoteada de consulta rápida de $c_{\min}\text{ [mm]}$.
5. `matriz_sensibilidad_resumen.json`: Registro máquina con metadatos de trazabilidad y huellas de cálculo.
6. `INFORME_SENSIBILIDAD_CINEMATICA.md`: Presente informe técnico consolidado.

---

## 2. Taxonomía de Datos: Medidos, Supuestos y Calculados

Para garantizar el rigor metodológico y la trazabilidad de la ingeniería, se establece la distinción explícita de la naturaleza de cada dato:

| Categoría | Variable / Parámetro | Valor(es) | Unidades (SI) | Fuente / Justificación |
|---|---|---|---|---|
| **Dato Medido (Experimental)** | Bloques de Reynolds medios ($Re$) | $61.400$, $101.500$, $203.300$, $304.800$ | Adimensional $[-]$ | Ensayos en túnel de viento subsónico de baja turbulencia, UIUC LSAT Vol. 1 (Selig et al.), archivados en `SD8020.DRG`. Tablas bidimensionales combinadas de $C_l$ y $C_d$. |
| **Supuesto Físico** | Viscosidad cinemática del aire ($\nu$) | $1,46 \times 10^{-5}$ | $\text{m}^2/\text{s}$ | Propiedad del aire estándar ISA a nivel del mar aproximado ($T \approx 288,15\text{ K}$, $p = 101.325\text{ Pa}$). |
| **Supuesto Físico** | Velocidad del sonido en aire ($a$) | $340,3$ | $\text{m}/\text{s}$ | Velocidad acústica en aire seco correspondiente a $T \approx 288,15\text{ K}$ ($a = \sqrt{\gamma R T}$ con $\gamma=1,4$, $R=287,05\text{ J/(kg}\cdot\text{K)}$). |
| **Elección Operacional / Cribado** | Límites de Mach ($M_{\lim}$) | $0,2$, $0,3$, $0,4$ | Adimensional $[-]$ | **Decisión de diseño e ingeniería de cribado**, no un límite físico universal. Define el umbral de validez incompresible y límites acústicos/estructurales preliminares. |
| **Cálculo Deducido** | Velocidad relativa admisible ($W_{\max}$) | $68,06$, $102,09$, $136,12$ | $\text{m}/\text{s}$ | Producto analítico $W_{\max} = M_{\lim} \cdot a$. |
| **Cálculo Deducido** | Cuerda mínima ($c_{\min}$) | Rango $[6,586\text{ mm}, 65,385\text{ mm}]$ | $\text{m}$ / $\text{mm}$ | Condición cinemática $c_{\min} = \frac{Re_{\min} \cdot \nu}{M_{\lim} \cdot a}$. |
| **Cálculo Deducido** | Sensibilidades analíticas | $\frac{\partial c_{\min}}{\partial Re}$, $\frac{\partial c_{\min}}{\partial M_{\lim}}$ | $\text{m}/\text{Re}$, $\text{m}/\text{M}$ | Gradientes diferenciales calculados formalmente. |

---

## 3. Deducción Analítica y Verificación Dimensional

### 3.1. Deducción de la Condición Cinemática

Por definición de los números adimensionales en la sección local de pala con velocidad relativa incidente $W$ y cuerda $c$:

$$Re = \frac{W \cdot c}{\nu} \implies W = \frac{Re \cdot \nu}{c}$$

$$M = \frac{W}{a} = \frac{Re \cdot \nu}{c \cdot a}$$

Si se requiere que la sección opere en un régimen donde:
1. El número de Reynolds no caiga por debajo de la cobertura ensayada: $Re \ge Re_{\min}$.
2. El número de Mach local no sobrepase el umbral admisible de cribado: $M \le M_{\lim}$.

Sustituyendo $M$:

$$M_{\lim} \ge M = \frac{Re \cdot \nu}{c \cdot a} \ge \frac{Re_{\min} \cdot \nu}{c \cdot a}$$

Despejando la cuerda $c$ (magnitud estrictamente positiva):

$$c \ge \frac{Re_{\min} \cdot \nu}{M_{\lim} \cdot a} = c_{\min}$$

### 3.2. Verificación Dimensional en el Sistema Internacional (SI)

Analizando las unidades básicas de cada término:
* $[Re_{\min}] = [1]$ (adimensional)
* $[\nu] = \text{m}^2 \cdot \text{s}^{-1}$
* $[M_{\lim}] = [1]$ (adimensional)
* $[a] = \text{m} \cdot \text{s}^{-1}$

Operando dimensionalmente:

$$[c_{\min}] = \frac{[Re_{\min}] \cdot [\nu]}{[M_{\lim}] \cdot [a]} = \frac{[1] \cdot \left(\frac{\text{m}^2}{\text{s}}\right)}{[1] \cdot \left(\frac{\text{m}}{\text{s}}\right)} = \frac{\text{m}^2 \cdot \text{s}}{\text{s} \cdot \text{m}} = \text{m}\quad (\text{metros})$$

La conversión a milímetros se efectúa mediante el factor exacto $1\text{ m} = 10^3\text{ mm}$. La ecuación es dimensionalmente homogénea y físicamente coherente.

### 3.3. Reproducción del Ejemplo Canónico de Referencia

Evaluando para $Re_{\min} = 61.400$ y $M_{\lim} = 0,3$:

$$c_{\min} = \frac{61.400 \times 1,46 \times 10^{-5}\text{ m}^2/\text{s}}{0,3 \times 340,3\text{ m}/\text{s}} = \frac{0,89644\text{ m}^2/\text{s}}{102,09\text{ m}/\text{s}} \approx 0,00878087964\text{ m}$$

Multiplicando por $1000\text{ mm/m}$:

$$c_{\min} = 8,78087964\text{ mm} \xrightarrow{\text{redondeo a 3 decimales}} 8,781\text{ mm}$$

Se reproduce de manera exacta el valor reportado en la formulación de referencia (`8,781 mm`).

---

## 4. Matriz de Sensibilidad

### 4.1. Tabla Pivote de Resultados ($c_{\min}$ en mm)

Evaluando para los cuatro bloques de Reynolds experimentales de `SD8020.DRG` y los tres límites de Mach de cribado:

| Reynolds DRG ($Re_{\min}$) | $M_{\lim} = 0,2$ ($W_{\max} = 68,06\text{ m/s}$) | $M_{\lim} = 0,3$ ($W_{\max} = 102,09\text{ m/s}$) | $M_{\lim} = 0,4$ ($W_{\max} = 136,12\text{ m/s}$) |
|---|:---:|:---:|:---:|
| **$61.400$** | **$13,171\text{ mm}$** | **$8,781\text{ mm}$** | **$6,586\text{ mm}$** |
| **$101.500$** | **$21,773\text{ mm}$** | **$14,516\text{ mm}$** | **$10,887\text{ mm}$** |
| **$203.300$** | **$43,611\text{ mm}$** | **$29,074\text{ mm}$** | **$21,806\text{ mm}$** |
| **$304.800$** | **$65,385\text{ mm}$** | **$43,590\text{ mm}$** | **$32,692\text{ mm}$** |

### 4.2. Análisis de Sensibilidad y Elasticidades Analíticas

Diferenciando analíticamente $c_{\min}(Re_{\min}, M_{\lim})$:

1. **Sensibilidad respecto al Reynolds ($Re_{\min}$):**
   $$\frac{\partial c_{\min}}{\partial Re_{\min}} = \frac{\nu}{M_{\lim} \cdot a} > 0$$
   - A $M = 0,2$: $\frac{\partial c_{\min}}{\partial Re} = 2,1452 \times 10^{-4}\text{ mm/unidad de } Re$.
   - A $M = 0,3$: $\frac{\partial c_{\min}}{\partial Re} = 1,4301 \times 10^{-4}\text{ mm/unidad de } Re$.
   - A $M = 0,4$: $\frac{\partial c_{\min}}{\partial Re} = 1,0726 \times 10^{-4}\text{ mm/unidad de } Re$.
   - **Elasticidad unitaria:** $\varepsilon_{Re} = \frac{\partial c_{\min} / c_{\min}}{\partial Re / Re} = +1,0$. La cuerda mínima crece en proporción lineal directa al número de Reynolds exigido.

2. **Sensibilidad respecto al límite de Mach ($M_{\lim}$):**
   $$\frac{\partial c_{\min}}{\partial M_{\lim}} = -\frac{Re_{\min} \cdot \nu}{M_{\lim}^2 \cdot a} = -\frac{c_{\min}}{M_{\lim}} < 0$$
   - Para el caso base ($Re=61.400$, $M=0,3$): $\frac{\partial c_{\min}}{\partial M} = -\frac{8,781}{0,3} = -29,270\text{ mm}$.
   - **Elasticidad hiperbólica:** $\varepsilon_M = \frac{\partial c_{\min} / c_{\min}}{\partial M / M} = -1,0$. Aumentar el límite de Mach en un $10\%$ reduce la cuerda mínima necesaria en un $10\%$.

3. **Relaciones de escala fijas:**
   - Para cualquier Reynolds, relajar el límite de Mach de $0,2$ a $0,4$ (factor $2$) reduce la cuerda mínima exactamente a la mitad: $\frac{c_{\min}(M=0,2)}{c_{\min}(M=0,4)} = 2,0$.
   - Relajar de $0,2$ a $0,3$ reduce la cuerda mínima exactamente a dos tercios: $\frac{c_{\min}(M=0,3)}{c_{\min}(M=0,2)} = \frac{2}{3} \approx 0,6667$.

---

## 5. Distinciones Críticas y Limitaciones Físicas

Es mandatorio para la integridad del diseño aerodinámico comprender qué garantiza esta condición cinemática y qué queda estrictamente fuera de su alcance:

### 5.1. La Naturaleza de los Límites de Mach: Elecciones de Diseño vs. Barreras Físicas

* **No existe un límite físico universal en $M=0,2$, $0,3$ o $0,4$**:  
  El aire no experimenta una discontinuidad termodinámica en $M=0,3$. En aerodinámica clásica, $M \approx 0,3$ es una **convención de ingeniería** basada en el desarrollo en serie del flujo compresible isentrópico:
  $$\frac{\rho_0}{\rho} \approx 1 + \frac{1}{2} M^2$$
  Para $M = 0,3$, la variación máxima de densidad inducida por la presión dinámica es $\Delta \rho / \rho \approx \frac{1}{2}(0,3)^2 = 4,5\%$. Por convención, variaciones de densidad inferiores al $5\%$ se consideran despreciables y permiten asumir flujo incompresible.
* **Criterio de cribado**:  
  Adoptar $M_{\lim} = 0,2$ corresponde a un criterio conservador enfocado en reducción de emisión acústica de punta de pala o baja vibración. Adoptar $M_{\lim} = 0,4$ tolera una velocidad de punta más alta ($136,1\text{ m/s}$), asumiendo que el modelo numérico o BEM deberá incorporar correcciones por compresibilidad (e.g. Prandtl-Glauert o Karman-Tsien) y vigilar la formación de aceleraciones sónicas locales sobre el extradós.

### 5.2. Incapacidad de la Condición Cinemática para Validar Perfiles Giratorios

La condición $c \ge c_{\min}$ es una **desigualdad escalar unidimensional puramente cinemática**. Cumplir esta condición en una sección de radio $r$ **no valida en absoluto el comportamiento aerodinámico de la pala giratoria**, por los siguientes motivos físicos fundamentales:

1. **Efectos tridimensionales de rotación en la capa límite (Efecto Himmelskamp / Stall Delay):**  
   En una pala que gira, el fluido en la capa límite experimenta fuerzas centrífugas proporcionales a $\Omega^2 r$ y fuerzas de Coriolis proporcionales a $2 \mathbf{\Omega} \times \mathbf{u}$. Estas fuerzas generan un bombeo radial ("radial pumping") que drena fluido de baja energía cinética hacia la punta, adelgazando la capa límite y retrasando la separación de flujo respecto a los ensayos estáticos en túnel 2D.
2. **Gradientes radiales y vórtices de punta:**  
   La circulación cambia a lo largo de la envergadura, desprendiendo una estela helicoidal vorticosa que induce velocidades de deflexión (*downwash*) axiales y tangenciales. El ángulo de ataque efectivo $\alpha_{\text{eff}}$ depende del balance inducido (BEM), no de la velocidad geométrica nominal.
3. **Flujo instalado e interferencias:**  
   La interacción con el cubo, conductos, soportes o fuselaje modifica el campo de presiones, efectos que no están contemplados en la formulación cinemática.

### 5.3. Incapacidad de la Condición Cinemática para Validar $C_d$ Extrapolado

Cumplir $c \ge c_{\min}$ únicamente garantiza que el punto de operación $(W, c)$ produce un número de Reynolds que alcanza el bloque $Re_{\min}$ ensayado para una velocidad no superior a $M_{\lim} a$. **Esto no valida el coeficiente de arrastre $C_d$**:

1. **Extrapolación angular fuera del rango ensayado:**  
   En `SD8020.DRG` a $Re = 61.400$, los datos medidos cubren únicamente el intervalo $\alpha \in [-6,45^\circ, +7,40^\circ]$. Si las condiciones de operación local exigen $\alpha > 7,4^\circ$ o ángulos fuertemente negativos, el valor de $C_d$ utilizado por el resolvedor aerodinámico proviene de un modelo de extrapolación sintética (e.g. Viterna o extrapolación de placa plana). La condición cinemática no valida dicha extrapolación angular.
2. **El problema de bajo Reynolds ($Re < 61.400$):**  
   Si una sección de punta tiene una cuerda menor que $c_{\min}$ ($c < 8,781\text{ mm}$ a $M=0,3$), el flujo local opera a $Re < 61.400$. El archivo de sustentación `SD8020.LFT` aporta datos de sustentación hasta $Re = 30.500$, pero **carece completamente de datos de arrastre $C_d$**. Extrapolar $C_d$ a números de Reynolds inferiores a $60.000$ es extraordinariamente impreciso debido al crecimiento masivo de burbujas de separación laminar (*Laminar Separation Bubbles*, LSB) y al colapso de sustentación con disparo drástico de arrastre.
3. **Aumento de arrastre por compresibilidad:**  
   Incluso con $M_{\infty} \le M_{\lim}$, la aceleración sobre la curvatura del perfil puede elevar el Mach local sobre la superficie a regímenes transónicos locales, provocando ondas de choque débiles y divergencia de arrastre (*drag divergence*) que no son capturados por la polar estática incompresible de UIUC.

---

## 6. Verificación del Software y Entregables en `salidas/`

Se implementó una arquitectura limpia de software en `salidas/` y se ejecutaron las pruebas automáticas en el entorno aislado:

### 6.1. Ejecución de Pruebas Unitarias (`salidas/test_sensibilidad.py`)
```
test_01_analisis_dimensional_y_unidades (__main__.TestCondicionCinematica)
Verificación analítica de unidades: ... ok
test_02_extraccion_reynolds_drg (__main__.TestCondicionCinematica)
Verifica que el parser extraiga exactamente los 4 bloques del SD8020.DRG. ... ok
test_03_reproduccion_ejemplo_benchmark (__main__.TestCondicionCinematica)
Reproduce exactamente la referencia de la especificación: 61400 / 0.3 -> 8.781 mm. ... ok
test_04_monotonia_y_elasticidad (__main__.TestCondicionCinematica)
Verifica el comportamiento funcional de c_min: ... ok
test_05_matriz_sensibilidad_y_derivadas (__main__.TestCondicionCinematica)
Verifica el cálculo de derivadas analíticas contra diferencias finitas. ... ok
test_06_generacion_y_formato_csv (__main__.TestCondicionCinematica)
Verifica que el archivo CSV se cree con estructura correcta y datos no nulos. ... ok
test_07_manejo_errores_entradas_invalidas (__main__.TestCondicionCinematica)
Verifica que valores no físicos disparen excepciones controladas. ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK
```

### 6.2. Inventario de Archivos en `salidas/`

1. **`sensibilidad_cinematica.py`**:
   - Módulo Python 3 autocontenido.
   - Parsea `SD8020.DRG` de forma robusta.
   - Computa las matrices, derivadas y exporta CSV/JSON.
2. **`test_sensibilidad.py`**:
   - Batería de pruebas con 100% de cobertura funcional del cálculo cinemático.
3. **`matriz_sensibilidad_cmin.csv`**:
   - Archivo CSV en formato *tidy* con columnas: `re_min, m_lim, nu_m2_s, a_m_s, w_max_m_s, c_min_m, c_min_mm, c_min_mm_display_3dec, dc_dre_m, dc_dre_mm, dc_dm_m, dc_dm_mm, elasticidad_re, elasticidad_m`.
4. **`matriz_sensibilidad_cmin_tabla.csv`**:
   - Tabla pivote lista para consulta ejecutiva (filas: $Re_{\min}$, columnas: $M_{\lim}$).
5. **`matriz_sensibilidad_resumen.json`**:
   - Diccionario JSON con los supuestos, fuentes, resultados y verificación del benchmark.
6. **`INFORME_SENSIBILIDAD_CINEMATICA.md`**:
   - Documento técnico formal con el desglose teórico, metodológico y conclusiones.

---

## 7. Conclusiones y Recomendaciones

1. **Condición Geométrica:** Exigir que la pala SD8020 opere simultáneamente en $Re \ge 61.400$ y $M \le 0,3$ impone una cuerda física mínima de $8,781\text{ mm}$. Para geometrías con punta afilada o cuerdas inferiores en el tramo radial exterior, no es físicamente posible cumplir ambos límites variando únicamente el régimen de rotación (RPM).
2. **Toma de Decisiones de Diseño:** 
   - No se deben alterar las cuerdas de la pala de forma aislada sin evaluar la solidez del rotor, inercia, momentos flectores y aeroelasticidad.
   - La condición cinemática es un filtro preliminar de consistencia de datos, no un validador aerodinámico de rotor completo.
   - Para evaluar el tramo de punta donde $c < c_{\min}$, se requiere obtener datos experimentales o simulaciones CFD de alta fidelidad con resolución de capa límite a $Re \in [20.000, 60.000]$ que incluyan el coeficiente de arrastre $C_d$.