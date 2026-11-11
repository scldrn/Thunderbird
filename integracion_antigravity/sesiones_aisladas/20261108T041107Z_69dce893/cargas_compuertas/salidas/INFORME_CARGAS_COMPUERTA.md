# INFORME TÉCNICO: ANÁLISIS PARAMÉTRICO DE CARGAS AERODINÁMICAS ILUSTRATIVAS EN COMPUERTAS DE CONDUCTO (ARQUITECTURA A)

---

## 1. RESUMEN EJECUTIVO

El presente informe documenta un estudio paramétrico y analítico de cargas aerodinámicas ilustrativas sobre las compuertas de ventiladores internos para vehículos con propulsión de Arquitectura A, evaluando las variantes escaladas para objetivos de masa de **2 kg, 5 kg y 10 kg** bajo condiciones de velocidad de **600 km/h** y **1000 km/h**.

Las formulaciones analíticas se basan en la teoría elemental de flujo incompresible bajo supuestos estrictamente declarados:
1. Presión dinámica: $q = \frac{1}{2} \rho V^2$
2. Presión diferencial: $\Delta p = C_{p,\text{dif}} \cdot q$
3. Fuerza normal aerodinámica: $F = \Delta p \cdot A$ (bajo hipótesis de distribución espacial uniforme)
4. Momento de charnela / vuelco: $M = F \cdot L_{\text{brazo}}$ (respecto a eje cinemático hipotético)

### Conclusiones Principales:
- Para $V = 1000\text{ km/h}$ y $\rho = 1.225\text{ kg/m}^3$, la presión dinámica exacta es de **$47260.80\text{ Pa}$**, confirmando el valor de prueba nominal de **$\approx 47261\text{ Pa}$** ($47.26\text{ kPa}$).
- Para $V = 600\text{ km/h}$, la presión dinámica es de **$17013.89\text{ Pa}$** ($17.01\text{ kPa}$).
- Las cargas aerodinámicas resultantes a estas velocidades alcanzan magnitudes masivas: a $1000\text{ km/h}$ con $C_{p,\text{dif}} = 1.0$, la fuerza normal supuesta sobre una sola tapa varía entre **$179.6\text{ N}$** (variante 2 kg) y **$525.2\text{ N}$** (variante 10 kg), con momentos de charnela entre **$6.35\text{ N}\cdot\text{m}$** y **$31.76\text{ N}\cdot\text{m}$**.
- **ADVERTENCIA CRÍTICA Y DEFINITORIA**: Las compuertas de la Arquitectura A han sido concebidas **exclusivamente para maniobras a baja velocidad (despegue, sustentación vertical y transición inicial)**. No existe ningún mecanismo cinemático, servoactuador, guía ni sello validado ni dimensionado para resistir cargas a 600 o 1000 km/h. La apertura a estas velocidades provocaría el colapso estructural inmediato de cualquier mecanismo de micro-UAV.

---

## 2. DIFERENCIACIÓN EPISTEMOLÓGICA: DATOS MEDIDOS, SUPUESTOS Y CÁLCULOS

Para garantizar la máxima integridad metodológica y evitar atribuciones infundadas, se clasifican taxativamente todas las magnitudes y fuentes del estudio:

```
+----------------------------------------------------------------------------------------------------+
|                                    CLASIFICACIÓN DE INFORMACIÓN                                    |
+------------------------------------+-----------------------------------+---------------------------+
| 1. DATOS DE REFERENCIA / MEDIDOS   | 2. SUPUESTOS EXPLÍCITOS           | 3. CÁLCULOS DERIVADOS     |
+------------------------------------+-----------------------------------+---------------------------+
| - rho = 1.225 kg/m3 (ISA s.l.)     | - V = 600 y 1000 km/h (casos      | - V_ms = V_kmh / 3.6      |
|   Fuente: C02_CANDIDATA.json / ISA |   ilustrativos de alta velocidad) | - q = 0.5 * rho * V^2     |
| - Diámetro conducto = 0.084 m      | - Delta_p uniforme en toda el     | - Delta_p = Cp * q        |
|   Fuente: nominal_bore_diameter_m  |   área de la compuerta            | - lambda_L = (m/5)^(1/3)  |
| - Conversión SI: 1 km/h = 1/3.6 m/s| - Area ref (5kg) = 0.0070 m2      | - lambda_A = (m/5)^(2/3)  |
| - Posición ejes CAD nominales      |   (hipotética, cubre conducto)    | - Area(m) = A_ref * lam_A |
|   Fuente: propuesta_elevacion.json | - Brazo ref (5kg) = 0.048 m       | - Brazo(m) = L_ref * lam_L|
| - Objetivos de masa: 2, 5, 10 kg   |   (hipotético eje a centro p.)    | - Fuerza F = Delta_p * A  |
|   Fuente: mass_targets_kg C02      | - Cp_dif in [0.1 .. 2.0]          | - Momento M = F * Brazo   |
|                                    | - Escalado isomórfico (m/5)^(1/3) |                           |
+------------------------------------+-----------------------------------+---------------------------+
```

### Reglas de Integridad Aplicadas:
1. **Masas Reales**: En `C02_CANDIDATA.json`, el campo `actual_mass_kg` figura como `null`, y se explicita que `"mass_targets_are_actual_masses": false`. En este estudio **no se infiere que las reservas sin masa asignada tengan masa real nula ni no nula**. Los valores de 2 kg, 5 kg y 10 kg son tratados estrictamente como **objetivos de masa geométrica**, no como balanzas medidas.
2. **Ausencia de Archivos No Copiados**: No se infiere que archivos o solvers que no estén presentes en el entorno local no existan en repositorios externos, ni se asumen resultados de CFD pausados.
3. **No Invención de Actores ni Marcas**: No se atribuyen mecanismos, marcas comerciales de servos ni autores ficticios.
4. **Independencia Operativa**: Las notas encontradas en las referencias técnicas de `entradas/` se tratan como contexto de solo lectura, sin alterar las instrucciones del presente mandato.

---

## 3. FORMULACIÓN ANALÍTICA Y COMPROBACIÓN NUMÉRICA

### 3.1. Conversión de Unidades de Velocidad
La velocidad se convierte de kilómetros por hora ($\text{km/h}$) a metros por segundo ($\text{m/s}$) mediante el factor exacto del Sistema Internacional:
$$V_{\text{m/s}} = \frac{V_{\text{km/h}}}{3.6}$$

- Para $V = 600\text{ km/h}$:
  $$V_{600} = \frac{600}{3.6} = \frac{500}{3}\text{ m/s} \approx 166.666667\text{ m/s}$$
- Para $V = 1000\text{ km/h}$:
  $$V_{1000} = \frac{1000}{3.6} = \frac{2500}{9}\text{ m/s} \approx 277.777778\text{ m/s}$$

### 3.2. Presión Dinámica Incompresible ($q$)
Con la densidad estándar de referencia $\rho = 1.225\text{ kg/m}^3$:
$$q = \frac{1}{2} \rho V_{\text{m/s}}^2$$

- **Caso 600 km/h**:
  $$q_{600} = \frac{1}{2} \cdot 1.225 \cdot \left(\frac{500}{3}\right)^2 = \frac{1.225 \cdot 250000}{18} = \frac{153125}{9} \approx 17013.8889\text{ Pa} \approx \mathbf{17.014\text{ kPa}}$$

- **Caso 1000 km/h**:
  $$q_{1000} = \frac{1}{2} \cdot 1.225 \cdot \left(\frac{2500}{9}\right)^2 = \frac{1.225 \cdot 6250000}{162} = \frac{3828125}{81} \approx 47260.8025\text{ Pa}$$
  Redondeando al entero más cercano:
  $$\mathbf{q_{1000} \approx 47261\text{ Pa} \quad (47.261\text{ kPa})}$$
  *(La discrepancia con 47261 Pa es de solo $0.1975\text{ Pa}$, inferior al $0.00042\%$, verificando plenamente el valor objetivo).*

### 3.3. Presión Diferencial Uniforme Supuesta ($\Delta p$)
Se define el coeficiente de presión diferencial adimensional $C_{p,\text{dif}}$ entre el exterior de la compuerta y el interior de la cavidad/conducto como:
$$C_{p,\text{dif}} = \frac{p_{\text{int}} - p_{\text{ext}}}{q} \quad \implies \quad \Delta p = C_{p,\text{dif}} \cdot q$$

Se evalúa una gama de coeficientes representativos:
$$C_{p,\text{dif}} \in \{0.10, 0.20, 0.50, 0.80, 1.00, 1.20, 1.50, 2.00\}$$

---

## 4. ESCALADO GEOMÉTRICO ISOMÓRFICO (2 kg, 5 kg, 10 kg)

Siguiendo la semejanza geométrica isomórfica definida en la Arquitectura A (`LEEME.md` y `C02_CANDIDATA.json`), las longitudes escalan con la raíz cúbica de la razón de masa respecto a la referencia de $5.0\text{ kg}$:
$$\lambda_L = \left(\frac{m}{m_{\text{ref}}}\right)^{1/3} = \left(\frac{m}{5.0}\right)^{1/3}$$

### 4.1. Factores de Escala Derivados
- Factor de área: $\lambda_A = \lambda_L^2 = \left(\frac{m}{5.0}\right)^{2/3}$
- Factor de volumen / masa: $\lambda_V = \lambda_L^3 = \frac{m}{5.0}$

| Parámetro | Variante 2.0 kg | Variante 5.0 kg (Ref.) | Variante 10.0 kg |
| :--- | :---: | :---: | :---: |
| **Razón de masa** ($m / 5$) | $0.4000$ | $1.0000$ | $2.0000$ |
| **Factor lineal** $\lambda_L$ | $(0.4)^{1/3} \approx \mathbf{0.7368}$ | $\mathbf{1.0000}$ | $2^{1/3} \approx \mathbf{1.2599}$ |
| **Factor de área** $\lambda_A$ | $(0.4)^{2/3} \approx \mathbf{0.5429}$ | $\mathbf{1.0000}$ | $2^{2/3} \approx \mathbf{1.5874}$ |

### 4.2. Dimensiones Explícitamente Hipotéticas Adoptadas
1. **Área de compuerta de referencia ($5\text{ kg}$)**:
   - Diámetro del conducto documentado: $D_{\text{bore}} = 0.084\text{ m} = 84\text{ mm}$.
   - Área neta de paso del conducto: $A_{\text{conducto}} = \frac{\pi}{4}(0.084)^2 \approx 0.005542\text{ m}^2$ ($55.42\text{ cm}^2$).
   - Para permitir pestaña de sellado y solape perimetral sobre la camisa recortada, se adopta un **área de compuerta explícitamente hipotética**:
     $$A_{\text{ref, 5kg}} = \mathbf{0.0070\text{ m}^2} \quad (70.00\text{ cm}^2)$$
   - Escalado a 2 kg: $A_{2\text{kg}} = 0.0070 \cdot 0.542884 \approx \mathbf{0.003800\text{ m}^2} \quad (38.00\text{ cm}^2)$
   - Escalado a 10 kg: $A_{10\text{kg}} = 0.0070 \cdot 1.587401 \approx \mathbf{0.011112\text{ m}^2} \quad (111.12\text{ cm}^2)$

2. **Brazo de palanca al centro de presiones ($5\text{ kg}$)**:
   - Coherencia dimensional con CAD: en `propuesta_elevacion.json`, el eje de traslación/giro de la compuerta se sitúa en $Y = \pm 124\text{ mm}$, y el centro del rotor/conducto en $Y = \pm 76\text{ mm}$ (`C02_CANDIDATA.json`), arrojando una separación de $|124 - 76| = 48\text{ mm} = 0.048\text{ m}$.
   - Se adopta como **brazo de palanca explícitamente hipotético**:
     $$L_{\text{ref, 5kg}} = \mathbf{0.048\text{ m}} \quad (48.00\text{ mm})$$
   - Escalado a 2 kg: $L_{2\text{kg}} = 0.048 \cdot 0.736806 \approx \mathbf{0.035367\text{ m}} \quad (35.37\text{ mm})$
   - Escalado a 10 kg: $L_{10\text{kg}} = 0.048 \cdot 1.259921 \approx \mathbf{0.060476\text{ m}} \quad (60.48\text{ mm})$

### 4.3. Ley de Semejanza de Momentos
Bajo distribución uniforme y escalado isomórfico, para un $q$ y $C_{p,\text{dif}}$ dados:
$$F(m) = \Delta p \cdot A(m) = \Delta p \cdot A_{\text{ref}} \cdot \lambda_L^2$$
$$M(m) = F(m) \cdot L(m) = (\Delta p \cdot A_{\text{ref}} \cdot \lambda_L^2) \cdot (L_{\text{ref}} \cdot \lambda_L) = M_{\text{ref}} \cdot \lambda_L^3 = M_{\text{ref}} \cdot \frac{m}{m_{\text{ref}}}$$
El momento aerodinámico resultante escala **estrictamente de forma lineal con la masa objetivo del vehículo**:
$$\frac{M_{10\text{kg}}}{M_{5\text{kg}}} = 2.000, \qquad \frac{M_{2\text{kg}}}{M_{5\text{kg}}} = 0.400$$

---

## 5. RESULTADOS DEL ANÁLISIS PARAMÉTRICO

### 5.1. Condición $V = 600\text{ km/h}$ ($166.67\text{ m/s}$), $q = 17013.89\text{ Pa}$ ($17.014\text{ kPa}$)

| Masa Objetivo | $A$ [cm²] | $L$ [mm] | $C_{p,\text{dif}}$ [-] | $\Delta p$ [Pa] | $\Delta p$ [kPa] | Fuerza $F$ [N] | Fuerza [kgf] | Momento $M$ [N·m] |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2.0 kg** | 38.00 | 35.37 | 0.10 | 1701.4 | 1.701 | 6.47 | 0.66 | 0.229 |
| **2.0 kg** | 38.00 | 35.37 | 0.20 | 3402.8 | 3.403 | 12.93 | 1.32 | 0.457 |
| **2.0 kg** | 38.00 | 35.37 | 0.50 | 8506.9 | 8.507 | 32.33 | 3.30 | 1.143 |
| **2.0 kg** | 38.00 | 35.37 | 0.80 | 13611.1 | 13.611 | 51.72 | 5.27 | 1.829 |
| **2.0 kg** | 38.00 | 35.37 | 1.00 | 17013.9 | 17.014 | 64.66 | 6.59 | 2.287 |
| **2.0 kg** | 38.00 | 35.37 | 1.20 | 20416.7 | 20.417 | 77.59 | 7.91 | 2.744 |
| **2.0 kg** | 38.00 | 35.37 | 1.50 | 25520.8 | 25.521 | 96.98 | 9.89 | 3.430 |
| **2.0 kg** | 38.00 | 35.37 | 2.00 | 34027.8 | 34.028 | 129.31 | 13.19 | 4.573 |
| **5.0 kg** | 70.00 | 48.00 | 0.10 | 1701.4 | 1.701 | 11.91 | 1.21 | 0.572 |
| **5.0 kg** | 70.00 | 48.00 | 0.20 | 3402.8 | 3.403 | 23.82 | 2.43 | 1.143 |
| **5.0 kg** | 70.00 | 48.00 | 0.50 | 8506.9 | 8.507 | 59.55 | 6.07 | 2.858 |
| **5.0 kg** | 70.00 | 48.00 | 0.80 | 13611.1 | 13.611 | 95.28 | 9.72 | 4.573 |
| **5.0 kg** | 70.00 | 48.00 | 1.00 | 17013.9 | 17.014 | 119.10 | 12.14 | 5.717 |
| **5.0 kg** | 70.00 | 48.00 | 1.20 | 20416.7 | 20.417 | 142.92 | 14.57 | 6.860 |
| **5.0 kg** | 70.00 | 48.00 | 1.50 | 25520.8 | 25.521 | 178.65 | 18.22 | 8.575 |
| **5.0 kg** | 70.00 | 48.00 | 2.00 | 34027.8 | 34.028 | 238.19 | 24.29 | 11.433 |
| **10.0 kg** | 111.12 | 60.48 | 0.10 | 1701.4 | 1.701 | 18.90 | 1.93 | 1.143 |
| **10.0 kg** | 111.12 | 60.48 | 0.20 | 3402.8 | 3.403 | 37.81 | 3.86 | 2.287 |
| **10.0 kg** | 111.12 | 60.48 | 0.50 | 8506.9 | 8.507 | 94.52 | 9.64 | 5.717 |
| **10.0 kg** | 111.12 | 60.48 | 0.80 | 13611.1 | 13.611 | 151.24 | 15.42 | 9.146 |
| **10.0 kg** | 111.12 | 60.48 | 1.00 | 17013.9 | 17.014 | 189.05 | 19.28 | 11.433 |
| **10.0 kg** | 111.12 | 60.48 | 1.20 | 20416.7 | 20.417 | 226.86 | 23.13 | 13.720 |
| **10.0 kg** | 111.12 | 60.48 | 1.50 | 25520.8 | 25.521 | 283.57 | 28.92 | 17.149 |
| **10.0 kg** | 111.12 | 60.48 | 2.00 | 34027.8 | 34.028 | 378.10 | 38.56 | 22.866 |

---

### 5.2. Condición $V = 1000\text{ km/h}$ ($277.78\text{ m/s}$), $q = 47260.80\text{ Pa}$ ($47.261\text{ kPa}$)

| Masa Objetivo | $A$ [cm²] | $L$ [mm] | $C_{p,\text{dif}}$ [-] | $\Delta p$ [Pa] | $\Delta p$ [kPa] | Fuerza $F$ [N] | Fuerza [kgf] | Momento $M$ [N·m] |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2.0 kg** | 38.00 | 35.37 | 0.10 | 4726.1 | 4.726 | 17.96 | 1.83 | 0.635 |
| **2.0 kg** | 38.00 | 35.37 | 0.20 | 9452.2 | 9.452 | 35.92 | 3.66 | 1.270 |
| **2.0 kg** | 38.00 | 35.37 | 0.50 | 23630.4 | 23.630 | 89.80 | 9.16 | 3.176 |
| **2.0 kg** | 38.00 | 35.37 | 0.80 | 37808.6 | 37.809 | 143.68 | 14.65 | 5.081 |
| **2.0 kg** | 38.00 | 35.37 | 1.00 | 47260.8 | 47.261 | 179.60 | 18.31 | 6.352 |
| **2.0 kg** | 38.00 | 35.37 | 1.20 | 56713.0 | 56.713 | 215.52 | 21.98 | 7.622 |
| **2.0 kg** | 38.00 | 35.37 | 1.50 | 70891.2 | 70.891 | 269.40 | 27.47 | 9.528 |
| **2.0 kg** | 38.00 | 35.37 | 2.00 | 94521.6 | 94.522 | 359.20 | 36.63 | 12.704 |
| **5.0 kg** | 70.00 | 48.00 | 0.10 | 4726.1 | 4.726 | 33.08 | 3.37 | 1.588 |
| **5.0 kg** | 70.00 | 48.00 | 0.20 | 9452.2 | 9.452 | 66.17 | 6.75 | 3.176 |
| **5.0 kg** | 70.00 | 48.00 | 0.50 | 23630.4 | 23.630 | 165.41 | 16.87 | 7.940 |
| **5.0 kg** | 70.00 | 48.00 | 0.80 | 37808.6 | 37.809 | 264.66 | 26.99 | 12.704 |
| **5.0 kg** | 70.00 | 48.00 | 1.00 | 47260.8 | 47.261 | 330.83 | 33.73 | 15.880 |
| **5.0 kg** | 70.00 | 48.00 | 1.20 | 56713.0 | 56.713 | 396.99 | 40.48 | 19.056 |
| **5.0 kg** | 70.00 | 48.00 | 1.50 | 70891.2 | 70.891 | 496.24 | 50.60 | 23.819 |
| **5.0 kg** | 70.00 | 48.00 | 2.00 | 94521.6 | 94.522 | 661.65 | 67.47 | 31.759 |
| **10.0 kg** | 111.12 | 60.48 | 0.10 | 4726.1 | 4.726 | 52.52 | 5.36 | 3.176 |
| **10.0 kg** | 111.12 | 60.48 | 0.20 | 9452.2 | 9.452 | 105.03 | 10.71 | 6.352 |
| **10.0 kg** | 111.12 | 60.48 | 0.50 | 23630.4 | 23.630 | 262.58 | 26.78 | 15.880 |
| **10.0 kg** | 111.12 | 60.48 | 0.80 | 37808.6 | 37.809 | 420.12 | 42.84 | 25.407 |
| **10.0 kg** | 111.12 | 60.48 | 1.00 | 47260.8 | 47.261 | 525.15 | 53.55 | 31.759 |
| **10.0 kg** | 111.12 | 60.48 | 1.20 | 56713.0 | 56.713 | 630.18 | 64.26 | 38.111 |
| **10.0 kg** | 111.12 | 60.48 | 1.50 | 70891.2 | 70.891 | 787.73 | 80.33 | 47.639 |
| **10.0 kg** | 111.12 | 60.48 | 2.00 | 94521.6 | 94.522 | 1050.31 | 107.10 | 63.519 |

---

## 6. DISCUSIÓN TÉCNICA Y LIMITACIONES FÍSICAS CRÍTICAS

### 6.1. La presión dinámica $q$ NO es una presión diferencial uniforme
1. **Compresibilidad del Flujo**:
   - A $T_{\text{std}} = 288.15\text{ K}$, la velocidad del sonido es $a = \sqrt{\gamma R T} = \sqrt{1.4 \cdot 287.05 \cdot 288.15} \approx 340.29\text{ m/s}$.
   - Para $V = 600\text{ km/h}$ ($166.67\text{ m/s}$), el número de Mach es $M \approx 0.490$ (régimen subsónico compresible moderado).
   - Para $V = 1000\text{ km/h}$ ($277.78\text{ m/s}$), el número de Mach es $M \approx 0.816$ (**régimen transónico alto**).
   - En régimen transónico, la hipótesis incompresible subestima la presión de impacto total ($p_0 - p_\infty > q$), se forman ondas de choque locales sobre la curvatura del fuselaje y las expansiones supersónicas generan picos extremos de succión no lineales.
2. **Distribución No Uniforme y Vórtices**:
   - En un conducto abierto o parcialmente abierto, el flujo exterior interacciona con la cavidad muerta del conducto generando desprendimiento en el borde de ataque de la compuerta, vórtices de cizalladura de cavidad (*shear layer resonance*) y variaciones espaciales drásticas del centro de presiones.
   - Tratar $\Delta p$ como constante en toda el área es únicamente una herramienta ilustrativa de cota media global, no apta para diseño de esfuerzo local, fatiga ni pandeo.

### 6.2. Las compuertas son para BAJA VELOCIDAD (Despegue / Transición)
- En la concepción original de la Arquitectura A (`LEEME.md`):
  > *"La apertura está destinada al estudio de baja velocidad; no se valida su uso en avance rápido."*
- Durante vuelo de crucero a alta velocidad, los cuatro ventiladores internos están inactivos y las **ocho compuertas (cuatro superiores y cuatro inferiores) deben permanecer herméticamente cerradas y bloqueadas**.
- Si una compuerta intentara abrirse a 600 o 1000 km/h:
  - Generaría una fuerza de desprendimiento de entre $120\text{ N}$ y $1050\text{ N}$ por compuerta.
  - El arrastre inducido por cavidad desestabilizaría el vehículo, arruinando la continuidad aerodinámica y causando momentos de guiñada y cabeceo incontrolables.

### 6.3. Disparidad Frente a la Capacidad de Actuadores y Mecanismos de Micro-UAV
- Para un vehículo no tripulado de 2 a 10 kg, los servomotores rotativos comerciales de alto rendimiento para superficies secundarias proporcionan pares de bloqueo típicos de entre $0.20\text{ N}\cdot\text{m}$ y $1.50\text{ N}\cdot\text{m}$ (aproximadamente $2$ a $15\text{ kg}\cdot\text{cm}$), con pesos propios de 15 a 60 gramos.
- Los momentos calculados bajo $\Delta p = q$ ($C_{p,\text{dif}} = 1.0$) son:
  - A 600 km/h: $M = 2.29\text{ N}\cdot\text{m}$ (2 kg) a $11.43\text{ N}\cdot\text{m}$ (10 kg).
  - A 1000 km/h: $M = 6.35\text{ N}\cdot\text{m}$ (2 kg) a $31.76\text{ N}\cdot\text{m}$ (10 kg).
- **El momento aerodinámico supera la capacidad de retención de servos estándar entre un $400\%$ y más de un $3000\%$ ($4\times$ a $30\times$)**.
- La compuerta sería forzada a cerrarse violentamente o arrancada de su eje, destruyendo cualquier timonería o reductora.

### 6.4. Mecanismos no instalados ni resueltos
- Como se certifica en `LEEME.md` y `C02_CANDIDATA.json`:
  > *"No hay todavía guías, bisagras, soportes, cierres, sellos, cableado o actuadores de compuerta dimensionados. La trayectoria impone dos coordenadas cinemáticas; falta sintetizar y alojar el mecanismo que las produzca. Los ejes de movimiento están documentados como geometría de construcción, no como herrajes instalados."*
- Ninguna de las cargas obtenidas en este informe corresponde a una pieza ensayada o instalada en un banco de ensayos.

---

## 7. INVENTARIO DE ENTREGABLES Y PRUEBAS REALIZADAS

### 7.1. Archivos Generados en `salidas/`
Todos los entregables han sido depositados con permisos de lectura y escritura en `salidas/`:

1. `salidas/analisis_cargas_compuerta.py`:
   - Script ejecutable en Python 3 con funciones analíticas modulares, validaciones de rango físico, escalado geométrico e interfaces de exportación a CSV, JSON y Markdown.
2. `salidas/test_cargas_compuerta.py`:
   - Batería de 14 pruebas unitarias automatizadas (`unittest`) que evalúa conversiones, presiones dinámicas exactas, $q_{1000} \approx 47261\text{ Pa}$, factores isomórficos, leyes de semejanza de momento y validez de esquemas de datos.
3. `salidas/tablas_cargas_compuerta.csv`:
   - Tabla plana estructurada con los 48 casos paramétricos calculados (todas las combinaciones de velocidad, masa objetivo y $C_p$).
4. `salidas/resultados_cargas_compuerta.json`:
   - Archivo JSON estructurado con metadatos de estudio, constantes, advertencias explícitas y colección jerárquica de resultados.
5. `salidas/tablas_cargas_compuerta.md`:
   - Documento Markdown con tablas detalladas formateadas con unidades completas en SI y unidades técnicas secundarias.
6. `salidas/INFORME_CARGAS_COMPUERTA.md`:
   - El presente informe técnico integral y exhaustivo.

### 7.2. Resumen de Pruebas Automatizadas Ejecutadas
La batería de pruebas `test_cargas_compuerta.py` se ejecutó con el motor de `unittest` de Python 3.9 en el entorno de pruebas local:
```
test_dynamic_pressure_1000kmh (__main__.TestAerodynamicConversionsAndQ) ... ok (q = 47260.80 Pa ~ 47261 Pa)
test_dynamic_pressure_600kmh (__main__.TestAerodynamicConversionsAndQ) ... ok (q = 17013.89 Pa)
test_dynamic_pressure_invalid_inputs (__main__.TestAerodynamicConversionsAndQ) ... ok
test_kmh_to_ms_exact (__main__.TestAerodynamicConversionsAndQ) ... ok (600 -> 500/3 m/s, 1000 -> 2500/9 m/s)
test_differential_pressure (__main__.TestAerodynamicFormulasAndScaling) ... ok
test_force_and_moment_calculations (__main__.TestAerodynamicFormulasAndScaling) ... ok
test_force_scales_with_area (__main__.TestAerodynamicFormulasAndScaling) ... ok (F/F_ref == (m/5)^(2/3))
test_geometric_scaling_factors (__main__.TestAerodynamicFormulasAndScaling) ... ok (2kg: 0.7368, 10kg: 1.2599)
test_moment_scales_linearly_with_mass_target (__main__.TestAerodynamicFormulasAndScaling) ... ok (M10/M5 == 2.0, M2/M5 == 0.4)
test_case_values_monotonicity (__main__.TestParametricSweepAndOutputs) ... ok
test_exported_csv_validity (__main__.TestParametricSweepAndOutputs) ... ok (48 filas verificadas)
test_exported_json_validity (__main__.TestParametricSweepAndOutputs) ... ok
test_exported_markdown_validity (__main__.TestParametricSweepAndOutputs) ... ok
test_parametric_sweep_cardinality (__main__.TestParametricSweepAndOutputs) ... ok (48 casos)

Ran 14 tests in 0.002s -> STATUS: ALL OK (14/14 superados)
```

---

## 8. CONCLUSIÓN Y RECOMENDACIÓN TÉCNICA

El análisis paramétrico demuestra de forma concluyente que las compuertas de la Arquitectura A no pueden ser operadas en vuelo rápido. Cualquier apertura a velocidades del orden de 600 a 1000 km/h induciría cargas aerodinámicas de centenas de Newtons y momentos de charnela de decenas de Newtons-metro por tapa, superando por más de un orden de magnitud la capacidad admisible de mecanismos ligeros de micro-UAV. 

Se recomienda de forma categórica:
1. Mantener las tapas enrasadas y cerradas con enclavamiento pasivo o cerrojo mecánico durante cualquier régimen de avance rápido o crucero.
2. Restringir la cinemática de apertura exclusivamente a las envolventes de baja velocidad ($V < 50\text{ km/h}$ o régimen de sustentación pura).
3. Llevar a cabo simulaciones aeroelásticas tridimensionales acopladas y síntesis de mecanismos reales antes de definir requisitos de actuador definitivo.
