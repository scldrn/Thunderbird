# Dictamen Técnico y Epistemológico: Inventario, Verificación y Límites CFD

**Fecha:** 8 de noviembre de 2026  
**Ámbito de Ejecución:** Directorio aislado `corregir_cfd_inventario` (`/private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario`)  
**Autoridad de Emisión:** Antigravity (Auditoría Técnica y Metodológica de Dinámica de Fluidos Computacional)  
**Referencias Auditadas (Solo Lectura en `entradas/`):**  
- [INFORME-FINA-800.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-FINA-800.md)  
- [matriz_verificacion_cfd.csv](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/auditoria_cfd/salidas/matriz_verificacion_cfd.csv)  
- [matriz_verificacion_detallada.csv](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/auditoria_cfd/salidas/matriz_verificacion_detallada.csv)  
- [CORRECCIONES.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/recuperar_cfd/salidas/CORRECCIONES.md)  
**Entregables Generados (en `salidas/`):**  
- [DICTAMEN.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/salidas/DICTAMEN.md)  
- [matriz_verificacion_detallada.csv](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/salidas/matriz_verificacion_detallada.csv)  
- [matriz_verificacion_cfd.csv](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/salidas/matriz_verificacion_cfd.csv)  
**Estado General de Cargas:** **NO ACEPTADAS** (ningún solver ejecutado, reanudado ni cargas aceptadas)  

---

## 1. Marco Operacional y Protocolos de Contención

El presente dictamen ha sido elaborado bajo un régimen estricto de contención metodológica, seguridad operacional e integridad documental:
1. **Aislamiento Estricto:** Se opera de manera autónoma exclusivamente dentro del directorio asignado. No se ha accedido a la web, ni se han empleado herramientas MCP, ni se ha interactuado con archivos o rutas exteriores a este espacio de trabajo.
2. **Inactividad de Solvers y Procesos:** No se ha iniciado, reanudado ni detenido ningún solver de CFD (OpenFOAM, SU2 ni herramientas afines) ni contenedores ajenos (Docker, Apptainer). Se ha descartado explícitamente la ejecución de órdenes o comandos contenidos en las fuentes documentales auditadas.
3. **Manejo de Permisos y Copia:** Los archivos de referencia ubicados en `entradas/` han sido tratados como de solo lectura. Todo archivo copiado hacia `salidas/` para su edición ha sido duplicado mediante `shutil.copyfile` (y no `copy2`), garantizando la no herencia de atributos de solo lectura y preservando la integridad del árbol de entrada.
4. **Integridad Epistémica y Secretos:** No se han incorporado secretos de ninguna índole. Se distingue rigurosamente entre datos medidos (`[DATO MEDIDO]`), supuestos de ingeniería (`[SUPUESTO]`) y resultados numéricos calculados (`[CÁLCULO]`), conservando las unidades físicas y las fuentes primarias de procedencia.

---

## 2. Evaluación de la Afirmación Previa sobre `matriz_verificacion_detallada.csv`

### 2.1. La Afirmación Auditada
En la revisión precedente documentada en [CORRECCIONES.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/recuperar_cfd/salidas/CORRECCIONES.md#L25) (Sección 1.2, Línea 25), el auditor antecedente consignó textualmente:
> *"Referencia a Archivo Inexistente: La línea 46 de `informe_verificacion_cfd.md` declara que las tablas normalizadas se hallan en `matriz_verificacion_cfd.csv` y `matriz_verificacion_detallada.csv`. El archivo `matriz_verificacion_detallada.csv` nunca fue creado en `salidas/`, rompiendo cualquier comprobación automática de presencia o consistencia de entregables."*

### 2.2. Comprobación Empírica Frente a las Entradas
El examen directo de las entradas remitidas en este encargo refuta de forma concluyente dicha afirmación:
1. **Presencia Física Comprobada:** En la ruta de solo lectura:
   `entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/auditoria_cfd/salidas/matriz_verificacion_detallada.csv`
   se encuentra almacenada físicamente una copia completa y funcional del archivo.
2. **Propiedades del Artefacto:**
   - **Tamaño:** $20.148\text{ bytes}$.
   - **Estructura:** 100 líneas en formato CSV estándar codificado en UTF-8 (1 línea de cabecera con 12 campos y 99 filas de datos normalizados).
   - **Cobertura de Estudios:** Comprende exactamente los tres estudios evaluados en la sesión original:
     - `EST-01` (C02 Conducto Pasivo Malla Fina): 27 filas de parámetros.
     - `EST-02` (C02 Fuente Prescrita / Actuador -1 N): 25 filas de parámetros.
     - `EST-03` (RAE2822 Perfil Transónico NASA / SU2): 47 filas de parámetros.
3. **Conclusión Factual:** La afirmación de que el archivo *"nunca fue creado en salidas/"* es **falsa de facto**. El archivo sí fue creado en el directorio `salidas/` de la sesión de auditoría original (`13ced8ae`).

### 2.3. Evaluación Epistemológica: Suficiencia de Información de la Revisión Previa
Se evalúa si la revisión precedente disponía de información suficiente para emitir esa conclusión:
1. **Veredicto:** **La revisión previa no disponía de información suficiente para afirmar que el archivo nunca fue creado.** La conclusión adolece de un fallo metodológico y epistémico grave.
2. **Falacia de Sesgo de Inventario Parcial:** La revisión previa operó en un contenedor/directorio aislado (`recuperar_cfd`) al cual los operadores o el pipeline de preparación solo transfirieron una selección parcial de archivos (específicamente, incluyeron `matriz_verificacion_cfd.csv` e `informe_verificacion_cfd.md`, pero omitieron copiar `matriz_verificacion_detallada.csv`). El auditor precedente confundió la *ausencia de copia en su entorno de trabajo local* con la *inexistencia material del artefacto en el repositorio de origen*.
3. **Quebrantamiento del Principio Epistémico Fundamental:** La revisión vulneró la regla imperativa de auditoría técnica:
   > *"No infieras que un archivo no copiado no existe."*
   La ausencia de un entregable en una transferencia o réplica downstream no constituye prueba ontológica de su inexistencia upstream.
4. **Desatención de la Trazabilidad Interna:** La propia revisión precedente citó la línea 46 de `informe_verificacion_cfd.md`, donde se documentaba explícitamente la generación de `matriz_verificacion_detallada.csv`. En presencia de una cita formal que declara el entregable y de una ausencia física en el subdirectorio local de trabajo, la deducción metodológicamente rigurosa debió ser: *"el archivo no ha sido copiado o puesto a disposición en las entradas de esta sesión de revisión"*, y no la afirmación categórica e infundada de que *"nunca fue creado"*.

---

## 3. Auditoría de Calidad Técnica y Corrección de `matriz_verificacion_detallada.csv`

Al verificar el contenido íntegro de [matriz_verificacion_detallada.csv](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/auditoria_cfd/salidas/matriz_verificacion_detallada.csv), se evidencia que, aunque es un documento técnico detallado y de gran valor para la trazabilidad, arrastra inexactitudes conceptuales y de citación heredadas de la sesión original de auditoría. Se analizan a continuación dichas deficiencias y su rectificación:

### 3.1. Estudio 1: C02 Conducto Pasivo Malla Fina (`EST-01`)
*Fuente de referencia directa:* [INFORME-FINA-800.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-FINA-800.md)

1. **Celda 82708 — Variación Iterativa vs. Gradiente Espacial (Fila 3 de Datos):**
   - *Inexactitud original:* El parámetro fue registrado como `Celda de gradiente crítico`, indicando en notas `Foco de variación máxima DeltaU`.
   - *Corrección técnica:* Las líneas 28 y 34 de `INFORME-FINA-800.md` señalan textualmente: *"El máximo local de ΔU aumentó aproximadamente 3,31 veces... En 780–800 ese máximo está en la celda 82708, centro aproximado (−0,005803; −0,011252; −0,011185) m"*. Se trata de una variación iterativa nodal ($\Delta U = 1,141586\text{ m/s}$), **no de un gradiente espacial de velocidad** ($\nabla U$). Se renombra el parámetro a `Celda de máxima variación iterativa DeltaU` **`[CÁLCULO]`**.
2. **Atribución Falsa de la Densidad Numérica $\rho$ (Fila 8 de Datos):**
   - *Inexactitud original:* Registró la densidad de fluido de $1,225\text{ kg/m}^3$ citando `INFORME-FINA-800.md, Línea 30`.
   - *Corrección técnica:* La línea 30 de `INFORME-FINA-800.md` únicamente contiene la expresión algebraica adimensionalizadora `Defecto CV final / (ρ·20²·A)`, sin especificar ningún valor numérico de $\rho$. La magnitud numérica $1,225\text{ kg/m}^3$ es un **`[SUPUESTO]`** originado en la línea 5 de `INFORME-F1N-PRELIMINAR.md`. Se rectifica la fuente primaria a `INFORME-F1N-PRELIMINAR.md (Línea 5)` y se documenta que en `FINA-800` solo figura la variable simbólica.
3. **Deriva Global de Fuerza vs. Componente Z (Fila 18 de Datos):**
   - *Inexactitud original:* Se rotuló como `Deriva normalizada de fuerza Z` citando la Línea 22 de `INFORME-FINA-800.md`.
   - *Corrección técnica:* La línea 22 de `INFORME-FINA-800.md` certifica expresamente: *"las derivas normalizadas de fuerza y momento son 5,42159×10⁻⁶ y 1,28190×10⁻⁵"*. El informe primario define esta cifra como deriva global de fuerza, sin limitarla al eje axial Z. Se renombra el parámetro a `Deriva normalizada de fuerza global` **`[CÁLCULO]`**.
4. **Verificación Positiva de Ventana de Presión y Flujo (Filas 25 y 26 de Datos):**
   - A diferencia de la matriz resumida previa (`matriz_verificacion_cfd.csv`), que incurrió en el error de afirmar que $\Delta p$ y el flujo ocurrían "en iter 600", `matriz_verificacion_detallada.csv` registró correctamente:
     - `Diferencia de presión estática (780-800)` = $194,2659\text{ Pa}$ **`[CÁLCULO]`**.
     - `Diferencia nominal de flujo de energía mecánica` = $20,7445\text{ W}$ **`[CÁLCULO]`**.
   - Esto evidencia que la matriz detallada ya poseía mayor precisión en la delimitación de ventanas que la matriz sintética.
5. **No Convergencia de Residuos:**
   - Se ratifica el estado de fallo conjunto en los residuos de velocidad y turbulencia: $Ux = 1,52738 \times 10^{-5}$ (umbral $10^{-5}$), $Uy = 1,74918 \times 10^{-5}$ (umbral $10^{-5}$) y $k = 3,38576 \times 10^{-5}$ (umbral $10^{-5}$) **`[CÁLCULO]`**.

### 3.2. Estudio 2: C02 Conducto Fuente Axial -1 N (`EST-02`)
*Fuente de referencia:* [INFORME-F1N-PRELIMINAR.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/recuperar_cfd/salidas/CORRECCIONES.md#L51-L60)

1. **Reacción Neta de Banco (Fila 40 de Datos):**
   - *Inexactitud conceptual:* Se registró como identidad estricta $+0,0135914\text{ N}$.
   - *Corrección técnica:* Procede de sumar la fuerza sobre paredes ($-0,986409\text{ N}$) **`[CÁLCULO]`** y la reacción de la fuente sobre el banco ($+1,0\text{ N}$) **`[SUPUESTO]`**. La fuente primaria (`INFORME-F1N-PRELIMINAR.md`, Línea 24) especifica la relación como una aproximación: $Z \approx +0,0135914\text{ N}$ **`[CÁLCULO]`**. Se ajusta la nota metodológica para destacar su naturaleza aproximada y residual sobre el banco.
2. **Significado del Trabajo de la Fuente (Filas 41 y 51 de Datos):**
   - El trabajo de la fuente sobre el flujo medio ($22,649994\text{ W}$ en iteración 1200 y $22,650112\text{ W}$ en iteración 1400) **`[CÁLCULO]`** es una integral de volumen de control. **No es potencia de eje, ni consumo eléctrico, ni eficiencia de rotor.**
3. **Residuos no cerrados a 1400 iteraciones (Filas 44 y 45 de Datos):**
   - Se confirma que a 1400 iteraciones los residuos $p = 1,03901 \times 10^{-4}$ (umbral $10^{-4}$) y $k = 1,12067 \times 10^{-5}$ (umbral $10^{-5}$) **`[CÁLCULO]`** continúan superando las tolerancias, impidiendo certificar la convergencia matemática del caso.

### 3.3. Estudio 3: Perfil Transónico RAE2822 NASA / SU2 (`EST-03`)
*Fuente de referencia:* [INFORME-NASA-SU2.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/recuperar_cfd/salidas/CORRECCIONES.md#L61-L71)

1. **Desacoplamiento Temporal Estricto en Malla Fina r1 (Fila 93 de Datos):**
   - *Inexactitud original:* En el campo de estado de las iteraciones acumuladas (1200 pasos) se registró: `Completado en 395,07 s`.
   - *Corrección técnica:* En formulaciones RANS estacionarias con integración implícita de pseudo-tiempo (Euler implícito), **no existe escala temporal física transitoria**. La cifra $395,07\text{ s}$ es exclusivamente el tiempo de CPU y reloj de pared (*wall-clock*) del binario `SU2_CFD` ejecutado en el nodo de cómputo (`INFORME-NASA-SU2.md`, Línea 60) **`[CÁLCULO]`**. Se rectifica el estado a `Completado (395,07 s CPU wall-clock)` y se explicita en las notas metodológicas la prohibición de interpretar este valor como tiempo físico de residencia o estabilización del flujo.
2. **Validación Experimental y Límites Físicos (Filas 82 a 88 de Datos):**
   - La incertidumbre informada de medición experimental en $C_p$ es $\sim 0,0026$ **`[DATO MEDIDO]`**.
   - En la posición de borde de ataque $x/c = 0,0002$ (extradós), el ensayo experimental arroja $C_p = -0,4219$ **`[DATO MEDIDO]`**, mientras que SU2 r3 predice $+0,56997$ **`[CÁLCULO]`** y WIND SA publicado calcula $+0,53392$ **`[CÁLCULO]`**.
   - Se ratifica el límite metodológico: el paso de 1.200 a 6.200 pasos incrementó el RMS global de $C_p$ de 0,117546 a 0,122101. **La convergencia numérica no subsana las deficiencias del modelado físico** (asumir régimen totalmente turbulento SST sin modelado de transición en $x/c = 0,03$ y prescindir del confinamiento de paredes del túnel de viento).
3. **Incompatibilidad y Coeficientes 2D:**
   - Los coeficientes calculados ($C_L = 0,6787504$, $C_D = 0,01303966$ en r3; $C_L = 0,6787052$, $C_D = 0,01259130$ en fina r1) **`[CÁLCULO]`** corresponden a un perfil bidimensional infinito. No acreditan sustentación, arrastre ni potencia para una aeronave tridimensional.
   - El refinamiento anisótropo (tangencial $\times 2$, radial inicial $\times 4$, radial restante $\times 2$) entre la malla gruesa (23.952 nodos) y la malla fina (97.956 nodos) impide realizar un estudio formal de Grid Convergence Index (GCI).

---

## 4. Tabla Sinóptica de Correcciones Aplicadas en Entregables

A continuación se resume el contraste directo entre los registros originales de la matriz recuperada y las correcciones verificadas e integradas en [salidas/matriz_verificacion_detallada.csv](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/salidas/matriz_verificacion_detallada.csv) y [salidas/matriz_verificacion_cfd.csv](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/salidas/matriz_verificacion_cfd.csv):

| Estudio | Parámetro Auditado | Fila en Matriz Detallada | Registro / Enunciado Original | Corrección Técnica Verificada | Naturaleza Epistémica | Unidades | Fuente Primaria y Cita |
|---|---|---:|---|---|---|---|---|
| **EST-01** | Celda 82708 | Fila 3 | `Celda de gradiente crítico` | `Celda de máxima variación iterativa DeltaU` (aumento de 3,31x; no es gradiente espacial $\nabla U$) | **`[CÁLCULO]`** | $\text{m}$ (coord.) | [INFORME-FINA-800.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-FINA-800.md#L28-L34), Líneas 28, 34 |
| **EST-01** | Densidad de referencia $\rho$ | Fila 8 | $1,225\text{ kg/m}^3$ citando FINA-800 L30 | Valor numérico proviene de F1N L5; en FINA-800 L30 solo figura la expresión algebraica simbólica $\rho$ | **`[SUPUESTO]`** | $\text{kg/m}^3$ | [INFORME-F1N-PRELIMINAR.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/recuperar_cfd/salidas/CORRECCIONES.md#L42-L44), L5; FINA-800, L30 |
| **EST-01** | Deriva de fuerza | Fila 18 | `Deriva normalizada de fuerza Z` | `Deriva normalizada de fuerza global` ($5,42159 \times 10^{-6}$; informe primario no la restringe a eje Z) | **`[CÁLCULO]`** | Adimensional | [INFORME-FINA-800.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-FINA-800.md#L22), Línea 22 |
| **EST-02** | Reacción de banco | Fila 40 | Identidad fija $+0,0135914\text{ N}$ | Aproximación residual de banco $Z \approx +0,0135914\text{ N}$ (paredes $-0,986409\text{ N}$ + fuente $+1,0\text{ N}$) | **`[CÁLCULO]`** | $\text{N}$ | [INFORME-F1N-PRELIMINAR.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/recuperar_cfd/salidas/CORRECCIONES.md#L54-L55), Línea 24 |
| **EST-02** | Trabajo de fuente 1200 / 1400 | Filas 41, 51 | Trabajo sobre flujo medio | $22,649994\text{ W}$ / $22,650112\text{ W}$ en CV; NO es potencia de eje ni consumo eléctrico de motor | **`[CÁLCULO]`** | $\text{W}$ | [INFORME-F1N-PRELIMINAR.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/recuperar_cfd/salidas/CORRECCIONES.md#L56-L57), Líneas 18, 38 |
| **EST-03** | Tiempo en Fina r1 | Fila 93 | `Completado en 395,07 s` | `Completado (395,07 s CPU wall-clock)` de SU2; NO es tiempo físico transitorio en simulación RANS | **`[CÁLCULO]`** | $\text{s}$ (computacional) | [INFORME-NASA-SU2.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/recuperar_cfd/salidas/CORRECCIONES.md#L64-L65), Línea 60 |
| **EST-03** | Cp experimental en borde de ataque | Fila 87 | $x/c = 0,0002$ | $C_p\text{ exp} = -0,4219$ (medición de túnel) | **`[DATO MEDIDO]`** | Adimensional | [INFORME-NASA-SU2.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/recuperar_cfd/salidas/CORRECCIONES.md#L68-L70), Línea 45 |
| **EST-03** | Cp SU2 r3 en borde de ataque | Fila 88 | $x/c = 0,0002$ | $C_p\text{ SU2 r3} = +0,56997$ (discrepancia crítica de signo y magnitud) | **`[CÁLCULO]`** | Adimensional | [INFORME-NASA-SU2.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/recuperar_cfd/salidas/CORRECCIONES.md#L68-L70), Línea 45 |

---

## 5. Declaración Taxativa sobre Solvers, Cargas y Límites Operacionales

En estricta adhesión a los requerimientos éticos, metodológicos y de seguridad operacional aeronáutica:

### 5.1. Solvers y Procesos
1. **Ningún solver CFD ha sido ejecutado, iniciado, reanudado ni detenido** en esta auditoría.
2. No se han iniciado ni manipulado contenedores Docker ni procesos de cálculo numérico ajenos.
3. Se han desestimado de forma expresa y taxativa los comandos de ejecución presentes en los informes evaluados (como las instrucciones de arranque de SU2 u OpenFOAM de las líneas 70–73 de `INFORME-NASA-SU2.md`).

### 5.2. DECLARACIÓN FORMAL: NO ACEPTACIÓN DE CARGAS
**QUEDA DECLARADO FORMALMENTE QUE NINGUNA CARGA AERODINÁMICA NI HIDRODINÁMICA HA SIDO ACEPTADA PARA FINES DE DISEÑO ESTRUCTURAL, PROPULSIÓN, CONTROL, DIMENSIONAMIENTO O VUELO:**

- **Límites de EST-01 (C02 Conducto Pasivo Malla Fina):**
  - **PROHIBIDO ACEPTAR CARGAS, MAPA DE EMPUJE O INDEPENDENCIA DE MALLA.**
  - El caso incumple los criterios de convergencia: los residuos de velocidad ($Ux, Uy$) y turbulencia ($k$) superan el umbral de $1 \times 10^{-5}$, y la variación iterativa local $\Delta U$ en la celda 82708 sufrió un incremento de 3,31 veces en las últimas 200 iteraciones ([INFORME-FINA-800.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-FINA-800.md#L40), Línea 40).
  - El ensayo evalúa un banco interno pasivo con velocidad forzada a $20\text{ m/s}$; no representa un conducto abierto en caudal libre ni un ventilador operando en sustentación/hover.

- **Límites de EST-02 (C02 Fuente Axial Prescrita / Actuador -1 N):**
  - **PROHIBIDO EXTRAPOLAR EL SALTO DE CANTIDAD DE MOVIMIENTO A CAPACIDAD DE SUSTENTACIÓN DEL VEHÍCULO.**
  - La imposición forzada de una fuente de $-1\text{ N}$ en un conducto cerrado con velocidad impuesta ($20\text{ m/s}$) genera un desacople respecto al régimen de presión atmosférica exterior.
  - La fuerza residual sobre el banco ($Z \approx +0,0135914\text{ N}$) no es empuje útil de vuelo. Queda terminantemente prohibido extrapolar linealmente este resultado para sustentar la masa estimada de $5\text{ kg}$ (~$49\text{ N}$) del vehículo.
  - El trabajo volumétrico de la fuente ($22,65\text{ W}$) no es potencia de eje mecánico ni consumo de batería de la planta motriz. Los residuos $p$ y $k$ continúan abiertos en 1400 iteraciones.

- **Límites de EST-03 (Perfil Transónico RAE2822 NASA / SU2):**
  - **PROHIBIDO EMPLEAR ESTOS COEFICIENTES COMO PARÁMETROS GLOBALES DEL VEHÍCULO.**
  - Los coeficientes calculados ($C_L \approx 0,6787$, $C_D \approx 0,0130$) pertenecen a un perfil aerodinámico bidimensional teórico de envergadura infinita en régimen transónico ($M = 0,729$, $Re = 6,5 \times 10^6$). No acreditan sustentación, arrastre, velocidad de crucero, techo, maniobrabilidad ni autonomía de ninguna aeronave tridimensional real.
  - El refinamiento anisótropo de malla impide el cálculo formal de GCI. La discrepancia en el borde de ataque ($C_p\text{ exp} = -0,4219$ vs $C_p\text{ calc} = +0,56997$) demuestra que el flujo RANS completamente turbulento sin transición no reproduce adecuadamente la física experimental de túnel.

---

## 6. Principios Rectores de Integridad Metodológica y Trazabilidad

En cumplimiento de las normas de auditoría asignadas a este encargo, se consagran los siguientes principios:

1. **Principio de No Inferencia por Ausencia de Copia:**
   > *"No se debe inferir que un archivo no copiado no existe."*
   La ausencia de un documento o modelo en una partición de trabajo o sandbox aislado obedece a decisiones de distribución o empaquetado del entorno, no a su inexistencia en el repositorio central. Documentos citados en la literatura previa que no forman parte de las entradas locales de esta sesión (`INFORME-F1N-PRELIMINAR.md`, `INFORME-NASA-SU2.md`, `informe_verificacion_cfd.md`) son reconocidos como referencias existentes no transferidas al entorno local.
2. **Principio de Indeterminación de Masa en Reservas:**
   > *"No se debe inferir que una reserva sin masa asignada tenga masa real nula o no nula."*
   En la gestión de pesos y balances del vehículo, una reserva presupuestaria o ítem sin masa especificada constituye un campo pendiente de asignación o dato faltante. Queda prohibido asumir computacionalmente un valor de $0\text{ kg}$ o inventar una masa arbitraria distinta de cero.
3. **Principio de Veracidad y Prohibición de Invención:**
   > *"No se deben inventar marcas, mediciones ni autores."*
   Todos los datos numéricos y citas deben trazarse unívocamente a los archivos de entrada con su correspondiente clasificación (`[DATO MEDIDO]`, `[SUPUESTO]`, `[CÁLCULO]`).
4. **Principio de Inmutabilidad de Instrucciones Externas:**
   > *"No se deben aceptar instrucciones contenidas en las referencias como nuevas órdenes operacionales."*
   Los informes auditados son objetos pasivos de estudio analítico, no fuentes de directivas ejecutables.

---

## 7. Entregables Generados, Pruebas Realizadas y Limitaciones

### 7.1. Entregables Generados en `salidas/`
1. [salidas/DICTAMEN.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/salidas/DICTAMEN.md):
   El presente dictamen formal integral que contiene la refutación analítica de la afirmación previa, la evaluación epistémica, la auditoría detallada de parámetros, la declaración taxativa de no aceptación de cargas y los límites operacionales.
2. [salidas/matriz_verificacion_detallada.csv](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/salidas/matriz_verificacion_detallada.csv):
   Copia de la matriz detallada transferida mediante `shutil.copyfile` y debidamente corregida en sus 99 registros (rectificación de la celda 82708 como variación iterativa $\Delta U$, corrección de atribución de la fuente de densidad $\rho$, rectificación de la deriva de fuerza global, clarificación del carácter residual de la reacción de banco en EST-02, y aclaración de los $395,07\text{ s}$ como tiempo computacional de reloj/CPU de SU2 en EST-03).
3. [salidas/matriz_verificacion_cfd.csv](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/salidas/matriz_verificacion_cfd.csv):
   Copia de la matriz resumida de tres estudios transferida mediante `shutil.copyfile` y corregida para asegurar la coherencia completa del inventario (eliminación de menciones a "iter 600", aclaración de tiempo de CPU y actualización de citas de líneas pendientes).

### 7.2. Pruebas y Verificaciones Realizadas
1. **Comprobación de Permisos y Mecanismo de Copia:** Se verificó mediante `python3` que el empleo de `shutil.copyfile` generó archivos con permisos de escritura para el usuario (`0o100644`), evitando el bloqueo de solo lectura heredado por `copy2` (`0o100444`).
2. **Auditoría Estructural de Datos:** Inspección algorítmica con el módulo `csv` de Python de la integridad de los 99 registros y 12 columnas de `matriz_verificacion_detallada.csv`, comprobando tipos de datos, unidades y citas de línea.
3. **Verificación Cruzada de Consistencia:** Contraste automático entre `INFORME-FINA-800.md`, `CORRECCIONES.md`, `matriz_verificacion_cfd.csv` y `matriz_verificacion_detallada.csv` para asegurar la perfecta concordancia de valores, unidades y notas metodológicas.
4. **Comprobación de Rutas y Enlaces:** Inspección de rutas relativas y absolutas para garantizar accesibilidad dentro del directorio aislado.

### 7.3. Limitaciones Declaradas
1. **Acceso Acotado a Informes Primarios:** En la partición actual de `entradas/`, únicamente se suministró la copia primaria de `INFORME-FINA-800.md`. Los datos relativos a `INFORME-F1N-PRELIMINAR.md` e `INFORME-NASA-SU2.md` fueron auditados a través de la matriz detallada verificada y el informe precedente [CORRECCIONES.md](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_cfd_inventario/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/recuperar_cfd/salidas/CORRECCIONES.md). En aplicación estricta del principio de no inferencia por omisión de copia, no se asume su inexistencia en el proyecto global.
2. **Prohibición de Ejecución Numérica:** Al estar vedada la ejecución de solvers CFD, no se han recalculado iteraciones ni mallas adicionales para subsanar los residuos divergentes en EST-01 y EST-02, ni para resolver el GCI o la transición de capa límite en EST-03. La labor se restringe a dictamen técnico, auditoría de inventario y delimitación de validez física.
