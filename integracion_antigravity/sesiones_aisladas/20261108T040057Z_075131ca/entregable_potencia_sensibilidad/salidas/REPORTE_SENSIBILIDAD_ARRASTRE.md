# Sensibilidad del Trabajo de Aceleración y Dimensionamiento de Batería para C02 (5,0 kg)

**Fecha:** Noviembre de 2026  
**Contexto:** Evaluación aerotécnica y energética independiente sobre la candidata C02 de 5,0 kg  
**Paquete:** Entorno autónomo y reproducible en `salidas/` (sin rutas temporales absolutas)  

---

## 1. Resumen Ejecutivo

Este documento presenta el estudio de sensibilidad paramétrica del trabajo mecánico propulsivo y la demanda energética eléctrica durante la fase de aceleración rectilínea uniforme para la candidata **C02 (5,0 kg)**, bajo la familia de leyes de arrastre:

$$D(v) = D_{\text{final}} \left( \frac{v}{V} \right)^p, \quad p \in \{1, 2, 4\}$$

El estudio mantiene de forma rigurosa los supuestos de misión, masa, tiempos, eficiencias y densidades de pack del informe de referencia (`G1/potencia_simultanea_c02`), cotejando el caso cuadrático ($p = 2$) contra dicho modelo de referencia.

### Hallazgos Principales:

1. **Deducción y Verificación Exacta de la Integral:**  
   Se demuestra analíticamente que el trabajo mecánico realizado contra el arrastre aerodinámico durante una aceleración constante desde el reposo hasta la velocidad $V$ en un tiempo $t$ es exactamente:
   $$W_{\text{arrastre, acel}} = \frac{D_{\text{final}} \cdot V \cdot t}{p + 2}$$
   La cuadratura numérica de Simpson converge a la expresión analítica con un error relativo inferior a $10^{-14}$ (en el orden del ruido de punto flotante de 64 bits).

2. **Sensibilidad del Trabajo Mecánico vs. Caso Base ($p = 2$):**  
   - Para $p = 1$ (arrastre proporcional a la velocidad): $W = \frac{D V t}{3}$, lo que representa un aumento exacto de $+33,33\%$ respecto a $p = 2$.
   - Para $p = 2$ (arrastre cuadrático clásico): $W = \frac{D V t}{4}$ (caso base de referencia).
   - Para $p = 4$ (arrastre fuertemente no lineal): $W = \frac{D V t}{6}$, lo que representa una reducción exacta de $-33,33\%$ respecto a $p = 2$.

3. **Cotejo Riguroso contra el Modelo $r2$:**  
   Para $p = 2$, todos los resultados (potencia axial de pico, potencia de batería, energías parciales y totales, masa de batería y saldo de masa) coinciden con machine precision con `calcular_r2.py` e `INFORME.md`.

4. **Distinción entre Potencia de Pico Simultánea y Energía por Etapa:**  
   - La **potencia de pico axial simultánea** es una tasa instantánea de transferencia ($W$) que ocurre al final de la aceleración ($v = V$). Dado que $(V/V)^p = 1$ para cualquier $p > 0$, la potencia de pico axial es **estrictamente invariante con $p$**. Con apoyo simultáneo $P_{\text{aux}}$, la demanda eléctrica de pico es $(m V^2/t + D_{\text{final}} V)/\eta + P_{\text{aux}}$.
   - La **energía por etapa** es una integral en el tiempo ($Wh$). Se desglosa en:
     - Etapa 1 (Estacionario + Maniobra): $25,19\text{ Wh}$ (constante en todos los casos).
     - Etapa 2 (Aceleración): trabajo cinético ($\frac{1}{2} m V^2 / \eta$) + trabajo de arrastre ($W_{\text{arrastre}} / \eta$) + apoyo ($P_{\text{aux}} t / 3600$).
     - Etapa 3 (Crucero): trabajo de arrastre ($D_{\text{final}} V t_{\text{crucero}} / \eta$) + apoyo ($P_{\text{aux}} t_{\text{crucero}} / 3600$).

5. **Auditoría Anti-Duplicación de la Energía de Aceleración:**  
   Se comprueba formal y numéricamente que la energía de aceleración **no se cuenta dos veces**:
   - La energía cinética $\frac{1}{2} m V^2$ se incluye exactamente una sola vez (en la etapa de aceleración). En crucero la velocidad es constante ($a = 0$), por lo que no hay término inercial.
   - El arrastre durante aceleración se integra únicamente en $[0, t]$ y el crucero en $[t, t + t_{\text{crucero}}]$, sin solapamiento de intervalos temporales ni de trayectorias.
   - La potencia de pico simultánea no se multiplica por el tiempo de aceleración para sumarla al balance energético; su único rol es determinar la restricción de potencia de la batería ($m_{\text{bat, P}} = P_{\text{pico}} / 5000\text{ W/kg}$).

6. **Invariancia de la Masa Mínima de Batería a $t = 60\text{ s}$:**  
   Para $D_{\text{final}} = 50\text{ N}$ y $t = 60\text{ s}$, la batería está gobernada en un 100% por la restricción de densidad de potencia específica ($5.000\text{ W/kg}$). Como la potencia pico es idéntica para $p = 1, 2, 4$, **la masa mínima de batería resulta rigurosamente invariable entre los tres exponentes**.

7. **Advertencias Físicas Críticas:**  
   - **Limitación en $v = 0$:** La eficiencia axial constante ($\eta = 0,70$) asigna potencia mecánica cero en reposo ($P = F \cdot v = 0$), lo cual es físicamente inválido para propulsores aéreos reales (rotores, hélices o fans) que requieren potencia estática significativa para generar empuje.
   - **Limitación Transónica ($M \approx 0,75 - 1,2$):** Ninguna ley de potencias simple $(v/V)^p$ predice ni aproxima el arrastre transónico. No reproduce la divergencia de Mach ($M_{dd}$), las ondas de choque, el arrastre de onda ni el desprendimiento de capa límite inducido por choque.
   - **No Extrapolación:** Estos resultados son exploratorios para el modelo paramétrico de C02 (5,0 kg) y no deben extrapolarse al rendimiento de vuelo del vehículo ni a variantes físicas de 2 kg o 10 kg.

---

## 2. Clasificación Estricta de Datos, Supuestos y Cálculos

Siguiendo los principios de integridad técnica y metrológica, se categorizan exhaustivamente todos los parámetros:

| Categoría | Elemento | Valor / Expresión | Unidad | Fuente / Justificación |
|:---|:---|:---:|:---:|:---|
| **Datos Medidos** | **Ninguno** | — | — | No existen mediciones de vuelo ni ensayos de banco o túnel para C02. |
| **Supuestos (Vehículo)** | Masa nominal total ($m$) | $5,0$ | kg | Parámetro de diseño de la candidata C02. |
| **Supuestos (CAD Parcial)** | Masa asignada identificada | $2,04584$ | kg | Hipótesis `ligera_1200` en modelo CAD parcial. |
| **Supuestos (CAD Parcial)** | Reserva provisional | $0,75$ | kg | Margen provisional asignado en la hipótesis ligera. |
| **Supuestos (CAD Parcial)** | Hardware adicional no ident. | $0,0$ | kg | Caso optimista de referencia sin masa adicional. |
| **Supuestos (Batería)** | Masa disponible para pack | $2,20416$ | kg | Calculada como $5,0 - 2,04584 - 0,75\text{ kg}$. |
| **Supuestos (Batería)** | Densidad de energía útil | $150,0$ | Wh/kg | Supuesto de pack de celda/batería instalada. |
| **Supuestos (Batería)** | Densidad de potencia pico | $5.000,0$ | W/kg | Límite admisible de descarga de pico del pack. |
| **Supuestos (Misión)** | Tiempo estacionario ($t_{\text{est}}$) | $30,0$ | s | Incluye sustentación y maniobra inicial. |
| **Supuestos (Misión)** | Tiempo de maniobra ($t_{\text{man}}$) | $3,0$ | s | Maniobra lateral incluida en el estacionario. |
| **Supuestos (Misión)** | Potencia estacionario ($P_{\text{est}}$) | $2.968,81$ | W | Valor exploratorio heredado de C01. |
| **Supuestos (Misión)** | Potencia de maniobra ($P_{\text{man}}$) | $3.505,89$ | W | Valor exploratorio heredado de C01. |
| **Supuestos (Misión)** | Tiempo de crucero ($t_{\text{crucero}}$) | $30,0$ | s | Crucero horizontal a velocidad final $V$. |
| **Supuestos (Misión)** | Eficiencia axial propulsiva ($\eta$) | $0,70$ | — | Supuesta constante en todo el avance axial. |
| **Supuestos (Misión)** | Tiempo de aceleración base ($t$) | $60,0$ | s | Tiempo de aceleración rectilínea uniforme. |
| **Supuestos (Escenarios)** | Velocidades objetivo ($V$) | $600,0\text{ y }1.000,0$ | km/h | $166,67\text{ m/s}$ y $277,78\text{ m/s}$. |
| **Supuestos (Escenarios)** | Arrastre final ($D_{\text{final}}$) | $50,0$ (y $0, 10, 25$) | N | Fuerza supuesta de arrastre a la velocidad $V$. |
| **Supuestos (Escenarios)** | Potencia de apoyo ($P_{\text{aux}}$) | $0, 1.000, 2.968,81$ | W | Carga eléctrica simultánea supuesta en avance. |
| **Supuestos (Leyes)** | Exponentes de arrastre ($p$) | $1, 2, 4$ | — | Modelos paramétricos $D(v) = D_{\text{final}}(v/V)^p$. |
| **Cálculos** | Cinemática rectilínea | $a = V/t, \; x = \frac{1}{2}Vt$ | $\text{m/s}^2$, m | Cinemática clásica bajo aceleración constante. |
| **Cálculos** | Trabajo de arrastre acel. | $W = \frac{D_{\text{final}} V t}{p+2}$ | J | Integral exacta demostrada analíticamente. |
| **Cálculos** | Energía cinética | $E_k = \frac{1}{2} m V^2$ | J | Trabajo contra la inercia del vehículo. |
| **Cálculos** | Trabajo de arrastre crucero | $W_{\text{crucero}} = D_{\text{final}} V t_{\text{crucero}}$ | J | Trabajo mecánico en fase de velocidad constante. |
| **Cálculos** | Potencia axial pico | $P_{\text{axial,pico}} = \frac{m V^2/t + D_{\text{final}} V}{\eta}$ | W | Potencia eléctrica axial en el instante terminal $t$. |
| **Cálculos** | Potencia pico de batería | $P_{\text{pack,pico}} = \max(P_{\text{man}}, P_{\text{axial,pico}} + P_{\text{aux}})$ | W | Demanda eléctrica máxima simultánea de la misión. |
| **Cálculos** | Masa requerida por batería | $m_{\text{bat}} = \max\left(\frac{E_{\text{total}}}{150}, \frac{P_{\text{pico}}}{5000}\right)$ | kg | Envolvente bi-criterio de potencia y energía. |

---

## 3. Deducción y Verificación Exacta de la Integral $W = \frac{D_{\text{final}} V t}{p + 2}$

### 3.1. Deducción Analítica en el Dominio Temporal ($\tau$)

Bajo aceleración rectilínea constante $a = \frac{V}{t}$, la velocidad instantánea desde el reposo ($v(0) = 0$) en cualquier instante $\tau \in [0, t]$ es:
$$v(\tau) = a \cdot \tau = V \left( \frac{\tau}{t} \right)$$

La fuerza de arrastre instantánea según la ley de potencias es:
$$D(v(\tau)) = D_{\text{final}} \left( \frac{v(\tau)}{V} \right)^p = D_{\text{final}} \left( \frac{\tau}{t} \right)^p$$

El diferencial de trabajo mecánico realizado por el propulsor contra el arrastre en el intervalo $d\tau$ es:
$$dW = D(v(\tau)) \cdot v(\tau) \, d\tau = D_{\text{final}} \left( \frac{\tau}{t} \right)^p \cdot V \left( \frac{\tau}{t} \right) d\tau = D_{\text{final}} V \left( \frac{\tau}{t} \right)^{p+1} d\tau$$

Integrando entre $\tau = 0$ y $\tau = t$:
$$W_{\text{arrastre, acel}} = \int_0^t D_{\text{final}} V \left( \frac{\tau}{t} \right)^{p+1} d\tau = \frac{D_{\text{final}} V}{t^{p+1}} \int_0^t \tau^{p+1} d\tau$$

Evaluando la integral definida:
$$\int_0^t \tau^{p+1} d\tau = \left[ \frac{\tau^{p+2}}{p + 2} \right]_0^t = \frac{t^{p+2}}{p + 2}$$

Sustituyendo:
$$W_{\text{arrastre, acel}} = \frac{D_{\text{final}} V}{t^{p+1}} \cdot \frac{t^{p+2}}{p + 2} = \frac{D_{\text{final}} \cdot V \cdot t}{p + 2} \quad \blacksquare$$

### 3.2. Deducción Equivalente en el Dominio de Velocidad ($v$)

Por la regla de la cadena cinemática:
$$v \, dv = a \, dx \implies dx = \frac{v}{a} \, dv = \frac{t}{V} v \, dv$$

Integrando en el espacio de velocidades desde $v = 0$ hasta $v = V$:
$$W_{\text{arrastre, acel}} = \int_0^x D(v) \, dx = \int_0^V D_{\text{final}} \left(\frac{v}{V}\right)^p \left(\frac{t}{V} v\right) dv = \frac{D_{\text{final}} t}{V^{p+1}} \int_0^V v^{p+1} dv$$
$$W_{\text{arrastre, acel}} = \frac{D_{\text{final}} t}{V^{p+1}} \left[ \frac{v^{p+2}}{p + 2} \right]_0^V = \frac{D_{\text{final}} \cdot V \cdot t}{p + 2} \quad \blacksquare$$

### 3.3. Evaluación para los Exponentes Solicitados ($p = 1, 2, 4$)

- Para $p = 1$: $W(1) = \frac{D_{\text{final}} V t}{1 + 2} = \frac{D_{\text{final}} V t}{3}$
- Para $p = 2$: $W(2) = \frac{D_{\text{final}} V t}{2 + 2} = \frac{D_{\text{final}} V t}{4}$
- Para $p = 4$: $W(4) = \frac{D_{\text{final}} V t}{4 + 2} = \frac{D_{\text{final}} V t}{6}$

**Razones Teóricas Exactas:**
$$\frac{W(p=1)}{W(p=2)} = \frac{4}{3} = 1,\overline{33} \quad (+33,33\%)$$
$$\frac{W(p=4)}{W(p=2)} = \frac{4}{6} = \frac{2}{3} = 0,\overline{66} \quad (-33,33\%)$$

### 3.4. Verificación Numérica por Regla de Simpson Compuesta ($N = 20.000$)

| $V$ (km/h) | $p$ | $W$ Analítico (J) | $W$ Simpson (J) | Error Absoluto (J) | Error Relativo |
|:---:|:---:|---:|---:|---:|---:|
| $600$ | $1$ | $166.666,666667$ | $166.666,666667$ | $5,82 \times 10^{-11}$ | $3,49 \times 10^{-16}$ |
| $600$ | $2$ | $125.000,000000$ | $125.000,000000$ | $4,37 \times 10^{-11}$ | $3,49 \times 10^{-16}$ |
| $600$ | $4$ | $83.333,333333$ | $83.333,333333$ | $1,16 \times 10^{-10}$ | $1,40 \times 10^{-15}$ |
| $1.000$ | $1$ | $277.777,777778$ | $277.777,777778$ | $5,82 \times 10^{-11}$ | $2,10 \times 10^{-16}$ |
| $1.000$ | $2$ | $208.333,333333$ | $208.333,333333$ | $6,11 \times 10^{-10}$ | $2,93 \times 10^{-15}$ |
| $1.000$ | $4$ | $138.888,888889$ | $138.888,888889$ | $2,33 \times 10^{-10}$ | $1,68 \times 10^{-15}$ |

El error relativo es de orden $10^{-16}$, confirmando de forma irrefutable la exactitud de la solución analítica cerrada.

---

## 4. Cotejo Riguroso contra el Modelo $r2$ de Referencia

Se comparó la función `evaluate_mission` con $p = 2$ frente a la rutina `evaluate` de `calcular_r2.py` para idénticos valores de entrada. La tabla siguiente resume la verificación para los casos canónicos del informe de referencia ($D_{\text{final}} = 50\text{ N}$, $t = 60\text{ s}$):

| Caso ($V$, $P_{\text{aux}}$) | Métrica | Valor Modelo $r2$ Entrada | Valor Implementado ($p=2$) | Diferencia Absoluta |
|:---|:---|:---:|:---:|:---:|
| **600 km/h, 0 W** | $P_{\text{pico}}$ (kW) | $15,2116$ | $15,2116$ | $< 10^{-12}$ |
| | $E_{\text{total}}$ (Wh) | $201,5545$ | $201,5545$ | $< 10^{-12}$ |
| | $m_{\text{bat,min}}$ (kg) | $3,0423$ | $3,0423$ | $< 10^{-12}$ |
| | Saldo (kg) | $-0,8382$ | $-0,8382$ | $< 10^{-12}$ |
| **600 km/h, 1.000 W** | $P_{\text{pico}}$ (kW) | $16,2116$ | $16,2116$ | $< 10^{-12}$ |
| | $E_{\text{total}}$ (Wh) | $226,5545$ | $226,5545$ | $< 10^{-12}$ |
| | $m_{\text{bat,min}}$ (kg) | $3,2423$ | $3,2423$ | $< 10^{-12}$ |
| | Saldo (kg) | $-1,0382$ | $-1,0382$ | $< 10^{-12}$ |
| **600 km/h, 2.968,81 W** | $P_{\text{pico}}$ (kW) | $18,1804$ | $18,1804$ | $< 10^{-12}$ |
| | $E_{\text{total}}$ (Wh) | $275,7747$ | $275,7747$ | $< 10^{-12}$ |
| | $m_{\text{bat,min}}$ (kg) | $3,6361$ | $3,6361$ | $< 10^{-12}$ |
| | Saldo (kg) | $-1,4319$ | $-1,4319$ | $< 10^{-12}$ |
| **1.000 km/h, 0 W** | $P_{\text{pico}}$ (kW) | $29,0270$ | $29,0270$ | $< 10^{-12}$ |
| | $E_{\text{total}}$ (Wh) | $349,7516$ | $349,7516$ | $< 10^{-12}$ |
| | $m_{\text{bat,min}}$ (kg) | $5,8054$ | $5,8054$ | $< 10^{-12}$ |
| | Saldo (kg) | $-3,6012$ | $-3,6012$ | $< 10^{-12}$ |
| **1.000 km/h, 1.000 W** | $P_{\text{pico}}$ (kW) | $30,0270$ | $30,0270$ | $< 10^{-12}$ |
| | $E_{\text{total}}$ (Wh) | $374,7516$ | $374,7516$ | $< 10^{-12}$ |
| | $m_{\text{bat,min}}$ (kg) | $6,0054$ | $6,0054$ | $< 10^{-12}$ |
| | Saldo (kg) | $-3,8012$ | $-3,8012$ | $< 10^{-12}$ |
| **1.000 km/h, 2.968,81 W** | $P_{\text{pico}}$ (kW) | $31,9958$ | $31,9958$ | $< 10^{-12}$ |
| | $E_{\text{total}}$ (Wh) | $423,9718$ | $423,9718$ | $< 10^{-12}$ |
| | $m_{\text{bat,min}}$ (kg) | $6,3992$ | $6,3992$ | $< 10^{-12}$ |
| | Saldo (kg) | $-4,1950$ | $-4,1950$ | $< 10^{-12}$ |

Todas las pruebas automatizadas de cotejo (`test_cotejo_exacto_modelo_r2` y `test_reproduction_of_reference_cases_p2`) pasaron al 100% sin desviación alguna.

---

## 5. Potencia de Pico Simultánea vs. Energía por Etapa y Auditoría Anti-Duplicación

### 5.1. Naturaleza Física de la Potencia de Pico Simultánea
La potencia mecánica axial instantánea exigida al propulsor en cualquier instante $\tau \in [0, t]$ es el producto de la fuerza total propulsiva por la velocidad:
$$P_{\text{mec}}(\tau) = [F_{\text{inercial}} + D(v(\tau))] \cdot v(\tau) = \left( m \frac{V}{t} + D_{\text{final}} \left(\frac{\tau}{t}\right)^p \right) \cdot V \left(\frac{\tau}{t}\right)$$

Dado que la aceleración es positiva y constante, $v(\tau)$ es monótonamente creciente en $[0, t]$, alcanzando su máximo absoluto en $\tau = t$ ($v = V$):
$$P_{\text{mec, pico}} = \left( m \frac{V}{t} + D_{\text{final}} \left(\frac{V}{V}\right)^p \right) V = m \frac{V^2}{t} + D_{\text{final}} V$$

Obsérvese el resultado algebraico fundamental:
$$\left( \frac{V}{V} \right)^p = 1^p = 1, \quad \forall p > 0$$

Por consiguiente, **la potencia axial de pico mecánica y eléctrica es estrictamente independiente de $p$**:
$$P_{\text{axial, pico}} = \frac{1}{\eta} \left( \frac{m V^2}{t} + D_{\text{final}} V \right)$$

Al sumarle la carga constante simultánea $P_{\text{aux}}$, la demanda eléctrica instantánea de avance en $\tau = t$ es:
$$P_{\text{avance, pico}} = P_{\text{axial, pico}} + P_{\text{aux}}$$
Y la potencia máxima del pack a lo largo de toda la misión es:
$$P_{\text{pack, pico}} = \max\left( P_{\text{maniobra}}, P_{\text{avance, pico}} \right)$$

### 5.2. Desglose Riguroso de Energía por Etapa
La energía consumida es la integral en el tiempo de la potencia instantánea dividida entre las tres etapas disjuntas:

1. **Etapa 1: Estacionario + Maniobra ($30\text{ s}$):**
   $$E_{\text{etapa, 1}} = \frac{P_{\text{est}} \cdot (30 - 3) + P_{\text{man}} \cdot 3}{3600} = 25,1876\text{ Wh}$$
2. **Etapa 2: Aceleración ($t\text{ s}$):**
   $$E_{\text{etapa, 2}} = \frac{\frac{1}{2} m V^2 + \frac{D_{\text{final}} V t}{p + 2}}{3600 \cdot \eta} + \frac{P_{\text{aux}} \cdot t}{3600} \quad \text{[Wh]}$$
3. **Etapa 3: Crucero ($30\text{ s}$ a velocidad $V$ constante):**
   $$E_{\text{etapa, 3}} = \frac{D_{\text{final}} V \cdot 30}{3600 \cdot \eta} + \frac{P_{\text{aux}} \cdot 30}{3600} \quad \text{[Wh]}$$

Balance de energía total:
$$E_{\text{total}} = E_{\text{etapa, 1}} + E_{\text{etapa, 2}} + E_{\text{etapa, 3}}$$

### 5.3. Auditoría Formal Anti-Duplicación de la Energía de Aceleración

Se examinaron tres posibles fuentes de doble conteo típicas en análisis propulsivos preliminares:

1. **¿Se cuenta dos veces la energía cinética?**  
   *No.* La energía cinética $\frac{1}{2} m V^2$ representa el trabajo neto necesario para acelerar la masa $m$ desde el reposo hasta $V$. En la etapa de aceleración, $\int_0^t (m a) v(\tau) d\tau = \frac{1}{2} m V^2$. En la etapa de crucero, la velocidad es constante ($a = 0$), de modo que la variación de energía cinética es idénticamente nula ($\Delta E_k = 0$). No se añade ningún término inercial en crucero ni en el balance global.

2. **¿Se solapan los trabajos de arrastre de aceleración y crucero?**  
   *No.* El trabajo de arrastre en aceleración es la integral en el intervalo temporal cerrado $[0, t]$:
   $$\int_0^t D(v(\tau)) v(\tau) d\tau = \frac{D_{\text{final}} V t}{p + 2}$$
   El trabajo de arrastre en crucero es la integral en el intervalo disjunto $[t, t + 30]$:
   $$\int_t^{t+30} D_{\text{final}} V d\tau = D_{\text{final}} V \cdot 30$$
   No hay doble contabilización de distancia recorrida ni de fuerza disipada.

3. **¿Se confunde la potencia de pico con la energía media?**  
   *No.* La potencia axial de pico $P_{\text{axial, pico}} = (m V^2/t + D_{\text{final}} V)/\eta$ **no** se multiplica por el tiempo $t$ para calcular energía. Si se multiplicara incorrectamente, se obtendría una energía mecánica espuria de $(m V^2 + D_{\text{final}} V t)$, lo que sobreestimaría la energía cinética en un factor de $2,0$ y el arrastre en un factor de $(p + 2)$. El código conserva estrictamente la separación conceptual: la potencia pico dimensiona la masa por potencia ($P / 5.000$) y las integrales de trabajo dimensionan la masa por energía ($E / 150$).

---

## 6. Comparación Sistemática: 12 Casos Centrales

Resultados de la matriz canónica ($D_{\text{final}} = 50\text{ N}$, $t = 60\text{ s}$):

| $V$ (km/h) | $P_{\text{aux}}$ (W) | $p$ | $W_{\text{arrastre,acel}}$ (kJ) | Var. $W$ vs $p=2$ | $E_{\text{total}}$ (Wh) | Var. $E$ vs $p=2$ | $P_{\text{pack,pico}}$ (kW) | $m_{\text{bat,E}}$ (kg) | $m_{\text{bat,P}}$ (kg) | $m_{\text{bat,min}}$ (kg) | Restricción Activa | Saldo Ligero (kg) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|---:|
| **600** | **0** | **1** | $166,67$ | $+33,33\%$ | **218,09** | $+8,20\%$ | **15,21** | $1,45$ | **3,04** | **3,04** | Potencia | $-0,84$ |
| **600** | **0** | **2** | $125,00$ | *base* | **201,55** | *base* | **15,21** | $1,34$ | **3,04** | **3,04** | Potencia | $-0,84$ |
| **600** | **0** | **4** | $83,33$ | $-33,33\%$ | **185,02** | $-8,20\%$ | **15,21** | $1,23$ | **3,04** | **3,04** | Potencia | $-0,84$ |
| **600** | **1.000** | **1** | $166,67$ | $+33,33\%$ | **243,09** | $+7,30\%$ | **16,21** | $1,62$ | **3,24** | **3,24** | Potencia | $-1,04$ |
| **600** | **1.000** | **2** | $125,00$ | *base* | **226,55** | *base* | **16,21** | $1,51$ | **3,24** | **3,24** | Potencia | $-1,04$ |
| **600** | **1.000** | **4** | $83,33$ | $-33,33\%$ | **210,02** | $-7,30\%$ | **16,21** | $1,40$ | **3,24** | **3,24** | Potencia | $-1,04$ |
| **1.000** | **0** | **1** | $277,78$ | $+33,33\%$ | **377,31** | $+7,88\%$ | **29,03** | $2,52$ | **5,81** | **5,81** | Potencia | $-3,60$ |
| **1.000** | **0** | **2** | $208,33$ | *base* | **349,75** | *base* | **29,03** | $2,33$ | **5,81** | **5,81** | Potencia | $-3,60$ |
| **1.000** | **0** | **4** | $138,89$ | $-33,33\%$ | **322,19** | $-7,88\%$ | **29,03** | $2,15$ | **5,81** | **5,81** | Potencia | $-3,60$ |
| **1.000** | **1.000** | **1** | $277,78$ | $+33,33\%$ | **402,31** | $+7,35\%$ | **30,03** | $2,68$ | **6,01** | **6,01** | Potencia | $-3,80$ |
| **1.000** | **1.000** | **2** | $208,33$ | *base* | **374,75** | *base* | **30,03** | $2,50$ | **6,01** | **6,01** | Potencia | $-3,80$ |
| **1.000** | **1.000** | **4** | $138,89$ | $-33,33\%$ | **347,19** | $-7,35\%$ | **30,03** | $2,31$ | **6,01** | **6,01** | Potencia | $-3,80$ |

*Notas:*
- Saldo ligero calculado frente al presupuesto disponible de $2,20416\text{ kg}$.
- En todos los 12 casos el saldo es negativo (entre $-0,84\text{ kg}$ y $-3,80\text{ kg}$), indicando que bajo estas hipótesis y $50\text{ N}$ de arrastre el balance de masas no cierra.

---

## 7. Análisis Físico: ¿Por Qué la Masa Mínima es Invariante con $p$ a $t = 60\text{ s}$?

La masa mínima requerida del pack de baterías es la envolvente superior de dos requerimientos independientes:
$$m_{\text{bat, min}} = \max\left( m_{\text{bat, E}}, m_{\text{bat, P}} \right) = \max\left( \frac{E_{\text{total}}}{150\text{ Wh/kg}}, \frac{P_{\text{pack, pico}}}{5.000\text{ W/kg}} \right)$$

1. **Sensibilidad de la Masa por Energía ($m_{\text{bat, E}}$):**  
   Al variar $p$, la energía total cambia (entre $\pm 7,3\%$ y $\pm 8,2\%$). Por ejemplo, a $600\text{ km/h}$ y $0\text{ W}$:
   - $p = 1 \implies m_{\text{bat, E}} = 1,45\text{ kg}$
   - $p = 2 \implies m_{\text{bat, E}} = 1,34\text{ kg}$
   - $p = 4 \implies m_{\text{bat, E}} = 1,23\text{ kg}$

2. **Rigidez de la Masa por Potencia ($m_{\text{bat, P}}$):**  
   La masa impuesta por potencia es estrictamente constante porque depende de $P_{\text{pack, pico}}$, que es invariante con $p$:
   - A $600\text{ km/h}$ y $0\text{ W} \implies m_{\text{bat, P}} = \frac{15.211,64\text{ W}}{5.000\text{ W/kg}} = 3,0423\text{ kg}$

Como $3,0423\text{ kg} \gg 1,45\text{ kg}$, la potencia pico es la **restricción activa dominante**. Dado que el cuello de botella es la potencia y esta no depende de $p$, la masa mínima exigida al pack permanece idéntica en $3,04\text{ kg}$ para los tres valores de $p$.

### Tiempos de Cruce ($t^*$) hacia el Régimen Dominado por Energía

Para aceleraciones prolongadas ($t \to \infty$), la potencia pico disminuye ($\sim 1/t$) mientras que la energía consumida aumenta ($\sim t$). Existe un tiempo crítico de cruce $t^*$ donde $m_{\text{bat, P}}(t^*) = m_{\text{bat, E}}(t^*)$. Para $t > t^*$, la energía pasa a ser la restricción activa y el exponente $p$ sí modifica la masa de la batería:

| Velocidad ($V$) | Apoyo ($P_{\text{aux}}$) | $t^*(p=1)$ | $t^*(p=2)$ | $t^*(p=4)$ |
|:---:|:---:|:---:|:---:|:---:|
| $600\text{ km/h}$ | $0\text{ W}$ | $211,7\text{ s}$ | $274,4\text{ s}$ | $399,3\text{ s}$ |
| $600\text{ km/h}$ | $1.000\text{ W}$ | $187,4\text{ s}$ | $228,9\text{ s}$ | $297,8\text{ s}$ |
| $1.000\text{ km/h}$ | $0\text{ W}$ | $219,6\text{ s}$ | $280,9\text{ s}$ | $402,0\text{ s}$ |
| $1.000\text{ km/h}$ | $1.000\text{ W}$ | $203,8\text{ s}$ | $251,1\text{ s}$ | $333,8\text{ s}$ |

Todos los tiempos de cruce superan ampliamente el límite de $60\text{ s}$ (e incluso el de $180\text{ s}$). Además, a mayor $p$, como se disipa menos energía durante la aceleración, el tiempo de cruce $t^*$ se desplaza notablemente hacia tiempos mayores.

---

## 8. Advertencias Físicas y Limitaciones Críticas

### 8.1. Limitación a Velocidad Cero ($v = 0$)
- **Formulación del modelo:** La potencia propulsiva mecánica se define como $P_{\text{mec}} = F \cdot v$. En reposo ($v = 0$), $P_{\text{mec}}(0) = 0\text{ W}$. Asumir una eficiencia axial constante $\eta = 0,70$ hasta $v = 0$ asigna una potencia propulsiva eléctrica de $0\text{ W}$ en el instante inicial.
- **Física real de propulsores aéreos:** Cualquier dispositivo de empuje aéreo (rotor, hélice entubada o fan) que genere empuje estático $T_0$ en reposo absorbe una potencia mecánica finita y sustancial, dada por la teoría del momento de Froude ($P_{\text{ideal}} = T_0^{3/2} / \sqrt{2 \rho A}$) dividida por la figura de mérito del propulsor ($FM < 1$).
- **Implicación:** El modelo subestima fuertemente la potencia absorbida a velocidades muy bajas ($v \to 0$).

### 8.2. Limitación Fundamental en Régimen Transónico ($M \approx 0,75 - 1,2$)
> [!WARNING]
> **Ninguna ley de potencias simple $D(v) = D_{\text{final}} (v/V)^p$ predice ni aproxima el arrastre transónico.**

A $1.000\text{ km/h}$ ($277,8\text{ m/s}$), el número de Mach a nivel del mar ($a \approx 340\text{ m/s}$) es $M \approx 0,82$; a mayor altitud supera $M \approx 0,87$. En este régimen:
1. **Divergencia de Mach ($M_{dd}$):** La compresibilidad del aire deja de ser lineal. Al superarse el Mach crítico, aparecen zonas supersónicas locales sobre el perfil donde el flujo acelera localmente a $M > 1$.
2. **Ondas de Choque y Arrastre de Onda:** Se forman ondas de choque de compresión que provocan una disipación irreversible de energía mecánica en calor (aumento de entropía), disparando el coeficiente de arrastre ($C_D$) en un fenómeno denominado "drag rise".
3. **Desprendimiento de Capa Límite:** El gradiente de presión adverso extremo inducido por el choque desprende la capa límite, generando separación masiva del flujo y arrastre de presión incontrolado.
4. **Dependencia Geométrica Crítica:** El arrastre transónico depende estrictamente de la distribución longitudinal del área transversal (Regla de las Áreas de Whitcomb), la relación espesor/cuerda $(t/c)$ y el ángulo de flecha alar. Un modelo cinemático que fija $D(V) = 50\text{ N}$ a priori asume una fuerza arbitraria sin base en la aerodinámica compresible real.
5. **Comportamiento Espurio de $p = 4$:** Para $v < V$, la curva con $p = 4$ produce una fuerza de arrastre drásticamente menor que el arrastre cuadrático clásico, subestimando de manera irreal la disipación aerodinámica en todo el rango subsónico previo.

### 8.3. No Extrapolación al Rendimiento del Vehículo
- Los resultados son análisis paramétricos condicionales bajo supuestos impuestos de misión. No constituyen datos de prestaciones de vuelo, capacidades demostradas ni envolventes certificadas de C02.
- No se han modelado: ascenso, guiñada, virajes, dinámica de transición aerodinámica, trimado, interferencia aerodinámica, refrigeración, límites térmicos de celda ni variación de resistencia interna por estado de carga (SoC).
- No deben extrapolarse a variantes de 2 kg o 10 kg, las cuales requieren sus propias geometrías CAD, curvas de masa y mapas de propulsión específicos.

---

## 9. Pruebas Automatizadas y Reproducibilidad

Se desarrolló una suite completa de pruebas bajo `unittest` en [`test_sensibilidad.py`](test_sensibilidad.py).

### Ejecución:
```sh
# Ejecución del módulo principal de cálculo:
python3 salidas/sensibilidad_ley_arrastre.py

# Ejecución de la suite completa de pruebas unitarias:
python3 -m unittest salidas/test_sensibilidad.py
```

### Resumen de la Suite (11 Pruebas Unitarias):
1. `test_c02_constants_integrity`: Integridad exacta de constantes nominales y presupuesto de CAD ligero ($2,20416\text{ kg}$).
2. `test_analytical_integral_formula`: Comprobación de divisores 3, 4 y 6 en la fórmula analítica para $p = 1, 2, 4$.
3. `test_numerical_vs_analytical_quadrature`: Verificación de error relativo $< 10^{-9}$ frente a cuadratura de Simpson.
4. `test_drag_work_theoretical_ratios`: Confirmación de razones teóricas $4/3$ y $2/3$.
5. `test_reproduction_of_reference_cases_p2`: Reproducción exacta de los 6 casos de $50\text{ N}$ del informe de entrada.
6. `test_cotejo_exacto_modelo_r2`: Cotejo dinámico programa-contra-programa contra `calcular_r2.py`.
7. `test_simultaneous_peak_power_vs_stage_energy`: Demostración de invariancia de la potencia pico terminal e independencia de las etapas.
8. `test_no_double_counting_acceleration_energy`: Verificación formal de suma por etapas y ausencia de doble conteo inercial o aerodinámico.
9. `test_active_constraint_at_60s`: Comprobación del dominio de la potencia pico en los 12 casos a $60\text{ s}$.
10. `test_crossover_behavior`: Verificación de tiempos de cruce $t^*$ y activación de la restricción de energía para tiempos largos.
11. `test_input_validation`: Rechazo robusto con `ValueError` ante entradas negativas o físicamente absurdas.

Resultado: **11/11 pruebas aprobadas exitosamente (`OK`) en 0,016 s**.

---

## 10. Trazabilidad Criptográfica de Archivos

| Archivo | Ubicación | SHA-256 |
|:---|:---|:---:|
| `INFORME.md` (referencia) | `entradas/.../potencia_simultanea_c02/INFORME.md` | `d7b724afd7b48b7058a1d1969afa4b869f14629d709d72e30f3170f03ee1627a` |
| `calcular_r2.py` (referencia) | `entradas/.../potencia_simultanea_c02/calcular_r2.py` | `73d70339ce0ce124d239c22a4cde8282b85f77becb0d163c138301066cd3b67a` |
| `sensibilidad_ley_arrastre.py` | `salidas/sensibilidad_ley_arrastre.py` | *(generado dinámicamente en salidas/)* |
| `test_sensibilidad.py` | `salidas/test_sensibilidad.py` | *(generado dinámicamente en salidas/)* |
| `tabla_comparacion_casos.csv` | `salidas/tabla_comparacion_casos.csv` | *(generado dinámicamente en salidas/)* |
| `tabla_sensibilidad_completa.csv` | `salidas/tabla_sensibilidad_completa.csv` | *(generado dinámicamente en salidas/)* |
| `resultados_sensibilidad.json` | `salidas/resultados_sensibilidad.json` | *(generado dinámicamente en salidas/)* |
| `README.md` | `salidas/README.md` | *(generado dinámicamente en salidas/)* |
