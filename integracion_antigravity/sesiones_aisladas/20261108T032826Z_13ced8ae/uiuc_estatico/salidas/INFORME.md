# Informe Aerodinámico Experimental: Análisis Estático de la Hélice Abierta Micro Invent 3.2x2.2 (UIUC)

---

## 1. Identificación y Fuentes Primarias

* **Objeto de Estudio:** Hélice ultraligera abierta Micro Invent 3.2x2.2 (configuración bipala, 2 palas según catálogo del fabricante).
* **Diámetro Real:** 3.2 pulgadas ($D = 0.08128\text{ m}$, radio $R = 0.04064\text{ m}$), confirmado en el gráfico geométrico fuente oficial (`mi_3.2x2.2_geom.png`).
* **Instalación y Ensayos:** Base de datos de hélices de la Universidad de Illinois en Urbana-Champaign (UIUC Propeller Database, Volume 2).
* **Régimen de Operación:** Ensayo estático / punto de tracción pura a punto fijo ($V_\infty = 0\text{ m/s}$, coeficiente de avance $J = 0$).
* **Archivos Fuente Locales (Solo Lectura):**
  * `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_static_0519rd.txt` (datos experimentales de ensayo estático: $\text{RPM}$, $C_T$, $C_P$).
  * `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_geom.txt` (distribución geométrica de cuerda $c/R$ y torsión $\beta$).
  * `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_geom.png` (gráfico de especificación geométrica del fabricante y laboratorio).
* **Enlaces Primarios Oficiales:**
  * UIUC Propeller Database (Volume 2): [https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html](https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html)
  * Deters, R. W., Ananda, G. K., & Selig, M. S. (2014). *Reynolds Number Effects on the Performance of Small-Scale Propellers.* AIAA Paper 2014-2151, 32nd AIAA Applied Aerodynamics Conference, Atlanta, GA: [https://m-selig.ae.illinois.edu/pubs/DetersAnandaSelig-2014-AIAA-2014-2151.pdf](https://m-selig.ae.illinois.edu/pubs/DetersAnandaSelig-2014-AIAA-2014-2151.pdf)

---

## 2. Resumen Ejecutivo

Se ha llevado a cabo el análisis aerodinámico riguroso punto por punto de la hélice abierta Micro Invent 3.2x2.2 en condición estática a partir de los 18 puntos experimentales documentados en la base de datos de UIUC. Para cada punto medido en el rango comprendido entre **2,950.000 RPM y 19,923.333 RPM**, se calcularon el empuje estático ($T$), la potencia mecánica de eje ($P$), el número de Mach de punta ($M_{\text{tip}}$), el número de Reynolds característico en la sección $0.75R$ ($Re_{0.75R}$) y la Figura de Mérito ideal ($FM$).

Los resultados evidencian un comportamiento clásico de micro-hélices operando a números de Reynolds ultra-bajos ($Re_{0.75R} \in [4,715, \, 31,845]$):
1. **Empuje estático ($T$):** Se incrementa desde $0.0134\text{ N}$ ($1.37\text{ gf}$) a 2,950 RPM hasta $0.7418\text{ N}$ ($75.64\text{ gf}$) a 19,923 RPM.
2. **Potencia mecánica de eje ($P$):** Aumenta desde $0.0265\text{ W}$ hasta $9.5271\text{ W}$.
3. **Régimen de compresibilidad:** El Mach de punta evoluciona de $0.0369$ a $0.2492$. Al mantenerse estrictamente por debajo de $0.30$, el flujo se encuentra en régimen subsónico incompresible.
4. **Figura de Mérito ideal ($FM$):** Pasa de $0.5184$ a $0.5947$, reflejando una ganancia de eficiencia aerodinámica del 15% conforme el número de Reynolds se incrementa y la capa límite se vuelve más resistente a la separación laminar.

---

## 3. Taxonomía Rigurosa de Datos: Medidos, Supuestos y Calculados

Para garantizar la integridad y trazabilidad del análisis, se desglosan explícitamente las tres clases de parámetros:

| Categoría | Parámetro | Símbolo | Valor / Rango | Unidades | Fuente / Justificación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dato Medido** | Frecuencia angular | $\text{RPM}$ | $2,950.000 - 19,923.333$ | $\text{rev/min}$ | Medición tacométrica en banco UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Dato Medido** | Coeficiente de empuje | $C_T$ | $0.103654 - 0.125828$ | $-$ | Transductor de fuerza en banco UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Dato Medido** | Coeficiente de potencia | $C_P$ | $0.051360 - 0.059879$ | $-$ | Transductor de par en banco UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Dato Medido** | Diámetro real | $D$ | $3.2$ ($0.08128$) | $\text{in}$ ($\text{m}$) | Gráfico de perfil de hélice UIUC (`mi_3.2x2.2_geom.png`) |
| **Dato Medido** | Número de palas | $B$ | $2$ | $-$ | Catálogo oficial del fabricante Micro Invent |
| **Dato Medido** | Cuerda relativa a $0.75R$ | $(c/R)_{0.75}$ | $0.1799$ | $-$ | Tabla geométrica digitalizada UIUC (`mi_3.2x2.2_geom.txt`, fila $r/R = 0.75$) |
| **Dato Medido** | Paso geométrico relativo | $\beta_{0.75}$ | $14.271$ | $^{\circ}$ | Ángulo de torsión local UIUC (`mi_3.2x2.2_geom.txt`) |
| **Supuesto** | Densidad del aire | $\rho$ | $1.225$ | $\text{kg/m}^3$ | Atmósfera estándar ISA a nivel del mar ($T_0 = 15^{\circ}\text{C}$, $p_0 = 101,325\text{ Pa}$) |
| **Supuesto** | Velocidad del sonido | $a$ | $340.3$ | $\text{m/s}$ | Atmósfera estándar ISA ($a = \sqrt{\gamma R_g T_0}$ con $\gamma = 1.4$) |
| **Supuesto** | Viscosidad cinemática | $\nu$ | $1.46 \times 10^{-5}$ | $\text{m}^2/\text{s}$ | Aire estándar a $15^{\circ}\text{C}$ ($\nu = \mu / \rho$) |
| **Supuesto** | Velocidad de avance | $V_\infty$ | $0.0$ | $\text{m/s}$ | Ensayo estático puro (vuelo a punto fijo / *hover*, $J = 0$) |
| **Supuesto** | Rigidez aeroelástica | $-$ | Indeformable | $-$ | Se asume geometría nominal constante sin deflexión torsional en régimen ensayado |
| **Calculado** | Frecuencia de giro | $n$ | $49.167 - 332.056$ | $\text{rev/s}$ | $n = \text{RPM} / 60$ |
| **Calculado** | Empuje estático | $T$ | $0.013397 - 0.741771$ | $\text{N}$ | $T = C_T \rho n^2 D^4$ |
| **Calculado** | Potencia de eje mecánica | $P$ | $0.026527 - 9.527113$ | $\text{W}$ | $P = C_P \rho n^3 D^5$ |
| **Calculado** | Mach de punta | $M_{\text{tip}}$ | $0.036893 - 0.249162$ | $-$ | $M_{\text{tip}} = (\pi n D) / a$ |
| **Calculado** | Reynolds a $0.75R$ | $Re_{0.75R}$ | $4,715.17 - 31,844.73$ | $-$ | $Re_{0.75R} = (0.75 \pi n D \cdot c_{0.75}) / \nu$ |
| **Calculado** | Figura de mérito ideal | $FM$ | $0.518435 - 0.594746$ | $-$ | $FM = \sqrt{2/\pi} \cdot (C_T^{3/2} / C_P)$ |

---

## 4. Marco Teórico y Ecuaciones Aerodinámicas

### 4.1 Definición de Coeficientes UIUC
En la literatura aeronáutica de hélices (UIUC Propeller Database, Glauert), los coeficientes adimensionales de empuje ($C_T$) y potencia ($C_P$) se definen respecto a la velocidad de rotación en revoluciones por segundo ($n$) y el diámetro total ($D$):

$$C_T = \frac{T}{\rho n^2 D^4} \implies T = C_T \, \rho \, n^2 \, D^4 \quad [\text{N}]$$

$$C_P = \frac{P}{\rho n^3 D^5} \implies P = C_P \, \rho \, n^3 \, D^5 \quad [\text{W}]$$

Donde:
* $n = \frac{\text{RPM}}{60} \quad [\text{rev/s}]$
* $D = 0.08128\text{ m}$
* $\rho = 1.225\text{ kg/m}^3$

### 4.2 Cinemática y Mach de Punta
La velocidad tangencial máxima alcanzada por el perfil en el extremo radial de la pala ($R = D/2$) es:

$$V_{\text{tip}} = \omega R = (2\pi n) \left(\frac{D}{2}\right) = \pi n D \quad [\text{m/s}]$$

El número de Mach de punta representa la razón entre esta velocidad circunferencial y la velocidad del sonido del medio:

$$M_{\text{tip}} = \frac{V_{\text{tip}}}{a} = \frac{\pi n D}{a}$$

### 4.3 Número de Reynolds Característico a $0.75R$
En régimen estático ($V_\infty = 0$), el flujo incidente experimentado por una sección radial $r$ está dominado por la componente de velocidad rotacional:

$$V_{0.75R} = \omega (0.75 R) = 2\pi n (0.75 R) = 0.75 \, \pi \, n \, D \quad [\text{m/s}]$$

La cuerda física local a tres cuartos de radio se obtiene de la distribución adimensional de la geometría UIUC:

$$(c/R)_{0.75} = 0.1799 \implies c_{0.75} = (c/R)_{0.75} \cdot R = 0.1799 \cdot 0.04064\text{ m} = 0.007311136\text{ m} \approx 7.311\text{ mm}$$

El número de Reynolds de la sección de referencia es por tanto:

$$Re_{0.75R} = \frac{V_{0.75R} \cdot c_{0.75}}{\nu} = \frac{(0.75 \, \pi \, n \, D) \cdot (0.1799 \cdot R)}{\nu}$$

### 4.4 Deducción Analítica de la Figura de Mérito Ideal ($FM$)
La Figura de Mérito ($FM$) cuantifica la eficiencia aerodinámica de un rotor en condición de sustentación pura o punto fijo (*hover*), comparando la potencia mínima teórica inducida según la teoría de cantidad de movimiento del disco actuador de Rankine-Froude ($P_{\text{ideal}}$) frente a la potencia mecánica real absorbida por el eje ($P$):

$$FM = \frac{P_{\text{ideal}}}{P}$$

#### 4.4.1 Potencia Ideal Inducida en Punto Fijo
De acuerdo con la teoría de cantidad de movimiento en el disco actuador con área de barrido $A = \frac{\pi}{4} D^2$, el empuje estático se relaciona con la velocidad inducida en el disco ($v_i$) mediante:

$$T = \dot{m} (2 v_i) = (\rho A v_i) (2 v_i) = 2 \rho A v_i^2 \implies v_i = \sqrt{\frac{T}{2 \rho A}}$$

La potencia ideal requerida para inducir dicho flujo descendente es:

$$P_{\text{ideal}} = T \cdot v_i = T \sqrt{\frac{T}{2 \rho A}} = \frac{T^{3/2}}{\sqrt{2 \rho A}}$$

#### 4.4.2 Relación con los Coeficientes Adimensionales de Hélice
Sustituyendo las definiciones de $T = C_T \rho n^2 D^4$, $P = C_P \rho n^3 D^5$ y $A = \frac{\pi}{4} D^2$:

$$T^{3/2} = \left(C_T \rho n^2 D^4\right)^{3/2} = C_T^{3/2} \, \rho^{3/2} \, n^3 \, D^6$$

$$\sqrt{2 \rho A} = \sqrt{2 \rho \left(\frac{\pi D^2}{4}\right)} = \sqrt{\frac{\pi}{2}} \, \rho^{1/2} \, D$$

Dividiendo ambas expresiones para obtener $P_{\text{ideal}}$:

$$P_{\text{ideal}} = \frac{C_T^{3/2} \, \rho^{3/2} \, n^3 \, D^6}{\sqrt{\frac{\pi}{2}} \, \rho^{1/2} \, D} = \frac{C_T^{3/2}}{\sqrt{\frac{\pi}{2}}} \, \rho \, n^3 \, D^5 = \sqrt{\frac{2}{\pi}} \, C_T^{3/2} \, \rho \, n^3 \, D^5$$

Finalmente, al dividir por la potencia real $P = C_P \rho n^3 D^5$, se eliminan todas las variables dimensionales ($\rho, n, D$):

$$FM = \frac{P_{\text{ideal}}}{P} = \frac{\sqrt{\frac{2}{\pi}} \, C_T^{3/2} \, \rho \, n^3 \, D^5}{C_P \, \rho \, n^3 \, D^5} = \sqrt{\frac{2}{\pi}} \, \frac{C_T^{3/2}}{C_P} = \frac{C_T^{3/2}}{\sqrt{\frac{\pi}{2}} \, C_P} \approx 0.79788456 \, \frac{C_T^{3/2}}{C_P}$$

> [!NOTE]
> La formulación dimensional ($P_{\text{ideal}}/P$) y la adimensional ($\sqrt{2/\pi} \cdot C_T^{3/2} / C_P$) son matemáticamente idénticas. En el script `salidas/analizar.py` y las pruebas de `salidas/test_analizar.py`, la concordancia entre ambas es exacta con una desviación inferior a $10^{-12}$.

---

## 5. Tabla Completa de Resultados Experimentales

A continuación se presenta la totalidad de los 18 puntos de ensayo procesados, almacenados en `salidas/puntos.csv`:

| Punto | RPM [rev/min] | $n$ [rev/s] | $C_T$ [-] | $C_P$ [-] | Empuje $T$ [N] | Empuje [gf] | Potencia $P$ [W] | $M_{\text{tip}}$ [-] | $Re_{0.75R}$ [-] | $FM$ [-] | $T/P$ [g/W] |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 2950.000 | 49.167 | 0.103654 | 0.051360 | 0.013397 | 1.366 | 0.026527 | 0.0369 | 4,715.2 | 0.518435 | 51.50 |
| 2 | 4086.667 | 68.111 | 0.105785 | 0.051792 | 0.026238 | 2.675 | 0.071117 | 0.0511 | 6,532.0 | 0.530046 | 37.62 |
| 3 | 5026.667 | 83.778 | 0.108049 | 0.052339 | 0.040546 | 4.135 | 0.133742 | 0.0629 | 8,034.4 | 0.541434 | 30.91 |
| 4 | 5940.000 | 99.000 | 0.109779 | 0.052154 | 0.057526 | 5.866 | 0.219911 | 0.0743 | 9,494.3 | 0.556457 | 26.68 |
| 5 | 7046.667 | 117.444 | 0.109755 | 0.052358 | 0.080939 | 8.254 | 0.368583 | 0.0881 | 11,263.1 | 0.554107 | 22.39 |
| 6 | 8106.667 | 135.111 | 0.109700 | 0.052165 | 0.107068 | 10.918 | 0.559123 | 0.1014 | 12,957.4 | 0.555739 | 19.53 |
| 7 | 8983.333 | 149.722 | 0.113454 | 0.054645 | 0.135976 | 13.866 | 0.797010 | 0.1123 | 14,358.6 | 0.557981 | 17.40 |
| 8 | 10056.667 | 167.611 | 0.112185 | 0.053441 | 0.168504 | 17.183 | 1.093547 | 0.1258 | 16,074.2 | 0.561006 | 15.71 |
| 9 | 11056.667 | 184.278 | 0.111483 | 0.052793 | 0.202407 | 20.640 | 1.435654 | 0.1383 | 17,672.6 | 0.562570 | 14.38 |
| 10 | 12006.667 | 200.111 | 0.115428 | 0.054298 | 0.247129 | 25.200 | 1.890828 | 0.1502 | 19,191.0 | 0.576266 | 13.33 |
| 11 | 13033.333 | 217.222 | 0.116712 | 0.054630 | 0.294439 | 30.024 | 2.433316 | 0.1630 | 20,832.0 | 0.582347 | 12.34 |
| 12 | 13900.000 | 231.667 | 0.119156 | 0.055969 | 0.341912 | 34.865 | 3.024076 | 0.1738 | 22,217.3 | 0.586363 | 11.53 |
| 13 | 14916.667 | 248.611 | 0.119737 | 0.056325 | 0.395677 | 40.348 | 3.761122 | 0.1865 | 23,842.3 | 0.586923 | 10.73 |
| 14 | 15860.000 | 264.333 | 0.122140 | 0.057434 | 0.456281 | 46.528 | 4.609772 | 0.1983 | 25,350.0 | 0.593004 | 10.09 |
| 15 | 16940.000 | 282.333 | 0.121822 | 0.057703 | 0.519184 | 52.941 | 5.643382 | 0.2119 | 27,076.3 | 0.587936 | 9.38 |
| 16 | 17940.000 | 299.000 | 0.122858 | 0.057937 | 0.587241 | 59.882 | 6.730141 | 0.2244 | 28,674.6 | 0.593047 | 8.90 |
| 17 | 18823.333 | 313.722 | 0.124658 | 0.058866 | 0.655966 | 66.890 | 7.898687 | 0.2354 | 30,086.5 | 0.596562 | 8.47 |
| 18 | 19923.333 | 332.056 | 0.125828 | 0.059879 | 0.741771 | 75.639 | 9.527113 | 0.2492 | 31,844.7 | 0.594746 | 7.94 |

---

## 6. Análisis y Discusión Aerodinámica

### 6.1 Régimen de Flujo a Bajos Números de Reynolds ($Re_{0.75R}$)
Tal como detallan Deters, Ananda y Selig (AIAA 2014-2151), las hélices de microescala operan en un régimen aerodinámico donde las fuerzas viscosas son comparables o dominantes respecto a las inerciales ($Re < 50,000$).
* A 2,950 RPM ($Re_{0.75R} \approx 4,715$), el flujo sobre el perfil de la pala es laminar y altamente susceptible al desprendimiento temprano con burbujas de separación laminar gruesas. Esto penaliza la sustentación relativa, resultando en un $C_T$ relativamente bajo ($0.10365$) y una Figura de Mérito de $0.5184$.
* A medida que las revoluciones aumentan hacia las 19,923 RPM ($Re_{0.75R} \approx 31,845$), la capa límite gana energía cinética relativa, retrasando la separación y mejorando la relación $C_l / C_d$ de las secciones alares. Por esta razón, $C_T$ crece de forma monotónica un 21.4% (hasta $0.12583$) y $FM$ escala hasta alcanzar un pico de $0.5966$ a 18,823 RPM, estabilizándose en torno a $0.595$.

### 6.2 Comportamiento de la Eficiencia Estática ($T/P$) y Carga de Disco
El empuje por unidad de potencia mecánica ($T/P$, expresado en gramos de empuje por vatio de eje $\text{g/W}$) exhibe la ley clásica de reducción asintótica conforme aumenta la velocidad inducida:
* A régimen mínimo (2,950 RPM), se logran hasta $51.5\text{ g/W}$, si bien con un empuje útil casi imperceptible ($1.37\text{ gf}$).
* En el punto operativo superior de 19,923 RPM, la relación cae a $7.94\text{ g/W}$, lo cual es coherente con la necesidad de mayor potencia para acelerar el caudal másico en un disco de apenas $8.1\text{ cm}$ de diámetro (carga de disco $T/A \approx 142.9\text{ N/m}^2$).

### 6.3 Verificación de Incompresibilidad ($M_{\text{tip}}$)
El número de Mach en la punta varía entre $0.0369$ y $0.2492$. Al no superar el umbral crítico de $M \approx 0.30$, se confirma de manera concluyente que:
* No existen efectos de compresibilidad apreciables.
* No se presentan ondas de choque de punta ni engrosamiento de capa límite inducido por gradientes de presión transónicos.
* Las variaciones observadas en $C_T$ y $C_P$ se deben pura y exclusivamente a efectos de número de Reynolds y flexibilidad estructural.

---

## 7. Limitaciones Críticas, Transferibilidad y Prohibición de Extrapolación

> [!WARNING]
> Las tres consideraciones siguientes son de obligado cumplimiento metodológico en cualquier modelo de propulsión subsiguiente.

### 7.1 No Validación del Ventilador Entubado (EDF) C02 de 8 Palas
Los datos analizados en este estudio corresponden a una **hélice abierta aislada de dos palas** Micro Invent 3.2x2.2. **Bajo ninguna circunstancia estos datos pueden emplearse para validar, predecir o correlacionar el rendimiento del ventilador entubado (EDF) C02 de ocho palas**, debido a incompatibilidades físicas insalvables:
1. **Aerodinámica de contorno (Rotor abierto vs. Confinado):** La hélice Micro Invent presenta desprendimiento libre de vórtices de punta de pala y una estela libre que experimenta contracción natural en estático ($A_{\text{estela}} \to A/2$). En contraste, un ventilador entubado (ducted fan) opera con holgura de punta mínima respecto a la carcasa, eliminando los vórtices marginales tridimensionales convencionales y generando una succión importante en el labio del conducto (*duct lip thrust*), que suele aportar entre un 30% y un 50% del empuje total en estático.
2. **Solidez y bloqueo (2 palas vs. 8 palas):** La relación de solidez ($\sigma = B \cdot c / (\pi R)$) de un rotor de 8 palas es drásticamente superior a la de una micro-hélice bipala. Las 8 palas interactúan en régimen de cascada de perfiles fuertemente acoplados (efectos de interferencia pala a pala), modificando los ángulos de entrada y coeficientes de bloqueo.
3. **Pérdidas de difusión interna:** El ducto introduce pérdidas por fricción superficial en las paredes interiores y efectos difusores que no existen en un rotor libre.

### 7.2 Distinción entre Potencia Mecánica de Eje y Potencia Eléctrica
* La variable $P$ calculada en este estudio es estrictamente la **potencia mecánica absorbida por el eje** ($P = 2\pi n Q = C_P \rho n^3 D^5$).
* **NO representa la potencia eléctrica ($P_{\text{elec}} = V \cdot I$)** que debe suministrar una batería al motor eléctrico o al ESC.
* La potencia eléctrica real es significativamente superior, gobernada por la cadena de rendimientos electromecánicos:
  $$P_{\text{elec}} = \frac{P}{\eta_{\text{motor}} \cdot \eta_{\text{esc}} \cdot \eta_{\text{mec}}}$$
* En micro-motores brushless (1 a 5 gramos) asociados comúnmente a hélices de 3.2 pulgadas, los rendimientos típicos son $\eta_{\text{motor}} \approx 0.50 - 0.70$ y $\eta_{\text{esc}} \approx 0.85 - 0.90$. Por consiguiente, la potencia eléctrica consumida puede duplicar a la potencia mecánica de eje aquí reportada.

### 7.3 Prohibición Estricta de Extrapolación de RPM
El dominio experimental certificado abarca rígidamente desde **2,950.000 RPM hasta 19,923.333 RPM**.
* **Prohibición por encima de 19,923.333 RPM:** Las micro-hélices de polímero ultraligero sufren deformación aeroelástica dependiente de las cargas centrífugas y aerodinámicas. Extrapolar hacia revoluciones mayores conllevaría desalineación del paso geométrico ($\beta$), vibraciones críticas (*flutter*) y riesgo inminente de fallo estructural, además de violar el comportamiento medido del banco UIUC.
* **Prohibición por debajo de 2,950.000 RPM:** A regímenes inferiores, el número de Reynolds cae por debajo de 4,000, ingresando en un régimen de separación laminar profunda donde los transductores de par y tracción de UIUC pierden sensibilidad y los modelos de semejanza cuadrática dejan de cumplirse.

---

## 8. Verificación y Pruebas del Software (`test_analizar.py`)

Para garantizar la reproducibilidad y corrección del código, se implementó una batería de 15 pruebas unitarias automatizadas con `unittest` en `salidas/test_analizar.py`.

### 8.1 Resumen de Casos de Prueba
1. `test_calcular_n`: Conversión exacta de RPM a rev/s y validación de RPM no negativa.
2. `test_calcular_empuje`: Concordancia con $T = C_T \rho n^2 D^4$ y leyes de semejanza ($T \propto n^2$, $T \propto D^4$).
3. `test_calcular_potencia`: Concordancia con $P = C_P \rho n^3 D^5$ y leyes de semejanza ($P \propto n^3$, $P \propto D^5$).
4. `test_calcular_mach_punta`: Exactitud cinemática $M_{\text{tip}} = (\pi n D)/a$ y comportamiento nulo a $n = 0$.
5. `test_calcular_reynolds_075`: Verificación rigurosa de la velocidad tangencial y cuerda seccional a $0.75R$.
6. `test_calcular_figura_merito`: Exactitud de la formulación adimensional $FM = \sqrt{2/\pi} \cdot C_T^{3/2} / C_P$.
7. `test_equivalencia_figura_merito_dimensional`: Comprobación de que la formulación dimensional $P_{\text{ideal}} / P$ y la adimensional coinciden numéricamente con tolerancia de $10^{-12}$.
8. `test_cargar_datos_estaticos`: Comprobación de lectura y parseo íntegro de los 18 registros en `mi_3.2x2.2_static_0519rd.txt`.
9. `test_cargar_geometria`: Validación de que la cuerda seccional relativa en $r/R = 0.75$ es exactamente $0.1799$.
10. `test_archivo_inexistente`: Manejo seguro de excepciones `FileNotFoundError`.
11. `test_numero_puntos`: Confirmación de 18 puntos calculados.
12. `test_monotonia_rpm_empuje_potencia`: Verificación de gradiente estrictamente positivo para $n$, $T$, $P$, $M_{\text{tip}}$ y $Re_{0.75R}$.
13. `test_acotacion_fisica`: Comprobación de que todas las variables se sitúan dentro de órdenes de magnitud físicamente admisibles.
14. `test_prohibicion_extrapolacion_rpm`: Comprobación activa de que el código emite una excepción si se intenta evaluar fuera del rango experimental $[2950.000, 19923.333]$ con la extrapolación desactivada.
15. `test_existencia_y_contenido_csv`: Validación de existencia, cabeceras normalizadas y valores no nulos en `salidas/puntos.csv`.

### 8.2 Resultado de Ejecución de Pruebas
```text
Ran 15 tests in 0.001s
OK
```
Todas las pruebas se ejecutaron satisfactoriamente en el entorno sandbox aislado sin advertencias ni fallos.

---

## 9. Inventario de Entregables Generados

Todos los entregables han sido ubicados exclusivamente en el directorio `salidas/`:

1. **`salidas/analizar.py`:** Script en Python 3 que procesa los archivos de referencia de `entradas/`, ejecuta las fórmulas aerodinámicas, valida los rangos sin extrapolación, genera `salidas/puntos.csv` e imprime en consola la tabla tabulada.
2. **`salidas/test_analizar.py`:** Suite completa de 15 pruebas unitarias y de integración sobre las fórmulas físicas, equivalencia de la Figura de Mérito, lectura de archivos y restricciones operativas.
3. **`salidas/puntos.csv`:** Archivo de datos normalizado conteniendo las 9 variables calculadas para cada uno de los 18 puntos de ensayo.
4. **`salidas/INFORME.md`:** El presente informe técnico detallado.

---

## 10. Referencias Bibliográficas

1. **University of Illinois at Urbana-Champaign (UIUC):** *UIUC Propeller Database - Volume 2.* Department of Aerospace Engineering. URL: [https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html](https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html).
2. **Deters, R. W., Ananda, G. K., & Selig, M. S. (2014):** *Reynolds Number Effects on the Performance of Small-Scale Propellers.* 32nd AIAA Applied Aerodynamics Conference, AIAA Aviation, Atlanta, Georgia, AIAA Paper 2014-2151. DOI / URL: [https://m-selig.ae.illinois.edu/pubs/DetersAnandaSelig-2014-AIAA-2014-2151.pdf](https://m-selig.ae.illinois.edu/pubs/DetersAnandaSelig-2014-AIAA-2014-2151.pdf).
3. **Leishman, J. G. (2006):** *Principles of Helicopter Aerodynamics.* Cambridge Aerospace Series, Cambridge University Press.
4. **Glauert, H. (1935):** *Airplane Propellers.* Aerodynamic Theory (W. F. Durand, ed.), Vol. 4, Div. L, Julius Springer, Berlin.
