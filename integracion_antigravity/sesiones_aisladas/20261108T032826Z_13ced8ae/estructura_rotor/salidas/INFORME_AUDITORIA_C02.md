# AUDITORÍA TÉCNICA Y COMPROBACIONES ANALÍTICAS INDEPENDIENTES DE ESCALADO CENTRÍFUGO — ROTOR C02

**Fecha de emisión:** 7 de noviembre de 2026  
**Ámbito de trabajo:** Directorio de trabajo aislado `estructura_rotor/`  
**Entregables generados:** `salidas/`  
**Referencias auditadas (solo lectura):** `entradas/investigacion-aeronautica/ejecucion/G5/rotor_C02/` (`INFORME.md`, `RESULTADOS.json`)  
**Entorno de cálculo:** Python 3.9 (Sandbox estándar)  

---

> [!CAUTION]
> ### AVISO EXPRESO DE LIMITACIÓN DE ALCANCE Y RESPONSABILIDAD TÉCNICA
> El presente documento y los cálculos que lo acompañan constituyen un **cribado geométrico condicionado y una verificación analítica cinemática/centrífuga preliminar**.
> 
> **BAJO NINGUNA CIRCUNSTANCIA DEBE PRESENTARSE NI INTERPRETARSE COMO:**
> 1. Un análisis de la **tensión de la pala real** (carece de acoplamiento tridimensional, cortante, torsión, alabeo y concentradores).
> 2. Un **análisis aeroelástico** (carece de acoplamiento fluido-estructura, divergencia torsional, bataneo, aleteo o inestabilidad dinámica).
> 3. Una **aprobación de diseño estructural, integridad física o aptitud para fabricación**.
>
> La viabilidad estructural final exige análisis avanzado por elementos finitos (FEA 3D no lineal), selección y caracterización experimental de material, modelos aeroelásticos acoplados y ensayos destructivos/no destructivos en banco.

---

## 1. RESUMEN EJECUTIVO Y OBJETIVO DE LA AUDITORÍA

Se ha llevado a cabo una auditoría técnica independiente del cribado estructural previo correspondiente al rotor **C02** (modelos geométricos D82 y su variante prototipo a escala D102,5), desarrollado en la etapa G5 de la investigación aeronáutica.

El objetivo central ha sido:
1. Auditar la consistencia matemática, las hipótesis físicas y los límites de validez del informe y archivo de resultados previo (`INFORME.md`, `RESULTADOS.json`).
2. Desarrollar formulaciones analíticas independientes de cinemática rotatoria y escalado centrífugo: **velocidad periférica de punta ($v_{tip}$)**, **número de Mach de punta ($M_{tip}$)** y **fuerza centrífuga radial proporcional a $\Omega^2$** para masas y radios supuestos.
3. Contrastar y desmitificar el factor de semejanza $0,6400$ hallado en las 72 parejas de resultados del cribado previo, explicando su origen cinemático e identificando su impacto bajo diferentes regímenes de escalado.
4. Evaluar la viabilidad de la separación radial crítica de $0,5\text{ mm}$ frente a dilatación elástica, térmica y dinámica.

---

## 2. TAXONOMÍA ESTRICTA DE DATOS (UNIDADES, FUENTES Y CLASIFICACIÓN)

Para garantizar la integridad técnica y evitar confusiones metodológicas, se clasifican taxativamente los datos utilizados:

### 2.1. Datos medidos
* **Ninguno.** En esta fase del proyecto **no existen mediciones físicas directas** (no hay ensayos extensométricos, lecturas de celdas de carga, mediciones dinámicas en túnel de viento ni caracterización destructiva de probetas). La totalidad de los datos proviene de modelos CAD virtuales y simulaciones analíticas preliminares.

### 2.2. Datos supuestos (Hipótesis de partida)
* **Geometría CAD de referencia:** Archivos STEP identificados por hash SHA256:
  * Rotor D82 (factor 1,0): `C02_D82_x-160_neutro/modulo.step` (`SHA256: 76fac72ce73e...`).
  * Rotor D102,5 (factor 1,25, prototipo separado no instalado en el mismo fuselaje): `C02_D102.5_neutro/modulo.step` (`SHA256: 0d460f72b8fb...`).
* **Número de palas:** 8 palas idénticas distribuidas simétricamente, aisladas por conectividad fuera del cilindro de corte nominal $R_{cubo} = 0,32 R$.
* **Escenarios operativos (procedentes del modelo C01 para vehículo de 5 kg y factor $\kappa = 0,85$):**
  * *Estacionario (Hover):* $46.231\text{ rpm}$ (D82) / $29.588\text{ rpm}$ (D102,5).
  * *Demanda lateral 0,5g:* $48.901\text{ rpm}$ (D82) / $31.297\text{ rpm}$ (D102,5).
  * *Demanda vertical ascendente +1g:* $65.376\text{ rpm}$ (D82) / $41.840\text{ rpm}$ (D102,5).
* **Densidades homogéneas supuestas:** $\rho \in \{1200, 1600, 2700\}\text{ kg/m}^3$ (valores paramétricos que no representan materiales aprobados para vuelo).
* **Atmósfera de referencia:** Atmósfera Estándar Internacional (ISA) a nivel del mar (ISO 2533):
  * $T_0 = 288,15\text{ K}$ ($15\text{ }^\circ\text{C}$), $\gamma = 1,4$, $R_{aire} = 287,05287\text{ J/(kg}\cdot\text{K)}$, $a_0 = 340,294\text{ m/s}$.
* **Comportamiento mecánico:** Cuerpo rígido en rotación pura, módulo elástico longitudinal uniforme sobre cada sección plana, distribución lineal de tensiones según la hipótesis de Bernoulli-Navier para flexión no simétrica.

### 2.3. Datos calculados
* Velocidad angular $\Omega\text{ [rad/s]}$, velocidad periférica de punta $v_{tip}\text{ [m/s]}$, número de Mach de punta $M_{tip}\text{ [-]}$.
* Aceleración centrípeta $a_c\text{ [m/s}^2\text{ y g]}$, masa exterior integrada $m_{ext}\text{ [kg]}$, centroide radial efectivo $r_{cm, eff}\text{ [m]}$.
* Fuerza centrífuga radial $F_{rad} = m_{ext} r_{cm, eff} \Omega^2\text{ [N]}$, fuerza transversal $F_y\text{ [N]}$, momentos en el centroide $M_x, M_y, M_z\text{ [N}\cdot\text{m]}$.
* Tensión axial media $\sigma_{mean} = N/A\text{ [MPa]}$, tensión normal máxima muestreada $\sigma_{max}\text{ [MPa]}$, factor de amplificación por flexión no simétrica $\sigma_{max} / \sigma_{mean}\text{ [-]}$.

---

## 3. AUDITORÍA DEL CRIBADO ESTRUCTURAL PREVIO (G5 / C02)

### 3.1. Evaluación del método de extracción y cuadratura
El informe previo detalla la extracción de las 8 palas tras retirar un cilindro central de radio $0,32 R$ ($13,12\text{ mm}$ en D82 y $16,40\text{ mm}$ en D102,5). Se destaca favorablemente el **rechazo explícito del corte sectorial angular**, el cual recortaba artificialmente el borde de ataque/salida e introducía esquinas parásitas de palas vecinas. El método de aislamiento por conectividad de sólidos garantiza que el volumen analizado corresponda efectivamente a la masa real de cada pala.

La integración de volumen, centroide e inercia mediante cuadratura adaptativa se ha auditado mediante la verificación de la invariante geométrica:
$$I_{x, geom} = \frac{F_x}{\rho \, \Omega^2} = \int_{V_{ext}} x \, dV$$
La comprobación numérica sobre los 144 registros de `RESULTADOS.json` arrojó una dispersión relativa máxima de $6,43 \times 10^{-16}$, lo que confirma una consistencia matemática estricta a nivel de precisión de máquina de coma flotante IEEE 754.

Asimismo, la prueba de sensibilidad de rebanado ($0,02\text{ mm}$ frente a $0,04\text{ mm}$) demostró un cambio relativo de área de apenas $4,83 \times 10^{-6}$ y de tensor de $1,75 \times 10^{-5}$. **Sin embargo, es fundamental aclarar que esta sensibilidad únicamente valida la precisión de discretización geométrica del algoritmo CAD; de ninguna manera valida las hipótesis mecánicas subyacentes ni la resistencia física real.**

### 3.2. Desmitificación del factor de semejanza 0,6400
El informe previo destacaba que, al escalar del diámetro $82\text{ mm}$ al prototipo de $102,5\text{ mm}$, la fuerza centrífuga radial se mantiene prácticamente constante ($F_{102,5} / F_{82} = 1,000000$) y la tensión normal se reduce a un factor aproximado de $0,64$ ($0,63990 - 0,64000$ en las 72 parejas).

Esta coincidencia **no es una propiedad mística ni una superioridad estructural intrínseca del rotor mayor**. Se debe estrictamente a la regla cinemática supuesta en el modelo C01:
1. El factor de escala lineal es $\lambda = \frac{102,5}{82,0} = 1,25$.
2. Por semejanza geométrica homóloga tridimensional:
   $$\text{Masa } m \propto \lambda^3 = 1,25^3 = 1,953125$$
   $$\text{Radio de centroide } r_{cm} \propto \lambda = 1,25$$
   $$\text{Área de sección } A \propto \lambda^2 = 1,25^2 = 1,5625$$
3. El escenario C01 impuso que el rotor D102,5 opere a menores rpm para generar el mismo empuje nominal de sustentación que el rotor D82 para el vehículo de 5 kg ($T \propto \Omega^2 D^4 = \text{constante} \implies \Omega \propto D^{-2}$).
4. Por lo tanto, la velocidad angular se redujo exactamente por:
   $$\frac{\Omega_{102,5}}{\Omega_{82}} = \left(\frac{1}{\lambda}\right)^2 = \frac{1}{1,25^2} = 0,6400$$
5. Al calcular la fuerza centrífuga radial:
   $$F_{rad} = m \, r_{cm} \, \Omega^2 \propto (\lambda^3) \cdot (\lambda) \cdot (\lambda^{-2})^2 = \lambda^4 \cdot \lambda^{-4} = 1,000000$$
6. Al calcular la tensión media $\sigma = F / A$:
   $$\sigma \propto \frac{1}{\lambda^2} = \frac{1}{1,5625} = 0,640000$$

### 3.3. Análisis de otros regímenes de escalado dimensional
El escalado $\Omega \propto D^{-2}$ solo es válido si el rotor opera bajo la condición de empuje de sustentación constante. Si se evalúan otros regímenes de diseño, el comportamiento estructural cambia drásticamente:

| Régimen de Escalado | Ley de rpm | Ratio $\frac{\text{rpm}_{102,5}}{\text{rpm}_{82}}$ | Ratio $\frac{v_{tip, 102,5}}{v_{tip, 82}}$ | Ratio $\frac{F_{rad, 102,5}}{F_{rad, 82}}$ | Ratio $\frac{\sigma_{102,5}}{\sigma_{82}}$ | Implicación Física y de Diseño |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Aerodinámico C01 (Empuje cte.)** | $\Omega \propto D^{-2}$ | **0,6400** | **0,8000** | **1,0000** | **0,6400** | Conserva empuje en hover; reduce velocidad periférica (-20%) y tensión (-36%). |
| **2. Velocidad de punta cte.** | $\Omega \propto D^{-1}$ | **0,8000** | **1,0000** | **1,5625** | **1,0000** | Conserva número de Mach de punta; la fuerza centrífuga aumenta un **+56,25%**. |
| **3. Velocidad rotacional cte.** | $\Omega = \text{cte}$ | **1,0000** | **1,2500** | **2,4414** | **1,5625** | Si el motor mantiene régimen, la fuerza radial salta **+144,14%** y la tensión **+56,25%**. |

> [!WARNING]
> Si el prototipo D102,5 requiere mayor empuje para maniobras dinámicas o no alcanza el coeficiente de sustentación previsto, elevar su velocidad por encima del criterio $\Omega \propto D^{-2}$ disparará las cargas centrífugas de forma cuadrática ($\Omega^2$).

---

## 4. COMPROBACIONES ANALÍTICAS INDEPENDIENTES DE ESCALADO CENTRÍFUGO

### 4.1. Cinemática de rotación y número de Mach de punta
Para cada escenario operativo y rotor se han formulado los cálculos analíticos exactos:
$$\Omega = \text{rpm} \cdot \frac{\pi}{30} \quad [\text{rad/s}], \quad v_{tip} = \Omega \cdot R_{tip} \quad [\text{m/s}], \quad M_{tip} = \frac{v_{tip}}{\sqrt{\gamma R T}}$$

#### Tabla 1: Cinemática y Mach de Punta en Condiciones ISA ($15\text{ }^\circ\text{C}$, $a_0 = 340,29\text{ m/s}$)

| Rotor | Diámetro | Escenario Operativo | rpm Supuesta | $\Omega$ (rad/s) | $v_{tip}$ (m/s) | $v_{tip}$ (km/h) | $M_{tip}$ (ISA) | Aceleración Punta ($a_c$) |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **D82** | 82,0 mm | Estacionario (Hover) | 46.231 | 4.841,35 | 198,50 | 714,6 | 0,583 | $961.036\text{ m/s}^2$ ($98.000\text{ g}$) |
| **D82** | 82,0 mm | Demanda lateral 0,5g | 48.901 | 5.120,92 | 209,96 | 755,8 | 0,617 | $1.075.148\text{ m/s}^2$ ($109.635\text{ g}$) |
| **D82** | 82,0 mm | Demanda vertical +1g | 65.376 | 6.846,13 | **280,69** | **1.010,5** | **0,825** | **$1.921.758\text{ m/s}^2$ ($195.965\text{ g}$)** |
| **D102,5** | 102,5 mm | Estacionario (Hover) | 29.588 | 3.098,46 | 158,80 | 571,7 | 0,467 | $492.050\text{ m/s}^2$ ($50.175\text{ g}$) |
| **D102,5** | 102,5 mm | Demanda lateral 0,5g | 31.297 | 3.277,39 | 167,97 | 604,7 | 0,494 | $550.476\text{ m/s}^2$ ($56.133\text{ g}$) |
| **D102,5** | 102,5 mm | Demanda vertical +1g | 41.840 | 4.381,52 | 224,55 | 808,4 | 0,660 | $983.940\text{ m/s}^2$ ($100.334\text{ g}$) |

> [!IMPORTANT]
> ### HALLAZGO CRÍTICO AERODINÁMICO EN EL ROTOR D82
> En la condición de **demanda vertical +1g ($65.376\text{ rpm}$)**, la punta de la pala del rotor D82 alcanza una velocidad periférica de **$280,69\text{ m/s}$**, lo que equivale a un número de **Mach de punta de 0,825**.
> 
> A $M_{tip} > 0,80$, la pala entra decididamente en el **régimen transónico**. Esto conlleva consecuencias directas que invalidan la aerodinámica asumida:
> 1. Aparición de ondas de choque locales en el extradós y desprendimiento de capa límite inducido por choque.
> 2. Fuerte divergencia de resistencia (*compressibility drag rise*), lo que hace físicamente imposible mantener la eficiencia de hover asumida ($\kappa = 0,85$).
> 3. Incremento drástico de emisiones acústicas (*High-Speed Impulsive Noise*, HSI).
> 4. Riesgo severo de vibraciones aeroelásticas no estacionarias (*shock buffet* y aleteo transónico).
> 5. Si la temperatura ambiente desciende a $0\text{ }^\circ\text{C}$ ($T = 273,15\text{ K}$, $a = 331,3\text{ m/s}$), el Mach de punta sube a **0,847**.

### 4.2. Carga centrífuga radial proporcional a $\Omega^2$
Para una masa $m$ rotando a una distancia radial de centro de masa $r_{cm}$, la fuerza radial centrífuga exacta viene dada por:
$$F_{rad} = m \, r_{cm} \, \Omega^2$$

Para un elemento diferencial de pala con densidad lineal $\mu(r)$, la fuerza en una sección de corte $r_0$ es:
$$F(r_0) = \int_{r_0}^{R_{tip}} \mu(r) \, \Omega^2 \, r \, dr = \Omega^2 \int_{r_0}^{R_{tip}} r \, dm$$

En la estación crítica muestreada $x/R = 0,33$ ($x = 13,53\text{ mm}$ en D82 y $16,91\text{ mm}$ en D102,5), la integración CAD arrojó los siguientes valores geométricos para la parte exterior de la pala:
* **D82:** Volumen exterior $V_{ext} = 2,7552 \times 10^{-7}\text{ m}^3$; $\int x dV = 7,09525 \times 10^{-9}\text{ m}^4$; Centroide radial efectivo $r_{cm, eff} = 25,752\text{ mm}$ ($62,81\% R$).
* **D102,5:** Volumen exterior $V_{ext} = 5,3812 \times 10^{-7}\text{ m}^3$; $\int x dV = 1,73224 \times 10^{-8}\text{ m}^4$; Centroide radial efectivo $r_{cm, eff} = 32,190\text{ mm}$ ($62,81\% R$).

#### Tabla 2: Cargas Radiales y Tensiones en la Estación Crítica $x/R = 0,33$ ($\rho = 1600\text{ kg/m}^3$)

| Rotor | Escenario | Masa Ext. Pala ($m$) | Radio Centroide ($r_{cm}$) | Fuerza Radial Analítica ($F_{rad}$) | Fuerza Radial CAD ($F_x$) | Área Sección ($A$) | Tensión Media ($N/A$) | Tensión Normal Máx. CAD | Amplificación por Flexión |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **D82** | Estacionario | $0,4408\text{ g}$ | $25,75\text{ mm}$ | **$266,09\text{ N}$** | $266,09\text{ N}$ | $6,358\text{ mm}^2$ | $41,85\text{ MPa}$ | $116,75\text{ MPa}$ | **2,79×** |
| **D82** | Lateral 0,5g | $0,4408\text{ g}$ | $25,75\text{ mm}$ | **$297,70\text{ N}$** | $297,70\text{ N}$ | $6,358\text{ mm}^2$ | $46,83\text{ MPa}$ | $130,62\text{ MPa}$ | **2,79×** |
| **D82** | Vertical +1g | $0,4408\text{ g}$ | $25,75\text{ mm}$ | **$532,08\text{ N}$** | $532,08\text{ N}$ | $6,358\text{ mm}^2$ | $83,69\text{ MPa}$ | $233,46\text{ MPa}$ | **2,79×** |
| **D102,5** | Estacionario | $0,8610\text{ g}$ | $32,19\text{ mm}$ | **$266,09\text{ N}$** | $266,09\text{ N}$ | $9,934\text{ mm}^2$ | $26,79\text{ MPa}$ | $74,71\text{ MPa}$ | **2,79×** |
| **D102,5** | Lateral 0,5g | $0,8610\text{ g}$ | $32,19\text{ mm}$ | **$297,70\text{ N}$** | $297,70\text{ N}$ | $9,934\text{ mm}^2$ | $29,97\text{ MPa}$ | $83,59\text{ MPa}$ | **2,79×** |
| **D102,5** | Vertical +1g | $0,8610\text{ g}$ | $32,19\text{ mm}$ | **$532,08\text{ N}$** | $532,08\text{ N}$ | $9,934\text{ mm}^2$ | $53,56\text{ MPa}$ | $149,39\text{ MPa}$ | **2,79×** |

> [!NOTE]
> ### INTERPRETACIÓN FÍSICA DE LA CARGA CENTRÍFUGA
> Obsérvese la enorme magnitud del esfuerzo: una diminuta pala cuya parte exterior pesa apenas **$0,44\text{ gramos}$** está sometida en régimen de ascenso a una tracción radial saliente de **$532,08\text{ N}$** (equivalente al peso de un bloque de $54,2\text{ kg}$ suspendido de una sección de solo $6,36\text{ mm}^2$).
> 
> La aceleración centrífuga en el centroide de la pala supera los **$123.000\text{ g}$**.

### 4.3. Flexión no simétrica y componente transversal
La sección transversal de la pala no es un prisma simétrico coaxial con el radio, sino un perfil alar con torsión, curvatura y flecha. En consecuencia:
1. Aparece una fuerza transversal en el plano de rotación $F_y = -19,47\text{ N}$ (en D82 hover, $\rho = 1600$). Esta componente representa un $7,3\%$ de la fuerza radial principal.
2. Los momentos resultantes respecto al centroide de la sección ($M_x = -0,0341\text{ N}\cdot\text{m}$, $M_y = 0,0003\text{ N}\cdot\text{m}$, $M_z = -0,0996\text{ N}\cdot\text{m}$) inducen tensiones normales por flexión que **casi triplican la tensión axial pura**:
   $$\sigma_{max} = 116,75\text{ MPa} \quad \text{vs} \quad \sigma_{mean} = 41,85\text{ MPa} \quad (\text{factor de amplificación } = 2,79\times)$$
3. **Omisión crítica previa:** El momento torsor $M_x = -0,0341\text{ N}\cdot\text{m}$ no fue traducido a tensiones de torsión de Saint-Venant ni alabeo torsional de Vlasov en las tablas previas.

---

## 5. EVALUACIÓN DE LA HOLGURA RADIAL DE PUNTA ($0,5\text{ mm}$)

El informe original señala: *"Estas contribuciones impiden dar por aprobada la separación radial 0,5 mm o los apoyos actuales."* La presente auditoría confirma plenamente esta advertencia a partir de cuatro mecanismos físicos concurrentes:

1. **Alargamiento elástico centrífugo ($\Delta r_{elast}$):**
   Para una pala de longitud libre $L \approx 27\text{ mm}$ sometida a una tensión axial promedio ponderada de $\approx 50\text{ MPa}$, la deformación elástica depende del módulo de Young $E$ del material final:
   $$\Delta r_{elast} = \int \frac{\sigma(r)}{E} \, dr \approx \frac{\bar{\sigma} \, L}{E}$$
   * Si se emplea un termoplástico técnico o polímero reforzado con fibra corta ($E \approx 5 - 10\text{ GPa}$):
     $$\Delta r_{elast} \approx \frac{50 \times 10^6\text{ Pa} \times 0,027\text{ m}}{10 \times 10^9\text{ Pa}} \approx 0,135\text{ mm} \quad (\mathbf{27\%}\text{ de la holgura})$$
   * Si el material sufre fluencia (*creep*) a temperatura de operación, este valor se incrementará de forma irreversible.
2. **Dilatación térmica diferencial ($\Delta r_{term}$):**
   Con un salto térmico en el rotor de $\Delta T \approx 40 - 60\text{ K}$ respecto al montaje frío y un coeficiente de dilatación térmica $\alpha \approx 30 - 50 \times 10^{-6}\text{ K}^{-1}$:
   $$\Delta r_{term} = \alpha \, \Delta T \, R \approx (40 \times 10^{-6}) \times 50 \times 41\text{ mm} \approx 0,082\text{ mm} \quad (\mathbf{16\%}\text{ de la holgura})$$
3. **Deformación dinámica, desbalanceo y juego en cojinetes ($\Delta r_{din}$):**
   La excentricidad radial admisible en rodamientos en miniatura a $> 46.000\text{ rpm}$, combinada con el descentramiento de mecanizado y el bataneo aeroelástico, consume habitualmente entre $0,10$ y $0,15\text{ mm}$.
4. **Deformación del conducto/carcasa bajo carga aerodinámica:**
   El informe menciona una carga de presión pendiente de $47\text{ kPa}$ sobre la carcasa. Si el conducto exterior se ovaliza o deflexiona localmente hacia el interior en apenas $0,15\text{ mm}$, la holgura efectiva neta se reduce a cero, provocando el roce catastrófico de punta (*tip rub*) y la destrucción del rotor.

---

## 6. SÍNTESIS DE ENTREGABLES GENERADOS Y PRUEBAS REALIZADAS

### 6.1. Archivos generados en `salidas/`
1. **`salidas/comprobaciones_centrifugas.py`:**
   * Script estándar independiente en Python 3 (sin dependencias externas).
   * Modela cinemática rotatoria, velocidad del sonido ISA, Mach de punta, cargas centrífugas analíticas y contraste sistemático de las 144 filas de `RESULTADOS.json`.
   * Exporta automáticamente tablas reproducibles y comparativas de regímenes de escalado.
2. **`salidas/test_comprobaciones_centrifugas.py`:**
   * Suite de pruebas unitarias (`unittest`) con 18 verificaciones automáticas:
     * Cinemática angular y velocidad del sonido ISA.
     * Proporcionalidad estricta $F \propto \Omega^2$, masa $m$ y radio $r$.
     * Solución analítica exacta de viga uniforme y ahusada vs modelo puntual.
     * Invariantes de escalado dimensional ($\lambda = 1,25$, ratio de fuerzas $1,00$, ratio de tensiones $0,64$).
     * Integridad de `RESULTADOS.json` y dispersión numérica de máquina ($< 10^{-12}$).
     * Límites de ingeniería: detección de Mach transónico $> 0,80$ y consumo de holgura radial $> 25\%$.
3. **`salidas/tabla_escalado_centrifugo.csv`:**
   * Registro exhaustivo (144 combinaciones) de variables cinemáticas, Mach de punta, masas, centros de masa efectivos, cargas radiales analíticas y contraste con tensiones del cribado previo.
4. **`salidas/tabla_comparativa_regimenes_escalado.csv`:**
   * Matriz comparativa entre los 3 regímenes de escalado dimensional (C01 empuje constante, velocidad de punta constante y régimen rotacional constante).
5. **`salidas/resumen_analitico.json`:**
   * Metadatos de auditoría estructurados y muestra de la estación crítica $x/R = 0,33$.
6. **`salidas/INFORME_AUDITORIA_C02.md`:**
   * El presente informe técnico detallado.

### 6.2. Resultados de las pruebas ejecutadas
* **Comando:** `python3 -m unittest salidas/test_comprobaciones_centrifugas.py`
* **Resultado:** `Ran 18 tests in 0.001s - OK`
* **Dispersión numérica máxima en integrales CAD:** $6,43 \times 10^{-16}$ (verificación de convergencia estricta).
* **Consistencia de fuerza centrífuga en parejas de semejanza:** Ratio $1,000000$ exacto en las 72 parejas.

---

## 7. LIMITACIONES EXPLÍCITAS Y RECOMENDACIONES DE FASE SIGUIENTE

1. **Ausencia de material aprobado:** Los cálculos usan densidades genéricas ($1200, 1600, 2700\text{ kg/m}^3$). No se dispone de curvas S-N de fatiga, tenacidad a la fractura, límite elástico $\sigma_y$, resistencia a tracción $\sigma_u$ ni anisotropía de compuesto.
2. **Omisión de cargas aerodinámicas:** Las cargas centrífugas aquí auditadas actúan simultáneamente con la sustentación y resistencia aerodinámica de cada perfil alar, las cuales inducen momentos flectores y torsores adicionales fuera del plano.
3. **Concentración de tensiones no lineal en la raíz ($K_t$):** La estación analizada ($x/R = 0,33$) está fuera del cubo. La unión real pala-cubo presentará concentradores de tensión geométricos que elevarán localmente las tensiones entre un $50\%$ y un $200\%$, requiriendo redondeos de acuerdo (*fillets*) optimizados.
4. **Régimen transónico en demanda vertical:** La operación a $M_{tip} = 0,825$ en D82 exige rediseñar la cuerda y el espesor relativo de punta o limitar electrónicamente las rpm máximas del controlador para no exceder $M_{tip} \approx 0,65 - 0,70$.
5. **Holgura radial de $0,5\text{ mm}$ inviable:** Se recomienda ampliar la holgura nominal a no menos de $1,0 - 1,2\text{ mm}$ o realizar un análisis termomecánico acoplado antes de congelar las cotas del utillaje.
