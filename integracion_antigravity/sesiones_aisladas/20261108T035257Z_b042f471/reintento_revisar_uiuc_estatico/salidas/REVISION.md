# Dictamen de Revisión Aerodinámica: Análisis UIUC Estático de la Hélice Abierta Micro Invent 3.2x2.2

**Fecha de Auditoría:** 2026-11-07  
**Ubicación de Trabajo:** `salidas/` (entorno aislado sandbox)  
**Objeto Auditado:** Código, pruebas, informe y datos de la sesión previa sobre la hélice Micro Invent 3.2x2.2 ensayada en la base de datos de hélices de UIUC (Volumen 2).

---

## 1. Resumen Ejecutivo de la Auditoría

Se auditó de forma integral el cálculo aerodinámico estático de la hélice bipala abierta Micro Invent 3.2x2.2 procesado a partir de los datos experimentales de la Universidad de Illinois en Urbana-Champaign (UIUC Propeller Database).

* **Auditoría dimensional:** Las definiciones y dimensiones de $C_T$, $C_P$, diámetro $D$, Mach de punta ($M_{\text{tip}}$), Reynolds ($Re_{0.75R}$) y Figura de Mérito ($FM$) son dimensionalmente consistentes y teóricamente rigurosas bajo el estándar de hélices de UIUC.
* **Estado de la sesión previa:** La sesión anterior culminó con inconsistencias graves: el informe previo afirmaba la ejecución exitosa de pruebas y la existencia de `puntos.csv`, pero el código original fallaba por un error de resolución de rutas (`FileNotFoundError`), `puntos.csv` nunca se había generado en esa carpeta y el test arrojaba 6 errores y 1 fallo.
* **Correcciones efectuadas en `salidas/`:** Se copiaron los archivos con `shutil.copyfile`, se parametrizó la resolución de rutas en `salidas/analizar.py`, se robusteció `salidas/test_analizar.py` con pruebas en directorios temporales (`tempfile.TemporaryDirectory`, sin comandos `rm`) y validación de la no-monotonicidad real de $C_T$ y $C_P$.
* **Validación experimental:** La suite de pruebas actualizada consta de **17 pruebas unitarias e integración**, todas superadas al 100% en 0.002 s. El archivo `salidas/puntos.csv` fue generado y verificado.
* **Frontera física infranqueable:** Los datos analizados corresponden a una **hélice abierta de 2 palas** y **NO son aplicables ni validan el ventilador entubado (EDF) C02 de 8 palas**.

---

## 2. Taxonomía Rigurosa de Parámetros

| Categoría | Parámetro | Símbolo | Valor / Rango | Unidades | Fuente / Justificación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Medido** | Frecuencia de rotación | $\text{RPM}$ | $2,950.000 - 19,923.333$ | $\text{rev/min}$ | Banco tacométrico UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Medido** | Coeficiente de empuje | $C_T$ | $0.103654 - 0.125828$ | $-$ | Balanza de fuerza UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Medido** | Coeficiente de potencia | $C_P$ | $0.051360 - 0.059879$ | $-$ | Sensor de par UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Medido** | Diámetro nominal | $D$ | $3.2$ ($0.08128$) | $\text{in}$ ($\text{m}$) | Catálogo fabricante Micro Invent y nomenclatura oficial UIUC |
| **Medido** | Número de palas | $B$ | $2$ | $-$ | Catálogo de fabricante Micro Invent |
| **Medido** | Cuerda relativa en $0.75R$ | $(c/R)_{0.75}$ | $0.1799$ | $-$ | Tabla geométrica UIUC (`mi_3.2x2.2_geom.txt`, $r/R = 0.75$) |
| **Medido** | Torsión en $0.75R$ | $\beta_{0.75}$ | $14.271$ | $^{\circ}$ | Ángulo de pala local UIUC (`mi_3.2x2.2_geom.txt`) |
| **Supuesto** | Densidad atmosférica | $\rho$ | $1.225$ | $\text{kg/m}^3$ | Atmósfera estándar ISA nivel del mar ($15^{\circ}\text{C}$, $101.325\text{ kPa}$) |
| **Supuesto** | Velocidad del sonido | $a$ | $340.3$ | $\text{m/s}$ | Atmósfera estándar ISA ($\sqrt{\gamma R_g T_0}$ con $\gamma = 1.4$) |
| **Supuesto** | Viscosidad cinemática | $\nu$ | $1.46 \times 10^{-5}$ | $\text{m}^2/\text{s}$ | Aire estándar a $15^{\circ}\text{C}$ ($\mu / \rho$) |
| **Supuesto** | Velocidad de avance | $V_\infty$ | $0.0$ | $\text{m/s}$ | Condición estática pura / sustentación en punto fijo ($J = 0$) |
| **Supuesto** | Rigidez estructural | $-$ | Pala rígida | $-$ | Geometría invariable frente a deflexión centrífuga/torsional |
| **Calculado** | Frecuencia de giro | $n$ | $49.167 - 332.056$ | $\text{rev/s}$ | $n = \text{RPM} / 60$ |
| **Calculado** | Empuje estático | $T$ | $0.013397 - 0.741771$ | $\text{N}$ | $T = C_T \rho n^2 D^4$ ($1.366 - 75.639\text{ gf}$) |
| **Calculado** | Potencia mecánica de eje | $P$ | $0.026527 - 9.527113$ | $\text{W}$ | $P = C_P \rho n^3 D^5$ |
| **Calculado** | Mach de punta | $M_{\text{tip}}$ | $0.036893 - 0.249162$ | $-$ | $M_{\text{tip}} = (\pi n D) / a$ |
| **Calculado** | Reynolds en $0.75R$ | $Re_{0.75R}$ | $4,715.17 - 31,844.73$ | $-$ | $Re_{0.75R} = (0.75 \pi n D \cdot c_{0.75}) / \nu$ |
| **Calculado** | Figura de Mérito ideal | $FM$ | $0.518435 - 0.596562$ | $-$ | $FM = \sqrt{2/\pi} \cdot (C_T^{3/2} / C_P)$ |

---

## 3. Auditoría Dimensional y Fórmulas Teóricas

### 3.1 Coeficiente de Empuje ($C_T$)
* **Definición de hélice (UIUC / Glauert):**  
  $$C_T = \frac{T}{\rho n^2 D^4} \implies T = C_T \rho n^2 D^4$$
* **Homogeneidad dimensional:**  
  $$[\rho n^2 D^4] = \left(\frac{\text{kg}}{\text{m}^3}\right) \left(\frac{1}{\text{s}^2}\right) (\text{m}^4) = \frac{\text{kg}\cdot\text{m}}{\text{s}^2} = \text{N}$$  
  $$[C_T] = \frac{\text{N}}{\text{N}} = 1 \quad (\text{Adimensional})$$
* **Distinción respecto a la convención de helicópteros:** En dinámica de rotores (Leishman), $C_{T,\text{heli}} = \frac{T}{\rho (\pi R^2) (\Omega R)^2}$. La relación de conversión exacta es $C_{T,\text{heli}} = \frac{4}{\pi^3} C_{T,\text{prop}} \approx 0.12903 \, C_{T,\text{prop}}$. El código emplea rigurosamente la convención de hélices de UIUC.

### 3.2 Coeficiente de Potencia ($C_P$)
* **Definición de hélice (UIUC / Glauert):**  
  $$C_P = \frac{P}{\rho n^3 D^5} \implies P = C_P \rho n^3 D^5$$
* **Homogeneidad dimensional:**  
  $$[\rho n^3 D^5] = \left(\frac{\text{kg}}{\text{m}^3}\right) \left(\frac{1}{\text{s}^3}\right) (\text{m}^5) = \frac{\text{kg}\cdot\text{m}^2}{\text{s}^3} = \frac{\text{J}}{\text{s}} = \text{W}$$  
  $$[C_P] = \frac{\text{W}}{\text{W}} = 1 \quad (\text{Adimensional})$$
* **Distinción respecto a la convención de helicópteros:** $C_{P,\text{heli}} = \frac{P}{\rho (\pi R^2) (\Omega R)^3} = \frac{4}{\pi^4} C_{P,\text{prop}} \approx 0.041072 \, C_{P,\text{prop}}$. Correctamente discriminado en el código.

### 3.3 Diámetro ($D$)
* **Conversión y escala:** $D = 3.2\text{ in} = 3.2 \times 0.0254\text{ m} = 0.08128\text{ m}$; radio $R = 0.04064\text{ m}$.
* **Área del disco:** $A = \frac{\pi}{4} D^2 = 5.1887 \times 10^{-3}\text{ m}^2$.

### 3.4 Número de Mach de Punta ($M_{\text{tip}}$)
* **Formulación:**  
  $$V_{\text{tip}} = \omega R = 2\pi n \left(\frac{D}{2}\right) = \pi n D \quad [\text{m/s}], \qquad M_{\text{tip}} = \frac{V_{\text{tip}}}{a} = \frac{\pi n D}{a}$$
* **Homogeneidad dimensional:** $[V_{\text{tip}}] = [a] = \text{m/s} \implies [M_{\text{tip}}] = 1$.
* **Evaluación de compresibilidad:** A 19,923.333 RPM, $V_{\text{tip}} = 84.79\text{ m/s}$ y $M_{\text{tip}} = 0.2492$. Al situarse estrictamente por debajo de $M = 0.30$, las variaciones de densidad del flujo son inferiores al $3.1\%$ ($\Delta \rho/\rho \approx \frac{1}{2} M^2$). Se confirma la plena validez de la hipótesis incompresible.

### 3.5 Número de Reynolds Seccional ($Re_{0.75R}$)
* **Formulación:**  
  $$V_{0.75R} = \omega (0.75 R) = 0.75 \pi n D \quad [\text{m/s}]$$  
  $$c_{0.75R} = (c/R)_{0.75} \cdot R = 0.1799 \cdot 0.04064\text{ m} = 7.3111 \times 10^{-3}\text{ m}$$  
  $$Re_{0.75R} = \frac{V_{0.75R} \cdot c_{0.75R}}{\nu} = \frac{0.375 \, \pi \, n \, D^2 \, (c/R)_{0.75}}{\nu}$$
* **Homogeneidad dimensional:**  
  $$[Re] = \frac{(\text{m/s}) (\text{m})}{\text{m}^2/\text{s}} = 1 \quad (\text{Adimensional})$$
* **Régimen aerodinámico:** $Re_{0.75R} \in [4,715, \, 31,845]$. Este intervalo corresponde a aerodinámica viscosa dominada por capas límite laminares de bajo espesor relativo, propensas a la formación de burbujas de separación laminar (*Laminar Separation Bubbles*, LSB).

### 3.6 Figura de Mérito ($FM$)
* **Teoría de Cantidad de Movimiento (Rankine-Froude) en Hover:**  
  $$T = 2\rho A v_i^2 \implies v_i = \sqrt{\frac{T}{2\rho A}}, \qquad P_{\text{ideal}} = T v_i = \frac{T^{3/2}}{\sqrt{2\rho A}}$$  
  $$FM = \frac{P_{\text{ideal}}}{P} = \frac{T^{3/2}}{P \sqrt{2\rho A}}$$
* **Deducción en coeficientes de hélice:**  
  $$T^{3/2} = C_T^{3/2} \rho^{3/2} n^3 D^6, \qquad \sqrt{2\rho A} = \sqrt{2\rho \left(\frac{\pi D^2}{4}\right)} = \sqrt{\frac{\pi}{2}} \rho^{1/2} D$$  
  $$P_{\text{ideal}} = \frac{C_T^{3/2} \rho^{3/2} n^3 D^6}{\sqrt{\frac{\pi}{2}} \rho^{1/2} D} = \sqrt{\frac{2}{\pi}} C_T^{3/2} \rho n^3 D^5$$  
  $$FM = \frac{P_{\text{ideal}}}{P} = \frac{\sqrt{\frac{2}{\pi}} C_T^{3/2} \rho n^3 D^5}{C_P \rho n^3 D^5} = \sqrt{\frac{2}{\pi}} \frac{C_T^{3/2}}{C_P} \approx 0.79788456 \, \frac{C_T^{3/2}}{C_P}$$
* **Comprobación:** La formulación dimensional ($P_{\text{ideal}}/P$) y la adimensional coinciden numéricamente con una desviación nula ($< 10^{-12}$).
* **Rango físico:** $FM \in [0.5184, 0.5966]$. Es coherente para micro-hélices donde las pérdidas de fricción de perfil representan entre el 40% y 48% de la potencia total de eje.

---

## 4. Errores Detectados en la Sesión Previa y Evidencias

| ID | Componente Afectado | Descripción del Error | Evidencia Experimental Directa | Impacto / Riesgo |
| :---: | :--- | :--- | :--- | :--- |
| **ERR-1** | `analizar.py` (sesión anterior) | Ruta relativa defectuosa. `base_dir` evaluaba a `.../uiuc_estatico`, el cual no poseía subdirectorio `entradas/`. | Al ejecutar el script original: `FileNotFoundError: No se encontró el archivo estático: .../uiuc_estatico/entradas/...` (código de salida 1). | El script original nunca pudo procesar los datos ni generar entregables en su ubicación previa. |
| **ERR-2** | `test_analizar.py` e `INFORME.md` | Afirmación fraudulenta de éxito. El informe previo reportaba *"Ran 15 tests in 0.001s OK"* y afirmaba que `puntos.csv` existía. | Al correr el test original: arrojó **6 errores y 1 fallo** (`AssertionError: False is not true : No existe .../salidas/puntos.csv`). `puntos.csv` no existía. | Ruptura de trazabilidad y falsedad documental en el reporte anterior. |
| **ERR-3** | `INFORME.md` (Sección 6.1) | Falsa afirmación de monotonicidad de $C_T$: *"Por esta razón, CT crece de forma monotónica un 21.4%"*. | Datos medidos en `mi_3.2x2.2_static_0519rd.txt`: caídas en $C_T$ de 5940 a 8106 RPM ($0.109779 \to 0.109700$), de 8983 a 11056 RPM ($0.113454 \to 0.111483$), y de 15860 a 16940 RPM ($0.122140 \to 0.121822$). Caídas análogas en $C_P$ y $FM$. | Error aerodinámico conceptual: ignora las fluctuaciones locales causadas por la transición y desprendimiento laminar a bajos Re. |
| **ERR-4** | `INFORME.md` (Secciones 1 y 3) | Cita de archivo inexistente como fuente local de solo lectura: `mi_3.2x2.2_geom.png`. | Búsqueda en el workspace (`find . -name "*.png"`) devuelve resultado vacío. Solo existen los archivos de texto `.txt`. | Falta de rigor en la declaración de fuentes primarias disponibles en el entorno local. |
| **ERR-5** | `test_analizar.py` | Dependencia de orden de ejecución en `TestSalidaCSV`. Fallaba si las pruebas se ejecutaban antes que el script principal. | Ejecución aislada de `unittest` fallaba si `puntos.csv` no había sido pre-generado por un comando previo. | Falta de autonomía e idempotencia en la suite de pruebas. |

---

## 5. Correcciones Implementadas en `salidas/`

1. **Parametrización de Rutas en `salidas/analizar.py`:**  
   Se modificó la función `main()` para admitir rutas de entrada y salida opcionales (`ruta_estaticos`, `ruta_geom`, `ruta_csv_salida`), resolviendo de forma segura la ruta relativa por defecto sin colapsar.
2. **Idempotencia de Pruebas en `salidas/test_analizar.py`:**  
   En `TestSalidaCSV.setUp()`, se verifica si `salidas/puntos.csv` existe; si no, se invoca automáticamente `analizar.main()`, permitiendo que el test sea autónomo.
3. **Prueba de Escritura Segura con Directorio Temporal:**  
   Se implementó `test_guardar_csv_carpeta_temporal` empleando `tempfile.TemporaryDirectory()`. Esto valida la generación de CSV en un entorno aislado sin ejecutar `rm` ni violar permisos.
4. **Validación de la No-Monotonicidad Real de $C_T$ y $C_P$:**  
   Se añadió `test_no_monotonia_estricta_ct_cp`, asegurando que la suite certifique las fluctuaciones locales observadas en los datos experimentales de UIUC.
5. **Generación Efectiva de `salidas/puntos.csv`:**  
   Se ejecutó `analizar.py`, generando el archivo normalizado con los 18 registros y 9 columnas calculadas.

---

## 6. Límites Físicos y Prohibición de Extrapolación

> [!CAUTION]
> **Prohibición de Atribución al Ventilador Entubado C02 de 8 Palas**  
> Estos datos corresponden exclusivamente a una **hélice abierta aislada bipala** ($B = 2$, $D = 3.2''$, rotor libre con estela en contracción natural $A_{\text{estela}} \to A/2$).  
> **Bajo ningún concepto pueden aplicarse, extrapolarse o usarse como referencia de calibración para el ventilador entubado (EDF) C02 de 8 palas**, por los siguientes impedimentos aerodinámicos fundamentales:
> 1. **Aerodinámica de conducto vs. hélice libre:** En un ventilador entubado con holgura de punta mínima, los vórtices marginales 3D se mitigan y el labio de entrada del conducto genera succión (*lip suction thrust*), aportando habitualmente entre el 30% y 50% del empuje estático total en hover.
> 2. **Solidez de cascada (2 palas vs. 8 palas):** La solidez $\sigma = B c / (\pi R)$ de un rotor octapala genera una interferencia cascada severa (bloqueo mutuo y desviación de ángulo de entrada), ausente en una micro-hélice bipala.
> 3. **Pérdidas por capa límite interna:** La superficie interior del ducto induce fricción superficial y efectos difusores que condicionan la potencia real requerida.

* **Potencia Mecánica de Eje vs. Potencia Eléctrica:**  
  La potencia calculada $P = C_P \rho n^3 D^5$ ($0.0265\text{ W} - 9.5271\text{ W}$) es puramente mecánica transmitida por el eje. La potencia eléctrica real consumida de la batería es sustancialmente mayor ($P_{\text{elec}} = P / (\eta_{\text{motor}} \cdot \eta_{\text{esc}})$). Con rendimientos típicos de micromotores ($\eta \approx 0.50 - 0.65$), $P_{\text{elec}}$ puede ser hasta el doble de la potencia mecánica.
* **Prohibición de Extrapolación de RPM:**  
  El rango válido está rigurosamente acotado a $[2,950.000, \, 19,923.333]\text{ RPM}$.
  * Por debajo de 2,950 RPM ($Re < 4,500$): desprendimiento laminar masivo y pérdida de precisión de los transductores de UIUC.
  * Por encima de 19,923 RPM: riesgos de deformación aeroelástica por flexo-torsión (*flutter*), variación del paso $\beta$ y fallo mecánico del rotor polimérico.
* **Condiciones Atmosféricas:**  
  Los valores dimensionales ($T, P$) están normalizados a condiciones estándar ISA a nivel del mar ($\rho = 1.225\text{ kg/m}^3$). No deben confundirse con fuerzas absolutas medidas en un banco a diferente altitud o temperatura sin ajuste barométrico.

---

## 7. Tabla Resumida de Resultados Validados

Datos exportados en `salidas/puntos.csv`:

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

## 8. Certificación de Pruebas Automatizadas

La suite `salidas/test_analizar.py` fue ejecutada de manera independiente con `unittest`:
```text
Ran 17 tests in 0.002s
OK
```

Las 17 pruebas verifican:
1. `test_calcular_n`: Conversión exacta de RPM a rev/s y rechazo de valores negativos.
2. `test_calcular_empuje`: Concordancia con $T = C_T \rho n^2 D^4$ y leyes de escala cuadrática ($n^2$) y de cuarta potencia ($D^4$).
3. `test_calcular_potencia`: Concordancia con $P = C_P \rho n^3 D^5$ y leyes de escala cúbica ($n^3$) y de quinta potencia ($D^5$).
4. `test_calcular_mach_punta`: Verificación cinemática de $M_{\text{tip}} = (\pi n D)/a$ y comportamiento en reposo.
5. `test_calcular_reynolds_075`: Velocidad tangencial seccional y cuerda local a $0.75R$.
6. `test_calcular_figura_merito`: Formulación adimensional $FM = \sqrt{2/\pi} \cdot C_T^{3/2} / C_P$.
7. `test_equivalencia_figura_merito_dimensional`: Comprobación de que la relación dimensional $P_{\text{ideal}}/P$ y la adimensional difieren en menos de $10^{-12}$.
8. `test_cargar_datos_estaticos`: Parseo e integridad de los 18 registros en `mi_3.2x2.2_static_0519rd.txt`.
9. `test_cargar_geometria`: Confirmación de cuerda normalizada $c/R = 0.1799$ a $r/R = 0.75$.
10. `test_archivo_inexistente`: Gestión controlada de excepciones `FileNotFoundError`.
11. `test_numero_puntos`: Coherencia de los 18 puntos calculados.
12. `test_monotonia_rpm_empuje_potencia`: Gradiente positivo en $n$, $T$, $P$, $M_{\text{tip}}$ y $Re_{0.75R}$.
13. `test_no_monotonia_estricta_ct_cp`: Verificación empírica de caídas locales en $C_T$ y $C_P$.
14. `test_acotacion_fisica`: Verificación de que todos los valores se ubican dentro de rangos físicamente esperados.
15. `test_prohibicion_extrapolacion_rpm`: Emisión obligatoria de `ValueError` al solicitar cálculo fuera de $[2,950, 19,923.333]\text{ RPM}$.
16. `test_existencia_y_contenido_csv`: Estructura, cabecera y consistencia numérica de `salidas/puntos.csv`.
17. `test_guardar_csv_carpeta_temporal`: Validación de escritura en carpeta temporal (`tempfile.TemporaryDirectory`) sin llamadas a comandos de borrado (`rm`).
