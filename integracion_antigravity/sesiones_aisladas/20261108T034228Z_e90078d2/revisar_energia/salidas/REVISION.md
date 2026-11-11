# Informe Técnico de Revisión Independiente: Ley de Arrastre Generalizada, Energía, Potencia y Dimensionamiento en C02 (5,0 kg)

**Fecha:** 7 de noviembre de 2026  
**Entorno:** Entorno autónomo aislado y reproducible  
**Estado:** Verificación matemática, física y computacional completada  
**Ubicación de entregables:** Carpeta `salidas/`  

---

## 1. Resumen Ejecutivo de la Revisión

Se ha llevado a cabo una auditoría y verificación analítica, física y numérica completamente independiente del modelo cinemático y energético basado en la ley generalizada de arrastre:

$$D(v) = D_{\text{final}} \left( \frac{v}{V} \right)^p, \quad p \in \{1, 2, 4\}$$

aplicada al vehículo aéreo conceptual **C02 (5,0 kg)** según las condiciones establecidas en los informes de referencia contenidos en `entradas/`.

### Conclusiones y Veredictos de la Auditoría:
1. **Verificación Analítica y Numérica de la Integral de Arrastre:**  
   Se confirma de manera concluyente que bajo aceleración rectilínea constante ($a = V/t$), el trabajo mecánico disipado contra el arrastre aerodinámico es exactamente:
   $$W_{\text{arrastre, acel}} = \frac{D_{\text{final}} \cdot V \cdot t}{p + 2}$$
   La deducción es válida idénticamente tanto en el dominio temporal ($\tau$) como en el dominio espacial ($x$). La integración numérica (Simpson compuesta) corrobora la fórmula cerrada con un error residual inferior a $10^{-10}\text{ J}$ (precisión de máquina en el dominio temporal).
2. **Invariancia Estricta de la Potencia Axial Pico:**  
   Dado que $(V/V)^p = 1$ para cualquier exponente $p > 0$, la fuerza de arrastre a la velocidad terminal $v = V$ es idénticamente $D_{\text{final}}$. Al ser la aceleración uniforme, la potencia mecánica axial máxima ocurre invariablemente en el instante final $\tau = t$. En consecuencia, **la potencia pico axial y la potencia pico del pack de batería son matemáticamente invariantes frente a $p$**.
3. **Gobierno por Potencia y Masa de Batería Invariante a $t = 60\text{ s}$:**  
   A $t = 60\text{ s}$ y $D_{\text{final}} = 50\text{ N}$, los 12 casos evaluados están limitados al 100% por la restricción de **densidad de potencia específica** ($5.000\text{ W/kg}$), pues la masa requerida por potencia ($3,04\text{ a }6,01\text{ kg}$) supera ampliamente la masa requerida por energía ($1,23\text{ a }2,68\text{ kg}$). Al depender la potencia únicamente del punto final, **la masa mínima de batería del vehículo resulta rigurosamente idéntica para $p = 1, 2, 4$ a $60\text{ s}$**.
4. **No Cierre Eléctrico:**  
   En los 12 casos directos con $D_{\text{final}} = 50\text{ N}$, el saldo de batería es negativo (déficits entre $-0,84\text{ kg}$ y $-3,80\text{ kg}$ frente a los $2,204\text{ kg}$ asignables en la hipótesis geométrica ligera).
5. **Advertencia Física Fundamental sobre Modelación Aerodinámica y Transónica:**  
   Se ratifica que **ninguna ley monomial $D(v) = D_{\text{final}} (v/V)^p$ tiene fundamento físico en régimen de alta velocidad ni es capaz de predecir arrastre transónico**. En particular, la elección $p = 4$ genera un artificio matemático: al estar normalizada forzadamente a $D(V) = 50\text{ N}$, produce un arrastre espuriamente bajo en las velocidades intermedias ($v < V$), lo que reduce el trabajo de arrastre en un $-33,33\%$ respecto a $p = 2$. En la aerodinámica real, la divergencia de Mach incrementa drásticamente el arrastre debido a la formación de ondas de choque disipativas (arrastre de onda).

---

## 2. Clasificación Taxativa de Fuentes y Metrología

Para garantizar transparencia metrológica, se categorizan inequívocamente todos los parámetros según su naturaleza epistemológica:

| Categoría | Elemento | Valor / Expresión | Unidad | Fuente / Justificación |
|:---|:---|:---:|:---:|:---|
| **Datos Medidos** | **Ninguno** | *No existen mediciones físicas de prototipos reales C02.* | — | No se dispone de datos de báscula calibrada, túnel de viento ni telemetría de vuelo. |
| **Supuestos (Vehículo)** | Masa total nominal C02 | $5,0$ | kg | Requisito de clase conceptual de vehículo C02. |
| **Supuestos (CAD Parcial)** | Masa asignada componentes CAD | $2,04584$ | kg | Hipótesis `ligera_1200` en `MASA_INERCIA_PARCIAL.json` (54 piezas no identificadas). |
| **Supuestos (CAD Parcial)** | Reserva provisional | $0,75$ | kg | Margen de reserva hipotético asignado en arquitectura ligera. |
| **Supuestos (CAD Parcial)** | Hardware adicional no identificado | $0,0$ | kg | Escenario de referencia optimista (sin penalización por integración). |
| **Supuestos (Batería)** | Masa neta asignable a batería | $2,20416$ | kg | Calculado como $5,0 - 2,04584 - 0,75\text{ kg}$. |
| **Supuestos (Batería)** | Densidad de energía gravimétrica útil | $150,0$ | Wh/kg | Supuesto de pack de batería Li-ion instalado. |
| **Supuestos (Batería)** | Densidad de potencia pico admisible | $5.000,0$ | W/kg | Supuesto de descarga específica máxima de pack. |
| **Supuestos (Misión)** | Tiempo fase estacionario ($t_{\text{est}}$) | $30,0$ | s | Incluye despegue, sustentación vertical inicial y maniobra. |
| **Supuestos (Misión)** | Tiempo fase maniobra lateral ($t_{\text{man}}$) | $3,0$ | s | Lapso dentro de estacionario a mayor potencia. |
| **Supuestos (Misión)** | Potencia en estacionario ($P_{\text{est}}$) | $2.968,81$ | W | Valor exploratorio derivado del modelo C01; no es ensayo de C02. |
| **Supuestos (Misión)** | Potencia en maniobra ($P_{\text{man}}$) | $3.505,89$ | W | Valor exploratorio derivado del modelo C01; no es ensayo de C02. |
| **Supuestos (Misión)** | Tiempo fase crucero ($t_{\text{crucero}}$) | $30,0$ | s | Trayectoria a velocidad final constante $V$. |
| **Supuestos (Misión)** | Eficiencia axial propulsiva ($\eta$) | $0,70$ | — | Supuesta plana y constante para todo $v \in [0, V]$. |
| **Supuestos (Misión)** | Tiempo aceleración evaluado ($t$) | $60,0$ | s | Escenario estándar comparativo (barrido extendido hasta 180 s). |
| **Supuestos (Escenario)** | Velocidades terminales ($V$) | $600,0\text{ y }1.000,0$ | km/h | $166,67\text{ m/s}$ ($M \approx 0,49$) y $277,78\text{ m/s}$ ($M \approx 0,82$). |
| **Supuestos (Escenario)** | Arrastre terminal ($D_{\text{final}}$) | $50,0$ | N | Fuerza de arrastre arbitrada a la velocidad terminal $V$. |
| **Supuestos (Escenario)** | Potencia eléctrica de apoyo ($P_{\text{aux}}$) | $0\text{ y }1.000$ | W | Carga auxiliar constante supuesta durante avance axial. |
| **Supuestos (Modelo)** | Ley paramétrica de arrastre | $D(v) = D_{\text{final}} (v/V)^p$ | N | Familia paramétrica con $p \in \{1, 2, 4\}$. |
| **Cálculos** | Aceleración media rectilínea | $a = V/t$ | $\text{m/s}^2$ | Cinemática clásica con $a = \text{constante}$. |
| **Cálculos** | Distancia de aceleración | $X = \frac{1}{2} V t$ | m | Integral de velocidad en aceleración uniforme. |
| **Cálculos** | Trabajo de arrastre en aceleración | $W_{\text{arrastre}} = \frac{D_{\text{final}} V t}{p+2}$ | J | Integral analítica verificada en este informe. |
| **Cálculos** | Energía cinética terminal | $E_{\text{cin}} = \frac{1}{2} m V^2$ | J | Teorema de fuerzas vivas ($m = 5,0\text{ kg}$). |
| **Cálculos** | Trabajo de crucero | $W_{\text{crucero}} = D_{\text{final}} V t_{\text{crucero}}$ | J | Trabajo a fuerza y velocidad constantes. |
| **Cálculos** | Energía axial eléctrica | $E_{\text{axial}} = \frac{E_{\text{cin}} + W_{\text{arrastre}} + W_{\text{crucero}}}{3600 \cdot \eta}$ | Wh | Conversión mecánica a eléctrica con $\eta = 0,70$. |
| **Cálculos** | Potencia pico axial mecánica | $P_{\text{mec, pico}} = m \frac{V^2}{t} + D_{\text{final}} V$ | W | Máximo en $\tau = t$ (independiente de $p$). |
| **Cálculos** | Potencia pico de batería | $P_{\text{pack, pico}} = \max(P_{\text{man}}, \frac{P_{\text{mec, pico}}}{\eta} + P_{\text{aux}})$ | W | Envolvente de demanda eléctrica instantánea. |
| **Cálculos** | Masa mínima de batería | $m_{\text{bat, min}} = \max\left(\frac{E_{\text{total}}}{150}, \frac{P_{\text{pack, pico}}}{5000}\right)$ | kg | Criterio envolvente bi-dimensional. |

---

## 3. Deducción Rigurosa y Verificación de la Integral de Arrastre

### 3.1. Deducción Analítica en el Dominio Temporal ($\tau$)
Un móvil parte del reposo ($v(0) = 0$) y alcanza la velocidad $V$ en el tiempo $t$ con aceleración uniforme $a = V/t$. La velocidad instantánea es:
$$v(\tau) = a \cdot \tau = V \left( \frac{\tau}{t} \right), \quad \tau \in [0, t]$$

La fuerza de arrastre prescrita por la ley paramétrica es:
$$D(v(\tau)) = D_{\text{final}} \left( \frac{v(\tau)}{V} \right)^p = D_{\text{final}} \left( \frac{\tau}{t} \right)^p$$

La potencia mecánica infinitesimal disipada por el arrastre es:
$$P_{\text{arrastre}}(\tau) = D(v(\tau)) \cdot v(\tau) = D_{\text{final}} \left( \frac{\tau}{t} \right)^p \cdot V \left( \frac{\tau}{t} \right) = D_{\text{final}} V \left( \frac{\tau}{t} \right)^{p+1}$$

El trabajo mecánico disipado en el intervalo $[0, t]$ es la integral temporal de la potencia:
$$W_{\text{arrastre, acel}} = \int_0^t P_{\text{arrastre}}(\tau) \, d\tau = D_{\text{final}} V \int_0^t \left( \frac{\tau}{t} \right)^{p+1} d\tau = \frac{D_{\text{final}} V}{t^{p+1}} \left[ \frac{\tau^{p+2}}{p + 2} \right]_0^t$$

Evaluando en los límites:
$$W_{\text{arrastre, acel}} = \frac{D_{\text{final}} V}{t^{p+1}} \cdot \frac{t^{p+2}}{p + 2} = \frac{D_{\text{final}} \cdot V \cdot t}{p + 2} \quad \blacksquare$$

### 3.2. Deducción Analítica en el Dominio Espacial ($x$)
La posición recorrida como función del tiempo es $x(\tau) = \frac{1}{2} a \tau^2 = \frac{1}{2} \frac{V}{t} \tau^2$.  
La distancia total recorrida al final de la aceleración es $X = x(t) = \frac{1}{2} V t$.  
Despejando $\tau/t$ en función de la posición normalizada:
$$\frac{x}{X} = \frac{\frac{1}{2} a \tau^2}{\frac{1}{2} a t^2} = \left( \frac{\tau}{t} \right)^2 \implies \frac{\tau}{t} = \left( \frac{x}{X} \right)^{1/2}$$

Sustituyendo en la fuerza de arrastre:
$$D(x) = D_{\text{final}} \left( \frac{\tau}{t} \right)^p = D_{\text{final}} \left( \frac{x}{X} \right)^{p/2}$$

El trabajo de arrastre es la integral de la fuerza a lo largo de la distancia:
$$W_{\text{arrastre, acel}} = \int_0^X D(x) \, dx = D_{\text{final}} \int_0^X \left( \frac{x}{X} \right)^{p/2} dx = \frac{D_{\text{final}}}{X^{p/2}} \left[ \frac{x^{\frac{p}{2} + 1}}{\frac{p}{2} + 1} \right]_0^X = D_{\text{final}} \frac{X}{\frac{p+2}{2}} = \frac{2 D_{\text{final}} X}{p + 2}$$

Sustituyendo $X = \frac{1}{2} V t$:
$$W_{\text{arrastre, acel}} = \frac{2 D_{\text{final}} \left( \frac{1}{2} V t \right)}{p + 2} = \frac{D_{\text{final}} \cdot V \cdot t}{p + 2} \quad \blacksquare$$

### 3.3. Interpretación Física por Fuerza Media Espacial ($\bar{D}_x$)
El trabajo sobre la distancia $X$ se expresa directamente como $W = \bar{D}_x \cdot X$, donde $\bar{D}_x$ es la fuerza media espacial:
$$\bar{D}_x = \frac{1}{X} \int_0^X D(x) \, dx = \frac{2}{p + 2} D_{\text{final}}$$

- Para $p = 1$: $D(x) \propto \sqrt{x}$, $\bar{D}_x = \frac{2}{3} D_{\text{final}} \approx 0,667 D_{\text{final}} \implies W = \frac{1}{3} D_{\text{final}} V t$ (+33,33 % vs $p=2$).
- Para $p = 2$: $D(x) \propto x$, $\bar{D}_x = \frac{1}{2} D_{\text{final}} = 0,500 D_{\text{final}} \implies W = \frac{1}{4} D_{\text{final}} V t$ (referencia cuadrática base).
- Para $p = 4$: $D(x) \propto x^2$, $\bar{D}_x = \frac{1}{3} D_{\text{final}} \approx 0,333 D_{\text{final}} \implies W = \frac{1}{6} D_{\text{final}} V t$ (−33,33 % vs $p=2$).

Esta deducción aclara por qué $p=4$ arroja un trabajo significativamente menor: porque la fuerza crece como una parábola espacial ($x^2$), manteniéndose casi nula durante los primeros dos tercios del recorrido y concentrándose únicamente al final.

### 3.4. Verificación Numérica Comparativa (Cuadratura Compuesta)
Se ejecutó cuadratura de Simpson con $20.000$ intervalos tanto en el dominio temporal como en el espacial:

| Velocidad ($V$) | Exponente ($p$) | Trabajo Analítico ($J$) | Numérico Temporal ($J$) | Error Rel. Temporal | Numérico Espacial ($J$) | Error Rel. Espacial |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| $600\text{ km/h}$ | $p = 1$ | $166.666,6667$ | $166.666,6667$ | $3,49 \times 10^{-16}$ | $166.666,6595$ | $4,31 \times 10^{-8}$ |
| $600\text{ km/h}$ | $p = 2$ | $125.000,0000$ | $125.000,0000$ | $3,49 \times 10^{-16}$ | $125.000,0000$ | $1,16 \times 10^{-16}$ |
| $600\text{ km/h}$ | $p = 4$ | $83.333,3333$ | $83.333,3333$ | $1,40 \times 10^{-15}$ | $83.333,3333$ | $1,75 \times 10^{-16}$ |
| $1.000\text{ km/h}$ | $p = 1$ | $277.777,7778$ | $277.777,7778$ | $2,10 \times 10^{-16}$ | $277.777,7658$ | $4,31 \times 10^{-8}$ |
| $1.000\text{ km/h}$ | $p = 2$ | $208.333,3333$ | $208.333,3333$ | $2,93 \times 10^{-15}$ | $208.333,3333$ | $1,40 \times 10^{-16}$ |
| $1.000\text{ km/h}$ | $p = 4$ | $138.888,8889$ | $138.888,8889$ | $1,68 \times 10^{-15}$ | $138.888,8889$ | $4,19 \times 10^{-16}$ |

> [!NOTE]
> **Hallazgo numérico:** En el dominio temporal, el integrando $\tau^{p+1}$ es un polinomio de grado entero ($2, 3, 5$), lo que permite a la regla de Simpson converger a precisión de punto flotante de 64 bits ($10^{-16}$). En el dominio espacial con $p=1$, el integrando es $x^{1/2} = \sqrt{x}$; la derivada $\frac{d}{dx}\sqrt{x} = \frac{1}{2\sqrt{x}}$ presenta una singularidad infinita en $x = 0$, reduciendo la tasa de convergencia asintótica de Simpson a un residuo de $4,3 \times 10^{-8}$.

---

## 4. Análisis Analítico de Potencia y Energía

### 4.1. Perfil Temporal de Potencia y Monotonía Estricta
La potencia mecánica total requerida por el propulsor axial en el instante $\tau \in [0, t]$ es la suma del término inercial y del término de arrastre:
$$P_{\text{mec}}(\tau) = F_{\text{prop}}(\tau) \cdot v(\tau) = [m a + D(v(\tau))] v(\tau) = m \left(\frac{V}{t}\right)^2 \tau + D_{\text{final}} V \left( \frac{\tau}{t} \right)^{p+1}$$

Calculando su derivada temporal:
$$\frac{d P_{\text{mec}}}{d\tau} = m \left(\frac{V}{t}\right)^2 + (p + 1) \frac{D_{\text{final}} V}{t} \left( \frac{\tau}{t} \right)^p$$

Dado que $m > 0$, $V > 0$, $t > 0$, $D_{\text{final}} \ge 0$, $p > 0$ y $\tau \ge 0$, se cumple de manera estricta que:
$$\frac{d P_{\text{mec}}}{d\tau} > 0, \quad \forall \tau \in [0, t]$$

Por tanto, **la potencia mecánica axial es estrictamente monótona creciente en todo el intervalo de aceleración**, alcanzando su valor máximo global de forma única y exclusiva en el instante terminal $\tau = t$ ($v = V$).

### 4.2. Demostración Formal de la Invariancia de la Potencia Pico
Evaluando en $\tau = t$ ($v = V$):
$$P_{\text{mec, pico}} = m \left(\frac{V}{t}\right)^2 t + D_{\text{final}} V \left( \frac{t}{t} \right)^{p+1} = \frac{m V^2}{t} + D_{\text{final}} V (1)^{p+1} = \frac{m V^2}{t} + D_{\text{final}} V$$

Obsérvese que para todo $p > 0$:
$$1^{p+1} = 1$$

Por consiguiente, el exponente $p$ desaparece completamente de la potencia pico terminal:
$$P_{\text{axial, pico}} = \frac{1}{\eta} \left( \frac{m V^2}{t} + D_{\text{final}} V \right)$$
$$P_{\text{pack, pico}} = \max\left( P_{\text{man}}, P_{\text{axial, pico}} + P_{\text{aux}} \right)$$

Esto demuestra matemáticamente por qué **la potencia pico de batería es exactamente idéntica para $p = 1$, $p = 2$ y $p = 4$**.

---

## 5. Comparación Sistemática: Los 12 Casos Directos

La siguiente tabla resume los 12 casos directos solicitados ($D_{\text{final}} = 50\text{ N}$, $t = 60\text{ s}$, $V \in \{600, 1000\}\text{ km/h}$, $P_{\text{aux}} \in \{0, 1000\}\text{ W}$, $p \in \{1, 2, 4\}$):

| $V$ (km/h) | $P_{\text{aux}}$ (W) | $p$ | $W_{\text{arrastre}}$ (kJ) | Var. $W$ vs $p=2$ | $E_{\text{total}}$ (Wh) | Var. $E$ vs $p=2$ | $P_{\text{batería, pico}}$ (kW) | $m_{\text{bat, E}}$ (kg) | $m_{\text{bat, P}}$ (kg) | $m_{\text{bat, min}}$ (kg) | Limitante | Saldo Ligero (kg) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **600** | **0** | **1** | $166,67$ | $+33,33\text{ \%}$ | **218,09** | $+8,20\text{ \%}$ | **15,21** | $1,45$ | **3,04** | **3,04** | Potencia | $-0,84$ |
| **600** | **0** | **2** | $125,00$ | *base ($0\text{ \%}$)* | **201,55** | *base ($0\text{ \%}$)* | **15,21** | $1,34$ | **3,04** | **3,04** | Potencia | $-0,84$ |
| **600** | **0** | **4** | $83,33$ | $-33,33\text{ \%}$ | **185,02** | $-8,20\text{ \%}$ | **15,21** | $1,23$ | **3,04** | **3,04** | Potencia | $-0,84$ |
| **600** | **1.000** | **1** | $166,67$ | $+33,33\text{ \%}$ | **243,09** | $+7,30\text{ \%}$ | **16,21** | $1,62$ | **3,24** | **3,24** | Potencia | $-1,04$ |
| **600** | **1.000** | **2** | $125,00$ | *base ($0\text{ \%}$)* | **226,55** | *base ($0\text{ \%}$)* | **16,21** | $1,51$ | **3,24** | **3,24** | Potencia | $-1,04$ |
| **600** | **1.000** | **4** | $83,33$ | $-33,33\text{ \%}$ | **210,02** | $-7,30\text{ \%}$ | **16,21** | $1,40$ | **3,24** | **3,24** | Potencia | $-1,04$ |
| **1.000** | **0** | **1** | $277,78$ | $+33,33\text{ \%}$ | **377,31** | $+7,88\text{ \%}$ | **29,03** | $2,52$ | **5,81** | **5,81** | Potencia | $-3,60$ |
| **1.000** | **0** | **2** | $208,33$ | *base ($0\text{ \%}$)* | **349,75** | *base ($0\text{ \%}$)* | **29,03** | $2,33$ | **5,81** | **5,81** | Potencia | $-3,60$ |
| **1.000** | **0** | **4** | $138,89$ | $-33,33\text{ \%}$ | **322,19** | $-7,88\text{ \%}$ | **29,03** | $2,15$ | **5,81** | **5,81** | Potencia | $-3,60$ |
| **1.000** | **1.000** | **1** | $277,78$ | $+33,33\text{ \%}$ | **402,31** | $+7,35\text{ \%}$ | **30,03** | $2,68$ | **6,01** | **6,01** | Potencia | $-3,80$ |
| **1.000** | **1.000** | **2** | $208,33$ | *base ($0\text{ \%}$)* | **374,75** | *base ($0\text{ \%}$)* | **30,03** | $2,50$ | **6,01** | **6,01** | Potencia | $-3,80$ |
| **1.000** | **1.000** | **4** | $138,89$ | $-33,33\text{ \%}$ | **347,19** | $-7,35\text{ \%}$ | **30,03** | $2,31$ | **6,01** | **6,01** | Potencia | $-3,80$ |

### Puntos Salientes de la Comparación:
1. **Masa Mínima Idéntica:** Para una velocidad y apoyo dados, $m_{\text{bat, min}}$ es exactamente igual para $p = 1, 2, 4$ porque $m_{\text{bat, P}} > m_{\text{bat, E}}$ en todos los casos a $60\text{ s}$.
2. **Saldo de Batería Negativo en Todos los Casos:** Ninguno de los 12 escenarios cierra dentro del presupuesto de masa disponible ($2,204\text{ kg}$). A $1.000\text{ km/h}$, la masa de batería requerida ($5,81\text{ a }6,01\text{ kg}$) supera incluso la masa total del vehículo completo ($5,0\text{ kg}$).
3. **Tiempos de Cruce Hacia Régimen Dominado por Energía ($t^*$):**  
   Para que el diseño pase a estar dominado por energía ($m_{\text{bat, E}} > m_{\text{bat, P}}$), el tiempo de aceleración debe superar $t^*$:
   - A $600\text{ km/h}$, $0\text{ W}$: $t^*(p=1) = 211,7\text{ s}$, $t^*(p=2) = 274,4\text{ s}$, $t^*(p=4) = 399,3\text{ s}$.
   - A $1.000\text{ km/h}$, $0\text{ W}$: $t^*(p=1) = 219,6\text{ s}$, $t^*(p=2) = 280,9\text{ s}$, $t^*(p=4) = 402,0\text{ s}$.
   Todos estos tiempos superan holgadamente la cota de misión de $60\text{ s}$ e incluso el límite ampliado de $180\text{ s}$.

---

## 6. Catálogo Crítico de Defectos Físicos y Supuestos No Físicos

A continuación se documentan con detalle los supuestos no físicos y defectos estructurales identificados en los modelos analizados:

### Defecto 1: Inadecuación Física del Modelo $D(v) = D_{\text{final}} (v/V)^p$ y Falsa Representación Transónica
- **Carencia de base aerodinámica:** La fuerza aerodinámica real responde a $D = \frac{1}{2} \rho v^2 S C_D(Re, M, \alpha)$.
- **Inaplicabilidad de $p = 1$:** La ley lineal corresponde al flujo de Stokes para números de Reynolds $Re \ll 1$ (micropartículas en medios viscosos). Para C02 a $600\text{ km/h}$, $Re \approx 5 \times 10^6$, régimen plenamente turbulento incompresible donde el arrastre es estrictamente cuadrático ($p = 2$).
- **Paradoja espuria de $p = 4$ frente a la divergencia de Mach:** Podría suponerse erróneamente que $p = 4$ "simula el arrastre transónico" por crecer rápido al final. Sin embargo:
  1. La formulación fuerza $D(V) = D_{\text{final}} = 50\text{ N}$. En la física real transónica ($M \approx 0,82$ a $1.000\text{ km/h}$), el coeficiente $C_D$ se dispara drásticamente por arrastre de onda, pudiendo triplicar o quintuplicar el arrastre respecto a la predicción subsónica.
  2. Como $(v/V) < 1$ en todo el trayecto previo, $(v/V)^4 \ll (v/V)^2$. Por ejemplo, a la mitad de la velocidad ($v/V = 0,5$), $(0,5)^4 = 0,0625$ frente a $(0,5)^2 = 0,25$ (un factor de 4 veces menor).
  3. Esto provoca que $p = 4$ subestime artificialmente el arrastre subsónico durante casi toda la aceleración, entregando un consumo de arrastre un **$-33,33\%$ menor** que el caso base $p = 2$, lo cual contradice frontalmente la realidad física del vuelo transónico donde el arrastre de onda incrementa la disipación energética.
- **Ausencia del parámetro termodinámico Mach ($M$):** La variable independiente normalizada es $v/V$, no $v/a_{\text{sonido}}$. No existe dependencia con la temperatura del aire $T$, la relación de calores específicos $\gamma$, ni la regla de las áreas de Whitcomb.

### Defecto 2: Eficiencia Axial Plana Constante a Velocidad Cero ($\eta = 0,70$)
- En el modelo, $P_{\text{axial}}(\tau) = \frac{F_{\text{prop}}(\tau) \cdot v(\tau)}{\eta}$.
- Cuando $\tau = 0$, $v(0) = 0$, lo que implica $P_{\text{axial}}(0) = 0\text{ W}$.
- **Violación de la teoría del disco actuador de Rankine-Froude:** Generar empuje estático $T = m \cdot a = 5,0 \cdot (166,67/60) = 13,89\text{ N}$ a velocidad de avance nula requiere una potencia inducida finita no nula:
  $$P_i = T \sqrt{\frac{T}{2 \rho A}} > 0$$
  Asumir $\eta = 0,70$ constante asigna potencia eléctrica cero al reposo, violando la conservación del momento en fluidos.

### Defecto 3: Hipótesis Cinemática de Aceleración Uniforme ($a = \text{constante}$)
- En una aeronave con propulsión eléctrica real, la planta motriz está limitada por potencia máxima continua del inversor/motor ($P_{\text{máx}}$).
- A potencia constante, el empuje disponible disminuye hiperbólicamente con la velocidad ($T \approx P/v$), lo que genera aceleraciones elevadas a baja velocidad y aceleraciones decrecientes a alta velocidad ($a(v) \sim 1/v$).
- Forzar $a = \text{constante}$ impone una curva de demanda de potencia que escala monótonamente hasta un pico abrupto en $v = V$, exigiendo un sobredimensionamiento severo de potencia en el último segundo de aceleración.

### Defecto 4: Desacoplamiento Completo entre Sustentación y Arrastre (Omisión del Arrastre Inducido)
- El arrastre total de un ala o fuselaje sustentador comprende arrastre parásito y arrastre inducido:
  $$D_{\text{total}} = q S C_{D0} + \frac{2 W^2}{\rho v^2 \pi b^2 e}$$
- A bajas velocidades ($v \to 0$), el arrastre inducido por sustentación es muy elevado ($\sim 1/v^2$); a altas velocidades domina el arrastre parásito ($\sim v^2$).
- El modelo paramétrico unidimensional $D(v) = D_{\text{final}} (v/V)^p$ y la adición desacoplada de una carga constante $P_{\text{aux}}$ omiten la física polar de la aeronave y la transición aerodinámica de sustentación por sustentador rotativo a ala fija.

### Defecto 5: Modelo Electroquímico Ideal y Régimen de Descarga Imposible
- A $1.000\text{ km/h}$ y $0\text{ W}$, la potencia de batería requerida es de $29,03\text{ kW}$ sobre una energía total de $349,75\text{ Wh}$.
- La tasa de descarga equivalente en C-rate es:
  $$\text{C-rate} = \frac{29.027\text{ W}}{349,75\text{ Wh}} \approx 83\text{ C}$$
- A $600\text{ km/h}$ y $0\text{ W}$, la tasa es $\frac{15.211\text{ W}}{201,55\text{ Wh}} \approx 75\text{ C}$.
- **Imposibilidad electroquímica:** Ninguna celda secundaria comercial con densidad de energía de $150\text{ Wh/kg}$ a nivel pack puede sostener descargas continuas de $75\text{ a }83\text{ C}$ durante $60\text{ s}$ sin colapso inmediato de tensión por caída óhmica ($I R$), pérdida drástica de capacidad disponible (ley de Peukert) y descontrol térmico destructivo.
- No se modelan las masas de los sistemas auxiliares de refrigeración líquida activa ni la resistencia de barraje.

### Defecto 6: Incertidumbre Estructural del Presupuesto de Masa
- El presupuesto disponible de $2,20416\text{ kg}$ se sustenta en un cómputo geométrico CAD incompleto con 54 componentes sin identificación de material ni masa real asignada.
- No existe asignación de masa para arneses de potencia de alta corriente (que para $30\text{ kW}$ a baja tensión exigen conductores gruesos), disipadores térmicos, conectores ni instrumentación de vuelo.

---

## 7. Defectos de Código y Entorno Detectados en las Copias y Correcciones Realizadas

Durante la revisión y copia de los archivos de código a `salidas/`, se identificaron y subsanaron los siguientes defectos:

1. **Defecto de Resolución de Rutas Relativas:**  
   - En el código de entrada original, las rutas hacia los archivos de referencia estaban fijadas como `HERE.parent / "entradas"`. Al ejecutarse desde subdirectorios o entornos aislados donde la jerarquía difiere, las rutas fallaban.  
   - **Corrección realizada en la copia:** Se implementó la función `find_entradas_dir(start)` en `salidas/sensibilidad_ley_arrastre.py`, la cual explora dinámicamente el árbol hacia la raíz localizando de manera robusta la carpeta `entradas/` sin depender de una profundidad fija.
2. **Permisos de Archivo Heredados de Referencias Read-Only:**  
   - Al copiar con `cp` las plantillas desde `entradas/`, los archivos heredaron permisos de solo lectura (`-r--r--r--`), impidiendo su modificación. Se ajustaron los permisos exclusivamente sobre las copias en `salidas/` mediante `chmod u+w`.
3. **Carencia de Validación Espacial y Monotonía en la Suite de Pruebas Original:**  
   - La suite original contaba con 10 pruebas unitarias enfocadas en el dominio temporal y la reproducción de casos.  
   - **Corrección y ampliación en la copia:** Se amplió la suite en `salidas/test_sensibilidad.py` a **15 pruebas unitarias**, agregando:
     - `test_drag_force_at_terminal_speed`: Comprobación explícita de $D(V) = D_{\text{final}}$ para 7 valores de $p$.
     - `test_spatial_vs_temporal_drag_integral`: Verificación formal de la identidad integral en el dominio espacial ($x$).
     - `test_power_profile_monotonicity`: Verificación de monotonía estricta de la potencia mecánica y localización del pico en el borde terminal.
     - `test_cruise_work_invariance_with_p`: Comprobación de que la fase de crucero es independiente de $p$.
     - `test_negative_battery_margin_all_12_cases`: Validación de que ningún caso de 50 N cierra con saldo positivo.

---

## 8. Trazabilidad Criptográfica de Archivos y Entregables

### Archivos de Entrada (Solo Lectura en `entradas/`):
- `entradas/investigacion-aeronautica/ejecucion/G1/potencia_simultanea_c02/INFORME.md`  
  SHA-256: `d7b724afd7b48b7058a1d1969afa4b869f14629d709d72e30f3170f03ee1627a`
- `entradas/investigacion-aeronautica/ejecucion/G1/potencia_simultanea_c02/calcular_r2.py`  
  SHA-256: `73d70339ce0ce124d239c22a4cde8282b85f77becb0d163c138301066cd3b67a`
- `entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/energia_ley_arrastre/salidas/REPORTE_SENSIBILIDAD_ARRASTRE.md`  
  SHA-256: `74f0c9780fc93dd3cb4bda43f3dd5dfbb9bc19cf2c7e0f8f1c843eebccb1e60f`

### Archivos Generados en `salidas/`:
- `salidas/sensibilidad_ley_arrastre.py`: Script principal corregido con resolución dinámica y cuadraturas temporal/espacial.
- `salidas/test_sensibilidad.py`: Suite ampliada a 15 pruebas unitarias automatizadas.
- `salidas/tabla_comparacion_casos.csv`: Matriz de los 12 casos directos con diferencias respecto a $p=2$.
- `salidas/tabla_sensibilidad_completa.csv`: Matriz extendida de 90 escenarios paramétricos.
- `salidas/resultados_sensibilidad.json`: Resumen estructurado en JSON con comprobaciones de cuadratura y tiempos de cruce.
- `salidas/REVISION.md`: Este informe técnico de auditoría y revisión independiente.

---

## 9. Pruebas Realizadas y Resultados de Verificación

Se ejecutó la suite de pruebas unitarias en `salidas/test_sensibilidad.py`:
- **Comando:** `python3 salidas/test_sensibilidad.py`
- **Total de pruebas ejecutadas:** 15 pruebas unitarias estándar.
- **Resultado:** 15 aprobadas (`OK`), 0 fallos, 0 errores.
- **Tiempo de ejecución:** $0,047\text{ s}$.

### Desglose de las 15 Comprobaciones:
1. `test_c02_constants_integrity`: Integridad de parámetros de C02 (masa $5,0\text{ kg}$, tiempos, eficiencias, densidades).
2. `test_analytical_integral_formula`: Validación de la fórmula analítica cerrada $\frac{D_{\text{final}} V t}{p+2}$ para $p \in \{1, 2, 4\}$.
3. `test_numerical_vs_analytical_quadrature`: Convergencia temporal de Simpson vs analítica en 7 configuraciones (error rel. $< 10^{-9}$).
4. `test_drag_work_theoretical_ratios`: Verificación de las razones teóricas exactas $4/3$ y $2/3$ frente a $p=2$.
5. `test_reproduction_of_reference_cases_p2`: Reproducción exacta de los casos de $50\text{ N}$ del informe de referencia (`INFORME.md`).
6. `test_peak_power_invariance_with_p`: Demostración formal de la invariancia de potencia axial y de pack con respecto a $p$.
7. `test_energy_sensitivity_across_p`: Monotonía decreciente estricta de la energía total y masa por energía con respecto a $p$.
8. `test_active_constraint_at_60s`: Comprobación de que la potencia gobierna el dimensionamiento en los 12 casos a $60\text{ s}$.
9. `test_crossover_time_existence`: Existencia y monotonía de los tiempos de cruce $t^*(p)$ hacia el régimen dominado por energía.
10. `test_input_validation`: Rechazo robusto de parámetros físicos inválidos (velocidades o tiempos nulos/negativos, arrastres negativos).
11. `test_drag_force_at_terminal_speed`: Validación de que $D(V) = D_{\text{final}}$ invariablemente para cualquier exponente $p > 0$.
12. `test_spatial_vs_temporal_drag_integral`: Identidad de la integral espacial $\int_0^X D(x) dx$ y la temporal $\int_0^t P dt$, analizando la singularidad de $\sqrt{x}$ para $p=1$.
13. `test_power_profile_monotonicity`: Comprobación de que la potencia mecánica es estrictamente monótona creciente en $\tau \in [0, t]$.
14. `test_cruise_work_invariance_with_p`: Comprobación de que el trabajo de arrastre en crucero es exactamente $D_{\text{final}} V t_{\text{crucero}}$, independiente de $p$.
15. `test_negative_battery_margin_all_12_cases`: Validación de que los 12 casos centrales con $50\text{ N}$ presentan saldo de batería estrictamente negativo.

---

## 10. Limitaciones Explícitas del Estudio

1. **Aproximación Cinemática Prescriptiva:** La cinemática de aceleración constante $a = V/t$ es una hipótesis de diseño impuesta, no la respuesta dinámica de un sistema aero-propulsivo acoplado a las ecuaciones de movimiento de Newton-Euler.
2. **Inexistencia de Modelo CFD o Ensayos de Arrastre Real:** No se cuenta con mapas aerodinámicos bidimensionales ni tridimensionales generados mediante dinámica de fluidos computacional (RANS/LES) ni ensayos experimentales en túnel subsónico/transónico.
3. **No Representatividad Transónica:** Ninguna ley polinómica $D(v) \propto v^p$ predice arrastre transónico, divergencia de Mach, aparición de ondas de choque locales ni desprendimiento inducido por gradientes adversos de presión.
4. **Simplificación Termo-Electroquímica:** Las densidades de $150\text{ Wh/kg}$ y $5.000\text{ W/kg}$ no contemplan impedancia interna de celda, calentamiento Joule ($I^2 R$), balance térmico, degradación cíclica ni caída de tensión bajo tasas C extremas ($> 70\text{ C}$).
5. **Presupuesto Geométrico Ligero No Vinculante:** La masa asignada de $2,20416\text{ kg}$ para batería no constituye una cota demostrada para vuelo; omite la masa de aviónica completa, actuadores de timones, cableado de potencia y arquitectura de fijación estructural.
6. **No Transferibilidad a Otras Escalas:** Los resultados son válidos únicamente para las condiciones nominales supuestas en C02 (5,0 kg) y no son extrapolables de manera lineal a plataformas de 2 kg ni de 10 kg.
