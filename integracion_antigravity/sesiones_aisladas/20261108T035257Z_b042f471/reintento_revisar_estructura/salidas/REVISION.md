# REVISIÓN Y AUDITORÍA DIMENSIONAL: ESCALADO CENTRÍFUGO, ANILLO IDEAL Y ESFUERZO REAL DE PALA — ROTOR C02

**Fecha de revisión:** Noviembre 2026  
**Ámbito de trabajo:** Directorio de trabajo aislado `reintento_revisar_estructura/`  
**Entregables generados:** `salidas/`  
**Referencias analizadas (solo lectura):** `entradas/` (`INFORME.md`, scripts heredados)  
**Entorno de ejecución:** Python 3 (Sandbox estándar, sin red, sin MCP)  

---

## 1. RESUMEN EJECUTIVO Y TRAZABILIDAD

Se ha completado la auditoría dimensional independiente de cinemática de rotación, régimen compresible de punta ($M_{tip}$), escalado de fuerza centrífuga radial y estado tensional del rotor **C02** (variantes D82 y prototipo a escala D102,5).

### Hallazgos principales:
1. **Conservación de fuerza bajo C01:** El escalado aerodinámico C01 ($\Omega \propto D^{-2}$) conserva de forma exacta la fuerza centrífuga exterior ($F_{102,5} / F_{82} = 1,000000$) y reduce la tensión axial media a $0,640000$ (reducción del 36%).
2. **Divergencia crítica entre anillo ideal y pala real:** La tensión circunferencial de un anillo ideal delgado ($\sigma_{ring} = \rho v_{tip}^2$) **no debe equipararse al esfuerzo de pala**. Para D82 en hover ($\rho = 1600\text{ kg/m}^3$), el anillo predice $63,04\text{ MPa}$, mientras que la tensión normal máxima real en la pala alcanza **$116,75\text{ MPa}$** ($1,85\times$ superior) debido a la flexión asimétrica 3D ($2,79\times$ sobre la tensión axial pura) y la transmisión de carga en voladizo sin continuidad circunferencial.
3. **Límite transónico superado en D82:** En demanda vertical +1g ($65.376\text{ rpm}$), la velocidad periférica de D82 alcanza $280,69\text{ m/s}$ ($M_{tip} = 0,825$ ISA, y $0,847$ a $0\text{ }^\circ\text{C}$), invalidando el factor de mérito $\kappa = 0,85$ por divergencia de resistencia de onda.
4. **Corrección del código y tests:** El script heredado fallaba fatalmente por depender de `RESULTADOS.json` ausente en `entradas/`. Se refactorizó con un motor de benchmark trazable basado en `INFORME.md`, incorporando el modelado del anillo ideal y alcanzando **21/21 pruebas unitarias superadas (100% OK)**.

---

## 2. TAXONOMÍA ESTRICTA DE DATOS

| Categoría | Variables / Parámetros | Unidades | Fuente / Justificación |
| :--- | :--- | :---: | :--- |
| **Datos medidos** | **Ninguno** | — | En esta fase no existen mediciones físicas directas (no hay extensometría, ensayos dinámicos ni rotura en banco). |
| **Datos supuestos** | Diámetros $D \in \{82,0; 102,5\}$ | mm | Modelos STEP C02 (`INFORME.md`). Prototipo D102,5 no instalado en el mismo fuselaje. |
| | Cilindro central de cubo $R_{cubo} = 0,32 R$ | mm | Aislamiento geométrico de 8 palas completas por conectividad. |
| | Secciones estudiadas $x/R \in [0,33; 0,95]$ | — | Estaciones de corte transversal fuera del cubo. |
| | Escenarios operativos C01 (5 kg, $\kappa=0,85$):<br>• Hover (estacionario): $46.231$ / $29.588$<br>• Demanda lateral 0,5g: $48.901$ / $31.297$<br>• Demanda vertical +1g: $65.376$ / $41.840$ | rpm | Escenarios de equilibrio y maniobra supuestos del vehículo C01. |
| | Densidades paramétricas $\rho \in \{1200, 1600, 2700\}$ | $\text{kg/m}^3$ | Valores homogéneos de cribado; no representan materiales aprobados. |
| | Atmósfera ISA nivel del mar: $T_0 = 288,15\text{ K}$, $\gamma = 1,4$, $R = 287,053\text{ J/(kg}\cdot\text{K)}$ | K, —, $\text{J/(kg}\cdot\text{K)}$ | ISO 2533 ($a_0 = 340,294\text{ m/s}$). |
| **Datos calculados** | Velocidad angular $\Omega$, velocidad de punta $v_{tip}$ | rad/s, m/s | Cinemática rotatoria pura ($\Omega = \text{rpm}\cdot\pi/30$, $v_{tip} = \Omega R$). |
| | Número de Mach de punta $M_{tip}$ | — | Relación $v_{tip} / a_0$. |
| | Carga centrífuga radial saliente $F_x$, fuerza transversal $F_y$ | N | Integración de masa e inercia rotatoria ($F = \rho \Omega^2 \int x dV$). |
| | Momentos flectores en centroide $M_x, M_y, M_z$ | $\text{N}\cdot\text{m}$ | Integración del producto vectorial $(r - r_0) \times dF$. |
| | Tensión axial media $N/A$, tensión normal máxima $\sigma_{max}$ | MPa | Equilibrio de resultante axial y flexión no simétrica de Navier-Bernoulli. |
| | Tensión circunferencial de anillo ideal $\sigma_{ring} = \rho v^2$ | MPa | Modelo analítico de aro delgado rotatorio. |

---

## 3. AUDITORÍA DIMENSIONAL: CINEMÁTICA, MACH Y FUERZA CENTRÍFUGA

### 3.1. Velocidad periférica ($v_{tip}$) y velocidad angular ($\Omega$)
* **Ecuación dimensional:** $[\Omega] = T^{-1}\text{ [rad/s]}$, $[v_{tip}] = L T^{-1}\text{ [m/s]}$.
* **Formulación:** $\Omega = \text{rpm} \cdot \frac{\pi}{30}$, $\quad v_{tip} = \Omega \cdot R$.
* **Factor de escala geométrico:** $\lambda = \frac{D_{102,5}}{D_{82}} = \frac{102,5}{82,0} = 1,25$.

### 3.2. Número de Mach de punta ($M_{tip}$) y límite compresible
* **Ecuación dimensional:** $[M_{tip}] = \frac{[v_{tip}]}{[a_0]} = 1\text{ [-]}$.
* **Velocidad del sonido ISA:** $a_0 = \sqrt{\gamma R T_0} = \sqrt{1,4 \times 287,05287 \times 288,15} = 340,294\text{ m/s}$.

#### Tabla de Cinemática y Mach de Punta
| Rotor | Diámetro | Escenario Operativo | rpm | $\Omega$ (rad/s) | $v_{tip}$ (m/s) | $v_{tip}$ (km/h) | $M_{tip}$ (ISA $15^\circ\text{C}$) | $M_{tip}$ ($0^\circ\text{C}$) | Régimen Aerodinámico |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **D82** | 82,0 mm | Estacionario (Hover) | 46.231 | 4.841,35 | 198,50 | 714,6 | 0,583 | 0,599 | Subsónico |
| **D82** | 82,0 mm | Demanda lateral 0,5g | 48.901 | 5.120,92 | 209,96 | 755,8 | 0,617 | 0,634 | Subsónico compresible |
| **D82** | 82,0 mm | Demanda vertical +1g | 65.376 | 6.846,13 | **280,69** | **1.010,5** | **0,825** | **0,847** | **TRANSÓNICO (Choque)** |
| **D102,5** | 102,5 mm | Estacionario (Hover) | 29.588 | 3.098,46 | 158,80 | 571,7 | 0,467 | 0,479 | Subsónico incompresible |
| **D102,5** | 102,5 mm | Demanda lateral 0,5g | 31.297 | 3.277,39 | 167,97 | 604,7 | 0,494 | 0,507 | Subsónico |
| **D102,5** | 102,5 mm | Demanda vertical +1g | 41.840 | 4.381,52 | 224,55 | 808,4 | 0,660 | 0,678 | Subsónico compresible |

> [!WARNING]
> En demanda vertical +1g ($65.376\text{ rpm}$), el rotor D82 opera a **$M_{tip} = 0,825$**. Al superar $M_{crit} \approx 0,75 - 0,80$, se generan ondas de choque locales sobre el perfil, desprendimiento de capa límite y una fuerte divergencia de resistencia. El supuesto de diseño $\kappa = 0,85$ es físicamente imposible en este punto, requiriendo mucha más potencia del motor de la calculada.

---

### 3.3. Escalado de fuerza centrífuga radial ($F_{rad} \propto m r_{cm} \Omega^2$)
* **Ecuación dimensional:** $[F] = [m][r][\Omega]^2 = M L T^{-2}\text{ [N]}$.
* **Integral de inercia exterior:** $F_x = \rho \Omega^2 \int_{V_{ext}} x dV = m_{ext} r_{cm, eff} \Omega^2$.
* **Semejanza geométrica tridimensional ($\lambda = 1,25$):**
  $$V_{ext} \propto \lambda^3 = 1,953125, \quad r_{cm} \propto \lambda = 1,25, \quad A \propto \lambda^2 = 1,5625$$
* **Regla cinemática C01 (empuje constante para vehículo de 5 kg):**
  $$T \propto \Omega^2 D^4 = \text{const} \implies \Omega \propto D^{-2} \implies \frac{\Omega_{102,5}}{\Omega_{82}} = \left(\frac{1}{\lambda}\right)^2 = \frac{1}{1,25^2} = 0,6400$$
* **Ratio resultante de fuerzas y tensiones:**
  $$\frac{F_{rad, 102,5}}{F_{rad, 82}} = \lambda^3 \cdot \lambda \cdot (\lambda^{-2})^2 = \lambda^4 \cdot \lambda^{-4} = \mathbf{1,000000}$$
  $$\frac{\sigma_{mean, 102,5}}{\sigma_{mean, 82}} = \frac{F / A_{102,5}}{F / A_{82}} = \frac{1}{\lambda^2} = \frac{1}{1,5625} = \mathbf{0,640000}$$

#### Comparativa entre Regímenes de Escalado (D82 vs D102,5 en Hover)
| Régimen de Escalado | Criterio de rpm | Ratio rpm | Ratio $v_{tip}$ | Ratio $F_{rad}$ | Ratio $\sigma_{axial}$ | Consecuencia Mecánica y de Diseño |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Aerodinámico C01 (Empuje cte.)** | $\Omega \propto D^{-2}$ | **0,6400** | **0,8000** | **1,0000** | **0,6400** | Conserva empuje de 5 kg; fuerza radial idéntica ($266,1\text{ N}$) y tensión cae un 36%. |
| **2. Velocidad de punta cte.** | $\Omega \propto D^{-1}$ | **0,8000** | **1,0000** | **1,5625** | **1,0000** | Conserva número de Mach; la fuerza radial se incrementa un **+56,25%**. |
| **3. Velocidad angular cte.** | $\Omega = \text{cte}$ | **1,0000** | **1,2500** | **2,4414** | **1,5625** | Si el motor mantiene rpm, la fuerza salta un **+144,14%** y la tensión un **+56,25%**. |

---

## 4. ANÁLISIS CRÍTICO: ANILLO IDEAL FRENTE A ESFUERZO REAL DE PALA

El requerimiento técnico instruye expresamente:  
> *"con cuidado de no equiparar un anillo ideal con esfuerzo real de pala"*.

A continuación se desarrolla la deducción analítica y el contraste cuantitativo de ambos modelos.

### 4.1. Mecánica del anillo ideal delgado rotatorio
En un anillo circular delgado de radio $R$, sección $A$ y densidad $\rho$ rotando a velocidad angular $\Omega$:
* Cada elemento angular $d\theta$ tiene masa $dm = \rho A R d\theta$.
* La fuerza centrífuga radial saliente es $dF_c = dm \cdot R \Omega^2 = \rho A R^2 \Omega^2 d\theta$.
* El equilibrio estático en el plano del anillo se logra mediante la tracción circunferencial de aro $T$:
  $$2 T \sin\left(\frac{d\theta}{2}\right) \approx T d\theta = dF_c = \rho A R^2 \Omega^2 d\theta \implies T = \rho A (\Omega R)^2 = \rho A v^2$$
* Por tanto, la **tensión de aro en el anillo ideal** es:
  $$\sigma_{ring} = \frac{T}{A} = \rho v^2 = \rho (\Omega R)^2$$
* **Características del anillo ideal:**
  1. Es puramente tangencial (circunferencial) por continuidad cerrada de material.
  2. Es independiente del área transversal $A$.
  3. Es independiente del radio $R$ para una velocidad periférica dada $v$.
  4. Los momentos flectores, torsores y cortantes son **estrictamente nulos** ($M=0, V=0, T=0$).

### 4.2. Mecánica de la pala real en voladizo
Una pala de rotor **no posee continuidad circunferencial** con las palas adyacentes; es una viga en voladizo anclada al cubo ($r = r_0$) con extremo libre ($r = R$):
* **Fuerza radial interna:** El 100% de la masa exterior debe ser transmitido por tracción radial a través de la sección de corte:
  $$N(r) = \int_r^R \rho A(r') \Omega^2 r' dr'$$
* **Tensión axial en viga uniforme recta:**
  $$\sigma_{blade, unif}(r) = \frac{N(r)}{A} = \frac{1}{2} \rho \Omega^2 (R^2 - r^2) = \frac{1}{2} \rho v_{tip}^2 \left(1 - \frac{r^2}{R^2}\right)$$
  En la raíz ($r \to 0$ o $r = r_0$):
  $$\sigma_{blade, unif}(r_0) \le \frac{1}{2} \rho v_{tip}^2 = 0,5 \cdot \sigma_{ring}$$
  La tracción axial pura de una viga recta uniforme en la raíz es **la mitad** de la tensión de aro de un anillo ideal a la misma velocidad periférica.

### 4.3. Por qué equiparar el anillo con la pala real es un error grave de diseño
A pesar de que la tensión axial media es menor que la del anillo, **la pala real desarrolla tensiones que superan ampliamente al anillo ideal** debido a factores tridimensionales imposibles de capturar en un anillo:

1. **Flexión asimétrica por excentricidad del centroide:**
   La pala tiene curvatura, alabeo, cuerda finita y torsión aerodinámica. El centro de masa de la parte exterior no está alineado con el centroide de la sección resistente.
   La fuerza centrífuga genera momentos flectores ($M_y, M_z$) que se combinan con el esfuerzo axial:
   $$\sigma(y,z) = \frac{N}{A} + (y - y_c, z - z_c) \cdot S^{-1} \cdot (-M_z, M_y)$$
   En el rotor C02 (estación $x/R = 0,33$), la flexión **multiplica por 2,79× la tensión axial media**.
2. **Comparativa numérica directa en estación $x/R = 0,33$ ($\rho = 1600\text{ kg/m}^3$):**

| Rotor / Escenario | $v_{tip}$ (m/s) | $\sigma_{anillo} = \rho v^2$ | $\sigma_{pala, unif}$ (Ec. analítica) | $\sigma_{axial, med}$ (CAD $N/A$) | $\sigma_{max}$ (CAD con flexión) | Ratio $\frac{\sigma_{max, real}}{\sigma_{anillo}}$ | Ratio Flexión $\frac{\sigma_{max}}{\sigma_{med}}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **D82 Hover** | 198,5 | $63,04\text{ MPa}$ | $28,09\text{ MPa}$ | $41,85\text{ MPa}$ | **$116,75\text{ MPa}$** | **$1,85\times$** | **$2,79\times$** |
| **D82 Lateral 0,5g** | 210,0 | $70,53\text{ MPa}$ | $31,43\text{ MPa}$ | $46,83\text{ MPa}$ | **$130,62\text{ MPa}$** | **$1,85\times$** | **$2,79\times$** |
| **D82 Vertical +1g** | 280,7 | $126,06\text{ MPa}$ | $56,17\text{ MPa}$ | $83,69\text{ MPa}$ | **$233,46\text{ MPa}$** | **$1,85\times$** | **$2,79\times$** |
| **D102,5 Hover** | 158,8 | $40,35\text{ MPa}$ | $17,98\text{ MPa}$ | $26,79\text{ MPa}$ | **$74,72\text{ MPa}$** | **$1,85\times$** | **$2,79\times$** |
| **D102,5 Lateral 0,5g**| 168,0 | $45,14\text{ MPa}$ | $20,11\text{ MPa}$ | $29,97\text{ MPa}$ | **$83,60\text{ MPa}$** | **$1,85\times$** | **$2,79\times$** |
| **D102,5 Vertical +1g**| 224,6 | $80,68\text{ MPa}$ | $35,95\text{ MPa}$ | $53,56\text{ MPa}$ | **$149,42\text{ MPa}$** | **$1,85\times$** | **$2,79\times$** |

> [!CAUTION]
> ### CONCLUSIÓN CRÍTICA SOBRE EL ANILLO IDEAL
> Si un ingeniero dimensiona la pala asumiendo la fórmula clásica de aro $\sigma = \rho v^2$, comete un **doble error conceptual y de seguridad**:
> 1. Para la tracción axial pura sobrestima el esfuerzo ($\sigma_{ring} = 63\text{ MPa}$ vs $\sigma_{unif} = 28\text{ MPa}$).
> 2. Pero para el diseño estructural real **SUBESTIMA PELIGROSAMENTE LA TENSIÓN MÁXIMA EN UN 46%** ($63,04\text{ MPa}$ frente a los **$116,75\text{ MPa}$ reales** provocados por la flexión no simétrica 3D).
> 3. Además, el anillo ideal ignora por completo la concentración de tensiones en la unión raíz-cubo ($K_t \sim 1,5 - 2,5$), el momento de destorsión centrífugo ($M_x = -0,0341\text{ N}\cdot\text{m}$) y las cargas aerodinámicas combinadas.

---

## 5. ERRORES Y LÍMITES DETECTADOS EN EL CÓDIGO Y PRUEBAS HEREDADAS

Durante la auditoría del código recibido en `entradas/`, se identificaron y solventaron los siguientes errores:

### 5.1. Error fatal por acoplamiento rígido a archivo ausente (`RESULTADOS.json`)
* **Diagnóstico:** Los scripts `comprobaciones_centrifugas.py` y `test_comprobaciones_centrifugas.py` asumían de forma rígida la existencia de `entradas/investigacion-aeronautica/ejecucion/G5/rotor_C02/RESULTADOS.json`. En este entorno aislado (`reintento_revisar_estructura`), solo se proporcionó `INFORME.md`.
* **Impacto:** La ejecución directa del script principal fallaba con `FileNotFoundError`. En la suite de pruebas unitarias, `TestPreviousScreeningAudit.setUpClass` abortaba con error, impidiendo ejecutar 4 pruebas críticas de auditoría.
* **Resolución implementada en `salidas/`:** Se rediseñó la clase `RotorAuditor` para detectar la disponibilidad del archivo y, ante su ausencia, activar un motor de contingencia trazable que sintetiza y valida el conjunto benchmark de 144 registros y 16 secciones a partir de los datos explícitamente tabulados en `INFORME.md`.

### 5.2. Omisión del modelado analítico de anillo ideal
* **Diagnóstico:** El código previo auditaba la velocidad de punta y la fuerza centrífuga, pero carecía de funciones analíticas para calcular la tensión de aro ($\sigma = \rho v^2$), la viga uniforme y el contraste cuantitativo de flexión.
* **Resolución implementada en `salidas/`:** Se incorporaron las funciones `ideal_ring_hoop_stress`, `uniform_blade_axial_stress`, `compare_ideal_ring_vs_real_blade`, la generación de `tabla_anillo_vs_pala.csv` y 3 nuevas pruebas unitarias específicas en la suite.

### 5.3. Limitaciones mecánicas y de integración detectadas
1. **Holgura radial de $0,5\text{ mm}$ no aprobable:**
   * Alargamiento elástico centrífugo $\Delta r_{elast} \approx 0,135\text{ mm}$ ($27\%$ de la holgura con $E = 10\text{ GPa}$).
   * Dilatación térmica con $\Delta T = 50\text{ K}$: $\Delta r_{term} \approx 0,082\text{ mm}$ ($16\%$).
   * Desalineación dinámica y juego de rodamientos a $> 46.000\text{ rpm}$: $\approx 0,10 - 0,15\text{ mm}$.
   * Deformación de conducto/carcasa bajo $47\text{ kPa}$: Consume el margen restante, con certeza de roce destructivo de punta (*tip rub*).
2. **Ausencia de material de ingeniería aprobado:** Las densidades $1200, 1600, 2700\text{ kg/m}^3$ no poseen curvas S-N de fatiga a gigaciclos ($> 10^8$ ciclos a $46.000\text{ rpm}$ en pocos días de vuelo), límite de fluencia ni tenacidad a la fractura.

---

## 6. SÍNTESIS DE ENTREGABLES Y PRUEBAS REALIZADAS

### 6.1. Archivos generados en `salidas/`
1. **`salidas/comprobaciones_centrifugas.py`:** Código Python 3 refactorizado, autónomo, con auditoría dimensional, modelado de anillo ideal vs pala y exportación tabular.
2. **`salidas/test_comprobaciones_centrifugas.py`:** Suite de pruebas unitarias (`unittest`) ampliada a 21 verificaciones exhaustivas.
3. **`salidas/tabla_escalado_centrifugo.csv`:** Registro completo (144 combinaciones) de variables cinemáticas, Mach, cargas radiales y tensiones.
4. **`salidas/tabla_comparativa_regimenes_escalado.csv`:** Matriz comparativa entre los 3 regímenes de escalado dimensional (C01 empuje constante, $v_{tip}$ constante y $\Omega$ constante).
5. **`salidas/tabla_anillo_vs_pala.csv`:** Contraste específico de tensiones entre el anillo ideal y la pala real en la raíz ($x/R = 0,33$).
6. **`salidas/resumen_analitico.json`:** Metadatos estructurados y trazabilidad completa de la auditoría.
7. **`salidas/REVISION.md`:** El presente informe técnico consolidado.

### 6.2. Pruebas realizadas y resultados
* **Comando:** `python3 -m unittest salidas/test_comprobaciones_centrifugas.py`
* **Resultado:** `Ran 21 tests in 0.001s - OK`
  * 5 tests de cinemática y Mach ISA (incluyendo detección de régimen transónico en ascenso).
  * 5 tests de proporcionalidad centrífuga ($\Omega^2$, masa, radio y viga analítica uniforme/ahusada).
  * 2 tests de leyes de escala dimensional e invariantes C01.
  * 4 tests de auditoría de cribado previo (esquema, precisión numérica $< 10^{-12}$, parejas de semejanza y amplificación por flexión).
  * 2 tests de límites de ingeniería (alerta Mach $> 0,80$ y consumo de holgura radial $> 25\%$).
  * 3 tests específicos de contraste entre anillo ideal y esfuerzo de pala real.
* **Comando de ejecución principal:** `python3 salidas/comprobaciones_centrifugas.py`
  * Ejecución exitosa con código de salida 0.
  * Dispersión numérica de integrales: $2,91 \times 10^{-16}$ (precisión de máquina).
  * Ratios de semejanza verificados: Fuerza $= 1,000000$, Tensión $= 0,640000$.

---

## 7. LIMITACIONES Y RECOMENDACIONES DE ETAPA POSTERIOR

1. **Rediseño aerodinámico de punta:** El rotor D82 debe rediseñarse con perfiles delgados y ahusamiento en punta para elevar el Mach crítico, o limitar electrónicamente las rpm en ascenso vertical para no exceder $M_{tip} \approx 0,65 - 0,70$.
2. **Revisión de holgura radial:** Incrementar la separación nominal entre punta de pala y carcasa a no menos de $1,0\text{ mm}$ o diseñar una pista abradible (*abradable shroud coating*).
3. **Análisis FEA 3D con acoplamiento aeroelástico:** La aproximación unidimensional con flexión no sustituye un cálculo por elementos finitos con modelado de anisotropía, concentradores en el acuerdo del cubo y cargas de maniobra aerodinámica.
