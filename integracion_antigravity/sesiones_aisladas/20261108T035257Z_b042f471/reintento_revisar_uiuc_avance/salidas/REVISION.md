# REVISIÓN Y AUDITORÍA TÉCNICA: ANÁLISIS AERODINÁMICO UIUC (AVANCE)
## Auditoría Metrológica, Física y de Software del Ensayo Micro Invent 3.2x2.2 @ 20.051 RPM

**Fecha de Auditoría:** Noviembre 2026  
**Instalación y Fuente Oficial:** UIUC Propeller Data Site (Volume 2), University of Illinois at Urbana-Champaign  
**Conjunto de Ensayos Auditado:** `mi_3.2x2.2_0544rd_20051.txt` (avance) y `mi_3.2x2.2_static_0519rd.txt` (estático)  
**Ruta de Fuentes (solo lectura):** `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/`  
**Entregables Revisados y Corregidos:** `salidas/`  

---

### 1. Alcance y Diagnóstico General

Se realizó una auditoría independiente, física y de código sobre los entregables del avance de procesamiento UIUC (`procesar_uiuc_prop.py`, `test_procesar_uiuc_prop.py` e `informe_tecnico_uiuc_avance.md`).

**Diagnóstico General:** El modelado físico de base, la derivación dimensional y la formulación metrológica son conceptualmente sólidos y rigurosos. Sin embargo, se identificaron **5 fallos concretos** (un error de representación de rango en CLI, una vulnerabilidad de división por cero en condiciones de avance nulo, falta de aislamiento temporal en una prueba unitaria, leves imprecisiones numéricas en factores de escala textuales y rutas absolutas heredadas de sesiones previas). Todas las anomalías fueron corregidas en las copias de trabajo en `salidas/`, verificándose el 100% de las pruebas automatizadas (11/11 tests aprobados).

---

### 2. Clasificación Trazable de Variables

Conforme a las normas metrológicas, se desglosa el conjunto de variables diferenciando datos medidos, supuestos y cálculos:

| Categoría | Variable | Símbolo / Unidad | Fuente / Justificación | Rango / Valor |
| :--- | :--- | :--- | :--- | :--- |
| **Dato Medido** | Coeficiente de avance | $J$ [-] | Túnel de viento UIUC (`0544rd_20051`) | $[0.044195, 0.448667]$ (19 pts) |
| **Dato Medido** | Coeficiente de empuje | $C_T$ [-] | Balanza extensométrica UIUC | $[0.041281, 0.124104]$ |
| **Dato Medido** | Coeficiente de potencia | $C_P$ [-] | Celda de torsión/tacómetro UIUC | $[0.035779, 0.058227]$ |
| **Dato Medido** | Eficiencia registrada | $\eta_{reg}$ [-] | Sistema de adquisición UIUC | $[0.094195, 0.562131]$ |
| **Dato Medido** | Frecuencia de giro nominal | $\text{RPM}$ [rpm] | Tacómetro óptico del banco UIUC | $20.051\text{ rpm}$ |
| **Supuesto** | Diámetro de hélice | $D$ [m] | Especificación Micro Invent $3.2''$ | $0.08128\text{ m}$ ($3.2 \times 0.0254$) |
| **Supuesto** | Densidad atmosférica | $\rho$ [$\text{kg/m}^3$] | Atmósfera Estándar ISA nivel del mar | $1.225\text{ kg/m}^3$ ($15^\circ\text{C}$, $1013.25\text{ hPa}$) |
| **Supuesto** | Régimen cinemático | $n$ [$\text{rev/s}$] | Constancia de RPM nominal en corrida | $334.183333...\text{ rev/s}$ ($20051/60$) |
| **Supuesto** | Entorno fluidodinámico | Tipo de flujo | Supuesto de diseño aerodinámico | Incompresible libre, hélice aislada |
| **Cálculo** | Velocidad de avance | $V$ [$\text{m/s}$], [$\text{km/h}$] | $V = J \cdot n \cdot D$, $V_{km/h} = 3.6 \cdot V$ | $[1.2004, 12.1869\text{ m/s}]$ ($[4.32, 43.87\text{ km/h}]$) |
| **Cálculo** | Empuje dimensional | $T$ [$\text{N}$], [$\text{gf}$] | $T = C_T \rho n^2 D^4$, $T_{gf} = 1000 \cdot T / 9.80665$ | $[0.2465, 0.7410\text{ N}]$ ($[25.13, 75.56\text{ gf}]$) |
| **Cálculo** | Potencia mecánica de eje | $P$ [$\text{W}$] | $P = C_P \rho n^3 D^5$ | $[5.8028, 9.4435\text{ W}]$ |
| **Cálculo** | Potencia útil propulsiva | $P_{out}$ [$\text{W}$] | $P_{out} = T \cdot V$ | $[0.8895, 3.8319\text{ W}]$ |
| **Cálculo** | Eficiencia analítica | $\eta_{calc}$ [-] | $\eta_{calc} = J \cdot C_T / C_P = P_{out} / P$ | $[0.094196, 0.562136]$ |
| **Cálculo** | Residuo tabular | $\Delta \eta$ [-] | $\Delta \eta = \eta_{reg} - \eta_{calc}$ | $[-1.18 \times 10^{-5}, +2.34 \times 10^{-6}]$ |

---

### 3. Evaluación Técnica Detallada de los Ejes Auditados

#### 3.1. Coeficiente de Avance ($J$) y Velocidad ($V$)
- La relación $V = J \cdot n \cdot D$ se verificó dimensionalmente: $[-] \cdot [\text{s}^{-1}] \cdot [\text{m}] = [\text{m/s}]$.
- Con $n = 334.1833\text{ rev/s}$ y $D = 0.08128\text{ m}$, el factor cinemático constante es $n \cdot D = 27.162421\text{ m/s}$.
- Coherencia con ensayo estático: En `mi_3.2x2.2_static_0519rd.txt` a $19.923\text{ RPM}$ ($V=0$, $J=0$), se tiene $C_T = 0.125828$ y $C_P = 0.059879$. En el ensayo dinámico a $20.051\text{ RPM}$, el primer punto ($J = 0.044195$) registra $C_T = 0.124104$ y $C_P = 0.058227$, lo que demuestra continuidad física perfecta entre la condición de tracción pura a punto fijo y el flujo incidente de túnel.

#### 3.2. Coeficientes $C_T$, $C_P$, Empuje ($T$) y Potencia ($P$)
- Monotonía física: $C_T$ y $C_P$ decrecen de forma estrictamente monótona conforme $J$ se incrementa (el ángulo de ataque efectivo de las secciones de pala decrece al aumentar la velocidad axial).
- Factores de conversión dimensional analíticos:
  $$\rho \cdot n^2 \cdot D^4 = 1.225 \times (334.183333)^2 \times (0.08128)^4 = 5.970909\text{ N}$$
  $$\rho \cdot n^3 \cdot D^5 = 5.970909 \times 27.162421 = 162.184342\text{ W}$$
- Las transformaciones dimensionales en `salidas/procesar_uiuc_prop.py` son exactas y no sufren truncamiento intermedio.

#### 3.3. Eficiencia ($\eta$) y Metrología de Redondeo vs. Error Experimental
- Punto óptimo: La eficiencia máxima ocurre en el punto 16 ($J = 0.380780$), con $\eta_{reg} = 0.562131$ ($56.21\%$), generando $T = 0.3524\text{ N}$ y requiriendo $P = 6.4843\text{ W}$ a $V = 37.23\text{ km/h}$.
- Metrología del residuo:
  - Discrepancia máxima: $|\Delta \eta|_{max} = 1.1825 \times 10^{-5}$ ($0.00228\%$).
  - Cota de propagación por 6 decimales ASCII: $\epsilon = 0.5 \times 10^{-6} \implies |\Delta \eta|_{cota} = \eta \left( \frac{\epsilon}{J} + \frac{\epsilon}{C_T} + \frac{\epsilon}{C_P} \right) + \epsilon$.
  - En los 19 puntos, $|\Delta \eta| \le |\Delta \eta|_{cota}$. El residuo es puramente numérico.
- **Distinción crítica**: El residuo de redondeo tabular ($< 0.003\%$) **no debe equipararse** a la incertidumbre experimental del túnel de viento de UIUC (la cual oscila entre $\pm 1\%$ y $\pm 3\%$ debido a errores sistemáticos y aleatorios de la balanza de fuerza y el sensor de par a números de Reynolds bajos $Re_c \sim 20.000$). Confundir el formato de salida con la exactitud física sería un error metrológico grave.

#### 3.4. Rango Medido y Advertencias Físicas contra Extrapolación (600 km/h y Ventilador C02)
- **Extrapolación a 600 km/h ($166.67\text{ m/s}$)**:
  - Velocidad máxima ensayada: $43.87\text{ km/h}$ ($12.19\text{ m/s}$).
  - Déficit de velocidad: $556.13\text{ km/h}$ ($600\text{ km/h}$ es $13.68\times$ la velocidad máxima ensayada).
  - Coeficiente de avance necesario a 20.051 RPM: $J_{600} = 6.1359$ (frente al límite ensayado $J_{max} = 0.4487$).
  - **Imposibilidad física por 3 factores insalvables:**
    1. *Régimen de freno molinillo*: Para paso/diámetro $P/D = 2.2/3.2 \approx 0.69$, el empuje nulo ($C_T=0$) ocurre en $J \approx 0.55 - 0.60$. A $J = 6.14$, el flujo incide con ángulo fuertemente negativo; la hélice frena masivamente ($C_T \ll 0$) absorbiendo energía del aire en lugar de propulsar.
    2. *Compresibilidad y pérdida en punta*: A 600 km/h la velocidad helicoidal en punta alcanzaría $V_{punta} = \sqrt{166.67^2 + 85.33^2} \approx 187.2\text{ m/s}$ ($M_{punta} \approx 0.55$). El perfil laminar delgado ultraligero de la microhélice entra en choque, engrosamiento severo de capa límite y separación aerodinámica descontrolada.
    3. *Fallo mecánico estructural*: La presión dinámica $q = \frac{1}{2}\rho V^2$ se multiplica por 187 veces ($16.667\text{ Pa}$ frente a $89\text{ Pa}$ del ensayo). Las cargas de flexión destrozarían las palas de microescala instantáneamente.
- **Invalidez de transferencia al "ventilador C02"**:
  - *Arquitectura*: La Micro Invent es una hélice libre abierta (2 palas, solidez $\sigma \ll 0.1$, contracción libre de estela y vórtice de punta). Un ventilador entubado opera dentro de un ducto cilíndrico (con holgura radial, recuperación de presión estática difusora, estatores de desvío y solidez $\sigma > 0.5$ con 5 a 15+ álabes).
  - *Fluido*: En caso de operar en dióxido de carbono ($CO_2$), la densidad ($\rho \approx 1.84\text{ kg/m}^3$) es 50% superior a la del aire, la velocidad del sonido es sensiblemente menor ($a \approx 268\text{ m/s}$ frente a $340\text{ m/s}$), y el coeficiente adiabático $\gamma \approx 1.28$ altera drásticamente los números de Mach y Reynolds, anulando cualquier extrapolación sin ensayos dedicados.

---

### 4. Fallos Concretos Identificados y Correcciones Realizadas

A continuación se detallan los fallos detectados en el avance original y las correcciones exactas aplicadas en los entregables de `salidas/`:

#### Fallo Concreto 1: Rango de Eficiencia Mal Reportado en CLI (`salidas/procesar_uiuc_prop.py`)
- **Problema:** En el método `main()` de `procesar_uiuc_prop.py`, la impresión de variables medidas contenía valores literales fijos:
  `print(" - eta (eficiencia registrada): [0.094195 .. 0.517650]")`
  El valor `0.517650` corresponde al punto final (punto 19), pero no es el valor máximo medido. La eficiencia máxima real es `0.562131` (en el punto 16). Reportar `[0.094195 .. 0.517650]` distorsionaba el rango experimental en 4.45 puntos porcentuales. Adicionalmente, $C_T$ y $C_P$ estaban listados en orden inverso `[max .. min]`.
- **Corrección:**
  1. Se ampliaron las estadísticas en `get_summary_statistics()` calculando dinámicamente `eta_min`, `eta_max`, `CT_min`, `CT_max`, `CP_min`, `CP_max`, `J_min`, `J_max`.
  2. Se actualizó `main()` para imprimir los rangos dinámicamente:
     `eta (eficiencia registrada): [0.094195 .. 0.562131]`
     `CT (coeficiente de empuje): [0.041281 .. 0.124104]`
     `CP (coeficiente de potencia): [0.035779 .. 0.058227]`

#### Fallo Concreto 2: Riesgo de División por Cero en Avance Nulo / Estático (`salidas/procesar_uiuc_prop.py`)
- **Problema:** En el cálculo de la cota teórica de propagación de redondeo:
  `rounding_prop_bound = (eta_calc * (eps_tab / j + eps_tab / ct + eps_tab / cp) + eps_tab)`
  Si $j = 0$ (condición estática o ensayo de despegue), la expresión evalúa `eps_tab / 0.0` y arroja `ZeroDivisionError`, a pesar de que el límite analítico $\lim_{j \to 0} \eta_{calc} \frac{\epsilon}{j} = \epsilon \frac{C_T}{C_P}$ es finito y regular.
- **Corrección:** Se implementó una cláusula condicional protectora:
  ```python
  if j > 0 and ct > 0 and cp > 0:
      rounding_prop_bound = eta_calc * (eps_tab / j + eps_tab / ct + eps_tab / cp) + eps_tab
  elif cp > 0:
      rounding_prop_bound = eps_tab * (ct / cp) + eps_tab
  else:
      rounding_prop_bound = eps_tab
  ```

#### Fallo Concreto 3: Falta de Aislamiento Temporal en Suite de Pruebas (`salidas/test_procesar_uiuc_prop.py`)
- **Problema:** La prueba `test_07_csv_file_generation_and_headers` escribía directamente sobre el archivo productivo `salidas/uiuc_mi_3.2x2.2_20051_procesado.csv` sin validar la exportación en un directorio temporal aislado, lo cual podía ocultar problemas de permisos o acoplamientos de estado entre pruebas.
- **Corrección:**
  1. Se rediseñó `test_07` utilizando `tempfile.TemporaryDirectory` para validar la exportación y estructura de encabezados en un entorno temporal aislado y estéril.
  2. Se añadieron dos nuevas pruebas unitarias:
     - `test_10_summary_statistics_ranges`: Verifica que `get_summary_statistics()` reporte con exactitud los extremos de todas las variables (especialmente `eta_max = 0.562131`).
     - `test_11_zero_division_guard`: Verifica la robustez metrológica ante puntos singulares con $J=0$.

#### Fallo Concreto 4: Factores de Escala Textuales y Vínculos Rotos en el Informe Previo
- **Problema:**
  1. En `informe_tecnico_uiuc_avance.md` (sección 2.3), los factores de escala impresos en texto eran $5.970834\text{ N}$ y $162.179048\text{ W}$, discrepando ligeramente con la evaluación exacta de $n = 20051/60\text{ rev/s}$ ($5.970909\text{ N}$ y $162.184342\text{ W}$).
  2. Los hipervínculos en la sección 7.1 apuntaban a rutas absolutas caducadas de una sesión sandbox previa (`aero_20261108T032826Z_13ced8ae_9o_xznyz`).
- **Corrección:** Se corrigieron ambos factores en el informe y se restablecieron los enlaces a la sesión actual.

#### Fallo Concreto 5: Resolución de Rutas de Trabajo en CLI
- **Problema:** Tanto el script como las pruebas dependían de `parent.parent`, fallando si se invocaban directamente desde la raíz del proyecto sin situar el script en subcarpetas.
- **Corrección:** Se implementó búsqueda automática de la carpeta base inspeccionando `entradas/` tanto en `parent.parent` como en `Path.cwd()`.

---

### 5. Resumen de Pruebas Ejecutadas y Verificación

La suite de pruebas fue ejecutada en el sandbox local con Python 3 (`salidas/test_procesar_uiuc_prop.py`). Se superaron 11 pruebas unitarias y físicas rigurosas:

```
test_01_input_file_integrity: Existencia y presencia de 19 puntos UIUC ............ OK
test_02_velocity_transformation: Transformación cinemática V = J*n*D ............. OK
test_03_thrust_transformation: Transformación analítica de empuje T .............. OK
test_04_power_transformation_and_balance: Balance de potencia P y Pout .......... OK
test_05_rounding_vs_measurement_error: Distinción redondeo vs error experimental . OK
test_06_measured_range_and_600kmh_comparison: Déficit respecto a 600 km/h ........ OK
test_07_csv_file_generation_and_headers: Exportación en carpeta temporal e isolated OK
test_08_aerodynamic_monotonicity_and_peak: Monotonía de CT/CP y pico de eta ..... OK
test_09_prohibition_rules_validation: Rechazo de 600 km/h y ventilador C02 ....... OK
test_10_summary_statistics_ranges: Verificación de extremos dinámicos (eta_max) .. OK
test_11_zero_division_guard: Protección analítica ante avance nulo (J=0) ......... OK

----------------------------------------------------------------------
Ran 11 tests in 0.005s (OK)
```

---

### 6. Entregables Generados en `salidas/`

Todos los archivos han sido generados en `salidas/` con permisos de lectura y escritura independientes (creados mediante `shutil.copyfile` o generados directamente):

1. [`procesar_uiuc_prop.py`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_uiuc_avance/salidas/procesar_uiuc_prop.py): Script corregido de procesamiento de datos UIUC, con cálculo dinámico de estadísticas y protección ante división por cero.
2. [`test_procesar_uiuc_prop.py`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_uiuc_avance/salidas/test_procesar_uiuc_prop.py): Suite de 11 pruebas unitarias y de consistencia física con aislamiento en carpetas temporales.
3. [`uiuc_mi_3.2x2.2_20051_procesado.csv`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_uiuc_avance/salidas/uiuc_mi_3.2x2.2_20051_procesado.csv): Tabla de datos dimensionales y adimensionales con metadatos descriptivos completos.
4. [`informe_tecnico_uiuc_avance.md`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_uiuc_avance/salidas/informe_tecnico_uiuc_avance.md): Informe técnico de ingeniería actualizado con constantes precisas y trazabilidad.
5. [`REVISION.md`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_uiuc_avance/salidas/REVISION.md): Este documento formal de auditoría y revisión técnica.

---

### 7. Limitaciones Técnicas del Estudio

1. **Rango Operativo Válido:** Los datos procesados aplican estrictamente a velocidades de avance entre $4.32\text{ km/h}$ y $43.87\text{ km/h}$ ($J \in [0.044, 0.449]$) a $20.051\text{ RPM}$ nominales. No son válidos fuera de este rango.
2. **Efectos de Escala a Bajo Reynolds:** La hélice Micro Invent 3.2x2.2 opera a $Re_{cuerda} \approx 15.000 - 30.000$. Los coeficientes $C_T$ y $C_P$ no son escalables geométricamente a hélices de mayor envergadura sin corrección por flujo laminar separado.
3. **Incompatibilidad de Transferencia:** Queda estrictamente desaconsejada cualquier extrapolación a velocidades de crucero elevadas ($600\text{ km/h}$) o la transferencia de estos coeficientes a ventiladores entubados o circuitos de fluidos no gaseosos atmosféricos ($CO_2$).
