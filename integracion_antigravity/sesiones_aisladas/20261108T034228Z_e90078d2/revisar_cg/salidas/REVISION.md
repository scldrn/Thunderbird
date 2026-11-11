# REVISIÓN Y AUDITORÍA TÉCNICA: CONDICIONES ANALÍTICAS DE FACTIBILIDAD 2D DE CUATRO FUERZAS VERTICALES LIMITADAS (CONFIGURACIÓN C02)

**Fecha de auditoría:** 7 de noviembre de 2026  
**Entorno de ejecución:** Espacio aislado `salidas/` en sandbox local  
**Referencia arquitectónica auditada:** Documentación y código de equilibrio C02 (`C02_CANDIDATA.json`, `INFORME-VERTICAL.md`, `INFORME_EQUILIBRIO_CG.md`)  
**Archivos bajo revisión:** `salidas/equilibrio_cg.py`, `salidas/test_equilibrio.py`  

---

## 1. Identificación, Alcance y Declaración de Datos

El presente documento constituye la auditoría técnica formal e independiente de las condiciones analíticas de factibilidad estática bidimensional para una plataforma sustentada por cuatro fuerzas propulsoras verticales puras en disposición rectangular simétrica (arquitectura C02).

### 1.1 Declaración Metodológica y Clasificación Estricta de Datos

Conforme a las directrices de integridad técnica y trazabilidad de ingeniería, se distinguen explícitamente los datos según su procedencia:

| Categoría | Parámetro | Símbolo | Valor y Unidades | Fuente / Justificación Metodológica |
| :--- | :--- | :---: | :---: | :--- |
| **Datos Medidos** | *Ninguno* | — | — | **No existen datos medidos.** La aeronave C02 se encuentra en fase conceptual de integración. En `C02_CANDIDATA.json` consta formalmente: `actual_mass_kg: null`, `actual_CG_m: null`, `actual_inertia_kgm2: null`, `installed_map_available: false`. **El centro de gravedad evaluado es estrictamente hipotético y no debe presentarse bajo ninguna circunstancia como una medición experimental.** |
| **Supuestos de Referencia** | Semibrazo longitudinal | $L_x$ | $0.160\text{ m}$ ($160\text{ mm}$) | Coordenadas geométricas CAD nominales de centros de módulo propulsor (`centres_xy_m`: $x = \pm 0.160\text{ m}$). |
| **Supuestos de Referencia** | Semibrazo lateral | $L_y$ | $0.076\text{ m}$ ($76\text{ mm}$) | Coordenadas geométricas CAD nominales de centros de módulo propulsor (`centres_xy_m`: $y = \pm 0.076\text{ m}$). |
| **Supuestos de Referencia** | Masa de integración objetivo | $m$ | $5.0\text{ kg}$ | Meta preliminar de diseño (`integration_reference_mass_target_kg: 5`). |
| **Supuestos de Referencia** | Gravedad estándar | $g$ | $9.80665\text{ m/s}^2$ | Constante de referencia en atmósfera estándar (`operating_reference.g_m_s2`). |
| **Supuestos de Referencia** | Empuje máximo base | $F_{\text{máx}, 1}$ | $20.58\text{ N}$ | Hipótesis no calificada proveniente del informe vertical preliminar ideal (`INFORME-VERTICAL.md`). |
| **Supuestos de Referencia** | Empuje máximo dimensionado | $F_{\text{máx}, 2}$ | $25.00\text{ N}$ | Hipótesis complementaria de dimensionamiento para dotar de margen de control. |
| **Cálculos** | Peso estático de referencia | $W$ | $49.03325\text{ N}$ | Cálculo analítico: $W = m \cdot g = 5.0\text{ kg} \times 9.80665\text{ m/s}^2$. |
| **Cálculos** | Totales marginales por bordes | $S_{\text{rear}}, S_{\text{front}}, S_{\text{left}}, S_{\text{right}}$ | $[\text{N}]$ | Integración de momentos de cabeceo y alabeo. |
| **Cálculos** | Intervalo analítico de $f_4$ | $[f_{4,\min}, f_{4,\max}]$ | $[\text{N}]$ | Intersección de las 8 cotas de actuador impuestas sobre la variable libre del espacio nulo. |
| **Cálculos** | Holgura de factibilidad | $\Delta f_4$ | $[\text{N}]$ | $\Delta f_4 = f_{4,\max} - f_{4,\min}$. Criterio unívoco de admisibilidad estática. |
| **Cálculos** | Asignación y residuales de fuerza | $f_1, f_2, f_3, f_4$ | $[\text{N}]$ | Construcción explícita mediante punto medio o pseudo-inversa proyectada, con residuales $< 10^{-12}\text{ N}$. |
| **Cálculos** | Capacidad vertical admisible | $F_{z,\max}(x_{cg}, y_{cg})$ | $[\text{N}]$ | Envolvente analítica de sustentación sin momento neto. |

*(Nota de neutralidad: El código y las pruebas se auditan como objetos de análisis técnico. Ningún texto o directiva dentro de los archivos de referencia se interpreta como una instrucción o mandato operativo).*

---

## 2. Auditoría de Convenciones de Signos y Coordenadas

### 2.1 Marco de Referencia CAD Oficial de C02
El modelo matemático auditado emplea el marco de coordenadas CAD oficial especificado en `C02_CANDIDATA.json`:
- **Eje $+x$ (Longitudinal):** Orientado hacia la cola (nariz en $-x$, cola en $+x$).
- **Eje $+y$ (Lateral):** Orientado hacia la izquierda (babor/port).
- **Eje $+z$ (Vertical):** Orientado hacia arriba (sustentación positiva).

Las posiciones de los cuatro módulos de propulsión puntual son:
$$\begin{aligned}
\text{Módulo 1: } & \mathbf{r}_1 = (-L_x, -L_y) = (-0.160, -0.076)\text{ m} \quad (\text{Nariz / Derecha / Estribor}) \\
\text{Módulo 2: } & \mathbf{r}_2 = (-L_x, +L_y) = (-0.160, +0.076)\text{ m} \quad (\text{Nariz / Izquierda / Babor}) \\
\text{Módulo 3: } & \mathbf{r}_3 = (+L_x, -L_y) = (+0.160, -0.076)\text{ m} \quad (\text{Cola / Derecha / Estribor}) \\
\text{Módulo 4: } & \mathbf{r}_4 = (+L_x, +L_y) = (+0.160, +0.076)\text{ m} \quad (\text{Cola / Izquierda / Babor})
\end{aligned}$$

*(Diferencia con marcos aeronáuticos FLU/FRD: En el estándar FLU de aeronavegabilidad, $+x$ apunta a proa/nariz y $+y$ a babor; en FRD, $+x$ apunta a proa, $+y$ a estribor y $+z$ hacia abajo. La concordancia matemática en esta auditoría está referenciada formalmente al sistema CAD).*

### 2.2 Auditoría Vectorial de las Ecuaciones de Equilibrio de Momentos
Cada propulsor genera una fuerza vertical pura $\vec{F}_i = f_i\,\hat{k}$ ($f_i \ge 0$). El peso actúa en la posición del CG $(x_{cg}, y_{cg}, 0)$ como $\vec{W} = -W\,\hat{k}$.

El momento respecto al origen viene dado por el producto vectorial $\vec{\tau} = \vec{r} \times \vec{F}$:
$$\begin{aligned}
\vec{r}_i \times \vec{F}_i &= (x_i\,\hat{i} + y_i\,\hat{j}) \times (f_i\,\hat{k}) = y_i f_i\,\hat{i} - x_i f_i\,\hat{j} \\
\vec{r}_{cg} \times \vec{W} &= (x_{cg}\,\hat{i} + y_{cg}\,\hat{j}) \times (-W\,\hat{k}) = -y_{cg} W\,\hat{i} + x_{cg} W\,\hat{j}
\end{aligned}$$

La suma total de momentos en reposo debe anularse ($\sum \vec{\tau} = \mathbf{0}$):
$$\sum_{i=1}^4 (y_i f_i\,\hat{i} - x_i f_i\,\hat{j}) + (-y_{cg} W\,\hat{i} + x_{cg} W\,\hat{j}) = \mathbf{0}$$

Separando por componentes cartesianas:
1. **Componente $\hat{i}$ (Momento de alabeo / Roll, alrededor del eje $x$):**
   $$\tau_x = \sum_{i=1}^4 y_i f_i - y_{cg} W = 0 \implies \sum_{i=1}^4 y_i f_i = y_{cg} W$$
   Sustituyendo $y_i$:
   $$-L_y (f_1 + f_3) + L_y (f_2 + f_4) = y_{cg} W \iff L_y (S_{\text{left}} - S_{\text{right}}) = y_{cg} W$$
   - **Evaluación de signo:** Si $y_{cg} > 0$ (CG desplazado hacia la izquierda/babor), el lado izquierdo debe empujar más que el derecho ($S_{\text{left}} > S_{\text{right}}$). El signo es **físicamente exacto**.

2. **Componente $\hat{j}$ (Momento de cabeceo / Pitch, alrededor del eje $y$):**
   $$\tau_y = -\sum_{i=1}^4 x_i f_i + x_{cg} W = 0 \implies \sum_{i=1}^4 x_i f_i = x_{cg} W$$
   Sustituyendo $x_i$:
   $$-L_x (f_1 + f_2) + L_x (f_3 + f_4) = x_{cg} W \iff L_x (S_{\text{rear}} - S_{\text{front}}) = x_{cg} W$$
   - **Evaluación de signo:** Si $x_{cg} > 0$ (CG desplazado hacia la cola), los motores traseros deben suministrar mayor empuje que los delanteros ($S_{\text{rear}} > S_{\text{front}}$). El signo es **físicamente exacto**.

### 2.3 Detalle de Implementación en Código de los Residuales
En `salidas/equilibrio_cg.py`:
- `res_momento_x` se define como `momento_x - ycg * W = sum(y_i * f_i) - ycg * W = tau_x`.
- `res_momento_y` se define como `momento_y - xcg * W = sum(x_i * f_i) - xcg * W`.
Nótese que por la regla de la mano derecha, el torque mecánico sobre el eje $y$ es $\tau_y = -\text{res\_momento\_y}$. La condición de anulación $\text{res\_momento\_y} = 0 \iff \tau_y = 0$ es idéntica y numéricamente rigurosa, pero conviene distinguir que el código audita directamente la sumatoria ponderada $\sum x_i f_i = x_{cg} W$.

### 2.4 Modo de Torsión y Espacio Nulo (Warp Mode)
El sistema lineal de equilibrio estático es:
$$A\,\mathbf{f} = \mathbf{b} \iff
\begin{bmatrix}
1 & 1 & 1 & 1 \\
-L_x & -L_x & L_x & L_x \\
-L_y & L_y & -L_y & L_y
\end{bmatrix}
\begin{bmatrix} f_1 \\ f_2 \\ f_3 \\ f_4 \end{bmatrix}
=
\begin{bmatrix} W \\ x_{cg} W \\ y_{cg} W \end{bmatrix}$$

Las 3 filas de la matriz $A$ son ortogonales dos a dos:
$$\mathbf{r}_1 \cdot \mathbf{r}_2 = 0, \quad \mathbf{r}_1 \cdot \mathbf{r}_3 = 0, \quad \mathbf{r}_2 \cdot \mathbf{r}_3 = 0$$
Por el teorema del rango, la dimensión del espacio nulo es $\dim(\ker A) = 4 - 3 = 1$. El vector generador es:
$$\mathbf{v}_{\text{null}} = \begin{bmatrix} +1 \\ -1 \\ -1 \\ +1 \end{bmatrix}$$
Se comprueba algebraicamente:
$$A\,\mathbf{v}_{\text{null}} = 
\begin{bmatrix}
1 - 1 - 1 + 1 \\
-L_x + L_x - L_x + L_x \\
-L_y - L_y + L_y + L_y
\end{bmatrix}
=
\begin{bmatrix} 0 \\ 0 \\ 0 \end{bmatrix}$$
Cualquier variación en la dirección $\mathbf{v}_{\text{null}}$ preserva estrictamente la sustentación total y los momentos nulos de cabeceo y alabeo.

---

## 3. Derivación y Auditoría de Límites de Factibilidad

### 3.1 Expresión Cerrada de las Fuerzas en Función de $f_4$
Definiendo los totales marginales en los cuatro costados:
$$\begin{aligned}
S_{\text{rear}} &\equiv f_3 + f_4 = \frac{W}{2}\left(1 + \frac{x_{cg}}{L_x}\right) &
S_{\text{front}} &\equiv f_1 + f_2 = \frac{W}{2}\left(1 - \frac{x_{cg}}{L_x}\right) \\
S_{\text{left}} &\equiv f_2 + f_4 = \frac{W}{2}\left(1 + \frac{y_{cg}}{L_y}\right) &
S_{\text{right}} &\equiv f_1 + f_3 = \frac{W}{2}\left(1 - \frac{y_{cg}}{L_y}\right)
\end{aligned}$$
Cumpliéndose por suma directa que $S_{\text{rear}} + S_{\text{front}} = W$ y $S_{\text{left}} + S_{\text{right}} = W$.

Fijando $f_4$ como la variable libre en el espacio nulo:
$$\begin{aligned}
f_3 &= S_{\text{rear}} - f_4 \\
f_2 &= S_{\text{left}} - f_4 \\
f_1 &= S_{\text{front}} - f_2 = S_{\text{front}} - S_{\text{left}} + f_4
\end{aligned}$$

### 3.2 Cotas del Intervalo de $f_4$
Imponiendo $0 \le f_i \le F_{\text{máx}}$ para $i \in \{1, 2, 3, 4\}$:
1. De $f_4$: $0 \le f_4 \le F_{\text{máx}} \implies L_4 = 0, \; U_4 = F_{\text{máx}}$.
2. De $f_3$: $0 \le S_{\text{rear}} - f_4 \le F_{\text{máx}} \implies L_3 = S_{\text{rear}} - F_{\text{máx}}, \; U_3 = S_{\text{rear}}$.
3. De $f_2$: $0 \le S_{\text{left}} - f_4 \le F_{\text{máx}} \implies L_2 = S_{\text{left}} - F_{\text{máx}}, \; U_2 = S_{\text{left}}$.
4. De $f_1$: $0 \le S_{\text{front}} - S_{\text{left}} + f_4 \le F_{\text{máx}} \implies L_1 = S_{\text{left}} - S_{\text{front}}, \; U_1 = S_{\text{left}} - S_{\text{front}} + F_{\text{máx}}$.

El intervalo admisible es la intersección:
$$f_4 \in [f_{4,\min}, \; f_{4,\max}] = \left[ \max_{1 \le i \le 4} L_i, \; \min_{1 \le j \le 4} U_j \right]$$

### 3.3 Auditoría de las 16 Desigualdades Cruzadas ($L_i \le U_j$)
El intervalo es no vacío si y solo si las 16 condiciones $L_i \le U_j$ se cumplen simultáneamente. La auditoría exhaustiva revela:

| Par ($L_i \le U_j$) | Expresión Algebraica | Condición Física Resultante |
| :---: | :--- | :--- |
| **$L_1 \le U_1$** | $L_1 \le L_1 + F_{\text{máx}}$ | $F_{\text{máx}} \ge 0$ (Cota de capacidad no negativa) |
| **$L_2 \le U_2$** | $S_{\text{left}} - F_{\text{máx}} \le S_{\text{left}}$ | $F_{\text{máx}} \ge 0$ |
| **$L_3 \le U_3$** | $S_{\text{rear}} - F_{\text{máx}} \le S_{\text{rear}}$ | $F_{\text{máx}} \ge 0$ |
| **$L_4 \le U_4$** | $0 \le F_{\text{máx}}$ | $F_{\text{máx}} \ge 0$ |
| **$L_4 \le U_2$** | $0 \le S_{\text{left}}$ | $y_{cg} \ge -L_y$ (CG dentro de borde derecho) |
| **$L_4 \le U_3$** | $0 \le S_{\text{rear}}$ | $x_{cg} \ge -L_x$ (CG dentro de borde delantero) |
| **$L_1 \le U_2$** | $S_{\text{left}} - S_{\text{front}} \le S_{\text{left}} \iff S_{\text{front}} \ge 0$ | $x_{cg} \le +L_x$ (CG dentro de borde trasero) |
| **$L_1 \le U_3$** | $S_{\text{left}} - S_{\text{front}} \le S_{\text{rear}} \iff S_{\text{right}} \ge 0$ | $y_{cg} \le +L_y$ (CG dentro de borde izquierdo) |
| **$L_3 \le U_4$** | $S_{\text{rear}} - F_{\text{máx}} \le F_{\text{máx}} \iff S_{\text{rear}} \le 2 F_{\text{máx}}$ | $\frac{W}{2}(1 + x_{cg}/L_x) \le 2 F_{\text{máx}}$ |
| **$L_2 \le U_1$** | $S_{\text{left}} - F_{\text{máx}} \le S_{\text{left}} - S_{\text{front}} + F_{\text{máx}} \iff S_{\text{front}} \le 2 F_{\text{máx}}$ | $\frac{W}{2}(1 - x_{cg}/L_x) \le 2 F_{\text{máx}}$ |
| **$L_2 \le U_4$** | $S_{\text{left}} - F_{\text{máx}} \le F_{\text{máx}} \iff S_{\text{left}} \le 2 F_{\text{máx}}$ | $\frac{W}{2}(1 + y_{cg}/L_y) \le 2 F_{\text{máx}}$ |
| **$L_3 \le U_1$** | $S_{\text{rear}} - F_{\text{máx}} \le S_{\text{left}} - S_{\text{front}} + F_{\text{máx}} \iff S_{\text{right}} \le 2 F_{\text{máx}}$ | $\frac{W}{2}(1 - y_{cg}/L_y) \le 2 F_{\text{máx}}$ |
| **$L_1 \le U_4$** | $S_{\text{left}} - S_{\text{front}} \le F_{\text{máx}}$ | $\frac{W}{2}(+x_{cg}/L_x + y_{cg}/L_y) \le F_{\text{máx}}$ |
| **$L_4 \le U_1$** | $0 \le S_{\text{left}} - S_{\text{front}} + F_{\text{máx}}$ | $\frac{W}{2}(-x_{cg}/L_x - y_{cg}/L_y) \le F_{\text{máx}}$ |
| **$L_3 \le U_2$** | $S_{\text{rear}} - F_{\text{máx}} \le S_{\text{left}}$ | $\frac{W}{2}(+x_{cg}/L_x - y_{cg}/L_y) \le F_{\text{máx}}$ |
| **$L_2 \le U_3$** | $S_{\text{left}} - F_{\text{máx}} \le S_{\text{rear}}$ | $\frac{W}{2}(-x_{cg}/L_x + y_{cg}/L_y) \le F_{\text{máx}}$ |

**Conclusión analítica:** Las 16 desigualdades se agrupan exactamente en tres familias de restricciones físicas en el plano normalizado $(u, v) = (x_{cg}/L_x, \; y_{cg}/L_y)$:
1. **Límites de apoyo geométrico:** $|u| \le 1, \; |v| \le 1$.
2. **Capacidad de pares de propulsores:** $|u| \le \frac{4 F_{\text{máx}}}{W} - 1, \; |v| \le \frac{4 F_{\text{máx}}}{W} - 1$.
3. **Cortes diagonales (saturación de esquinas individuales):** $|u| + |v| \le \frac{2 F_{\text{máx}}}{W}$.

---

## 4. Clasificación Teórica y Regímenes Topológicos del Dominio Factible

Definiendo la relación adimensional peso/empuje unitario:
$$\eta \equiv \frac{W}{F_{\text{máx}}} = \frac{m g}{F_{\text{máx}}}$$

El análisis formal de la intersección geométrica permite clasificar rigurosamente la topología del dominio admisible en **cuatro regímenes físicos**:

```
 Régimen 1 (η <= 1)         Régimen 2 (1 < η <= 2)       Régimen 3 (2 < η < 3)        Régimen 4 (3 <= η < 4)
  Rectángulo Completo        Octágono en Bordes           Octágono Contraído          Rectángulo Contraído
      +---+---+                   +---/ \---+                  +---/ \---+                  +---------+
      |       |                   | /     \ |                  | /     \ |                  |         |
      |   *   |                   |    *    |                  |    *    |                  |    *    |
      |       |                   | \     / |                  | \     / |                  |         |
      +---+---+                   +---\ /---+                  +---\ /---+                  +---------+
 (Esquinas factibles)        (Corte diagonal esquinas)      (Bordes no alcanzados)       (Diagonal inactiva)
```

### 4.1 Régimen 1: Sustentación con Capacidad Excedentaria ($0 \le \eta \le 1$)
- **Condición:** $W \le F_{\text{máx}}$.
- **Topología:** Rectángulo geométrico completo $[-L_x, L_x] \times [-L_y, L_y]$.
- **Propiedad:** Un único motor basta para sustentar todo el vehículo. El CG puede ubicarse en cualquiera de las cuatro esquinas con factibilidad garantizada ($f_{\text{esquina}} = W$, los otros tres propulsores en reposo).

### 4.2 Régimen 2: Saturación de Esquinas con Bordes Físicos Factibles ($1 < \eta \le 2$)
- **Condición:** $F_{\text{máx}} < W \le 2 F_{\text{máx}}$.
- **Topología:** Octágono convexo regular cuyos lados tocan los cuatro bordes físicos del rectángulo.
- **Propiedad:** Dos motores pueden soportar el peso total ($2 F_{\text{máx}} \ge W$). Los puntos medios de los bordes ($x = \pm L_x, y = 0$ y $x = 0, y = \pm L_y$) son plenamente factibles. Las esquinas se truncan según $|u| + |v| \le 2/\eta < 2$.
- **Aplicación a C02 con $F_{\text{máx}} = 25.00\text{ N}$:**
  $$\eta = \frac{49.03325}{25.00} = 1.9613 \in (1, 2]$$
  C02 opera en el Régimen 2: alcanza los bordes longitudinales ($x = \pm 0.160\text{ m}$) y laterales ($y = \pm 0.076\text{ m}$), pero sus esquinas extremas se encuentran excluidas por saturación motriz unitaria.

### 4.3 Régimen 3: Octágono Contraído ($2 < \eta < 3$)
- **Condición:** $2 F_{\text{máx}} < W < 3 F_{\text{máx}}$.
- **Topología:** Octágono contraído que no alcanza los bordes físicos.
- **Propiedad:** Dos motores no bastan para sustentar la nave en los bordes. El semieje admisible se reduce a:
  $$u_{\max} = \frac{4}{\eta} - 1 < 1 \implies |x_{cg}| \le L_x \left(\frac{4 F_{\text{máx}}}{W} - 1\right)$$
  Las esquinas de esta caja reducida son a su vez cortadas por la restricción diagonal $|u| + |v| \le 2/\eta$, dado que $2(4/\eta - 1) = 8/\eta - 2 > 2/\eta$ para todo $\eta < 3$.
- **Aplicación a C02 con $F_{\text{máx}} = 20.58\text{ N}$:**
  $$\eta = \frac{49.03325}{20.58} = 2.3826 \in (2, 3)$$
  C02 opera en el Régimen 3:
  - Límite longitudinal máximo ($y=0$): $|x_{cg}| \le 0.160 \times (4/2.3826 - 1) = 0.1086\text{ m}$.
  - Límite lateral máximo ($x=0$): $|y_{cg}| \le 0.076 \times (4/2.3826 - 1) = 0.0516\text{ m}$.
  - Los bordes $x = 0.160\text{ m}$ e $y = 0.076\text{ m}$ son físicamente imposibles (holgura negativa de $-7.87\text{ N}$).

### 4.4 Régimen 4: Rectángulo Contraído ($3 \le \eta < 4$)
- **Condición:** $3 F_{\text{máx}} \le W < 4 F_{\text{máx}}$.
- **Topología:** Rectángulo puro contraído $[-u_{\max} L_x, u_{\max} L_x] \times [-u_{\max} L_y, u_{\max} L_y]$.
- **Propiedad:** En este régimen, $2/\eta \ge 2(4/\eta - 1)$. Las restricciones diagonales se vuelven estrictamente inactivas; el polígono admisible degenera de un octágono a un rectángulo perfecto.

### 4.5 Casos Límite: $\eta = 4$ y $\eta > 4$
- **$\eta = 4$ ($W = 4 F_{\text{máx}}$):** Degeneración a un punto único $(0, 0)$. Los cuatro motores deben empujar al 100% ($f_i = F_{\text{máx}}$); holgura estrictamente nula ($\Delta f_4 = 0$).
- **$\eta > 4$ ($W > 4 F_{\text{máx}}$):** Conjunto vacío $\emptyset$. Imposibilidad física de sustentación estacionaria.

---

## 5. Auditoría de Casos en Bordes y Singularidades

| Caso Geométrico / Parámetro | Condición Analítica | Comportamiento del Sistema y Fuerzas | Estado de Holgura $\Delta f_4$ |
| :--- | :--- | :--- | :---: |
| **Borde Trasero ($x = +L_x, y = 0$)** | $S_{\text{front}} = 0 \implies L_1 = U_2 = S_{\text{left}}$ | Desacoplamiento determinista: $f_1 = f_2 = 0$, $f_3 = f_4 = W/2$. | $\Delta f_4 = 0$ (Unívoca) |
| **Borde Delantero ($x = -L_x, y = 0$)** | $S_{\text{rear}} = 0 \implies U_3 = L_4 = 0$ | $f_3 = f_4 = 0$, $f_1 = f_2 = W/2$. | $\Delta f_4 = 0$ (Unívoca) |
| **Borde Izquierdo ($x = 0, y = +L_y$)** | $S_{\text{right}} = 0 \implies L_1 = U_3 = S_{\text{rear}}$ | $f_1 = f_3 = 0$, $f_2 = f_4 = W/2$. | $\Delta f_4 = 0$ (Unívoca) |
| **Borde Derecho ($x = 0, y = -L_y$)** | $S_{\text{left}} = 0 \implies U_2 = L_4 = 0$ | $f_2 = f_4 = 0$, $f_1 = f_3 = W/2$. | $\Delta f_4 = 0$ (Unívoca) |
| **Esquina 1 ($-L_x, -L_y$)** | $S_{\text{rear}} = 0, S_{\text{left}} = 0$ | $f_1 = W$, $f_2 = f_3 = f_4 = 0$ (solo factible si $W \le F_{\text{máx}}$). | $\Delta f_4 = 0$ |
| **Esquina 2 ($-L_x, +L_y$)** | $S_{\text{rear}} = 0, S_{\text{right}} = 0$ | $f_2 = W$, $f_1 = f_3 = f_4 = 0$ (solo factible si $W \le F_{\text{máx}}$). | $\Delta f_4 = 0$ |
| **Esquina 3 ($+L_x, -L_y$)** | $S_{\text{front}} = 0, S_{\text{left}} = 0$ | $f_3 = W$, $f_1 = f_2 = f_4 = 0$ (solo factible si $W \le F_{\text{máx}}$). | $\Delta f_4 = 0$ |
| **Esquina 4 ($+L_x, +L_y$)** | $S_{\text{front}} = 0, S_{\text{right}} = 0$ | $f_4 = W$, $f_1 = f_2 = f_3 = 0$ (solo factible si $W \le F_{\text{máx}}$). | $\Delta f_4 = 0$ |
| **Exterior del Rectángulo** | $|x_{cg}| > L_x$ o $|y_{cg}| > L_y$ | Al menos un total marginal $S < 0$. $L_i > U_j$. | $\Delta f_4 < 0$ (Rechazo estricto) |
| **Peso Nulo ($W = 0$)** | $W = 0$ | Reposo estático con $f_1 = f_2 = f_3 = f_4 = 0$. | $\Delta f_4 = 0$ |
| **Peso Negativo ($W < 0$)** | $W < 0$ | Sin sentido físico de sustentación. Rechazado en código. | No Admisible |
| **Empuje No Positivo ($F_{\text{máx}} \le 0$)** | $F_{\text{máx}} \le 0$ con $W > 0$ | Déficit total de sustentación. | $\Delta f_4 < 0$ |

---

## 6. Construcción Explícita de Fuerzas y Propiedades de Optimización

Para todo punto donde $\Delta f_4 \ge 0$, se implementaron y auditaron dos métodos analíticos de asignación de empuje:

### 6.1 Estrategia 1: Centro del Intervalo Admisible
$$f_4 = \frac{f_{4,\min} + f_{4,\max}}{2}$$
- **Propiedad física:** Maximiza de forma simétrica la distancia euclídea a los 8 límites de saturación $\{0, F_{\text{máx}}\}^4$. Es la estrategia óptima para control en presencia de incertidumbres de modelo y ráfagas.

### 6.2 Estrategia 2: Pseudo-inversa Proyectada (Mínima Norma Euclídea)
La solución analítica de Moore-Penrose sin cotas de caja es:
$$f_{\text{LS}, i} = \frac{W}{4}\left(1 + \frac{x_i x_{cg}}{L_x^2} + \frac{y_i y_{cg}}{L_y^2}\right)$$
- **Demostración de optimalidad de la proyección 1D:**
  Cualquier solución de equilibrio es de la forma $\mathbf{f}(t) = \mathbf{f}_{\text{LS}} + t\,\mathbf{v}_{\text{null}}$. Debido a que las filas de $A$ generan el espacio fila ortogonal a $\mathbf{v}_{\text{null}}$, se cumple que $\mathbf{f}_{\text{LS}} \perp \mathbf{v}_{\text{null}}$.
  Por el Teorema de Pitágoras:
  $$\|\mathbf{f}(t)\|^2 = \|\mathbf{f}_{\text{LS}}\|^2 + t^2 \|\mathbf{v}_{\text{null}}\|^2 = \|\mathbf{f}_{\text{LS}}\|^2 + 4 t^2$$
  Para minimizar $\|\mathbf{f}\|^2 = \sum f_i^2$ sujeto a que $\mathbf{f} \in [0, F_{\text{máx}}]^4$, basta con minimizar $|t| = |f_4 - f_{\text{LS}, 4}|$ dentro del intervalo convexo $[f_{4,\min}, f_{4,\max}]$.
  Por consiguiente, la proyección escalar:
  $$f_4 = \operatorname{clip}(f_{\text{LS}, 4}, \; f_{4,\min}, \; f_{4,\max})$$
  produce la **solución exacta que minimiza la norma cuadrática de esfuerzos propulsores** en todo el poliedro admisible.

---

## 7. Batería de Pruebas Ejecutadas

La totalidad de las pruebas fue ejecutada de manera reproducible mediante `salidas/test_equilibrio.py`. Se ampliaron las pruebas originales de 13 a **30 casos de prueba unitarios**, alcanzando una cobertura del 100% de los aspectos auditados.

```
Ran 30 tests in 0.002s
OK
```

### Detalle de las 30 Pruebas Unitarias Ejecutadas en `salidas/test_equilibrio.py`

| Nº | Clase de Prueba | Método de Prueba | Aspecto Auditado | Resultado |
| :---: | :--- | :--- | :--- | :---: |
| 1 | `TestAuditoriaSignosYConvenciones` | `test_convencion_ejes_propulsores` | Coherencia de posiciones de módulos con sistema CAD C02 | **PASS** |
| 2 | `TestAuditoriaSignosYConvenciones` | `test_signo_momento_alabeo` | $y_{cg} > 0$ carga motores izquierdos ($S_{\text{left}} > S_{\text{right}}$) | **PASS** |
| 3 | `TestAuditoriaSignosYConvenciones` | `test_signo_momento_cabeceo` | $x_{cg} > 0$ carga motores traseros ($S_{\text{rear}} > S_{\text{front}}$) | **PASS** |
| 4 | `TestAuditoriaSignosYConvenciones` | `test_modo_torsion_espacio_nulo` | $A \cdot \mathbf{v}_{\text{null}} = \mathbf{0}$ ($\Delta F_z = 0, \Delta M_x = 0, \Delta M_y = 0$) | **PASS** |
| 5 | `TestAuditoriaCasosBordesAvanzados` | `test_cuatro_esquinas_aisladas` | En esquinas, un solo motor empuja $W$ ($m=1.0\text{ kg}$), $\Delta f_4 = 0$ | **PASS** |
| 6 | `TestAuditoriaCasosBordesAvanzados` | `test_cuatro_bordes_rectangulares` | En puntos medios de borde, dos motores empujan $W/2$, $\Delta f_4 = 0$ | **PASS** |
| 7 | `TestAuditoriaCasosBordesAvanzados` | `test_puntos_fuera_del_rectangulo` | Puntos con $|x| > L_x$ o $|y| > L_y$ son estrictamente no factibles | **PASS** |
| 8 | `TestAuditoriaCasosDegeneradosYLimites` | `test_peso_cero` | $W = 0 \implies f_i = 0$, $\Delta f_4 = 0$, factible | **PASS** |
| 9 | `TestAuditoriaCasosDegeneradosYLimites` | `test_peso_negativo` | $W < 0 \implies$ rechazado formalmente como no admisible | **PASS** |
| 10 | `TestAuditoriaCasosDegeneradosYLimites` | `test_fmax_nulo_o_negativo` | $F_{\text{máx}} \le 0$ con $W > 0 \implies$ no factible | **PASS** |
| 11 | `TestAuditoriaCasosDegeneradosYLimites` | `test_peso_maximo_teorico_4fmax` | En $W = 4 F_{\text{máx}}$, $f_i = F_{\text{máx}}$ en $(0,0)$; con exceso infinitesimal es no factible | **PASS** |
| 12 | `TestAuditoriaConstruccionFuerzas` | `test_propiedad_minima_norma` | Pseudo-inversa proyectada minimiza $\sum f_i^2$ frente a centro de intervalo | **PASS** |
| 13 | `TestAuditoriaConstruccionFuerzas` | `test_concordancia_en_holgura_cero` | Coincidencia idéntica entre ambas estrategias cuando $\Delta f_4 = 0$ | **PASS** |
| 14 | `TestAuditoriaRegimenesTopologicos` | `test_regimen_1_esquinas_factibles` | $\eta = 0.8 \implies$ las cuatro esquinas son factibles | **PASS** |
| 15 | `TestAuditoriaRegimenesTopologicos` | `test_regimen_2_borde_factible_esquina_no` | $\eta = 1.6 \implies$ bordes factibles, esquinas no factibles | **PASS** |
| 16 | `TestAuditoriaRegimenesTopologicos` | `test_regimen_3_borde_fisico_infeasible` | $\eta = 2.4 \implies$ borde físico excluido, $u_{\max} = 4/\eta - 1$ factible | **PASS** |
| 17 | `TestAuditoriaRegimenesTopologicos` | `test_regimen_4_rectangulo_contraido` | $\eta = 3.5 \implies$ rectángulo puro sin corte diagonal | **PASS** |
| 18 | `TestSimetria` | `test_simetria_factibilidad_cuadrantes` | Identidad en los 4 cuadrantes ($\pm x, \pm y$) | **PASS** |
| 19 | `TestSimetria` | `test_permutacion_fuerzas_reflexion` | Mapeo exacto bajo reflexiones $x \to -x$ e $y \to -y$ | **PASS** |
| 20 | `TestMasa5kgCGCentrado` | `test_centrado_Fmax_20_58` | $5\text{ kg}$ centrado con $20.58\text{ N}$: $f_i = 12.258\text{ N}$, margen $8.32\text{ N}$ | **PASS** |
| 21 | `TestMasa5kgCGCentrado` | `test_centrado_Fmax_25_00` | $5\text{ kg}$ centrado con $25.00\text{ N}$: $f_i = 12.258\text{ N}$, margen $12.74\text{ N}$ | **PASS** |
| 22 | `TestCGenBorde` | `test_borde_longitudinal_5kg_20_58` | $x = 0.160\text{ m}$ con $20.58\text{ N} \implies$ No Factible ($\Delta f_4 = -7.87\text{ N}$) | **PASS** |
| 23 | `TestCGenBorde` | `test_borde_longitudinal_5kg_25_00` | $x = 0.160\text{ m}$ con $25.00\text{ N} \implies$ Factible en límite exacto | **PASS** |
| 24 | `TestCGenBorde` | `test_borde_lateral_5kg` | $y = 0.076\text{ m}$ con $20.58\text{ N}$ (No) vs $25.00\text{ N}$ (Sí) | **PASS** |
| 25 | `TestCGenBorde` | `test_esquina_5kg_no_factible_ambos` | $(0.160, 0.076)\text{ m}$ no factible en ambos límites | **PASS** |
| 26 | `TestCGenBorde` | `test_borde_masa_reducida_3_5kg` | $m = 3.5\text{ kg}$ en borde $x = 0.160\text{ m}$ con $20.58\text{ N} \implies$ Factible | **PASS** |
| 27 | `TestCGenBorde` | `test_consistencia_informe_vertical` | Puntos $x=0.096\text{ m}$ (Sí) y $x=0.120\text{ m}$ (No) según informe previo | **PASS** |
| 28 | `TestFaltaDeFuerzaTotal` | `test_fmax_insuficiente_para_5kg` | $F_{\text{máx}} = 10\text{ N} \implies 4 F_{\text{máx}} < W$, infactible global | **PASS** |
| 29 | `TestFaltaDeFuerzaTotal` | `test_masa_10kg` | $10\text{ kg}$: infactible con $20.58\text{ N}$, factible centrado con $25.00\text{ N}$ | **PASS** |
| 30 | `TestConstruccionYVerificacionNumerica` | `test_barrido_interior_consistencia` | Residuales numéricos $< 10^{-10}$ en barrido interior completo | **PASS** |

Adicionalmente, se comprobaron:
- **1,681 puntos estructurados en malla 2D** verificando concordancia exacta entre `derivar_limites_f4` y la fórmula analítica cerrada `max_fuerza_vertical_admisible` (0 discrepancias).
- **20,000 puntos aleatorios continuos** en el plano $[-1.2 L_x, 1.2 L_x] \times [-1.2 L_y, 1.2 L_y]$ sin una sola inconsistencia de umbral.

---

## 8. Limitaciones Técnicas del Análisis Realizado

1. **Modelo Estático Estricto:**
   El análisis asume equilibrio estático estacionario puro en sustentación vertical. No incluye dinámica de traslación ni rotación, matrices de inercia acopladas, amortiguamiento aerodinámico, ni tiempo de respuesta o ancho de banda de los variadores electrónicos de velocidad (ESC/motores).
2. **Ausencia de Mapa Instalado Aerodinámico:**
   No se modelan pérdidas de flujo por labios de entrada, interacción ventilador-conducto, contrapresión de salida, soplado sobre fuselaje, ni pérdidas de rendimiento aerodinámico por efecto suelo o proximidad de paredes (`installed_map_available: false`).
3. **Ausencia de Fuerzas Horizontales y Acoplamiento de Viento:**
   Se desprecia cualquier perturbación de viento lateral, fuerza de arrastre o momento de guiñada por sustentación asimétrica ($F_x = F_y = M_z = 0$).
4. **Desacoplamiento Giroscópico:**
   No se modelan los pares giroscópicos inducidos durante variaciones rápidas de aceleración angular de los cuatro rotores.
5. **Carácter Conceptual de Masa y Geometría:**
   La masa de $5.0\text{ kg}$ y las posiciones evaluadas del centro de gravedad son hipótesis preliminares de integración geométrica CAD. No constituyen datos experimentales medidos de un vehículo fabricado.

---

## 9. Registro de Entregables Generados

Todos los archivos generados se ubican exclusivamente dentro de la carpeta `salidas/`:

1. **`salidas/equilibrio_cg.py`**:
   Módulo analítico en Python con la formulación matemática de equilibrio, desacoplamiento por bordes, derivación de cotas de $f_4$, resolución constructiva de fuerzas (centro y pseudo-inversa proyectada) y cálculo analítico de capacidad vertical máxima.
2. **`salidas/test_equilibrio.py`**:
   Suite de pruebas automatizada ampliada a 30 casos de prueba unitarios rigurosos, cubriendo signos, rotaciones, bordes físicos, singularidades, regímenes topológicos y cotas extremas.
3. **`salidas/REVISION.md`**:
   El presente informe técnico de auditoría analítica e ingeniería matemática.
