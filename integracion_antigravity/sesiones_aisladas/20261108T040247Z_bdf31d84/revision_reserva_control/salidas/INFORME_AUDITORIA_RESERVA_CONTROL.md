# INFORME DE AUDITORÍA TÉCNICA INDEPENDIENTE: LÍMITES DEL ANÁLISIS DE RESERVA DE FUERZA ESTÁTICA (CANDIDATA C02)

**Fecha:** 7 de noviembre de 2026  
**Ámbito:** Auditoría independiente de modelos estáticos preliminares de control y reserva de empuje  
**Entorno de trabajo:** Espacio aislado de ejecución (`salidas/`)  

---

## 1. Resumen ejecutivo y dictamen de auditoría

Se ha realizado una auditoría técnica independiente y exhaustiva sobre el análisis de sensibilidad y reserva de fuerza estática para la candidata aérea C02 (masa supuesta de 5,0 kg). El objeto auditado comprende los informes y scripts preliminares que evalúan el impacto de reservar un 0%, 10% y 20% del empuje nominal por módulo propulsor.

### Dictámenes principales de la auditoría:
1. **Verificación del equilibrio vertical y momentos de cabeceo:**  
   Se confirma que la formulación de equilibrio estático vertical acoplada con el momento de cabeceo es matemáticamente rigurosa bajo las hipótesis geométricas documentadas.
2. **Comprobación aritmética del caso crítico ($m = 5{,}0\text{ kg}, x_{\text{cg}} = +0{,}096\text{ m}, x_{\text{fan}} = \pm 0{,}160\text{ m}, F_{\text{nom}} = 20{,}58\text{ N}, r = 10\%$):**  
   Se comprueba de manera exacta e incontestable que la fuerza requerida por módulo de par posterior para equilibrar el peso y trimar el cabeceo es de **$19{,}6133\text{ N}$**. Al aplicar una reserva de control del 10%, el empuje utilizable disponible es de **$18{,}5220\text{ N}$**. Como $19{,}6133\text{ N} > 18{,}5220\text{ N}$ (déficit de $-1{,}0913\text{ N}$ por módulo trasero, equivalente a un $-5{,}89\%$ del empuje utilizable), **NO EXISTE EQUILIBRIO VERTICAL EN ESE MODELO**. El vehículo es estrictamente inviable para vuelo estacionario (hover) bajo dichas condiciones.
3. **Revisión crítica y rechazo de columnas de aceleración horizontal ($a_x$) y márgenes de momento ($\Delta M_y, \Delta M_x$):**  
   Las columnas numéricas de aceleración horizontal y de márgenes de momentos rotacionales publicadas en informes previos se declaran **NO SUSTENTADAS Y SE RECHAZAN FORMALMENTE** como indicadores de capacidad de maniobra en vuelo. Dichas cifras se basan en hipótesis irreales de desacoplamiento unieje perfecto, suposición no sustentada de brazo vertical nulo ($z_{\text{rel}} = 0$), empuje mínimo cero y conos esféricos sin pérdidas instaladas. No deben promoverse como prestaciones de la aeronave.

---

## 2. Distinción explícita de datos: medidos, supuestos y cálculos

En estricto cumplimiento de los principios de integridad técnica, se desglosan los datos de acuerdo con su naturaleza física, unidades y procedencia:

### 2.1 Datos medidos
* **NINGUNO.** En la documentación y referencias existentes no consta ninguna medición experimental identificada de la candidata C02. No hay ensayos de empuje instalado en banco, mediciones de labio de admisión, consumos eléctricos medidos, ni centro de gravedad determinado en balanza física de un prototipo construido.

### 2.2 Datos supuestos (hipótesis de diseño preliminar)
* **Masa nominal supuesta:** $m = 5{,}0\text{ kg}$ (especificación de diseño C02).
* **Constante gravitatoria estándar:** $g = 9{,}80665\text{ m/s}^2$ (norma ISO 80000-3 / CODATA). Peso resultante: $W = m \cdot g = 49{,}03325\text{ N}$.
* **Geometría de centros de actuación:**
  * Cuatro módulos idénticos distribuidos simétricamente en el plano longitudinal en $x_{\text{fan}} = \pm 0{,}160\text{ m}$ ($L = 0{,}160\text{ m}$): dos módulos traseros en $x = +0{,}160\text{ m}$ y dos módulos delanteros en $x = -0{,}160\text{ m}$ (sistema CAD donde $+x$ apunta a la cola y $-x$ a la nariz).
  * Separación transversal en $y_{\text{fan}} = \pm 0{,}076\text{ m}$ ($b = 0{,}076\text{ m}$), con dos módulos a babor y dos a estribor.
  * Brazo vertical fuerza-CG: $z_{\text{rel}} = z_{\text{fuerza}} - z_{\text{CG}} = 0{,}0\text{ m}$ (supuesto geométrico de coplanaridad).
* **Posiciones longitudinales supuestas de CG:** $x_{\text{cg}} \in \{0{,}000;\; 0{,}040;\; 0{,}080;\; 0{,}096\}\text{ m}$ con $y_{\text{cg}} = 0{,}0\text{ m}$. Son puntos de prueba paramétrica; la cifra $+0{,}096\text{ m}$ proviene de un centroide geométrico parcial en CAD y **no representa el CG real del vehículo**.
* **Límites nominales de empuje por módulo:** $F_{\text{nom}} \in \{20{,}58\text{ N};\; 25{,}00\text{ N}\}$ (hipótesis teóricas de límite superior en cono ideal).
* **Fracción de reserva escalar por módulo:** $r \in \{0{,}00;\; 0{,}10;\; 0{,}20\}$ ($0\%$, $10\%$, $20\%$).
* **Semiconos teóricos de empuje:** $\theta \in \{35^\circ;\; 45^\circ\}$ (conos geométricos ideales no identificados aerodinámicamente).

### 2.3 Cálculos y formulación matemática derivada
* **Empuje utilizable por módulo bajo reserva:**
  $$F_{\text{utilizable}} = F_{\text{nom}} \cdot (1 - r)$$
  * Para $F_{\text{nom}} = 20{,}58\text{ N}$: $F_{\text{utilizable}} \in \{20{,}5800\text{ N};\; 18{,}5220\text{ N};\; 16{,}4640\text{ N}\}$.
  * Para $F_{\text{nom}} = 25{,}00\text{ N}$: $F_{\text{utilizable}} \in \{25{,}0000\text{ N};\; 22{,}5000\text{ N};\; 20{,}0000\text{ N}\}$.
* **Equilibrio estático vertical en hover y trim de cabeceo:** Fuerzas $f_{z,\text{rear}}$ y $f_{z,\text{front}}$ calculadas analíticamente por estática fundamental.
* **Límite vertical de la aeronave en cabeceo equilibrado ($F_{z,\text{máx}}, a_{z,\text{máx}}$):** Deducción por saturación del módulo crítico.
* **Posición límite analítica de CG para hover ($x_{\text{cg,crit}}$):** Umbral geométrico en el que el empuje utilizable satura al peso del vehículo.

---

## 3. Verificación independiente del equilibrio vertical y momentos de cabeceo

El equilibrio en sustentación estacionaria (hover) exige simultáneamente la anulación de la fuerza vertical neta y del momento de cabeceo respecto al centro de gravedad:

$$\sum F_z = 2 f_{z,\text{rear}} + 2 f_{z,\text{front}} - W = 0$$

$$\sum M_{y,\text{cg}} = 2 (L - x_{\text{cg}}) f_{z,\text{rear}} - 2 (L + x_{\text{cg}}) f_{z,\text{front}} = 0$$

Desarrollando la ecuación de momentos:
$$2 L (f_{z,\text{rear}} - f_{z,\text{front}}) - 2 x_{\text{cg}} (f_{z,\text{rear}} + f_{z,\text{front}}) = 0$$

Sustituyendo $2(f_{z,\text{rear}} + f_{z,\text{front}}) = W$:
$$2 L (f_{z,\text{rear}} - f_{z,\text{front}}) = x_{\text{cg}} W \implies f_{z,\text{rear}} - f_{z,\text{front}} = \frac{x_{\text{cg}} W}{2 L}$$

Sumando y restando con $f_{z,\text{rear}} + f_{z,\text{front}} = \frac{W}{2}$, se obtiene la solución analítica unívoca:

$$f_{z,\text{rear}} = \frac{W}{4}\left(1 + \frac{x_{\text{cg}}}{L}\right)$$

$$f_{z,\text{front}} = \frac{W}{4}\left(1 - \frac{x_{\text{cg}}}{L}\right)$$

### Propiedades físicas comprobadas:
1. **Simetría perfecta en $x_{\text{cg}} = 0$:**  
   $f_{z,\text{rear}} = f_{z,\text{front}} = \frac{W}{4} = \frac{49{,}03325}{4} = 12{,}2583\text{ N}$ por módulo.
2. **Transferencia asimétrica de carga con $x_{\text{cg}} > 0$:**  
   A medida que el CG se desplaza hacia la cola ($+x$), los dos módulos traseros soportan una fracción monótonamente creciente del peso total, mientras que los módulos delanteros se descargan proporcionalmente.
3. **Límite de apoyo monopolar ($x_{\text{cg}} = L = 0{,}160\text{ m}$):**  
   $f_{z,\text{rear}} = \frac{W}{2} = 24{,}5166\text{ N}$ y $f_{z,\text{front}} = 0\text{ N}$.
4. **Fuerza vertical máxima en cabeceo equilibrado ($M_y = 0$):**  
   Al escalar la potencia de los módulos manteniendo cabeceo nulo, los módulos traseros alcanzan primero su límite utilizable $F_{\text{utilizable}}$, fijando el techo de empuje vertical del sistema en:
   $$F_{z,\text{máx}} = \frac{4 F_{\text{utilizable}}}{1 + |x_{\text{cg}}| / L}, \quad a_{z,\text{máx}} / g = \frac{F_{z,\text{máx}}}{W} - 1$$
   Este resultado reproduce con exactitud milimétrica la tabla documentada en la referencia `INFORME-VERTICAL.md` (líneas 42–45):
   * $x_{\text{cg}} = 0{,}000\text{ m} \to F_{z,\text{máx}} = 82{,}32\text{ N}$ ($+0{,}679\text{ g}$).
   * $x_{\text{cg}} = +0{,}040\text{ m} \to F_{z,\text{máx}} = 65{,}86\text{ N}$ ($+0{,}343\text{ g}$).
   * $x_{\text{cg}} = +0{,}080\text{ m} \to F_{z,\text{máx}} = 54{,}88\text{ N}$ ($+0{,}119\text{ g}$).
   * $x_{\text{cg}} = +0{,}096\text{ m} \to F_{z,\text{máx}} = 51{,}45\text{ N}$ ($+0{,}049\text{ g}$).

---

## 4. Comprobación aritmética estricta del caso crítico auditado

Se somete a revisión aritmética independiente el caso especificado:
* **Masa nominal:** $m = 5{,}0\text{ kg}$
* **Gravedad:** $g = 9{,}80665\text{ m/s}^2$
* **Peso resultante:** $W = 5{,}0 \times 9{,}80665 = 49{,}03325\text{ N}$
* **Cuarto de peso base ($W/4$):** $12{,}2583125\text{ N}$
* **Posición longitudinal de CG:** $x_{\text{cg}} = +0{,}096\text{ m}$
* **Semibrazo longitudinal de módulos:** $L = 0{,}160\text{ m}$
* **Relación de excentricidad:** $x_{\text{cg}} / L = 0{,}096 / 0{,}160 = 0{,}600$
* **Factor de amplificación trasero:** $1 + x_{\text{cg}}/L = 1 + 0{,}600 = 1{,}600$
* **Factor de desahogo delantero:** $1 - x_{\text{cg}}/L = 1 - 0{,}600 = 0{,}400$
* **Límite nominal por módulo:** $F_{\text{nom}} = 20{,}58\text{ N}$
* **Reserva de fuerza impuesta:** $r = 10\% = 0{,}10$

### 4.1 Cálculo del límite utilizable disponible
$$F_{\text{utilizable}} = F_{\text{nom}} \times (1 - r) = 20{,}58\text{ N} \times (1 - 0{,}10) = 20{,}58\text{ N} \times 0{,}90 = 18{,}5220\text{ N}$$

### 4.2 Cálculo de la fuerza necesaria en el módulo trasero
$$f_{z,\text{rear}} = \frac{W}{4}\left(1 + \frac{x_{\text{cg}}}{L}\right) = 12{,}2583125\text{ N} \times 1{,}600 = 19{,}61330\text{ N} \approx \mathbf{19{,}6133\text{ N}}$$

### 4.3 Cálculo de la fuerza en el módulo delantero
$$f_{z,\text{front}} = \frac{W}{4}\left(1 - \frac{x_{\text{cg}}}{L}\right) = 12{,}2583125\text{ N} \times 0{,}400 = 4{,}903325\text{ N} \approx \mathbf{4{,}9033\text{ N}}$$

### 4.4 Verificación de cierres de estática
* Cierre de sustentación: $2 \times 19{,}61330\text{ N} + 2 \times 4{,}903325\text{ N} = 39{,}22660\text{ N} + 9{,}80665\text{ N} = 49{,}03325\text{ N} \equiv W$.
* Cierre de momentos respecto al origen:
  $$\sum M_{y,0} = 2(0{,}160)(19{,}61330) - 2(0{,}160)(4{,}903325) = 0{,}320 \times 14{,}709975 = 4{,}707192\text{ N}\cdot\text{m}$$
  $$x_{\text{cg}} \cdot W = 0{,}096\text{ m} \times 49{,}03325\text{ N} = 4{,}707192\text{ N}\cdot\text{m} \implies \sum M_{y,0} - x_{\text{cg}} W = 0{,}000000\text{ N}\cdot\text{m}$$

### 4.5 Comparación y déficit en el módulo trasero
$$\text{Margen residual} = F_{\text{utilizable}} - f_{z,\text{rear}} = 18{,}5220\text{ N} - 19{,}6133\text{ N} = \mathbf{-1{,}0913\text{ N}}$$

El requerimiento de sustentación y trim supera la capacidad disponible en $1{,}0913\text{ N}$ por módulo trasero (déficit relativo del $-5{,}89\%$ respecto al límite utilizable).

### 4.6 Umbral analítico crítico de CG ($x_{\text{cg,crit}}$)
El punto geométrico máximo donde el margen de sustentación se anula exactamente ($f_{z,\text{rear}} = F_{\text{utilizable}}$) es:
$$x_{\text{cg,crit}} = L \left(\frac{4 F_{\text{utilizable}}}{W} - 1\right) = 0{,}160\text{ m} \left(\frac{4 \times 18{,}5220\text{ N}}{49{,}03325\text{ N}} - 1\right) = 0{,}160 \times (1{,}510972 - 1) = \mathbf{0{,}08175\text{ m}} \approx \mathbf{0{,}0818\text{ m}}$$

Dado que $x_{\text{cg}} = +0{,}096\text{ m} > 0{,}0818\text{ m}$, el CG evaluado se sitúa un **17,4% más retrasado** que el límite físico admisible para este nivel de empuje y reserva.

### 4.7 Dictamen categórico del caso
> [!CAUTION]
> **DICTAMEN:** Puesto que la fuerza requerida por módulo de par posterior ($19{,}6133\text{ N}$) es mayor que el límite utilizable ($18{,}5220\text{ N}$), **NO HAY EQUILIBRIO VERTICAL EN ESE MODELO**. El vehículo colapsa verticalmente y no puede realizar vuelo estacionario conservando una reserva de control del 10%.

---

## 5. Revisión crítica y rechazo de columnas no sustentadas

La auditoría ha identificado dos conjuntos de métricas promovidas en análisis previos que adolecen de graves deficiencias metodológicas y físicas. Se emite un dictamen formal de rechazo para cada una de ellas:

### 5.1 Rechazo de las columnas de aceleración horizontal ($a_x$)
En el informe previo se computó la aceleración horizontal simultánea evaluando para cada módulo la expresión escalar:
$$f_{x,i} = \min\left(f_{z,i} \tan\theta,\; \sqrt{F_{\text{utilizable}}^2 - f_{z,i}^2}\right), \quad a_x / g = \frac{\sum f_{x,i}}{W}$$

Esta columna se **RECHAZA POR FALTA DE SUSTENTO** por las siguientes razones:
1. **Suposición no sustentada de brazo vertical nulo ($z_{\text{rel}} = 0$):**  
   Al asumir $z_{\text{rel}} = 0{,}0\text{ m}$, el cálculo ignora que la fuerza horizontal $F_x$ genera momento de cabeceo:
   $$\sum M_{y,\text{cg}} = \sum x_i f_{z,i} - x_{\text{cg}} W - z_{\text{rel}} F_x$$
   En el documento de referencia `INFORME.md` (líneas 44–48), se demostró que un desvío vertical de apenas $\pm 0{,}039\text{ m}$ (menos de 4 cm) altera la aceleración horizontal de $0{,}731\text{ g}$ a $0{,}254\text{ g}$ (una asimetría de casi 3:1). Dado que el centro de gravedad vertical y el punto real de aplicación de la fuerza del conducto no se conocen ni han sido medidos, publicar un valor de $a_x$ asumiendo $z_{\text{rel}} = 0$ es un artefacto matemático sin validez física.
2. **Incoherencia con el modelo de optimización lineal de referencia:**  
   El estudio riguroso de referencia (`INFORME.md`) empleó un problema de programación lineal (LP) discretizando el cono en un poliedro interior de 65 rayos, obteniendo $a_x = 0{,}441\text{ g}$ para $x_{\text{cg}} = +0{,}096\text{ m}, r = 0\%$. La fórmula desacoplada anterior arrojó $0{,}454\text{ g}$. Promover cifras analíticas continuas que ignoran la discretización y las restricciones multieje del LP introduce discordancia numérica no validada.
3. **Ausencia de mecanismo de vectorización y pérdidas aerodinámicas instaladas:**  
   Un ventilador en conducto no puede inclinar su empuje a 35° o 45° sin sufrir desprendimiento masivo de flujo en el labio de barlovento, distorsión en el rotor y una drástica caída de empuje neto. Asumir un cono esférico ideal sin un mapa aerodinámico instalado carece de sustento ingenieril.
4. **Falsa noción de reserva operativa:**  
   La fórmula asigna el 100% del empuje restante a generar fuerza horizontal ($\sqrt{F_{\text{utilizable}}^2 - f_{z}^2}$). En este estado, el actuador no tiene margen de modulación hacia arriba ni hacia abajo para rechazo de ráfagas o control de actitud.

### 5.2 Rechazo de las columnas de márgenes de momento ($\Delta M_y^+, \Delta M_y^-, \Delta M_x$)
En el informe anterior se calcularon márgenes unieje de cabeceo y alabeo mediante:
$$\Delta M_y^+ = 4 L \min(F_{\text{utilizable}} - f_{z,\text{rear}},\; f_{z,\text{front}})$$
$$\Delta M_x = 2 b \left( \min(f_{z,\text{rear}}, F_{\text{util}} - f_{z,\text{rear}}) + \min(f_{z,\text{front}}, F_{\text{util}} - f_{z,\text{front}}) \right)$$

Estas columnas se **RECHAZAN COMO INDICADORES DE MARGEN DE CONTROL REAL** por las siguientes causas:
1. **Fantasía de desacoplamiento unieje (aislamiento ficticio de ejes):**  
   Estas expresiones asumen que el 100% del recorrido de los actuadores puede destinarse exclusivamente a cabeceo O exclusivamente a alabeo. En una aeronave VTOL real, la matriz de asignación de control mezcla simultáneamente cabeceo, alabeo, guiñada y sustentación vertical:
   $$\vec{u} = \mathbf{B} \vec{v}_{\text{control}}$$
   Cualquier corrección en alabeo consume el empuje disponible en los módulos de una banda, reduciendo de inmediato la autoridad en cabeceo a una fracción del valor unieje reportado.
2. **Suposición de empuje mínimo nulo ($f_{\text{min}} = 0$):**  
   La fórmula supone que los ventiladores pueden reducir su empuje hasta $0\text{ N}$ de manera instantánea y estable. Los motores brushless y ventiladores en conducto operan con un empuje de ralentí (idle) no nulo para evitar desincronización del ESC y pérdida de ancho de banda. Si $f_{\text{min}} > 0$, la excursión hacia abajo se acorta sustancialmente, recortando la autoridad de momento.
3. **Omisión de dinámicas de par de reacción y acoplamiento giroscópico:**  
   Las variaciones diferenciales rápidas de RPM generan par de reacción aerodinámico del estator ($Q \propto \Omega^2$) y momentos de precesión giroscópica ($\vec{\tau} = \vec{\Omega} \times \vec{L}_{\text{rotor}}$) que inducen guiñada y alabeo cruzados no compensados en este modelo 1D.
4. **Colapso extremo y asimetría no lineal:**  
   Para $F_{\text{nom}} = 20{,}58\text{ N}$ y $x_{\text{cg}} = +0{,}080\text{ m}$, al pasar de $r = 0\%$ a $r = 10\%$, la autoridad a encabritar $\Delta M_y^+$ colapsa de $1{,}403\text{ N}\cdot\text{m}$ a apenas $0{,}086\text{ N}\cdot\text{m}$ (una **pérdida del 93,9%**). Esta cifra es insignificante frente a cualquier perturbación aerodinámica externa.

---

## 6. Matriz completa de resultados auditados

A continuación se presenta la matriz completa de los 24 escenarios evaluados ($F_{\text{nom}} \times r \times x_{\text{cg}}$), auditando rigurosamente la sustentación estática y etiquetando explícitamente el estado de validez de cada indicador:

| $F_{\text{nom}}$ (N) | Reserva $r$ | $F_{\text{util}}$ (N) | $x_{\text{cg}}$ (m) | $x_{\text{cg}}/L$ | Dictamen vertical estático | $f_{z,\text{rear}}$ (N) | Margen crít. (N) | $F_{z,\text{máx}}$ (N) | $a_{z,\text{máx}}$ ($g$) | $x_{\text{cg,crit}}$ (m) | Estado columnas $a_x$ y $\Delta M$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 20,58 | 0% | 20,580 | 0,000 | 0,00 | **EQUILIBRIO FACTIBLE** | 12,258 | +8,322 | 82,32 | +0,679 | 0,1086 | RECHAZADO / NO SUSTENTADO |
| 20,58 | 0% | 20,580 | 0,040 | 0,25 | **EQUILIBRIO FACTIBLE** | 15,323 | +5,257 | 65,86 | +0,343 | 0,1086 | RECHAZADO / NO SUSTENTADO |
| 20,58 | 0% | 20,580 | 0,080 | 0,50 | **EQUILIBRIO FACTIBLE** | 18,388 | +2,192 | 54,88 | +0,119 | 0,1086 | RECHAZADO / NO SUSTENTADO |
| 20,58 | 0% | 20,580 | 0,096 | 0,60 | **EQUILIBRIO FACTIBLE** | 19,613 | +0,967 | 51,45 | +0,049 | 0,1086 | RECHAZADO / NO SUSTENTADO |
| 20,58 | 10% | 18,522 | 0,000 | 0,00 | **EQUILIBRIO FACTIBLE** | 12,258 | +6,264 | 74,09 | +0,511 | 0,0818 | RECHAZADO / NO SUSTENTADO |
| 20,58 | 10% | 18,522 | 0,040 | 0,25 | **EQUILIBRIO FACTIBLE** | 15,323 | +3,199 | 59,27 | +0,209 | 0,0818 | RECHAZADO / NO SUSTENTADO |
| 20,58 | 10% | 18,522 | 0,080 | 0,50 | **EQUILIBRIO FACTIBLE** | 18,388 | +0,135 | 49,39 | +0,007 | 0,0818 | RECHAZADO / NO SUSTENTADO |
| **20,58** | **10%** | **18,522** | **0,096** | **0,60** | **INVIABLE / SIN EQUILIBRIO** | **19,613** | **-1,091** | **46,31** | **-0,056** | **0,0818** | **INVIABLE (HOVER IMPOSIBLE)** |
| 20,58 | 20% | 16,464 | 0,000 | 0,00 | **EQUILIBRIO FACTIBLE** | 12,258 | +4,206 | 65,86 | +0,343 | 0,0549 | RECHAZADO / NO SUSTENTADO |
| 20,58 | 20% | 16,464 | 0,040 | 0,25 | **EQUILIBRIO FACTIBLE** | 15,323 | +1,141 | 52,68 | +0,074 | 0,0549 | RECHAZADO / NO SUSTENTADO |
| 20,58 | 20% | 16,464 | 0,080 | 0,50 | **INVIABLE / SIN EQUILIBRIO** | 18,388 | -1,923 | 43,90 | -0,105 | 0,0549 | INVIABLE (HOVER IMPOSIBLE) |
| 20,58 | 20% | 16,464 | 0,096 | 0,60 | **INVIABLE / SIN EQUILIBRIO** | 19,613 | -3,149 | 41,16 | -0,161 | 0,0549 | INVIABLE (HOVER IMPOSIBLE) |
| 25,00 | 0% | 25,000 | 0,000 | 0,00 | **EQUILIBRIO FACTIBLE** | 12,258 | +12,742 | 100,00 | +1,039 | 0,1663 | RECHAZADO / NO SUSTENTADO |
| 25,00 | 0% | 25,000 | 0,040 | 0,25 | **EQUILIBRIO FACTIBLE** | 15,323 | +9,677 | 80,00 | +0,631 | 0,1663 | RECHAZADO / NO SUSTENTADO |
| 25,00 | 0% | 25,000 | 0,080 | 0,50 | **EQUILIBRIO FACTIBLE** | 18,388 | +6,612 | 66,67 | +0,360 | 0,1663 | RECHAZADO / NO SUSTENTADO |
| 25,00 | 0% | 25,000 | 0,096 | 0,60 | **EQUILIBRIO FACTIBLE** | 19,613 | +5,387 | 62,50 | +0,275 | 0,1663 | RECHAZADO / NO SUSTENTADO |
| 25,00 | 10% | 22,500 | 0,000 | 0,00 | **EQUILIBRIO FACTIBLE** | 12,258 | +10,242 | 90,00 | +0,836 | 0,1337 | RECHAZADO / NO SUSTENTADO |
| 25,00 | 10% | 22,500 | 0,040 | 0,25 | **EQUILIBRIO FACTIBLE** | 15,323 | +7,177 | 72,00 | +0,468 | 0,1337 | RECHAZADO / NO SUSTENTADO |
| 25,00 | 10% | 22,500 | 0,080 | 0,50 | **EQUILIBRIO FACTIBLE** | 18,388 | +4,112 | 60,00 | +0,224 | 0,1337 | RECHAZADO / NO SUSTENTADO |
| 25,00 | 10% | 22,500 | 0,096 | 0,60 | **EQUILIBRIO FACTIBLE** | 19,613 | +2,887 | 56,25 | +0,147 | 0,1337 | RECHAZADO / NO SUSTENTADO |
| 25,00 | 20% | 20,000 | 0,000 | 0,00 | **EQUILIBRIO FACTIBLE** | 12,258 | +7,742 | 80,00 | +0,631 | 0,1010 | RECHAZADO / NO SUSTENTADO |
| 25,00 | 20% | 20,000 | 0,040 | 0,25 | **EQUILIBRIO FACTIBLE** | 15,323 | +4,677 | 64,00 | +0,305 | 0,1010 | RECHAZADO / NO SUSTENTADO |
| 25,00 | 20% | 20,000 | 0,080 | 0,50 | **EQUILIBRIO FACTIBLE** | 18,388 | +1,612 | 53,33 | +0,088 | 0,1010 | RECHAZADO / NO SUSTENTADO |
| 25,00 | 20% | 20,000 | 0,096 | 0,60 | **EQUILIBRIO FACTIBLE** | 19,613 | +0,387 | 50,00 | +0,020 | 0,1010 | RECHAZADO / NO SUSTENTADO |

---

## 7. Pruebas realizadas y validación automatizada

La verificación cuantitativa de la auditoría se ha automatizado por completo en el script `salidas/test_auditoria_reserva.py` dentro del entorno de pruebas. Las 9 pruebas unitarias se ejecutaron con éxito pleno:

```text
test_01_equilibrio_fuerzas_verticales_hover (__main__.TestAuditoriaReserva) ... ok
test_02_equilibrio_momento_cabeceo_hover (__main__.TestAuditoriaReserva) ... ok
test_03_caso_critico_especifico_aritmetica_y_deficit (__main__.TestAuditoriaReserva) ... ok
test_04_reproduccion_referencia_informe_vertical (__main__.TestAuditoriaReserva) ... ok
test_05_escalado_lineal_fuerza_utilizable (__main__.TestAuditoriaReserva) ... ok
test_06_umbral_critico_cg (__main__.TestAuditoriaReserva) ... ok
test_07_demostracion_colapso_cabeceo_desacoplado (__main__.TestAuditoriaReserva) ... ok
test_08_auditoria_critica_rechazo_columnas_desacopladas (__main__.TestAuditoriaReserva) ... ok
test_09_integridad_csv_auditados (__main__.TestAuditoriaReserva) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.001s

OK
```

### Síntesis de las comprobaciones:
1. **`test_01` (Equilibrio vertical):** Verifica que $\sum F_z = 2 f_{z,\text{rear}} + 2 f_{z,\text{front}} = W$ con error nulo ($< 10^{-12}\text{ N}$) en los 24 escenarios.
2. **`test_02` (Momento de cabeceo):** Comprueba que $2 L (f_{z,\text{rear}} - f_{z,\text{front}}) = x_{\text{cg}} W$ en todos los casos.
3. **`test_03` (Caso crítico auditado):** Valida punto por punto que para $m = 5{,}0\text{ kg}, x_{\text{cg}} = 0{,}096\text{ m}, L = 0{,}160\text{ m}, F_{\text{nom}} = 20{,}58\text{ N}, r = 10\%$, se cumple $f_{z,\text{rear}} = 19{,}6133\text{ N} > 18{,}5220\text{ N}$, déficit $=-1{,}0913\text{ N}$ y `hay_equilibrio_vertical == False`.
4. **`test_04` (Reproducción de referencia):** Comprueba la coincidencia exacta de los límites analíticos $F_{z,\text{máx}}$ y $a_{z,\text{máx}}$ con la tabla de `INFORME-VERTICAL.md`.
5. **`test_05` (Escalado lineal):** Valida que $F_{z,\text{máx}}(r) = (1 - r) F_{z,\text{máx}}(0)$ para toda combinación de CG.
6. **`test_06` (Frontera analítica $x_{\text{cg,crit}}$):** Confirma los límites analíticos exactos de sustentación ($x_{\text{cg,crit}} = 0{,}0818\text{ m}$ para 10% y $0{,}0549\text{ m}$ para 20% en 20,58 N).
7. **`test_07` (Colapso no lineal de cabeceo):** Confirma numéricamente que un 10% de reserva escalar genera una caída del $93{,}9\%$ en $\Delta M_y^+$ para $x_{\text{cg}} = 0{,}080\text{ m}$ en 20,58 N.
8. **`test_08` (Dictamen de rechazo):** Confirma que todas las columnas desacopladas quedan explícitamente dictaminadas como rechazadas en la base de datos auditada.
9. **`test_09` (Integridad de archivos):** Comprueba formato, existencia y número exacto de filas (25 filas: 1 cabecera + 24 casos) de los CSVs generados.

---

## 8. Archivos generados y limitaciones

### 8.1 Entregables generados en el espacio `salidas/`
1. **`salidas/auditar_reserva_control.py`:** Código ejecutable en Python 3 puro (estándar, sin librerías externas) que implementa las ecuaciones de equilibrio, efectúa la auditoría aritmética del caso crítico y genera las tablas de datos.
2. **`salidas/test_auditoria_reserva.py`:** Suite de 9 pruebas unitarias automatizadas (`unittest`) que reproducen y verifican los resultados numéricos y las aserciones de auditoría.
3. **`salidas/registro_pruebas_auditoria.log`:** Registro íntegro de la ejecución exitosa de la suite de pruebas.
4. **`salidas/sensibilidad_reserva_auditada.csv`:** Base de datos exhaustiva (24 combinaciones) con clasificación explícita entre columnas sustentadas y columnas desacopladas rechazadas.
5. **`salidas/resumen_auditoria_estatica.csv`:** Tabla resumen ejecutiva enfocada en la factibilidad vertical y los márgenes críticos de sustentación.
6. **`salidas/INFORME_AUDITORIA_RESERVA_CONTROL.md`:** Este informe formal de auditoría técnica.

### 8.2 Limitaciones técnicas del modelo auditado
* **Modelo puramente estático:** No incorpora la inercia rotacional del rotor ($J \dot{\Omega} = Q_{\text{motor}} - Q_{\text{aero}}$), constantes de tiempo de aceleración de los ventiladores ($50$ a $200\text{ ms}$), retardos de transporte de la IMU/ESC, ni márgenes de estabilidad en lazo cerrado.
* **Geometría y CG no identificados experimentalmente:** El punto real de aplicación tridimensional del empuje instalado, el brazo vertical efectivo ($z_{\text{rel}}$) y el centro de gravedad físico del conjunto construido siguen sin ser medidos en banco.
* **Ausencia de aerodinámica externa y flujo cruzado:** No se modelan las fuerzas y momentos de sustentación/resistencia del fuselaje, la distorsión del labio de entrada ante viento relativo o ráfagas, ni las pérdidas inducidas por interacción mutua de estelas.
* **Falta de modelo eléctrico y térmico:** El cálculo asume que los límites de empuje se sostienen indefinidamente, ignorando la caída de tensión en batería (battery sag), las pérdidas Joule en bobinados y ESCs ($I^2 R \propto T^2$) y los umbrales térmicos de operación continua.
