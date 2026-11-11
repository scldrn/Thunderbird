# Informe Técnico: Verificación Analítica de Fuerza Descendente a Actitud Fija

**Fecha:** 8 de noviembre de 2026  
**Ubicación de entrega:** `salidas/INFORME_TECNICO.md`  
**Archivos asociados:** `salidas/README.md`, `salidas/fuerza_descendente.py`, `salidas/test_fuerza_descendente.py`, `salidas/tabla_fuerza_descendente.csv`, `salidas/resultados_resumen.json`  
**Configuración de referencia:** Aeronave con cuatro módulos propulsores integrados en cuerpo rígido.

---

## 1. Resumen Ejecutivo

El presente documento establece, deriva algebraicamente y verifica numéricamente la condición analítica de fuerza propulsora descendente necesaria para que una aeronave mantenga una **actitud angular rigurosamente fija** mientras experimenta una aceleración descendente neta prescrita $a_{\text{desc}} = n \cdot g$, bajo la acción exclusiva de un campo gravitatorio constante y en ausencia de otras fuerzas externas.

Se demuestra formalmente que la fuerza propulsora descendente total mínima requerida satisface:
$$F_{\text{rev,total}} \ge \max\left(0,\, m \cdot g \cdot (n - 1)\right)$$

En una disposición simétrica de cuatro módulos propulsores idénticos en estaciones rectangulares $(\pm d_x, \pm d_y)$ con centro de gravedad baricéntrico, la fuerza requerida por módulo es exactamente un cuarto de la total:
$$F_{\text{rev,mod}} = \frac{F_{\text{rev,total}}}{4} \ge \max\left(0,\, \frac{m \cdot g \cdot (n - 1)}{4}\right)$$

Para el caso testigo especificado ($m = 5{,}0\text{ kg}$, $n = 2{,}0$ y aceleración de gravedad estándar $g_0 = 9{,}80665\text{ m/s}^2$), la demanda teórica por módulo resulta:
$$F_{\text{rev,mod}} = \frac{5{,}0 \cdot 9{,}80665 \cdot (2{,}0 - 1{,}0)}{4} = 12{,}2583125\text{ N} \approx 12{,}258\text{ N}$$

Adicionalmente, se enfatizan dos conclusiones fundamentales de la mecánica de vuelo:
1. **Dependencia estricta de la actitud fija:** La necesidad de fuerza descendente activa ($F_{\text{rev}} > 0$) es un resultado condicionado exclusivamente a la restricción cinemática de actitud horizontal fija. Si se permite variar la actitud angular (por ejemplo, mediante una maniobra de medio alabeo o vuelo invertido a $180^\circ$), los propulsores directos convencionales orientan su vector hacia abajo, eliminando la necesidad de reversibilidad.
2. **La fuerza estática necesaria no garantiza controlabilidad dinámica ni viabilidad física:** Disponer de la cota de empuje $F_{\text{rev,mod}}$ no garantiza que la aeronave pueda estabilizarse dinámicamente ante perturbaciones (saturación de control de actitud con margen $\Delta F = 0$, retardos de inversión de actuadores) ni que sea físicamente construible sin sufrir penalizaciones severas por desprendimiento de flujo aerodinámico interno en el conducto, sobretensiones eléctricas por frenado regenerativo o inversión de esfuerzos mecánicos.

---

## 2. Clasificación Metodológica: Datos Medidos, Supuestos y Cálculos

Para garantizar máxima trazabilidad, se categorizan explícitamente los elementos del estudio:

### 2.1 Datos Medidos y Parámetros Geométricos Previos
- **Cotas geométricas de ubicación de actuadores:**
  - Estaciones longitudinales: $x_i = \pm 0{,}160\text{ m}$ (semidistancia $d_x = 0{,}160\text{ m}$).
  - Estaciones transversales: $y_i = \pm 0{,}076\text{ m}$ (semidistancia $d_y = 0{,}076\text{ m}$).
  - Número de módulos: $N = 4$.
  - Fuente: Geometría de referencia C02 / Arquitectura A (`entradas/.../INFORME-VERTICAL.md`).
- **Aclaración sobre ausencia de datos medidos de reversa:**
  - No existen mediciones experimentales en banco de pruebas de empuje en flujo inverso para esta configuración.
  - Las cotas de empuje mencionadas en estudios previos (ej. $20{,}58\text{ N}$ en empuje ascendente para 5 kg) constituyen supuestos ideales de modelado y no mediciones físicas de flujo inverso instalado.
  - No se inventan marcas, mediciones ni autores.

### 2.2 Supuestos del Modelo Analítico
- **Actitud angular rígidamente fija:**
  - Ángulos de cabeceo ($\theta$), alabeo ($\phi$) y guiñada ($\psi$) constantes e idénticamente nulos: $\theta = 0, \phi = 0, \psi = 0$.
  - Velocidad y aceleración angular nulas: $\vec{\omega} = \vec{0}$, $\dot{\vec{\omega}} = \vec{0}$.
- **Campo gravitatorio uniforme:**
  - Valor canónico principal: $g_0 = 9{,}80665\text{ m/s}^2$ (gravedad estándar según ISO 80000-3 / WGS-84).
  - Valor comparativo de referencia: $g = 9{,}81\text{ m/s}^2$.
- **Masas supuestas del estudio:**
  - Escalas objetivo: $m \in \{2{,}0\text{ kg}, 5{,}0\text{ kg}, 10{,}0\text{ kg}\}$.
  - *Principio de precaución:* No se asume que una reserva sin masa asignada posea masa real nula o no nula.
- **Aceleraciones descendentes prescritas:**
  - Factores de carga vertical: $n \in \{1{,}2, 2{,}0, 5{,}0\}$, correspondientes a una aceleración neta descendente $a_{\text{desc}} = n \cdot g$.
- **Ausencia de fuerzas externas no gravitatorias:**
  - Sustentación del cuerpo o alas nula ($L = 0$).
  - Resistencia aerodinámica exterior nula ($D = 0$).
  - Empuje axial nulo ($T_{\text{axial}} = 0$).
  - Momentos aerodinámicos externos nulos.
- **Simetría baricéntrica ideal:**
  - Centro de gravedad (CG) situado en el origen geométrico ($x_{\text{CG}} = 0, y_{\text{CG}} = 0$).
- **Módulos con capacidad de fuerza reversible ideal:**
  - Se asume que cada módulo puede suministrar una fuerza vertical descendente independiente $F_{\text{rev}, i} \ge 0$.

### 2.3 Cálculos
- Formulación de equilibrio dinámico mediante las leyes de Newton-Euler para traslación vertical y rotación plana.
- Derivación analítica de la desigualdad $F_{\text{rev,total}} \ge \max(0, m \cdot g \cdot (n - 1))$ y de la división por cuatro módulos.
- Formulación de la sensibilidad por excentricidad del centro de gravedad.
- Pruebas computacionales de homogeneidad dimensional y balances estáticos.

---

## 3. Derivación Analítica Rigurosa

### 3.1 Marco de Referencia Inercial y Convención de Signos
Se define un marco inercial dextrógiro centrado en la aeronave:
- Eje $+X$: Longitudinal horizontal.
- Eje $+Y$: Transversal horizontal.
- Eje $+Z$: Vertical ascendente (hacia el cenit).

En este sistema:
1. El vector de aceleración de la gravedad es:
   $$\vec{g} = -g \, \hat{k} \quad (g > 0)$$
2. La fuerza debida al peso es:
   $$\vec{F}_{\text{grav}} = m \vec{g} = -m \, g \, \hat{k}$$
3. La aceleración neta prescrita para la aeronave es puramente vertical y orientada hacia abajo, con magnitud $a_{\text{desc}} = n \cdot g$:
   $$\vec{a} = -n \, g \, \hat{k}$$
4. El sistema propulsor genera una fuerza vertical total:
   $$\vec{F}_{\text{prop}} = F_{\text{prop}, z} \, \hat{k}$$

### 3.2 Balance de Fuerzas por la Segunda Ley de Newton
Dado que la actitud está fija y no hay rotación, la ecuación de cantidad de movimiento es:
$$\sum \vec{F} = m \vec{a}$$

Proyectando sobre el eje vertical $+Z$:
$$\sum F_z = F_{\text{grav}, z} + F_{\text{prop}, z} = m \, a_z$$
$$-m \, g + F_{\text{prop}, z} = -m \, n \, g$$

Despejando la fuerza vertical requerida del sistema propulsor:
$$F_{\text{prop}, z} = -m \, n \, g + m \, g = -m \, g \, (n - 1)$$

### 3.3 Definición de la Fuerza Reversa / Descendente Activa
La fuerza $F_{\text{prop}, z}$ representa el vector propulsor sobre $+Z$. Cuando $n > 1$, $F_{\text{prop}, z}$ es estrictamente negativo, lo que significa que el sistema propulsor debe empujar activamente en sentido $-Z$ (hacia abajo).

Definiendo la magnitud de la fuerza descendente activa como $F_{\text{rev,total}} = -F_{\text{prop}, z}$:
$$F_{\text{rev,total}} = m \cdot g \cdot (n - 1)$$

Analicemos los tres dominios posibles del factor de carga $n$:
1. **Régimen Hiper-gravitatorio ($n > 1$):**
   La aceleración descendente deseada excede la aceleración provista por la gravedad pura ($g$). La gravedad sola es insuficiente para alcanzar $n \cdot g$, por lo que se requiere una fuerza propulsora hacia abajo estrictamente positiva:
   $$F_{\text{rev,total}} = m \cdot g \cdot (n - 1) > 0$$
2. **Régimen de Caída Libre Pura ($n = 1$):**
   La aceleración deseada es exactamente $1{,}0 \, g$. La gravedad proporciona íntegramente la aceleración requerida:
   $$F_{\text{rev,total}} = m \cdot g \cdot (1 - 1) = 0\text{ N}$$
   Los actuadores no deben empujar hacia abajo ni hacia arriba.
3. **Régimen Sub-gravitatorio ($0 \le n < 1$):**
   La gravedad por sí sola aceleraría el cuerpo a $1{,}0 \, g$, lo cual es mayor que el valor objetivo $n \cdot g$. Para descender a una tasa menor que la caída libre (o sostenerse en vuelo estacionario con $n = 0$), el vehículo requiere **fuerza propulsora positiva hacia arriba** ($+Z$), dada por $F_{\text{sust}} = m \cdot g \cdot (1 - n) > 0$. En este caso, la demanda de fuerza descendente es nula ($F_{\text{rev,total}} = 0$).

Agrupando todos los regímenes bajo una formulación físicamente consistente:
$$F_{\text{rev,total}} \ge \max\left(0,\, m \cdot g \cdot (n - 1)\right) \quad \blacksquare$$

### 3.4 Distribución de Empuje entre Cuatro Módulos Simétricos
Considérense cuatro módulos situados en el plano $XY$ respecto al centro de gravedad:
- Módulo 1: $(+d_x, +d_y)$
- Módulo 2: $(+d_x, -d_y)$
- Módulo 3: $(-d_x, -d_y)$
- Módulo 4: $(-d_x, +d_y)$

Cada módulo ejerce una fuerza descendente $F_i \ge 0$ orientada en $-Z$ (vector $-F_i \, \hat{k}$).

Las ecuaciones de momento respecto al CG son:
$$M_x = \sum_{i=1}^4 y_i (-F_i) = (-F_1 d_y) + (F_2 d_y) + (F_3 d_y) + (-F_4 d_y) = d_y (-F_1 + F_2 + F_3 - F_4)$$
$$M_y = \sum_{i=1}^4 -x_i (-F_i) = (F_1 d_x) + (F_2 d_x) + (-F_3 d_x) + (-F_4 d_x) = d_x (F_1 + F_2 - F_3 - F_4)$$

Para satisfacer la condición de actitud fija ($\sum M_x = 0, \sum M_y = 0$):
$$-F_1 + F_2 + F_3 - F_4 = 0$$
$$F_1 + F_2 - F_3 - F_4 = 0$$

Sumando y restando ambas ecuaciones, se deduce:
$$F_2 = F_4 \quad \text{y} \quad F_1 = F_3$$
Por simetría transversal y longitudinal completa, la solución que minimiza la disipación cuadrática de potencia ($\sum F_i^2$) y el esfuerzo máximo ($\min \max_i F_i$) impone igualdad entre los cuatro actuadores:
$$F_1 = F_2 = F_3 = F_4 = F_{\text{rev,mod}}$$

Sustituyendo en la ecuación de fuerza vertical total:
$$\sum_{i=1}^4 F_i = 4 \, F_{\text{rev,mod}} = F_{\text{rev,total}}$$

Por ende, la fuerza descendente requerida por módulo es exactamente un cuarto de la total:
$$F_{\text{rev,mod}} = \frac{F_{\text{rev,total}}}{4} \ge \max\left(0,\, \frac{m \cdot g \cdot (n - 1)}{4}\right) \quad \blacksquare$$

---

## 4. Generalización: Sensibilidad a la Excentricidad del Centro de Gravedad

Si el centro de gravedad real se desplaza del baricentro geométrico a una posición $(x_{\text{CG}}, y_{\text{CG}})$, los momentos sobre el nuevo CG son:
$$\sum M_x = -\sum_{i=1}^4 (y_i - y_{\text{CG}}) F_i = 0 \implies \sum_{i=1}^4 y_i F_i = y_{\text{CG}} F_{\text{rev,total}}$$
$$\sum M_y = \sum_{i=1}^4 (x_i - x_{\text{CG}}) F_i = 0 \implies \sum_{i=1}^4 x_i F_i = x_{\text{CG}} F_{\text{rev,total}}$$

En una formulación plana desacoplada (equivalente al ajuste por mínimos cuadrados ponderados), la fuerza demandada a cada módulo es:
$$F_i = \frac{F_{\text{rev,total}}}{4} \left( 1 + \frac{x_i \, x_{\text{CG}}}{d_x^2} + \frac{y_i \, y_{\text{CG}}}{d_y^2} \right)$$

Dado que $x_i = \pm d_x$ e $y_i = \pm d_y$:
$$F_i = \frac{F_{\text{rev,total}}}{4} \left( 1 \pm \frac{x_{\text{CG}}}{d_x} \pm \frac{y_{\text{CG}}}{d_y} \right)$$

El módulo más cargado (en el cuadrante hacia el cual se desplazó el CG) demanda la fuerza crítica:
$$F_{\text{crítico}} = \frac{m \cdot g \cdot (n - 1)}{4} \left( 1 + \frac{|x_{\text{CG}}|}{d_x} + \frac{|y_{\text{CG}}|}{d_y} \right)$$

### Ejemplo Numérico de Amplificación
Tomando $d_x = 0{,}160\text{ m}$, $d_y = 0{,}076\text{ m}$ y una excentricidad longitudinal típica de $x_{\text{CG}} = 0{,}040\text{ m}$ con $y_{\text{CG}} = 0$:
$$\text{Factor de amplificación} = 1 + \frac{0{,}040}{0{,}160} = 1{,}25 \quad (+25\%)$$
Para $m = 5\text{ kg}$ y $n = 2{,}0$:
- Módulos en simetría teórica: $12{,}258\text{ N}$ por módulo.
- Módulo crítico con CG excéntrico: $12{,}258 \times 1{,}25 = 15{,}323\text{ N}$.

Esto confirma que el reparto simétrico $1/4$ es una cota mínima teórica; cualquier imperfección en la posición del CG eleva la capacidad individual requerida en los actuadores críticos.

---

## 5. Homogeneidad Dimensional y Casos Límite

### 5.1 Verificación Dimensional en el SI
Sea la relación analítica por módulo:
$$F_{\text{rev,mod}} = \frac{m \cdot g \cdot (n - 1)}{4}$$

Ecuaciones dimensionales de las magnitudes intervinientes:
- Masa: $[m] = \text{M}^1 \text{L}^0 \text{T}^0$
- Aceleración gravitatoria: $[g] = \text{M}^0 \text{L}^1 \text{T}^{-2}$
- Factor de carga $n$: Relación de aceleraciones $n = a_{\text{desc}} / g$:
  $$[n] = \frac{\text{L}^1 \text{T}^{-2}}{\text{L}^1 \text{T}^{-2}} = \text{M}^0 \text{L}^0 \text{T}^0 \quad (\text{adimensional})$$
  Por ende, el factor $(n - 1)$ es puramente adimensional.
- Denominador $4$: Cantidad escalar de actuadores propulsores, adimensional ($[4] = 1$).

Combinando las dimensiones:
$$[F_{\text{rev,mod}}] = \frac{(\text{M}^1) \cdot (\text{L}^1 \text{T}^{-2}) \cdot (1)}{1} = \text{M}^1 \text{L}^1 \text{T}^{-2}$$

Dado que $1\text{ N} = 1\text{ kg}\cdot\text{m}\cdot\text{s}^{-2}$, la dimensión coincide exactamente con la dimensión física de fuerza en el SI.

### 5.2 Evaluación en Casos Límite
1. **$n = 1{,}0$ (Caída libre pura):**
   $F_{\text{rev,total}} = m \cdot g \cdot (0) = 0\text{ N}$. Consistente: no se requiere fuerza activa.
2. **$n = 0{,}0$ (Vuelo estacionario):**
   $\max(0, m \cdot g \cdot (-1)) = 0\text{ N}$ de fuerza descendente. La fuerza vertical total requerida es $F_{\text{prop}, z} = +m \cdot g$, es decir, empuje ascendente para equilibrar el peso.
3. **$g \to 0$ (Entorno espacial o microgravedad con aceleración lineal $a$ impuesta):**
   $F_{\text{rev,total}} = m \cdot a$, $F_{\text{rev,mod}} = m \cdot a / 4$. Recupera exactamente la 2ª ley de Newton en el vacío libre de gravedad.

---

## 6. Resultados Tabulados y Análisis Comparativo

Se evalúan sistemáticamente las combinaciones de masas $m \in \{2{,}0, 5{,}0, 10{,}0\}\text{ kg}$ y factores $n \in \{1{,}2, 2{,}0, 5{,}0\}$ bajo gravedad canónica $g_0 = 9{,}80665\text{ m/s}^2$ y comparativa $g = 9{,}81\text{ m/s}^2$:

| Masa $m$ [kg] | Factor $n$ | Exceso $(n - 1)$ | Acel. $a_{\text{desc}}$ [m/s²] | Peso $W$ [N] | $F_{\text{rev,tot}}$ [N] | $F_{\text{rev,tot}}$ [kgf] | **$F_{\text{rev,mod}}$ ($g_0$) [N]** | $F_{\text{rev,mod}}$ [kgf] | $F_{\text{rev,mod}}$ ($9{,}81$) [N] | Ratio $F_{\text{mod}} / (W/4)$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2,0** | 1,2 | 0,2 | 11,7680 | 19,6133 | 3,9227 | 0,40 | **0,9807** | 0,10 | 0,9810 | 0,20 |
| **2,0** | 2,0 | 1,0 | 19,6133 | 19,6133 | 19,6133 | 2,00 | **4,9033** | 0,50 | 4,9050 | 1,00 |
| **2,0** | 5,0 | 4,0 | 49,0333 | 19,6133 | 78,4532 | 8,00 | **19,6133** | 2,00 | 19,6200 | 4,00 |
| **5,0** | 1,2 | 0,2 | 11,7680 | 49,0333 | 9,8066 | 1,00 | **2,4517** | 0,25 | 2,4525 | 0,20 |
| **5,0** | **2,0** | **1,0** | **19,6133** | **49,0333** | **49,0333** | **5,00** | **12,2583** | **1,25** | **12,2625** | **1,00** |
| **5,0** | 5,0 | 4,0 | 49,0333 | 49,0333 | 196,1330 | 20,00 | **49,0333** | 5,00 | 49,0500 | 4,00 |
| **10,0** | 1,2 | 0,2 | 11,7680 | 98,0665 | 19,6133 | 2,00 | **4,9033** | 0,50 | 4,9050 | 0,20 |
| **10,0** | 2,0 | 1,0 | 19,6133 | 98,0665 | 98,0665 | 10,00 | **24,5166** | 2,50 | 24,5250 | 1,00 |
| **10,0** | 5,0 | 4,0 | 49,0333 | 98,0665 | 392,2660 | 40,00 | **98,0665** | 10,00 | 98,1000 | 4,00 |

### Verificación Numérica Mandataria: 5 kg y 2g
Para $m = 5{,}0\text{ kg}$ y $n = 2{,}0$:
$$F_{\text{rev,mod}} = \frac{5{,}0 \times 9{,}80665 \times (2{,}0 - 1{,}0)}{4} = \frac{49{,}03325}{4} = 12{,}2583125\text{ N}$$
Redondeado a tres cifras decimales: **`12.258 N`**.

### Propiedad Invariante de Escala
Nótese que la relación normalizada respecto al peso en estacionario por módulo ($W/4$):
$$\frac{F_{\text{rev,mod}}}{W / 4} = \frac{m \cdot g \cdot (n - 1) / 4}{m \cdot g / 4} = n - 1$$
El esfuerzo de reversa por módulo respecto a su capacidad de sustentación depende únicamente del exceso de factor de carga $(n - 1)$, siendo independiente de la masa del vehículo:
- Para $n = 1{,}2$: Requiere el $20\%$ de la sustentación estática en reversa.
- Para $n = 2{,}0$: Requiere el $100\%$ de la sustentación estática en reversa.
- Para $n = 5{,}0$: Requiere el $400\%$ de la sustentación estática en reversa.

---

## 7. Efecto de la Actitud Variable y Otras Fuerzas Externas

### 7.1 ¿Por qué la conclusión cambia radicalmente con actitud variable?
La necesidad estricta de contar con fuerza propulsora en reversa ($F_{\text{rev}} > 0$) es un resultado condicionado de manera indisoluble a la premisa de **actitud fija horizontal**:
1. **Inversión de actitud (vuelo invertido a $\phi = 180^\circ$ o $\theta = 180^\circ$):**
   Si la aeronave puede rotar sobre su eje de alabeo o cabeceo, los propulsores principales unidireccionales (que generan empuje directo en $+Z_{\text{cuerpo}}$) pasan a apuntar hacia abajo en el sistema inercial ($-Z_{\text{inercial}}$).
   - En esa actitud invertida, la aceleración vertical neta hacia abajo es:
     $$a_{\text{desc}} = g + \frac{T_{\text{directo}}}{m}$$
   - Para obtener $a_{\text{desc}} = 2{,}0 \, g$, basta con aplicar un empuje directo equivalente a $1{,}0 \, g$ ($49{,}03\text{ N}$ para $5\text{ kg}$) con los motores convencionales en sentido directo.
   - **Resultado:** No se requiere ningún mecanismo de reversibilidad, toberas bidireccionales ni hélices de paso variable.
2. **Maniobras con cabeceo o alabeo no nulo ($\theta \ne 0, \phi \ne 0$):**
   El empuje propulsor se descompone vectorialmente, introduciendo componentes horizontales acopladas que permiten aceleraciones combinadas.

### 7.2 ¿Por qué la conclusión cambia ante otras fuerzas externas?
En vuelo real dentro de la atmósfera terrestre, la aeronave está sometida a un campo de fuerzas hidrodinámicas:
1. **Resistencia aerodinámica al descenso ($D_z$):**
   Durante un descenso rápido a velocidad $v_z$, la interacción con el aire genera una fuerza de arrastre que se opone al movimiento, es decir, actúa hacia arriba ($+Z$):
   $$D_z = \frac{1}{2} \rho v_z^2 S C_{D,z}$$
   Incorporando $D_z$ en el balance de Newton:
   $$-m \, g - F_{\text{rev,total}} + D_z = -m \, n \, g \implies F_{\text{rev,total}} = m \, g \, (n - 1) + D_z$$
   El arrastre parásito **aumenta significativamente la fuerza descendente requerida**. Para velocidades de descenso elevadas, $D_z$ puede superar con creces el propio peso de la aeronave.
2. **Sustentación aerodinámica ($L$):**
   Si el vehículo posee velocidad de avance horizontal ($v_x > 0$), el fuselaje o las alas pueden generar sustentación positiva o negativa dependiendo del ángulo de ataque, alterando sustancialmente el balance vertical.
3. **Corrientes descendentes (*downbursts*):**
   Una corriente vertical descendente induce una aceleración convectiva que asiste la caída, reduciendo la fuerza propulsora necesaria.
4. **Empuje axial residual:**
   Si existen motores de propulsión horizontal o toberas con desalineación angular, cualquier proyección en el eje $Z$ afecta directamente la ecuación de equilibrio.

---

## 8. Análisis Crítico: Fuerza Necesaria vs. Control Dinámico y Factibilidad Física

La relación matemática $F_{\text{rev,mod}} = \frac{m g (n-1)}{4}$ es únicamente una **condición estática necesaria**, pero de ningún modo es suficiente para garantizar la viabilidad del vuelo o de la ingeniería de la aeronave.

### 8.1 La fuerza necesaria NO garantiza control dinámico
1. **Saturación de actuadores y pérdida de autoridad de momentos:**
   - Para controlar la actitud ($\theta = 0, \phi = 0$) en un entorno real con turbulencia o ráfagas, el sistema de control debe poder generar momentos diferenciales:
     $$M_x = d_y (-F_1 + F_2 + F_3 - F_4)$$
     $$M_y = d_x (F_1 + F_2 - F_3 - F_4)$$
   - Si los cuatro módulos se encuentran operando en su cota de empuje máxima disponible para satisfacer la aceleración lineal $n \cdot g$, los actuadores quedan completamente **saturados**.
   - Con margen diferencial nulo ($\Delta F = 0$), cualquier perturbación angular inducirá una divergencia incontrolable de cabeceo o alabeo, provocando la pérdida total de la actitud fija.
2. **Dinámica de actuadores y retardos en la inversión de flujo:**
   - La inversión del empuje no ocurre instantáneamente ($t_{\text{inv}} > 0$).
   - En sistemas BLDC con inversión electrónica de fase: se requiere decelerar la inercia rotacional del rotor ($J \dot{\Omega}$), cruzar por velocidad cero y acelerar en sentido opuesto. Este proceso introduce retardos de entre $150\text{ ms}$ y más de $600\text{ ms}$, durante los cuales el empuje es nulo o transitorio.
   - En sistemas de paso variable: el servomecanismo posee una velocidad angular finita ($d\beta/dt$), generando un transitorio no lineal y riesgo de desprendimiento dinámico de pala.
3. **Pares giroscópicos y de reacción:**
   - Durante las aceleraciones y deceleraciones rápidas del rotor para modular empuje inverso, la derivada del momento angular $\dot{\vec{H}} = J \dot{\vec{\Omega}}$ genera pares de guiñada y de acoplamiento giroscópico cruzado con las velocidades angulares residuales.

### 8.2 La fuerza necesaria NO garantiza un diseño real
1. **Aerodinámica interna en flujo reverso de conductos integrados:**
   - Los ventiladores entubados (EDF) de la Arquitectura A están diseñados con labios de entrada redondeados en el extradós superior y difusores en el intradós inferior.
   - En flujo inverso, el aire entra por el difusor (que ahora actúa como una tobera mal adaptada con bordes agudos), desprendiendo la capa límite e induciendo pérdidas de presión de remanso enormes.
   - Los álabes del rotor tienen curvatura y torsión diseñadas para flujo descendente. En sentido contrario, operan a ángulos de ataque desfavorables con borde de fuga actuando como borde de ataque, sufriendo colapso de sustentación (*stall*) y reduciendo la eficiencia aerodinámica en más de un 60%.
2. **Límites de los variadores electrónicos (ESC) y motores eléctricos:**
   - La inversión ultra-rápida a alta potencia exige ESCs regenerativos de 4 cuadrantes. La energía cinética rotacional del rotor devuelta al bus de continua genera picos de sobretensión que pueden destruir los condensadores y transistores MOSFET.
   - El sobrecalentamiento térmico del estator por sobrecorrientes transitorias reduce drásticamente la vida útil del motor.
3. **Inversión de cargas estructurales:**
   - Las bancadas de motor, fijaciones y carenados de conducto suelen diseñarse para soportar tracción ascendente (sostener el peso). La aplicación de empuje descendente invierte el sentido de las fuerzas cortantes y de tracción sobre los tornillos y uniones adhesivas del chasis.
4. **Espiral de masa agregada:**
   - La inclusión de mecanismos mecánicos reversibles (servos de paso variable o toberas con persianas deflectoras) añade peso muerto que incrementa la masa total $m$, elevando a su vez el peso $W = m \cdot g$ y retroalimentando la demanda de empuje en un bucle perjudicial para la autonomía en crucero.

---

## 9. Conclusiones y Resumen de Entregables

1. **Condición Matemática Demostrada:**
   $$F_{\text{rev,total}} \ge \max\left(0,\, m \cdot g \cdot (n - 1)\right)$$
   $$F_{\text{rev,mod}} \ge \max\left(0,\, \frac{m \cdot g \cdot (n - 1)}{4}\right)$$
2. **Exactitud Numérica:**
   Para $m = 5{,}0\text{ kg}$ y $n = 2{,}0$, la demanda teórica es estrictamente **`12.258 N`** por módulo ($12{,}2583125\text{ N}$ con $g_0 = 9{,}80665\text{ m/s}^2$).
3. **Condicionalidad Metodológica:**
   La reversibilidad activa es exclusivamente necesaria bajo la premisa cinemática de actitud horizontal fija. Con actitud variable, la maniobra se resuelve mediante vuelo invertido con propulsores estándar unidireccionales.
4. **Suite de Pruebas:**
   El paquete cuenta con una suite independiente de 10 pruebas unitarias reproducibles (`salidas/test_fuerza_descendente.py`) que validan álgebra, dimensionalidad, equilibrio de Newton-Euler, casos límite y consistencia numérica, sin emplear rutas temporales absolutas.
