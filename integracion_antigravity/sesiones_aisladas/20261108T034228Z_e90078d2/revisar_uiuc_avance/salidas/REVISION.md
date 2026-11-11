# AUDITORÍA TÉCNICA Y REVISIÓN AERODINÁMICA UIUC EN AVANCE
## Análisis del Ensayo Micro Invent 3.2x2.2 @ 20.051 RPM
**Documento de Entrega:** `salidas/REVISION.md`  
**Fecha:** Noviembre 2026  
**Entorno de Trabajo:** Directorio aislado de ejecución (`revisar_uiuc_avance`)  
**Archivos de Referencia Auditados (solo lectura):**
- `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_0544rd_20051.txt`
- `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_static_0519rd.txt`
- `entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/uiuc_avance/salidas/procesar_uiuc_prop.py`
- `entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/uiuc_avance/salidas/test_procesar_uiuc_prop.py`
- `entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/uiuc_avance/salidas/informe_tecnico_uiuc_avance.md`

---

## 1. Resumen Ejecutivo de la Auditoría

Se ha realizado una auditoría exhaustiva, analítica y experimental del procesamiento aerodinámico correspondiente a los datos de túnel de viento UIUC (University of Illinois at Urbana-Champaign, UIUC Propeller Data Site Volume 2) para la microhélice **Micro Invent 3.2x2.2** a una velocidad angular nominal de **20.051 RPM**.

La auditoría evaluó:
1. La formulación matemática y física de las variables de avance ($J$, $V$), empuje ($C_T$, $T$), potencia ($C_P$, $P$) y eficiencia propulsiva ($\eta$).
2. La distinción metrológica entre datos medidos, supuestos adoptados y cálculos derivados.
3. La consistencia entre la discrepancia residual de redondeo ($\Delta \eta \sim 10^{-5}$) y la incertidumbre experimental real de los transductores ($\pm 1\%$ a $\pm 3\%$).
4. El sobre de vuelo ensayado en túnel ($4.32$ a $43.87$ km/h) frente a extrapolaciones inadmisibles (e.g. $600$ km/h) o transferencias indebidas (e.g. "ventilador C02").
5. La integridad del código y las pruebas: se identificaron **7 fallos concretos** en las copias de referencia de `entradas/`, incluyendo un fallo de resolución de rutas relativas que impedía ejecutar el script y los tests en su ubicación original.

Las copias del script y de la suite de pruebas fueron corregidas, ampliadas y colocadas en `salidas/`. Se incorporaron 14 pruebas unitarias (frente a las 9 originales), superadas al 100% con código de salida 0.

---

## 2. Auditoría Técnica Detallada de Parámetros Físicos y Metrológicos

### 2.1. Clasificación Rigurosa de Variables
Para garantizar la integridad y trazabilidad metrológica, cada variable se categoriza formalmente:

| Categoría | Variable | Unidades | Origen / Definición | Observaciones Metrológicas |
|:---|:---|:---:|:---|:---|
| **Dato Medido** | $J$ (Avance) | $[-]$ | Archivo UIUC `0544rd_20051.txt` | 19 puntos tabulados: $[0.044195, 0.448667]$ |
| **Dato Medido** | $C_T$ (Empuje) | $[-]$ | Archivo UIUC `0544rd_20051.txt` | Celda de carga del túnel: $[0.041281, 0.124104]$ |
| **Dato Medido** | $C_P$ (Potencia) | $[-]$ | Archivo UIUC `0544rd_20051.txt` | Transductor de par y tacómetro: $[0.035779, 0.058227]$ |
| **Dato Medido** | $\eta_{reg}$ (Eficiencia) | $[-]$ | Archivo UIUC `0544rd_20051.txt` | Registrado por sistema DAQ de UIUC: $[0.094195, 0.517650]$ |
| **Dato Medido** | $C_{T,static}$, $C_{P,static}$ | $[-]$ | Archivo UIUC `static_0519rd.txt` | Banco estático a 18 RPMs ($2.950$ a $19.923$ RPM) |
| **Supuesto** | $D$ (Diámetro) | $\text{m}$ | $3.2\text{ in} = 0.08128\text{ m}$ | Geometría nominal del fabricante (Micro Invent) |
| **Supuesto** | $P_{geom}$ (Paso) | $\text{m}$ | $2.2\text{ in} = 0.05588\text{ m}$ | Paso nominal ($P/D = 0.6875$) |
| **Supuesto** | $\rho$ (Densidad) | $\text{kg/m}^3$ | $1.225\text{ kg/m}^3$ | Atmósfera estándar ISA a nivel del mar ($15^\circ\text{C}$, $1013.25\text{ hPa}$) |
| **Supuesto** | $n_{nominal}$ | $\text{rev/s}$ | $20051.0 / 60 = 334.1833\text{ rev/s}$ | RPM nominal constante asumida para toda la corrida |
| **Cálculo Derivado** | $V$ (Velocidad) | $\text{m/s}$, $\text{km/h}$ | $V = J \cdot n \cdot D$, $V_{km/h} = 3.6 V$ | Rango: $[1.2004, 12.1869]\text{ m/s}$ ($[4.32, 43.87]\text{ km/h}$) |
| **Cálculo Derivado** | $T$ (Empuje) | $\text{N}$, $\text{gf}$ | $T = C_T \rho n^2 D^4$, $T_{gf} = 1000 T / g$ | Rango: $[0.2465, 0.7410]\text{ N}$ ($[25.13, 75.56]\text{ gf}$) |
| **Cálculo Derivado** | $P$ (Potencia eje) | $\text{W}$ | $P = C_P \rho n^3 D^5$ | Potencia absorbida: $[5.8028, 9.4435]\text{ W}$ |
| **Cálculo Derivado** | $P_{out}$ (Tracción) | $\text{W}$ | $P_{out} = T \cdot V$ | Potencia útil de tracción: $[0.8895, 3.8319]\text{ W}$ |
| **Cálculo Derivado** | $\eta_{calc}$ | $[-]$ | $\eta_{calc} = J \cdot C_T / C_P$ | Eficiencia clásica analítica |
| **Cálculo Derivado** | $M_{tip}$ (Mach punta) | $[-]$ | $M_{tip} = \sqrt{V^2 + (\pi n D)^2} / a$ | Rango: $[0.2508, 0.2533]$ (incompresible) |
| **Cálculo Derivado** | $Re_{0.75R}$ | $[-]$ | $Re = V_{0.75} \cdot c_{0.75} / \nu$ | Rango: $[29881, 30413]$ (régimen laminar microescala) |
| **Cálculo Derivado** | $J_0$ (Empuje nulo) | $[-]$ | Extrapolación analítica $C_T \to 0$ | $J_0 \approx 0.6084$ (5 puntos) / $0.5947$ (2 puntos) |

---

### 2.2. Análisis Específico de Parámetros Aerodinámicos

#### A. Coeficiente de Avance ($J$) y Velocidad ($V$)
1. **Definición clásica:**  
   $$J = \frac{V_\infty}{n \cdot D}$$
   donde $V_\infty$ es la velocidad del aire en el túnel, $n$ la frecuencia de rotación ($\text{rev/s}$) y $D$ el diámetro ($\text{m}$).
2. **Rango medido:** El archivo `mi_3.2x2.2_0544rd_20051.txt` contiene 19 puntos comprendidos entre $J_{min} = 0.044195$ y $J_{max} = 0.448667$.
3. **Ausencia de $J = 0$ en el ensayo de avance:**  
   En los túneles de viento aerodinámicos, no es posible medir a velocidad exactamente cero ($V = 0$) debido al límite inferior de sensibilidad del tubo Pitot-estático y a los vórtices de recirculación en la sección de ensayo. Por ello, la corrida de avance comienza en $V \approx 1.20\text{ m/s}$ ($4.32\text{ km/h}$).
4. **Validación con el banco estático complementario (`0519rd`):**  
   La carpeta de fuentes contiene `mi_3.2x2.2_static_0519rd.txt`, que registra el ensayo en banco estático puro ($V=0$, $J=0$). A la RPM máxima del banco estático ($19.923\text{ RPM}$, muy próxima a los $20.051\text{ RPM}$ nominales del ensayo dinámico):
   - $C_{T,static} = 0.125828$ frente a $C_T(J=0.044195) = 0.124104$ (diferencia de solo $-1.37\%$).
   - $C_{P,static} = 0.059879$ frente a $C_P(J=0.044195) = 0.058227$ (diferencia de solo $-2.76\%$).  
   Esto confirma rigurosamente la continuidad física inter-ensayo en $J \to 0$.

#### B. Coeficientes $C_T$, $C_P$ y Magnitudes Dimensionales
1. **Formulación adimensional estándar:**
   $$C_T = \frac{T}{\rho \cdot n^2 \cdot D^4}, \qquad C_P = \frac{P}{\rho \cdot n^3 \cdot D^5}$$
   Para los valores supuestos ($D = 0.08128\text{ m}$, $\rho = 1.225\text{ kg/m}^3$, $n = 334.1833\text{ rev/s}$):
   $$\rho \cdot n^2 \cdot D^4 \approx 5.970834\text{ N}, \qquad \rho \cdot n^3 \cdot D^5 \approx 162.179048\text{ W}$$
2. **Comportamiento aerodinámico:**  
   $C_T$ desciende monótonamente de $0.124104$ a $0.041281$ a medida que aumenta $J$, debido a la reducción del ángulo de ataque efectivo de los perfiles de pala. Igualmente, $C_P$ desciende monótonamente de $0.058227$ a $0.035779$, reflejando la menor resistencia aerodinámica de perfil requerida para sostener la rotación.

#### C. Rendimiento Propulsivo ($\eta$) y Metrología de Redondeo
1. **Definición de eficiencia propulsiva:**
   $$\eta = \frac{P_{out}}{P} = \frac{T \cdot V}{P} = \frac{(C_T \cdot \rho \cdot n^2 \cdot D^4) \cdot (J \cdot n \cdot D)}{C_P \cdot \rho \cdot n^3 \cdot D^5} = J \cdot \frac{C_T}{C_P}$$
2. **Pico de eficiencia:**  
   El rendimiento máximo registrado es $\eta_{max} = 56.2131\%$ en el punto 16 ($J = 0.380780$, $V = 37.23\text{ km/h}$, $T = 0.3524\text{ N}$, $P = 6.48\text{ W}$).
3. **Discrepancia residual $\Delta \eta = \eta_{reg} - \eta_{calc}$:**  
   La diferencia punto a punto es minúscula ($|\Delta \eta|_{max} = 1.1825 \times 10^{-5}$, error relativo $0.00228\%$).
4. **Demostración de cota de redondeo tabular:**  
   Dado que las variables $J$, $C_T$, $C_P$ y $\eta$ están representadas con 6 cifras decimales, la semicifra máxima de redondeo es $\epsilon = 0.5 \times 10^{-6}$. La cota teórica de primer orden es:
   $$|\Delta \eta|_{cota} = \eta_{calc} \left( \frac{\epsilon}{J} + \frac{\epsilon}{C_T} + \frac{\epsilon}{C_P} \right) + \epsilon$$
   En la totalidad de los 19 puntos, $|\Delta \eta| \le |\Delta \eta|_{cota}$.
5. **Distinción cardinal frente al error experimental:**  
   El residuo $\sim 10^{-5}$ es exclusivamente un artefacto de formateo ASCII en doble precisión a texto plano. La incertidumbre experimental real del túnel de viento (calibración de galgas extensométricas, presión dinámica y tara aerodinámica a números de Reynolds ultrabajos $Re \sim 30.000$) es de **$\pm 1\%$ a $\pm 3\%$**, lo cual supera en más de **400 a 1000 veces** la cota de redondeo numérico.

#### D. Extrapolación de Empuje Nulo ($J_0$)
Ajustando por mínimos cuadrados los últimos 5 puntos ensayados ($J \in [0.358, 0.449]$):
$$C_T(J) \approx -0.2601 \cdot J + 0.1582 \implies J_0 = \frac{0.1582}{0.2601} \approx 0.6084$$
Y mediante extrapolación de los últimos 2 puntos: $J_0 \approx 0.5947$.  
Esto concuerda estrechamente con el paso geométrico nominal $P/D = 2.2 / 3.2 = 0.6875$, situándose ligeramente por debajo debido al efecto de pérdida tridimensional y bajo número de Reynolds en la punta de pala.

---

### 2.3. Advertencias Físicas contra Extrapolación

```
                               SOBRE DE ENSAYO vs EXTRAPOLACIÓN
      [ Ensayado en Túnel UIUC ]                               [ Extrapolación Inadmisible ]
  0 km/h                      43.87 km/h                                            600 km/h
  |------------------------------|----------------------------------------------------|
  J: 0.044 -> 0.449               J0 ≈ 0.61                                       J = 6.14
  T: 0.74 N -> 0.25 N (Tracción)  T = 0                                           T << 0 (Freno Molinete)
  q: ~90 Pa                       q: ~90 Pa                                       q: 17.014 Pa (189x)
  Régimen: Laminar Re~30k         Régimen: Transición                             Régimen: Choque / Rotura
```

#### 1. Imposibilidad de Extrapolación a 600 km/h
- **Déficit de velocidad:** $\Delta V = 600.0 - 43.87 = 556.13\text{ km/h}$ ($154.48\text{ m/s}$). La velocidad objetivo es **$13.68\times$** la máxima ensayada.
- **Régimen de Freno Molinete (Windmilling):**  
  A $600\text{ km/h}$ y $20.051\text{ RPM}$, el coeficiente de avance hipotético sería:
  $$J_{600} = \frac{166.67\text{ m/s}}{(334.1833\text{ rev/s}) \cdot (0.08128\text{ m})} = 6.1359$$
  Como $J_{600} \approx 6.14 \gg J_0 \approx 0.61$, el ángulo de pala relativo es fuertemente negativo. La hélice deja de generar tracción y se convierte en un freno aerodinámico de arrastre masivo ($C_T \ll 0$), absorbiendo energía del aire y transmitiendo sobretorque destructivo al eje.
- **Carga de Presión Dinámica y Colapso Estructural:**  
  La presión dinámica del flujo libre pasa de:
  $$q_{ensayo,max} = \frac{1}{2} (1.225) (12.187)^2 \approx 90.96\text{ Pa}$$
  a:
  $$q_{600} = \frac{1}{2} (1.225) (166.667)^2 \approx 17.014\text{ Pa}$$
  Un incremento de **$187\times$**. La microhélice Micro Invent 3.2x2.2 (peso inferior a $1\text{ gramo}$, pala delgada no reforzada) colapsaría instantáneamente por sobrecarga de flexión o flutter aeroelástico destructivo.
- **Efectos de Compresibilidad en Punta de Pala:**  
  La velocidad resultante de punta sería $V_{punta} = \sqrt{166.67^2 + 85.33^2} \approx 187.2\text{ m/s}$ ($M_{punta} \approx 0.55$). A este número de Mach, los perfiles de placa curvada de microescala sufren gradientes adversos intensos de presión y desprendimiento masivo de capa límite.

#### 2. Incompatibilidad de Transferencia de Datos al "Ventilador C02"
- **Topología y Aerodinámica de Conducto:**  
  La hélice Micro Invent 3.2x2.2 es una hélice abierta libre con contracción de vena según Froude-Rankine y vórtices de punta libre. Un ventilador (axial o centrífugo, como el "ventilador C02") opera entubado (ducted fan), donde la holgura de punta (tip clearance) confina el flujo, el ducto genera sustentación en el labio y recuperación de presión estática por difusión, y los álabes estatores recuperan la energía del swirl.
- **Solidez y Número de Álabes:**  
  Esta hélice consta de 2 palas con solidez baja ($\sigma \ll 0.1$). Un ventilador opera con solidez elevada ($\sigma > 0.5$) y entre 5 y 15+ álabes con acoplamiento aerodinámico cascada.
- **Fluido de Trabajo (Aire vs. CO2):**  
  El CO₂ a condiciones normales tiene densidad $\approx 1.84\text{ kg/m}^3$ (50% superior al aire), velocidad del sonido $\approx 268\text{ m/s}$ (frente a $340\text{ m/s}$) y relación de calores específicos $\gamma \approx 1.28$ (frente a $1.40$). La similitud de Reynolds y Mach queda completamente desfasada.

---

## 3. Fallos Concretos Identificados en las Copias de Referencia (`entradas/`)

Durante la auditoría de los scripts y reportes ubicados en `entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/uiuc_avance/salidas/`, se detectaron los siguientes fallos concretos:

### Fallo 1: Fragilidad en Resolución de Rutas Relativas (Error de Ejecución `FileNotFoundError`)
- **Ubicación:** `procesar_uiuc_prop.py` (líneas 384–386) y `test_procesar_uiuc_prop.py` (líneas 27–36).
- **Código defectuoso:**
  ```python
  base_dir = Path(__file__).resolve().parent.parent
  input_file = base_dir / "entradas" / "investigacion-aeronautica" / "fuentes" / "uiuc_propdb" / "mi_3.2x2.2_0544rd_20051.txt"
  ```
- **Problema concreto:** Asumía que `entradas/` residía dos niveles por encima del script. En la estructura original anidada (`sesiones_aisladas/.../uiuc_avance/salidas/`), `parent.parent` era `uiuc_avance/`, que no contenía ninguna carpeta `entradas/`. Ejecutar el script o los tests en su ubicación original lanzaba de forma inmediata un fallo fatal:
  `FileNotFoundError: Archivo de entrada no encontrado: .../uiuc_avance/entradas/...`
- **Corrección aplicada en `salidas/`:** Se implementó la función `find_workspace_root()` que busca recursivamente hacia los directorios padres la presencia de `entradas/` o `salidas/`, asegurando portabilidad desde cualquier nivel del árbol.

### Fallo 2: Omisión Total del Archivo de Ensayo Estático (`mi_3.2x2.2_static_0519rd.txt`)
- **Ubicación:** Todo el código original y el informe técnico.
- **Problema concreto:** En `entradas/.../fuentes/uiuc_propdb/` existía el archivo `mi_3.2x2.2_static_0519rd.txt` con 18 mediciones estáticas de la misma hélice ($2.950$ a $19.923$ RPM). El análisis original lo ignoró por completo, omitiendo la validación fundamental de continuidad en $J \to 0$ y perdiendo la oportunidad de contrastar los coeficientes estáticos ($C_{T,static}=0.1258$, $C_{P,static}=0.0599$) con el punto inicial de avance ($J=0.044$).
- **Corrección aplicada en `salidas/`:** Se incorporó el método `load_static_data()`, se calculó la figura de mérito y la relación empuje/potencia ($gf/W$), y se añadió la comparación inter-ensayo en `get_summary_statistics()`.

### Fallo 3: Rigidez Excesiva en la Validación de Cadenas de Texto (`validate_application_limits`)
- **Ubicación:** `procesar_uiuc_prop.py` (líneas 268–269).
- **Código defectuoso:**
  ```python
  "machine_type_compatible": target_machine_type.lower() in ["open_propeller", "helice_abierta"],
  "fluid_compatible": working_fluid.lower() in ["air", "aire"],
  ```
- **Problema concreto:** Si un usuario o aplicación pasaba `"hélice abierta"` (con tilde) o `"open propeller"` (con espacio) o `"aire (ISA)"`, la función rechazaba erróneamente la máquina o el fluido como incompatibles.
- **Corrección aplicada en `salidas/`:** Se implementó `_normalize_string()` que elimina tildes con descomposición NFKD, normaliza espacios y guiones a guiones bajos y expande el conjunto de alias válidos (`open_propeller`, `helice_abierta`, `helice`, `propeller`, `micro_propeller`, `aire_isa`, etc.).

### Fallo 4: Código Muerto y Discrepancia de Encabezados en `export_csv`
- **Ubicación:** `procesar_uiuc_prop.py` (líneas 316–333 vs 343–360).
- **Problema concreto:** Se definía una lista `fieldnames` con 16 nombres de columnas que luego nunca era utilizada porque se empleaba directamente `csv.writer` con otra lista de columnas que sí incluía unidades (e.g. `V_km_h [km/h]`).
- **Corrección aplicada en `salidas/`:** Se eliminó la variable muerta `fieldnames` y se unificó la lista de columnas con metadatos descriptivos explícitos, unidades del SI y la adición de las columnas analíticas de régimen `Mach_punta [-]` y `Re_cuerda_075 [-]`.

### Fallo 5: Hipervínculos Rotos con Rutas Absolutas de Sesión Externa
- **Ubicación:** `informe_tecnico_uiuc_avance.md` (líneas 162–165).
- **Problema concreto:** Los enlaces a los archivos apuntaban a una ruta externa efímera (`file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/...`) que violaba las directrices de aislamiento y portabilidad de los entregables.
- **Corrección aplicada en `salidas/`:** Todos los enlaces y referencias se ajustaron a la ruta absoluta del espacio de trabajo aislado actual (`file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_uiuc_avance/salidas/...`).

### Fallo 6: Ausencia de Estimación Analítica Cuantitativa de $J_0$
- **Ubicación:** `informe_tecnico_uiuc_avance.md` (sección 5.3) y código original.
- **Problema concreto:** El informe cualitativamente mencionaba que $J_0 \approx 0.55 - 0.60$, pero el script no realizaba ninguna estimación matemática ni ajuste de curva sobre los datos medidos para corroborarlo.
- **Corrección aplicada en `salidas/`:** Se implementó el método `estimate_zero_thrust_advance_ratio()`, que calcula formalmente $J_0$ por regresión local de mínimos cuadrados ($J_0 \approx 0.6084$).

### Fallo 7: Falta de Interfaz de Línea de Comandos (CLI) Parametrizable
- **Ubicación:** `procesar_uiuc_prop.py` (función `main()`).
- **Problema concreto:** `main()` no aceptaba argumentos por línea de comandos; cualquier cambio en $D$, $\rho$, RPM o rutas exigía modificar el código fuente.
- **Corrección aplicada en `salidas/`:** Se implementó `argparse` con los argumentos `--input`, `--static`, `--output`, `--diameter`, `--rpm` y `--rho`.

---

## 4. Correcciones Implementadas en las Copias de `salidas/`

A continuación se resumen las mejoras estructurales introducidas en los entregables de `salidas/`:

```
entradas/ (Solo Lectura)                                   salidas/ (Entregables Auditados)
----------------------------------------                   ----------------------------------------
procesar_uiuc_prop.py (rel-path bug,       ===> Copia &    procesar_uiuc_prop.py (find_workspace_root,
  sin datos estáticos, sin CLI)                Mejora        datos estáticos 0519rd, CLI argparse,
                                                             normalización strings, J0 analítico)

test_procesar_uiuc_prop.py (9 tests,       ===> Copia &    test_procesar_uiuc_prop.py (14 tests,
  falla en carpeta original)                   Mejora        pruebas estáticas, robustez de rutas,
                                                             100% éxito)

(No existía REVISION.md)                   ===> Generación  REVISION.md (Auditoría técnica formal,
                                                             metrología, fallos y correcciones)

(CSV sin Mach ni Reynolds)                 ===> Regenerado  uiuc_mi_3.2x2.2_20051_procesado.csv
                                                             (18 columnas, metadatos, unidades SI)
```

1. **`salidas/procesar_uiuc_prop.py`:**
   - Incorporación de `find_workspace_root()` y soporte para CLI con `argparse`.
   - Soporte dual para archivos de avance (`0544rd_20051`) y estático (`static_0519rd`).
   - Cálculo de cinemática de punta de pala ($V_{punta}$, $M_{tip}$) y número de Reynolds seccional ($Re_{0.75R}$).
   - Estimación analítica del punto de empuje nulo $J_0$.
   - Normalización robusta de cadenas de caracteres en `validate_application_limits`.
   - Limpieza de variables muertas y exportación de CSV enriquecido con 18 columnas.
2. **`salidas/test_procesar_uiuc_prop.py`:**
   - Aumento de 9 a **14 pruebas unitarias exhaustivas**.
   - Pruebas añadidas: continuidad estática (`test_06`), cálculo de $J_0$ (`test_07`), regímenes de Mach y Reynolds (`test_09`), validación robusta de strings (`test_11`), verificación de resolución de rutas (`test_13`) y manejo de archivos inválidos o corruptos (`test_14`).
3. **`salidas/uiuc_mi_3.2x2.2_20051_procesado.csv`:**
   - Regenerado con metadatos descriptivos en cabecera y 18 columnas con unidades explícitas.

---

## 5. Verificación Experimental y Ejecución de Pruebas

### 5.1. Ejecución del Procesador Aerodinámico
Se ejecutó el script `salidas/procesar_uiuc_prop.py` obteniendo el siguiente informe de salida:

```text
================================================================================
PROCESAMIENTO AERODINÁMICO UIUC - HÉLICE MICRO INVENT 3.2x2.2 @ 20.051 RPM
================================================================================
Raíz de trabajo detectada: /private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_uiuc_avance
Archivo de entrada avance: .../uiuc_propdb/mi_3.2x2.2_0544rd_20051.txt
Archivo de entrada estático: .../uiuc_propdb/mi_3.2x2.2_static_0519rd.txt
Archivo de salida CSV: .../salidas/uiuc_mi_3.2x2.2_20051_procesado.csv

--- CLASIFICACIÓN RIGUROSA DE VARIABLES ---
1. DATOS MEDIDOS / REGISTRADOS:
   - J (coeficiente de avance): [0.044195 .. 0.448667] (19 puntos)
   - CT (coeficiente de empuje): [0.124104 .. 0.041281]
   - CP (coeficiente de potencia): [0.058227 .. 0.035779]
   - eta (eficiencia registrada): [0.094195 .. 0.517650]
   - RPM nominal de ensayo: 20051.0 rpm
   - Benchmark estático (0519rd @ 19923 RPM): CT=0.125828, CP=0.059879

2. SUPUESTOS ADOPTADOS:
   - Diámetro D: 0.08128 m (3.2 pulgadas)
   - Densidad del aire rho: 1.225 kg/m3 (ISA a nivel del mar)
   - Frecuencia rotacional n: 334.1833 rev/s (constante nominal)
   - Entorno: Flujo incompresible libre, hélice rígida aislada sin conducto ni carenado

3. CÁLCULOS ANALÍTICOS DERIVADOS:
   - Rango de Velocidad: [4.32 km/h .. 43.87 km/h] ([1.20 m/s .. 12.19 m/s])
   - Rango de Empuje: [0.2465 N .. 0.7410 N] ([25.13 gf .. 75.56 gf])
   - Rango de Potencia de eje: [5.8028 W .. 9.4435 W]
   - Eficiencia máxima registrada: 56.21% en J=0.3808 (V=37.23 km/h)
   - Mach en punta de pala: [0.251 .. 0.253] (régimen subsónico incompresible)
   - Reynolds seccional (0.75R): [29881 .. 30413] (régimen laminar de microescala)
   - Coeficiente de avance de empuje nulo estimado (J0): J0 ≈ 0.6084

--- COMPARACIÓN METROLÓGICA (eta registrada vs J*CT/CP) ---
   - Máxima diferencia absoluta |eta_reg - eta_calc|: 1.1825e-05
   - Máxima diferencia relativa: 0.0023%
   - ¿Todos los puntos dentro del margen de redondeo tabular (6 decimales)?: True

--- COMPARACIÓN CON VELOCIDAD OBJETIVO DE 600 km/h ---
   - Velocidad ensayada máxima: 43.87 km/h (12.19 m/s)
   - Velocidad de referencia: 600.00 km/h (166.67 m/s)
   - Déficit de velocidad: 556.13 km/h (154.48 m/s)
   - Factor de exceso: 600 km/h es 13.68x la velocidad máxima ensayada
   - Coeficiente de avance necesario a 600 km/h: J = 6.1359
```

### 5.2. Ejecución de la Suite de Pruebas Unitarias
Se ejecutó la suite completa `salidas/test_procesar_uiuc_prop.py`:

```text
test_01_input_file_integrity (__main__.TestPropellerUIUCProcessor) ... ok
test_02_velocity_transformation (__main__.TestPropellerUIUCProcessor) ... ok
test_03_thrust_transformation (__main__.TestPropellerUIUCProcessor) ... ok
test_04_power_transformation_and_balance (__main__.TestPropellerUIUCProcessor) ... ok
test_05_rounding_vs_measurement_error (__main__.TestPropellerUIUCProcessor) ... ok
test_06_static_dataset_continuity (__main__.TestPropellerUIUCProcessor) ... ok
test_07_zero_thrust_advance_ratio (__main__.TestPropellerUIUCProcessor) ... ok
test_08_measured_range_and_600kmh_comparison (__main__.TestPropellerUIUCProcessor) ... ok
test_09_aerodynamic_regime_mach_and_reynolds (__main__.TestPropellerUIUCProcessor) ... ok
test_10_aerodynamic_monotonicity_and_peak (__main__.TestPropellerUIUCProcessor) ... ok
test_11_prohibition_rules_validation (__main__.TestPropellerUIUCProcessor) ... ok
test_12_csv_file_generation_and_headers (__main__.TestPropellerUIUCProcessor) ... ok
test_13_robust_path_resolution (__main__.TestPropellerUIUCProcessor) ... ok
test_14_error_handling_invalid_inputs (__main__.TestPropellerUIUCProcessor) ... ok

----------------------------------------------------------------------
Ran 14 tests in 0.003s

OK
```

Todas las pruebas se ejecutaron exitosamente tanto desde la raíz del espacio de trabajo como desde el subdirectorio `salidas/`, verificando la total resolución del problema de rutas relativas.

---

## 6. Archivos Generados, Pruebas Realizadas y Limitaciones

### 6.1. Archivos Generados en `salidas/`
1. [`procesar_uiuc_prop.py`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_uiuc_avance/salidas/procesar_uiuc_prop.py): Script de procesamiento corregido y auditado. Incorpora descubrimiento robusto de rutas (`find_workspace_root`), interfaz CLI completa (`argparse`), lectura e integración del dataset estático (`0519rd`), estimación de $J_0$, cálculo de Mach y Reynolds, y normalización de cadenas de texto.
2. [`test_procesar_uiuc_prop.py`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_uiuc_avance/salidas/test_procesar_uiuc_prop.py): Suite de 14 pruebas unitarias automatizadas con `unittest`.
3. [`uiuc_mi_3.2x2.2_20051_procesado.csv`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_uiuc_avance/salidas/uiuc_mi_3.2x2.2_20051_procesado.csv): Tabla CSV de salida con metadatos descriptivos en comentarios y 18 columnas con unidades normalizadas SI.
4. [`REVISION.md`](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/revisar_uiuc_avance/salidas/REVISION.md): Este informe técnico formal de auditoría y revisión.

### 6.2. Pruebas Realizadas
Se diseñaron e implementaron 14 pruebas unitarias que cubren:
- Integridad y presencia de los archivos fuente de avance y estático (`test_01`).
- Exactitud analítica de las transformaciones de velocidad, empuje, potencia y balance energético (`test_02`, `test_03`, `test_04`).
- Demostración rigurosa de cotas de redondeo numérico frente a incertidumbre de medición experimental (`test_05`).
- Continuidad y empalme inter-ensayo entre el banco estático y el primer punto de avance (`test_06`).
- Extrapolación de avance de empuje nulo $J_0$ y coherencia con paso geométrico ($P/D = 0.6875$) (`test_07`).
- Cuantificación de discrepancias respecto a $600\text{ km/h}$ y factor de exceso (`test_08`).
- Comprobación de régimen subsónico incompresible ($M_{tip} \approx 0.25$) y laminar de baja escala ($Re \approx 30.000$) (`test_09`).
- Monotonía decreciente de $C_T$ y $C_P$ y localización del óptimo de eficiencia en el punto 16 (`test_10`).
- Validación de reglas de restricción de extrapolación y compatibilidad con tolerancia a variantes léxicas (`test_11`).
- Integridad de formato, estructura y comentarios del archivo CSV generado (`test_12`).
- Portabilidad y descubrimiento de directorio raíz desde cualquier subcarpeta (`test_13`).
- Tratamiento de excepciones ante ficheros ausentes o encabezados malformados (`test_14`).

### 6.3. Limitaciones Técnicas del Análisis
1. **Validez Restringida al Sobre Ensayado:** Los datos son rigurosamente válidos únicamente para velocidades de avance entre $4.32\text{ km/h}$ y $43.87\text{ km/h}$ ($J \in [0.044, 0.449]$) y velocidad angular nominal fija de $20.051\text{ RPM}$.
2. **Supuesto de Frecuencia Rotacional Constante:** La reconstrucción dimensional de $V$ asume $n = 20051.0 / 60\text{ rev/s}$ constante. En el túnel real, el sistema DAQ mide pequeñas fluctuaciones instantáneas de RPM para adimensionalizar; la reconstrucción paramétrica con $n$ constante introduce una tolerancia residual proporcional a dicha variación.
3. **Efectos de Escala No Extrapolables:** La microhélice opera en un régimen de Reynolds ultra-bajo ($Re \sim 30.000$), donde la separación laminar gobierna el comportamiento. Estos coeficientes adimensionales ($C_T$, $C_P$) no pueden escalarse a hélices de aviación general o UAS de mayor porte sin correcciones por número de Reynolds.
4. **Incompatibilidad Absoluta con Turbomaquinaria y Fluidos Densos:** Los resultados no son transferibles bajo ninguna circunstancia a ventiladores entubados (como el ventilador C02) ni a fluidos diferentes del aire atmosférico.
