# SÍNTESIS TÉCNICA: CONTROL DE FUENTES, TRAZABILIDAD Y NO PROPAGACIÓN DE ERRORES

**Fecha:** 8 de noviembre de 2026 | **Ámbito:** Directorio aislado `sintesis_control_fuentes` (sin red, sin MCP)  
**Propósito:** Síntesis ejecutiva de directrices epistémicas para preservar trazabilidad y erradicar la propagación de fallos de revisiones previas.

---

## 1. Integridad Epistémica, No Validación y Alcance Documental

1. **Ausencia de Validación Científica Vehicular:** **Ningún vehículo ni arquitectura evaluada (A07, A08, C01, C02) está científicamente validado.** Son modelos conceptuales preliminares: solvers CFD históricos pausados o sin convergencia de residuos, balances inerciales abiertos (`physical_mass_CG_and_inertia_closed: false`), hardware real sin calificar (`actual_hardware_qualified: false`) y mapa propulsivo instalado inexistente (`installed_map_available: false`).
2. **Delimitación de Fuente NASA:** [`NOTA-NASA-EDF.md`](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md) es una **nota técnica secundaria local**. **Queda prohibido atribuirla al artículo completo de la NASA** (*Weinstein et al., 2024, NTRS 20230017299*), cuyo documento PDF íntegro no ha sido leído en esta sesión.

---

## 2. Resolución de los Cuatro Errores Críticos Auditados

### 1) Masa de Reserva sin Asignar Estrictamente Desconocida
* **Error previo:** Atribuir *"regla crítica de no nulidad ($m \neq 0\text{ kg}$)"* a las 54 reservas de `BOM_GEOMETRICA_PARCIAL.csv`.
* **Corrección:** La ausencia de asignación no autoriza a asumir $m = 0$ (falso cierre), pero tampoco $m \neq 0$. El estado epistémico es **estrictamente DESCONOCIDO (`[DESCONOCIDO]`)**.
* **Sustento:** Existen interfaces vacías de paso de aire como `canal_axial_60_exterior_56_interior` ($V = 291.539,80\text{ mm}^3$, **$79,02\%$ del volumen sin asignar** y $14,58\%$ del vehículo) e `interfaz_posterior_reservada` ($1.507,96\text{ mm}^3$) cuya masa agregada puede ser **cero ($m = 0$)** si no se instalan conductos densos ni tobera física. Asimismo, los sobres volumétricos (*envelopes* de 4 actuadores y 4 cojinetes) y el solapamiento en uniones legadas (*material sharing*) impiden imputar masa multiplicando volumen bruto por densidades arbitrarias.
* **Trazabilidad:** Conservar celdas vacías (`None`/`NaN`), clasificar como `[DESCONOCIDO]` y mantener abierto el balance inercial. [Ref: DICTAMEN BOM](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T035419Z_55aa97fb/corregir_bom_incertidumbre/salidas/DICTAMEN.md).

### 2) Identificación Estricta del EDF de la Nota y Rechazo de Marcas no Sustentadas
* **Error previo:** `REVISION.md` inventó las marcas *"EDF comercial Schübeler de 130 mm"* y *"motor brushless Hacker"*, y redujo el ensayo a un *"banco estático abierto"*.
* **Corrección:** [`NOTA-NASA-EDF.md`](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md) identifica exclusivamente:
  - **Ventilador:** **Jetfan 130 Pro** (10 palas, 7 álabes fijos; diámetro pala $5,11\text{ in}$ / $129,79\text{ mm}$, conducto exterior $5,23\text{ in}$ / $132,84\text{ mm}$).
  - **Motor:** **Sin marca indicada en la nota**; caracterizado únicamente por datos medidos: masa $1.100\text{ g}$, diámetro $56\text{ mm}$, potencia continua máxima $7\text{ kW}$.
  - **Instalación:** Ensayado en el **túnel de baja velocidad de 12 pies de NASA Langley** ($\alpha \in [0^\circ, 30^\circ]$, presión dinámica $q \in [0, 6]\text{ psf}$).
  - **Régimen medido (extremos no simultáneos):** $2.875\text{–}25.150\text{ rpm}$, empuje $0\text{–}21,25\text{ lbf}$, potencia eléctrica CC $190\text{–}6.420\text{ W}$; modelo dinámico de segundo orden para velocidad de motor.
  - **Contexto:** Ensayado para el proyecto **SUSAN**, no transferible a C02 ni al módulo D82.
* **Trazabilidad:** Rechazar marcas espurias (*Schübeler*, *Hacker*). [Ref: DICTAMEN NASA](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T035419Z_55aa97fb/corregir_fuente_nasa/salidas/DICTAMEN.md).

### 3) No Confundir Entrada no Suministrada con Archivo Inexistente
* **Error previo:** `CORRECCIONES.md` afirmó que `matriz_verificacion_detallada.csv` *"nunca fue creado en salidas/"*, declarándolo inexistente.
* **Corrección:** El archivo **sí existía físicamente** ($20.148\text{ bytes}$, 99 filas para EST-01, EST-02 y EST-03) en la sesión upstream `13ced8ae`. El error provino de un sesgo de inventario parcial: omitir la copia al entorno local downstream `recuperar_cfd`.
* **Principio rector:** *"No infieras que un archivo no copiado no existe"*. La ausencia local debe reportarse como *"entrada no suministrada a esta sesión"*, jamás como inexistencia en el repositorio. [Ref: DICTAMEN CFD](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T035419Z_55aa97fb/corregir_cfd_inventario/salidas/DICTAMEN.md).

### 4) Orientación CAD $+y$ a la Derecha según Conversión Documentada y Quiralidad
* **Error previo:** `INFORME_EQUILIBRIO_CG.md` declaró que CAD $+y$ era *"izquierda"* mientras afirmaba que se invertía para ser izquierda en FLU (contradicción lógica).
* **Corrección cinemática:** Matriz $R_{\text{flight\_from\_CAD}} = \operatorname{diag}(-1, -1, 1)$ en `C02_CANDIDATA.json`. Con FLU canónico ($+x_{\text{FLU}}$ adelante/nariz, $+y_{\text{FLU}}$ izquierda/babor, $+z_{\text{FLU}}$ arriba):
  - $x_{\text{CAD}} = -x_{\text{FLU}} \implies$ **CAD $+x$ apunta hacia la COLA** (popa); CAD $-x$ apunta a la NARIZ.
  - $y_{\text{CAD}} = -y_{\text{FLU}} \implies$ **CAD $+y$ corresponde a la DERECHA** (estribor); CAD $-y$ a la IZQUIERDA.
  - Quiralidad: $\det(R) = +1,0 \in SO(3)$ (rotación propia de $180^\circ$ en $z$) conserva la regla de la mano derecha ($\hat{x}_{\text{cola}} \times \hat{y}_{\text{derecha}} = \hat{z}_{\text{arriba}}$). Definir CAD $+y$ a la izquierda formaría un triedro levógiro no admisible ($\hat{x} \times \hat{y} = -\hat{z}$).
* **Distinción de impacto:** Es un **error documental y de nomenclatura semántica**. No altera magnitudes del modelo bilateral simétrico ($W = 49,033\text{ N}$, envolvente octogonal, $F_{z,\max}$, $\Delta f_4$, empujes nominales en $y_{cg}=0$). En condiciones asimétricas ($y_{cg} \neq 0$), los valores de fuerza son correctos pero sus etiquetas laterales están permutadas ($M1 \leftrightarrow M2$, $M3 \leftrightarrow M4$); trasladarlo a hardware o FCU invertiría el mando de alabeo (*roll*). [Ref: DICTAMEN CG](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T035419Z_55aa97fb/corregir_ejes_cg/salidas/DICTAMEN.md).

---

## 3. Identificación de Dictámenes de Agentes (Sujetos a Contraste Obligatorio)

Las siguientes afirmaciones en el expediente son **exclusivamente dictámenes periciales emitidos por agentes/subagentes de IA** y **requieren contraste preceptivo frente a fuentes primarias**:

1. **Dogma de masa no nula ($m \neq 0$) en reservas:** Dictamen de agente en `INFORME_AUDITORIA_BOM.md` $\to$ *Contraste:* `BOM_GEOMETRICA_PARCIAL.csv` refuta el dogma; rige principio de indeterminación.
2. **Atribución de masa nula ($m = 0$) a interfaz axial:** Dictamen deductivo de subagente G3 $\to$ *Contraste:* Requiere confirmación contra especificaciones de ingeniería sobre si el canal albergará conducto estructural o vano de aire.
3. **Atribución de marcas Schübeler y Hacker:** Dictamen espurio de agente en `REVISION.md` $\to$ *Contraste:* `NOTA-NASA-EDF.md` refuta ambas marcas y acredita Jetfan 130 Pro con motor sin marca.
4. **Declaración de inexistencia de matriz detallada:** Dictamen erróneo de agente en `CORRECCIONES.md` $\to$ *Contraste:* Archivos físicos de la sesión `13ced8ae` refutan la inexistencia (sesgo de copia).
5. **Definición de CAD $+y$ como izquierda:** Dictamen contradictorio de agente en `INFORME_EQUILIBRIO_CG.md` $\to$ *Contraste:* Matriz $R$ en `C02_CANDIDATA.json` demuestra analíticamente que CAD $+y$ es la derecha.
6. **No aceptación de cargas CFD:** Dictamen pericial de subagente G2 $\to$ *Contraste:* Verificado en `INFORME-FINA-800.md` (residuos $Ux, Uy, k > 10^{-5}$ incumplen convergencia; no se aceptan cargas).

---

## 4. Matriz de Clasificación Epistémica de Parámetros

| Categoría Epistémica | Parámetro / Magnitud | Valor / Rango | Unidades | Fuente Primaria | Criterio Metodológico |
|---|---|---:|:---:|---|---|
| **`[DATO MEDIDO]`** | Diámetro pala / ducto Jetfan 130 Pro | $5,11$ / $5,23$ | $\text{in}$ ($129,8$ / $132,8\text{ mm}$) | `NOTA-NASA-EDF.md` | Medición física en túnel NASA. |
| **`[DATO MEDIDO]`** | Masa y potencia continua motor NASA | $1.100$ / $7$ | $\text{g}$ / $\text{kW}$ | `NOTA-NASA-EDF.md` | Banco de ensayo (motor no calificado C02). |
| **`[DATO MEDIDO]`** | Extremos operativos Jetfan NASA | $2.875\text{–}25.150$ / $0\text{–}21,25$ / $190\text{–}6.420$ | $\text{rpm}$ / $\text{lbf}$ / $\text{W}$ | `NOTA-NASA-EDF.md` | Túnel 12 pies; extremos desacoplados. |
| **`[DATO MEDIDO]`** | $C_p$ experimental RAE2822 ($x/c=0,0002$) | $-0,4219$ | Adimensional | `INFORME-NASA-SU2.md` | Medición túnel transónico. |
| **`[SUPUESTO]`** | Masa objetivo C02 y reserva provisional | $5,000$ / $0,750$ | $\text{kg}$ | `C02_CANDIDATA.json` | Cota preliminar de diseño. |
| **`[SUPUESTO]`** | Densidad hipótesis mixta C02 | $1600$ | $\text{kg/m}^3$ | `MASA_INERCIA_PARCIAL.json` | Hipótesis paramétrica provisional. |
| **`[SUPUESTO]`** | Velocidad flujo banco conducto / Fuente | $20,0$ / $-1,0$ | $\text{m/s}$ / $\text{N}$ | `INFORME-FINA-800.md` / `F1N` | Contorno forzado y fuente puntual ideal. |
| **`[SUPUESTO]`** | Matriz $R_{\text{flight\_from\_CAD}}$ | $\operatorname{diag}(-1, -1, 1)$ | Adimensional | `C02_CANDIDATA.json` | Definición de cambio de base FLU-CAD. |
| **`[CÁLCULO]`** | Volumen total CAD C02 (316 piezas) | $1.999.635,12$ | $\text{mm}^3$ | `BOM_GEOMETRICA_PARCIAL.csv` | Integración numérica B-Rep nominal. |
| **`[CÁLCULO]`** | Masa asignada (262 piezas) / Remanente | $2,783990$ / $1,466010$ | $\text{kg}$ | `MASA_INERCIA_PARCIAL.json` | Sumatoria determinista bajo hipótesis mixta. |
| **`[CÁLCULO]`** | Determinante $\det(R_{\text{flight\_from\_CAD}})$ | $+1,0$ | Adimensional | Álgebra matricial | Conservación quiralidad dextrógira. |
| **`[CÁLCULO]`** | Tiempo cómputo SU2 r1 transónico | $395,07$ | $\text{s}$ (CPU wall-clock) | `INFORME-NASA-SU2.md` | Tiempo de máquina (NO es tiempo físico). |
| **`[DESCONOCIDO]`**| Masa real de las 54 reservas C02 | *Indeterminada* | $\text{kg}$ | `BOM_GEOMETRICA_PARCIAL.csv` | Sin hardware calificado ($m=0$ o $m>0$). |

---

## 5. Referencias Documentales Locales Disponibles (Sin Red)

* [`NOTA-NASA-EDF.md`](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md): Nota secundaria local sobre el ventilador Jetfan 130 Pro (proyecto SUSAN).
* [`DICTAMEN.md (BOM)`](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T035419Z_55aa97fb/corregir_bom_incertidumbre/salidas/DICTAMEN.md): Auditoría de incertidumbre de masa, volumen de reservas y principio de indeterminación.
* [`DICTAMEN.md (NASA)`](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T035419Z_55aa97fb/corregir_fuente_nasa/salidas/DICTAMEN.md): Identificación fidedigna del Jetfan 130 Pro y rectificación de marcas espurias.
* [`DICTAMEN.md (CFD)`](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T035419Z_55aa97fb/corregir_cfd_inventario/salidas/DICTAMEN.md): Refutación de inexistencia de matriz detallada y no aceptación de cargas numéricas.
* [`DICTAMEN.md (CG)`](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T035419Z_55aa97fb/corregir_ejes_cg/salidas/DICTAMEN.md): Deducción cinemática de CAD $+y$ a la derecha, quiralidad y evaluación de simetría.
* [`DECISION-ARQUITECTURA.md`](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/modelos_integrados/DECISION-ARQUITECTURA.md): Selección de arquitectura de ventiladores internos y restricciones vigentes.
* [`ESTADO-VERIFICACION-GLOBAL.md`](file:///private/tmp/aero_20261108T040808Z_57ad9241_dbto_xrf/sintesis_control_fuentes/entradas/investigacion-aeronautica/ESTADO-VERIFICACION-GLOBAL.md): Estado general de seguimiento, solvers pausados y benchmarks de control.
