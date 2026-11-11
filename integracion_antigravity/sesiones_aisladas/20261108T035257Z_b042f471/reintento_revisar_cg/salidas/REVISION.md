# AUDITORÍA TÉCNICA: CONDICIONES ANALÍTICAS DE FACTIBILIDAD 2D DE EQUILIBRIO VERTICAL (CONFIGURACIÓN C02)

**Documento:** `REVISION.md`  
**Fecha de auditoría:** 7 de noviembre de 2026  
**Entorno de ejecución:** Espacio aislado `salidas/` (sandbox local)  
**Código auditado:** `salidas/equilibrio_cg.py` y `salidas/test_equilibrio.py`  

---

## 1. Declaración de Integridad Metodológica y Datos

Para asegurar trazabilidad rigurosa y evitar la asunción errónea de datos conceptuales como verificados, se clasifica la totalidad de los parámetros según su origen:

| Categoría | Parámetro | Valor y Unidades | Fuente / Justificación | Estado de Validación |
| :--- | :--- | :--- | :--- | :--- |
| **Datos Medidos** | *Ninguno* | — | Fase conceptual C02 (`C02_CANDIDATA.json`): `actual_mass_kg: null`, `actual_CG_m: null`, `actual_inertia_kgm2: null`, `installed_map_available: false`. | **No medido** |
| **Supuestos de Referencia** | Semibrazo longitudinal $L_x$ | $0.160\text{ m}$ ($160\text{ mm}$) | Centros geométricos de propulsores en modelo CAD oficial (`centres_xy_m`). | Supuesto CAD nominal |
| **Supuestos de Referencia** | Semibrazo lateral $L_y$ | $0.076\text{ m}$ ($76\text{ mm}$) | Centros geométricos de propulsores en modelo CAD oficial (`centres_xy_m`). | Supuesto CAD nominal |
| **Supuestos de Referencia** | Masa de integración $m$ | $5.0\text{ kg}$ | Meta de integración de diseño (`integration_reference_mass_target_kg: 5`). | **Supuesto de diseño (NO medido)** |
| **Supuestos de Referencia** | CG nominal | $(x_{cg}, y_{cg}) = (0.0, 0.0)\text{ m}$ | Hipótesis de simetría de diseño ideal. | **Supuesto de diseño (NO medido)** |
| **Supuestos de Referencia** | Aceleración de gravedad $g$ | $9.80665\text{ m/s}^2$ | Constante estándar internacional de referencia operativa. | Referencia estándar |
| **Supuestos de Referencia** | Empuje máximo base $F_{\text{máx}, 1}$ | $20.58\text{ N}$ | Hipótesis ideal de partida no calificada (`INFORME-VERTICAL.md`). | Supuesto preliminar |
| **Supuestos de Referencia** | Empuje máximo alternativo $F_{\text{máx}, 2}$ | $25.00\text{ N}$ | Hipótesis de dimensionamiento complementario. | Supuesto de diseño |
| **Cálculos** | Peso estático de diseño $W$ | $49.03325\text{ N}$ | $W = m \cdot g = 5.0 \times 9.80665\text{ N}$. | Calculado |
| **Cálculos** | Cotas analíticas $[f_{4,\min}, f_{4,\max}]$ | $[f_{4,\min}, f_{4,\max}]\text{ N}$ | Intersección analítica de 8 desigualdades primarias. | Calculado y verificado |
| **Cálculos** | Fuerzas de actuadores $f_1, f_2, f_3, f_4$ | $[0, F_{\text{máx}}]\text{ N}$ | Asignación constructiva (centro o pseudo-inversa proyectada). | Calculado y verificado |
| **Cálculos** | Capacidad vertical máxima $F_{z,\max}$ | $\text{N}$ | Fórmula analítica desacoplada de bordes y esquinas. | Calculado y verificado |

> [!IMPORTANT]
> **Aclaración sobre el Centro de Gravedad:** El centro de gravedad $(0, 0)\text{ m}$ y la masa de $5.0\text{ kg}$ constituyen metas y supuestos de trabajo de ingeniería; bajo ninguna circunstancia deben presentarse ni interpretarse como valores medidos en banco de pruebas o prototipo físico.

---

## 2. Auditoría de Ecuaciones, Convención de Signos y Geometría

### 2.1 Sistema de Coordenadas y Ubicación de Actuadores
El modelo adopta el sistema de coordenadas CAD oficial:
- Eje $+x$: Longitudinal orientado hacia la cola (nariz en $-x$, cola en $+x$).
- Eje $+y$: Lateral orientado hacia babor/izquierda (estribor/derecha en $-y$).
- Eje $+z$: Vertical ascendente.

*(Nota aeronáutica: Si se compara con la convención de vuelo FLU —Forward-Left-Up—, el eje longitudinal invierte signo: $x_{\text{FLU}} = -x_{\text{CAD}}$, mientras que el eje lateral se mantiene orientado a babor).*

Las posiciones de los cuatro módulos propulsores son:
$$\mathbf{r}_1 = (-L_x, -L_y), \quad \mathbf{r}_2 = (-L_x, +L_y), \quad \mathbf{r}_3 = (+L_x, -L_y), \quad \mathbf{r}_4 = (+L_x, +L_y)$$

### 2.2 Verificación de Signos de Equilibrio
El peso ejerce $\vec{W} = -W\,\hat{k}$ en $(x_{cg}, y_{cg})$. Cada motor ejerce empuje ascendente $\vec{F}_i = f_i\,\hat{k}$ ($f_i \ge 0$).

1. **Fuerza vertical pura ($\sum F_z = 0$):**
   $$\sum_{i=1}^4 f_i = W$$
2. **Momento de cabeceo ($\sum M_y = 0$ alrededor del eje $y$ transversal):**
   $$\sum_{i=1}^4 x_i f_i = x_{cg} W \iff -L_x (f_1 + f_2) + L_x (f_3 + f_4) = x_{cg} W$$
   *Auditoría de signo:* Si $x_{cg} > 0$ (CG desplazado a popa/cola), el peso induce momento a encabuzar/bajar cola; para equilibrar, los propulsores traseros $(f_3 + f_4)$ deben ejercer mayor empuje que los delanteros $(f_1 + f_2)$. La ecuación produce:
   $$S_{\text{rear}} = f_3 + f_4 = \frac{W}{2}\left(1 + \frac{x_{cg}}{L_x}\right) > \frac{W}{2}$$
   Signo verificado: **CORRECTO**.
3. **Momento de alabeo ($\sum M_x = 0$ alrededor del eje $x$ longitudinal):**
   $$\sum_{i=1}^4 y_i f_i = y_{cg} W \iff -L_y (f_1 + f_3) + L_y (f_2 + f_4) = y_{cg} W$$
   *Auditoría de signo:* Si $y_{cg} > 0$ (CG desplazado a babor/izquierda), el peso baja el lado izquierdo; para equilibrar, los propulsores izquierdos $(f_2 + f_4)$ deben aumentar. La ecuación produce:
   $$S_{\text{left}} = f_2 + f_4 = \frac{W}{2}\left(1 + \frac{y_{cg}}{L_y}\right) > \frac{W}{2}$$
   Signo verificado: **CORRECTO**.

---

## 3. Auditoría de Factibilidad Analítica y Espacio Nulo

### 3.1 Espacio Nulo de la Matriz de Efectividad
El sistema $A \mathbf{f} = \mathbf{b}$ con:
$$A = \begin{bmatrix} 1 & 1 & 1 & 1 \\ -L_x & -L_x & L_x & L_x \\ -L_y & L_y & -L_y & L_y \end{bmatrix}, \quad \mathbf{b} = \begin{bmatrix} W \\ x_{cg} W \\ y_{cg} W \end{bmatrix}$$
posee filas mutuamente ortogonales ($r_i \cdot r_j = 0$ para $i \neq j$), por lo que $\operatorname{rango}(A) = 3$. El espacio nulo es de dimensión 1, generado por:
$$\mathbf{v}_{\text{null}} = \begin{bmatrix} +1 \\ -1 \\ -1 \\ +1 \end{bmatrix}$$
Cualquier solución se expresa en función de $f_4$:
$$f_3 = S_{\text{rear}} - f_4, \quad f_2 = S_{\text{left}} - f_4, \quad f_1 = S_{\text{front}} - S_{\text{left}} + f_4$$

### 3.2 Cotas Analíticas de $f_4$ y las 16 Desigualdades Cruzadas
Imponiendo $0 \le f_i \le F_{\text{máx}}$ para $i=1,2,3,4$:
- Cotas inferiores: $L_1 = S_{\text{left}} - S_{\text{front}}$, $L_2 = S_{\text{left}} - F_{\text{máx}}$, $L_3 = S_{\text{rear}} - F_{\text{máx}}$, $L_4 = 0$.
- Cotas superiores: $U_1 = L_1 + F_{\text{máx}}$, $U_2 = S_{\text{left}}$, $U_3 = S_{\text{rear}}$, $U_4 = F_{\text{máx}}$.

La condición necesaria y suficiente de factibilidad es:
$$f_{4,\min} = \max_i L_i \le \min_j U_j = f_{4,\max} \quad \text{y} \quad W \ge 0$$
Al expandir las 16 condiciones $L_i \le U_j$:
1. $L_i \le U_i \iff F_{\text{máx}} \ge 0$ (4 identidades).
2. No negatividad de totales marginales (4 condiciones):
   - $L_1 \le U_2 \implies S_{\text{front}} \ge 0 \iff x_{cg} \le L_x$
   - $L_4 \le U_3 \implies S_{\text{rear}} \ge 0 \iff x_{cg} \ge -L_x$
   - $L_4 \le U_2 \implies S_{\text{left}} \ge 0 \iff y_{cg} \ge -L_y$
   - $L_1 \le U_3 \implies S_{\text{right}} \ge 0 \iff y_{cg} \le L_y$
   *(El CG debe estar dentro del rectángulo geométrico $[-L_x, L_x] \times [-L_y, L_y]$).*
3. Capacidad de pares de actuadores (4 condiciones):
   - $L_3 \le U_4 \implies S_{\text{rear}} \le 2 F_{\text{máx}} \iff W(1 + x_{cg}/L_x) \le 4 F_{\text{máx}}$
   - $L_2 \le U_1 \implies S_{\text{front}} \le 2 F_{\text{máx}} \iff W(1 - x_{cg}/L_x) \le 4 F_{\text{máx}}$
   - $L_2 \le U_4 \implies S_{\text{left}} \le 2 F_{\text{máx}} \iff W(1 + y_{cg}/L_y) \le 4 F_{\text{máx}}$
   - $L_3 \le U_1 \implies S_{\text{right}} \le 2 F_{\text{máx}} \iff W(1 - y_{cg}/L_y) \le 4 F_{\text{máx}}$
4. Saturación de esquina / acoplamiento diagonal (4 condiciones):
   - $L_1 \le U_4 \iff \frac{W}{2}\left(\frac{x_{cg}}{L_x} + \frac{y_{cg}}{L_y}\right) \le F_{\text{máx}}$
   - $L_4 \le U_1 \iff \frac{W}{2}\left(-\frac{x_{cg}}{L_x} - \frac{y_{cg}}{L_y}\right) \le F_{\text{máx}}$
   - $L_3 \le U_2 \iff \frac{W}{2}\left(\frac{x_{cg}}{L_x} - \frac{y_{cg}}{L_y}\right) \le F_{\text{máx}}$
   - $L_2 \le U_3 \iff \frac{W}{2}\left(-\frac{x_{cg}}{L_x} + \frac{y_{cg}}{L_y}\right) \le F_{\text{máx}}$
   Equivalentes a:
   $$\left| \frac{x_{cg}}{L_x} \pm \frac{y_{cg}}{L_y} \right| \le \frac{2 F_{\text{máx}}}{W}$$

Esto define rigurosamente un **octógono convexo de sustentación** en el plano $(x_{cg}, y_{cg})$. La capacidad vertical admisible en cualquier punto $(x_{cg}, y_{cg})$ es:
$$F_{z,\max}(x_{cg}, y_{cg}) = \min\left( 4 F_{\text{máx}}, \; \frac{4 F_{\text{máx}}}{1 + \frac{|x_{cg}|}{L_x}}, \; \frac{4 F_{\text{máx}}}{1 + \frac{|y_{cg}|}{L_y}}, \; \frac{2 F_{\text{máx}}}{\frac{|x_{cg}|}{L_x} + \frac{|y_{cg}|}{L_y}} \right)$$
para $|x_{cg}| \le L_x$ y $|y_{cg}| \le L_y$, y cero fuera de dicho dominio.

### 3.3 Fracción Continua de Área Admisible
Integrando analíticamente el octógono sobre el rectángulo base $4 L_x L_y$ para $m = 5.0\text{ kg}$ ($W = 49.033\text{ N}$):
- Con $F_{\text{máx}} = 20.58\text{ N}$: área continua admisible = **32.65%** del rectángulo.
- Con $F_{\max} = 25.00\text{ N}$: área continua admisible = **51.95%** del rectángulo (+59.1% de incremento geométrico).

---

## 4. Auditoría de Casos en Borde y Singularidades

1. **Borde longitudinal ($x_{cg} = L_x, y_{cg} = 0$):**
   - $S_{\text{front}} = 0 \implies f_1 = f_2 = 0$.
   - $f_3 = f_4 = W/2$.
   - El intervalo colapsa a un único punto: $f_{4,\min} = f_{4,\max} = W/2$.
   - Factible si y solo si $W \le 2 F_{\text{máx}}$.
   - Para 5 kg: con $F_{\text{máx}} = 20.58\text{ N}$ ($2 F_{\text{máx}} = 41.16\text{ N} < 49.03\text{ N}$) es **NO FACTIBLE** (déficit de 7.87 N). Con $F_{\text{máx}} = 25.0\text{ N}$ ($2 F_{\text{máx}} = 50.0\text{ N} \ge 49.03\text{ N}$) es **FACTIBLE**.
2. **Borde lateral ($x_{cg} = 0, y_{cg} = L_y$):**
   - Análogo al longitudinal: $f_1 = f_3 = 0$, $f_2 = f_4 = W/2$. Factible si y solo si $W \le 2 F_{\text{máx}}$.
3. **Esquina geométrica ($x_{cg} = L_x, y_{cg} = L_y$):**
   - $S_{\text{front}} = 0$, $S_{\text{right}} = 0 \implies f_1 = f_2 = f_3 = 0$, $f_4 = W$.
   - Factible si y solo si un único motor puede soportar el peso total: $W \le F_{\text{máx}}$.
   - Para $m = 5.0\text{ kg}$ ($W = 49.03\text{ N}$): imposible en ambos empujes.
   - Para $m = 1.0\text{ kg}$ ($W = 9.81\text{ N} \le 20.58\text{ N}$): **FACTIBLE**, verificado en prueba unitaria.
4. **Saturación total en centro ($x_{cg}=0, y_{cg}=0, W = 4 F_{\text{máx}}$):**
   - Para $W = 4 \times 20.58 = 82.32\text{ N}$: solución única $f_1=f_2=f_3=f_4 = 20.58\text{ N}$, con holgura $\Delta f_4 = 0.000\text{ N}$.
   - Para $W = 82.32 + \epsilon$: $\Delta f_4 < 0$, estrictamente no factible.
5. **Cero y negatividad:**
   - $W = 0$: Solución trivial $f_i = 0$.
   - $W < 0$ o $F_{\text{máx}} \le 0$: Rechazados inmediatamente como no factibles.
   - Puntos con $|x_{cg}| > L_x$ o $|y_{cg}| > L_y$: Rechazados analíticamente ($f_{4,\min} > f_{4,\max}$).

---

## 5. Auditoría de Construcción Explícita de Fuerzas

El módulo proporciona dos esquemas explícitos de resolución:

1. **Centro del intervalo:**
   $$f_4 = \frac{f_{4,\min} + f_{4,\max}}{2}$$
   Maximiza la distancia simétrica a los límites de saturación física.
2. **Pseudo-inversa proyectada (mínima norma euclídea):**
   La solución de mínimos cuadrados no restringida es:
   $$f_{\text{LS}, i} = \frac{W}{4}\left(1 + \frac{x_i x_{cg}}{L_x^2} + \frac{y_i y_{cg}}{L_y^2}\right)$$
   Al proyectar la componente libre sobre el intervalo admisible:
   $$f_4 = \operatorname{clip}(f_{\text{LS}, 4}, \; f_{4,\min}, \; f_{4,\max})$$
   *Demostración matemática de optimalidad:* Toda solución admisible cumple $\mathbf{f}(t) = \mathbf{f}_{\text{LS}} + t\,\mathbf{v}_{\text{null}}$ con $t = f_4 - f_{\text{LS}, 4}$. La distancia euclídea al origen satisface:
   $$\|\mathbf{f}\|^2 = \|\mathbf{f}_{\text{LS}}\|^2 + t^2 \|\mathbf{v}_{\text{null}}\|^2 = \|\mathbf{f}_{\text{LS}}\|^2 + 4(f_4 - f_{\text{LS}, 4})^2$$
   Por ende, recortar $f_4$ en $[f_{4,\min}, f_{4,\max}]$ minimiza estrictamente $\|\mathbf{f}\|^2$ en el politopo cerrado de fuerzas factibles.

*Comprobación de residuales numéricos en todas las soluciones factibles:*
$$\Delta W = |\sum f_i - W| \le 10^{-12}\text{ N}, \quad |\Delta M_x| \le 10^{-12}\text{ N}\cdot\text{m}, \quad |\Delta M_y| \le 10^{-12}\text{ N}\cdot\text{m}$$

---

## 6. Resultados de Pruebas Automatizadas

Se ejecutó la suite completa en `salidas/test_equilibrio.py` con 20 pruebas unitarias:

| Suite / Clase | Casos Evaluados | Resultado |
| :--- | :--- | :---: |
| `TestSimetria` | Simetría en 4 cuadrantes e intercambios por reflexión ($x \to -x$, $y \to -y$) | **PASS (2/2)** |
| `TestMasa5kgCGCentrado` | CG centrado con $F_{\text{máx}} = 20.58\text{ N}$ y $25.00\text{ N}$, residuales nulos | **PASS (2/2)** |
| `TestCGenBorde` | Bordes longitudinales, laterales, esquinas y comparación con `INFORME-VERTICAL.md` | **PASS (6/6)** |
| `TestFaltaDeFuerzaTotal` | $F_{\text{máx}}$ insuficiente y masa excesiva de 10 kg | **PASS (2/2)** |
| `TestConstruccionYVerificacionNumerica` | Barrido interior completo con ambas estrategias y verificación de cotas | **PASS (1/1)** |
| `TestCasosBordeYPropiedadesAnaliticas` | Esquina con masa reducida (1 kg), peso cero, peso negativo, $F_{\max}$ negativo, saturación exacta 4 motores, puntos fuera del rectángulo y minimización de norma de pseudo-inversa proyectada | **PASS (7/7)** |
| **TOTAL** | **20 pruebas automatizadas** | **100% OK (0.002 s)** |

---

## 7. Limitaciones Técnicas del Análisis

1. **Modelo Estático:** No incorpora dinámica de cuerpo rígido, amortiguamiento ni respuesta en lazo cerrado de actuadores.
2. **Sin Mapa Instalado:** Supone empuje constante unidireccional sin considerar pérdidas aerodinámicas por conductos, distorsión en toberas, efecto suelo ni interacción entre flujos adyacentes.
3. **Ausencia de Fuerzas Horizontales:** No incluye viento cruzado ni desacoplamiento de ángulos de ataque de la aeronave.
4. **Efectos Giroscópicos No Modelados:** El balance de momentos asume régimen permanente; transitorios de aceleración angular de rotores introducen pares de guiñada residuales.
5. **Datos Hipotéticos:** Los cálculos dependen de la masa supuesta de 5.0 kg y la geometría nominal CAD, pendientes de validación en prototipo físico integrado.

---

## 8. Inventario de Entregables en `salidas/`

1. `salidas/equilibrio_cg.py`: Módulo analítico de verificación geométrica, derivación de intervalos y construcción de fuerzas.
2. `salidas/test_equilibrio.py`: Suite ampliada de 20 pruebas unitarias automatizadas.
3. `salidas/INFORME_EQUILIBRIO_CG.md`: Informe técnico de referencia matemática y espacial.
4. `salidas/REVISION.md`: Este reporte de auditoría técnica.