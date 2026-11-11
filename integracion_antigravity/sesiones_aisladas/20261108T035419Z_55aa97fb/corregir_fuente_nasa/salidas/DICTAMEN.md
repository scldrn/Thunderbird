# DICTAMEN TÉCNICO: COMPARACIÓN DE LA IDENTIFICACIÓN DEL VENTILADOR Y MOTOR NASA

**Documento evaluado:** [`REVISION.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/revisar_respuesta/salidas/REVISION.md)  
**Documento de referencia:** [`NOTA-NASA-EDF.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md)  
**Ubicación de entrega:** `salidas/DICTAMEN.md`  
**Fecha:** Noviembre 2026  

---

## 1. Declaración de Alcance, Fuentes y Limitación de Lectura

- **Fuente primaria citada:** Weinstein y colaboradores, NASA/AIAA, 2024, NTRS 20230017299 (*Weinstein_SciTech2024_Final.pdf* / `NASA_EDF_20230017299.pdf`).
- **Declaración explícita de alcance:** La nota técnica suministrada en [`NOTA-NASA-EDF.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md) deriva directamente del artículo NTRS 20230017299 de la NASA, pero **no se ha leído el documento PDF completo original**. Este dictamen se fundamenta estrictamente en la contrastación entre la información expuesta en la nota técnica suministrada y las afirmaciones contenidas en la revisión de respuesta ([`REVISION.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/revisar_respuesta/salidas/REVISION.md)).
- **Criterio de integridad:** No se inventan marcas, mediciones ni autores. No se infiere que un archivo no copiado no exista, ni que una reserva sin masa asignada posea masa real nula o no nula. Se preservan escrupulosamente las unidades, magnitudes y fuentes.

---

## 2. Tabla Comparativa de Identificación y Discrepancias

| Parámetro / Elemento | Revisión de Respuesta (`REVISION.md`) | Nota NASA Suministrada (`NOTA-NASA-EDF.md`) | Estado / Tipo de Discrepancia |
|---|---|---|---|
| **Marca / Modelo del Ventilador (EDF)** | *"EDF comercial Schübeler de 130 mm"* (Sección 2 y 2.1) | *"Ventilador Jetfan 130 Pro"* (Línea 8) | **DISCREPANCIA CRÍTICA DE MARCA:** `REVISION.md` atribuye el ventilador a la marca *Schübeler*, mientras que la nota NASA documenta que es un *Jetfan 130 Pro*. |
| **Geometría del Rotor y Estator** | No especifica número de palas ni álabes fijos. | *"diez palas y siete álabes fijos"* (Línea 9) | **OMISIÓN:** `REVISION.md` omite la configuración aerodinámica interna del ventilador. |
| **Dimensiones del Ventilador y Conducto** | Cita únicamente *"130 mm de diámetro"* (Línea 48). | **Tabla 1:** diámetro de pala de $5,11\text{ in}$ ($129,79\text{ mm}$); diámetro exterior del conducto de $5,23\text{ in}$ ($132,84\text{ mm}$). | **DISCREPANCIA DE UNIDADES Y PRECISIÓN:** `REVISION.md` usa un valor nominal métrico redondeado ($130\text{ mm}$); la nota preserva mediciones dimensionales en pulgadas ($5,11\text{ in}$ y $5,23\text{ in}$). |
| **Marca del Motor Eléctrico** | *"motor Hacker"* / *"motor brushless Hacker"* (Líneas 36 y 48) | **No indica marca ni fabricante.** Se describe únicamente por especificaciones físicas (Líneas 12-13). | **DISCREPANCIA CRÍTICA / DATO NO SUSTENTADO:** `REVISION.md` inventa o introduce externamente la marca *Hacker*. La nota técnica NASA no menciona *Hacker* en ningún punto. |
| **Parámetros Físicos del Motor** | Omite masa, diámetro y potencia nominal del motor ensayado en NASA. | **Tabla 2:** motor de $1.100\text{ g}$ de masa, $56\text{ mm}$ de diámetro y $7\text{ kW}$ de potencia continua máxima nominal. *"No es el motor C02"*. | **OMISIÓN TÉCNICA:** `REVISION.md` no consigna la masa ($1.100\text{ g}$), diámetro ($56\text{ mm}$) ni potencia continua nominal ($7\text{ kW}$) de la planta ensayada. |
| **Instalación de Ensayo Experimental** | *"banco estático dinamométrico de la NASA"* (Líneas 33, 48) y *"banco estático abierto"* (Línea 214). | *"ensayado aisladamente en el túnel de baja velocidad de 12 pies de NASA Langley"* (Líneas 8-9). | **DISCREPANCIA CRÍTICA DE ENSAYO / INSTALACIÓN:** `REVISION.md` afirma que el ensayo se hizo en un banco estático dinamométrico abierto. La nota NASA indica que fue ensayado en el *túnel de baja velocidad de 12 pies de NASA Langley*. |
| **Condiciones y Régimen del Ensayo** | Asume únicamente un contexto de banco estático. | **Tablas 5 y 6:** ensayos con variación de ángulo de incidencia entre $0^\circ$ y $30^\circ$, y presión dinámica de $0$ a $6\text{ psf}$. | **DISCREPANCIA DE ENSAYO Y UNIDADES:** `REVISION.md` omite los ensayos aerodinámicos en túnel con incidencia ($0^\circ\text{–}30^\circ$) y presión dinámica ($0\text{–}6\text{ psf}$). |
| **Rango Operativo Medido (Extremos)** | Omite los valores de operación registrados en el ensayo NASA. | **Tabla 6:** velocidad $2.875\text{–}25.150\text{ rpm}$, empuje estático $0\text{–}21,25\text{ lbf}$, potencia $190\text{–}6.420\text{ W}$. Advierte: **no se asumen medidos en un mismo punto**. | **OMISIÓN DE DATOS MEDIDOS Y UNIDADES:** `REVISION.md` no reporta el rango empírico de rpm, empuje en $\text{lbf}$, ni potencia eléctrica en $\text{W}$, ni la advertencia metodológica de desacoplamiento de extremos. |
| **Definición de Potencia** | No define la naturaleza de la potencia del modelo. | **Sección G:** potencia corresponde a potencia eléctrica de corriente continua (CC / DC) suministrada al conjunto. | **OMISIÓN DE ESPECIFICACIÓN:** Falta de especificación del tipo de potencia eléctrica en `REVISION.md`. |
| **Evidencia Dinámica y Modelado** | Afirma limitador por rampa de firmware en ESC comercial, subida lineal, aproximación asintótica y asimetría aceleración/deceleración (Líneas 50-53). | **Sección VI.D:** los autores ajustaron una **respuesta de segundo orden para la velocidad del motor**; la rampa del controlador y el tamaño del escalón influyeron en el transitorio (Líneas 20-22). | **DISCREPANCIA DE EVIDENCIA:** `REVISION.md` añade deducciones empíricas sobre el firmware del ESC y asimetría de aceleración/deceleración no indicadas en la nota; la nota se limita a señalar el ajuste de segundo orden de velocidad del motor y la influencia de rampa y escalón. |
| **Contexto del Vehículo / Proyecto** | Refiere la no-transferibilidad únicamente frente al vehículo hipotético *C02*. | Titula el ensayo para el proyecto **SUSAN**. Señala que el rotor es más grande y distinto al **módulo candidato D82** (Líneas 1, 25-27). | **DISCREPANCIA DE CONTEXTO:** `REVISION.md` no menciona el proyecto *SUSAN* ni el *módulo D82*, evaluando la unidad únicamente frente al escenario de simulación *C02*. |

---

## 3. Análisis Detallado de las Discrepancias

### 3.1. Discrepancia de Marca: Ventilador Schübeler vs. Jetfan 130 Pro
En la Sección 2 (cuadro de la línea 36) y en la Sección 2.1 (línea 48), [`REVISION.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/revisar_respuesta/salidas/REVISION.md) asevera textualmente:
> *"EDF comercial Schübeler de 130 mm"* y *"Un ventilador canalizado eléctrico (EDF) comercial Schübeler de 130 mm de diámetro"*.

Por el contrario, la nota técnica primaria [`NOTA-NASA-EDF.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md) establece de forma explícita en su línea 8:
> *"Ventilador Jetfan 130 Pro ensayado aisladamente en el túnel de baja velocidad de 12 pies de NASA Langley; diez palas y siete álabes fijos."*

**Dictamen:** Se trata de una atribución de marca errónea. *Schübeler* (fabricante alemán de EDFs de carbono) y *Jetfan* (línea de ventiladores desarrollada por E-Jets) son fabricantes y productos completamente diferentes. La fuente documental NASA suministrada designa la unidad inequívocamente como **Jetfan 130 Pro**.

### 3.2. Discrepancia de Motor: Marca "Hacker" no Respaldada
En [`REVISION.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/revisar_respuesta/salidas/REVISION.md) (líneas 36 y 48) se afirma que el conjunto cuenta con un:
> *"motor Hacker"* / *"accionado por un motor brushless Hacker"*.

Al cotejar con [`NOTA-NASA-EDF.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md) (líneas 12-13), la nota técnica consigna:
> *"Tabla 2: motor indicado de 1.100 g de masa, 56 mm de diámetro y 7 kW de potencia continua máxima nominal. No es el motor C02."*

**Dictamen:** En ninguna parte de la nota técnica suministrada se menciona la marca *Hacker*. Incluir *Hacker* como fabricante del motor constituye la incorporación de un dato no documentado en las entradas suministradas. Asimismo, `REVISION.md` omite los parámetros medidos y reportados en la Tabla 2: masa ($1.100\text{ g}$), diámetro de carcasa ($56\text{ mm}$) y potencia continua máxima nominal ($7\text{ kW}$).

### 3.3. Discrepancia en Unidades y Mediciones Dimensionales y Operativas
1. **Dimensiones geométricas:**
   - `REVISION.md` se refiere de forma imprecisa a *"130 mm de diámetro"*.
   - `NOTA-NASA-EDF.md` documenta con rigor dimensional (Tabla 1):
     - Diámetro de pala: $5,11\text{ pulgadas}$ ($129,794\text{ mm}$).
     - Diámetro exterior del conducto: $5,23\text{ pulgadas}$ ($132,842\text{ mm}$).
2. **Condiciones del flujo y túnel:**
   - `NOTA-NASA-EDF.md` reporta unidades anglosajonas de ensayo aerodinámico: presión dinámica $q \in [0, 6]\text{ psf}$ (libras por pie cuadrado, $\text{lbf/ft}^2$) e incidencia $\alpha \in [0^\circ, 30^\circ]$. Ninguna de estas magnitudes ni sus unidades figuran en `REVISION.md`.
3. **Rango de funcionamiento y advertencia de desacoplamiento:**
   - `NOTA-NASA-EDF.md` (Tabla 6) especifica:
     - Velocidad del ventilador: $2.875\text{ a }25.150\text{ rpm}$.
     - Empuje estático: $0\text{ a }21,25\text{ lbf}$ ($0\text{ a }94,52\text{ N}$).
     - Potencia eléctrica en corriente continua (Sección G): $190\text{ a }6.420\text{ W}$.
   - La nota incluye una advertencia técnica fundamental: *“Estos extremos describen el conjunto de pruebas y **no se asumen medidos en un mismo punto**”*. `REVISION.md` no refleja estos datos ni la cautela operativa asociada.

### 3.4. Discrepancia de Instalación y Tipo de Ensayo: Banco Estático vs. Túnel Aerodinámico de 12 Pies
En [`REVISION.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/revisar_respuesta/salidas/REVISION.md) se declara:
- Línea 33: *"Banco estático dinamométrico de la NASA."*
- Línea 48: *"sobre un banco estático dinamométrico de la NASA."*
- Línea 214: *"en banco estático abierto"*.

En contraposición, [`NOTA-NASA-EDF.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md) declara explícitamente:
- Líneas 8-9: *"ensayado aisladamente en el túnel de baja velocidad de 12 pies de NASA Langley"*.
- Líneas 17-18: *"Tablas 5 y 6: ensayos de incidencia entre 0° y 30° y presión dinámica de 0 a 6 psf"*.

**Dictamen:** Describir la campaña experimental de la NASA como un ensayo en *"banco estático dinamométrico abierto"* es erróneo y reduccionista. Aunque se realizaron mediciones estáticas (presión dinámica de $0\text{ psf}$), la instalación experimental utilizada fue el **túnel de baja velocidad de 12 pies de NASA Langley**, permitiendo evaluar la respuesta con velocidad de corriente libre incidente ($q$ hasta $6\text{ psf}$) y ángulos de ataque de hasta $30^\circ$.

### 3.5. Discrepancia en la Evidencia Dinámica y Modelado
En [`REVISION.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/revisar_respuesta/salidas/REVISION.md) (Sección 2.1, líneas 49-54), se presentan como *"Hallazgos empíricos del ensayo"*:
> 1. *"La respuesta real ante escalones de media y gran amplitud está dominada por el limitador interno de aceleración (rampa/slew-rate) programado en el firmware del ESC."*  
> 2. *"La respuesta dinámica no es puramente exponencial ni lineal: presenta una etapa de subida lineal de pendiente constante seguida por una aproximación asintótica."*  
> 3. *"El tiempo de subida depende de la amplitud del escalón comandado ($\Delta u$)."*  
> 4. *"Existe una clara asimetría dinámica entre aceleración y deceleración."*

Por su parte, [`NOTA-NASA-EDF.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md) (Sección VI.D, líneas 20-23) sintetiza la evidencia real registrada en el informe:
> *"Sección VI.D: los autores ajustaron una respuesta de segundo orden para la velocidad del motor; la rampa del controlador y el tamaño del escalón influyeron en el transitorio. La configuración y sus tiempos no se transfieren a C02."*

**Dictamen:** Aunque coinciden en el principio cualitativo de que la rampa del variador/controlador y el escalón afectan el transitorio y no son transferibles al escenario C02, `REVISION.md` incorpora afirmaciones específicas (atribución a firmware del ESC comercial, asimetría explícita de aceleración/desaceleración y descomposición cinemática por tramos) que no se encuentran en el texto de la nota de referencia. La nota técnica se limita a constatar el ajuste de una función de transferencia de **segundo orden para la velocidad del motor**.

### 3.6. Contexto de Proyecto y Vehículo de Referencia
- [`NOTA-NASA-EDF.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md) contextualiza el ensayo para el concepto de aeronave híbrida/eléctrica **SUSAN** de la NASA (*Subsonic Single Aft Engine*) y compara la unidad frente al módulo propulsor candidato **D82**, subrayando que el rotor es más grande y no transferible a este.
- [`REVISION.md`](file:///private/tmp/aero_20261108T035419Z_55aa97fb_2gsxg2ve/corregir_fuente_nasa/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/revisar_respuesta/salidas/REVISION.md) omite toda mención a SUSAN y al módulo D82, enfocando su comparación de no-transferibilidad de forma exclusiva frente a la arquitectura teórica de cuatro ductos de C02.

---

## 4. Distinción Metodológica: Datos Medidos, Supuestos y Cálculos

Para evitar ambigüedades técnicas en futuros desarrollos, se formaliza la clasificación de cada variable:

1. **Datos medidos (procedentes de la campaña experimental de la NASA según nota técnica):**
   - Ventilador Jetfan 130 Pro: 10 palas rotatorias, 7 estatores fijos.
   - Dimensiones geométricas medidas (Tabla 1): diámetro de pala de $5,11\text{ pulgadas}$, diámetro exterior de ducto de $5,23\text{ pulgadas}$.
   - Motor (Tabla 2): masa de $1.100\text{ g}$, diámetro de $56\text{ mm}$, potencia máxima continua de $7\text{ kW}$.
   - Condiciones de ensayo en túnel (Tablas 5 y 6): $\alpha \in [0^\circ, 30^\circ]$, $q \in [0, 6]\text{ psf}$.
   - Extremos medidos (Tabla 6): régimen de $2.875\text{ a }25.150\text{ rpm}$, empuje estático de $0\text{ a }21,25\text{ lbf}$, potencia eléctrica continua (DC) de $190\text{ a }6.420\text{ W}$ (extremos no simultáneos).
   - Ajuste empírico de autores (Sección VI.D): modelo de segundo orden para la velocidad del motor.

2. **Supuestos técnicos (procedentes de hipótesis de diseño para C02):**
   - Inexistencia total de mediciones experimentales para C02 o D82.
   - Constante temporal $\tau \in \{0,08\text{ s}, 0,20\text{ s}, 0,50\text{ s}\}$ supuesta para análisis de respuesta y sensibilidad.
   - Cota de rampa máxima de empuje de $50\text{ N/s}$ por módulo de $21\text{ N}$, derivando una tasa normalizada supuesta $R \approx 2,381\text{ s}^{-1}$.
   - Amortiguamiento crítico idealizado ($\zeta = 1,0$) para el modelo analítico de segundo orden.

3. **Cálculos y derivaciones matemáticas:**
   - Factores adimensionales analíticos exactos ($u_{10\%}, u_{50\%}, u_{90\%}$) y relaciones de retardo ($5,0475\text{x}$ en $10\%$, $2,4213\text{x}$ en $50\%$, $1,6893\text{x}$ en $90\%$).
   - Tiempos de respuesta dimensionales $t = u \cdot \tau$.
   - Integración numérica temporal mediante Runge-Kutta 4 (RK4) para respuesta con rampa de saturación.

---

## 5. Conclusiones y Dictamen Final

1. **Corrección de Marcas y Modelos:** En cualquier documento o modelo posterior debe eliminarse la mención a *Schübeler* y a *Hacker* respecto al ensayo NASA. La identificación correcta y fiel a la nota técnica es **ventilador Jetfan 130 Pro** (10 palas, 7 álabes fijos) accionado por un motor de $1.100\text{ g}$, $56\text{ mm}$ de diámetro y $7\text{ kW}$ de potencia continua, sin marca especificada en la nota.
2. **Corrección de la Instalación Experimental:** Debe rectificarse la afirmación de que el ensayo se redujo a un "banco estático abierto". Debe indicarse que fue realizado en el **túnel de baja velocidad de 12 pies de NASA Langley**, abarcando incidencia ($0^\circ\text{–}30^\circ$) y presión dinámica ($0\text{–}6\text{ psf}$).
3. **Fidelidad de Evidencia Dinámica:** Debe citarse con exactitud lo reportado en la nota técnica: los autores de la NASA ajustaron un modelo de segundo orden a la velocidad del motor, constatando que la rampa del controlador y la magnitud del escalón afectan la respuesta transitoria.
4. **Reserva de Consulta Primaria:** Tal como estipula la nota técnica, cualquier parámetro numérico o curva aerodinámica adicional requiere consultar el PDF original (`NASA_EDF_20230017299.pdf`), sus tablas y gráficas correspondientes.
