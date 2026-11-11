# Sensibilidad del Trabajo de Aceleración y Dimensionamiento de Batería para C02 (5 kg)

**Fecha:** 7 de noviembre de 2026  
**Contexto:** Evaluación aerotécnica y energética independiente sobre la candidata C02 de 5,0 kg  
**Autor:** Antigravity (Entorno autónomo aislado)  

---

## 1. Resumen Ejecutivo

Este informe documenta el estudio de sensibilidad independiente del trabajo mecánico y consumo eléctrico durante la fase de aceleración rectilínea uniforme bajo la familia paramétrica de leyes de arrastre:

$$D(v) = D_{\text{final}} \left( \frac{v}{V} \right)^p, \quad p \in \{1, 2, 4\}$$

El estudio mantiene de forma estricta e íntegra la misión, la arquitectura y los supuestos de la candidata **C02 (5,0 kg)** establecidos en el informe de referencia (`entradas/.../potencia_simultanea_c02/INFORME.md`).

### Hallazgos Principales:
1. **Verificación Analítica y Numérica de la Integral de Arrastre:** Se comprueba analíticamente que el trabajo mecánico realizado contra el arrastre durante la aceleración constante es exactamente:
   $$W_{\text{arrastre, acel}} = \frac{D_{\text{final}} \cdot V \cdot t}{p + 2}$$
   La integración numérica de cuadratura compuesta (Simpson) converge a la formulación analítica con un error residual inferior a $10^{-10}\text{ J}$ (error relativo $< 10^{-15}$).
2. **Impacto en el Trabajo y Energía:**
   - Para $p = 1$ (crecimiento lineal con la velocidad), el trabajo de arrastre en aceleración es $\frac{D V t}{3}$, lo que representa un **+33,33 %** respecto al caso base cuadrático ($p = 2$).
   - Para $p = 2$ (arrastre cuadrático clásico con $C_D$ constante), el trabajo es $\frac{D V t}{4}$.
   - Para $p = 4$ (crecimiento rápido de cuarto orden), el trabajo es $\frac{D V t}{6}$, lo que representa un **−33,33 %** respecto al caso base.
   - La energía eléctrica total de la misión varía entre un **+7,3 % y +8,2 %** para $p = 1$, y disminuye entre un **−7,3 % y −8,2 %** para $p = 4$, para $D_{\text{final}} = 50\text{ N}$ y $t = 60\text{ s}$.
3. **Invariancia Estricta de la Potencia Pico:** La potencia mecánica y eléctrica axial máxima requerida durante el avance ocurre invariablemente al final de la aceleración ($v = V$). Dado que $(V/V)^p = 1$ para cualquier $p > 0$, la fuerza de arrastre final es idénticamente $D_{\text{final}} = 50\text{ N}$. En consecuencia, **la potencia pico de batería es exactamente idéntica para $p = 1, 2, 4$** ($15,21\text{ kW}$ a $600\text{ km/h}$ con $0\text{ W}$ de apoyo; $16,21\text{ kW}$ con $1.000\text{ W}$; $29,03\text{ kW}$ a $1.000\text{ km/h}$ con $0\text{ W}$; $30,03\text{ kW}$ con $1.000\text{ W}$).
4. **Gobierno por Potencia y Masa Mínima de Pack:** A $t = 60\text{ s}$ y $50\text{ N}$, los 12 casos analizados están gobernados exclusivamente por el límite de **densidad de potencia específica** ($5.000\text{ W/kg}$), pues la masa requerida por potencia ($3,04\text{ a }6,01\text{ kg}$) duplica o triplica la requerida por energía ($1,23\text{ a }2,68\text{ kg}$). Por consiguiente, **la masa mínima de batería resulta rigurosamente idéntica entre $p = 1, 2, 4$ para $t = 60\text{ s}$**.
5. **No Cierre Eléctrico con 50 N:** En todos los 12 casos con $D_{\text{final}} = 50\text{ N}$, el saldo de batería es negativo (déficit entre $-0,84\text{ kg}$ y $-3,80\text{ kg}$ respecto al presupuesto disponible de $2,204\text{ kg}$).
6. **Advertencia Física Fundamental sobre Régimen Transónico:** **Ningún exponente $p$ predice arrastre transónico.** La elevación de orden ($p = 4$) no modela la divergencia de Mach ($M_{dd}$), la aparición de ondas de choque locales, el desprendimiento de capa límite inducido por choque ni el arrastre de onda.

---

## 2. Clasificación Estricta: Datos Medidos, Supuestos y Cálculos

Para preservar la integridad metrológica y documental, se clasifican taxativamente los elementos del modelo:

| Categoría | Elemento | Valor / Descripción | Unidad | Fuente / Justificación |
|:---|:---|:---:|:---:|:---|
| **Datos Medidos** | **Ninguno** | *No existen pesajes reales de prototipo C02 ni ensayos de túnel de viento/vuelo en los datos disponibles.* | — | Las masas de referencia provienen de modelos CAD parciales (hipótesis); no son componentes pesados en báscula calibrada. |
| **Supuestos (Vehículo)** | Masa total C02 | $5,0$ | kg | Supuesto de diseño C02 (no modificado). |
| **Supuestos (CAD Ligero)** | Masa asignada parcial | $2,04584$ | kg | Hipótesis `ligera_1200` en `MASA_INERCIA_PARCIAL.json`. |
| **Supuestos (CAD Ligero)** | Reserva provisional | $0,75$ | kg | Reserva asignada en la hipótesis ligera. |
| **Supuestos (CAD Ligero)** | Masa adicional no id. | $0,0$ | kg | Caso optimista de referencia sin hardware adicional. |
| **Supuestos (Batería)** | Masa disponible para pack | $2,20416$ | kg | Calculada como $5,0 - 2,04584 - 0,75\text{ kg}$. |
| **Supuestos (Batería)** | Densidad de energía útil | $150,0$ | Wh/kg | Supuesto de pack de batería a nivel celda/pack instalado. |
| **Supuestos (Batería)** | Densidad de potencia pico | $5.000,0$ | W/kg | Supuesto de descarga específica admisible. |
| **Supuestos (Misión)** | Tiempo estacionario ($t_{\text{est}}$) | $30,0$ | s | Incluye fase inicial de sustentación pura y maniobra. |
| **Supuestos (Misión)** | Tiempo maniobra ($t_{\text{man}}$) | $3,0$ | s | Maniobra lateral incluida en los 30 s de estacionario. |
| **Supuestos (Misión)** | Potencia estacionario ($P_{\text{est}}$) | $2.968,81$ | W | Valor exploratorio heredado de C01 (no instalado en C02). |
| **Supuestos (Misión)** | Potencia maniobra ($P_{\text{man}}$) | $3.505,89$ | W | Valor exploratorio heredado de C01 (no instalado en C02). |
| **Supuestos (Misión)** | Tiempo crucero ($t_{\text{crucero}}$) | $30,0$ | s | Fase de crucero a velocidad constante $V$. |
| **Supuestos (Misión)** | Eficiencia axial propulsiva ($\eta$) | $0,70$ | — | Supuesto constante para todo el rango de avance. |
| **Supuestos (Misión)** | Tiempo aceleración analizado | $60,0$ | s | Tiempo de aceleración del escenario de referencia. |
| **Supuestos (Escenarios)** | Velocidades objetivo ($V$) | $600,0\text{ y }1.000,0$ | km/h | Escenarios de avance axial ($166,67\text{ y }277,78\text{ m/s}$). |
| **Supuestos (Escenarios)** | Arrastre final ($D_{\text{final}}$) | $50,0$ | N | Fuerza supuesta de arrastre a la velocidad final $V$. |
| **Supuestos (Escenarios)** | Potencia de apoyo ($P_{\text{aux}}$) | $0\text{ y }1.000$ | W | Carga eléctrica adicional en avance (sustentación/servicios). |
| **Supuestos (Leyes)** | Exponentes de arrastre ($p$) | $1, 2, 4$ | — | Modelos paramétricos $D(v) = D_{\text{final}}(v/V)^p$. |
| **Cálculos** | Cinemática rectilínea | $a = V/t, \quad x = \frac{1}{2}Vt$ | $\text{m/s}^2$, m | Cinemática clásica bajo aceleración constante. |
| **Cálculos** | Trabajo arrastre aceleración | $W_{\text{arrastre}} = \frac{D_{\text{final}} V t}{p+2}$ | J | Integral analítica verificada en este trabajo. |
| **Cálculos** | Energía cinética | $E_{\text{cin}} = \frac{1}{2} m V^2$ | J | Teorema de las fuerzas vivas. |
| **Cálculos** | Trabajo arrastre crucero | $W_{\text{crucero}} = D_{\text{final}} V t_{\text{crucero}}$ | J | Trabajo a velocidad y arrastre constantes. |
| **Cálculos** | Energía axial eléctrica | $E_{\text{axial}} = \frac{E_{\text{cin}} + W_{\text{arrastre}} + W_{\text{crucero}}}{3600 \cdot \eta}$ | Wh | Conversión mecánica a eléctrica considerando eficiencia. |
| **Cálculos** | Potencia axial pico | $P_{\text{axial,pico}} = \frac{m V^2/t + D_{\text{final}} V}{\eta}$ | W | Potencia mecánica instantánea máxima en $t$. |
| **Cálculos** | Potencia pico de batería | $P_{\text{pack,pico}} = \max(P_{\text{man}}, P_{\text{axial,pico}} + P_{\text{aux}})$ | W | Mayor demanda eléctrica de la misión. |
| **Cálculos** | Masa de pack requerida | $m_{\text{bat}} = \max\left(\frac{E_{\text{total}}}{150}, \frac{P_{\text{pico}}}{5000}\right)$ | kg | Criterio de dimensionamiento bi-criterio (energía/potencia). |

---

## 3. Deducción y Verificación Analítica de la Integral de Arrastre

### 3.1. Deducción Analítica en el Dominio Temporal ($\tau$)

Consideremos un móvil de masa $m$ que parte del reposo ($v(0) = 0$) y alcanza la velocidad final $V$ en el tiempo $t$ bajo aceleración constante $a = \frac{V}{t}$.
La velocidad instantánea en cualquier instante $\tau \in [0, t]$ es:
$$v(\tau) = a \cdot \tau = V \left( \frac{\tau}{t} \right)$$

La fuerza de arrastre prescrita por la ley de potencias es:
$$D(v(\tau)) = D_{\text{final}} \left( \frac{v(\tau)}{V} \right)^p = D_{\text{final}} \left( \frac{\tau}{t} \right)^p$$

El trabajo mecánico infinitesimal realizado por la fuerza de arrastre en un intervalo $d\tau$ es el producto de la fuerza por el desplazamiento infinitesimal $dx = v(\tau) d\tau$:
$$dW_{\text{arrastre}} = D(v(\tau)) \cdot v(\tau) \, d\tau = D_{\text{final}} \left( \frac{\tau}{t} \right)^p \cdot V \left( \frac{\tau}{t} \right) d\tau = D_{\text{final}} V \left( \frac{\tau}{t} \right)^{p+1} d\tau$$

Integrando desde $\tau = 0$ hasta $\tau = t$:
$$W_{\text{arrastre, acel}} = \int_0^t D_{\text{final}} V \left( \frac{\tau}{t} \right)^{p+1} d\tau = \frac{D_{\text{final}} V}{t^{p+1}} \int_0^t \tau^{p+1} d\tau$$

Evaluando la primitiva:
$$\int_0^t \tau^{p+1} d\tau = \left[ \frac{\tau^{p+2}}{p + 2} \right]_0^t = \frac{t^{p+2}}{p + 2}$$

Sustituyendo:
$$W_{\text{arrastre, acel}} = \frac{D_{\text{final}} V}{t^{p+1}} \cdot \frac{t^{p+2}}{p + 2} = \frac{D_{\text{final}} \cdot V \cdot t}{p + 2} \quad \blacksquare$$

### 3.2. Deducción Equivalente en el Dominio Espacial y de Velocidad ($v$)

Por cinemática bajo aceleración uniforme $a$:
$$v \, dv = a \, dx \implies dx = \frac{v}{a} \, dv = \frac{t}{V} v \, dv$$

El trabajo de arrastre en función de la velocidad es:
$$W_{\text{arrastre, acel}} = \int_0^x D(v) \, dx = \int_0^V D_{\text{final}} \left(\frac{v}{V}\right)^p \left(\frac{t}{V} v\right) dv = \frac{D_{\text{final}} t}{V^{p+1}} \int_0^V v^{p+1} dv$$
$$W_{\text{arrastre, acel}} = \frac{D_{\text{final}} t}{V^{p+1}} \left[ \frac{v^{p+2}}{p + 2} \right]_0^V = \frac{D_{\text{final}} t}{V^{p+1}} \frac{V^{p+2}}{p + 2} = \frac{D_{\text{final}} \cdot V \cdot t}{p + 2} \quad \blacksquare$$

### 3.3. Evaluación para los Exponentes Solicitados ($p = 1, 2, 4$)

- **Caso Lineal ($p = 1$):**
  $$W(p=1) = \frac{D_{\text{final}} V t}{1 + 2} = \frac{D_{\text{final}} V t}{3}$$
- **Caso Cuadrático ($p = 2$, referencia estándar):**
  $$W(p=2) = \frac{D_{\text{final}} V t}{2 + 2} = \frac{D_{\text{final}} V t}{4}$$
- **Caso Cuártico ($p = 4$):**
  $$W(p=4) = \frac{D_{\text{final}} V t}{4 + 2} = \frac{D_{\text{final}} V t}{6}$$

**Razones teóricas exactas:**
$$\frac{W(p=1)}{W(p=2)} = \frac{4}{3} = 1,\overline{33} \quad (+33,33\%)$$
$$\frac{W(p=4)}{W(p=2)} = \frac{4}{6} = \frac{2}{3} = 0,\overline{66} \quad (-33,33\%)$$

### 3.4. Verificación Numérica mediante Cuadratura Compuesta

Se implementó una rutina de cuadratura compuesta de Simpson con $20.000$ intervalos para comprobar la formulación analítica. Los resultados calculados son:

| Velocidad ($V$) | Exponente ($p$) | Trabajo Analítico ($J$) | Trabajo Numérico ($J$) | Error Absoluto ($J$) | Error Relativo |
|:---:|:---:|:---:|:---:|:---:|:---:|
| $600\text{ km/h}$ | $p = 1$ | $166.666,666667$ | $166.666,666667$ | $5,82 \times 10^{-11}$ | $3,49 \times 10^{-16}$ |
| $600\text{ km/h}$ | $p = 2$ | $125.000,000000$ | $125.000,000000$ | $4,37 \times 10^{-11}$ | $3,49 \times 10^{-16}$ |
| $600\text{ km/h}$ | $p = 4$ | $83.333,333333$ | $83.333,333333$ | $1,16 \times 10^{-10}$ | $1,40 \times 10^{-15}$ |
| $1.000\text{ km/h}$ | $p = 1$ | $277.777,777778$ | $277.777,777778$ | $5,82 \times 10^{-11}$ | $2,10 \times 10^{-16}$ |
| $1.000\text{ km/h}$ | $p = 2$ | $208.333,333333$ | $208.333,333333$ | $6,11 \times 10^{-10}$ | $2,93 \times 10^{-15}$ |
| $1.000\text{ km/h}$ | $p = 4$ | $138.888,888889$ | $138.888,888889$ | $2,33 \times 10^{-10}$ | $1,68 \times 10^{-15}$ |

La discrepancia numérica está en el orden del ruido de redondeo de punto flotante de 64 bits ($10^{-16}$ relativo), validando inequívocamente la fórmula cerrada.

---

## 4. Invariancia Analítica de la Potencia Pico

La potencia mecánica propulsiva instantánea durante la aceleración uniforme es:
$$P_{\text{mec}}(\tau) = F_{\text{prop}}(\tau) \cdot v(\tau) = [m \cdot a + D(v(\tau))] \cdot v(\tau) = m \frac{V}{t} v(\tau) + D_{\text{final}} \left(\frac{v(\tau)}{V}\right)^p v(\tau)$$

Dado que $v(\tau) \ge 0$ es monótonamente creciente en $\tau \in [0, t]$ y tanto el término inercial como el término de arrastre son productos de funciones positivas crecientes, el valor máximo de $P_{\text{mec}}(\tau)$ ocurre estrictamente en el instante final $\tau = t$, donde $v(t) = V$:
$$P_{\text{mec, pico}} = m \frac{V}{t} V + D_{\text{final}} \left(\frac{V}{V}\right)^p V = \frac{m V^2}{t} + D_{\text{final}} V$$

Obsérvese que:
$$\left( \frac{V}{V} \right)^p = 1^p = 1, \quad \forall p > 0$$

Por tanto, la potencia mecánica axial pico es **rigurosamente idéntica para cualquier exponente $p$**:
$$P_{\text{axial, pico}} = \frac{1}{\eta} \left( \frac{m V^2}{t} + D_{\text{final}} V \right)$$

En la fase de crucero ($a = 0$), la potencia mecánica es $D_{\text{final}} V$, estrictamente inferior a la potencia al final de la aceleración. Por lo tanto, la potencia pico eléctrica de la batería en avance es:
$$P_{\text{batería, pico}} = \max\left( P_{\text{maniobra}}, P_{\text{axial, pico}} + P_{\text{aux}} \right)$$
la cual es completamente independiente de $p$.

---

## 5. Comparación Sistemática: 12 Casos Centrales

A continuación se presenta la matriz de resultados para los 12 casos evaluados:
- Velocidades: $600\text{ km/h}$ ($166,67\text{ m/s}$) y $1.000\text{ km/h}$ ($277,78\text{ m/s}$)
- Arrastre final: $50,0\text{ N}$
- Tiempo de aceleración: $60,0\text{ s}$
- Potencias de apoyo simultáneo: $0\text{ W}$ y $1.000\text{ W}$
- Exponentes de arrastre: $p \in \{1, 2, 4\}$

### Tabla Comparativa Integral

| $V$ (km/h) | $P_{\text{aux}}$ (W) | $p$ | $W_{\text{arrastre}}$ (kJ) | Var. $W$ vs $p=2$ | $E_{\text{axial}}$ (Wh) | $E_{\text{total}}$ (Wh) | Var. $E$ vs $p=2$ | $P_{\text{pico}}$ (kW) | $m_{\text{bat,E}}$ (kg) | $m_{\text{bat,P}}$ (kg) | $m_{\text{bat,min}}$ (kg) | Limitante | Saldo Ligero (kg) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|---:|
| **600** | **0** | **1** | $166,67$ | $+33,33\text{ \%}$ | $192,90$ | **218,09** | $+8,20\text{ \%}$ | **15,21** | $1,45$ | **3,04** | **3,04** | Potencia | $-0,84$ |
| **600** | **0** | **2** | $125,00$ | *base ($0\text{ \%}$)* | $176,37$ | **201,55** | *base ($0\text{ \%}$)* | **15,21** | $1,34$ | **3,04** | **3,04** | Potencia | $-0,84$ |
| **600** | **0** | **4** | $83,33$ | $-33,33\text{ \%}$ | $159,83$ | **185,02** | $-8,20\text{ \%}$ | **15,21** | $1,23$ | **3,04** | **3,04** | Potencia | $-0,84$ |
| **600** | **1.000** | **1** | $166,67$ | $+33,33\text{ \%}$ | $192,90$ | **243,09** | $+7,30\text{ \%}$ | **16,21** | $1,62$ | **3,24** | **3,24** | Potencia | $-1,04$ |
| **600** | **1.000** | **2** | $125,00$ | *base ($0\text{ \%}$)* | $176,37$ | **226,55** | *base ($0\text{ \%}$)* | **16,21** | $1,51$ | **3,24** | **3,24** | Potencia | $-1,04$ |
| **600** | **1.000** | **4** | $83,33$ | $-33,33\text{ \%}$ | $159,83$ | **210,02** | $-7,30\text{ \%}$ | **16,21** | $1,40$ | **3,24** | **3,24** | Potencia | $-1,04$ |
| **1.000** | **0** | **1** | $277,78$ | $+33,33\text{ \%}$ | $352,12$ | **377,31** | $+7,88\text{ \%}$ | **29,03** | $2,52$ | **5,81** | **5,81** | Potencia | $-3,60$ |
| **1.000** | **0** | **2** | $208,33$ | *base ($0\text{ \%}$)* | $324,56$ | **349,75** | *base ($0\text{ \%}$)* | **29,03** | $2,33$ | **5,81** | **5,81** | Potencia | $-3,60$ |
| **1.000** | **0** | **4** | $138,89$ | $-33,33\text{ \%}$ | $297,01$ | **322,19** | $-7,88\text{ \%}$ | **29,03** | $2,15$ | **5,81** | **5,81** | Potencia | $-3,60$ |
| **1.000** | **1.000** | **1** | $277,78$ | $+33,33\text{ \%}$ | $352,12$ | **402,31** | $+7,35\text{ \%}$ | **30,03** | $2,68$ | **6,01** | **6,01** | Potencia | $-3,80$ |
| **1.000** | **1.000** | **2** | $208,33$ | *base ($0\text{ \%}$)* | $324,56$ | **374,75** | *base ($0\text{ \%}$)* | **30,03** | $2,50$ | **6,01** | **6,01** | Potencia | $-3,80$ |
| **1.000** | **1.000** | **4** | $138,89$ | $-33,33\text{ \%}$ | $297,01$ | **347,19** | $-7,35\text{ \%}$ | **30,03** | $2,31$ | **6,01** | **6,01** | Potencia | $-3,80$ |

*Notas:*
- $E_{\text{estacionario}} = 25,19\text{ Wh}$ en todos los casos ($30\text{ s}$ que incluyen $3\text{ s}$ de maniobra a $3.505,89\text{ W}$ y $27\text{ s}$ a $2.968,81\text{ W}$).
- $E_{\text{apoyo}} = 0\text{ Wh}$ (apoyo $0\text{ W}$) o $25,00\text{ Wh}$ (apoyo $1.000\text{ W}$ durante $60\text{ s acel} + 30\text{ s crucero} = 90\text{ s}$).
- Saldo ligero frente al presupuesto disponible de $2,20416\text{ kg}$.

---

## 6. Análisis Físico y Dimensional del Dimensionamiento

### 6.1. ¿Por qué la Masa Mínima de Batería es Invariante con $p$ a $t = 60\text{ s}$?

La masa requerida de batería responde a una envolvente de dos restricciones independientes:
$$m_{\text{bat, min}} = \max\left( m_{\text{bat, E}}, m_{\text{bat, P}} \right) = \max\left( \frac{E_{\text{total}}}{e_{\text{pack}}}, \frac{P_{\text{pico}}}{p_{\text{pack}}} \right)$$

1. **Masa por Energía ($m_{\text{bat, E}}$):**
   Varía sensiblemente con $p$:
   - A $600\text{ km/h}$ y $0\text{ W}$, pasa de $1,45\text{ kg}$ ($p=1$) a $1,34\text{ kg}$ ($p=2$) y $1,23\text{ kg}$ ($p=4$).
   - A $1.000\text{ km/h}$ y $1.000\text{ W}$, pasa de $2,68\text{ kg}$ ($p=1$) a $2,50\text{ kg}$ ($p=2$) y $2,31\text{ kg}$ ($p=4$).
2. **Masa por Potencia ($m_{\text{bat, P}}$):**
   Es completamente rígida respecto a $p$ porque depende únicamente del punto terminal $v = V$:
   - A $600\text{ km/h}$, $m_{\text{bat, P}} = 3,04\text{ kg}$ ($0\text{ W}$) o $3,24\text{ kg}$ ($1.000\text{ W}$).
   - A $1.000\text{ km/h}$, $m_{\text{bat, P}} = 5,81\text{ kg}$ ($0\text{ W}$) o $6,01\text{ kg}$ ($1.000\text{ W}$).

Dado que $m_{\text{bat, P}} \gg m_{\text{bat, E}}$ en todos los escenarios para $t = 60\text{ s}$, **la restricción activa es la potencia pico**. Al ser la potencia pico invariable con $p$, la masa mínima del pack permanece fija en el valor impuesto por la potencia.

### 6.2. Régimen de Transición y Tiempos de Cruce ($t^*$)

Si se varía el tiempo de aceleración $t$, el requerimiento de potencia disminuye con $\sim 1/t$ mientras que la energía consumida por arrastre y apoyo aumenta linealmente con $t$. Existe un tiempo crítico de cruce $t^*$ en el cual $m_{\text{bat, P}}(t^*) = m_{\text{bat, E}}(t^*)$.

Para tiempos $t > t^*$, la masa de batería pasa a estar dominada por energía, y en ese régimen **la ley de arrastre ($p$) sí altera la masa mínima del vehículo**.

Los tiempos de cruce exactos calculados para $D_{\text{final}} = 50\text{ N}$ son:

| Velocidad ($V$) | Apoyo ($P_{\text{aux}}$) | $t^*(p=1)$ | $t^*(p=2)$ | $t^*(p=4)$ |
|:---:|:---:|:---:|:---:|:---:|
| $600\text{ km/h}$ | $0\text{ W}$ | $211,7\text{ s}$ | $274,4\text{ s}$ | $399,3\text{ s}$ |
| $600\text{ km/h}$ | $1.000\text{ W}$ | $187,4\text{ s}$ | $228,9\text{ s}$ | $297,8\text{ s}$ |
| $1.000\text{ km/h}$ | $0\text{ W}$ | $219,6\text{ s}$ | $280,9\text{ s}$ | $402,0\text{ s}$ |
| $1.000\text{ km/h}$ | $1.000\text{ W}$ | $203,8\text{ s}$ | $251,1\text{ s}$ | $333,8\text{ s}$ |

**Interpretación Física:**
- Todos los tiempos de cruce superan ampliamente los $60\text{ s}$ e incluso el límite de $180\text{ s}$ contemplado en el cribado amplio.
- A mayor $p$, menor es la energía acumulada en aceleración, por lo que el tiempo de cruce $t^*$ se desplaza significativamente hacia tiempos más largos ($p=4$ retrasa el cruce en más de $120\text{ s}$ respecto a $p=2$).

---

## 7. Advertencia Fundamental: Por Qué Ninguna Ley $p$ Predice Arrastre Transónico

> [!WARNING]
> **Declaración explícita:** Ninguna ley de potencias de la forma $D(v) = D_{\text{final}} (v/V)^p$ (con $p = 1, 2, 4$ ni ningún otro exponente constante) modela, predice ni reproduce la física del arrastre aerodinámico transónico.

### 7.1. Naturaleza Física del Régimen Transónico
El régimen transónico (típicamente $0,75 \lesssim M \lesssim 1,2$) no es una extrapolación polinómica del flujo incompresible o subsónico subsónico. Está gobernado por fenómenos ondulatorios y de compresibilidad no lineales:
1. **Número de Mach Crítico ($M_{\text{crit}}$):** Es la velocidad de corriente libre a la cual la velocidad local sobre algún punto del perfil o fuselaje alcanza localmente $M = 1,0$.
2. **Número de Mach de Divergencia de Arrastre ($M_{dd}$):** Definido formalmente como el punto donde $\frac{\partial C_D}{\partial M} = 0,10$. A partir de $M_{dd}$, el coeficiente de arrastre experimenta un abrupto incremento ("drag rise" o subida de arrastre).
3. **Arrastre de Onda (Wave Drag):** Formación de ondas de choque de compresión normales u oblicuas que disipan energía mecánica en forma de saltos de entropía irreversibles a través de la discontinuidad del choque.
4. **Interacción Choque-Capa Límite:** El fuerte gradiente de presión adverso inducido por el choque provoca el desprendimiento prematuro de la capa límite, elevando drásticamente el arrastre de presión y generando inestabilidades aeroelásticas (buffet boundary).

### 7.2. Inadecuación Estructural del Modelo Paramétrico $D(v) = D_{\text{final}} (v/V)^p$
- **Anclaje forzado en $D_{\text{final}}$:** La formulación prescribe $D(V) = D_{\text{final}}$ a priori. Si $V = 1.000\text{ km/h}$ ($M \approx 0,82$ a nivel del mar), la función asume de manera arbitraria que el arrastre a esa velocidad es de $50\text{ N}$, en lugar de calcular si a $M \approx 0,82$ el vehículo ya entró en divergencia de Mach donde el arrastre real podría multiplicarse por factores de 3 a 10.
- **Ausencia de escala de compresibilidad:** La variable $v/V$ es adimensionalizada respecto a la velocidad objetivo, no respecto a la velocidad del sonido local $a = \sqrt{\gamma R T}$. Por lo tanto, no contiene dependencia termodinámica de Mach ($M = v/a$).
- **Comportamiento sub-terminal espurio de $p = 4$:** Elevar la potencia a $p = 4$ concentra la fuerza en las velocidades inmediatamente anteriores a $V$, pero para $v < V$ produce un arrastre **mucho menor** que el arrastre cuadrático real subsónico ($C_D$ subsónico). Esto significa que $p = 4$ subestima el arrastre en la mayor parte de la trayectoria de aceleración, lo cual contradice la física real de un vehículo que experimenta arrastre de fricción y presión subsónica estándar durante el despegue y subida inicial.
- **Geometría y Regla del Área:** El arrastre transónico depende críticamente de la distribución de área transversal a lo largo del eje longitudinal (Regla de las Áreas de Whitcomb), espesor relativo $(t/c)$ y flecha alar. Ninguna de estas dependencias físicas puede capturarse mediante un exponente escalar $p$.

---

## 8. Preservación del Caso de Estudio C02

Se deja constancia explícita de que **no se ha modificado la candidata C02**:
- Se mantiene su masa total nominal de $5,0\text{ kg}$.
- Se conserva su desglose de misión: $30\text{ s}$ estacionario ($27\text{ s}$ a $2.968,81\text{ W} + 3\text{ s}$ a $3.505,89\text{ W}$), aceleración uniforme y $30\text{ s}$ de crucero a velocidad final.
- Se conserva su eficiencia axial constante $\eta = 0,70$.
- Se conservan las hipótesis de densidad de batería de $150\text{ Wh/kg}$ y $5.000\text{ W/kg}$.
- Se conserva el presupuesto ligero de batería de $2,20416\text{ kg}$ derivado del CAD parcial.
- No se han adoptado instrucciones ajenas provenientes de las carpetas de referencia.

---

## 9. Pruebas Automatizadas y Verificación

Se implementó una batería completa de pruebas unitarias estándar bajo `unittest` en [`salidas/test_sensibilidad.py`](file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/energia_ley_arrastre/salidas/test_sensibilidad.py).

### Resumen de Ejecución:
- **Pruebas ejecutadas:** 10 pruebas unitarias.
- **Resultado:** 10 aprobadas (`OK`), 0 fallos, 0 errores.
- **Tiempo de ejecución:** $0,016\text{ s}$.

### Detalle de las Comprobaciones Implementadas:
1. `test_c02_constants_integrity`: Comprueba la integridad de todas las constantes físicas y supuestos de C02 (masa $5,0\text{ kg}$, tiempos, potencias, eficiencias, densidades).
2. `test_analytical_integral_formula`: Verifica la fórmula $D_{\text{final}} V t / (p+2)$ para $p=1, 2, 4$, demostrando los divisores 3, 4 y 6.
3. `test_numerical_vs_analytical_quadrature`: Evalúa la cuadratura numérica de Simpson contra la solución analítica en 7 configuraciones distintas, exigiendo error relativo $< 10^{-9}$.
4. `test_drag_work_theoretical_ratios`: Comprueba las razones exactas $4/3$ y $2/3$ entre los trabajos mecánicos de arrastre.
5. `test_reproduction_of_reference_cases_p2`: Valida la reproducción exacta de los 6 casos de $50\text{ N}$ reportados en la tabla del informe de referencia (`INFORME.md`).
6. `test_peak_power_invariance_with_p`: Demuestra formalmente la invariancia estricta de la potencia pico axial y de batería frente a variaciones de $p$.
7. `test_energy_sensitivity_across_p`: Comprueba la monotonía decreciente estricta de la energía total y de la masa por energía respecto a $p$.
8. `test_active_constraint_at_60s`: Valida que en los 12 casos analizados a $t = 60\text{ s}$, la potencia sea el limitante activo y la masa mínima de batería sea idéntica.
9. `test_crossover_behavior`: Comprueba la existencia y monotonía de los tiempos de cruce $t^*(p)$ hacia el régimen gobernado por energía.
10. `test_input_validation`: Valida el rechazo robusto de entradas no físicas (velocidades negativas, arrastres negativos, tiempos nulos, exponentes no positivos).

---

## 10. Trazabilidad de Archivos y Fuentes Criptográficas

Para garantizar reproducibilidad absoluta y control de versiones, se registran las huellas SHA-256 de todas las fuentes y entregables:

### Archivos de Entrada (Solo Lectura):
- `entradas/.../potencia_simultanea_c02/INFORME.md`  
  SHA-256: `d7b724afd7b48b7058a1d1969afa4b869f14629d709d72e30f3170f03ee1627a`
- `entradas/.../potencia_simultanea_c02/calcular_r2.py`  
  SHA-256: `73d70339ce0ce124d239c22a4cde8282b85f77becb0d163c138301066cd3b67a`

### Archivos Generados en `salidas/`:
- `salidas/sensibilidad_ley_arrastre.py`: Módulo principal de cálculo paramétrico y exportación de datos.
- `salidas/test_sensibilidad.py`: Suite de 10 pruebas unitarias automatizadas.
- `salidas/tabla_comparacion_casos.csv`: Tabla con los 12 casos centrales comparativos solicitados.
- `salidas/tabla_sensibilidad_completa.csv`: Matriz extendida con 90 escenarios paramétricos ($t \in [10, 180]\text{ s}$ y apoyos adicionales).
- `salidas/resultados_sensibilidad.json`: Resumen estructurado en formato JSON con metadatos, verificación de cuadratura y tiempos de cruce.
- `salidas/REPORTE_SENSIBILIDAD_ARRASTRE.md`: Este documento técnico integral.

---

## 11. Limitaciones Explícitas del Análisis

1. **Modelo de Arrastre Paramétrico Puro:** La prescripción $D(v) = D_{\text{final}} (v/V)^p$ es una aproximación cinemática unidimensional. No proviene de un campo de presiones CFD resuelto por Navier-Stokes ni de ensayos en túnel aerodinámico.
2. **Eficiencia Axial Plana a Velocidad Cero:** Asumir $\eta = 0,70$ constante hasta $v = 0$ asigna una potencia propulsiva mecánica nula en reposo ($P = F \cdot v = 0$). Un propulsor aéreo real que genera empuje estático absorbe potencia mecánica y eléctrica significativa a velocidad cero ($v = 0$).
3. **Ausencia de Dinámica de Transición y Trimado:** No se modela la sustentación vertical acoplada, el ángulo de ataque, el trimado longitudinal, el desprendimiento del flujo en los conductos ni la interferencia entre la sustentación y el chorro axial.
4. **Potencia de Apoyo Desacoplada:** El término $P_{\text{aux}}$ es una carga eléctrica constante hipotética superpuesta, no un mapa real de potencia del ventilador de sustentación en función de la velocidad de avance.
5. **Comportamiento Electroquímico Simplificado:** Las densidades de $150\text{ Wh/kg}$ y $5.000\text{ W/kg}$ suponen una batería ideal sin caídas de tensión por resistencia interna, sin variación por estado de carga (SoC), sin límites de corriente de descarga continua vs ráfaga (C-rate) y sin balance térmico ni degradación.
6. **Presupuesto de Masa no Verificado:** La masa ligera disponible ($2,20416\text{ kg}$) se basa en un inventario geométrico CAD parcial con 54 piezas no identificadas. No representa una cota inferior demostrada ni garantiza la inclusión de arneses, conectores, actuadores, aviónica o soporte estructural completo.
7. **No Extrapolación a Otras Variantes:** Los resultados son exclusivos para el vehículo conceptual C02 de 5,0 kg y no son directamente escalables ni trasladables a vehículos de 2 kg o 10 kg sin sus propios presupuestos geométricos y mapas propulsivos independientes.
