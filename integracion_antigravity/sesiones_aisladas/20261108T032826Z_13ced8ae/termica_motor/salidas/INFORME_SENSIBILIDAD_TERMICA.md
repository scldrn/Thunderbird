# Informe Técnico: Modelo Térmico Concentrado de Sensibilidad para Motor de Módulo Interno (Escenario C01/C02)

**Fecha:** 8 de noviembre de 2026  
**Autor:** Antigravity (Entorno Autónomo de Análisis Térmico)  
**Ubicación de Entregables:** `salidas/`  
**Estado:** Sensibilidad Exploratoria Paramétrica — **No constituye diseño térmico final ni homologación de componente**  

---

## 1. Resumen Ejecutivo y Marco de Trabajo

Este informe presenta el desarrollo, resolución analítica, verificación numérica y análisis de sensibilidad de un modelo térmico de parámetros concentrados de un nodo (1-lump) para la reserva de motor del módulo propulsor de referencia D82, en el marco de la integración compacta estudiada en el informe de referencia `entradas/investigacion-aeronautica/ejecucion/G3/C02/INFORME-C02.md`.

El modelo responde a la ecuación diferencial lineal de balance térmico:
$$C \frac{dT}{dt} = P_{\text{loss}} - \frac{T - T_{\text{amb}}}{R}$$

Bajo las condiciones de contorno establecidas:
- Temperatura ambiente: $T_{\text{amb}} = 25{,}0\ ^\circ\text{C}$.
- Temperatura inicial: $T(0) = T_{\text{amb}} = 25{,}0\ ^\circ\text{C}$.
- Pérdida térmica disipada: $P_{\text{loss}} = 74{,}2\ \text{W}$, vinculada de manera estricta y explícita al escenario no validado C01/C02 (estacionario de 5 kg con rotor D82, potencia de eje demandada de 668 W y eficiencia eléctrica global supuesta de 0,90).
- Matriz de capacidad calorífica concentrada: $C \in \{10,\, 50,\, 100\}\ \text{J/K}$.
- Matriz de resistencia térmica hacia el entorno: $R \in \{1,\, 3,\, 10\}\ \text{K/W}$.
- Horizontes temporales de evaluación: $t \in \{10,\, 30,\, 120\}\ \text{s}$.
- Umbral de comparación: $80{,}0\ ^\circ\text{C}$, utilizado exclusivamente como valor ilustrativo procedente de la literatura técnica de la NASA ([Weinstein et al., AIAA SciTech 2024](https://ntrs.nasa.gov/api/citations/20230017299/downloads/Weinstein_SciTech2024_Final.pdf?attachment=true)), **sin ser considerado un límite operativo o de seguridad aplicable a todo motor eléctrico**.

Los entregables asociados generados en `salidas/` comprenden:
1. `modelo_termico.py`: Implementación modular en Python 3 de la formulación analítica y resolución numérica por Runge-Kutta de orden 4 (RK4).
2. `sensibilidad_termica.csv`: Matriz estructurada con los 27 casos evaluados y sus métricas térmicas asociadas.
3. `test_modelo_termico.py`: Batería de 12 pruebas unitarias y comprobaciones analíticas automatizadas.
4. `INFORME_SENSIBILIDAD_TERMICA.md`: El presente reporte técnico integral.

---

## 2. Clasificación Epistemológica: Datos Medidos, Supuestos y Cálculos

En cumplimiento de las directrices metodológicas de rigor epistémico, se distinguen explícitamente las tres naturalezas de la información empleada en este trabajo:

| Naturaleza Epistémica | Parámetro / Variable | Valor y Unidades | Fuente / Justificación Metodológica |
|---|---|---|---|
| **Dato Medido** | *Ninguno* | *N/A* | **No existen mediciones físicas reales.** La reserva de motor en C02 es un volumen vacío cilíndrico en CAD. No se dispone de prototipo físico ni ensayos de banco. |
| **Supuesto / Hipótesis** | Pérdida térmica constante | $P_{\text{loss}} = 74{,}2\ \text{W}$ | Demanda de diseño no validada del escenario C01/C02 (`INFORME-C02.md`, Sec. "Requisitos de motor: cálculo, no hardware disponible"). Corresponde a $P_{\text{eje}} = 668\ \text{W}$ con $\eta = 0{,}90$. |
| **Supuesto / Hipótesis** | Temperatura ambiente | $T_{\text{amb}} = 25{,}0\ ^\circ\text{C}$ | Condición normalizada de ensayo estándar a nivel del suelo. |
| **Supuesto / Hipótesis** | Condición inicial térmica | $T(0) = 25{,}0\ ^\circ\text{C}$ | Arranque en equilibrio térmico con el ambiente. |
| **Supuesto / Hipótesis** | Rango de capacidad térmica | $C \in \{10,\, 50,\, 100\}\ \text{J/K}$ | Rango plausible de sensibilidad representativo de micromotores BLDC de 30 a 150 g de masa activa de cobre/acero. |
| **Supuesto / Hipótesis** | Rango de resistencia térmica | $R \in \{1,\, 3,\, 10\}\ \text{K/W}$ | Exploración de entornos de refrigeración: $1\ \text{K/W}$ (buen acoplamiento por conducción/convección forzada), $3\ \text{K/W}$ (disipación convectiva moderada), $10\ \text{K/W}$ (alojamiento encapsulado y estancado). |
| **Supuesto / Hipótesis** | Hipótesis de nodo concentrado | Biot $\ll 1$ | Asume conductividad interna infinita en el motor (temperatura espacialmente uniforme). |
| **Supuesto / Hipótesis** | Umbral ilustrativo de contraste | $T_{\text{umbral}} = 80{,}0\ ^\circ\text{C}$ | Cota de referencia metodológica tomada de NASA Weinstein et al. (AIAA SciTech 2024); **no es límite general de motor**. |
| **Cálculo Analítico** | Constante de tiempo | $\tau = R \cdot C\ \text{[s]}$ | Solución de la ecuación característica de primer orden. |
| **Cálculo Analítico** | Sobretemperatura estacionaria | $\Delta T_{\text{ss}} = R \cdot P_{\text{loss}}\ \text{[K]}$ | Balance en $dT/dt = 0 \implies \Delta T_{\text{ss}} = R \cdot P_{\text{loss}}$. |
| **Cálculo Analítico** | Temperatura estacionaria | $T_{\text{ss}} = T_{\text{amb}} + \Delta T_{\text{ss}}\ \text{[}^\circ\text{C]}$ | Asíntota para $t \to \infty$. |
| **Cálculo Analítico** | Evolución transitoria $T(t)$ | $T(t) = T_{\text{amb}} + \Delta T_{\text{ss}}(1 - e^{-t/\tau})\ \text{[}^\circ\text{C]}$ | Solución analítica exacta de la EDO lineal de 1er orden. |
| **Cálculo Analítico** | Tasa de calentamiento $dT/dt$ | $\frac{dT}{dt}(t) = \frac{P_{\text{loss}}}{C} e^{-t/\tau}\ \text{[K/s]}$ | Derivada temporal analítica de la trayectoria. |
| **Cálculo Analítico** | Tiempo de alcance de 80 °C | $t_{80} = -\tau \ln\left(1 - \frac{55}{R \cdot P_{\text{loss}}}\right)\ \text{[s]}$ | Inversión analítica de la función de temperatura para $T(t) = 80\ ^\circ\text{C}$. |

---

## 3. Vinculación con el Escenario No Validado C01/C02

El informe de integración geométrica `INFORME-C02.md` señala en su sección **"Requisitos de motor: cálculo, no hardware disponible"** lo siguiente:

> *"Se aplican los puntos C01 de estacionario de 5 kg, $\kappa=0{,}85$ y eficiencia eléctrica conjunta 0,90 como **demandas de diseño**. No son cargas instaladas aceptadas del C02.*  
> *Para el rotor nominal D82:  
> - Reserva cilíndrica de motor: Ø21,8 × 16,1 mm.  
> - Potencia de eje del escenario: 668 W.  
> - Par de eje del escenario: 0,138 N·m.  
> - Régimen del escenario: 46.231 rpm.  
> - Pérdida conjunta motor+ESC supuesta: 74,2 W.*  
> [...]  
> *La exposición directa de todo el cilindro es deliberadamente optimista: el motor está dentro de una copa y faltan resistencias en serie, contactos y flujo de cavidad. No se predicen temperaturas reales ni se asigna una temperatura admisible de componente. La refrigeración es un requisito pendiente decisivo del alojamiento compacto."*

La pérdida de $74{,}2\ \text{W}$ se deriva directamente del balance de potencias supuesto:
$$P_{\text{eléctrica}} = \frac{P_{\text{eje}}}{\eta_{\text{eléctrica}}} = \frac{668\ \text{W}}{0{,}90} \approx 742{,}22\ \text{W}$$
$$P_{\text{loss}} = P_{\text{eléctrica}} - P_{\text{eje}} = 742{,}22 - 668 = 74{,}22\ \text{W} \approx 74{,}2\ \text{W}$$

**Advertencia Fundamental:** Este valor es una hipótesis matemática de dimensionamiento aéreo preliminar y no proviene de un motor existente, ensayado o seleccionado. Por lo tanto, cualquier resultado térmico derivado debe entenderse estrictamente como una exploración de sensibilidad y no como una predicción operativa del vehículo.

---

## 4. Fundamento Teórico y Formulación Matemática

### 4.1. Ecuación Diferencial Gobernadora
El balance de energía térmica para un cuerpo isotermo concentrado de capacidad térmica $C$ acoplado a un sumidero infinito a $T_{\text{amb}}$ mediante una resistencia térmica $R$ es:
$$C \frac{dT(t)}{dt} = P_{\text{loss}} - \frac{T(t) - T_{\text{amb}}}{R}$$

Reordenando en forma canónica de sistema de primer orden:
$$\frac{dT(t)}{dt} + \frac{1}{R \cdot C} T(t) = \frac{P_{\text{loss}}}{C} + \frac{T_{\text{amb}}}{R \cdot C}$$

Definiendo la sobretemperatura respecto al ambiente $\theta(t) = T(t) - T_{\text{amb}}$ y la constante de tiempo térmica $\tau = R \cdot C$:
$$\frac{d\theta(t)}{dt} + \frac{1}{\tau} \theta(t) = \frac{P_{\text{loss}}}{C}$$

### 4.2. Solución Analítica Exacta
Multiplicando por el factor integrante $\mu(t) = e^{t/\tau}$:
$$\frac{d}{dt} \left[ \theta(t) e^{t/\tau} \right] = \frac{P_{\text{loss}}}{C} e^{t/\tau}$$

Integrando entre $t=0$ (donde $\theta(0) = 0$ por la condición $T(0) = T_{\text{amb}}$) y $t$:
$$\theta(t) e^{t/\tau} = \frac{P_{\text{loss}}}{C} \left[ \tau e^{t/\tau} - \tau \right] = \frac{P_{\text{loss}}}{C} (R \cdot C) \left( e^{t/\tau} - 1 \right) = R \cdot P_{\text{loss}} \left( e^{t/\tau} - 1 \right)$$

Despejando $\theta(t)$ y restituyendo $T(t)$:
$$T(t) = T_{\text{amb}} + R \cdot P_{\text{loss}} \left( 1 - e^{-t / \tau} \right)$$
$$\Delta T(t) = T(t) - T_{\text{amb}} = R \cdot P_{\text{loss}} \left( 1 - e^{-t / \tau} \right)$$

### 4.3. Tasa de Calentamiento Temporal
Derivando analíticamente respecto al tiempo:
$$\frac{dT(t)}{dt} = \frac{R \cdot P_{\text{loss}}}{\tau} e^{-t/\tau} = \frac{P_{\text{loss}}}{C} e^{-t / (R \cdot C)}$$

Propiedades físicas fundamentales:
- **Tasa inicial ($t=0$):** $\left.\frac{dT}{dt}\right|_{t=0} = \frac{P_{\text{loss}}}{C}$. Depende **única y exclusivamente** de la capacidad térmica $C$ y de la potencia disipada $P_{\text{loss}}$, siendo completamente independiente de la resistencia térmica $R$.
- **Régimen permanente ($t \to \infty$):** $\lim_{t \to \infty} T(t) = T_{\text{ss}} = T_{\text{amb}} + R \cdot P_{\text{loss}}$. Depende exclusivamente de $R$ y $P_{\text{loss}}$, siendo independiente de $C$.
- **Monotonía y concavidad:** Como $P_{\text{loss}} > 0$, $\frac{dT}{dt} > 0$ y $\frac{d^2T}{dt^2} = -\frac{P_{\text{loss}}}{R C^2} e^{-t/\tau} < 0$, garantizando un calentamiento asintótico estrictamente cóncavo hacia abajo.

### 4.4. Inversión Analítica del Tiempo de Cruce de Umbral
Para una temperatura umbral $T_{\text{target}}$ tal que $T_{\text{amb}} \le T_{\text{target}} < T_{\text{ss}}$, el tiempo exacto en que se alcanza dicho valor se despeja de:
$$\frac{T_{\text{target}} - T_{\text{amb}}}{R \cdot P_{\text{loss}}} = 1 - e^{-t_{\text{target}} / \tau}$$
$$t_{\text{target}} = -\tau \ln \left( 1 - \frac{T_{\text{target}} - T_{\text{amb}}}{R \cdot P_{\text{loss}}} \right) = - R \cdot C \ln \left( 1 - \frac{T_{\text{target}} - T_{\text{amb}}}{R \cdot P_{\text{loss}}} \right)$$

Para $T_{\text{target}} = 80{,}0\ ^\circ\text{C}$ con $T_{\text{amb}} = 25{,}0\ ^\circ\text{C}$, el salto requerido es $\Delta T = 55{,}0\ \text{K}$. Como $R \cdot P_{\text{loss}} \ge 1{,}0 \times 74{,}2 = 74{,}2\ \text{K} > 55{,}0\ \text{K}$ para todos los valores evaluados ($R \in \{1, 3, 10\}$), el umbral de 80 °C es asintóticamente alcanzable en los 9 pares $(C, R)$.

---

## 5. Justificación Metodológica del Umbral Ilustrativo de 80 °C (NASA SciTech 2024)

El valor de **80 °C** se introduce en este estudio en estricto cumplimiento de la solicitud, tomando como referencia el informe técnico de la NASA:
*Weinstein, N., et al., "Thermal Modeling and Testing of an Electric Aircraft Powertrain Motor / Inverter", AIAA SciTech 2024 Forum, NASA Glenn Research Center / Langley Research Center* ([Enlace NTRS NASA](https://ntrs.nasa.gov/api/citations/20230017299/downloads/Weinstein_SciTech2024_Final.pdf?attachment=true)).

### Contexto Técnico del Umbral:
1. **Referencia metodológica de contraste:** En dicho documento, 80 °C se utiliza como umbral de referencia característico para monitorización de devanados y control de temperatura de banco durante fases de carga transitoria y pruebas de laboratorio.
2. **Imanes permanentes de neodimio:** En imanes NdFeB estándar (grados N, sin dopaje pesado de disprosio o terbio), temperaturas del orden de 80 °C a 100 °C marcan el inicio de pérdidas térmicas reversibles de inducción remanente ($B_r$) y riesgo de desimanación irreversible si el punto de trabajo magnético cae por debajo del codo de la curva de desmagnetización.
3. **No es un límite universal:** Los motores eléctricos aeronáuticos y de competición emplean rutinariamente materiales con tolerancias térmicas sustancialmente superiores:
   - **Clases de aislamiento de devanado (norma NEMA / IEC 60085):** Clase F ($155\ ^\circ\text{C}$), Clase H ($180\ ^\circ\text{C}$) o Clase 200/220 ($200\text{--}220\ ^\circ\text{C}$).
   - **Grados magnéticos avanzados:** Neodimio de alta temperatura (grados SH hasta $150\ ^\circ\text{C}$, UH hasta $180\ ^\circ\text{C}$, EH hasta $200\ ^\circ\text{C}$) o Samario-Cobalto ($Sm_2Co_{17}$ hasta $300\text{--}350\ ^\circ\text{C}$).
4. **Conclusión epistemológica:** La comparación con 80 °C sirve para evaluar la velocidad de calentamiento en una escala temporal estandarizada, **no para dictaminar la falla o inviabilidad intrínseca de una máquina eléctrica no seleccionada**.

---

## 6. Resultados: Matriz Paramétrica Completa (27 Casos)

La evaluación sistemática de las 27 combinaciones ($3 \times 3 \times 3$) se resume a continuación, ordenada por capacidad térmica $C$, resistencia térmica $R$ y tiempo transcurrido $t$.

| Caso | $C$ [J/K] | $R$ [K/W] | $\tau$ [s] | $t$ [s] | $t/\tau$ | Régimen Dinámico | $T(t)$ [°C] | $\Delta T$ [K] | $dT/dt$ [K/s] | Supera 80°C | Margen 80°C [K] | $t_{80}$ [s] | $T_{\text{ss}}$ [°C] |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|:---:|---:|---:|---:|
| **C10_R1_t10** | 10 | 1 | 10 | 10 | 1,000 | Transitorio acoplado | **71,90** | 46,90 | 2,730 | No | +8,10 | 13,52 | 99,20 |
| **C10_R1_t30** | 10 | 1 | 10 | 30 | 3,000 | Cuasi estacionario | **95,51** | 70,51 | 0,369 | **Sí** | -15,51 | 13,52 | 99,20 |
| **C10_R1_t120** | 10 | 1 | 10 | 120 | 12,000 | Cuasi estacionario | **99,20** | 74,20 | 0,000 | **Sí** | -19,20 | 13,52 | 99,20 |
| **C10_R3_t10** | 10 | 3 | 30 | 10 | 0,333 | Transitorio acoplado | **88,10** | 63,10 | 5,317 | **Sí** | -8,10 | 8,51 | 247,60 |
| **C10_R3_t30** | 10 | 3 | 30 | 30 | 1,000 | Transitorio acoplado | **165,71** | 140,71 | 2,730 | **Sí** | -85,71 | 8,51 | 247,60 |
| **C10_R3_t120** | 10 | 3 | 30 | 120 | 4,000 | Cuasi estacionario | **243,52** | 218,52 | 0,136 | **Sí** | -163,52 | 8,51 | 247,60 |
| **C10_R10_t10** | 10 | 10 | 100 | 10 | 0,100 | Casi adiabático | **95,61** | 70,61 | 6,714 | **Sí** | -15,61 | 7,70 | 767,00 |
| **C10_R10_t30** | 10 | 10 | 100 | 30 | 0,300 | Transitorio acoplado | **217,31** | 192,31 | 5,497 | **Sí** | -137,31 | 7,70 | 767,00 |
| **C10_R10_t120** | 10 | 10 | 100 | 120 | 1,200 | Transitorio acoplado | **543,51** | 518,51 | 2,235 | **Sí** | -463,51 | 7,70 | 767,00 |
| **C50_R1_t10** | 50 | 1 | 50 | 10 | 0,200 | Transitorio acoplado | **38,45** | 13,45 | 1,215 | No | +41,55 | 67,59 | 99,20 |
| **C50_R1_t30** | 50 | 1 | 50 | 30 | 0,600 | Transitorio acoplado | **58,48** | 33,48 | 0,814 | No | +21,52 | 67,59 | 99,20 |
| **C50_R1_t120** | 50 | 1 | 50 | 120 | 2,400 | Transitorio acoplado | **92,47** | 67,47 | 0,135 | **Sí** | -12,47 | 67,59 | 99,20 |
| **C50_R3_t10** | 50 | 3 | 150 | 10 | 0,067 | Casi adiabático | **39,36** | 14,36 | 1,388 | No | +40,64 | 42,57 | 247,60 |
| **C50_R3_t30** | 50 | 3 | 150 | 30 | 0,200 | Transitorio acoplado | **65,35** | 40,35 | 1,215 | No | +14,65 | 42,57 | 247,60 |
| **C50_R3_t120** | 50 | 3 | 150 | 120 | 0,800 | Transitorio acoplado | **147,58** | 122,58 | 0,667 | **Sí** | -67,58 | 42,57 | 247,60 |
| **C50_R10_t10** | 50 | 10 | 500 | 10 | 0,020 | Casi adiabático | **39,69** | 14,69 | 1,455 | No | +40,31 | 38,51 | 767,00 |
| **C50_R10_t30** | 50 | 10 | 500 | 30 | 0,060 | Casi adiabático | **68,21** | 43,21 | 1,398 | No | +11,79 | 38,51 | 767,00 |
| **C50_R10_t120** | 50 | 10 | 500 | 120 | 0,240 | Transitorio acoplado | **183,32** | 158,32 | 1,167 | **Sí** | -103,32 | 38,51 | 767,00 |
| **C100_R1_t10** | 100 | 1 | 100 | 10 | 0,100 | Casi adiabático | **32,06** | 7,06 | 0,671 | No | +47,94 | 135,19 | 99,20 |
| **C100_R1_t30** | 100 | 1 | 100 | 30 | 0,300 | Transitorio acoplado | **44,23** | 19,23 | 0,550 | No | +35,77 | 135,19 | 99,20 |
| **C100_R1_t120** | 100 | 1 | 100 | 120 | 1,200 | Transitorio acoplado | **76,85** | 51,85 | 0,224 | No | **+3,15** | 135,19 | 99,20 |
| **C100_R3_t10** | 100 | 3 | 300 | 10 | 0,033 | Casi adiabático | **32,30** | 7,30 | 0,718 | No | +47,70 | 85,14 | 247,60 |
| **C100_R3_t30** | 100 | 3 | 300 | 30 | 0,100 | Casi adiabático | **46,18** | 21,18 | 0,671 | No | +33,82 | 85,14 | 247,60 |
| **C100_R3_t120** | 100 | 3 | 300 | 120 | 0,400 | Transitorio acoplado | **98,39** | 73,39 | 0,497 | **Sí** | -18,39 | 85,14 | 247,60 |
| **C100_R10_t10** | 100 | 10 | 1000 | 10 | 0,010 | Casi adiabático | **32,38** | 7,38 | 0,735 | No | +47,62 | 77,02 | 767,00 |
| **C100_R10_t30** | 100 | 10 | 1000 | 30 | 0,030 | Casi adiabático | **46,93** | 21,93 | 0,720 | No | +33,07 | 77,02 | 767,00 |
| **C100_R10_t120** | 100 | 10 | 1000 | 120 | 0,120 | Casi adiabático | **108,91** | 83,91 | 0,658 | **Sí** | -28,91 | 77,02 | 767,00 |

*Nota epistemológica:* Los datos numéricos de la tabla son cálculos analíticos exactos derivados de las hipótesis del modelo. Todos los registros constan en el archivo `salidas/sensibilidad_termica.csv`.

---

## 7. Análisis de Sensibilidad y Discusión Física

### 7.1. Dinámica a Tiempos Cortos ($t = 10\ \text{s}$): Régimen Casi Adiabático
Para $t \ll \tau$ (cuando $t/\tau < 0{,}2$), el término de disipación convectiva/conductiva $\frac{T - T_{\text{amb}}}{R}$ es prácticamente despreciable frente a la generación interna $P_{\text{loss}}$. La aproximación asintótica de Taylor da:
$$T(t) \approx T_{\text{amb}} + \frac{P_{\text{loss}}}{C} t$$

- Para $C = 100\ \text{J/K}$, la predicción adiabática a $t=10\ \text{s}$ es $25 + \frac{74{,}2}{100} \times 10 = 32{,}42\ ^\circ\text{C}$. Los valores exactos para $R=1$, $R=3$ y $R=10\ \text{K/W}$ son respectivamente $32{,}06\ ^\circ\text{C}$, $32{,}30\ ^\circ\text{C}$ y $32{,}38\ ^\circ\text{C}$ (una dispersión inferior a $0{,}32\ \text{K}$).
- Para $C = 50\ \text{J/K}$, la aproximación adiabática a $10\ \text{s}$ es $25 + 14{,}84 = 39{,}84\ ^\circ\text{C}$; los valores reales caen en la estrecha banda de $38{,}45\ ^\circ\text{C}$ a $39{,}69\ ^\circ\text{C}$.
- **Conclusión de diseño:** Durante los primeros 10 segundos de maniobra intensa o ráfaga de empuje, la resistencia térmica $R$ apenas influye; la contención térmica depende casi en su totalidad de la masa térmica activa ($C$).

### 7.2. Sensibilidad a Tiempos Medios ($t = 30\ \text{s}$)
A $t = 30\ \text{s}$:
- Con $C = 10\ \text{J/K}$, la constante de tiempo es corta ($\tau \le 30\ \text{s}$ para $R \le 3$), por lo que las temperaturas ya superan drásticamente el umbral ilustrativo ($95{,}51\ ^\circ\text{C}$ para $R=1$; $165{,}71\ ^\circ\text{C}$ para $R=3$; $217{,}31\ ^\circ\text{C}$ para $R=10$).
- Con $C = 50\ \text{J/K}$, la temperatura se mantiene entre $58{,}48\ ^\circ\text{C}$ ($R=1$) y $68{,}21\ ^\circ\text{C}$ ($R=10$), preservando un margen positivo de $11{,}8\ \text{K}$ a $21{,}5\ \text{K}$ frente al umbral de 80 °C.
- Con $C = 100\ \text{J/K}$, el calentamiento acumulado es moderado ($44{,}23\ ^\circ\text{C}$ a $46{,}93\ ^\circ\text{C}$), con márgenes superiores a $33\ \text{K}$.

### 7.3. Dinámica a Tiempos Prolongados ($t = 120\ \text{s}$): Dominancia de la Resistencia Térmica
A $t = 120\ \text{s}$ (2 minutos de estacionario sostenido):
- **Solo un único caso de los 27 permanece por debajo del umbral de 80 °C:** el caso **C100_R1_t120**, con $T = 76{,}85\ ^\circ\text{C}$ (margen de $+3{,}15\ \text{K}$). En este caso particular, $\tau = 100\ \text{s}$ y el tiempo necesario para alcanzar 80 °C es $t_{80} = 135{,}19\ \text{s}$.
- Todos los demás casos ($R \ge 3\ \text{K/W}$ o $C \le 50\ \text{J/K}$) han cruzado el umbral de 80 °C mucho antes de los 120 s:
  - Para $R = 3\ \text{K/W}$: las temperaturas oscilan entre $98{,}39\ ^\circ\text{C}$ ($C=100$) y $243{,}52\ ^\circ\text{C}$ ($C=10$).
  - Para $R = 10\ \text{K/W}$: las temperaturas oscilan entre $108{,}91\ ^\circ\text{C}$ ($C=100$) y $543{,}51\ ^\circ\text{C}$ ($C=10$).
- **Conclusión de diseño:** Si la misión requiere sustentación estacionaria continua por más de 1 a 2 minutos con disipación del orden de 74 W, es imprescindible garantizar una resistencia térmica extraordinariamente baja ($R \le 1\ \text{K/W}$), lo cual exige convección forzada directa o acoplamiento conductivo masivo con la estructura metálica del vehículo.

---

## 8. Verificación Analítica y Pruebas Unitarias

Se implementó un conjunto de pruebas formales en `salidas/test_modelo_termico.py`, ejecutadas mediante el módulo estándar `unittest` de Python 3 en el entorno sandbox aislado. Las 12 pruebas ejecutadas y sus criterios de superación fueron:

```text
test_asymptotic_limit ..................................................... [PASÓ]
  Verifica convergencia a T_ss en t = 25 tau con tolerancia < 1e-6 K.
test_c02_loss_value_consistency ........................................... [PASÓ]
  Verifica que P_loss = 74.2 W proviene de P_eje = 668 W con eta = 0.90.
test_characteristic_time_constant ......................................... [PASÓ]
  Verifica que en t = tau, delta_T / delta_T_ss = 1 - 1/e (~63.212056%).
test_governing_ode_identity ............................................... [PASÓ]
  Verifica que el residuo C dT/dt + (T - Tamb)/R - P_loss es identicamente nulo (< 1e-9).
test_initial_condition .................................................... [PASÓ]
  Verifica que T(0) == Tamb (25.0 °C) y delta_T(0) == 0.0 K.
test_initial_heating_rate ................................................. [PASÓ]
  Verifica que (dT/dt)(0) == P_loss / C de forma exacta.
test_monotonicity_and_concavity ........................................... [PASÓ]
  Verifica dT/dt > 0 y d^2T/dt^2 < 0 en toda la trayectoria.
test_parametric_grid_structure_and_csv .................................... [PASÓ]
  Verifica generacion integra de los 27 casos en CSV con cabeceras y trazabilidad.
test_rk4_numerical_integration_convergence ................................ [PASÓ]
  Verifica que el integrador RK4 (dt=0.005 s) coincide con la solucion analitica (< 1e-5 K).
test_threshold_80C_specific_values ........................................ [PASÓ]
  Verifica calculo analitico de t_80 exacto para todos los pares (C, R).
test_time_to_temperature_inversion ........................................ [PASÓ]
  Verifica inversion temporal T(t_reach) == T_target para multiples temperaturas intermedias.
test_unreachable_temperature .............................................. [PASÓ]
  Verifica que para T_target >= T_ss la funcion devuelve None (inalcanzable).

----------------------------------------------------------------------
Ran 12 tests in 0.324s (100% OK)
```

---

## 9. Limitaciones Críticas: Razones para No Extrapolar la Disipación Real

Es imperativo subrayar que los valores estacionarios ($T_{\text{ss}}$) calculados en este informe para $R = 3\ \text{K/W}$ ($247{,}6\ ^\circ\text{C}$) y $R = 10\ \text{K/W}$ ($767{,}0\ ^\circ\text{C}$) son **construcciones matemáticas analíticas extremas** y **no deben extrapolarse como temperaturas físicas que el motor alcanzaría en la realidad**. Las razones físicas y metodológicas son las siguientes:

1. **Destrucción física previa del componente:** A temperaturas superiores a $180\text{--}220\ ^\circ\text{C}$, los barnices de aislamiento de los devanados de cobre sufren pirólisis, provocando cortocircuitos entre espiras; los imanes de neodimio sufren desimanación térmica irreversible completa; y la grasa de los rodamientos de bolas se carboniza. Por tanto, predicciones analíticas como $543\ ^\circ\text{C}$ o $767\ ^\circ\text{C}$ describen un sistema lineal ficticio que habría colapsado mucho antes.
2. **Dependencia térmica de las pérdidas de cobre ($I^2 R$):** La resistividad eléctrica del cobre aumenta con la temperatura con un coeficiente lineal de $\alpha_{\text{Cu}} \approx 0{,}00393\ \text{K}^{-1}$. A $125\ ^\circ\text{C}$, la resistencia eléctrica es un $39{,}3\%$ mayor que a $25\ ^\circ\text{C}$, lo que incrementa las pérdidas por efecto Joule para una misma corriente de par, pudiendo disparar un embalamiento térmico que este modelo (con $P_{\text{loss}}$ constante de 74,2 W) no contempla.
3. **No linealidad de la transferencia térmica hacia el ambiente:**
   - **Convección:** El coeficiente de convección $h$ aumenta con la sobretemperatura $(\Delta T)^{1/4}$ o $(\Delta T)^{1/3}$ en convección natural, o con la velocidad inducida del flujo en convección forzada.
   - **Radiación superficial:** La disipación radiativa crece con $T^4 - T_{\text{amb}}^4$. A temperaturas elevadas ($> 150\ ^\circ\text{C}$), la radiación neta reduce la resistencia térmica efectiva global, amortiguando la temperatura final real respecto a la asíntota lineal pura.
4. **Geometría real del alojamiento C02:** Como advierte explícitamente el informe `INFORME-C02.md`, el motor se encuentra alojado en el interior de un cubo ahuecado (hollow hub) cerrado. Existen resistencias térmicas en serie complejas (entrehierro de aire de 0,5 mm, soporte de rodamiento, contacto con el cubo y paredes del conducto). No hay contacto directo ideal con el aire libre exterior sin penalización aerodinámica o constructiva.
5. **Variabilidad de la potencia de eje en vuelo real:** El valor de 668 W corresponde a un punto estacionario puro de 5 kg con cuatro rotores nominales D82. En vuelo de avance horizontal, transición o descenso, la demanda de potencia de los rotores verticales varía drásticamente, alternando periodos de carga con descansos térmicos no representables por una disipación constante en el tiempo.

---

## 10. Conclusiones y Recomendaciones de Ingeniería

1. **Capacidad de amortiguamiento transitorio:** Para operaciones breves ($t \le 10\ \text{s}$), una capacidad térmica $C \ge 50\ \text{J/K}$ garantiza que el incremento de temperatura no supere los $15\ \text{K}$ (alcanzando $< 40\ ^\circ\text{C}$), proporcionando un margen de seguridad cómodo frente a umbrales conservadores de referencia.
2. **Requisito crítico de refrigeración para estacionario continuo:** Para tiempos de sustentación prolongados ($t \ge 120\ \text{s}$), disipar $74{,}2\ \text{W}$ por módulo dentro del volumen cilíndrico de $\varnothing 21{,}8 \times 16{,}1\ \text{mm}$ sin superar temperaturas operativas admisibles es inviable sin ventilación activa forzada o acoplamiento térmico directo ($R \le 1\ \text{K/W}$).
3. **Paso siguiente en la maduración del diseño C02:** Reemplazar el modelo concentrado de 1 nodo por una red de resistencias térmicas acopladas (stator, devanado, rotor, entrehierro, alojamiento y flujo inducido por el rotor D82) y acoplarlo al mapa de flujo tridimensional CFD cuando se disponga de la geometría de álabes y motor comercial seleccionado.
