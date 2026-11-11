# INFORME TÉCNICO: PROCESAMIENTO AERODINÁMICO INDEPENDIENTE DE ENSAYO UIUC
## Hélice Abierta Micro Invent 3.2x2.2 a 20.051 RPM

**Fecha:** Noviembre 2026  
**Fuente oficial de datos:** UIUC Propeller Data Site (Volume 2), University of Illinois at Urbana-Champaign  
**URL de referencia:** https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html  
**Archivo fuente de ensayo:** `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_0544rd_20051.txt`  
**Entorno de ejecución:** Entorno aislado de trabajo (sandbox local sin acceso externo)  

---

### 1. Resumen Ejecutivo

Se ha procesado de manera independiente y rigurosa el conjunto de datos de túnel de viento correspondiente a la hélice abierta de microescala **Micro Invent 3.2x2.2** ensayada a una velocidad angular nominal de **20.051 RPM** en las instalaciones aerodinámicas de UIUC (corrida `0544rd_20051`).

Bajo los supuestos de ingeniería especificados ($D = 0.08128\text{ m}$, $\rho = 1.225\text{ kg/m}^3$, régimen incompresible estándar a nivel del mar), se transformaron las variables adimensionales de avance ($J$), empuje ($C_T$) y potencia ($C_P$) a magnitudes físicas dimensionales: velocidad de avance $V$, empuje aerodinámico $T$ y potencia de eje $P$. Asimismo, se realizó una comparación metrológica exhaustiva entre la eficiencia registrada $\eta_{reg}$ y el valor calculado analíticamente $\eta_{calc} = J \cdot C_T / C_P$, distinguiendo categóricamente los artefactos de redondeo de la representación tabular frente a la incertidumbre experimental de medición.

Finalmente, se identificó el sobre de velocidad ensayado y se evaluó la discrepancia con una velocidad de referencia de $600\text{ km/h}$, estableciendo las razones físicas por las cuales no es admisible extrapolar estos datos ni transferirlos a un ventilador entubado (como el ventilador C02).

---

### 2. Clasificación Rigurosa de Variables

Para garantizar la máxima integridad técnica, se clasifica cada variable en una de las tres categorías metrológicas fundamentales:

#### 2.1. Datos Medidos / Registrados en el Ensayo
Provienen directamente del archivo de ensayo en túnel de viento de UIUC (`mi_3.2x2.2_0544rd_20051.txt`):
- **$J$ (Coeficiente de avance):** Adimensional, definido en el banco como $J = V / (n \cdot D)$. Rango medido en 19 puntos: $[0.044195, 0.448667]$.
- **$C_T$ (Coeficiente de empuje registrado):** Adimensional, medido mediante celda de carga aerodinámica. Rango: $[0.041281, 0.124104]$.
- **$C_P$ (Coeficiente de potencia registrado):** Adimensional, obtenido mediante sensor de par y tacómetro. Rango: $[0.035779, 0.058227]$.
- **$\eta_{reg}$ (Rendimiento registrado en tabla):** Adimensional, eficiencia de propulsión calculada en el sistema de adquisición del túnel de viento. Rango: $[0.094195, 0.562131]$.
- **$\text{RPM}_{nominal}$:** $20.051\text{ rpm}$ (identificador nominal del punto de prueba UIUC).

#### 2.2. Supuestos de Ingeniería Adoptados
Parámetros físicos y contextuales fijados según los requerimientos del ensayo:
- **Diámetro de la hélice ($D$):** $D = 0.08128\text{ m}$ (equivalente exacto a $3.2\text{ pulgadas}$, $3.2 \times 0.0254\text{ m}$).
- **Densidad atmosférica del fluido ($\rho$):** $\rho = 1.225\text{ kg/m}^3$ (condiciones estándar ISA a nivel del mar, $T=15^\circ\text{C}$, $P=1013.25\text{ hPa}$).
- **Frecuencia rotacional constante ($n$):** $n = \text{RPM} / 60 = 20051.0 / 60 = 334.183333...\text{ rev/s}$ (asumida fija durante la corrida).
- **Régimen de flujo:** Flujo subsónico incompresible libre, hélice rígida de microescala aislada en túnel de viento, sin ducto exterior, sin carenado ni interferencia de fuselaje.

#### 2.3. Cálculos Analíticos Derivados
Transformaciones basadas en las leyes de semejanza y definiciones normalizadas de propulsores:
- **Velocidad de avance ($V$):**
  $$V = J \cdot n \cdot D \quad [\text{m/s}], \qquad V_{km/h} = V \cdot 3.6 \quad [\text{km/h}]$$
- **Empuje aerodinámico dimensional ($T$):**
  $$T = C_T \cdot \rho \cdot n^2 \cdot D^4 \quad [\text{N}], \qquad T_{gf} = \frac{T}{9.80665} \cdot 1000 \quad [\text{gf}]$$
  *(Factor de escala constante: $\rho \cdot n^2 \cdot D^4 \approx 5.970834\text{ N}$)*
- **Potencia mecánica de eje absorbida ($P$):**
  $$P = C_P \cdot \rho \cdot n^3 \cdot D^5 \quad [\text{W}]$$
  *(Factor de escala constante: $\rho \cdot n^3 \cdot D^5 \approx 162.179048\text{ W}$)*
- **Potencia útil de tracción ($P_{out}$):**
  $$P_{out} = T \cdot V \quad [\text{W}]$$
- **Eficiencia calculada analítica ($\eta_{calc}$):**
  $$\eta_{calc} = \frac{P_{out}}{P} = \frac{(C_T \cdot \rho \cdot n^2 \cdot D^4) \cdot (J \cdot n \cdot D)}{C_P \cdot \rho \cdot n^3 \cdot D^5} = J \cdot \frac{C_T}{C_P}$$
- **Discrepancia residual numérica ($\Delta \eta$):**
  $$\Delta \eta = \eta_{reg} - \eta_{calc} \quad [-], \qquad \text{Error Relativo } [\%] = \frac{|\Delta \eta|}{\eta_{calc}} \times 100$$

---

### 3. Resultados Tabulados del Ensayo

A continuación se detalla la matriz de resultados completos para los 19 puntos ensayados:

| Pto | $J$ [-] | $C_T$ [-] | $C_P$ [-] | $\eta_{reg}$ [-] | $V$ [m/s] | $V$ [km/h] | $T$ [N] | $T$ [gf] | $P$ [W] | $P_{out}$ [W] | $\eta_{calc}$ [-] | $\Delta \eta$ [-] | Err Rel [\%] |
|:---:|:-------:|:---------:|:---------:|:----------------:|:---------:|:----------:|:-------:|:--------:|:-------:|:-------------:|:-----------------:|:-----------------:|:------------:|
| 1 | 0.044195 | 0.124104 | 0.058227 | 0.094195 | 1.2004 | 4.3216 | 0.7410 | 75.56 | 9.4435 | 0.8895 | 0.094196 | -1.44e-06 | 0.0015% |
| 2 | 0.066718 | 0.121536 | 0.057491 | 0.141043 | 1.8122 | 6.5240 | 0.7257 | 74.00 | 9.3241 | 1.3151 | 0.141042 | +1.12e-06 | 0.0008% |
| 3 | 0.088757 | 0.117885 | 0.056270 | 0.185947 | 2.4109 | 8.6791 | 0.7039 | 71.78 | 9.1261 | 1.6970 | 0.185945 | +2.11e-06 | 0.0011% |
| 4 | 0.111397 | 0.113976 | 0.055299 | 0.229598 | 3.0258 | 10.8929 | 0.6805 | 69.40 | 8.9686 | 2.0592 | 0.229599 | -8.08e-07 | 0.0004% |
| 5 | 0.134128 | 0.109746 | 0.054025 | 0.272469 | 3.6432 | 13.1157 | 0.6553 | 66.82 | 8.7620 | 2.3874 | 0.272467 | +2.34e-06 | 0.0009% |
| 6 | 0.156795 | 0.104346 | 0.052320 | 0.312711 | 4.2589 | 15.3322 | 0.6230 | 63.53 | 8.4855 | 2.6535 | 0.312709 | +2.07e-06 | 0.0007% |
| 7 | 0.179557 | 0.101613 | 0.051660 | 0.353179 | 4.8772 | 17.5579 | 0.6067 | 61.87 | 8.3784 | 2.9591 | 0.353181 | -1.90e-06 | 0.0005% |
| 8 | 0.202574 | 0.097039 | 0.050045 | 0.392796 | 5.5024 | 19.8086 | 0.5794 | 59.08 | 8.1165 | 3.1882 | 0.392798 | -2.05e-06 | 0.0005% |
| 9 | 0.223871 | 0.092632 | 0.048605 | 0.426658 | 6.0809 | 21.8912 | 0.5531 | 56.40 | 7.8830 | 3.3633 | 0.426656 | +1.93e-06 | 0.0005% |
| 10 | 0.246292 | 0.088982 | 0.047578 | 0.460623 | 6.6899 | 24.0836 | 0.5313 | 54.18 | 7.7164 | 3.5544 | 0.460624 | -7.07e-07 | 0.0002% |
| 11 | 0.269633 | 0.084149 | 0.046294 | 0.490111 | 7.3239 | 26.3660 | 0.5024 | 51.24 | 7.5082 | 3.6799 | 0.490114 | -3.21e-06 | 0.0007% |
| 12 | 0.290655 | 0.079279 | 0.044887 | 0.513345 | 7.8949 | 28.4216 | 0.4734 | 48.27 | 7.2800 | 3.7372 | 0.513352 | -7.15e-06 | 0.0014% |
| 13 | 0.313895 | 0.074564 | 0.043830 | 0.533996 | 8.5261 | 30.6941 | 0.4452 | 45.40 | 7.1085 | 3.7960 | 0.534001 | -5.07e-06 | 0.0009% |
| 14 | 0.336420 | 0.070231 | 0.042853 | 0.551349 | 9.1380 | 32.8967 | 0.4193 | 42.76 | 6.9501 | 3.8319 | 0.551353 | -3.60e-06 | 0.0007% |
| 15 | 0.358306 | 0.064986 | 0.041508 | 0.560973 | 9.7325 | 35.0369 | 0.3880 | 39.57 | 6.7319 | 3.7764 | 0.560973 | -1.55e-07 | 0.0000% |
| **16** | **0.380780** | **0.059023** | **0.039981** | **0.562131** | **10.3429** | **37.2345** | **0.3524** | **35.94** | **6.4843** | **3.6451** | **0.562136** | **-5.46e-06** | **0.0010%** |
| 17 | 0.402069 | 0.053937 | 0.038838 | 0.558373 | 10.9212 | 39.3162 | 0.3221 | 32.84 | 6.2989 | 3.5172 | 0.558381 | -7.86e-06 | 0.0014% |
| 18 | 0.425915 | 0.047714 | 0.037363 | 0.543910 | 11.5689 | 41.6480 | 0.2849 | 29.05 | 6.0597 | 3.2959 | 0.543910 | +2.73e-08 | 0.0000% |
| 19 | 0.448667 | 0.041281 | 0.035779 | 0.517650 | 12.1869 | 43.8728 | 0.2465 | 25.13 | 5.8028 | 3.0039 | 0.517662 | -1.18e-05 | 0.0023% |

---

### 4. Comparación Crítica de $\eta_{reg}$ frente a $J \cdot C_T / C_P$: Distinción entre Redondeo e Incertidumbre Experimental

Uno de los aspectos metrológicos más críticos en el procesamiento de bases de datos experimentales es evitar la confusión entre la **precisión de representación numérica** y la **incertidumbre física de medición**.

#### 4.1. Análisis de la Discrepancia Tabular Residual ($\sim 10^{-5}$)
La comparación punto a punto entre la eficiencia reportada $\eta_{reg}$ y la calculada $\eta_{calc} = J \cdot C_T / C_P$ revela diferencias numéricas muy reducidas:
- Diferencia absoluta máxima: $|\Delta \eta|_{max} = 1.1825 \times 10^{-5}$ (punto 19).
- Error relativo máximo: $0.00228\%$ ($\sim 23\text{ ppm}$).

Para determinar el origen de esta diferencia, se formuló la propagación de error por truncamiento a 6 decimales ($\epsilon = 0.5 \times 10^{-6}$):
$$d\eta = \eta \left( \frac{dJ}{J} + \frac{dC_T}{C_T} - \frac{dC_P}{C_P} \right)$$
$$|\Delta \eta|_{cota} = \eta_{calc} \left( \frac{\epsilon}{J} + \frac{\epsilon}{C_T} + \frac{\epsilon}{C_P} \right) + \epsilon$$

En los 19 puntos ensayados se verificó estrictamente que:
$$|\eta_{reg} - \eta_{calc}| \le |\Delta \eta|_{cota}$$

Esto demuestra de forma concluyente que la discrepancia observada es **exclusivamente un residuo de redondeo numérico** originado al truncar los números de coma flotante de doble precisión a 6 cifras decimales al exportar la tabla ASCII original.

#### 4.2. Por Qué el Error de Redondeo NO Equivale al Error de Medición Experimental
Suponer que la exactitud experimental del ensayo es de $10^{-5}$ o $0.002\%$ constituiría un error grave de ingeniería:
1. **Incertidumbre instrumental real:** En el túnel de viento de UIUC, el empuje se mide mediante una celda de deformación extensométrica (strain-gage balance), el par mediante un transductor de reacción/torsión, la velocidad mediante presión dinámica con tubo Pitot-estático y la rotación con tacómetro óptico.
2. **Propagación física:** La incertidumbre combinada de calibración, repetibilidad, alineación y tara aerodinámica para microhélices operando a números de Reynolds ultrabajos ($Re_{chord} \sim 15.000 - 30.000$) genera una incertidumbre experimental real del orden de **$\pm 1\%$ a $\pm 3\%$** (e incrementándose por encima del $\pm 5\%$ a bajos valores de empuje).
3. **Relación de magnitudes:** La incertidumbre experimental real ($\sim 1\%$) es más de **400 a 1000 veces mayor** que el error de redondeo de la tabla ($0.0023\%$). El redondeo solo indica la resolución del formato de texto, no la certeza física del ensayo.

---

### 5. Análisis del Rango de Velocidad y Comparación con 600 km/h

#### 5.1. Rango Medido en el Ensayo
- Velocidad de avance ensayada: **$1.20\text{ m/s}$ a $12.19\text{ m/s}$** (**$4.32\text{ km/h}$ a $43.87\text{ km/h}$**).
- Empuje generado: **$0.7410\text{ N}$ ($75.56\text{ gf}$)** en $J=0.044$ descendiendo a **$0.2465\text{ N}$ ($25.13\text{ gf}$)** en $J=0.449$.
- Eficiencia máxima: $\eta_{max} = 56.21\%$ en $J = 0.3808$, correspondiente a $V = 10.34\text{ m/s}$ ($37.23\text{ km/h}$).

#### 5.2. Comparación Cuantitativa con $600\text{ km/h}$ ($166.67\text{ m/s}$)
- **Déficit absoluto de velocidad:**
  $$\Delta V = 600.0\text{ km/h} - 43.87\text{ km/h} = 556.13\text{ km/h} \quad (154.48\text{ m/s})$$
- **Factor de discrepancia:** $600\text{ km/h}$ es **$13.68\text{ veces}$** superior a la velocidad máxima ensayada en el túnel.
- **Coeficiente de avance hipotético ($J_{600}$):** Si la hélice girase a las mismas 20.051 RPM a $600\text{ km/h}$:
  $$J_{600} = \frac{V_{600}}{n \cdot D} = \frac{166.6667\text{ m/s}}{334.1833\text{ rev/s} \times 0.08128\text{ m}} = 6.1359$$
  Esto representa más de **13.6 veces el límite máximo ensayado ($J_{max} = 0.4487$)**.

#### 5.3. Imposibilidad Fisiometrológica y Aerodinámica de Extrapolación a 600 km/h
No es físicamente admisible extrapolar los datos de este ensayo a $600\text{ km/h}$ por las siguientes razones:
1. **Régimen de Freno Aerodinámico / Molinete (Windmilling):**  
   Para una hélice con relación paso/diámetro $P/D = 2.2 / 3.2 = 0.6875$, el punto de empuje nulo ($C_T = 0$) se sitúa en torno a $J \approx 0.55 - 0.60$. A $J = 6.14$, el ángulo de pala relativo es fuertemente negativo; la hélice ya no tracciona sino que genera una resistencia masiva de frenado molinillo, extrayendo energía del flujo con coeficientes $C_T \ll 0$ y $C_P \ll 0$.
2. **Efectos de Compresibilidad y Ondas de Choque en Punta de Pala:**  
   La velocidad helicoidal resultante en la punta a $600\text{ km/h}$ sería:
   $$V_{punta} = \sqrt{V_\infty^2 + (\pi \cdot n \cdot D)^2} = \sqrt{166.67^2 + 85.33^2} \approx 187.2\text{ m/s} \implies M_{punta} \approx 0.55$$
   Aunque subcrítico para aire estándar, el perfil de la Micro Invent 3.2x2.2 es una lámina delgada de curvatura simple (cambered thin plate) diseñada para perfiles de aeromodelos de interior ultraligeros a $M < 0.05$. A $M = 0.55$ experimentaría fuertes gradientes adversos de presión, engrosamiento drástico de la capa límite y desprendimiento total de flujo.
3. **Colapso Mecánico y Estructural:**  
   Las fuerzas de presión dinámica a $600\text{ km/h}$ ($q = \frac{1}{2} \rho V^2 \approx 17.000\text{ Pa}$, en contraste con los $\sim 90\text{ Pa}$ del ensayo a $43.8\text{ km/h}$) superan en más de 180 veces las cargas aerodinámicas de diseño, provocando la rotura por flexión y aeroelasticidad instantánea de las palas.

---

### 6. Invalidez de Transferencia de Datos al "Ventilador C02"

Es fundamental advertir que los datos aerodinámicos de este propulsor **no pueden transferirse, escalarse ni aplicarse al ventilador C02**. Existen diferencias insalvables de configuración y física de fluidos:

1. **Configuración Libre vs. Entubada (Ducted Fan):**  
   La Micro Invent 3.2x2.2 es una hélice abierta libre cuya estela experimenta contracción de vena según la teoría de Froude-Rankine, con pérdidas significativas por vórtice de punta libre. Un ventilador (axial o centrífugo, como el C02) opera confinado dentro de un conducto o carcasa cilíndrica. El conducto elimina el vórtice de punta, introduce efectos de holgura radial (tip clearance), produce difusión interna con recuperación de presión estática y genera sustentación en el labio de succión del carenado.
2. **Solidez de Pala y Número de Álabes:**  
   Esta microhélice tiene únicamente 2 palas con solidez minúscula ($\sigma \ll 0.1$). Los ventiladores industriales o turbomaquinarias axiales operan con alta solidez ($\sigma > 0.5 - 0.8$), múltiples álabes (5 a 15+) y álabes estatores para la recuperación del momento angular del flujo (swirl recovery).
3. **Diferencias Termofísicas del Fluido (Aire vs. CO2):**  
   Si el "ventilador C02" hace referencia al bombeo o presurización de dióxido de carbono, las propiedades termodinámicas son radicalmente distintas a las del aire ensayado:
   - Densidad a STP: $\rho_{CO2} \approx 1.84\text{ kg/m}^3$ (50% más denso que el aire).
   - Velocidad del sonido: $a_{CO2} \approx 268\text{ m/s}$ (frente a $340\text{ m/s}$ en aire).
   - Coeficiente de dilatación adiabática: $\gamma_{CO2} \approx 1.28$ (frente a $1.40$ en aire).  
   Estas variaciones modifican los números de Mach y Reynolds, invalidando cualquier similitud dinámica directa.

---

### 7. Resumen de Archivos Generados, Pruebas Ejecutadas y Limitaciones

#### 7.1. Archivos Generados en `salidas/`
1. [`procesar_uiuc_prop.py`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/uiuc_avance/salidas/procesar_uiuc_prop.py): Script estándar Python 3 (sin dependencias externas) que implementa la carga, transformación analítica, verificación de cotas de redondeo, comprobación de límites operativos y exportación de resultados.
2. [`uiuc_mi_3.2x2.2_20051_procesado.csv`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/uiuc_avance/salidas/uiuc_mi_3.2x2.2_20051_procesado.csv): Archivo CSV estructurado con metadatos completos, encabezados descriptivos y las 16 columnas dimensionales y adimensionales con indicación explícita de variables medidas, supuestas y calculadas.
3. [`test_procesar_uiuc_prop.py`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/uiuc_avance/salidas/test_procesar_uiuc_prop.py): Suite de pruebas unitarias automatizadas con el framework `unittest`.
4. [`informe_tecnico_uiuc_avance.md`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/uiuc_avance/salidas/informe_tecnico_uiuc_avance.md): Este informe técnico formal.

#### 7.2. Pruebas Automatizadas Ejecutadas
Se diseñaron y ejecutaron 9 pruebas unitarias automatizadas (`test_01` a `test_09`), todas superadas con éxito (código de salida 0):
- **test_01_input_file_integrity:** Integridad, presencia y lectura de los 19 puntos tabulados de la corrida UIUC `0544rd_20051`.
- **test_02_velocity_transformation:** Verificación de la relación $V = J \cdot n \cdot D$ y conversión a km/h con tolerancia numérica $< 10^{-9}$.
- **test_03_thrust_transformation:** Verificación del empuje $T = C_T \cdot \rho \cdot n^2 \cdot D^4$ y su conversión a gramos-fuerza.
- **test_04_power_transformation_and_balance:** Validación de la potencia de eje $P = C_P \cdot \rho \cdot n^3 \cdot D^5$, potencia útil de tracción $P_{out} = T \cdot V$ y congruencia exacta $P_{out}/P = \eta_{calc}$.
- **test_05_rounding_vs_measurement_error:** Verificación metrológica demostrando que las 19 discrepancias $|\Delta \eta|$ son estrictamente inferiores a la cota teórica de propagación de redondeo de 6 decimales ($< 1.5 \times 10^{-5}$) y que la incertidumbre de medición experimental típica es más de 400 veces mayor.
- **test_06_measured_range_and_600kmh_comparison:** Validación del rango ensayado ($4.32$ a $43.87\text{ km/h}$), cuantificación del déficit con $600\text{ km/h}$ ($> 550\text{ km/h}$) y cálculo del $J$ hipotético ($J > 6.0$).
- **test_07_csv_file_generation_and_headers:** Comprobación de existencia del CSV, metadatos, encabezados y 19 registros de datos.
- **test_08_aerodynamic_monotonicity_and_peak:** Validación física de monotonía estrictamente decreciente de $C_T$ y $C_P$ con respecto a $J$, y confirmación del pico de eficiencia en el punto 16 ($J = 0.380780$, $\eta = 56.21\%$).
- **test_09_prohibition_rules_validation:** Comprobación de que las reglas de bloqueo impiden la extrapolación a $600\text{ km/h}$ y la transferencia al ventilador C02 o fluidos no equivalentes.

#### 7.3. Limitaciones del Estudio
1. **Rango de Velocidad Acotado:** Los datos solo son válidos para velocidades de avance entre $4.32\text{ km/h}$ y $43.87\text{ km/h}$ ($J \in [0.044, 0.449]$) y RPM constante en torno a 20.000 rpm.
2. **Supuesto de Régimen Permanente Estándar:** Se asumió $\rho = 1.225\text{ kg/m}^3$ constante y flujo incompresible libre. Variaciones en la densidad o temperatura de ensayo alterarán proporcionalmente el empuje y la potencia absoluta.
3. **Efectos de Escala de Microhélice:** Las características aerodinámicas están dominadas por números de Reynolds de cuerda extremadamente bajos ($Re_c < 30.000$), por lo que los coeficientes $C_T$ y $C_P$ no son escalables geométricamente a hélices de mayor envergadura sin correcciones por efecto de escala y separación laminar.
4. **No Transferibilidad:** Los coeficientes no son aplicables bajo ninguna circunstancia a propulsores entubados, ventiladores axiales ni a fluidos diferentes del aire atmosférico.
