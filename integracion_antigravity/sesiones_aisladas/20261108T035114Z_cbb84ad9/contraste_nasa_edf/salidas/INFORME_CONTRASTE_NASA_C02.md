# Informe Técnico: Contraste Trazable entre Referencia NASA EDF e Integración C02

**Fecha de emisión:** 8 de noviembre de 2026  
**Área:** Propulsión Eléctrica y Evaluación Conceptual Aeronáutica  
**Entorno de ejecución:** Espacio de trabajo aislado (`contraste_nasa_edf/`)  
**Entregables generados:** `salidas/conversiones.py`, `salidas/test_conversiones.py`, `salidas/tabla_comparativa.csv`, `salidas/tabla_comparativa.md`, `salidas/INFORME_CONTRASTE_NASA_C02.md`

---

## 1. Identificación Documental y Trazabilidad de Fuentes

El presente análisis establece una comparación metrológica, dimensional, másica y operativa rigurosamente trazable entre la nota de referencia del ventilador eléctrico ensayado por NASA y el informe de integración conceptual C02.

### 1.1 Fuente Primaria NASA y Copia en Sesión
* **Referencia primaria formal:**  
  Weinstein et al., *"Aerodynamic and Acoustic Performance of a Boundary Layer Ingesting Fan Tested in the NASA Langley 12-Foot Low-Speed Tunnel"*, NASA/AIAA 2024 SciTech Forum.  
  Identificador de la NASA Technical Reports Server: [NTRS 20230017299](https://ntrs.nasa.gov/api/citations/20230017299/downloads/Weinstein_SciTech2024_Final.pdf?attachment=true).
* **Copia disponible en sesión:**  
  `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md` (extracto y resumen de datos).
* **Declaración explícita de disponibilidad:**  
  **En esta sesión de trabajo NO se dispone del documento PDF original completo (`NASA_EDF_20230017299.pdf`)**. Toda referencia a datos NASA proviene estrictamente de las tablas y secciones extractadas en `NOTA-NASA-EDF.md`. Para acceder a puntos operativos específicos de curvas, gráficas de transitorios o detalles constructivos internos no resumidos, se requiere recurrir al PDF primario original.

### 1.2 Fuente C02
* **Documento de referencia:**  
  `entradas/investigacion-aeronautica/ejecucion/G3/C02/INFORME-C02.md` (3 de noviembre de 2026).
* **Naturaleza del documento C02:**  
  El informe C02 describe una **candidata de alojamiento volumétrico y cinemática geométrica** para una integración de 4 módulos propulsores en un vehículo de 5 kg objetivo.  
  El propio documento enfatiza que **"C02 no es una selección de motor ni un producto aprobado"**. El tubo axial OD60 y los cubos de motor son reservas espaciales vacías, sin modelo electromagnético seleccionado ni componentes de hardware comercial aprobados.

---

## 2. Conversiones Metrológicas Trazables

Para permitir la comparación física con el sistema internacional de unidades (SI), se aplican los factores de conversión metrológica oficiales:

### 2.1 Conversión de Diámetro de Pala: 5,11 pulgadas a mm
* **Definición metrológica:** Acuerdo Internacional de la Yarda y la Libra (1959):  
  $$1\text{ in} = 25{,}4\text{ mm (exacto)}$$
* **Cálculo trazable:**
  $$\text{Diámetro} = 5{,}11\text{ in} \times 25{,}4\frac{\text{mm}}{\text{in}} = 129{,}794\text{ mm (exacto)}$$
* **Redondeo técnico usual:** $129{,}79\text{ mm}$ o $\sim 129{,}8\text{ mm}$.
* *Dato complementario:* El diámetro exterior del conducto reportado en la Tabla 1 de la nota NASA es de $5{,}23\text{ in}$, correspondiente a:
  $$5{,}23\text{ in} \times 25{,}4\frac{\text{mm}}{\text{in}} = 132{,}842\text{ mm (exacto)}$$

### 2.2 Conversión de Empuje Estático Extremo: 21,25 lbf a N
* **Definición metrológica:**  
  - Libra avoirdupois: $1\text{ lb} = 0{,}45359237\text{ kg}$ (exacto).
  - Aceleración normal de la gravedad: $g_0 = 9{,}80665\text{ m/s}^2$ (3ª Conferencia General de Pesas y Medidas, CGPM 1901).
  - Factor de fuerza:
    $$1\text{ lbf} = 0{,}45359237\text{ kg} \times 9{,}80665\frac{\text{m}}{\text{s}^2} = 4{,}4482216152605\text{ N (exacto)}$$
* **Cálculo trazable:**
  $$21{,}25\text{ lbf} \times 4{,}4482216152605\frac{\text{N}}{\text{lbf}} = 94{,}524709324285625\text{ N}$$
* **Valores normalizados:**
  - 4 decimales: $94{,}5247\text{ N}$
  - 2 decimales: $94{,}52\text{ N}$

---

## 3. Comparación Geométrica y Dimensional

### 3.1 Rotores y Conductos
| Parámetro | NASA (Jetfan 130 Pro) | C02 Módulo Nominal (D82) | C02 Módulo Alternativo (D102,5) | Relación NASA / C02 D82 |
|---|---|---|---|---|
| **Diámetro de pala / rotor** | $129{,}794\text{ mm}$ ($5{,}11\text{ in}$) | $82{,}0\text{ mm}$ (radio nominal R41 mm) | $102{,}5\text{ mm}$ | **+58,3% en diámetro** |
| **Área frontal de barrido** | $13.232\text{ mm}^2$ | $5.281\text{ mm}^2$ | $8.252\text{ mm}^2$ | **2,506 veces superior (+150,6%)** |
| **Diámetro del conducto** | $132{,}842\text{ mm}$ ($5{,}23\text{ in}$ ext.) | Taladro interior $\varnothing 84{,}0\text{ mm}$ (R42 mm) | Pendiente de cierre final | NASA: unidad aislada con conducto propio |
| **Holgura de punta de pala** | No especificada en nota | $0{,}5\text{ mm}$ radial nominal (envolvente R41,5 frente a taladro R42) | No cerrada | C02 exige unión booleana BRep previa |

**Conclusión dimensional del rotor:**  
El rotor del Jetfan 130 Pro ensayado por NASA es sustancialmente más grande que los módulos candidatos de C02. El área de barrido de la pala NASA duplica con creces la del módulo C02 D82, lo que implica condiciones de carga aerodinámica, regímenes de velocidad de punta de pala y números de Reynolds completamente desalineados.

### 3.2 Incompatibilidad Geométrica del Motor NASA en C02
Un punto crítico de diseño es el espacio reservado para el motor eléctrico:
* **Motor reportado en nota NASA (Tabla 2):**
  - Diámetro exterior: **$\varnothing 56{,}0\text{ mm}$**.
  - Masa: **$1.100\text{ g}$**.
  - Potencia continua nominal: **$7\text{ kW}$**.
* **Reservas volumétricas de motor en C02:**
  - En módulo D82: Cilindro de **$\varnothing 21{,}8\text{ mm} \times 16{,}1\text{ mm}$** de longitud.
  - En módulo D102,5: Cilindro de **$\varnothing 27{,}5\text{ mm} \times 19{,}35\text{ mm}$** de longitud.

```
Comparación diametral a escala relativa:
[================= Motor NASA: Ø56,0 mm =================]
[======= Reserva C02 D102,5: Ø27,5 mm =======]
[===== Reserva C02 D82: Ø21,8 mm =====]
```

* **Evaluación de interferencia volumétrica:**
  - El diámetro del motor NASA ($\varnothing 56{,}0\text{ mm}$) es **2,57 veces superior** al diámetro disponible en la cavidad del módulo D82 ($\varnothing 21{,}8\text{ mm}$).
  - El diámetro del motor NASA es **2,04 veces superior** al diámetro disponible en la cavidad del módulo D102,5 ($\varnothing 27{,}5\text{ mm}$).
* **Declaración taxativa:**  
  **BAJO NINGUNA CIRCUNSTANCIA EL MOTOR NASA CABE EN EL ALOJAMIENTO C02**.  
  No sólo existe una interferencia volumétrica insalvable, sino que el motor NASA ocupa prácticamente el mismo diámetro total que el propio conducto interno del módulo D82 ($\varnothing 82\text{ mm}$), bloqueando por completo el flujo de aire y colisionando con los soportes estructurales, cubos y mecanismos cinemáticos de álabes.

---

## 4. Comparación de Masas e Impacto en el Presupuesto del Vehículo

### 4.1 Desglose de Masa Reportado
* **NASA (Jetfan 130 Pro):**
  - Masa del motor ensayado: **$1.100\text{ g}$** ($1{,}10\text{ kg}$).
  - Masa total de la unidad propulsora (rotor, carcasa, álabes, tobera): **No reportada en la nota copiada**. (Se requeriría consultar el PDF de Weinstein et al.).
* **C02 (Integración cuadrimotor de referencia):**
  - Masa de despegue objetivo global: **$5{,}00\text{ kg}$** ($5.000\text{ g}$).
  - Balance geométrico CAD (316 registros sólidos evaluados, excluyendo 54 reservas de hardware no seleccionado):
    - Hipótesis ligera (envolvente $1.200\text{ kg/m}^3$): **$2{,}046\text{ kg}$** (remanente disponible para baterías y sistemas: $2{,}204\text{ kg}$).
    - Hipótesis mixta (envolvente $1.600\text{ kg/m}^3$): **$2{,}784\text{ kg}$** (remanente disponible: $1{,}466\text{ kg}$).
    - Hipótesis aluminio ($2.700\text{ kg/m}^3$): **$4{,}421\text{ kg}$** (remanente: $-0{,}171\text{ kg}$, inviable).
  - Reserva provisional para equipos identificados pendientes: **$0{,}75\text{ kg}$**.

### 4.2 Impacto Másico Comparado
Si se pretendiera incorporar el motor de la nota NASA al vehículo C02:
* La configuración C02 utiliza **cuatro (4) módulos propulsores**.
* Cuatro motores NASA sumarían:
  $$4 \times 1{,}10\text{ kg} = 4{,}40\text{ kg}$$
* Dicha cifra representaría el **$88{,}0\%$** de la masa total objetivo de todo el vehículo ($5{,}00\text{ kg}$).
* Dejaría escasos $0{,}60\text{ kg}$ para toda la estructura de fuselaje, cuatro mecanismos de álabes vectorizables, tapas motorizadas, aviónica, sensores, cableado y batería.
* **Conclusión másica:** El motor ensayado por NASA es una máquina de laboratorio industrial para ensayos continuos de alta durabilidad en túnel aerodinámico, totalmente ajena a la clase de masa, densidad de potencia y escala física requerida por C02.

---

## 5. Análisis Operativo: Empuje, Potencia y Envolventes de Ensayo

### 5.1 Envolvente de Ensayo NASA: No Simultaneidad de Extremos
En la Tabla 6 de `NOTA-NASA-EDF.md` se indican los siguientes rangos operacionales del Jetfan 130 Pro:
* Velocidad del ventilador: $2.875\text{ a }25.150\text{ rpm}$
* Empuje estático reportado: $0\text{ a }21{,}25\text{ lbf}$ ($0\text{ a }94{,}52\text{ N}$)
* Potencia eléctrica DC suministrada al conjunto: $190\text{ a }6.420\text{ W}$

> [!IMPORTANT]
> **Rigor Metodológico sobre Extremos:**  
> Estos valores resumen la **envolvente global** evaluada durante la campaña en el túnel de viento de baja velocidad de NASA Langley (incluyendo ángulos de ataque de 0° a 30° y presiones dinámicas de 0 a 6 psf).  
> **NO se debe suponer que el empuje máximo de $21{,}25\text{ lbf}$ ($94{,}52\text{ N}$) y la potencia máxima de $6.420\text{ W}$ ocurran en el mismo punto de funcionamiento.**  
> En un ensayo aerodinámico, el empuje estático máximo se mide a velocidad de avance nula ($q_\infty = 0$), mientras que la potencia eléctrica máxima puede alcanzarse bajo condiciones de viento incidente con pérdidas de ingestión de capa límite (BLI), incidencia elevada o desprendimiento inducido. Determinar el punto operativo simultáneo exacto requiere consultar las curvas tabuladas en el PDF original.

### 5.2 Demandas de Diseño C02 vs Mediciones NASA
* **Naturaleza en C02:**  
  C02 **no cuenta con datos medidos en banco de pruebas**. Sus cifras son demandas calculadas analíticamente para sostener en vuelo estacionario un vehículo de $5\text{ kg}$ con 4 módulos ($F_{\text{empuje, total}} \approx 49{,}03\text{ N}$, es decir $\sim 12{,}26\text{ N}$ por módulo):
  - Módulo D82: Potencia de eje requerida = $668\text{ W}$ a $46.231\text{ rpm}$ (par de eje $0{,}138\text{ N}\cdot\text{m}$). Pérdidas supuestas motor+ESC = $74{,}2\text{ W}$. Corriente DC supuesta = $123{,}7\text{ A}$ a $24\text{ V}$.
  - Módulo D102,5: Potencia de eje requerida = $534\text{ W}$ a $29.588\text{ rpm}$ (par de eje $0{,}172\text{ N}\cdot\text{m}$). Pérdidas supuestas = $59{,}4\text{ W}$. Corriente DC supuesta = $99{,}0\text{ A}$ a $24\text{ V}$.
* **Diferencia de régimen de giro:**  
  El módulo D82 demanda girar a **$46.231\text{ rpm}$**, casi el doble del régimen máximo alcanzado en el túnel por el Jetfan 130 Pro ($25.150\text{ rpm}$).

### 5.3 Prohibición de Escalado de Curvas como Medición de C02
> [!WARNING]
> **No escalar la curva NASA como medición C02:**  
> Es metodológicamente inválido tomar la curva de rendimiento del Jetfan 130 Pro de NASA y aplicarle leyes de afinidad o escalado para presentarla como una predicción o sustituto de medición para C02.  
> 1. **Diferencias arquitectónicas:** El Jetfan 130 Pro es un EDF axi-simétrico convencional (10 palas fijas, 7 álabes estatores). El módulo C02 posee álabes articulados en 4 filas para vectorización y control, un ducto integrado en fuselaje no axi-simétrico y tapas móviles que distorsionan el flujo.  
> 2. **Diferencia en número de Reynolds y compresibilidad:** La escala geométrica ($130\text{ mm}$ vs $82\text{ mm}$) y la discrepancia de régimen ($25.150\text{ rpm}$ vs $46.231\text{ rpm}$) operan en regímenes fluidodinámicos con espesores de capa límite y pérdidas secundarias no extrapolables linealmente.  
> 3. **Definición de potencia:** La curva de NASA reporta potencia eléctrica de corriente continua (DC) suministrada globalmente; las demandas de C02 expresan potencia mecánica aerodinámica en el eje con hipótesis desacopladas de rendimiento eléctrico.

---

## 6. Clasificación Epistemológica de los Datos

Para garantizar la máxima trazabilidad técnica, la siguiente matriz clasifica la naturaleza exacta de cada magnitud reportada:

| Parámetro | Valor y Unidad Reportada | Categoría Epistemológica | Fuente Documental Directa | Limitaciones / Validez |
|---|---|---|---|---|
| **Diámetro pala NASA** | $5{,}11\text{ in}$ ($129{,}794\text{ mm}$) | **Especificación geométrica** | `NOTA-NASA-EDF.md` (Tabla 1) | Medida nominal del fabricante/ensayo |
| **Diámetro ext. conducto NASA** | $5{,}23\text{ in}$ ($132{,}842\text{ mm}$) | **Especificación geométrica** | `NOTA-NASA-EDF.md` (Tabla 1) | Geometría exterior del carenado |
| **Masa motor NASA** | $1.100\text{ g}$ ($1{,}10\text{ kg}$) | **Dato de catálogo** | `NOTA-NASA-EDF.md` (Tabla 2) | No incluye cableado auxiliar ni banco |
| **Diámetro motor NASA** | $\varnothing 56{,}0\text{ mm}$ | **Dato de catálogo** | `NOTA-NASA-EDF.md` (Tabla 2) | Cilíndrico exterior |
| **Potencia nominal motor NASA** | $7\text{ kW}$ continua | **Especificación de régimen continuo** | `NOTA-NASA-EDF.md` (Tabla 2) | Capacidad térmica nominal del motor |
| **Régimen de giro NASA** | $2.875\text{ a }25.150\text{ rpm}$ | **Dato medido en túnel** | `NOTA-NASA-EDF.md` (Tabla 6) | Rango envolvente del ensayo de túnel |
| **Empuje estático NASA** | $0\text{ a }21{,}25\text{ lbf}$ ($0\text{ a }94{,}52\text{ N}$) | **Dato medido en túnel** | `NOTA-NASA-EDF.md` (Tabla 6) | Extremos de sobre; no simultáneos con $P_{\max}$ |
| **Potencia eléctrica DC NASA** | $190\text{ a }6.420\text{ W}$ | **Dato medido en banco/túnel** | `NOTA-NASA-EDF.md` (Tabla 6) | Potencia eléctrica DC en bornes del sistema |
| **Rotor nominal C02 D82** | $\varnothing 82{,}0\text{ mm}$ (R41 nominal) | **Dimensión geométrica CAD** | `INFORME-C02.md` (Resumen inicial) | Modelo conceptual BRep; contención R41,5 mm |
| **Reserva motor C02 D82** | $\varnothing 21{,}8\text{ mm} \times 16{,}1\text{ mm}$ | **Reserva volumétrica vacía** | `INFORME-C02.md` (Tabla Requisitos) | No corresponde a ningún motor seleccionado |
| **Rotor nominal C02 D102,5** | $\varnothing 102{,}5\text{ mm}$ | **Dimensión geométrica CAD** | `INFORME-C02.md` (Tabla Compromiso) | Variante de estudio de compromiso |
| **Reserva motor C02 D102,5** | $\varnothing 27{,}5\text{ mm} \times 19{,}35\text{ mm}$ | **Reserva volumétrica vacía** | `INFORME-C02.md` (Tabla Requisitos) | No corresponde a ningún motor seleccionado |
| **Masa geométrica C02 (316 sól.)** | $2{,}046\text{ a }4{,}421\text{ kg}$ | **Cálculo de integración geométrica** | `INFORME-C02.md` (Tabla Masa e inercia) | Depende de densidad; excluye 54 reservas |
| **Masa objetivo total C02** | $5{,}00\text{ kg}$ | **Requisito de diseño de misión** | `INFORME-C02.md` (Resultado materializado) | Criterio superior de diseño para 4 rotores |
| **Potencia de eje C02 D82** | $668\text{ W}$ por módulo | **Demanda analítica calculada** | `INFORME-C02.md` (Tabla Requisitos) | Cálculo estacionario C01 ($\kappa=0{,}85, \eta=0{,}90$) |
| **Régimen de giro C02 D82** | $46.231\text{ rpm}$ | **Demanda analítica calculada** | `INFORME-C02.md` (Tabla Requisitos) | Cálculo BEM en punto de diseño |
| **Pérdida motor+ESC C02 D82** | $74{,}2\text{ W}$ | **Supuesto de eficiencia** | `INFORME-C02.md` (Tabla Requisitos) | Supuesto global sin diseño electromagnético |

---

## 7. Tabla Comparativa Consolidada

A continuación se reproduce el contenido estructurado de `salidas/tabla_comparativa.md`:

| Parámetro | NASA Jetfan 130 Pro | C02 (D82) | C02 (D102,5) | Naturaleza de Datos (NASA / C02) | Observaciones de Trazabilidad |
|---|---|---|---|---|---|
| **Diámetro de pala / rotor** | 5.11 in (129.794 mm) | 82,0 mm (R41 mm nominal; contención R41,5 mm) | 102,5 mm nominal | **NASA:** Dato de informe / catálogo (Tabla 1) (`NOTA-NASA-EDF.md`)<br>**C02:** Dimensión geométrica CAD (`INFORME-C02.md`) | NASA es 58,3% mayor en diámetro que C02 D82 (área 2,50x superior). Escala y dinámica fluidas divergentes. |
| **Diámetro exterior conducto** | 5.23 in (132.842 mm) | Taladro R42 mm ($\varnothing 84{,}0\text{ mm}$ int.; holgura radial $0{,}5\text{ mm}$) | No especificado conducto final | **NASA:** Dato de informe (Tabla 1)<br>**C02:** Dimensión geométrica CAD | NASA ensayado aislado en túnel 12 ft. C02 integrado en fuselaje cuadrimotor. |
| **Diámetro de motor** | 56,0 mm | Reserva cilíndrica $\varnothing 21{,}8\text{ mm}$ (long. $16{,}1\text{ mm}$) | Reserva cilíndrica $\varnothing 27{,}5\text{ mm}$ (long. $19{,}35\text{ mm}$) | **NASA:** Especificación de motor ensayado (Tabla 2)<br>**C02:** Reserva volumétrica CAD vacía | **EL MOTOR NASA NO CABE EN C02:** $\varnothing 56\text{ mm}$ supera por 2,57x la reserva de D82 y por 2,04x la de D102,5. |
| **Masa del motor** | 1.100 g (1,10 kg) | Sin hardware asignado (registro vacío en BOM geométrica) | Sin hardware asignado (registro vacío en BOM geométrica) | **NASA:** Especificación de catálogo (Tabla 2)<br>**C02:** Volumen reservado vacío (54 reservas) | 4 motores NASA pesarían 4,40 kg, agotando el 88% del peso total objetivo de C02 (5,0 kg). |
| **Masa global de referencia** | No reportada en nota | Objetivo 5,0 kg. Masa geométrica: 2,046 kg (ligera), 2,784 kg (mixta), 4,421 kg (aluminio) | Evaluado en compromiso de envolvente para vehículo 5,0 kg | **NASA:** Dato ausente en nota copiada (requiere PDF)<br>**C02:** Hipótesis de densidad y cálculo sobre 316 piezas | C02 incluye reserva de 0,75 kg para equipos pendientes; no asigna masa a reservas vacías. |
| **Arquitectura de álabes** | 10 palas rotor, 7 estatores | 4 filas independientes, 3 álabes por fila sincronizados | Módulo cinemático similar | **NASA:** Geometría fija convencional ensayada<br>**C02:** Cinemática articulada de vectorización | Conceptos aerodinámicos totalmente heterogéneos. |
| **Empuje estático reportado** | Rango 0 a 21.25 lbf (0 a 94.52 N) | Requisito de cálculo: $\sim 12{,}26\text{ N}$/módulo para estacionario de 5 kg (total $\sim 49{,}03\text{ N}$) | Requisito similar para estacionario de 5 kg | **NASA:** Medido en túnel de viento (Tabla 6)<br>**C02:** Demanda de diseño analítica | Extremos NASA del conjunto de pruebas; NO se asumen medidos en un mismo punto. Curva no escalable a C02. |
| **Potencia reportada** | Rango 190 a 6.420 W (eléctrica DC) | Demanda calculada: 668 W en eje por módulo (+ 74,2 W supuestas en pérdidas) | Demanda calculada: 534 W en eje por módulo (+ 59,4 W supuestas en pérdidas) | **NASA:** Medido en bornes DC (Tablas 5 y 6)<br>**C02:** Demanda analítica en eje | NASA midió potencia eléctrica de entrada; C02 expresa potencia mecánica de eje sin motor seleccionado. |
| **Régimen de giro** | 2.875 a 25.150 rpm | 46.231 rpm (cálculo estacionario) | 29.588 rpm (cálculo estacionario) | **NASA:** Medido / rango de ensayo (Tabla 6)<br>**C02:** Cálculo BEM en punto de diseño | C02 D82 demanda un régimen casi un 84% superior al máximo ensayado en NASA. |
| **Potencia nominal del motor** | 7 kW (7.000 W) continua | Sin motor seleccionado (demanda de eje 668 W/módulo; 2.672 W eje total 4 módulos) | Sin motor seleccionado (demanda de eje 534 W/módulo; 2.136 W eje total 4 módulos) | **NASA:** Especificación de motor (Tabla 2)<br>**C02:** Demanda de cálculo, sin hardware | El motor NASA es un equipo sobredimensionado para ensayos industriales de túnel. |

---

## 8. Conclusiones y Limitaciones

1. **Incompatibilidad Física Absoluta:**  
   El motor indicado en la nota NASA ($\varnothing 56{,}0\text{ mm}$, $1.100\text{ g}$) no puede alojarse en los módulos de C02 ($\varnothing 21{,}8\text{ mm}$ en D82 y $\varnothing 27{,}5\text{ mm}$ en D102,5). Adicionalmente, instalar 4 motores de dicha masa consumiría $4{,}40\text{ kg}$ de los $5{,}00\text{ kg}$ totales del vehículo, haciendo físicamente inviable el proyecto.
2. **Independencia de Envolventes Operativas:**  
   Los valores extremos reportados por NASA ($21{,}25\text{ lbf}$ / $94{,}52\text{ N}$ y $6.420\text{ W}$) delimitan el banco de pruebas y no deben tratarse como un único punto de funcionamiento acoplado.
3. **No Escalabilidad de Curvas:**  
   Las mediciones aerodinámicas del Jetfan 130 Pro no constituyen una medición ni pueden escalarse directamente para predecir las prestaciones del módulo C02. La discrepancia en escala, número de palas, cinemática vectorizable, régimen de rotación ($25.150\text{ rpm}$ vs $46.231\text{ rpm}$) y acoplamiento con el fuselaje impiden cualquier extrapolación heurística directa.
4. **Limitación de Fuentes:**  
   La sesión de trabajo carece del archivo PDF original de Weinstein et al. (NTRS 20230017299). Toda la información NASA se deriva estrictamente de `NOTA-NASA-EDF.md`. Para cualquier detalle de micro-geometría de álabes, mapas completos de rendimiento o transitorios dinámicos de segundo orden, es imperativo consultar la publicación primaria original.
