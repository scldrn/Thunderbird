# Tablas de Análisis Paramétrico de Cargas en Compuerta

> **NOTA METODOLÓGICA Y LIMITACIONES**:
> 1. Los valores de fuerza $F$ y momento $M$ se obtienen asumiendo $\Delta p = C_{p,\text{dif}} \cdot q$ **estrictamente uniforme** sobre toda el área.
> 2. Las áreas $A$ y brazos $L$ son **EXPLÍCITAMENTE HIPOTÉTICOS** y están escalados geométricamente con $(m/5)^{1/3}$.
> 3. La presión dinámica $q$ **NO** es una presión diferencial uniforme real.
> 4. Las tapas son para **baja velocidad / despegue / transición**; no están validadas para vuelo a 600 ni a 1000 km/h.
> 5. **Ningún actuador, soporte ni mecanismo instalado está resuelto ni validado.**

## Condición de Vuelo Hipotética: $V = 600$ km/h (166.67 m/s)
- **Densidad $\rho$**: 1.225 kg/m³
- **Presión dinámica $q$**: 17013.89 Pa (17.014 kPa)

### Variante de Masa Objetivo: 2.0 kg
- Factor lineal $\lambda_L$: `0.7368` | Factor área $\lambda_A$: `0.5429`
- Área supuesta $A$: `0.003800` m² (38.00 cm²)
- Brazo supuesto $L$: `0.0354` m (35.37 mm)

| $C_{p,\text{dif}}$ [-] | $\Delta p$ [Pa] | $\Delta p$ [kPa] | Fuerza $F$ [N] | Fuerza [kgf] | Momento $M$ [N·m] |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0.10 |     1701.4 |    1.701 |      6.47 |    0.66 |    0.229 |
| 0.20 |     3402.8 |    3.403 |     12.93 |    1.32 |    0.457 |
| 0.50 |     8506.9 |    8.507 |     32.33 |    3.30 |    1.143 |
| 0.80 |    13611.1 |   13.611 |     51.72 |    5.27 |    1.829 |
| 1.00 |    17013.9 |   17.014 |     64.66 |    6.59 |    2.287 |
| 1.20 |    20416.7 |   20.417 |     77.59 |    7.91 |    2.744 |
| 1.50 |    25520.8 |   25.521 |     96.98 |    9.89 |    3.430 |
| 2.00 |    34027.8 |   34.028 |    129.31 |   13.19 |    4.573 |

### Variante de Masa Objetivo: 5.0 kg
- Factor lineal $\lambda_L$: `1.0000` | Factor área $\lambda_A$: `1.0000`
- Área supuesta $A$: `0.007000` m² (70.00 cm²)
- Brazo supuesto $L$: `0.0480` m (48.00 mm)

| $C_{p,\text{dif}}$ [-] | $\Delta p$ [Pa] | $\Delta p$ [kPa] | Fuerza $F$ [N] | Fuerza [kgf] | Momento $M$ [N·m] |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0.10 |     1701.4 |    1.701 |     11.91 |    1.21 |    0.572 |
| 0.20 |     3402.8 |    3.403 |     23.82 |    2.43 |    1.143 |
| 0.50 |     8506.9 |    8.507 |     59.55 |    6.07 |    2.858 |
| 0.80 |    13611.1 |   13.611 |     95.28 |    9.72 |    4.573 |
| 1.00 |    17013.9 |   17.014 |    119.10 |   12.14 |    5.717 |
| 1.20 |    20416.7 |   20.417 |    142.92 |   14.57 |    6.860 |
| 1.50 |    25520.8 |   25.521 |    178.65 |   18.22 |    8.575 |
| 2.00 |    34027.8 |   34.028 |    238.19 |   24.29 |   11.433 |

### Variante de Masa Objetivo: 10.0 kg
- Factor lineal $\lambda_L$: `1.2599` | Factor área $\lambda_A$: `1.5874`
- Área supuesta $A$: `0.011112` m² (111.12 cm²)
- Brazo supuesto $L$: `0.0605` m (60.48 mm)

| $C_{p,\text{dif}}$ [-] | $\Delta p$ [Pa] | $\Delta p$ [kPa] | Fuerza $F$ [N] | Fuerza [kgf] | Momento $M$ [N·m] |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0.10 |     1701.4 |    1.701 |     18.91 |    1.93 |    1.143 |
| 0.20 |     3402.8 |    3.403 |     37.81 |    3.86 |    2.287 |
| 0.50 |     8506.9 |    8.507 |     94.53 |    9.64 |    5.717 |
| 0.80 |    13611.1 |   13.611 |    151.24 |   15.42 |    9.147 |
| 1.00 |    17013.9 |   17.014 |    189.06 |   19.28 |   11.433 |
| 1.20 |    20416.7 |   20.417 |    226.87 |   23.13 |   13.720 |
| 1.50 |    25520.8 |   25.521 |    283.58 |   28.92 |   17.150 |
| 2.00 |    34027.8 |   34.028 |    378.11 |   38.56 |   22.867 |

## Condición de Vuelo Hipotética: $V = 1000$ km/h (277.78 m/s)
- **Densidad $\rho$**: 1.225 kg/m³
- **Presión dinámica $q$**: 47260.80 Pa (47.261 kPa)

### Variante de Masa Objetivo: 2.0 kg
- Factor lineal $\lambda_L$: `0.7368` | Factor área $\lambda_A$: `0.5429`
- Área supuesta $A$: `0.003800` m² (38.00 cm²)
- Brazo supuesto $L$: `0.0354` m (35.37 mm)

| $C_{p,\text{dif}}$ [-] | $\Delta p$ [Pa] | $\Delta p$ [kPa] | Fuerza $F$ [N] | Fuerza [kgf] | Momento $M$ [N·m] |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0.10 |     4726.1 |    4.726 |     17.96 |    1.83 |    0.635 |
| 0.20 |     9452.2 |    9.452 |     35.92 |    3.66 |    1.270 |
| 0.50 |    23630.4 |   23.630 |     89.80 |    9.16 |    3.176 |
| 0.80 |    37808.6 |   37.809 |    143.68 |   14.65 |    5.081 |
| 1.00 |    47260.8 |   47.261 |    179.60 |   18.31 |    6.352 |
| 1.20 |    56713.0 |   56.713 |    215.52 |   21.98 |    7.622 |
| 1.50 |    70891.2 |   70.891 |    269.40 |   27.47 |    9.528 |
| 2.00 |    94521.6 |   94.522 |    359.20 |   36.63 |   12.704 |

### Variante de Masa Objetivo: 5.0 kg
- Factor lineal $\lambda_L$: `1.0000` | Factor área $\lambda_A$: `1.0000`
- Área supuesta $A$: `0.007000` m² (70.00 cm²)
- Brazo supuesto $L$: `0.0480` m (48.00 mm)

| $C_{p,\text{dif}}$ [-] | $\Delta p$ [Pa] | $\Delta p$ [kPa] | Fuerza $F$ [N] | Fuerza [kgf] | Momento $M$ [N·m] |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0.10 |     4726.1 |    4.726 |     33.08 |    3.37 |    1.588 |
| 0.20 |     9452.2 |    9.452 |     66.17 |    6.75 |    3.176 |
| 0.50 |    23630.4 |   23.630 |    165.41 |   16.87 |    7.940 |
| 0.80 |    37808.6 |   37.809 |    264.66 |   26.99 |   12.704 |
| 1.00 |    47260.8 |   47.261 |    330.83 |   33.73 |   15.880 |
| 1.20 |    56713.0 |   56.713 |    396.99 |   40.48 |   19.056 |
| 1.50 |    70891.2 |   70.891 |    496.24 |   50.60 |   23.819 |
| 2.00 |    94521.6 |   94.522 |    661.65 |   67.47 |   31.759 |

### Variante de Masa Objetivo: 10.0 kg
- Factor lineal $\lambda_L$: `1.2599` | Factor área $\lambda_A$: `1.5874`
- Área supuesta $A$: `0.011112` m² (111.12 cm²)
- Brazo supuesto $L$: `0.0605` m (60.48 mm)

| $C_{p,\text{dif}}$ [-] | $\Delta p$ [Pa] | $\Delta p$ [kPa] | Fuerza $F$ [N] | Fuerza [kgf] | Momento $M$ [N·m] |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0.10 |     4726.1 |    4.726 |     52.52 |    5.36 |    3.176 |
| 0.20 |     9452.2 |    9.452 |    105.03 |   10.71 |    6.352 |
| 0.50 |    23630.4 |   23.630 |    262.58 |   26.78 |   15.880 |
| 0.80 |    37808.6 |   37.809 |    420.12 |   42.84 |   25.407 |
| 1.00 |    47260.8 |   47.261 |    525.15 |   53.55 |   31.759 |
| 1.20 |    56713.0 |   56.713 |    630.18 |   64.26 |   38.111 |
| 1.50 |    70891.2 |   70.891 |    787.73 |   80.33 |   47.639 |
| 2.00 |    94521.6 |   94.522 |   1050.31 |  107.10 |   63.519 |

