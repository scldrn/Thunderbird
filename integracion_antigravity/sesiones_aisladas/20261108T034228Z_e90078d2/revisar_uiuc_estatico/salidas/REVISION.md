# Auditoría Técnica y Revisión del Cálculo UIUC Estático

**Fecha de Auditoría:** Noviembre 2026  
**Instalación / Objeto:** Hélice ultraligera Micro Invent 3.2x2.2 en banco UIUC (Volumen 2)  
**Sesión de Origen Auditada:** `20261108T032826Z_13ced8ae/uiuc_estatico` (terminada con error de red)  
**Espacio de Trabajo Actual:** `/private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_uiuc_estatico`  
**Entorno de Ejecución:** Sandbox aislado (solo lectura en `entradas/`, entregables en `salidas/`)

---

## 1. Resumen Ejecutivo de la Auditoría

Se auditó de manera exhaustiva el cálculo aerodinámico estático de la hélice abierta **Micro Invent 3.2x2.2** producido en la sesión anterior, el cual había quedado interrumpido por fallo de red tras generar los archivos. 

Se procedió a:
1. Copiar los scripts de cálculo y prueba a `salidas/` (`salidas/analizar.py` y `salidas/test_analizar.py`).
2. Ejecutarlos contra las fuentes de datos oficiales UIUC ubicadas en `entradas/`.
3. Realizar una **auditoría dimensional y física formal** de los parámetros $C_T$, $C_P$, diámetro $D$, Mach de punta $M_{\text{tip}}$, Reynolds seccional $Re_{0.75R}$ y Figura de Mérito $FM$.
4. Detectar errores de interpretación analítica en la documentación previa (`INFORME.md`) y fragilidades de acoplamiento en la suite de pruebas unitarias (`test_analizar.py`).
5. Aplicar las correcciones pertinentes exclusivamente sobre las copias en `salidas/` y verificar la ejecución completa de 16 pruebas unitarias exitosas.

---

## 2. Taxonomía de Datos: Medidos, Supuestos y Calculados

Para preservar la trazabilidad científica, se clasifican los datos empleados en el modelo:

| Categoría | Parámetro | Símbolo | Valor / Rango | Unidades | Fuente / Justificación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dato Medido** | Velocidad de rotación | $\text{RPM}$ | $2,950.000 - 19,923.333$ | $\text{rev/min}$ | Tacómetro óptico banco UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Dato Medido** | Coeficiente de empuje | $C_T$ | $0.103654 - 0.125828$ | $-$ | Balanza de fuerza banco UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Dato Medido** | Coeficiente de potencia | $C_P$ | $0.051360 - 0.059879$ | $-$ | Sensor de par banco UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Dato Medido** | Diámetro nominal | $D$ | $3.2$ ($0.08128$) | $\text{in}$ ($\text{m}$) | Especificación fabricante / perfil UIUC (`mi_3.2x2.2_geom.png`) |
| **Dato Medido** | Número de palas | $B$ | $2$ | $-$ | Catálogo oficial Micro Invent (hélice bipala) |
| **Dato Medido** | Cuerda relativa a $0.75R$ | $(c/R)_{0.75}$ | $0.1799$ | $-$ | Archivo geométrico UIUC (`mi_3.2x2.2_geom.txt`, fila $r/R = 0.75$) |
| **Dato Medido** | Ángulo de torsión local | $\beta_{0.75}$ | $14.271$ | $^{\circ}$ | Archivo geométrico UIUC (`mi_3.2x2.2_geom.txt`) |
| **Supuesto** | Densidad atmosférica | $\rho$ | $1.225$ | $\text{kg/m}^3$ | Atmósfera estándar ISA a nivel del mar ($T_0=15^{\circ}\text{C}, p_0=101,325\text{ Pa}$) |
| **Supuesto** | Velocidad del sonido | $a$ | $340.3$ | $\text{m/s}$ | Atmósfera estándar ISA ($a = \sqrt{\gamma R_g T_0}$, $\gamma=1.4$) |
| **Supuesto** | Viscosidad cinemática | $\nu$ | $1.46 \times 10^{-5}$ | $\text{m}^2/\text{s}$ | Aire estándar a $15^{\circ}\text{C}$ ($\nu = \mu / \rho$) |
| **Supuesto** | Velocidad de corriente libre | $V_\infty$ | $0.0$ | $\text{m/s}$ | Condición estática pura (punto fijo / *hover*, $J = 0$) |
| **Supuesto** | Deformabilidad estructural | $-$ | Indeformable | $-$ | Se desprecia flexión/torsión aeroelástica en el rango ensayado |
| **Calculado** | Frecuencia de rotación | $n$ | $49.167 - 332.056$ | $\text{rev/s}$ | $n = \text{RPM} / 60$ |
| **Calculado** | Empuje estático | $T$ | $0.013397 - 0.741771$ | $\text{N}$ | $T = C_T \rho n^2 D^4$ |
| **Calculado** | Potencia mecánica de eje | $P$ | $0.026527 - 9.527113$ | $\text{W}$ | $P = C_P \rho n^3 D^5$ |
| **Calculado** | Mach de punta | $M_{\text{tip}}$ | $0.036893 - 0.249162$ | $-$ | $M_{\text{tip}} = (\pi n D) / a$ |
| **Calculado** | Reynolds a $0.75R$ | $Re_{0.75R}$ | $4,715.17 - 31,844.73$ | $-$ | $Re_{0.75R} = (0.75 \pi n D \cdot c_{0.75}) / \nu$ |
| **Calculado** | Figura de Mérito ideal | $FM$ | $0.518435 - 0.596562$ | $-$ | $FM = \sqrt{2/\pi} \cdot (C_T^{3/2} / C_P)$ |

---

## 3. Auditoría Dimensional y Física Exhaustiva

### 3.1 Coeficiente de Empuje ($C_T$) y Empuje Dimensional ($T$)
* **Definición estándar UIUC:**
  $$C_T = \frac{T}{\rho n^2 D^4} \implies T = C_T \rho n^2 D^4$$
* **Homogeneidad dimensional:**
  * $[T] = \text{M} \text{L} \text{T}^{-2}$ ($\text{N} = \text{kg}\cdot\text{m}\cdot\text{s}^{-2}$)
  * $[\rho] = \text{M} \text{L}^{-3}$ ($\text{kg}\cdot\text{m}^{-3}$)
  * $[n] = \text{T}^{-1}$ ($\text{s}^{-1}$)
  * $[D] = \text{L}$ ($\text{m}$)
  * Denominador: $[\rho n^2 D^4] = (\text{M} \text{L}^{-3}) (\text{T}^{-2}) (\text{L}^4) = \text{M} \text{L} \text{T}^{-2} = \text{N}$
  * $[C_T] = \frac{\text{M} \text{L} \text{T}^{-2}}{\text{M} \text{L} \text{T}^{-2}} = 1$ (adimensional estricto).
* **Evaluación del código:** `analizar.py` implementa `ct * rho * (n ** 2) * (d ** 4)`. La fórmula es correcta y dimensionalmente homogénea.
* **Distinción con formulación de helicópteros:** En dinámica de rotores de alas giratorias se define $C_T^{\text{heli}} = \frac{T}{\rho A (\Omega R)^2}$. Dado que $\Omega = 2\pi n$, $R = D/2$ y $A = \frac{\pi}{4} D^2$, se tiene:
  $$\rho A (\Omega R)^2 = \rho \left(\frac{\pi D^2}{4}\right) (\pi^2 n^2 D^2) = \frac{\pi^3}{4} \rho n^2 D^4 \implies C_T^{\text{heli}} = \frac{4}{\pi^3} C_T^{\text{prop}} \approx 0.129006 \, C_T^{\text{prop}}$$
  El script y los datos de UIUC emplean con total corrección el coeficiente de hélice $C_T^{\text{prop}}$.

### 3.2 Coeficiente de Potencia ($C_P$) y Potencia Dimensional ($P$)
* **Definición estándar UIUC:**
  $$C_P = \frac{P}{\rho n^3 D^5} \implies P = C_P \rho n^3 D^5$$
* **Homogeneidad dimensional:**
  * $[P] = \text{M} \text{L}^2 \text{T}^{-3}$ ($\text{W} = \text{J/s} = \text{kg}\cdot\text{m}^2\cdot\text{s}^{-3}$)
  * $[\rho n^3 D^5] = (\text{M} \text{L}^{-3}) (\text{T}^{-3}) (\text{L}^5) = \text{M} \text{L}^2 \text{T}^{-3} = \text{W}$
  * $[C_P] = \frac{\text{W}}{\text{W}} = 1$ (adimensional estricto).
* **Evaluación del código:** `analizar.py` implementa `cp * rho * (n ** 3) * (d ** 5)`. Es exacto.
* **Distinción con helicópteros:** $C_P^{\text{heli}} = \frac{P}{\rho A (\Omega R)^3} = \frac{4}{\pi^4} C_P^{\text{prop}} \approx 0.04106 \, C_P^{\text{prop}}$.
* **Naturaleza física:** $P$ es **potencia mecánica absorbida por el eje** ($P = \omega Q = 2\pi n Q$). No debe confundirse con la potencia eléctrica del motor.

### 3.3 Diámetro ($D$) y Cuerda Seccional ($c_{0.75}$)
* **Conversión dimensional:**
  $$D = 3.2\text{ in} \times 0.0254\frac{\text{m}}{\text{in}} = 0.08128\text{ m} \quad (R = 0.04064\text{ m})$$
* **Auditoría de implementación geométrica:**
  En el archivo de geometría `mi_3.2x2.2_geom.txt`, la segunda columna corresponde a la relación $c/R$ (cuerda local dividida por el radio, no por el diámetro).
  A $r/R = 0.75$, se tiene $(c/R)_{0.75} = 0.1799$.
  En `analizar.py`:
  ```python
  r = d / 2.0
  c_075 = c_over_r_075 * r  # 0.1799 * 0.04064 m = 0.007311136 m (7.311 mm)
  ```
  Se comprobó que el script no comete el error común de multiplicar por $D$, lo que habría sobreestimado la cuerda y el número de Reynolds en un factor de $2.0$.

### 3.4 Número de Mach de Punta ($M_{\text{tip}}$)
* **Cinemática rotacional:**
  $$V_{\text{tip}} = \omega R = (2\pi n) \left(\frac{D}{2}\right) = \pi n D \quad [\text{m/s}]$$
  $$M_{\text{tip}} = \frac{V_{\text{tip}}}{a} = \frac{\pi n D}{a}$$
* **Homogeneidad dimensional:**
  $$[M_{\text{tip}}] = \frac{\text{L} \text{T}^{-1}}{\text{L} \text{T}^{-1}} = 1 \quad (\text{adimensional})$$
* **Régimen de compresibilidad:**
  * A 2,950 RPM ($n = 49.167\text{ rev/s}$): $V_{\text{tip}} = 12.555\text{ m/s} \implies M_{\text{tip}} = 0.0369$.
  * A 19,923.333 RPM ($n = 332.056\text{ rev/s}$): $V_{\text{tip}} = 84.776\text{ m/s} \implies M_{\text{tip}} = 0.2492$.
  * Al verificarse $M_{\text{tip}} \le 0.2492 < 0.30$ en todo el dominio experimental, la variación de densidad por compresibilidad es despreciable ($\Delta \rho / \rho \approx \frac{1}{2} M^2 < 0.031$, i.e. $< 3.1\%$), validando la hipótesis de flujo incompresible.

### 3.5 Número de Reynolds Seccional ($Re_{0.75R}$)
* **Definición seccional estática:**
  En condición estática pura ($V_\infty = 0$), el flujo incidente se aproxima por la velocidad tangencial de la pala a $0.75R$:
  $$V_{0.75R} = \omega (0.75 R) = 2 \pi n \left(0.75 \frac{D}{2}\right) = 0.75 \, \pi \, n \, D \quad [\text{m/s}]$$
  $$Re_{0.75R} = \frac{V_{0.75R} \cdot c_{0.75}}{\nu} = \frac{(0.75 \pi n D) \cdot ((c/R)_{0.75} \cdot R)}{\nu}$$
* **Homogeneidad dimensional:**
  $$[Re] = \frac{(\text{L} \text{T}^{-1}) \cdot (\text{L})}{\text{L}^2 \text{T}^{-1}} = 1 \quad (\text{adimensional})$$
* **Régimen aerodinámico:**
  * $Re_{0.75R} \in [4,715.17, \, 31,844.73]$.
  * Este rango sitúa a la hélice en el régimen subcrítico ultra-bajo, gobernado por capas límite laminares espesas y formación de burbujas de separación laminar (*laminar separation bubbles*), lo que incrementa notablemente el coeficiente de resistencia de perfil ($C_d$).
* **Límite de modelo (inclusión de velocidad inducida):**
  La teoría de cantidad de movimiento predice una velocidad inducida estática en el disco de $v_i = \sqrt{T / (2 \rho A)}$. A 19,923 RPM ($T = 0.7418\text{ N}$, $A = 0.005189\text{ m}^2$), $v_i \approx 7.64\text{ m/s}$. La velocidad resultante efectiva local es:
  $$V_{\text{eff}} = \sqrt{V_{0.75}^2 + v_i^2} = \sqrt{(63.58)^2 + (7.64)^2} = 64.04\text{ m/s}$$
  La diferencia respecto a la velocidad tangencial pura ($63.58\text{ m/s}$) es de solo $+0.72\%$. La convención habitual de la literatura de micro-hélices (Deters et al., AIAA 2014-2151) toma la velocidad puramente tangencial para caracterizar $Re_{0.75R}$, por lo que la fórmula del código es consistente y estándar.

### 3.6 Figura de Mérito Ideal ($FM$)
* **Deducción a partir de la teoría de cantidad de movimiento de Rankine-Froude:**
  En punto fijo (*hover*), el flujo másico a través del disco actuador es $\dot{m} = \rho A v_i$.
  El empuje es $T = \dot{m} (2 v_i) = 2 \rho A v_i^2 \implies v_i = \sqrt{\frac{T}{2 \rho A}}$.
  La potencia inducida mínima teórica requerida para producir dicho empuje es:
  $$P_{\text{ideal}} = T v_i = \frac{T^{3/2}}{\sqrt{2 \rho A}}$$
  Sustituyendo $T = C_T \rho n^2 D^4$, $A = \frac{\pi}{4} D^2$ y $P_{\text{real}} = C_P \rho n^3 D^5$:
  $$T^{3/2} = C_T^{3/2} \rho^{3/2} n^3 D^6$$
  $$\sqrt{2 \rho A} = \sqrt{2 \rho \frac{\pi D^2}{4}} = \sqrt{\frac{\pi}{2}} \rho^{1/2} D$$
  $$P_{\text{ideal}} = \frac{C_T^{3/2} \rho^{3/2} n^3 D^6}{\sqrt{\frac{\pi}{2}} \rho^{1/2} D} = \sqrt{\frac{2}{\pi}} C_T^{3/2} \rho n^3 D^5$$
  Dividiendo entre $P_{\text{real}}$:
  $$FM = \frac{P_{\text{ideal}}}{P_{\text{real}}} = \frac{\sqrt{\frac{2}{\pi}} C_T^{3/2} \rho n^3 D^5}{C_P \rho n^3 D^5} = \sqrt{\frac{2}{\pi}} \frac{C_T^{3/2}}{C_P} \approx 0.79788456 \, \frac{C_T^{3/2}}{C_P}$$
* **Homogeneidad dimensional:**
  Tanto $P_{\text{ideal}}/P$ como $\sqrt{2/\pi} \cdot C_T^{3/2} / C_P$ son estrictamente adimensionales:
  $$[FM] = \frac{\text{W}}{\text{W}} = 1$$
* **Comprobación numérica:** Las dos vías (adimensional y dimensional) coinciden con residuo $< 10^{-12}$ en todas las pruebas.
* **Valores observados:** $FM \in [0.5184, 0.5966]$. Este rango es plenamente consistente con hélices rígidas de pequeño tamaño en vuelo estático a bajo Reynolds.

---

## 4. Identificación de Errores Precisos y Evidencias Documentales

Durante la auditoría del trabajo previo se detectaron las siguientes discrepancias y errores específicos:

### Error 1: Afirmación errónea de monotonicidad de $C_T$ en `INFORME.md` (Sección 6.1)
* **Evidencia textual (`INFORME.md`, línea 162):**  
  > *"Por esta razón, $C_T$ crece de forma monotónica un 21.4% (hasta $0.12583$) y $FM$ escala hasta alcanzar un pico de $0.5966$ a 18,823 RPM..."*
* **Evidencia numérica objetiva de los datos UIUC (`mi_3.2x2.2_static_0519rd.txt`):**
  * Entre Punto 4 (5,940 RPM, $C_T = 0.109779$) y Punto 5 (7,046 RPM, $C_T = 0.109755$): **decrece** $\Delta C_T = -0.000024$.
  * Entre Punto 5 y Punto 6 (8,106 RPM, $C_T = 0.109700$): **decrece** $\Delta C_T = -0.000055$.
  * Entre Punto 7 (8,983 RPM, $C_T = 0.113454$) y Punto 8 (10,056 RPM, $C_T = 0.112185$): **decrece** $\Delta C_T = -0.001269$ (caída del $1.12\%$).
  * Entre Punto 8 y Punto 9 (11,056 RPM, $C_T = 0.111483$): **decrece** $\Delta C_T = -0.000702$ (caída del $0.63\%$).
  * Entre Punto 14 (15,860 RPM, $C_T = 0.122140$) y Punto 15 (16,940 RPM, $C_T = 0.121822$): **decrece** $\Delta C_T = -0.000318$.
* **Corrección aerodinámica:**  
  La afirmación previa confunde la monotonicidad del **empuje dimensional** $T$ (que sí es estrictamente monótono creciente porque $n^2$ domina fuertemente) con la evolución del **coeficiente adimensional** $C_T$. $C_T$ experimenta una **tendencia global creciente** (+21.39% neto), pero **NO es monotónico punto a punto**. Presenta fluctuaciones y mesetas debidas a la formación, desplazamiento o colapso de burbujas de separación laminar (*laminar separation bubbles*) en los perfiles ultraligeros a bajo Reynolds, sumadas a la incertidumbre instrumental de UIUC.

### Error 2: Comportamiento no monótono de la Figura de Mérito ($FM$)
* **Evidencia:**  
  En concordancia con las oscilaciones de $C_T$ y $C_P$, $FM$ tampoco evoluciona de forma estrictamente monótona:
  * Cae de $0.5565$ (Punto 4) a $0.5541$ (Punto 5).
  * Cae de $0.5930$ (Punto 14) a $0.5879$ (Punto 15).
  * Alcanza su valor máximo en el Punto 17 (18,823.333 RPM) con $FM = 0.596562$ y retrocede en el Punto 18 (19,923.333 RPM) a $FM = 0.594746$.

### Error 3: Fragilidad de acoplamiento en `test_analizar.py` (`TestSalidaCSV`)
* **Evidencia:**  
  La prueba unitaria `TestSalidaCSV` verificaba la existencia de `salidas/puntos.csv` pero no garantizaba su creación previa. Si un usuario o proceso de CI/CD ejecutaba únicamente `python3 -m unittest salidas/test_analizar.py` sobre un directorio limpio, la prueba fallaba con `AssertionError: False is not true : No existe .../salidas/puntos.csv`.
* **Corrección aplicada en `salidas/test_analizar.py`:**  
  Se añadió inicialización autónoma en `TestSalidaCSV.setUp`: si el archivo CSV no existe, el caso de prueba invoca de manera controlada `analizar.main()` antes de realizar las aserciones sobre su estructura y contenido.

### Error 4: Omisión del test de escalado cuadrático de Reynolds con el diámetro
* **Evidencia:**  
  La suite original solo verificaba la linealidad de $Re$ con la frecuencia de rotación $n$ ($Re \propto n$), obviando verificar que al escalar el diámetro geométricamente ($D \to 2D$), la velocidad seccional ($V \propto D$) y la cuerda física ($c \propto D$) se duplican simultáneamente, dando lugar a un escalado cuadrático $Re \propto D^2$.
* **Corrección aplicada en `salidas/test_analizar.py`:**  
  Se incorporó la prueba `re_doble_d` que confirma numéricamente que duplicar $D$ cuadruplica $Re$ (`4.0 * re_calculado`). Asimismo, se añadió el test `test_no_monotonia_estricta_ct_cp` para certificar la presencia de decrementos locales en los datos experimentales de $C_T$ y $C_P$.

---

## 5. Prohibición Absoluta de Atribución al Ventilador Entubado C02

> [!CAUTION]
> **Los resultados aerodinámicos de la hélice Micro Invent 3.2x2.2 NO son transferibles ni representativos del ventilador entubado (EDF) C02 de 8 palas.** Cualquier extrapolación o atribución de estos coeficientes al ventilador C02 inducirá errores graves de predicción de empuje, par y consumo eléctrico.

Las razones físicas insalvables son:

1. **Topología de flujo: Rotor libre vs. Flujo confinado:**
   * La hélice Micro Invent opera en régimen de **rotor abierto aislado**: la vena de aire sufre una contracción transversal libre ($A_{\text{vena}} \to A/2$) y genera un sistema de vórtices helicoidales libres desprendidos en la punta de cada pala (*tip vortex shedding*).
   * El ventilador C02 es un **ventilador entubado (EDF)**: la presencia de la carcasa cilíndrica con holgura de punta mínima suprime el vórtice marginal libre convencional. Además, la fuerte aceleración del fluido alrededor del labio del conducto genera una fuerza de succión axial sobre la pared del ducto (*duct lip thrust*), que en régimen estático aporta típicamente entre el **30% y el 50% del empuje total** del conjunto motor-conducto.

2. **Solidez aerodinámica e interferencia entre palas:**
   * La hélice abierta Micro Invent es bipala ($B=2$) con solidez sumamente baja ($\sigma = B c / (\pi R) \approx 0.076$ a $0.75R$). Cada pala opera esencialmente como un perfil alar aislado con débil acoplamiento inductivo.
   * El ventilador C02 cuenta con **8 palas** ($B=8$) y alta cuerda seccional ($\sigma \gg 0.35$). Opera en régimen de **cascada alar cerrada**, donde los campos de presión de una pala modifican severamente el ángulo de ataque incidente y la capa límite de la pala vecina, generando bloqueo aerodinámico y deflexión angular forzada.

3. **Álabes directores y recuperación de energía rotacional:**
   * La hélice abierta disipa toda la energía cinética del torbellino de salida (*swirl losses*) en la estela.
   * Un ventilador entubado incluye estatores o álabes directores fijos aguas abajo del rotor para enderezar el flujo y convertir la velocidad tangencial en incremento de presión estática y empuje axial adicional.

4. **Pérdidas viscosas de pared interna:**
   * En el conducto del ventilador C02 existe fricción superficial adicional en las paredes interiores del ducto y posibles desprendimientos en el difusor, factores inexistentes en una hélice libre.

---

## 6. Límites Operativos y Restricciones de Validez

1. **Rango de Ensayos UIUC Certificado:**
   * El rango de validez estricto abarca **$2,950.000 \text{ RPM} \le \text{RPM} \le 19,923.333 \text{ RPM}$**.
   * **Prohibición de extrapolación superior (> 19,923.333 RPM):** A velocidades más altas, las palas de plástico ultraligero de la hélice Micro Invent sufren importantes deflexiones torsional/flexionales por cargas centrífugas y aerodinámicas (*aeroelastic untwist*), cambiando el paso efectivo y arriesgando vibraciones aeroelásticas críticas (*flutter*).
   * **Prohibición de extrapolación inferior (< 2,950.000 RPM):** Por debajo de este umbral, el número de Reynolds cae por debajo de $4,000$, donde domina la separación laminar masiva sin reasentamiento (*stall* laminar) y los transductores de UIUC carecen de sensibilidad calibrada.

2. **Diferenciación entre Potencia Mecánica de Eje y Potencia Eléctrica:**
   * La potencia $P$ aquí auditada es exclusivamente la **potencia mecánica absorbida por el eje** ($P = \omega Q$).
   * Para alimentar este rotor mediante un micro-motor eléctrico y variador (ESC), la potencia eléctrica demandada a la batería será sustancialmente mayor:
     $$P_{\text{eléctrica}} = \frac{P}{\eta_{\text{motor}} \cdot \eta_{\text{esc}} \cdot \eta_{\text{mec}}}$$
   * Con eficiencias típicas de micro-propulsores ($\eta_{\text{motor}} \approx 0.55 - 0.70$, $\eta_{\text{esc}} \approx 0.85 - 0.90$), la potencia eléctrica requerida es entre un **50% y un 100% superior** a los valores de potencia mecánica reflejados en `salidas/puntos.csv`.

---

## 7. Pruebas Realizadas y Verificación en Sandbox

Se ejecutó la suite de pruebas unitarias actualizada en `salidas/test_analizar.py`, cubriendo 16 casos de verificación:

```text
Ran 16 tests in 0.002s

OK
```

### Detalle de las Pruebas Unitarias Ejecutadas:
1. `test_calcular_n`: Conversión exacta de RPM a rev/s y rechazo de valores negativos.
2. `test_calcular_empuje`: Verificación de homogeneidad física y leyes de semejanza ($T \propto n^2$, $T \propto D^4$).
3. `test_calcular_potencia`: Verificación de homogeneidad y leyes de semejanza de potencia ($P \propto n^3$, $P \propto D^5$).
4. `test_calcular_mach_punta`: Cinemática de velocidad tangencial $V_{\text{tip}} = \pi n D$ y razón $V/a$.
5. `test_calcular_reynolds_075`: Linealidad de $Re$ con $n$ y escalado cuadrático con $D^2$.
6. `test_calcular_figura_merito`: Exactitud de la constante analítica $\sqrt{2/\pi} \approx 0.797885$ y potencias $C_T^{1.5}/C_P$.
7. `test_equivalencia_figura_merito_dimensional`: Identidad estricta entre la formulación adimensional y la formulación dimensional de cantidad de movimiento ($P_{\text{ideal}}/P$) con residuo $< 10^{-12}$.
8. `test_cargar_datos_estaticos`: Lectura íntegra de los 18 registros del archivo de referencia `mi_3.2x2.2_static_0519rd.txt`.
9. `test_cargar_geometria`: Extracción exacta de $(c/R)_{0.75} = 0.1799$ del archivo `mi_3.2x2.2_geom.txt`.
10. `test_archivo_inexistente`: Manejo robusto de excepciones de entrada/salida (`FileNotFoundError`).
11. `test_numero_puntos`: Procesamiento completo de los 18 puntos de ensayo sin descartes indebidos.
12. `test_monotonia_rpm_empuje_potencia`: Monotonicidad estricta de las magnitudes dimensionales ($n, T, P, M_{\text{tip}}, Re_{0.75R}$).
13. `test_no_monotonia_estricta_ct_cp`: Verificación formal de que los coeficientes experimentales $C_T$ y $C_P$ presentan fluctuaciones locales a bajo Reynolds.
14. `test_acotacion_fisica`: Validación de rangos admisibles para micro-hélices ($T \in [0.01, 1.0]\text{ N}$, $M < 0.3$, $FM \in [0.50, 0.65]$).
15. `test_prohibicion_extrapolacion_rpm`: Comprobación activa del bloqueo de evaluación fuera del rango $[2,950.000, 19,923.333]\text{ RPM}$.
16. `test_existencia_y_contenido_csv`: Autonomía del test, verificación de cabeceras, 18 líneas de datos numéricos y consistencia de columnas en `salidas/puntos.csv`.

---

## 8. Inventario de Entregables Generados

Todos los entregables se encuentran estrictamente contenidos en el directorio `salidas/`:

1. **`salidas/analizar.py`:**  
   Script en Python 3 que procesa los archivos de entrada UIUC de `entradas/`, ejecuta el análisis aerodinámico, genera `salidas/puntos.csv` e imprime la tabla tabulada en consola.
2. **`salidas/test_analizar.py`:**  
   Suite de 16 pruebas unitarias autónomas que verifican dimensiones, semejanzas físicas, carga de datos, restricciones de extrapolación y no monotonicidad estricta de $C_T/C_P$.
3. **`salidas/puntos.csv`:**  
   Tabla de datos normalizada con los 18 puntos experimentales y sus 9 columnas calculadas (`rpm`, `n_rev_s`, `ct`, `cp`, `empuje_N`, `potencia_eje_W`, `mach_punta`, `re_075r`, `figura_merito`).
4. **`salidas/REVISION.md`:**  
   El presente documento técnico de auditoría y revisión.

---

## 9. Referencias Primarias y Bibliográficas

1. **UIUC Propeller Database (Volume 2):** Department of Aerospace Engineering, University of Illinois at Urbana-Champaign.  
   URL: [https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html](https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html)
2. **Deters, R. W., Ananda, G. K., & Selig, M. S. (2014):** *"Reynolds Number Effects on the Performance of Small-Scale Propellers."* AIAA Paper 2014-2151, 32nd AIAA Applied Aerodynamics Conference, Atlanta, Georgia.  
   URL: [https://m-selig.ae.illinois.edu/pubs/DetersAnandaSelig-2014-AIAA-2014-2151.pdf](https://m-selig.ae.illinois.edu/pubs/DetersAnandaSelig-2014-AIAA-2014-2151.pdf)
3. **Leishman, J. G. (2006):** *Principles of Helicopter Aerodynamics.* Cambridge Aerospace Series, Cambridge University Press.
4. **Glauert, H. (1935):** *Airplane Propellers.* Aerodynamic Theory (W. F. Durand, ed.), Vol. 4, Div. L, Julius Springer.
