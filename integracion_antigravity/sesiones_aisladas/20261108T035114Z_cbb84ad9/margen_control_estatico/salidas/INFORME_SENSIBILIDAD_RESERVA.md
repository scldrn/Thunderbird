# C02: Sensibilidad estática de reserva de control por módulo (0%, 10%, 20%)

**7 de noviembre de 2026, hora de Bogotá.**  
Este documento presenta el análisis cuantitativo de sensibilidad estática para la candidata C02 (5,0 kg), evaluando el impacto de reservar un **0%**, **10%** y **20%** de la capacidad nominal de fuerza por módulo propulsor para maniobras y rechazo de perturbaciones.

> [!IMPORTANT]
> **Alcance y definición metodológica:**  
> La reserva de fuerza se modela estrictamente como una **reducción conservadora del límite utilizable** por módulo:
> $$F_{\text{utilizable}} = F_{\text{nom}} \cdot (1 - r), \quad r \in \{0{,}00;\; 0{,}10;\; 0{,}20\}$$
> Este estudio evalúa la redistribución estática y los límites analíticos de frontera. **No constituye una garantía dinámica, ni una predicción de respuesta en vuelo, ni una certificación de márgenes multieje o de potencia.**

---

## 1. Distinción explícita de datos: medidos, supuestos y cálculos

Conforme a las directrices de integridad técnica, se desglosa el origen y la categoría de cada parámetro:

### 1.1 Datos medidos
* **Ninguno.** En las referencias técnicas disponibles no existen mediciones identificadas de la planta instalada C02, ni ensayos dinámicos en banco, ni curvas de empuje/potencia de ventiladores en conducto montados, ni centro de gravedad identificado de un prototipo construido.

### 1.2 Datos supuestos (hipótesis de diseño preliminar)
* **Masa nominal del vehículo:** $m = 5{,}0\text{ kg}$ (hipótesis de la candidata C02).
* **Constante gravitatoria estándar:** $g = 9{,}80665\text{ m/s}^2$ (norma ISO 80000-3 / CODATA), resultando en un peso nominal $W = m \cdot g = 49{,}03325\text{ N}$.
* **Geometría de centros de actuación:**
  * 4 módulos idénticos dispuestos simétricamente en el plano longitudinal a $x = \pm 0{,}160\text{ m}$ ($L = 0{,}160\text{ m}$): 2 módulos traseros en $+L$ y 2 módulos delanteros en $-L$ (sistema CAD donde $+x$ apunta a la cola y $-x$ a la nariz).
  * Separación transversal a $y = \pm 0{,}076\text{ m}$ ($b = 0{,}076\text{ m}$), con 2 módulos a babor y 2 a estribor.
  * Brazo vertical relativo fuerza-CG: $z_{\text{rel}} = z_{\text{fuerza}} - z_{\text{CG}} = 0{,}0\text{ m}$ (fuerzas coplanares con el CG supuesto).
* **Posiciones longitudinales supuestas de CG:** $x_{\text{CG}} \in \{0{,}000;\; 0{,}040;\; 0{,}080;\; 0{,}096\}\text{ m}$ con $y_{\text{CG}} = 0{,}0\text{ m}$. Son puntos de variación de prueba; el valor $+0{,}096\text{ m}$ procede de una suma geométrica parcial de CAD y **no representa el CG real**.
* **Límites nominales de fuerza por módulo:** $F_{\text{nom}} \in \{20{,}58\text{ N};\; 25{,}00\text{ N}\}$ (hipótesis de empuje máximo en cono ideal).
* **Fracción de reserva escalar por módulo:** $r \in \{0{,}00;\; 0{,}10;\; 0{,}20\}$ (0%, 10%, 20%).
* **Semiconos ideales de deflexión propulsora:** $\theta \in \{35^\circ;\; 45^\circ\}$ para evaluar el potencial horizontal simultáneo.

### 1.3 Cálculos y formulación matemática
* **Límite de fuerza utilizable:**
  $$F_{\text{utilizable}} = F_{\text{nom}} \cdot (1 - r)$$
  * Para $F_{\text{nom}} = 20{,}58\text{ N}$: $F_{\text{utilizable}} \in \{20{,}580\text{ N};\; 18{,}522\text{ N};\; 16{,}464\text{ N}\}$.
  * Para $F_{\text{nom}} = 25{,}00\text{ N}$: $F_{\text{utilizable}} \in \{25{,}000\text{ N};\; 22{,}500\text{ N};\; 20{,}000\text{ N}\}$.

* **Equilibrio longitudinal en vuelo estacionario (hover):**
  Aceleración neta nula ($a_z = 0$, $a_x = 0$) y momento de cabeceo nulo respecto al CG ($M_y = 0$):
  $$\sum F_z = 2 f_{z,\text{trasero}} + 2 f_{z,\text{delantero}} = W$$
  $$\sum M_y = 2 L f_{z,\text{trasero}} - 2 L f_{z,\text{delantero}} - x_{\text{CG}} W = 0$$
  Resolviendo para la fuerza requerida por módulo:
  $$f_{z,\text{trasero}} = \frac{W}{4}\left(1 + \frac{x_{\text{CG}}}{L}\right)$$
  $$f_{z,\text{delantero}} = \frac{W}{4}\left(1 - \frac{x_{\text{CG}}}{L}\right)$$
  Para $x_{\text{CG}} \ge 0$, los módulos traseros son los más cargados ($f_{z,\text{trasero}} \ge f_{z,\text{delantero}}$).

* **Margen estático residual de fuerza en el módulo crítico:**
  $$\Delta f_{\text{crit}} = F_{\text{utilizable}} - f_{z,\text{trasero}}$$
  La condición necesaria de sustentación estacionaria es $\Delta f_{\text{crit}} \ge 0$.

* **Posición límite analítica de CG para sustentación estacionaria:**
  El estacionario se anula exactamente cuando $f_{z,\text{trasero}} = F_{\text{utilizable}}$, lo que define el CG crítico:
  $$x_{\text{CG,crit}} = L \left(\frac{4 F_{\text{utilizable}}}{W} - 1\right)$$
  Si $x_{\text{CG}} > x_{\text{CG,crit}}$, el vehículo no puede sostener su propio peso en equilibrio estático.

* **Fuerza vertical total máxima y aceleración vertical:**
  Manteniendo equilibrio de cabeceo ($M_y = 0$) mediante escalado proporcional, los módulos traseros saturan primero al alcanzar $F_{\text{utilizable}}$:
  $$F_{z,\text{máx}} = \frac{4 F_{\text{utilizable}}}{1 + |x_{\text{CG}}| / L}$$
  $$a_{z,\text{máx}} / g = \frac{F_{z,\text{máx}}}{W} - 1 = \frac{4 F_{\text{utilizable}}}{W (1 + |x_{\text{CG}}| / L)} - 1$$

* **Autoridad de momento de cabeceo a empuje total constante ($F_z = W$):**
  Un par puro de cabeceo sin alterar la sustentación total se genera variando los módulos en oposición ($\Delta f_{\text{trasero}} = -\Delta f_{\text{delantero}} = \delta$):
  * **A encabritar ($\Delta M_y^+ > 0$, subir nariz / bajar cola):** Requiere incrementar empuje trasero y reducir delantero. Limitado por la saturación trasera:
    $$\Delta M_y^+ = 4 L \min\left(F_{\text{utilizable}} - f_{z,\text{trasero}},\; f_{z,\text{delantero}}\right)$$
  * **A picar ($\Delta M_y^- > 0$, bajar nariz / subir cola):** Requiere reducir empuje trasero e incrementar delantero:
    $$\Delta M_y^- = 4 L \min\left(f_{z,\text{trasero}},\; F_{\text{utilizable}} - f_{z,\text{delantero}}\right)$$

* **Autoridad de momento de alabeo en estacionario ($\Delta M_x$):**
  Diferencial transversal a empuje y cabeceo constantes ($y = \pm b$):
  $$\Delta M_x = 2 b \left( \min(f_{z,\text{trasero}}, F_{\text{utilizable}} - f_{z,\text{trasero}}) + \min(f_{z,\text{delantero}}, F_{\text{utilizable}} - f_{z,\text{delantero}}) \right)$$

* **Aceleración horizontal simultánea en estacionario ($a_x / g$):**
  Con $z_{\text{rel}} = 0$, la fuerza horizontal máxima de cada módulo está acotada por el semicono $\theta$ y la envolvente esférica de empuje:
  $$f_{x,i} = \min\left(f_{z,i} \tan\theta,\; \sqrt{\max\left(0,\; F_{\text{utilizable}}^2 - f_{z,i}^2\right)}\right)$$
  $$a_x / g = \frac{2 f_{x,\text{trasero}} + 2 f_{x,\text{delantero}}}{W}$$

---

## 2. Resultados de la sensibilidad estática

### 2.1 Caso $F_{\text{nom}} = 20{,}58\text{ N}$ por módulo

| Reserva $r$ | $F_{\text{util}}$ (N) | $x_{\text{CG}}$ (m) | ¿Hover factible? | $f_{z,\text{tras}}$ (N) | Margen crít. (N) | Margen (% util) | $F_{z,\text{máx}}$ (N) | $a_{z,\text{máx}}$ ($g$) | $\Delta M_y^+$ (N·m) | $\Delta M_y^-$ (N·m) | $\Delta M_x$ (N·m) | $a_{x,\text{máx}}^{45^\circ}$ ($g$) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0%** | 20,580 | 0,000 | **SÍ** | 12,258 | +8,322 | 40,4% | 82,32 | +0,679 | 5,326 | 5,326 | 2,530 | 1,000 |
| **0%** | 20,580 | 0,040 | **SÍ** | 15,323 | +5,257 | 25,5% | 65,86 | +0,343 | 3,365 | 7,287 | 2,197 | 0,935 |
| **0%** | 20,580 | 0,080 | **SÍ** | 18,388 | +2,192 | 10,7% | 54,88 | +0,119 | 1,403 | 9,248 | 1,265 | 0,627 |
| **0%** | 20,580 | 0,096 | **SÍ** | 19,613 | +0,967 | 4,7% | 51,45 | +0,049 | 0,619 | 10,033 | 0,892 | 0,454 |
| **10%** | 18,522 | 0,000 | **SÍ** | 12,258 | +6,264 | 33,8% | 74,09 | +0,511 | 4,009 | 4,009 | 1,904 | 1,000 |
| **10%** | 18,522 | 0,040 | **SÍ** | 15,323 | +3,199 | 17,3% | 59,27 | +0,209 | 2,047 | 5,970 | 1,884 | 0,799 |
| **10%** | 18,522 | 0,080 | **SÍ** | 18,388 | +0,135 | 0,7% | 49,39 | +0,007 | 0,086 | 7,931 | 0,952 | 0,341 |
| **10%** | 18,522 | 0,096 | **NO** | 19,613 | **-1,091** | -5,9% | 46,31 | -0,056 | 0,000 | 0,000 | 0,000 | 0,000 |
| **20%** | 16,464 | 0,000 | **SÍ** | 12,258 | +4,206 | 25,5% | 65,86 | +0,343 | 2,692 | 2,692 | 1,279 | 0,897 |
| **20%** | 16,464 | 0,040 | **SÍ** | 15,323 | +1,141 | 6,9% | 52,68 | +0,074 | 0,730 | 4,653 | 1,279 | 0,621 |
| **20%** | 16,464 | 0,080 | **NO** | 18,388 | **-1,923** | -11,7% | 43,90 | -0,105 | 0,000 | 0,000 | 0,000 | 0,000 |
| **20%** | 16,464 | 0,096 | **NO** | 19,613 | **-3,149** | -19,1% | 41,16 | -0,161 | 0,000 | 0,000 | 0,000 | 0,000 |

### 2.2 Caso $F_{\text{nom}} = 25{,}00\text{ N}$ por módulo

| Reserva $r$ | $F_{\text{util}}$ (N) | $x_{\text{CG}}$ (m) | ¿Hover factible? | $f_{z,\text{tras}}$ (N) | Margen crít. (N) | Margen (% util) | $F_{z,\text{máx}}$ (N) | $a_{z,\text{máx}}$ ($g$) | $\Delta M_y^+$ (N·m) | $\Delta M_y^-$ (N·m) | $\Delta M_x$ (N·m) | $a_{x,\text{máx}}^{45^\circ}$ ($g$) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0%** | 25,000 | 0,000 | **SÍ** | 12,258 | +12,742 | 51,0% | 100,00 | +1,039 | 7,845 | 7,845 | 3,727 | 1,000 |
| **0%** | 25,000 | 0,040 | **SÍ** | 15,323 | +9,677 | 38,7% | 80,00 | +0,631 | 5,884 | 9,807 | 2,868 | 1,000 |
| **0%** | 25,000 | 0,080 | **SÍ** | 18,388 | +6,612 | 26,5% | 66,67 | +0,360 | 3,923 | 11,768 | 1,937 | 0,941 |
| **0%** | 25,000 | 0,096 | **SÍ** | 19,613 | +5,387 | 21,5% | 62,50 | +0,275 | 3,138 | 12,553 | 1,564 | 0,832 |
| **10%** | 22,500 | 0,000 | **SÍ** | 12,258 | +10,242 | 45,5% | 90,00 | +0,836 | 6,555 | 6,555 | 3,114 | 1,000 |
| **10%** | 22,500 | 0,040 | **SÍ** | 15,323 | +7,177 | 31,9% | 72,00 | +0,468 | 4,593 | 8,516 | 2,488 | 1,000 |
| **10%** | 22,500 | 0,080 | **SÍ** | 18,388 | +4,112 | 18,3% | 60,00 | +0,224 | 2,632 | 10,477 | 1,557 | 0,779 |
| **10%** | 22,500 | 0,096 | **SÍ** | 19,613 | +2,887 | 12,8% | 56,25 | +0,147 | 1,847 | 11,262 | 1,184 | 0,650 |
| **20%** | 20,000 | 0,000 | **SÍ** | 12,258 | +7,742 | 38,7% | 80,00 | +0,631 | 4,955 | 4,955 | 2,353 | 1,000 |
| **20%** | 20,000 | 0,040 | **SÍ** | 15,323 | +4,677 | 23,4% | 64,00 | +0,305 | 2,993 | 6,916 | 2,108 | 0,899 |
| **20%** | 20,000 | 0,080 | **SÍ** | 18,388 | +1,612 | 8,1% | 53,33 | +0,088 | 1,032 | 8,877 | 1,177 | 0,571 |
| **20%** | 20,000 | 0,096 | **SÍ** | 19,613 | +0,387 | 1,9% | 50,00 | +0,020 | 0,247 | 9,662 | 0,804 | 0,360 |

---

## 3. Hallazgos analíticos clave

1. **Inviabilidad estática inducida por la reserva en 20,58 N:**
   * Con $F_{\text{nom}} = 20{,}58\text{ N}$ y reserva del 0%, el punto $x_{\text{CG}} = +0{,}096\text{ m}$ es marginalmente viable con solo $+0{,}967\text{ N}$ de margen por módulo trasero ($a_{z,\text{máx}} = +0{,}049\text{ g}$).
   * Al aplicar una **reserva del 10%** ($F_{\text{utilizable}} = 18{,}522\text{ N}$), el CG crítico retrocede a $x_{\text{CG,crit}} = 0{,}0818\text{ m}$. Como consecuencia, **$x_{\text{CG}} = 0{,}096\text{ m}$ se vuelve estrictamente inviable** en estacionario (déficit de $-1{,}091\text{ N}$ por módulo trasero, aceleración neta vertical de $-0{,}056\text{ g}$).
   * Con una **reserva del 20%** ($F_{\text{utilizable}} = 16{,}464\text{ N}$), el CG crítico retrocede a $x_{\text{CG,crit}} = 0{,}0549\text{ m}$. Por tanto, **tanto $x_{\text{CG}} = 0{,}080\text{ m}$ como $0{,}096\text{ m}$ son inviables**.
2. **Sensibilidad del actuador de 25,00 N:**
   * Con $F_{\text{nom}} = 25{,}00\text{ N}$, todos los puntos analizados conservan factibilidad estática incluso al 20% de reserva ($x_{\text{CG,crit}} = 0{,}1010\text{ m}$).
   * No obstante, para $x_{\text{CG}} = 0{,}096\text{ m}$ con 20% de reserva, el margen residual en el módulo trasero se reduce a solo $+0{,}387\text{ N}$ (un escaso 1,9% de la fuerza utilizable), dejando una aceleración vertical neta de apenas $+0{,}020\text{ g}$.

---

## 4. Por qué la reserva de fuerza escalar NO equivale a márgenes de momento, potencia o dinámica

> [!CAUTION]
> Es un error de diseño aeronáutico considerar que una reserva escalar del 10% o 20% en empuje estático por módulo se traduce directamente en un margen del 10% o 20% en la autoridad de maniobra o en la estabilidad del vehículo. Las razones físicas se detallan a continuación.

### 4.1 No equivale a un margen de momento (asimetría y colapso de cabeceo)
1. **Asimetría drástica del par de cabeceo:**
   Cuando el CG está desplazado hacia atrás ($x_{\text{CG}} > 0$), los módulos traseros soportan una fracción desproporcionada del peso en estacionario ($19{,}61\text{ N}$ frente a $4{,}90\text{ N}$ en los delanteros para $x_{\text{CG}} = 0{,}096\text{ m}$).
   * Para generar momento a encabritar ($\Delta M_y^+ > 0$), los módulos traseros deben aumentar empuje, pero ya se encuentran al borde de la saturación.
   * Por ejemplo, para $F_{\text{nom}} = 20{,}58\text{ N}$ en $x_{\text{CG}} = 0{,}080\text{ m}$:
     * Con reserva 0%, la autoridad a encabritar es $\Delta M_y^+ = 1{,}403\text{ N}\cdot\text{m}$.
     * Con reserva 10%, la autoridad a encabritar cae a $\Delta M_y^+ = 0{,}086\text{ N}\cdot\text{m}$.
     * **¡Una reducción del 10% en el empuje utilizable destruye el 93,9% de la autoridad de cabeceo a encabritar!**
   * En contraste, la autoridad a picar ($\Delta M_y^-$) se mantiene holgada ($7{,}931\text{ N}\cdot\text{m}$) porque los módulos delanteros disponen de gran recorrido para incrementar empuje y los traseros para reducirlo.
2. **Competencia multieje simultánea:**
   El empuje de cada módulo es un escalar único. Si se requiere control simultáneo de cabeceo ($\Delta M_y$), alabeo ($\Delta M_x$), guiñada ($\Delta M_z$) y sustentación vertical ($\Delta F_z$ ante una corriente descendente), las demandas se superponen algebraicamente en los actuadores:
   $$f_{1} = f_{z,\text{hover}} + \delta_{\text{cabeceo}} + \delta_{\text{alabeo}} + \frac{\Delta F_z}{4}$$
   Una demanda combinada de apenas el 3% en sustentación, 4% en cabeceo y 4% en alabeo agota por completo la reserva escalar del 10%.

### 4.2 No equivale a un margen de potencia o energía eléctrica
1. **No linealidad de la potencia aerodinámica:**
   Por teoría elemental de cantidad de movimiento en rotores y ventiladores en conducto:
   $$T \propto \Omega^2, \quad P_{\text{aero}} = T \cdot v_i \propto T^{3/2} \propto \Omega^3$$
   Para obtener un 10% adicional de empuje en la frontera alta, la potencia mecánica demandada no aumenta en 10%, sino en aproximadamente un $(1{,}10)^{1{,}5} - 1 \approx 15{,}4\%$. Si se exige un 20% de empuje, la potencia requerida se incrementa en un $31{,}5\%$.
2. **Pérdidas térmicas óhmicas en ESC y bobinados ($I^2 R$):**
   El par motor eléctrico $Q$ es proporcional a la corriente del motor ($I \propto Q \propto T$). Las pérdidas de calor por efecto Joule en el estator y la electrónica de potencia escalan con el cuadrado del empuje:
   $$P_{\text{pérdidas}} = R_{\text{fase}} I^2 \propto T^2$$
   Un incremento del 20% de empuje eleva la disipación térmica en un $44\%$, lo que puede provocar disparos de protección térmica, saturación magnética o caída de tensión en batería (battery sag) antes de que se alcance el límite mecánico.

### 4.3 No es una garantía dinámica
1. **Inercia del conjunto rotor-motor ($J \dot{\Omega} = Q_{\text{motor}} - Q_{\text{aero}}$):**
   El cálculo estático asume disponibilidad instantánea de fuerza. En la realidad física, los ventiladores tienen inercia rotacional y constantes de tiempo de aceleración típicas de $50$ a $200\text{ ms}$. Un margen estático utilizable no previene una pérdida de control si el actuador no puede acelerar a la velocidad que exige la perturbación.
2. **Retardos de transporte y respuesta de ESCs:**
   La cadena de control (muestreo IMU $\to$ filtro $\to$ lazo PID $\to$ protocolo PWM/DShot $\to$ tiempo de respuesta del inversor) introduce retardos de fase que degradan el margen de fase del sistema, conduciendo a inestabilidad antes de que se alcancen las fronteras de fuerza estática.
3. **Aerodinámica no estacionaria e interacción con ráfagas:**
   El flujo cruzado, la distorsión del labio de entrada del conducto y el acoplamiento aerodinámico del fuselaje en vuelo hacia adelante alteran radicalmente la curva de empuje respecto al cono estático ideal aquí supuesto.

---

## 5. Resumen de verificación y pruebas realizadas

La verificación numérica del modelo se ejecutó mediante la suite automatizada `salidas/test_sensibilidad.py`:

```
----------------------------------------------------------------------
Ran 8 tests in 0.001s
OK
```

1. **`test_01_equilibrio_fuerzas_verticales_hover`:** Comprobó que la suma de sustentación de los 4 módulos iguala al peso $W = 49{,}03325\text{ N}$ en todos los 24 casos (residuo $< 10^{-12}\text{ N}$).
2. **`test_02_equilibrio_momento_cabeceo_hover`:** Comprobó que el momento resultante respecto al origen iguala a $x_{\text{CG}} \cdot W$ en todos los casos (residuo $< 10^{-12}\text{ N}\cdot\text{m}$).
3. **`test_03_reproduccion_referencia_informe_vertical`:** Validó la reproducción exacta de los límites $F_{z,\text{máx}}$ y $a_{z,\text{máx}}$ de la tabla de referencia en `INFORME-VERTICAL.md` (82,32 N / +0,679 g; 65,86 N / +0,343 g; 54,88 N / +0,119 g; 51,45 N / +0,049 g).
4. **`test_04_escalado_lineal_fuerza_utilizable`:** Verificó que $F_{z,\text{máx}}(r) = (1 - r) \cdot F_{z,\text{máx}}(0)$ con error absoluto $< 10^{-3}\text{ N}$.
5. **`test_05_frontera_factibilidad_xcg_critico`:** Validó los umbrales analíticos de corte de sustentación:
   * Para $20{,}58\text{ N}$ con $10\%$ de reserva: $x_{\text{CG,crit}} = 0{,}0818\text{ m}$ (0,080 m factible; 0,096 m inviable).
   * Para $20{,}58\text{ N}$ con $20\%$ de reserva: $x_{\text{CG,crit}} = 0{,}0549\text{ m}$ (0,040 m factible; 0,080 m inviable).
6. **`test_06_simetria_y_asimetria_de_momentos`:** Verificó la simetría exacta en $x_{\text{CG}} = 0$ y la marcada asimetría $\Delta M_y^+ < \Delta M_y^-$ para $x_{\text{CG}} > 0$.
7. **`test_07_no_equivalencia_reserva_fuerza_con_margen_cabeceo`:** Confirmó numéricamente que una reserva escalar del 10% provoca una pérdida del 93,9% en la autoridad a encabritar para $x_{\text{CG}} = 0{,}080\text{ m}$ y $F_{\text{nom}} = 20{,}58\text{ N}$.
8. **`test_08_integridad_csv_generados`:** Confirmó la existencia, encabezados válidos y dimensión exacta de los archivos CSV generados (25 filas por archivo: cabecera + 24 escenarios).

---

## 6. Archivos generados y limitaciones

### 6.1 Entregables generados en `salidas/`
1. `salidas/calcular_sensibilidad_reserva.py`: Script ejecutable en Python 3 puro (sin dependencias externas) que implementa la física, ecuaciones de equilibrio y generación de datos.
2. `salidas/test_sensibilidad.py`: Suite de 8 pruebas unitarias automatizadas basadas en `unittest`.
3. `salidas/registro_pruebas.log`: Registro completo de la ejecución exitosa de las pruebas.
4. `salidas/sensibilidad_reserva_control.csv`: Base de datos completa con las 24 combinaciones ($F_{\text{nom}} \times r \times x_{\text{CG}}$) y 20 métricas cinemáticas/estáticas por caso.
5. `salidas/resumen_sensibilidad_reserva.csv`: Tabla ejecutiva compacta para consulta rápida.
6. `salidas/INFORME_SENSIBILIDAD_RESERVA.md`: Este informe técnico detallado.

### 6.2 Limitaciones del estudio
* **Modelo puramente estático:** No modela inercias de rotor, retardos temporales, respuesta frecuencial ni estabilidad en lazo cerrado.
* **Geometría y CG supuestos:** La posición de aplicación de fuerzas, la coincidencia vertical ($z_{\text{rel}} = 0$) y el CG son aproximaciones; un brazo vertical $z_{\text{rel}} \neq 0$ acoplará fuertemente la fuerza horizontal con el cabeceo.
* **Ausencia de aerodinámica externa:** No se incluyen sustentación o resistencia del fuselaje, momentos de charnela en álabes directores ni interacción de la estela con la estructura.
* **Empuje unidireccional:** Se asume que los ventiladores no invierten empuje ($f_z \ge 0$).
