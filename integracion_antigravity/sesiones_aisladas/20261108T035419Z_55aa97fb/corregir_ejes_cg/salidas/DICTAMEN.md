# DICTAMEN TÉCNICO: CONTRASTE DE SIGNOS Y CONVENCIONES CAD/FLU, QUIRALIDAD Y EVALUACIÓN DE IMPACTO EN EL MODELO SIMÉTRICO DE EQUILIBRIO DE CG (CONFIGURACIÓN C02)

**Fecha de dictamen:** 7 de noviembre de 2026  
**Entorno de ejecución:** Espacio aislado `corregir_ejes_cg/` en sandbox local  
**Referencias analizadas:**
- `entradas/investigacion-aeronautica/configuraciones/C02_CANDIDATA.json` (Configuración oficial C02)
- `entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/cg_bidimensional/salidas/INFORME_EQUILIBRIO_CG.md` (Informe de cálculo CG auditado)
- `entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T034228Z_e90078d2/revisar_cg/salidas/REVISION.md` (Auditoría previa)

---

## 1. Resumen Ejecutivo y Dictamen Pericial

A partir del contraste algebraico, cinemático y geométrico entre la definición oficial de la arquitectura C02 (`C02_CANDIDATA.json`) y el informe de cálculo estático de centro de gravedad (`INFORME_EQUILIBRIO_CG.md`), se dictamina de manera formal e incontrovertible lo siguiente:

1. **Orientación del Eje CAD $+x$:**  
   Cuando el sistema de vuelo aeronáutico FLU tiene $+x_{\text{FLU}}$ orientado hacia adelante (proa / nariz), el eje **CAD $+x$ apunta formalmente hacia la COLA** (popa / aft / rear), y **CAD $-x$ apunta hacia la NARIZ** (forward).  
   *Dictamen:* En este eje, la descripción textual del informe de CG coincide plenamente con la matriz de configuración $R_{\text{flight\_from\_CAD}}$.

2. **Orientación del Eje CAD $+y$:**  
   Cuando el sistema de vuelo aeronáutico FLU tiene $+y_{\text{FLU}}$ orientado hacia la izquierda (babor / port), el eje **CAD $+y$ corresponde formalmente a la DERECHA** (estribor / starboard), y **CAD $-y$ corresponde a la IZQUIERDA** (babor).  
   *Dictamen:* En este eje existe una **discrepancia y contradicción interna flagrante en el informe de CG**, el cual afirmó erróneamente que CAD $+y$ estaba "orientado hacia la izquierda (babor)".

3. **Quiralidad y Regla de la Mano Derecha (Right-Hand Rule):**  
   Dado que la matriz $R_{\text{flight\_from\_CAD}} = \operatorname{diag}(-1, -1, 1)$ tiene determinante $\det(R) = +1.0$, representa una rotación espacial propia de $180^\circ$ alrededor del eje vertical $z$. La transformación preserva estrictamente la quiralidad dextrógira del triedro ($\hat{x} \times \hat{y} = \hat{z}$). Un sistema con $+x = \text{cola}$, $+y = \text{izquierda}$ y $+z = \text{arriba}$ violaría la regla de la mano derecha (sería levógiro / zurdo, con $\hat{x} \times \hat{y} = -\hat{z}$).

4. **Naturaleza del Error:**  
   Se clasifica como un **ERROR DE DOCUMENTACIÓN, NOMENCLATURA Y ASIGNACIÓN SEMÁNTICA DE ETIQUETAS**.

5. **Impacto en Magnitudes del Modelo Simétrico:**  
   Debido a la estricta simetría bilateral geométrica y motriz de la plataforma C02 ($L_x = 0.160\text{ m}$, $L_y = 0.076\text{ m}$, propulsores idénticos en capacidad $0 \le f_i \le F_{\text{máx}}$), el error **NO altera las magnitudes cuantitativas** de:
   - El peso total $W$,
   - La envolvente bidimensional admisible (octógono de sustentación),
   - El número de posiciones factibles en mallas simétricas (291 de 945 para $F_{\text{máx}} = 20.58\text{ N}$; 473 de 945 para $F_{\text{máx}} = 25.00\text{ N}$),
   - La capacidad máxima vertical analítica $F_{z,\max}(x_{cg}, y_{cg})$,
   - La holgura analítica de factibilidad $\Delta f_4$,
   - Ni las fuerzas individuales calculadas en la condición nominal simétrica ($y_{cg} = 0$, donde $f_1 = f_2$ y $f_3 = f_4$).  
   En posiciones asimétricas ($y_{cg} \ne 0$), el conjunto de magnitudes numéricas de las fuerzas calculadas es matemáticamente exacto para las coordenadas evaluadas, pero las etiquetas laterales de los motores y bordes están permutadas respecto a la posición física en el vehículo de vuelo ($f_1 \leftrightarrow f_2$ y $f_3 \leftrightarrow f_4$).

---

## 2. Clasificación Metodológica de Datos

Siguiendo las directrices de trazabilidad técnica, no se asume ninguna masa nula o no nula para reservas sin masa asignada, ni se infiere la no existencia de archivos no copiados. Los datos se discriminan rigurosamente:

| Categoría | Parámetro / Entidad | Símbolo | Valor y Unidades | Fuente / Justificación |
| :--- | :--- | :---: | :---: | :--- |
| **Datos Medidos** | *Ninguno* | — | — | **No existen datos medidos.** En `C02_CANDIDATA.json` consta formalmente: `actual_mass_kg: null`, `actual_CG_m: null`, `actual_inertia_kgm2: null`, `installed_map_available: false`. La plataforma C02 es un modelo conceptual. |
| **Supuestos de Referencia** | Matriz de rotación cuerpo de vuelo desde CAD | $R_{\text{flight\_from\_CAD}}$ | $\begin{bmatrix} -1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$ (Adimensional) | `C02_CANDIDATA.json`: campo `flight_body_frame.R_flight_from_CAD`. |
| **Supuestos de Referencia** | Definición de marco de vuelo FLU | — | $+x$: adelante / nariz<br>$+y$: izquierda<br>$+z$: arriba | `C02_CANDIDATA.json`: campo `flight_body_frame`. |
| **Supuestos de Referencia** | Definición de marco CAD | — | $+x$: nariz en $-x$<br>$+y$: lateral<br>$+z$: arriba | `C02_CANDIDATA.json`: campo `coordinate_frame`. |
| **Supuestos de Referencia** | Semibrazo longitudinal nominal | $L_x$ | $0.160\text{ m}$ ($160\text{ mm}$) | `C02_CANDIDATA.json`: `fan_reference.centres_xy_m` ($x = \pm 0.160\text{ m}$). |
| **Supuestos de Referencia** | Semibrazo lateral nominal | $L_y$ | $0.076\text{ m}$ ($76\text{ mm}$) | `C02_CANDIDATA.json`: `fan_reference.centres_xy_m` ($y = \pm 0.076\text{ m}$). |
| **Supuestos de Referencia** | Masa de integración objetivo | $m$ | $5.0\text{ kg}$ | `C02_CANDIDATA.json`: `integration_reference_mass_target_kg: 5`. |
| **Supuestos de Referencia** | Aceleración de la gravedad estándar | $g$ | $9.80665\text{ m/s}^2$ | `C02_CANDIDATA.json`: `operating_reference.g_m_s2`. |
| **Supuestos de Referencia** | Empuje máximo base (caso ideal no calificado) | $F_{\text{máx}, 1}$ | $20.58\text{ N}$ | `INFORME_EQUILIBRIO_CG.md` e `INFORME-VERTICAL.md`. |
| **Supuestos de Referencia** | Empuje máximo dimensionado | $F_{\text{máx}, 2}$ | $25.00\text{ N}$ | `INFORME_EQUILIBRIO_CG.md`. |
| **Cálculos** | Determinante de la matriz de transformación | $\det(R)$ | $+1.0$ (Escalar) | Cálculo analítico: $\det(\operatorname{diag}(-1, -1, 1)) = (-1)(-1)(1) = +1$. |
| **Cálculos** | Vectores unitarios CAD en base FLU | $\mathbf{e}_{x,\text{CAD}}, \mathbf{e}_{y,\text{CAD}}, \mathbf{e}_{z,\text{CAD}}$ | $[-1, 0, 0]^T, [0, -1, 0]^T, [0, 0, 1]^T$ | Producto matricial $\mathbf{v}_{\text{FLU}} = R\,\mathbf{v}_{\text{CAD}}$. |
| **Cálculos** | Coordenadas FLU de los centros de ventilador | $\mathbf{r}_{i,\text{FLU}}$ | M1: $(+0.160, +0.076)\text{ m}$<br>M2: $(+0.160, -0.076)\text{ m}$<br>M3: $(-0.160, +0.076)\text{ m}$<br>M4: $(-0.160, -0.076)\text{ m}$ | Transformación $\mathbf{r}_{\text{FLU}} = R\,\mathbf{r}_{\text{CAD}}$. |
| **Cálculos** | Peso estático de referencia | $W$ | $49.03325\text{ N}$ | $W = m \cdot g = 5.0\text{ kg} \times 9.80665\text{ m/s}^2$. |
| **Cálculos** | Holgura y capacidad máxima analítica | $\Delta f_4, F_{z,\max}$ | $[\text{N}]$ | Ecuaciones analíticas de equilibrio 2D. |

---

## 3. Contraste de Signos: Definición Canónica vs. Informe de CG

### 3.1 Especificación Canónica en la Configuración C02

En el archivo fuente canónico `C02_CANDIDATA.json` se definen dos marcos de referencia y su matriz de enlace:

```json
  "coordinate_frame": {
    "x": "CAD longitudinal, nose at negative x",
    "y": "CAD lateral",
    "z": "up"
  },
  "flight_body_frame": {
    "name": "FLU",
    "x": "forward towards nose",
    "y": "left",
    "z": "up",
    "R_flight_from_CAD": [
      [-1,  0,  0],
      [ 0, -1,  0],
      [ 0,  0,  1]
    ],
    "rule": "Transform vectors, CG and inertia consistently; apply CAD-to-FLU before flight attitude in visualization"
  }
```

La relación vectorial de cambio de base entre un punto expresado en coordenadas CAD ($\mathbf{r}_{\text{CAD}}$) y en coordenadas de cuerpo de vuelo FLU ($\mathbf{r}_{\text{FLU}}$) es:
$$\mathbf{r}_{\text{FLU}} = R_{\text{flight\_from\_CAD}}\,\mathbf{r}_{\text{CAD}}$$

Dado que $R$ es una matriz diagonal ortonormal y simétrica:
$$R^{-1} = R^T = R = \begin{bmatrix} -1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
la transformación inversa es idéntica:
$$\mathbf{r}_{\text{CAD}} = R_{\text{flight\_from\_CAD}}\,\mathbf{r}_{\text{FLU}}$$

Desglosando en componentes escalares:
$$x_{\text{FLU}} = - x_{\text{CAD}} \iff x_{\text{CAD}} = - x_{\text{FLU}}$$
$$y_{\text{FLU}} = - y_{\text{CAD}} \iff y_{\text{CAD}} = - y_{\text{FLU}}$$
$$z_{\text{FLU}} = + z_{\text{CAD}} \iff z_{\text{CAD}} = + z_{\text{FLU}}$$

### 3.2 Identificación Analítica de los Ejes CAD

#### A. Eje Longitudinal ($x$): ¿Nariz o Cola?
- **Definición en FLU:** Por definición del estándar aeronáutico FLU, $+x_{\text{FLU}}$ apunta hacia **adelante** (proa / nariz), por lo que $x_{\text{FLU}} > 0$ es la región delantera.
- **Relación con CAD:** $x_{\text{CAD}} = - x_{\text{FLU}}$.
  - Para un punto situado hacia la nariz ($x_{\text{FLU}} > 0$): $x_{\text{CAD}} < 0$. La nariz se ubica en $x_{\text{CAD}}$ negativo.
  - Para un punto situado hacia la cola ($x_{\text{FLU}} < 0$): $x_{\text{CAD}} > 0$. La cola se ubica en $x_{\text{CAD}}$ positivo.
- **Conclusión sobre $+x$:**  
  El vector unitario CAD $+x$ apunta hacia la **COLA** (popa / aft / rear).

#### B. Eje Lateral ($y$): ¿Derecha o Izquierda?
- **Definición en FLU:** Por definición del estándar aeronáutico FLU, $+y_{\text{FLU}}$ apunta hacia la **izquierda** (babor / port), por lo que $y_{\text{FLU}} > 0$ es la semisección izquierda y $y_{\text{FLU}} < 0$ es la semisección derecha (estribor / starboard).
- **Relación con CAD:** $y_{\text{CAD}} = - y_{\text{FLU}}$.
  - Para un punto situado a la izquierda ($y_{\text{FLU}} > 0$): $y_{\text{CAD}} = - y_{\text{FLU}} < 0$. La izquierda corresponde a $y_{\text{CAD}}$ negativo.
  - Para un punto situado a la derecha ($y_{\text{FLU}} < 0$): $y_{\text{CAD}} = - y_{\text{FLU}} > 0$. La derecha corresponde a $y_{\text{CAD}}$ positivo.
- **Conclusión sobre $+y$:**  
  El vector unitario CAD $+y$ corresponde a la **DERECHA** (estribor / starboard), y CAD $-y$ corresponde a la **IZQUIERDA** (babor / port).

### 3.3 Demostración Formal de Quiralidad (Regla de la Mano Derecha)

Un sistema de coordenadas cartesiano tridimensional en ingeniería y física aeronáutica debe ser **dextrógiro** (mano derecha), satisfaciendo:
$$\mathbf{e}_x \times \mathbf{e}_y = \mathbf{e}_z$$

1. **En el sistema de vuelo FLU:**
   $$\hat{x}_{\text{adelante}} \times \hat{y}_{\text{izquierda}} = \hat{z}_{\text{arriba}}$$
   Se cumple exactamente ($\mathbf{i} \times \mathbf{j} = \mathbf{k}$).

2. **Propiedad de la rotación $R$:**
   $$\det(R) = (-1) \cdot (-1) \cdot (1) = +1.0$$
   Al ser el determinante estrictamente $+1.0$ (y no $-1.0$), la matriz $R$ pertenece al grupo ortogonal especial $SO(3)$. Esto demuestra rigurosamente que la transformación es una **rotación física rígida de $180^\circ$ alrededor del eje $z$ vertical**, la cual **conserva la quiralidad dextrógira**.

3. **Comprobación en el sistema CAD:**
   Con $\hat{x}_{\text{CAD}} = \text{Cola}$ y $\hat{z}_{\text{CAD}} = \text{Arriba}$:
   $$\hat{x}_{\text{CAD}} \times \hat{y}_{\text{CAD}} = \hat{z}_{\text{CAD}} \iff \text{Cola} \times \hat{y}_{\text{CAD}} = \text{Arriba}$$
   Aplicando la regla de la mano derecha (dedos apuntando a la cola / popa, rotando hacia el eje lateral para que el pulgar apunte hacia arriba):
   $$\text{Cola} \times \text{Derecha} = \text{Arriba}$$
   $$\text{Cola} \times \text{Izquierda} = \text{Abajo} \quad (\text{Levógiro / Inadmisible})$$
   Por consiguiente, la única orientación matemáticamente compatible con un marco CAD dextrógiro y consistente con $\det(R) = +1$ es que **CAD $+y$ apunte a la DERECHA**.

---

## 4. Análisis Crítico del Texto en `INFORME_EQUILIBRIO_CG.md`

### 4.1 La Contradicción Interna del Informe

En la Sección 1.1 de `INFORME_EQUILIBRIO_CG.md` (y reproducido acríticamente en la Sección 2.1 de `REVISION.md`), el autor escribió textualmente:

> *"Sistema de coordenadas CAD oficial:*  
> *- Eje +x: Longitudinal orientado hacia la cola (nariz en -x, cola en +x).*  
> *- Eje +y: Lateral orientado hacia la izquierda (babor).*  
> *- Eje +z: Vertical orientado hacia arriba.*  
> *(Nota: En el sistema de vuelo FLU de aeronavegabilidad, los ejes x e y invierten signo respecto a CAD)."*

Existe una **contradicción lógica directa** entre estas dos líneas contiguas:
- Si en FLU el eje $+y$ es la **izquierda** (definición universal de FLU),
- Y según la propia nota del autor: *"los ejes x e y invierten signo respecto a CAD"* ($y_{\text{FLU}} = - y_{\text{CAD}}$),
- Entonces CAD $+y$ **no puede ser la izquierda**. Forzosamente debe ser lo opuesto a la izquierda, es decir, la **DERECHA**.
- Al declarar simultáneamente que CAD $+y$ es "izquierda" y que "invierte signo para ser izquierda en FLU", el informe afirma implícitamente que $\text{Izquierda} = -\text{Izquierda}$, lo cual es absurdo.
- Además, un marco con $\text{Cola} (+x)$, $\text{Izquierda} (+y)$ y $\text{Arriba} (+z)$ sería un sistema de mano izquierda (levógiro), incompatible con la matriz $R$ dada.

### 4.2 Impacto en la Ubicación de los Módulos Propulsores

En la Sección 2.1 del informe, el autor asignó los cuatro ventiladores a partir de `centres_xy_m`:

$$\begin{aligned}
\text{Módulo 1: } & (x_1, y_1) = (-0.160, -0.076)\text{ m} \quad \text{Informe: "Nariz / Derecha"} \\
\text{Módulo 2: } & (x_2, y_2) = (-0.160, +0.076)\text{ m} \quad \text{Informe: "Nariz / Izquierda"} \\
\text{Módulo 3: } & (x_3, y_3) = (+0.160, -0.076)\text{ m} \quad \text{Informe: "Cola / Derecha"} \\
\text{Módulo 4: } & (x_4, y_4) = (+0.160, +0.076)\text{ m} \quad \text{Informe: "Cola / Izquierda"}
\end{aligned}$$

Al contrastar con la cinemática de vuelo real mediante $\mathbf{r}_{\text{FLU}} = R\,\mathbf{r}_{\text{CAD}}$:

| Módulo | Coordenadas CAD $(x, y)\text{ [m]}$ | Descripción en Informe de CG | Transformación FLU $(x, y)\text{ [m]}$ | Posición Física Real en Vuelo (FLU) | ¿Coincide la Etiqueta? |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **M1** | $(-0.160, -0.076)$ | Nariz / Derecha | $(+0.160, +0.076)$ | **Nariz / Izquierda (Babor)** | **INVERTIDA** |
| **M2** | $(-0.160, +0.076)$ | Nariz / Izquierda | $(+0.160, -0.076)$ | **Nariz / Derecha (Estribor)** | **INVERTIDA** |
| **M3** | $(+0.160, -0.076)$ | Cola / Derecha | $(-0.160, +0.076)$ | **Cola / Izquierda (Babor)** | **INVERTIDA** |
| **M4** | $(+0.160, +0.076)$ | Cola / Izquierda | $(-0.160, -0.076)$ | **Cola / Derecha (Estribor)** | **INVERTIDA** |

Las posiciones longitudinales (Nariz / Cola) son correctas en ambos marcos, pero **las etiquetas laterales (Izquierda / Derecha) en el informe están estrictamente permutadas respecto a la posición física real en la aeronave**.

---

## 5. Distinción entre Error de Documentación y Posible Efecto en Magnitudes del Modelo Simétrico

### 5.1 Invarianza de las Ecuaciones de Equilibrio Estático

Consideremos las ecuaciones de equilibrio estático en el marco CAD:
$$\begin{aligned}
\sum_{i=1}^4 f_i &= W \\
\sum_{i=1}^4 x_{i,\text{CAD}} f_i &= x_{cg,\text{CAD}} W \\
\sum_{i=1}^4 y_{i,\text{CAD}} f_i &= y_{cg,\text{CAD}} W
\end{aligned}$$

Si expresamos exactamente el mismo estado físico en el sistema de vuelo FLU, sustituyendo $x_{\text{FLU}} = -x_{\text{CAD}}$ e $y_{\text{FLU}} = -y_{\text{CAD}}$:
$$\begin{aligned}
\sum_{i=1}^4 f_i &= W \\
\sum_{i=1}^4 (-x_{i,\text{FLU}}) f_i &= (-x_{cg,\text{FLU}}) W \iff \sum_{i=1}^4 x_{i,\text{FLU}} f_i = x_{cg,\text{FLU}} W \\
\sum_{i=1}^4 (-y_{i,\text{FLU}}) f_i &= (-y_{cg,\text{FLU}}) W \iff \sum_{i=1}^4 y_{i,\text{FLU}} f_i = y_{cg,\text{FLU}} W
\end{aligned}$$

Los signos negativos en ambos miembros se cancelan de forma exacta. La física subyacente es 100% independiente del triedro dextrógiro elegido para proyectar los momentos.

### 5.2 Invarianza de la Envolvente de Factibilidad y Capacidad de Sustentación

El modelo analítico de C02 posee una geometría de sustentación perfectamente simétrica respecto a los planos longitudinal ($y = 0$) y transversal ($x = 0$):
- Cuatro propulsores rectangulares en $(\pm L_x, \pm L_y)$ con $L_x = 0.160\text{ m}$ y $L_y = 0.076\text{ m}$.
- Límites idénticos de saturación para los 4 actuadores: $0 \le f_i \le F_{\text{máx}}$.

Las ecuaciones analíticas que definen la factibilidad y la capacidad vertical máxima son:
$$\begin{aligned}
|x_{cg}| &\le L_x, \quad |y_{cg}| \le L_y \\
|x_{cg}| &\le L_x\left(\frac{4 F_{\text{máx}}}{W} - 1\right), \quad |y_{cg}| \le L_y\left(\frac{4 F_{\text{máx}}}{W} - 1\right) \\
\left|\frac{x_{cg}}{L_x} \pm \frac{y_{cg}}{L_y}\right| &\le \frac{2 F_{\text{máx}}}{W}
\end{aligned}$$
y la capacidad analítica cerrada:
$$F_{z,\max}(x_{cg}, y_{cg}) = \min\left(4 F_{\text{máx}},\; \frac{4 F_{\text{máx}}}{1 + \frac{|x_{cg}|}{L_x}},\; \frac{4 F_{\text{máx}}}{1 + \frac{|y_{cg}|}{L_y}},\; \frac{2 F_{\text{máx}}}{\frac{|x_{cg}|}{L_x} + \frac{|y_{cg}|}{L_y}}\right)$$

Dado que todas estas expresiones dependen exclusivamente de **valores absolutos** ($|x_{cg}|$, $|y_{cg}|$) o de combinaciones lineales simétricas invariantes ante la reflexión lateral $y \to -y$:
1. **El dominio admisible de CG (el octógono de sustentación) es idéntico.**
2. **El número de posiciones factibles en la malla simétrica evaluada es idéntico** (291 de 945 para $20.58\text{ N}$, y 473 de 945 para $25.00\text{ N}$).
3. **La holgura analítica de factibilidad $\Delta f_4$ es idéntica** en $(x_{cg}, y_{cg})$ y en $(x_{cg}, -y_{cg})$ (con residuales comprobados $< 10^{-12}\text{ N}$).
4. **La capacidad máxima de sustentación $F_{z,\max}$ es idéntica.**

### 5.3 Efecto en las Fuerzas Individuales de Propulsión

#### A. En la Condición Nominal Simétrica ($y_{cg} = 0$)
Todos los análisis del informe a lo largo del eje longitudinal (la tabla de puntos notables de la Sección 5.2, con $x_{cg} \in [0.000, 0.160]\text{ m}$ e $y_{cg} = 0$) se sitúan en el plano de simetría bilateral.
En dicha condición:
$$f_1 = f_2 \quad \text{y} \quad f_3 = f_4$$
Dado que la fuerza delantera izquierda es exactamente igual a la delantera derecha, y la trasera izquierda es igual a la trasera derecha, **el intercambio lateral de etiquetas no produce ninguna alteración numérica en los empujes de los motores**. Los valores reportados en el informe técnico para todos los puntos longitudinales son rigurosamente exactos tanto en magnitud como en asignación motriz.

#### B. En Condiciones con Excentricidad Lateral ($y_{cg} \ne 0$)
Si se evalúa una posición con coordenada CAD $y_{cg} > 0$:
- El modelo matemático calcula que los actuadores con coordenada $+y$ deben entregar mayor empuje que los actuadores con $-y$.
- En las ecuaciones del informe, se denominó a esto "lado izquierdo ($S_{\text{left}} > S_{\text{right}}$)".
- En la realidad del vehículo de vuelo FLU, una coordenada CAD $y_{cg} > 0$ corresponde a una posición física del CG desplazada hacia la **derecha** ($y_{\text{FLU}} = -y_{\text{CAD}} < 0$).
- Físicamente, los motores con coordenada CAD $+y$ son los Módulos 2 y 4, que se ubican físicamente a la **derecha** del vehículo ($y_{\text{FLU}} = -0.076\text{ m}$).
- Por lo tanto, el sistema de ecuaciones balanceó físicamente la masa de forma correcta: el lado donde está el peso físico recibió más empuje.
- Sin embargo, las etiquetas del informe invirtieron la terminología semántica: llamaron "izquierda" a los motores 2 y 4 (que son derechos) y llamaron "desplazamiento a la izquierda" a lo que era un desplazamiento físico hacia la derecha.

### 5.4 Conclusión del Dictamen sobre la Distinción del Error

```
+-----------------------------------------------------------------------------------+
|                        DICTAMEN DE DISTINCIÓN DE IMPACTO                          |
+-----------------------------------------------------------------------------------+
| 1. En Magnitudes Cuantitativas del Modelo Simétrico:                              |
|    - Capacidad máxima vertical Fz_max:         NINGÚN EFECTO (Idéntica)           |
|    - Holgura analítica de factibilidad Delta f4: NINGÚN EFECTO (Idéntica)         |
|    - Envolvente / Polígono de CG:              NINGÚN EFECTO (Idéntico)           |
|    - Puntos notables a lo largo de y=0:        NINGÚN EFECTO (Idéntico)           |
|    - Conjunto de magnitudes de empuje {fi}:    NINGÚN EFECTO (Mismos valores)     |
|                                                                                   |
| 2. En Nomenclatura, Documentación y Semántica:                                    |
|    - Eje CAD +y:                               ERROR DOCUMENTAL (Es Der., no Izq.)|
|    - Asignación de Módulos 1, 2, 3, 4:         PERMUTACIÓN LATERAL EN TEXTO       |
|    - Mapeo de totales marginales S_left/right: PERMUTACIÓN LATERAL EN TEXTO       |
|                                                                                   |
| 3. En Implementación y Operación Futura (Riesgo Crítico):                         |
|    - Si la documentación errónea se trasladase al cableado de actuadores físicos |
|      o al software del controlador de vuelo (FCU), los comandos de corrección     |
|      de alabeo (roll) se aplicarían en sentido inverso, generando divergencia     |
|      dinámica inmediata e inestabilidad catastrófica.                             |
+-----------------------------------------------------------------------------------+
```

---

## 6. Verificaciones y Pruebas Realizadas

Para respaldar este dictamen con total rigor matemático y garantizar su reproducibilidad en el sandbox local, se ejecutó el script de validación `salidas/verificar_ejes.py` con las siguientes comprobaciones automatizadas:

1. **Test de Álgebra Matricial:**
   - Determinante de $R_{\text{flight\_from\_CAD}}$: comprobado exactamente $+1.0$ (tolerancia $< 10^{-12}$).
   - Ortonormalidad: $R \cdot R^T = I$ con residuales nulos.
   - Simetría e involución: $R = R^T = R^{-1}$.
2. **Test de Quiralidad y Regla de la Mano Derecha:**
   - Triedro FLU canónico: $\mathbf{e}_{x,\text{FLU}} \times \mathbf{e}_{y,\text{FLU}} = \mathbf{e}_{z,\text{FLU}}$ (Dextrógiro comprobado).
   - Proyección de ejes CAD en FLU:
     - CAD $+x \to [-1, 0, 0]^T$ (Atrás / Cola).
     - CAD $+y \to [0, -1, 0]^T$ (Derecha / Estribor).
     - CAD $+z \to [0, 0, 1]^T$ (Arriba).
   - Triedro CAD: $\mathbf{e}_{x,\text{CAD}} \times \mathbf{e}_{y,\text{CAD}} = \mathbf{e}_{z,\text{CAD}}$ (Dextrógiro comprobado).
   - Comprobación de que asociar CAD $+y$ a la izquierda produciría un sistema levógiro $\mathbf{e}_x \times \mathbf{e}_y = -\mathbf{e}_z$.
3. **Mapeo Cinemático de Módulos:**
   - Transformación automatizada de los centros de los 4 ventiladores (`centres_xy_m`), verificando la permutación lateral entre el texto del informe y las coordenadas físicas de vuelo FLU.
4. **Test de Invarianza de Magnitudes y Simetría:**
   - Comprobación en múltiples pares $(x_{cg}, \pm y_{cg})$ de que la factibilidad, $\Delta f_4$ y $F_{z,\max}$ son estrictamente idénticas ($< 10^{-12}\text{ N}$).
   - Comprobación de la permutación exacta de fuerzas: $f_1(x, y) = f_2(x, -y)$, $f_3(x, y) = f_4(x, -y)$.

Todas las pruebas finalizaron con estado **PASS** (100% de éxito).

---

## 7. Limitaciones Técnicas del Análisis

1. **Carácter Conceptual de los Datos:**  
   La configuración C02 se encuentra en fase de desarrollo conceptual. Las masas ($5.0\text{ kg}$) y geometrías evaluadas son referencias de diseño preliminar. No se dispone de datos de prototipos ensayados físicamente ni de vehículos reales pesados en banco (`actual_mass_kg: null`, `actual_CG_m: null`).
2. **Modelo Estático Bidimensional:**  
   El análisis evalúa el equilibrio estático vertical puro sin considerar aerodinámica de avance, efectos de interacción conducto-hélice, efecto suelo, ni dinámicas de cabeceo/alabeo acopladas en tiempo real.
3. **Ausencia de Mapa Instalado:**  
   Se asume propulsión ideal puntual sin degradación de empuje por flujo oblicuo o contrapresión (`installed_map_available: false`).
4. **Desacoplamiento Estructural y Dinámico:**  
   No se evalúan deformaciones aeroelásticas de la estructura bajo carga motriz ni efectos giroscópicos transitorios debidos a la aceleración angular de los rotores.

---

## 8. Registro de Entregables Generados

Todos los entregables han sido generados autónomamente dentro de `salidas/`:

1. **`salidas/DICTAMEN.md`**: El presente dictamen técnico pericial completo y detallado.
2. **`salidas/verificar_ejes.py`**: Script en Python 3 que ejecuta la batería completa de comprobaciones matriciales, quiralidad, transformaciones de coordenadas y simetría analítica de fuerzas.
