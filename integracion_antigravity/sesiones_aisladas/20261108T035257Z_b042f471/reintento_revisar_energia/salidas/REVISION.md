# REVISIÓN TÉCNICA INDEPENDIENTE: LEY DE ARRASTRE PARAMÉTRICA Y DIMENSIONAMIENTO ENERGÉTICO PARA C02 (5,0 kg)

**Fecha:** 7 de noviembre de 2026  
**Entorno:** Sandbox aislado de ejecución autónoma  
**Directorio de trabajo:** `/private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia`  
**Estado:** Verificación matemática, física y de código completada  

---

## 1. Identificación y Trazabilidad

Se ha realizado una revisión y verificación independiente de la ley de arrastre paramétrica:
$$D(v) = D_{\text{fin}} \left( \frac{v}{V} \right)^p, \quad p \in \{1, 2, 4\}$$
y su correspondiente trabajo de aceleración:
$$W_{\text{arrastre, acel}} = \frac{D_{\text{fin}} \cdot V \cdot t}{p + 2}$$
así como de las demandas de energía y potencia pico, y su comparación frente al caso base cuadrático ($p = 2$) para la aeronave conceptual **C02 (5,0 kg)**.

Todos los entregables se han colocado exclusivamente en `salidas/`. Los archivos editados se copiaron desde `entradas/` usando `shutil.copyfile` para no heredar permisos de solo lectura. No se utilizaron comandos prohibidos (`rm`, `git`), no se interactuó con procesos o contenedores externos, no se consultó la web ni MCP, y no se incluyeron credenciales o secretos.

### Fuentes de Referencia Consultadas (Solo Lectura):
- [`entradas/investigacion-aeronautica/ejecucion/G1/potencia_simultanea_c02/INFORME.md`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/entradas/investigacion-aeronautica/ejecucion/G1/potencia_simultanea_c02/INFORME.md)  
  *SHA-256:* `d7b724afd7b48b7058a1d1969afa4b869f14629d709d72e30f3170f03ee1627a`
- [`entradas/investigacion-aeronautica/ejecucion/G1/potencia_simultanea_c02/calcular_r2.py`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/entradas/investigacion-aeronautica/ejecucion/G1/potencia_simultanea_c02/calcular_r2.py)  
  *SHA-256:* `73d70339ce0ce124d239c22a4cde8282b85f77becb0d163c138301066cd3b67a`
- Sesión previa de referencia en `entradas/.../20261108T032826Z_13ced8ae/energia_ley_arrastre/salidas/`:
  - `sensibilidad_ley_arrastre.py` (SHA-256: `9fa733d0cb8d2d64098939c4a85fb2bfe60309e51c8e1cb6df43c410313fdbec`)
  - `test_sensibilidad.py` (SHA-256: `7d00f74ef99df3d2e9bbccbc0be009252c8c6bc1a1f0a2043e74ff5844810756`)
  - `REPORTE_SENSIBILIDAD_ARRASTRE.md` (SHA-256: `1e95ca732a322e70be3868da56641e7f5e8d6973ba408e2f89f2187f54924c52`)

---

## 2. Taxonomía de Datos: Medidos vs. Supuestos vs. Cálculos

| Categoría | Parámetro | Valor | Unidad | Fuente / Justificación |
|:---|:---|:---:|:---:|:---|
| **Datos Medidos** | **Ninguno** | — | — | *No existen mediciones físicas directas (pesajes en báscula calibrada ni ensayos en túnel de viento) para C02.* |
| **Supuestos (Vehículo)** | Masa total C02 ($m$) | $5,0$ | kg | Especificación de diseño de la candidata C02. |
| **Supuestos (CAD Ligero)** | Masa asignada parcial | $2,04584$ | kg | Hipótesis `ligera_1200` en modelo CAD parcial. |
| **Supuestos (CAD Ligero)** | Reserva provisional | $0,75$ | kg | Asignación estimada de reserva para elementos no modelados. |
| **Supuestos (CAD Ligero)** | Hardware adicional no id. | $0,0$ | kg | Caso de referencia optimista (sin recargo adicional). |
| **Supuestos (Batería)** | Densidad de energía pack ($e_{\text{pack}}$) | $150,0$ | Wh/kg | Supuesto de celda/pack instalado. |
| **Supuestos (Batería)** | Densidad de potencia pack ($p_{\text{pack}}$) | $5.000,0$ | W/kg | Supuesto de descarga específica admisible. |
| **Supuestos (Misión)** | Tiempo estacionario ($t_{\text{est}}$) | $30,0$ | s | Duración de la fase inicial vertical (incluye maniobra). |
| **Supuestos (Misión)** | Tiempo maniobra lateral ($t_{\text{man}}$) | $3,0$ | s | Tramo de mayor demanda dentro del estacionario. |
| **Supuestos (Misión)** | Potencia estacionario ($P_{\text{est}}$) | $2.968,81$ | W | Valor exploratorio heredado del modelo C01. |
| **Supuestos (Misión)** | Potencia maniobra ($P_{\text{man}}$) | $3.505,89$ | W | Valor exploratorio heredado del modelo C01. |
| **Supuestos (Misión)** | Tiempo crucero ($t_{\text{crucero}}$) | $30,0$ | s | Crucero horizontal a velocidad final $V$. |
| **Supuestos (Misión)** | Eficiencia axial propulsiva ($\eta$) | $0,70$ | — | Supuesto constante a lo largo de toda la aceleración y crucero. |
| **Supuestos (Misión)** | Tiempo aceleración nominal ($t$) | $60,0$ | s | Tiempo de aceleración rectilínea uniforme analizado. |
| **Supuestos (Escenarios)** | Velocidades objetivo ($V$) | $600,0\text{ y }1.000,0$ | km/h | $166,67\text{ m/s}$ y $277,78\text{ m/s}$. |
| **Supuestos (Escenarios)** | Arrastre a velocidad final ($D_{\text{fin}}$) | $50,0$ | N | Cota supuesta en punto final $v = V$. |
| **Supuestos (Escenarios)** | Potencia de apoyo simultáneo ($P_{\text{aux}}$) | $0\text{ y }1.000$ | W | Carga auxiliar para sustentación vertical o servicios. |
| **Supuestos (Modelo)** | Exponentes de ley de arrastre ($p$) | $1, 2, 4$ | — | Formulación paramétrica $D(v) = D_{\text{fin}}(v/V)^p$. |
| **Cálculos** | Aceleración media | $a = V / t$ | $\text{m/s}^2$ | Cinemática rectilínea con aceleración constante. |
| **Cálculos** | Distancia de aceleración | $x = \frac{1}{2} V t$ | m | Integral cinemática $\int_0^t v(\tau) d\tau$. |
| **Cálculos** | Trabajo de arrastre aceleración | $W_{\text{arrastre}} = \frac{D_{\text{fin}} V t}{p+2}$ | J | Integral analítica verificada en este informe. |
| **Cálculos** | Energía cinética | $E_{\text{cin}} = \frac{1}{2} m V^2$ | J | Energía mecánica inercial ganada. |
| **Cálculos** | Trabajo de arrastre crucero | $W_{\text{crucero}} = D_{\text{fin}} V t_{\text{crucero}}$ | J | Trabajo a velocidad y fuerza constantes. |
| **Cálculos** | Energía eléctrica axial | $E_{\text{axial}} = \frac{E_{\text{cin}} + W_{\text{arrastre}} + W_{\text{crucero}}}{3600 \cdot \eta}$ | Wh | Conversión mecánica a eléctrica considerando $\eta = 0,70$. |
| **Cálculos** | Energía eléctrica estacionario | $E_{\text{est}} = \frac{P_{\text{est}}(t_{\text{est}}-t_{\text{man}}) + P_{\text{man}} t_{\text{man}}}{3600}$ | Wh | $25,1876\text{ Wh}$ constantes en todos los casos. |
| **Cálculos** | Energía de apoyo simultáneo | $E_{\text{aux}} = \frac{P_{\text{aux}}(t + t_{\text{crucero}})}{3600}$ | Wh | $0\text{ Wh}$ ($0\text{ W}$) o $25,00\text{ Wh}$ ($1.000\text{ W}$ a $t=60\text{ s}$). |
| **Cálculos** | Potencia pico axial | $P_{\text{axial, pico}} = \frac{m V^2/t + D_{\text{fin}} V}{\eta}$ | W | Máximo de potencia mecánica en $v = V$ dividido por $\eta$. |
| **Cálculos** | Potencia pico de batería | $P_{\text{pack, pico}} = \max(P_{\text{man}}, P_{\text{axial, pico}} + P_{\text{aux}})$ | W | Demanda pico global del pack. |
| **Cálculos** | Masa requerida por energía | $m_{\text{bat, E}} = E_{\text{total}} / e_{\text{pack}}$ | kg | Requerimiento basado en capacidad de energía. |
| **Cálculos** | Masa requerida por potencia | $m_{\text{bat, P}} = P_{\text{pack, pico}} / p_{\text{pack}}$ | kg | Requerimiento basado en potencia específica pico. |
| **Cálculos** | Masa mínima de pack | $m_{\text{bat, min}} = \max(m_{\text{bat, E}}, m_{\text{bat, P}})$ | kg | Criterio de dimensionamiento bi-envolvente. |
| **Cálculos** | Presupuesto disponible de batería | $m_{\text{disp}} = 5,0 - 2,04584 - 0,75$ | kg | $2,20416\text{ kg}$ disponibles para pack en CAD ligero. |
| **Cálculos** | Saldo de batería | $\Delta m = m_{\text{disp}} - m_{\text{bat, min}}$ | kg | Margen de masa (negativo indica no cierre). |

---

## 3. Verificación Matemática Independiente

### 3.1. Deducción Rigurosa de la Integral de Trabajo Mecánico de Arrastre

Bajo aceleración rectilínea constante $a = \frac{V}{t}$ partiendo del reposo:
$$v(\tau) = a \cdot \tau = V \frac{\tau}{t}, \quad \tau \in [0, t]$$
El diferencial de posición es $dx = v(\tau) d\tau$. La fuerza de arrastre prescrita por la ley de potencias es:
$$D(v(\tau)) = D_{\text{fin}} \left( \frac{v(\tau)}{V} \right)^p = D_{\text{fin}} \left( \frac{\tau}{t} \right)^p$$
El trabajo infinitesimal realizado contra el arrastre es:
$$dW = D(v(\tau)) \cdot v(\tau) \, d\tau = D_{\text{fin}} \left( \frac{\tau}{t} \right)^p \cdot V \left( \frac{\tau}{t} \right) d\tau = D_{\text{fin}} V \left( \frac{\tau}{t} \right)^{p+1} d\tau$$
Integrando en el intervalo $[0, t]$ con el cambio de variable adimensional $u = \frac{\tau}{t}$ ($du = \frac{d\tau}{t}$, $d\tau = t \, du$):
$$W_{\text{arrastre, acel}} = D_{\text{fin}} V t \int_0^1 u^{p+1} du = D_{\text{fin}} V t \left[ \frac{u^{p+2}}{p + 2} \right]_0^1 = \frac{D_{\text{fin}} \cdot V \cdot t}{p + 2} \quad \blacksquare$$

Esta expresión es matemáticamente exacta para todo $p > -2$. En el dominio de velocidad ($v \, dv = a \, dx \implies dx = \frac{t}{V} v \, dv$), la integral conduce idénticamente al mismo resultado:
$$W_{\text{arrastre, acel}} = \int_0^V D_{\text{fin}} \left( \frac{v}{V} \right)^p \left( \frac{t}{V} v \right) dv = \frac{D_{\text{fin}} t}{V^{p+1}} \int_0^V v^{p+1} dv = \frac{D_{\text{fin}} \cdot V \cdot t}{p + 2} \quad \blacksquare$$

### 3.2. Evaluación para $p \in \{1, 2, 4\}$ y Comparación frente a $p = 2$

- **Caso lineal ($p = 1$):**
  $$W(p=1) = \frac{D_{\text{fin}} V t}{3}$$
- **Caso cuadrático clásico ($p = 2$, referencia base):**
  $$W(p=2) = \frac{D_{\text{fin}} V t}{4}$$
- **Caso cuártico ($p = 4$):**
  $$W(p=4) = \frac{D_{\text{fin}} V t}{6}$$

**Razones Teóricas Exactas:**
$$\frac{W(p=1)}{W(p=2)} = \frac{1/3}{1/4} = \frac{4}{3} = 1,\overline{33} \quad (+33,33\%)$$
$$\frac{W(p=4)}{W(p=2)} = \frac{1/6}{1/4} = \frac{4}{6} = \frac{2}{3} = 0,\overline{66} \quad (-33,33\%)$$

El trabajo de arrastre en aceleración es estrictamente decreciente con $p$. Para $p = 4$, el trabajo acumulado se reduce exactamente en un tercio respecto a la ley cuadrática, debido a que la fuerza se concentra en los últimos instantes antes de alcanzar $V$.

### 3.3. Verificación Numérica mediante Cuadratura Compuesta de Simpson
Se contrastó la solución cerrada contra la cuadratura compuesta de Simpson con $20.000$ intervalos:
- Para $600\text{ km/h}$, $D_{\text{fin}} = 50\text{ N}$, $t = 60\text{ s}$:
  - $p = 1$: $W_{\text{ana}} = 166.666,67\text{ J}$, error absoluto $= 5,82 \times 10^{-11}\text{ J}$ (relativo $3,49 \times 10^{-16}$).
  - $p = 2$: $W_{\text{ana}} = 125.000,00\text{ J}$, error absoluto $= 4,37 \times 10^{-11}\text{ J}$ (relativo $3,49 \times 10^{-16}$).
  - $p = 4$: $W_{\text{ana}} = 83.333,33\text{ J}$, error absoluto $= 1,16 \times 10^{-10}\text{ J}$ (relativo $1,40 \times 10^{-15}$).
- Para $1.000\text{ km/h}$, $D_{\text{fin}} = 50\text{ N}$, $t = 60\text{ s}$:
  - $p = 1$: $W_{\text{ana}} = 277.777,78\text{ J}$, error absoluto $= 5,82 \times 10^{-11}\text{ J}$ (relativo $2,10 \times 10^{-16}$).
  - $p = 2$: $W_{\text{ana}} = 208.333,33\text{ J}$, error absoluto $= 6,11 \times 10^{-10}\text{ J}$ (relativo $2,93 \times 10^{-15}$).
  - $p = 4$: $W_{\text{ana}} = 138.888,89\text{ J}$, error absoluto $= 2,33 \times 10^{-10}\text{ J}$ (relativo $1,68 \times 10^{-15}$).

Los errores residuales son de orden de máquina de 64 bits ($< 10^{-15}$), confirmando la exactitud de la fórmula.

### 3.4. Invariancia Analítica de la Potencia Pico
La fuerza propulsiva axial total es:
$$F_{\text{axial}}(\tau) = m \cdot a + D(v(\tau)) = m \frac{V}{t} + D_{\text{fin}} \left(\frac{\tau}{t}\right)^p$$
La potencia mecánica instantánea es:
$$P_{\text{mec}}(\tau) = F_{\text{axial}}(\tau) \cdot v(\tau) = m \frac{V^2}{t^2} \tau + D_{\text{fin}} V \left(\frac{\tau}{t}\right)^{p+1}$$
Su derivada respecto al tiempo es:
$$\frac{dP_{\text{mec}}}{d\tau} = m \frac{V^2}{t^2} + (p+1) \frac{D_{\text{fin}} V}{t} \left(\frac{\tau}{t}\right)^p > 0, \quad \forall \tau \in (0, t]$$
Dado que la función es estrictamente monótona creciente, el máximo se localiza sin ambigüedad en el punto terminal $\tau = t$ ($v = V$):
$$P_{\text{mec, pico}} = m \frac{V^2}{t} + D_{\text{fin}} V \left( \frac{V}{V} \right)^p = \frac{m V^2}{t} + D_{\text{fin}} V$$
Puesto que $(V/V)^p = 1^p = 1$ para cualquier $p > 0$, **la potencia mecánica axial pico es estrictamente invariante con $p$**. En consecuencia:
$$P_{\text{axial, pico}} = \frac{m V^2 / t + D_{\text{fin}} V}{\eta}$$
$$P_{\text{pack, pico}} = \max\left( P_{\text{man}}, P_{\text{axial, pico}} + P_{\text{aux}} \right)$$
Ambas cantidades resultan exactamente independientes del exponente $p$.

---

## 4. Matriz Comparativa: 12 Casos Centrales ($D_{\text{fin}} = 50\text{ N}, t = 60\text{ s}$)

| $V$ (km/h) | $P_{\text{aux}}$ (W) | $p$ | $W_{\text{arrastre}}$ (kJ) | Var. $W$ vs $p=2$ | $E_{\text{total}}$ (Wh) | Var. $E$ vs $p=2$ | $P_{\text{pack, pico}}$ (kW) | $m_{\text{bat, E}}$ (kg) | $m_{\text{bat, P}}$ (kg) | $m_{\text{bat, min}}$ (kg) | Restricción Activa | Saldo frente a $2,204\text{ kg}$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|---:|
| **600** | **0** | **1** | $166,67$ | $+33,33\text{ \%}$ | **218,09** | $+8,20\text{ \%}$ | **15,21** | $1,45$ | **3,04** | **3,04** | Potencia | $-0,84\text{ kg}$ |
| **600** | **0** | **2** | $125,00$ | *base* | **201,55** | *base* | **15,21** | $1,34$ | **3,04** | **3,04** | Potencia | $-0,84\text{ kg}$ |
| **600** | **0** | **4** | $83,33$ | $-33,33\text{ \%}$ | **185,02** | $-8,20\text{ \%}$ | **15,21** | $1,23$ | **3,04** | **3,04** | Potencia | $-0,84\text{ kg}$ |
| **600** | **1.000** | **1** | $166,67$ | $+33,33\text{ \%}$ | **243,09** | $+7,30\text{ \%}$ | **16,21** | $1,62$ | **3,24** | **3,24** | Potencia | $-1,04\text{ kg}$ |
| **600** | **1.000** | **2** | $125,00$ | *base* | **226,55** | *base* | **16,21** | $1,51$ | **3,24** | **3,24** | Potencia | $-1,04\text{ kg}$ |
| **600** | **1.000** | **4** | $83,33$ | $-33,33\text{ \%}$ | **210,02** | $-7,30\text{ \%}$ | **16,21** | $1,40$ | **3,24** | **3,24** | Potencia | $-1,04\text{ kg}$ |
| **1.000** | **0** | **1** | $277,78$ | $+33,33\text{ \%}$ | **377,31** | $+7,88\text{ \%}$ | **29,03** | $2,52$ | **5,81** | **5,81** | Potencia | $-3,60\text{ kg}$ |
| **1.000** | **0** | **2** | $208,33$ | *base* | **349,75** | *base* | **29,03** | $2,33$ | **5,81** | **5,81** | Potencia | $-3,60\text{ kg}$ |
| **1.000** | **0** | **4** | $138,89$ | $-33,33\text{ \%}$ | **322,19** | $-7,88\text{ \%}$ | **29,03** | $2,15$ | **5,81** | **5,81** | Potencia | $-3,60\text{ kg}$ |
| **1.000** | **1.000** | **1** | $277,78$ | $+33,33\text{ \%}$ | **402,31** | $+7,35\text{ \%}$ | **30,03** | $2,68$ | **6,01** | **6,01** | Potencia | $-3,80\text{ kg}$ |
| **1.000** | **1.000** | **2** | $208,33$ | *base* | **374,75** | *base* | **30,03** | $2,50$ | **6,01** | **6,01** | Potencia | $-3,80\text{ kg}$ |
| **1.000** | **1.000** | **4** | $138,89$ | $-33,33\text{ \%}$ | **347,19** | $-7,35\text{ \%}$ | **30,03** | $2,31$ | **6,01** | **6,01** | Potencia | $-3,80\text{ kg}$ |

### Conclusiones del Dimensionamiento:
1. **Desacoplamiento entre Energía y Masa:** Aunque variar $p$ altera la energía total consumida entre un $\pm 7,3\%$ y $\pm 8,2\%$, **no altera en absoluto la masa mínima de batería** ($m_{\text{bat, min}}$).
2. **Dominancia Absoluta de Potencia a 60 s:** En los 12 casos, $m_{\text{bat, P}} \gg m_{\text{bat, E}}$ (la masa requerida por potencia duplica a la de energía). Como la potencia pico es invariante con $p$, el dimensionamiento final del vehículo es insensible a la ley de arrastre en este punto de diseño.
3. **No Cierre Eléctrico:** Con $D_{\text{fin}} = 50\text{ N}$, ningún caso cumple el presupuesto disponible de $2,204\text{ kg}$ (déficit de $-0,84\text{ kg}$ a $-3,80\text{ kg}$).

---

## 5. Auditoría Crítica: Defectos y Supuestos No Físicos

### 5.1. Defectos de Código y Documentación Identificados y Corregidos en `salidas/`
1. **Ruta absoluta externa obsoleta en documentación:** En el informe de la sesión anterior (`entradas/.../salidas/REPORTE_SENSIBILIDAD_ARRASTRE.md`), la línea 257 referenciaba una ruta fija de una sesión ajena (`file:///private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/...`). Se corrigió en la copia local [`salidas/REPORTE_SENSIBILIDAD_ARRASTRE.md`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/salidas/REPORTE_SENSIBILIDAD_ARRASTRE.md#L257) para apuntar a la ruta canónica del entorno actual.
2. **Discrepancia nominal en métodos de prueba:** El reporte listaba `test_crossover_behavior`, mientras que en el código de prueba el método se llamaba `test_crossover_time_existence`. Se corrigió la discrepancia en el reporte.
3. **Casos de borde en pruebas automatizadas:**
   - No existía una prueba explícita que verificara el comportamiento de `find_crossover_time` cuando la potencia domina en todo el intervalo ($D=0, P_{\text{aux}}=0$), donde la función debe retornar `None`. Se añadió `test_crossover_none_when_power_dominates_always` a [`salidas/test_sensibilidad.py`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/salidas/test_sensibilidad.py#L227).
   - Se añadió prueba de integridad sobre el tamaño y columnas de la matriz extendida (`test_extended_cases_count_and_columns`, 90 filas).
   - Se añadió prueba de exportación CSV en carpeta temporal aislada (`test_write_csv_in_temp_dir`) usando `tempfile.TemporaryDirectory()`.

### 5.2. Supuestos No Físicos del Modelo
1. **No física del exponente $p = 1$ en régimen de alta velocidad:**
   - La ley $D \propto v$ modela flujo laminar viscoso tipo Stokes a números de Reynolds microscópicos ($Re \ll 1$).
   - A $600\text{ a }1.000\text{ km/h}$, el número de Reynolds del vehículo supera $Re \sim 10^5 - 10^6$, donde el régimen es inercial turbulento ($D \propto v^2$). Adoptar $p=1$ carece de fundamento físico aerodinámico para este vehículo.
2. **Incapacidad fundamental de $p = 4$ para representar el régimen transónico:**
   - La función $D(v) = D_{\text{fin}}(v/V)^4$ no modela ondas de choque, divergencia de Mach ($M_{dd}$), regla de áreas ni desprendimiento de capa límite inducido por choque.
   - Forzar el anclaje en $D(V) = D_{\text{fin}}$ hace que para cualquier velocidad intermedia $v < V$, el arrastre predicho por $p=4$ sea **drásticamente inferior** al arrastre cuadrático subsónico real (a $v/V = 0,5$, $(0,5)^4 = 0,0625$ frente a $(0,5)^2 = 0,25$, una subestimación del $75\%$). Por tanto, $p=4$ subestima el consumo de energía en la mayor parte de la aceleración.
   - A $1.000\text{ km/h}$ ($277,8\text{ m/s}$), el número de Mach oscila entre $M \approx 0,82$ (nivel del mar) y $M \approx 0,84$ (altitud de Bogotá, $2.550\text{ m}$). En este régimen, el coeficiente $C_D$ experimenta una divergencia no lineal multiplicándose por factores considerables. Fijar $D_{\text{fin}} = 50\text{ N}$ idéntico a $600\text{ km/h}$ y a $1.000\text{ km/h}$ es un supuesto no físico.
3. **Eficiencia axial plana $\eta = 0,70$ constante hasta $v = 0$:**
   - El modelo calcula la potencia eléctrica axial como $P_{\text{elec}} = (m a + D) v / \eta$.
   - En reposo ($v = 0$), esto arroja $P_{\text{elec}} = 0$, sugiriendo que producir una fuerza de aceleración estática $F = m a \approx 13,9 - 23,1\text{ N}$ no consume potencia.
   - Según la teoría del elemento de pala y de disco actuador de Rankine-Froude, cualquier propulsor real requiere una potencia inducida estática significativa: $P_{\text{ind, est}} = \sqrt{\frac{T^3}{2 \rho A}}$. Suponer $\eta$ constante hasta $v=0$ viola las leyes de cantidad de movimiento y subestima el consumo inicial.
4. **Potencia de apoyo $P_{\text{aux}}$ desacoplada y constante:**
   - Suponer $P_{\text{aux}}$ constante durante toda la aceleración y crucero ignora la sustentación aerodinámica alar ($L \propto v^2$). En un vehículo VTOL de transición, la potencia de los ventiladores de sustentación debe decrementarse a medida que las alas generan sustentación suficiente para sostener los $5,0\text{ kg}$. Asumir $P_{\text{aux}} = 0$ (sustentación mágica instantánea a $v=0$) o $P_{\text{aux}} = 2.968,81\text{ W}$ a $1.000\text{ km/h}$ son dos extremos artificiales.
5. **Comportamiento electroquímico desacoplado:**
   - Exigir $15-30\text{ kW}$ de potencia a un pack de $2-3\text{ kg}$ implica tasas de descarga extremas ($30\text{C} - 60\text{C}$). A estas tasas, la resistencia interna produce caídas severas de tensión, disipación Joule ($I^2 R$) que eleva la temperatura, y reducción de la capacidad efectiva disponible (efecto Peukert).

---

## 6. Pruebas Realizadas

Se ejecutó la suite de pruebas unitarias [`salidas/test_sensibilidad.py`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/salidas/test_sensibilidad.py) bajo Python 3.9 en el entorno aislado:

- **Total de pruebas:** 13 pruebas unitarias estándar.
- **Resultado:** 13 aprobadas (`13 OK`), 0 fallos, 0 errores.
- **Tiempo de ejecución:** $0,018\text{ s}$.

### Desglose de Pruebas:
1. `test_c02_constants_integrity`: Verifica integridad de masa ($5,0\text{ kg}$), potencias, tiempos y eficiencias de C02.
2. `test_analytical_integral_formula`: Verifica analíticamente la fórmula $D_{\text{fin}} V t / (p+2)$ para $p=1, 2, 4$ (divisores 3, 4, 6).
3. `test_numerical_vs_analytical_quadrature`: Valida la concordancia con la cuadratura de Simpson con error relativo $< 10^{-9}$ en 7 combinaciones de $V, D, t, p$.
4. `test_drag_work_theoretical_ratios`: Comprueba razones exactas $4/3$ y $2/3$ frente a $p=2$.
5. `test_reproduction_of_reference_cases_p2`: Reproduce exactamente los 6 casos de $50\text{ N}$ del informe de referencia original.
6. `test_peak_power_invariance_with_p`: Comprueba la invariancia estricta de las potencias axiales y de batería frente a variaciones de $p$.
7. `test_energy_sensitivity_across_p`: Comprueba la monotonía decreciente estricta de la energía con $p$.
8. `test_active_constraint_at_60s`: Valida que la potencia sea el limitante activo en los 12 casos y que la masa mínima sea idéntica.
9. `test_crossover_time_existence`: Valida la existencia y orden de los tiempos de cruce $t^*(p)$.
10. `test_input_validation`: Comprueba el rechazo de argumentos negativos o no admisibles.
11. `test_crossover_none_when_power_dominates_always`: Verifica que retorne `None` cuando no existe cruce finito.
12. `test_extended_cases_count_and_columns`: Comprueba estructura de la matriz extendida (90 casos).
13. `test_write_csv_in_temp_dir`: Comprueba la exportación en disco temporal sin efectos colaterales.

---

## 7. Archivos Generados en `salidas/`

Todos los entregables residen exclusivamente en `salidas/`:
1. [`salidas/sensibilidad_ley_arrastre.py`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/salidas/sensibilidad_ley_arrastre.py): Script de cálculo paramétrico, verificación de cuadratura y exportación.
2. [`salidas/test_sensibilidad.py`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/salidas/test_sensibilidad.py): Suite de 13 pruebas unitarias automatizadas.
3. [`salidas/tabla_comparacion_casos.csv`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/salidas/tabla_comparacion_casos.csv): Tabla CSV con los 12 casos centrales comparativos.
4. [`salidas/tabla_sensibilidad_completa.csv`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/salidas/tabla_sensibilidad_completa.csv): Matriz extendida con 90 escenarios paramétricos ($t \in [10, 180]\text{ s}$, apoyos $0, 1.000\text{ y }2.968,81\text{ W}$).
5. [`salidas/resultados_sensibilidad.json`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/salidas/resultados_sensibilidad.json): Resumen estructurado en JSON con huellas SHA-256 de fuentes, errores de cuadratura y tiempos de cruce.
6. [`salidas/REPORTE_SENSIBILIDAD_ARRASTRE.md`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/salidas/REPORTE_SENSIBILIDAD_ARRASTRE.md): Reporte técnico de sensibilidad con enlaces canónicos corregidos.
7. [`salidas/REVISION.md`](file:///private/tmp/aero_20261108T035257Z_b042f471_ottqcod9/reintento_revisar_energia/salidas/REVISION.md): Este documento de revisión independiente y auditoría técnica.

---

## 8. Limitaciones Explícitas

1. **Aproximación Cinemática 1D:** La ley de arrastre paramétrica no resuelve las ecuaciones diferenciales de Navier-Stokes ni campos de presión/velocidad tridimensionales.
2. **Desacoplamiento Aerodinámico:** No se resuelven ángulos de ataque, sustentación vertical inducida, polar de arrastre ni trimado longitudinal.
3. **Omisión de Compresibilidad Fiel:** El régimen transónico a $1.000\text{ km/h}$ requiere CFD compressible con modelos de turbulencia para capturar ondas de choque y divergencia de Mach real.
4. **Simplificación del Sistema Propulsivo:** Se asume $\eta = 0,70$ constante sin modelar mapas de compresores/ventiladores, estator ni efectos de flujo estático.
5. **Simplificación Electroquímica:** Las densidades de $150\text{ Wh/kg}$ y $5.000\text{ W/kg}$ no consideran temperatura, estado de carga (SoC), resistencia interna ni degradación de celdas bajo descargas superiores a 30C.
6. **No Extrapolación:** Las conclusiones aplican exclusivamente a la configuración conceptual C02 de 5,0 kg y no son extrapolables a variantes de distinta escala o arquitectura.
