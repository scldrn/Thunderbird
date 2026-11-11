# Informe Técnico: Derivación de Condiciones de Fuerza Descendente y Requerimientos de Reversibilidad bajo Actitud Fija

**Fecha:** 8 de noviembre de 2026  
**Ubicación de entrega:** `salidas/INFORME_REVERSIBILIDAD_DESCENDENTE.md`  
**Archivos complementarios:** `salidas/tabla_fuerza_descendente.csv`, `salidas/verificar_condiciones.py`, `salidas/resultados_pruebas.json`  
**Arquitectura base:** Arquitectura A — Cuatro ventiladores internos integrados en el cuerpo (se mantiene sin alteraciones).  

---

## 1. Resumen Ejecutivo y Marco de Trabajo

El presente estudio deriva analíticamente las condiciones de fuerza propulsora descendente necesarias para que un vehículo aéreo con **cuatro módulos propulsores ideales** mantenga una **actitud fija horizontal** mientras ejecuta aceleraciones verticales netas hacia abajo estrictamente superiores a la aceleración de la gravedad ($a_{\text{desc}} = n \cdot g$, con $n > 1$).

### Declaraciones de Cumplimiento Normativo y Arquitectónico
1. **La arquitectura actual NO dispone de empuje reversible:** La configuración de referencia vigente (Arquitectura A, con ventiladores internos según `DECISION-ARQUITECTURA.md` y estudio `C02` en `INFORME-VERTICAL.md`) emplea rotores con conductos orientados para generar empuje neto hacia arriba ($+Z$). La variante de doble flujo (`vectorizacion_A/CAD_doble_flujo/`) permanece como un ejercicio de reserva exploratorio y no ha sido adoptada como selección formal.
2. **No equivalencia estático-dinámica:** La condición analítica aquí obtenida es un balance cuasi-estático instantáneo de fuerzas y momentos. Un equilibrio estático puntual **no valida** la dinámica de vuelo, la estabilidad en bucle cerrado, la controlabilidad en presencia de retardos ni los transitorios de maniobra.
3. **Preservación estricta de la arquitectura:** Se mantiene categóricamente la selección de **Arquitectura A (ventiladores internos)**. No se modifica el número, tipo ni disposición base de los ventiladores internos.

---

## 2. Clasificación Metodológica: Datos Medidos, Supuestos y Cálculos

Conforme a los estándares de rigor técnico, se distingue explícitamente el origen de cada parámetro:

### 2.1 Datos Medidos y Cotas Geométricas de Referencia (CAD / Modelos Previos)
- **Estaciones longitudinales y transversales de los módulos (Geometría C02):**  
  $x_i = \pm 0{,}160\text{ m}$, $y_i = \pm 0{,}076\text{ m}$ respecto al origen geométrico del cuerpo (Fuente: `entradas/investigacion-aeronautica/ejecucion/G6/autoridad_C02/INFORME-VERTICAL.md` y `DECISION-ARQUITECTURA.md`).
- **Número de módulos propulsores:** $N = 4$ conductos internos integrados.
- **Capacidad de referencia unidireccional previa:** $F_{\text{máx}} = 20{,}58\text{ N}$ por ventilador en el estudio de 5 kg (Fuente: `INFORME-VERTICAL.md`). Nota: es una cota de modelo ideal previo, no un empuje medido en banco de ensayo con conducto instalado.

### 2.2 Supuestos del Modelo
- **Actitud fija del cuerpo:** Ángulos de cabeceo ($\theta$), alabeo ($\phi$) y guiñada ($\psi$) constantes y nulos ($\theta = 0, \phi = 0, \psi = 0$). No se permite rotar el cuerpo para reorientar empuje vertical hacia abajo.
- **Cuerpo rígido ideal:** Masa concentrada y estructura indeformable.
- **Aceleración de la gravedad constante:**  
  - Valor canónico estándar: $g_0 = 9{,}80665\text{ m/s}^2$ (ISO 80000-3 / WGS-84).
  - Valor comparativo secundario: $g = 9{,}81\text{ m/s}^2$.
- **Masas supuestas del estudio:** Escalas objetivo prescritas $m \in \{2{,}0\text{ kg}, 5{,}0\text{ kg}, 10{,}0\text{ kg}\}$.
- **Aceleraciones descendentes netas prescritas:** Factores de carga $n \in \{1{,}2, 2{,}0, 5{,}0\}$, correspondientes a aceleraciones descendentes netas $a_{\text{desc}} = n \cdot g$.
- **Ausencia de fuerzas externas adicionales:** Sustentación aerodinámica nula ($L = 0$), arrastre exterior nulo ($D = 0$), empuje de propulsión axial nulo ($T_{\text{axial}} = 0$) y momentos aerodinámicos nulos.
- **Módulos propulsores ideales con capacidad reversible:** Se asume que cada módulo puede ejercer una fuerza descendente limitada $0 \le R_i \le R$ paralela al eje vertical del cuerpo.
- **Caso simétrico base:** Centro de gravedad (CG) perfectamente coincidente con el baricentro geométrico de los cuatro módulos ($x_{\text{CG}} = 0$, $y_{\text{CG}} = 0$).

### 2.3 Cálculos
- Balances analíticos de cantidad de movimiento y momento angular.
- Formulación de la desigualdad $R \ge \frac{m \cdot g \cdot (n - 1)}{4}$.
- Extensión analítica a CG longitudinal y transversalmente excéntrico.
- Evaluaciones numéricas puntuales, análisis dimensional y pruebas de equilibrio computadas en `salidas/verificar_condiciones.py`.

---

## 3. Derivación Analítica de las Condiciones de Fuerza Descendente

### 3.1 Marco de Referencia y Convención de Signos
Se define un sistema de coordenadas de cuerpo solidario a la aeronave con origen en el centroide de los cuatro actuadores:
- Eje $+X$: Longitudinal, apuntando hacia la popa/cola (según sistema CAD de referencia C02; en FLU apunta hacia adelante).
- Eje $+Y$: Transversal, apuntando a estribor.
- Eje $+Z$: Vertical, apuntando hacia el cenit (hacia arriba).
- El vector aceleración de la gravedad en este sistema es:
  $$\vec{g} = -g \, \hat{k} \quad (g > 0)$$
- Para una aceleración neta descendente de magnitud $a_{\text{desc}} = n \cdot g$, el vector aceleración lineal del vehículo es:
  $$\vec{a} = -a_{\text{desc}} \, \hat{k} = -n \cdot g \, \hat{k}$$

### 3.2 Ecuaciones de Movimiento de Newton-Euler
Para un cuerpo rígido con velocidad angular $\vec{\omega} = \vec{0}$ y aceleración angular $\dot{\vec{\omega}} = \vec{0}$ (actitud rigurosamente fija):
$$\sum \vec{F} = m \vec{a}$$
$$\sum \vec{M}_{\text{CG}} = \vec{0}$$

### 3.3 Balance de Fuerzas Verticales
En ausencia de sustentación y arrastre exterior, las únicas fuerzas que actúan en el eje $Z$ son el peso gravitatorio y las fuerzas propulsoras verticales ejercidas por los cuatro módulos:
$$\sum F_z = F_{g,z} + \sum_{i=1}^{4} F_{\text{prop},z,i}$$

El peso es:
$$F_{g,z} = -m \cdot g$$

Sea $R_i$ la magnitud de la fuerza descendente activa generada por el módulo $i$. Al actuar empujando el vehículo hacia abajo, su vector en el eje $+Z$ es:
$$F_{\text{prop},z,i} = -R_i \quad (R_i \ge 0)$$

Sustituyendo en la ecuación de Newton:
$$-m \cdot g - \sum_{i=1}^{4} R_i = m \cdot a_z$$

Como la aceleración neta descendente impuesta es $a_z = -n \cdot g$:
$$-m \cdot g - \sum_{i=1}^{4} R_i = -m \cdot n \cdot g$$

Multiplicando por $-1$ y despejando la fuerza propulsora descendente total necesaria:
$$\sum_{i=1}^{4} R_i = m \cdot n \cdot g - m \cdot g = m \cdot g \cdot (n - 1)$$

Definiendo la fuerza descendente neta requerida como $F_{\text{desc,total}} = \sum_{i=1}^{4} R_i$:
$$F_{\text{desc,total}} = m \cdot g \cdot (n - 1)$$

### 3.4 Distribución Simétrica y Condición sobre la Capacidad Máxima $R$
Consideremos las posiciones de los 4 módulos en el plano horizontal respecto al origen geométrico:
- Módulo 1 (proa-estribor o popa-estribor según cuadrante): $(+d_x, +d_y, 0)$
- Módulo 2: $(+d_x, -d_y, 0)$
- Módulo 3: $(-d_x, -d_y, 0)$
- Módulo 4: $(-d_x, +d_y, 0)$

El vector de posición relativo al centro de gravedad $\vec{r}_{\text{CG}} = (x_{\text{CG}}, y_{\text{CG}}, 0)$ es $\vec{\rho}_i = \vec{r}_i - \vec{r}_{\text{CG}}$.
El momento propulsor sobre el CG es:
$$\vec{M}_{\text{CG}} = \sum_{i=1}^{4} \vec{\rho}_i \times (-R_i \, \hat{k})$$

Desglosando en componentes cartesianas:
$$M_x = -\sum_{i=1}^{4} (y_i - y_{\text{CG}}) R_i = 0 \implies \sum_{i=1}^{4} y_i R_i = y_{\text{CG}} \sum_{i=1}^{4} R_i$$
$$M_y = \sum_{i=1}^{4} (x_i - x_{\text{CG}}) R_i = 0 \implies \sum_{i=1}^{4} x_i R_i = x_{\text{CG}} \sum_{i=1}^{4} R_i$$

Para el **caso simétrico sin excentricidad de masa** ($x_{\text{CG}} = 0, y_{\text{CG}} = 0$):
$$\sum_{i=1}^{4} y_i R_i = 0 \implies (R_1 + R_4 - R_2 - R_3) \, d_y = 0$$
$$\sum_{i=1}^{4} x_i R_i = 0 \implies (R_1 + R_2 - R_3 - R_4) \, d_x = 0$$

Dado que la función de costo habitual en control busca minimizar el esfuerzo máximo de los actuadores ($\min \max_i R_i$) o la disipación cuadrática ($\min \sum R_i^2$), la solución de equilibrio idéntico por simetría es uniforme:
$$R_1 = R_2 = R_3 = R_4 = R_0$$

Sustituyendo en la condición vertical total:
$$4 R_0 = m \cdot g \cdot (n - 1) \implies R_0 = \frac{m \cdot g \cdot (n - 1)}{4}$$

Si cada módulo posee una capacidad máxima de empuje descendente $R$ (tal que $0 \le R_i \le R$ para todo $i$):
Para que la maniobra sea físicamente realizable en este caso simétrico, es estrictamente necesario que la capacidad $R$ cubra la demanda $R_0$:
$$R \ge \frac{m \cdot g \cdot (n - 1)}{4} \quad \blacksquare$$

---

### 3.5 Generalización: Sensibilidad a la Excentricidad del CG
Si el centro de gravedad presenta una desviación respecto a la simetría geométrica ($x_{\text{CG}} \ne 0$ y/o $y_{\text{CG}} \ne 0$), el sistema de 3 ecuaciones lineales (fuerza total, momento de cabeceo y momento de alabeo) con 4 incógnitas $R_i$ admite una distribución plana estándar:
$$R_i = \frac{F_{\text{desc,total}}}{4} \left( 1 + \frac{x_i \, x_{\text{CG}}}{d_x^2} + \frac{y_i \, y_{\text{CG}}}{d_y^2} \right)$$

Dado que $x_i = \pm d_x$ e $y_i = \pm d_y$, la expresión para los cuatro módulos es:
$$R_i = \frac{m \cdot g \cdot (n - 1)}{4} \left( 1 \pm \frac{x_{\text{CG}}}{d_x} \pm \frac{y_{\text{CG}}}{d_y} \right)$$

El módulo más solicitado (en el cuadrante hacia el que se desplaza el CG) experimenta la fuerza crítica:
$$R_{\text{crítico}} = \frac{m \cdot g \cdot (n - 1)}{4} \left( 1 + \frac{|x_{\text{CG}}|}{d_x} + \frac{|y_{\text{CG}}|}{d_y} \right)$$

Por tanto, para un CG excéntrico, la condición necesaria para que ningún módulo sature es más exigente:
$$R \ge \frac{m \cdot g \cdot (n - 1)}{4} \left( 1 + \frac{|x_{\text{CG}}|}{d_x} + \frac{|y_{\text{CG}}|}{d_y} \right)$$

*Ejemplo:* Con $x_{\text{CG}} = 0{,}040\text{ m}$ y $d_x = 0{,}160\text{ m}$ (como en los ensayos de C02), el factor de amplificación es $1 + 0{,}040/0{,}160 = 1{,}25$ (+25% de demanda sobre los módulos traseros/delanteros según corresponda).

---

## 4. Pruebas Dimensionales y de Consistencia Físico-Matemática

### 4.1 Análisis Dimensional Formal
Sea la relación analítica:
$$R = \frac{m \cdot g \cdot (n - 1)}{4}$$

Analizamos las dimensiones básicas en el Sistema Internacional (SI) con la base de dimensiones:
- Masa: $[M]$ (kilogramo, $\text{kg}$)
- Longitud: $[L]$ (metro, $\text{m}$)
- Tiempo: $[T]$ (segundo, $\text{s}$)

Evaluación de los factores que componen la ecuación:
1. Masa: $[m] = \text{M}^1 \, \text{L}^0 \, \text{T}^0$
2. Aceleración gravitatoria: $[g] = \text{M}^0 \, \text{L}^1 \, \text{T}^{-2}$
3. Factor de aceleración $n$: Por definición, $n = a_{\text{desc}} / g$. Al ser el cociente entre dos aceleraciones:
   $$[n] = \frac{[a_{\text{desc}}]}{[g]} = \frac{\text{L}^1 \, \text{T}^{-2}}{\text{L}^1 \, \text{T}^{-2}} = \text{M}^0 \, \text{L}^0 \, \text{T}^0 \quad (\text{adimensional})$$
   Por ende, el binomio $(n - 1)$ es estrictamente adimensional.
4. El denominador $4$ representa la cantidad de módulos independientes, siendo un escalar entero adimensional ($[4] = 1$).

Combinando las dimensiones:
$$[R] = \frac{[m] \cdot [g] \cdot [n - 1]}{[4]} = \frac{(\text{M}^1) \cdot (\text{L}^1 \, \text{T}^{-2}) \cdot (1)}{1} = \text{M}^1 \, \text{L}^1 \, \text{T}^{-2}$$

La dimensión resultante $\text{M} \, \text{L} \, \text{T}^{-2}$ corresponde exactamente a la dimensión de la fuerza en la mecánica newtoniana:
$$[\text{Fuerza}] = \text{M} \, \text{L} \, \text{T}^{-2} \equiv \text{Newton (N)} = \text{kg} \cdot \text{m} \cdot \text{s}^{-2}$$

**Conclusión dimensional:** La ecuación es dimensionalmente homogénea y físicamente coherente.

---

## 5. Pruebas de Equilibrio y Casos Límite

Para validar la solidez de la formulación, se comprueban los balances en condiciones límite y asintóticas:

### 5.1 Caso Límite 1: Caída Libre Pura ($n = 1{,}0$, $a_{\text{desc}} = 1{,}0 \, g$)
- Sustitución: $n - 1 = 1{,}0 - 1{,}0 = 0$.
- Fuerza descendente requerida:
  $$F_{\text{desc,total}} = m \cdot g \cdot (0) = 0\text{ N} \implies R \ge 0\text{ N}$$
- **Interpretación física:** En caída libre, la gravedad proporciona exactamente la aceleración requerida ($g$). Los propulsores deben estar completamente apagados (empuje nulo). No se requiere capacidad de reversa activa para caer a $1{,}0 \, g$.

### 5.2 Caso Límite 2: Descenso Sub-gravitatorio ($0 \le n < 1{,}0$, e.g., $n = 0{,}5$)
- Sustitución: $n - 1 < 0$. Para $n = 0{,}5$, $n - 1 = -0{,}5$.
- Fuerza calculada:
  $$F_{\text{desc,total}} = -0{,}5 \, m \, g < 0$$
- **Interpretación física:** Un valor negativo de fuerza descendente indica que la gravedad por sí sola produce una aceleración superior a la deseada. Para descender a una tasa menor que $g$ (o flotar en estacionario con $n = 0$), el vehículo requiere **fuerza vertical positiva (hacia arriba)**, es decir, sustentación activa proporcionada por los ventiladores unidireccionales estándar.

### 5.3 Caso Límite 3: Descenso Hiper-gravitatorio ($n > 1{,}0$, e.g., $n \in \{1{,}2, 2{,}0, 5{,}0\}$)
- Sustitución: $n - 1 > 0$.
- **Interpretación física:** Como la gravedad solo puede aportar a lo sumo $1{,}0 \, g$ de aceleración descendente, cualquier aceleración descendente neta superior a $1{,}0 \, g$ con el fuselaje en actitud fija horizontal es matemáticamente y físicamente imposible sin una fuerza activa hacia abajo. Por ello, la reversibilidad o empuje descendente activo es una **condición necesaria**.

### 5.4 Caso Límite 4: Microgravedad o Entorno Orbital ($g \to 0$)
- Si $g \to 0$ manteniendo una aceleración lineal descendente prescrita $a_{\text{desc}}$:
  $$F_{\text{desc,total}} = m \cdot a_{\text{desc}} - m \cdot g \xrightarrow{g \to 0} m \cdot a_{\text{desc}}$$
  $$R \ge \frac{m \cdot a_{\text{desc}}}{4}$$
- Coincide exactamente con la segunda ley de Newton pura en el espacio profundo para cuatro propulsores en paralelo.

### 5.5 Comprobación Numérica del Equilibrio Estático de Fuerzas y Momentos
Las pruebas computacionales automáticas ejecutadas en `salidas/verificar_condiciones.py` evalúan:
$$\epsilon_F = \left| \left( -m \cdot g - 4 R_0 \right) - (-m \cdot n \cdot g) \right| < 10^{-12}\text{ N}$$
$$\epsilon_{M_x} = \left| \sum_{i=1}^4 y_i (-R_0) \right| < 10^{-12}\text{ N}\cdot\text{m}$$
$$\epsilon_{M_y} = \left| \sum_{i=1}^4 -x_i (-R_0) \right| < 10^{-12}\text{ N}\cdot\text{m}$$
Todas las tolerancias se satisfacen con error residual inferior a $10^{-14}$, confirmando el equilibrio estricto.

---

## 6. Tabla Numérica de Resultados

A continuación se presentan los valores analíticos calculados para las masas prescritas ($2{,}0$, $5{,}0$ y $10{,}0\text{ kg}$) y los tres factores de aceleración descendente neta ($1{,}2$, $2{,}0$ y $5{,}0\text{ g}$). 

Se adopta $g_0 = 9{,}80665\text{ m/s}^2$ como referencia canónica principal y se añade la columna de comparación directa con $g = 9{,}81\text{ m/s}^2$. Asimismo, se incluye la fuerza en kilogramo-fuerza ($\text{kgf}$, donde $1\text{ kgf} = g_0\text{ N}$).

| Masa $m$ [kg] | Factor $n$ | $(n - 1)$ | Acel. descendente $a_{\text{desc}}$ [m/s²] | Peso $W = m \cdot g$ [N] | Fuerza descendente total $F_{\text{desc}}$ [N] | $F_{\text{desc}}$ [kgf] | **Fuerza mín. por módulo $R$ ($g_0$) [N]** | $R$ [kgf] | $R$ con $g=9{,}81$ [N] | Relación $R / (W/4)$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2,0** | 1,2 | 0,2 | 11,7680 | 19,6133 | 3,9227 | 0,40 | **0,9807** | 0,10 | 0,9810 | 0,20 |
| **2,0** | 2,0 | 1,0 | 19,6133 | 19,6133 | 19,6133 | 2,00 | **4,9033** | 0,50 | 4,9050 | 1,00 |
| **2,0** | 5,0 | 4,0 | 49,0333 | 19,6133 | 78,4532 | 8,00 | **19,6133** | 2,00 | 19,6200 | 4,00 |
| **5,0** | 1,2 | 0,2 | 11,7680 | 49,0333 | 9,8066 | 1,00 | **2,4517** | 0,25 | 2,4525 | 0,20 |
| **5,0** | 2,0 | 1,0 | 19,6133 | 49,0333 | 49,0333 | 5,00 | **12,2583** | 1,25 | 12,2625 | 1,00 |
| **5,0** | 5,0 | 4,0 | 49,0333 | 49,0333 | 196,1330 | 20,00 | **49,0333** | 5,00 | 49,0500 | 4,00 |
| **10,0** | 1,2 | 0,2 | 11,7680 | 98,0665 | 19,6133 | 2,00 | **4,9033** | 0,50 | 4,9050 | 0,20 |
| **10,0** | 2,0 | 1,0 | 19,6133 | 98,0665 | 98,0665 | 10,00 | **24,5166** | 2,50 | 24,5250 | 1,00 |
| **10,0** | 5,0 | 4,0 | 49,0333 | 98,0665 | 392,2660 | 40,00 | **98,0665** | 10,00 | 98,1000 | 4,00 |

### Observaciones de la Tabla
1. **Independencia de la escala geométrica:** La condición $R / (W/4) = n - 1$ revela que la fuerza descendente por módulo normalizada por la cuarta parte del peso del vehículo depende **exclusivamente del exceso de aceleración $(n - 1)$**.
   - Para $n = 1{,}2$: Cada módulo debe suministrar en reversa el $20\%$ de su empuje de sustentación en estacionario ($0{,}20 \times W/4$).
   - Para $n = 2{,}0$: Cada módulo debe suministrar en reversa el $100\%$ de su empuje de sustentación en estacionario ($1{,}00 \times W/4$).
   - Para $n = 5{,}0$: Cada módulo debe suministrar en reversa el $400\%$ de su empuje de sustentación en estacionario ($4{,}00 \times W/4$).
2. **Contraste con la capacidad unidireccional de C02 (referencia 5 kg):**
   - El límite unidireccional hipotético explorado en C02 era $F_{\text{máx}} = 20{,}58\text{ N}$ hacia arriba.
   - Si un hipotético sistema reversible tuviera una capacidad en reversa simétrica a ese límite ($R \approx 20{,}58\text{ N}$):
     - Para $5\text{ kg}$, permitiría cubrir holgadamente $n = 1{,}2$ ($R_{\text{req}} = 2{,}45\text{ N}$) y $n = 2{,}0$ ($R_{\text{req}} = 12{,}26\text{ N}$).
     - Sin embargo, para $n = 5{,}0$ ($R_{\text{req}} = 49{,}03\text{ N}$), el requerimiento supera en más de un factor $2{,}38$ dicha cota de $20{,}58\text{ N}$, lo que demuestra que maniobras agresivas a $5{,}0\text{ g}$ con actitud fija imponen demandas propulsoras severas que no pueden satisfacerse con la potencia del esquema de 5 kg base sin un rediseño radical de los motores/rotores.

---

## 7. Declaración Formal de Omisiones y Limitaciones del Modelo

En cumplimiento estricto con los requisitos de ingeniería y auditoría técnica:

1. **La arquitectura actual es estrictamente unidireccional:**
   - La arquitectura oficial seleccionada (Arquitectura A) posee conductos orientados exclusivamente hacia la parte inferior del fuselaje para generar sustentación vertical positiva ($+Z$).
   - El vehículo **no cuenta con mecanismos de reversa instalados**, tales como inversores de paso de pala (*variable pitch*), deflectores bi-direccionales de tobera o inversión ultra-rápida de giro de motor.
   - Ninguna conclusión de este informe debe interpretarse como una afirmación de que el prototipo actual dispone de empuje descendente o capacidad de vuelo invertido.

2. **No validación dinámica por condición estática:**
   - Este estudio resuelve únicamente el balance algebraico estacionario/instantáneo: $\sum F_z = m a_z$, $\sum M = 0$.
   - **No garantiza estabilidad dinámica**, controlabilidad en lazo cerrado, amortiguamiento ante perturbaciones ni seguimiento de trayectoria.

3. **Omisiones explícitas del modelo:**
   - **Dinámica y retardo de actuadores:** No se modela la tasa de cambio de fuerza ($dF/dt$), inercia rotacional del rotor ($J \dot{\Omega}$), tiempo de respuesta del ESC o inversión de flujo en el conducto.
   - **Aerodinámica exterior e interacciones de flujo:** Se omiten las fuerzas aerodinámicas inducidas por el movimiento descendente o de avance (resistencia parasitaria, sustentación del fuselaje, momentos aerodinámicos de inclinación inducidos por la carrocería deportiva).
   - **Aerodinámica interna en flujo inverso:** El perfil de los álabes y la geometría convergente/divergente de los conductos de la Arquitectura A están optimizados para flujo descendente de aire (empuje ascendente). El funcionamiento en flujo inverso implicaría severas pérdidas por desprendimiento de capa límite, bloqueo aerodinámico y una caída drástica de la eficiencia del rotor.
   - **Efectos giroscópicos y de par de reacción:** Se desprecian los pares giroscópicos generados durante variaciones de régimen y el acoplamiento cruzado de guiñada si los rotores no estuvieran perfectamente contrarrotativos y balanceados.
   - **Límites estructurales y térmicos:** No se consideran las cargas estructurales sobre las camisas de los conductos, la refrigeración de los motores en inversión de flujo ni la disipación térmica asociada a frenado regenerativo.
   - **Reservas para maniobra angular simultánea:** La condición $R \ge \frac{m g (n-1)}{4}$ satura completamente los 4 actuadores al límite $R$ en $n=5$, dejando cero margen de autoridad para corrección de cabeceo o alabeo si se produjera la más mínima ráfaga o perturbación.

---

## 8. Conclusiones

1. Se ha derivado rigurosamente la condición analítica de fuerza propulsora descendente necesaria por módulo bajo actitud fija y gravedad:
   $$R \ge \frac{m \cdot g \cdot (n - 1)}{4}$$
2. Se verificó formalmente la homogeneidad dimensional ($\text{M} \, \text{L} \, \text{T}^{-2} = \text{Newton}$) y la consistencia en los casos límite ($n=1 \to R=0$; $n<1 \to R<0$, sustentación; $g \to 0 \to R = m a/4$).
3. Se comprobó la sensibilidad a la excentricidad del CG, demostrando que cualquier desplazamiento longitudinal o transversal amplifica la demanda en el módulo crítico por el factor $\left(1 + \frac{|x_{\text{CG}}|}{d_x} + \frac{|y_{\text{CG}}|}{d_y}\right)$.
4. La selección de la **Arquitectura A (ventiladores internos)** se mantiene firme e inalterada, reconociendo con transparencia que para alcanzar aceleraciones descendentes netas superiores a $1{,}0\text{ g}$ sin variar la actitud horizontal del cuerpo se requeriría una tecnología de empuje reversible aún no instalada ni validada dinámicamente.
