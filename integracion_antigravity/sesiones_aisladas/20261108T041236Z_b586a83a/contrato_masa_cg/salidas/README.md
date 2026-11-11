# Contrato Versionado para Masa, Centro de Gravedad (CG) y Tensor de Inercia

Este repositorio contiene la especificación formal, el esquema JSON versionado, la implementación de referencia en **Python estándar** (sin dependencias externas), el conjunto de pruebas unitarias automatizadas y los ejemplos puramente sintéticos para la gestión rigurosa de propiedades inerciales en vehículos aeronáuticos.

---

## 1. Motivación y Arquitectura del Contrato

En proyectos aeronáuticos de alta fidelidad, la propagación descuidada de magnitudes inerciales conduce a fallos graves de simulación y control. Entre los problemas más frecuentes se encuentran:
1. **Confusión epistémica:** Mezclar valores medidos en banco con presupuestos preliminares o estimaciones CAD sin trazabilidad de su procedencia.
2. **Sustitución indebida de `null` por cero:** Asumir que una bahía o reserva sin masa asignada tiene masa 0 kg (o masa arbitraria no nula), desvirtuando el balance de masas y saturando artificialmente los algoritmos de asignación de control.
3. **Inconsistencia de marcos coordenados:** Incompatibilidad entre el datum de herramientas CAD (frecuentemente con la nariz orientada hacia $-X$) y los marcos de cuerpo de dinámica de vuelo (típicamente **FLU**: *Forward-Left-Up*).
4. **Matrices no físicas:** Tensores con elementos infinitos/NaN, asimetría por error de redondeo, o tensores que producen energías cinéticas rotacionales negativas ($T < 0$).
5. **Falsa suficiencia de la condición PSD:** Asumir erróneamente que si un tensor es semidefinido positivo (PSD), representa automáticamente un cuerpo físico real.

El presente contrato formaliza estas restricciones mediante el esquema versionado `1.0.0`.

---

## 2. Especificación del Contrato (`version_esquema: 1.0.0`)

El contrato está definido en [`esquema_contrato_v1.json`](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_masa_cg/salidas/esquema_contrato_v1.json) e implementado en [`contrato.py`](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_masa_cg/salidas/contrato.py).

### 2.1. Estructura de Campos

| Campo | Tipo | Obligatorio | Descripción |
| :--- | :--- | :--- | :--- |
| `version_esquema` | `string` | Sí | Versión semántica (`"1.0.0"`). |
| `id_contrato` | `string` | Sí | Identificador alfanumérico único de la instancia. |
| `fecha` | `string` | Sí | Fecha de registro o emisión (ISO-8601 o `YYYY-MM-DD`). |
| `unidades_canonicas` | `object` | Sí | Unidades SI canónicas: `masa: "kg"`, `longitud: "m"`, `inercia: "kg m^2"`, `angulo: "rad"`. |
| `masa` | `PropiedadMasa` | Sí | Escalar de masa en kg con trazabilidad. Si es `null`, NUNCA se sustituye por cero. |
| `posicion_cg` | `PropiedadPosicionCG` | Sí | Vector `[x, y, z]` en metros, marco (`"CAD"` o `"FLU"`), origen de referencia y trazabilidad. |
| `tensor_inercia_cg`| `PropiedadTensorInerciaCG` | Sí | Matriz 3x3 en $\text{kg}\cdot\text{m}^2$ respecto al CG, marco (`"CAD"` o `"FLU"`), flag `respecto_al_cg: true` y trazabilidad. |
| `notas_adicionales` | `string` | No | Observaciones técnicas adicionales o notas de auditoría. |

### 2.2. Trazabilidad Epistémica Obligatoria

Cada propiedad (`masa`, `posicion_cg`, `tensor_inercia_cg`) incorpora un bloque `trazabilidad`:
- `naturaleza`:
  - `"medido"`: Obtenido de pruebas físicas reales (balanza de precisión, banco de pesaje en tres apoyos, péndulo trifilar).
  - `"supuesto"`: Hipótesis de diseño, asignación presupuestaria top-down o cota teórica.
  - `"calculado"`: Resultado de integración volumétrica CAD, discretización de mallas o simulaciones multibody.
  - `"no_asignado"`: Reserva volumétrica o componente pendiente de definición/pesaje.
- `fuente`: Documento, archivo o banco de origen (ej. `"banco_pesaje_estatico_sintetico_01"`).
- `metodo`: Técnica empleada (ej. `"oscilacion_trifilar_tres_orientaciones"`).
- `fecha`: Fecha de captura del dato.
- `incertidumbre`: Margen de error o banda de confianza (ej. `"±0.005 kg"`).
- `notas`: Restricciones o condiciones de contorno.

---

## 3. Reglas de Validación en Python Estándar

Todas las validaciones están programadas en Python estándar (`contrato.py`), sin depender de `numpy`, `scipy` ni paquetes externos:

### 3.1. Matriz 3x3 Finita
- Comprueba que la estructura tenga exactamente 3 filas y 3 columnas.
- Cada elemento $M_{ij}$ debe ser estrictamente numérico (`float` o `int`).
- Todo elemento debe ser finito mediante `math.isfinite(M_ij)`. Se rechazan determinantemente valores `None`, `NaN`, `+Inf` y `-Inf`.

### 3.2. Simetría
- Todo tensor de inercia físico es un tensor simétrico de segundo orden: $I = I^T$.
- Se verifica $|I_{ij} - I_{ji}| \le \text{tol}$ para todo $i \ne j$.
- Tolerancia por defecto: $\text{tol} = 10^{-9}$.

### 3.3. Masa Positiva y Política Estricta de Null
- Si la masa está presente, debe ser estrictamente positiva: $m > 0$ kg y finita ($m \le 0$ es rechazado).
- **Regla inquebrantable:** *Nunca sustituyas null por cero ni infieras que una reserva sin masa asignada tenga masa real nula o no nula.*
- Si `valor_kg` es `null`, se conserva como `null`.
- El método `obtener_masa_estricta(contrato)` lanza `ValueError` si se intenta forzar una conversión numérica en una reserva no asignada, evitando que códigos de dinámica o control inicialicen masa nula (que produciría división por cero en $\mathbf{F}/m$) o masa espuria.

### 3.4. Energía Cinética No Negativa mediante Menores Principales (PSD)
La energía cinética rotacional de un cuerpo rígido con velocidad angular $\boldsymbol{\omega} = [\omega_x, \omega_y, \omega_z]^T$ es:
$$T_{\text{rot}} = \frac{1}{2} \boldsymbol{\omega}^T \mathbf{I}_{\text{CG}} \boldsymbol{\omega}$$

Por leyes fundamentales de la física clásica, $T_{\text{rot}} \ge 0$ para cualquier vector $\boldsymbol{\omega} \in \mathbb{R}^3$. Esto exige que $\mathbf{I}_{\text{CG}}$ sea una matriz **semidefinida positiva (PSD)**.

En álgebra lineal, una matriz simétrica real $3 \times 3$ es semidefinida positiva si y solo si **todos sus menores principales** (los 7 menores principales de órdenes 1, 2 y 3) son mayores o iguales a cero ($\ge -\text{tol}_{\text{psd}}$):
1. **Menores de Orden 1 (elementos de la diagonal principal):**
   $$M_0 = I_{00} \ge 0, \quad M_1 = I_{11} \ge 0, \quad M_2 = I_{22} \ge 0$$
2. **Menores de Orden 2 (determinantes de submatrices principales $2 \times 2$):**
   $$M_{01} = I_{00} I_{11} - I_{01}^2 \ge 0$$
   $$M_{02} = I_{00} I_{22} - I_{02}^2 \ge 0$$
   $$M_{12} = I_{11} I_{22} - I_{12}^2 \ge 0$$
3. **Menor de Orden 3 (determinante completo $3 \times 3$):**
   $$\det(\mathbf{I}) = I_{00}(I_{11} I_{22} - I_{12}^2) - I_{01}(I_{10} I_{22} - I_{12} I_{02}) + I_{02}(I_{10} I_{21} - I_{11} I_{02}) \ge 0$$

Si cualquiera de estos 7 menores es negativo ($< -10^{-12}$), la matriz no es PSD y permite orientaciones de giro con energía cinética negativa, lo cual es físicamente inadmisible.

---

## 4. Advertencia Física Fundamental: La Condición PSD es Necesaria pero NO Suficiente

> [!WARNING]
> **ADVERTENCIA FÍSICA CRÍTICA:**
> La condición de semidefinición positiva (PSD, menores principales $\ge 0$) es una condición matemáticamente necesaria para garantizar que la energía cinética rotacional sea no negativa ($T = \frac{1}{2}\boldsymbol{\omega}^T \mathbf{I}\boldsymbol{\omega} \ge 0$), pero **NO ES SUFICIENTE** para aceptar una medición física ni demuestra que el tensor cumpla todas las restricciones de un cuerpo físico real.

### ¿Por qué PSD no es suficiente?

1. **Desigualdades triangulares de una distribución continua de masa tridimensional:**
   Para cualquier cuerpo físico en $\mathbb{R}^3$ con densidad de masa $\rho(\mathbf{r}) \ge 0$:
   $$I_{xx} = \int (y^2 + z^2) \, dm, \quad I_{yy} = \int (x^2 + z^2) \, dm, \quad I_{zz} = \int (x^2 + y^2) \, dm$$
   Sumando dos componentes diagonales cualesquiera:
   $$I_{xx} + I_{yy} = \int (x^2 + y^2 + 2z^2) \, dm = I_{zz} + 2 \int z^2 \, dm \ge I_{zz}$$
   Por lo tanto, los momentos de inercia respecto a cualquier sistema ortogonal de ejes (y especialmente en los ejes principales) **deben satisfacer obligatoriamente las desigualdades triangulares:**
   $$I_{xx} + I_{yy} \ge I_{zz}$$
   $$I_{xx} + I_{zz} \ge I_{yy}$$
   $$I_{yy} + I_{zz} \ge I_{xx}$$

   **Contraejemplo ilustrativo:**
   Considérese el tensor diagonal sintético (suministrado en [`06_sintetico_psd_pero_no_fisico.json`](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_masa_cg/salidas/ejemplos_sinteticos/06_sintetico_psd_pero_no_fisico.json)):
   $$\mathbf{I} = \begin{pmatrix} 0.200 & 0 & 0 \\ 0 & 0.050 & 0 \\ 0 & 0 & 0.050 \end{pmatrix}$$
   - *Comprobación PSD:*
     $M_0 = 0.200 > 0$, $M_1 = 0.050 > 0$, $M_2 = 0.050 > 0$.
     $M_{01} = 0.010 > 0$, $M_{02} = 0.010 > 0$, $M_{12} = 0.0025 > 0$.
     $\det(\mathbf{I}) = 0.0005 > 0$.
     **Es estrictamente definida positiva (y por tanto PSD). Cumple $T > 0$.**
   - *Comprobación de cuerpo físico tridimensional:*
     $$I_{yy} + I_{zz} = 0.050 + 0.050 = 0.100 < 0.200 = I_{xx}$$
     **¡Viola la desigualdad triangular por 0.100 $\text{kg}\cdot\text{m}^2$!**
     **Conclusión:** Es imposible que exista un cuerpo rígido tridimensional real con esta inercia, a pesar de ser PSD.

2. **No garantiza ausencia de errores experimentales o de instrumentación:**
   Un banco de ensayo (péndulo de torsión, péndulo bifilar/trifilar) con fricción en apoyos, acoplamiento aeroelástico parásito, deformación de hilos o calibración deficiente puede generar numéricamente una matriz PSD sin que los coeficientes correspondan a la inercia real del vehículo.
3. **No verifica compatibilidad geométrica con la envolvente exterior:**
   Un tensor puede ser PSD y satisfacer las desigualdades triangulares pero exigir que la masa esté concentrada fuera de la carrocería del vehículo (es decir, radios de giro mayores que la semienvergadura o semilongitud).
4. **No garantiza consistencia baricéntrica (Teorema de Steiner):**
   El tensor respecto al CG debe ser el tensor de mínima traza respecto a cualquier traslación paralela ($\mathbf{I}_P = \mathbf{I}_{\text{CG}} + m [(\mathbf{d}^T\mathbf{d})\mathbf{E} - \mathbf{d}\mathbf{d}^T]$). Un tensor medido fuera de baricentro o con CG mal estimado invalida las ecuaciones de Newton-Euler rotacionales puras.

---

## 5. Conversión de Coordenadas: CAD a FLU mediante $\operatorname{diag}(-1, -1, 1)$

### 5.1. Definición de Marcos
- **Marco CAD:**
  - Origen: Datum del ensamblaje CAD (`CAD_DATUM`).
  - Eje $X_{\text{CAD}}$: Eje longitudinal con la **nariz en $X$ negativo** (convención canónica del modelo base).
  - Eje $Y_{\text{CAD}}$: Lateral derecho/izquierdo.
  - Eje $Z_{\text{CAD}}$: Vertical hacia arriba.
- **Marco FLU (Flight Body Frame):**
  - Eje $X_{\text{FLU}}$: **Forward** (hacia la proa/nariz del vehículo).
  - Eje $Y_{\text{FLU}}$: **Left** (hacia la izquierda del piloto/vehículo).
  - Eje $Z_{\text{FLU}}$: **Up** (hacia arriba).

### 5.2. Matriz de Transformación
La matriz de rotación de cambio de base es:
$$\mathbf{R}_{\text{CAD}\to\text{FLU}} = \begin{pmatrix} -1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \end{pmatrix} = \operatorname{diag}(-1, -1, 1)$$

### 5.3. Transformación de Posición del CG
Para un vector de posición baricéntrico $\mathbf{r}_{\text{CAD}} = [x, y, z]^T$:
$$\mathbf{r}_{\text{FLU}} = \mathbf{R}_{\text{CAD}\to\text{FLU}} \, \mathbf{r}_{\text{CAD}} = \begin{bmatrix} -x \\ -y \\ z \end{bmatrix}$$
*Ejemplo:* Si el CG en CAD está en $x = -0.020$ m (adelantado hacia la nariz), en FLU pasa a $x = +0.020$ m (hacia adelante).
*Regla estricta:* Si $\mathbf{r}_{\text{CAD}}$ es `null`, se preserva estrictamente como `null`; **nunca se sustituye por $[0, 0, 0]$**.

### 5.4. Transformación del Tensor de Inercia
El tensor de inercia $\mathbf{I}_{\text{CAD}}$ se transforma bajo el cambio ortogonal $\mathbf{R}$ mediante:
$$\mathbf{I}_{\text{FLU}} = \mathbf{R} \, \mathbf{I}_{\text{CAD}} \, \mathbf{R}^T$$
Dado que $\mathbf{R} = \mathbf{R}^T = \operatorname{diag}(-1, -1, 1)$:
$$\mathbf{I}_{\text{FLU}} = \begin{pmatrix} -1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \end{pmatrix} \begin{pmatrix} I_{xx} & I_{xy} & I_{xz} \\ I_{yx} & I_{yy} & I_{yz} \\ I_{zx} & I_{zy} & I_{zz} \end{pmatrix} \begin{pmatrix} -1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \end{pmatrix} = \begin{pmatrix} I_{xx} & I_{xy} & -I_{xz} \\ I_{yx} & I_{yy} & -I_{yz} \\ -I_{zx} & -I_{zy} & I_{zz} \end{pmatrix}$$
- Los momentos principales en la diagonal ($I_{xx}, I_{yy}, I_{zz}$) y el producto cruzado $I_{xy}$ **conservan idéntico valor y signo**.
- Los términos de acoplamiento con el eje vertical ($I_{xz}$ e $I_{yz}$) **invierten su signo algebraico**.
*Regla estricta:* Si el tensor es `null`, se preserva estrictamente como `null`; **nunca se sustituye por una matriz nula**.

---

## 6. Catálogo de Ejemplos Puramente Sintéticos

En [`salidas/ejemplos_sinteticos/`](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_masa_cg/salidas/ejemplos_sinteticos) se proporcionan 7 instancias sintéticas (sin autores, marcas ni mediciones inventadas):

| Archivo | Naturaleza | Estado Esperado | Propósito / Características |
| :--- | :--- | :--- | :--- |
| [`01_sintetico_medido_completo.json`](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_masa_cg/salidas/ejemplos_sinteticos/01_sintetico_medido_completo.json) | `medido` | **VÁLIDO** | Vehículo completamente medido en banco sintético; tensor simétrico, PSD y conforme a desigualdades triangulares físicas. |
| [`02_sintetico_supuesto_diseno.json`](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_masa_cg/salidas/ejemplos_sinteticos/02_sintetico_supuesto_diseno.json) | `supuesto` | **VÁLIDO** | Presupuesto preliminar top-down (5.0 kg objetivo, CG nominal y tensor diagonal estimado). |
| [`03_sintetico_reserva_no_asignada.json`](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_masa_cg/salidas/ejemplos_sinteticos/03_sintetico_reserva_no_asignada.json) | `no_asignado`| **VÁLIDO (Reserva)** | Reserva volumétrica interna con masa, CG e inercia `null`. Demuestra la preservación obligatoria de `null` sin asumir cero ni no nulo. |
| [`04_sintetico_invalido_no_simetrico.json`](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_masa_cg/salidas/ejemplos_sinteticos/04_sintetico_invalido_no_simetrico.json) | `calculado` | **RECHAZADO** | Tensor asimétrico ($I_{xy} = 0.020 \ne 0.005 = I_{yx}$). Detectado y rechazado por el validador de simetría. |
| [`05_sintetico_invalido_no_psd.json`](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_masa_cg/salidas/ejemplos_sinteticos/05_sintetico_invalido_no_psd.json) | `calculado` | **RECHAZADO** | Tensor simétrico pero no PSD ($M_{01} = -0.0039 < 0, \det = -0.00039 < 0$). Violación de energía cinética no negativa. |
| [`06_sintetico_psd_pero_no_fisico.json`](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_masa_cg/salidas/ejemplos_sinteticos/06_sintetico_psd_pero_no_fisico.json) | `medido` | **ADVERTENCIA FÍSICA** | Tensor estrictamente PSD pero que viola $I_{yy} + I_{zz} \ge I_{xx}$ ($0.100 < 0.200$). Demuestra por qué PSD es insuficiente para aceptar medición física. |
| [`07_sintetico_cad_para_conversion.json`](file:///private/tmp/aero_20261108T041236Z_b586a83a_abiz4snh/contrato_masa_cg/salidas/ejemplos_sinteticos/07_sintetico_cad_para_conversion.json) | `calculado` | **VÁLIDO** | Vehículo en marco CAD (nariz en $-X$) listo para transformación a FLU mediante `diag(-1,-1,1)`. |

---

## 7. Instrucciones de Uso y Comprobación

### 7.1. Ejecución de la Suite de Pruebas Unitarias
Toda la suite corre en el sandbox con la biblioteca estándar de Python:
```bash
python3 -m unittest salidas/test_contrato.py
```
Resultado: 38 pruebas unitarias automatizadas cubriendo finitud 3x3, simetría, masa positiva, menores principales, invariancia y sign-flip en FLU, preservación estricta de null y validación de ejemplos.

### 7.2. Uso de la Herramienta CLI de Validación
Para validar cualquier archivo de contrato:
```bash
python3 salidas/contrato.py salidas/ejemplos_sinteticos/01_sintetico_medido_completo.json
```

Para transformar un contrato desde marco CAD a marco de vuelo FLU aplicando $\operatorname{diag}(-1, -1, 1)$:
```bash
python3 salidas/contrato.py salidas/ejemplos_sinteticos/07_sintetico_cad_para_conversion.json --convertir-flu
```

Para guardar la versión transformada en un nuevo archivo:
```bash
python3 salidas/contrato.py salidas/ejemplos_sinteticos/07_sintetico_cad_para_conversion.json --convertir-flu --guardar salidas/07_sintetico_convertido_a_flu.json
```

Para validar en modo estricto exigiendo asignación completa (rechazando `null` sin convertirlo a cero):
```bash
python3 salidas/contrato.py salidas/ejemplos_sinteticos/03_sintetico_reserva_no_asignada.json --exigir-completo
```

---

## 8. Limitaciones y Alcance

1. **Restricción a Modelo de Cuerpo Rígido:** El contrato modela magnitudes de masa concentrada e inercia baricéntrica para dinámica de cuerpo rígido de 6 grados de libertad (6-DOF). No modela modos de deformación aeroelástica, flexibilidad estructural ni oleaje de combustible (*sloshing*).
2. **Dependencia de la Estructura de Ejes:** La transformación $\operatorname{diag}(-1, -1, 1)$ es específica para la convención de carrocería con proa en $-X_{\text{CAD}}$, lateral en $Y_{\text{CAD}}$ y vertical en $+Z_{\text{CAD}}$ hacia un sistema de cuerpo **FLU** ($+X$ proa, $+Y$ babor/izquierda, $+Z$ cenit/arriba). Otras convenciones (ej. NED: *North-East-Down* o FRD: *Forward-Right-Down*) requieren matrices de rotación diferentes.
3. **Insuficiencia Intrínseca de la Validación Numérica PSD:** Como se detalla en la Sección 4, la verificación de menores principales $\ge 0$ garantiza que las ecuaciones de dinámica de actitud no diverjan por energía cinética negativa, pero no reemplaza la inspección geométrica de envolvente, la verificación de tolerancias de pesaje ni la calibración rigurosa de bancos de ensayo físicos.
4. **Reserva sin Masa:** Una reserva con valores `null` no aporta información inercial. Los algoritmos de simulación que requieran evaluar trayectorias físicas deben detenerse o exigir un escenario explícito de asignación de masa antes de propagar estados dinámicos.
