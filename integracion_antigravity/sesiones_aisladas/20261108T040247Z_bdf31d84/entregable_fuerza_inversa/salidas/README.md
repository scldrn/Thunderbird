# Condición de Fuerza Descendente a Actitud Fija

Paquete técnico corto, reproducible, independiente y probado para el análisis de la fuerza propulsora descendente necesaria en una aeronave de 4 módulos propulsores bajo actitud fija, aceleración descendente neta $n \cdot g$, bajo gravedad constante y en ausencia de otras fuerzas externas.

---

## 1. Guía Rápida de Reproducción y Pruebas

Este paquete es autónomo y no requiere dependencias externas más allá de la biblioteca estándar de Python 3 (`python3`). Todas las rutas son relativas.

### Ejecución del cálculo y generación de datos
Desde la raíz del espacio de trabajo o desde la carpeta `salidas/`:
```bash
# Ejecutar desde la raíz del proyecto:
python3 salidas/fuerza_descendente.py

# O ejecutar dentro de la carpeta salidas/:
cd salidas && python3 fuerza_descendente.py
```
Esto genera y actualiza automáticamente los archivos `tabla_fuerza_descendente.csv` y `resultados_resumen.json`.

### Ejecución de la suite de pruebas unitarias
```bash
# Desde la raíz del proyecto:
python3 -m unittest salidas/test_fuerza_descendente.py

# O dentro de la carpeta salidas/:
cd salidas && python3 -m unittest test_fuerza_descendente.py
```
Todos los 10 tests unitarios deben reportar estado `OK`.

---

## 2. Clasificación Metodológica: Datos Medidos, Supuestos y Cálculos

Siguiendo las directrices de rigor y trazabilidad:

### 2.1 Datos Medidos y Cotas Geométricas de Referencia Previa
- **Disposición geométrica de módulos (Referencia C02 / Arquitectura A):**
  - Módulos en configuración rectangular simétrica: $x_i = \pm 0{,}160\text{ m}$, $y_i = \pm 0{,}076\text{ m}$ respecto al centroide geométrico (Fuente: `entradas/.../INFORME-VERTICAL.md`).
  - Número de actuadores propulsores: $N = 4$ ventiladores internos.
- **Aclaración sobre mediciones:**
  - No se dispone de mediciones experimentales en banco de ensayo de empuje en reversa para esta geometría instalada.
  - Las cotas previas de literatura interna (como $20{,}58\text{ N}$ en empuje ascendente para 5 kg) corresponden a supuestos de modelos ideales directos, no a mediciones de reversibilidad.
  - No se inventan marcas, mediciones ni autores.

### 2.2 Supuestos del Modelo Analítico
- **Actitud angular rigurosamente fija:**
  - Ángulos de inclinación del cuerpo constantes y nulos: cabeceo $\theta = 0$, alabeo $\phi = 0$, guiñada $\psi = 0$ ($\vec{\omega} = \vec{0}, \dot{\vec{\omega}} = \vec{0}$).
  - No se permite rotar el vehículo ni cabecear para reorientar empuje.
- **Aceleración gravitatoria uniforme:**
  - Valor canónico estándar: $g_0 = 9{,}80665\text{ m/s}^2$ (ISO 80000-3 / WGS-84).
  - Valor didáctico comparativo: $g = 9{,}81\text{ m/s}^2$.
- **Masas supuestas del estudio:**
  - Escalas prescritas: $m \in \{2{,}0\text{ kg}, 5{,}0\text{ kg}, 10{,}0\text{ kg}\}$.
  - *Nota metodológica:* No se infiere que reservas de peso sin masa asignada tengan masa real nula o no nula.
- **Aceleraciones descendentes netas prescritas:**
  - Factores de carga vertical: $n \in \{1{,}2, 2{,}0, 5{,}0\}$, donde la aceleración inercial vertical hacia abajo es $a_{\text{desc}} = n \cdot g$.
- **Ausencia de otras fuerzas externas:**
  - Sustentación aerodinámica nula ($L = 0$).
  - Resistencia aerodinámica exterior nula ($D = 0$).
  - Empuje axial nulo ($T_{\text{axial}} = 0$).
  - Momentos aerodinámicos nulos.
- **Simetría baricéntrica ideal base:**
  - Centro de gravedad (CG) perfectamente coincidente con el centroide geométrico de los 4 módulos ($x_{\text{CG}} = 0, y_{\text{CG}} = 0$).
- **Módulos propulsores ideales reversibles:**
  - Capacidad de ejercer fuerza descendente $F_{\text{rev}, i} \ge 0$.

### 2.3 Cálculos
- Formulación matemática basada en las leyes de Newton-Euler.
- Derivación algebraica de la cota inferior de fuerza descendente total y por módulo.
- Evaluaciones numéricas puntuales, análisis dimensional y balances de residuos estáticos.

---

## 3. Derivación Algebraica Formal

### 3.1 Sistema de Coordenadas y Balance de Fuerzas
Se adopta un marco de referencia inercial con el eje vertical $+Z$ orientado hacia el cenit (hacia arriba):
- Vector aceleración de la gravedad:
  $$\vec{g} = -g \, \hat{k} \quad (g > 0)$$
- Fuerza del peso gravitatorio:
  $$\vec{F}_{\text{grav}} = -m \, g \, \hat{k}$$
- Vector de aceleración neta descendente de magnitud $a_{\text{desc}} = n \cdot g$:
  $$\vec{a} = -a_{\text{desc}} \, \hat{k} = -n \, g \, \hat{k}$$
- Fuerza propulsora vertical generada por el sistema propulsor: $\vec{F}_{\text{prop}} = F_{\text{prop}, z} \, \hat{k}$.

Aplicando la 2ª ley de Newton ($\sum \vec{F} = m \vec{a}$):
$$\sum F_z = F_{\text{grav}, z} + F_{\text{prop}, z} = m \, a_z$$
$$-m \, g + F_{\text{prop}, z} = -m \, n \, g$$

Despejando la fuerza propulsora vertical:
$$F_{\text{prop}, z} = -m \, n \, g + m \, g = -m \, g \, (n - 1)$$

### 3.2 Condición de Fuerza Descendente Activa ($F_{\text{rev}}$)
Definimos $F_{\text{rev,total}}$ como la magnitud de la fuerza propulsora activa orientada hacia abajo (sentido $-Z$):
$$F_{\text{rev,total}} = -F_{\text{prop}, z} = m \, g \, (n - 1)$$

- **Para $n > 1$ (descenso hiper-gravitatorio):**
  La aceleración requerida supera la que aporta la gravedad por sí sola ($g$). La diferencia debe ser suministrada activamente por los propulsores empujando hacia abajo:
  $$F_{\text{rev,total}} = m \, g \, (n - 1) > 0$$

- **Para $n = 1$ (caída libre pura):**
  $n - 1 = 0 \implies F_{\text{rev,total}} = 0\text{ N}$. Los propulsores no aportan fuerza neta vertical.

- **Para $n < 1$ (descenso sub-gravitatorio o vuelo estacionario con $n = 0$):**
  $n - 1 < 0$. La gravedad por sí sola produce una aceleración superior a la deseada. Para mantener $a_{\text{desc}} = n \cdot g < g$, no se requiere fuerza descendente, sino **sustentación activa hacia arriba** ($F_{\text{sust}} = m \, g \, (1 - n) > 0$). Por lo tanto, la demanda de fuerza descendente activa es nula ($F_{\text{rev,total}} = 0$).

Unificando todos los regímenes físicos:
$$F_{\text{rev,total}} \ge \max\left(0,\, m \cdot g \cdot (n - 1)\right) \quad \blacksquare$$

### 3.3 Reparto Simétrico entre Cuatro Módulos
Para una aeronave con $N = 4$ módulos propulsores idénticos en estaciones $(\pm d_x, \pm d_y)$ y centro de gravedad simétrico ($x_{\text{CG}} = 0, y_{\text{CG}} = 0$):
- El momento de alabeo nulo exige:
  $$M_x = d_y \, (-F_1 + F_2 + F_3 - F_4) = 0$$
- El momento de cabeceo nulo exige:
  $$M_y = d_x \, (-F_1 - F_2 + F_3 + F_4) = 0$$
- Minimizando el esfuerzo máximo entre actuadores ($\min \max_i F_i$), la solución es estrictamente equitativa:
  $$F_1 = F_2 = F_3 = F_4 = F_{\text{rev,mod}}$$

Sustituyendo en la fuerza total:
$$\sum_{i=1}^{4} F_{\text{rev}, i} = 4 \, F_{\text{rev,mod}} = F_{\text{rev,total}}$$

Por módulo, la fuerza es exactamente **un cuarto del total**:
$$F_{\text{rev,mod}} = \frac{F_{\text{rev,total}}}{4} \ge \max\left(0,\, \frac{m \cdot g \cdot (n - 1)}{4}\right) \quad \blacksquare$$

---

## 4. Tabla Numérica de Resultados

Evaluación para $m \in \{2{,}0, 5{,}0, 10{,}0\}\text{ kg}$ y $n \in \{1{,}2, 2{,}0, 5{,}0\}$ con $g_0 = 9{,}80665\text{ m/s}^2$ (ISO 80000-3) y comparativa con $g = 9{,}81\text{ m/s}^2$:

| Masa $m$ [kg] | Factor $n$ | $(n - 1)$ | Acel. desc. $a_{\text{desc}}$ [m/s²] | Peso $W$ [N] | $F_{\text{rev,total}}$ [N] | $F_{\text{rev,total}}$ [kgf] | **$F_{\text{rev,mod}}$ ($g_0$) [N]** | **$F_{\text{rev,mod}}$ [kgf]** | $F_{\text{rev,mod}}$ ($g=9{,}81$) [N] | Ratio $F_{\text{mod}} / (W/4)$ |
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

### Verificación del Caso Testigo (5 kg, 2g)
- Masa $m = 5{,}0\text{ kg}$, Factor $n = 2{,}0$:
  $$F_{\text{rev,total}} = 5{,}0 \cdot 9{,}80665 \cdot (2{,}0 - 1{,}0) = 49{,}03325\text{ N}$$
  $$F_{\text{rev,mod}} = \frac{49{,}03325}{4} = 12{,}2583125\text{ N}$$
- **Redondeado a tres decimales:** **`12.258 N`**, satisfaciendo con absoluta exactitud el requerimiento técnico.

---

## 5. Análisis Crítico: Variación de Actitud y Fuerzas Externas

### 5.1 ¿Por qué la conclusión cambia con actitud variable?
La condición de requerir empuje inverso o fuerza descendente activa ($F_{\text{rev}} > 0$) es una consecuencia **directa y exclusiva de la restricción de actitud fija horizontal** ($\theta = 0, \phi = 0$).
- **Vuelo Invertido ($\phi = 180^\circ$ o $\theta = 180^\circ$):**
  Si se permite a la aeronave girar sobre su eje longitudinal o transversal e invertir su fuselaje, los módulos propulsores convencionales (que normalmente producen empuje hacia $+Z_{\text{cuerpo}}$) ahora apuntan directamente hacia el suelo ($-Z_{\text{inercial}}$).
  - En esta condición, la aceleración descendente neta es $a_{\text{desc}} = g + \frac{T_{\text{directo}}}{m}$.
  - Para alcanzar $n = 2{,}0$, basta con aplicar empuje normal hacia adelante/arriba de $1{,}0 \, g$ con el fuselaje invertido.
  - **Conclusión:** Con actitud variable, **no se requiere ninguna capacidad de reversibilidad mecánica ni aerodinámica**. La maniobra se ejecuta con propulsores estándar unidireccionales.
- **Actitud Inclinada ($\theta \ne 0, \phi \ne 0$):**
  El vector de empuje se descompone trigonométricamente ($T_z = T \cos\theta \cos\phi$). El control acopla aceleraciones horizontales y verticales.

### 5.2 ¿Por qué la conclusión cambia en presencia de otras fuerzas?
El modelo analítico asume un vacío ideal sin interacción aerodinámica externa:
- **Resistencia aerodinámica al descenso ($D_z$):**
  A medida que el vehículo adquiere velocidad vertical descendente $v_z$, aparece una fuerza de arrastre opuesta al movimiento ($+Z$), de magnitud $D_z = \frac{1}{2} \rho v_z^2 S C_{D,z}$.
  El balance real pasa a ser:
  $$-m \, g - F_{\text{rev}} + D_z = -m \, n \, g \implies F_{\text{rev}} = m \, g \, (n - 1) + D_z$$
  Por lo tanto, el arrastre aerodinámico **aumenta la fuerza descendente requerida**. Para velocidades de caída significativas, $D_z$ puede ser del mismo orden o mayor que el peso.
- **Sustentación aerodinámica ($L$):**
  Si existe flujo de aire relativo horizontal o ráfagas, las superficies del vehículo pueden inducir fuerzas sustentadoras verticales positivas o negativas, alterando drásticamente el balance.
- **Corrientes descendentes atmosféricas (*downbursts*):**
  Un flujo de aire descendente acelera el vehículo hacia abajo sin requerir empuje propulsor activo, disminuyendo la demanda de $F_{\text{rev}}$.

---

## 6. Distinción Fundamental: Fuerza Necesaria vs. Control Dinámico y Diseño Real

Disponer de la fuerza estática teórica $F_{\text{rev,mod}} = \frac{m g (n-1)}{4}$ es una **condición necesaria, pero de ningún modo suficiente**.

### 6.1 La fuerza necesaria NO garantiza control dinámico
1. **Pérdida de autoridad de control angular por saturación:**
   - La condición $F_{\text{rev,mod}} = 12{,}258\text{ N}$ calculada para $m=5\text{ kg}, n=2$ asume un reparto perfectamente simétrico.
   - Si los actuadores alcanzan su cota máxima $R$ para suministrar esta aceleración lineal, no queda margen de empuje diferencial ($\Delta F = R - F_{\text{rev,mod}} = 0$) para generar momentos de cabeceo ($M_y$) o alabeo ($M_x$).
   - Ante la más leve ráfaga, asimetría de masa o perturbación, el vehículo no podrá restaurar su actitud y entrará en divergencia angular incontrolada.
2. **Dinámica de actuadores, tiempos de respuesta y transitorios:**
   - Los modelos estáticos asumen cambio de empuje instantáneo ($t = 0$).
   - En la realidad física, invertir el sentido de empuje exige:
     - En hélices de paso variable: tiempo de desplazamiento mecánico del plato cíclico/servo ($d\beta/dt$).
     - En inversión de rotación del motor: frenado de la inercia del rotor ($J \dot{\Omega}$), cruce por cero RPM y aceleración en sentido contrario.
   - Durante ese transitorio (típicamente entre $100\text{ ms}$ y más de $500\text{ ms}$), la aeronave carece de empuje y de control de actitud.
3. **Efectos giroscópicos y de par reactivo:**
   - Variaciones asimétricas de RPM inducen pares reactivos de guiñada ($M_z$) y pares giroscópicos cruzados ($\vec{\tau} = \vec{\omega} \times \vec{H}$) que complican la estabilidad en lazo cerrado.

### 6.2 La fuerza necesaria NO garantiza un diseño físico real
1. **Aerodinámica interna asimétrica del ventilador entubado (EDF):**
   - Los conductos y álabes de la Arquitectura A están optimizados con perfiles alares asimétricos y difusores convergentes/divergentes para empuje positivo ($+Z$).
   - Al invertir el flujo (succión por la parte inferior y descarga por la superior), el borde de fuga actúa como borde de ataque, desprendiendo masivamente la capa límite y provocando bloqueo aerodinámico (*stall*).
   - En flujo inverso, la eficiencia decae drásticamente (a menudo más de un 50–70%), demandando potencias eléctricas desproporcionadas.
2. **Límites de los variadores electrónicos de velocidad (ESC) y motores:**
   - Invertir el giro a alta potencia exige ESCs de 4 cuadrantes con frenado regenerativo. La energía regenerada puede provocar picos de sobretensión en la batería o quemar los transistores MOSFET.
   - El estrés térmico en el bobinado del motor se multiplica severamente.
3. **Inversión de esfuerzos mecánicos y estructurales:**
   - Las bancadas de motor, fijaciones y conductos están dimensionadas para cargas de compresión/tracción ascendentes. La aplicación de empuje descendente invierte la dirección de las cargas estructurales sobre los tornillos de fijación y el chasis.
4. **Bucle de masa agregada:**
   - Instalar mecanismos de reversa (servos de paso variable o toberas con compuertas deflectoras) incrementa la masa total $m$ de la aeronave, lo que a su vez incrementa el peso $W$ y la fuerza descendente requerida, degradando la autonomía en vuelo de crucero.

---

## 7. Archivos del Paquete

- `fuerza_descendente.py`: Módulo principal de cálculo, exportación y análisis.
- `test_fuerza_descendente.py`: Suite de 10 pruebas unitarias reproducibles (`unittest`).
- `tabla_fuerza_descendente.csv`: Datos tabulados de los 9 escenarios evaluados.
- `resultados_resumen.json`: Estructura JSON completa con datos, metadatos y análisis de CG excéntrico.
- `INFORME_TECNICO.md`: Monografía técnica exhaustiva con derivaciones, matrices de balance y limitaciones.
- `README.md`: Este documento.
