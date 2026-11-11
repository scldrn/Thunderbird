# Tabla Comparativa: Modelos Normalizados de 1er Orden y 2do Orden Crítico

> **Distinción metodológica:**
> - **Datos medidos:** NINGUNO disponible para el vehículo analizado. La referencia NASA NTRS 20230017299 (Weinstein y col., SciTech 2024) ensaya un ventilador Jetfan 130 Pro aisladamente en el túnel de 12 pies de NASA Langley; sus mediciones no calibran este ejemplo.
> - **Supuestos técnicos:** Constantes tau in {0.08, 0.20, 0.50} s como hipótesis de trabajo y análisis de sensibilidad; cota de rampa supuesta R = 50 N/s / 21 N ~ 2.381 s^-1.
> - **Cálculos:** Soluciones analíticas exactas, inversión de 3er orden por Halley (|residual| < 10^-14) y simulación numérica RK4/Euler. Unidades: segundos (s), milisegundos (ms), s^-1, y coeficientes adimensionales (adim).

## 1. Tiempos de Respuesta Lineales (Sin Limitación de Rampa)

| Modelo | $\tau$ (s) | $t_{10\%}$ (ms) | $t_{50\%}$ (ms) | $t_{90\%}$ (ms) | $t_{10\to 90\%}$ (ms) | Pendiente Máx ($\text{s}^{-1}$) | $t_{\text{inflex}}$ (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **1er orden** | 0.08 | 8.43 | 55.45 | 184.21 | 175.78 | 12.50 | N/A |
| **2do orden crít.** | 0.08 | 42.54 | 134.27 | 311.18 | 268.63 | 4.60 | 0.08 |
| **1er orden** | 0.20 | 21.07 | 138.63 | 460.52 | 439.44 | 5.00 | N/A |
| **2do orden crít.** | 0.20 | 106.36 | 335.67 | 777.94 | 671.58 | 1.84 | 0.20 |
| **1er orden** | 0.50 | 52.68 | 346.57 | 1151.29 | 1098.61 | 2.00 | N/A |
| **2do orden crít.** | 0.50 | 265.91 | 839.17 | 1944.86 | 1678.95 | 0.74 | 0.50 |

## 2. Ratios y Retardos Relativos (2do Orden frente a 1er Orden)

| $\tau$ (s) | $\Delta t_{10\%}$ (ms) | Ratio $t_{10\%}$ | $\Delta t_{50\%}$ (ms) | Ratio $t_{50\%}$ | $\Delta t_{90\%}$ (ms) | Ratio $t_{90\%}$ | $\Delta t_{10\to 90}$ (ms) | Ratio Subida |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.08 | +34.12 (+404.8%) | 5.0475x | +78.82 (+142.1%) | 2.4213x | +126.97 (+68.9%) | 1.6893x | +92.85 (+52.8%) | 1.5283x |
| 0.20 | +85.29 (+404.8%) | 5.0475x | +197.04 (+142.1%) | 2.4213x | +317.43 (+68.9%) | 1.6893x | +232.14 (+52.8%) | 1.5283x |
| 0.50 | +213.23 (+404.8%) | 5.0475x | +492.60 (+142.1%) | 2.4213x | +793.57 (+68.9%) | 1.6893x | +580.34 (+52.8%) | 1.5283x |

## 3. Coeficientes Adimensionales Universales ($u = t/\tau$)

| Modelo | $u_{10\%}$ | $u_{50\%}$ | $u_{90\%}$ | $\Delta u_{10\to 90\%}$ | Expresión Analítica |
|---|---:|---:|---:|---:|---|
| **1er orden** | 0.105361 | 0.693147 | 2.302585 | 2.197225 | $u = -\ln(1-p)$ |
| **2do orden crít.** | 0.531812 | 1.678347 | 3.889720 | 3.357909 | $u = -1 - W_{-1}(-(1-p)/e)$ |
| **Factor 2do / 1er** | **5.0475x** | **2.4213x** | **1.6893x** | **1.5283x** | Invariante respecto a $\tau$ |

## 4. Efecto de Limitación de Rampa ESC / Slew-Rate ($R = 50\text{ N/s} / 21\text{ N} \approx 2.381\text{ s}^{-1}$)

| Modelo | $\tau$ (s) | $t_{10\%}$ Lineal (ms) | $t_{10\%}$ con Rampa (ms) | $t_{50\%}$ Lineal (ms) | $t_{50\%}$ con Rampa (ms) | $t_{90\%}$ Lineal (ms) | $t_{90\%}$ con Rampa (ms) | Estado de Saturación |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **1er orden** | 0.08 | 8.43 | **42.00** | 55.45 | **210.00** | 184.21 | **391.55** | Saturado en arranque ($1/\tau > R$) |
| **2do orden crít.** | 0.08 | 42.54 | **50.87** | 134.27 | **218.87** | 311.18 | **432.14** | Saturado en inflexión ($1/(e\tau) > R$) |
| **1er orden** | 0.20 | 21.07 | **42.00** | 138.63 | **210.00** | 460.52 | **532.13** | Saturado en arranque ($1/\tau > R$) |
| **2do orden crít.** | 0.20 | 106.36 | **106.36** | 335.67 | **335.66** | 777.94 | **777.94** | No saturado ($1/(e\tau) \le R$) |
| **1er orden** | 0.50 | 52.68 | **52.68** | 346.57 | **346.57** | 1151.29 | **1151.29** | No saturado ($1/\tau \le R$) |
| **2do orden crít.** | 0.50 | 265.91 | **265.90** | 839.17 | **839.16** | 1944.86 | **1944.86** | No saturado ($1/(e\tau) \le R$) |
