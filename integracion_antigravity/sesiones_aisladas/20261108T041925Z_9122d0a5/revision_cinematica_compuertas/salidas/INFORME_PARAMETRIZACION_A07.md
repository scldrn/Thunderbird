# INFORME TÉCNICO: REVISIÓN Y CORRECCIÓN CINEMÁTICA 2-DOF (TRAYECTORIA A07)

**Referencia del proyecto:** Arquitectura A — Ventiladores Internos  
**Línea base:** Trayectoria candidata A07 (Escala de referencia: 5 kg)  
**Directorio de trabajo:** Sandbox aislado de revisión cinemática  
**Archivos de entrada consultados:**  
- `entradas/investigacion-aeronautica/modelos_integrados/producto_A07/LEEME.md`  
- `entradas/.../salidas/cinematica_A07.py`  
- `entradas/.../salidas/test_cinematica.py`  
- `entradas/.../salidas/INFORME_PARAMETRIZACION_A07.md`  
- `entradas/.../salidas/resultados_perfiles.json`  

---

## 1. RESUMEN EJECUTIVO Y OBJETIVOS DE LA REVISIÓN

El presente informe audita, depura y corrige la formulación cinemática de dos grados de libertad (2-DOF) para la apertura de compuertas en la arquitectura A07. La trayectoria nominal comprende:
1. **Fase 1 (Traslación pura exterior):** Desplazamiento normal de $10\text{ mm}$ en la escala de referencia de $5\text{ kg}$ ($+Z$ compuertas superiores, $-Z$ compuertas inferiores en marco CAD).
2. **Fase 2 (Rotación pura exterior):** Giro de $110^\circ$ ($1.919862\text{ rad}$) alrededor del eje longitudinal transportado solidario con la compuerta.

### Correcciones principales efectuadas respecto al informe previo:
1. **Resolución de contradicción en Jerk:** El informe anterior postulaba simultáneamente jerk nulo en reposo/fronteras y reconocía que la derivada tercera del polinomio quíntico es $60$ en extremos. Se derivan analíticamente los límites unilaterales del movimiento frente al reposo estático, demostrando que la trayectoria es estrictamente de clase $C^2$ (posición, velocidad y aceleración continuas) y que el jerk experimenta saltos finitos no nulos en todas las fronteras de conmutación.
2. **Corrección de afirmación sobre aceleración pico:** Se refuta la afirmación sin demostración de que el polinomio quíntico minimiza la aceleración pico entre todos los perfiles posibles. Se demuestra matemáticamente que el quíntico minimiza la integral cuadrática de jerk ($\int (\dddot{q})^2 dt$), pero perfiles como el bang-bang (aceleración constante) o trapezoidales obtienen aceleraciones pico sensiblemente inferiores.
3. **Portabilidad de código y pruebas:** Se corrigieron fallos de ejecución debidos a asunciones de rutas rígidas hacia archivos no copiados en `entradas/` (`propuesta_elevacion.json`, `VERIFICACION_RECORRIDO.json`, `C02_CANDIDATA.json`). Conforme a la directriz operativa de no inferir la inexistencia de archivos no copiados, se encapsularon las especificaciones nominales A07 para permitir una verificación autónoma y pruebas unitarias portables.
4. **Respeto a la geometría A07 y ausencia de mecanismo aprobado:** Se conserva estrictamente la geometría A07 y se reitera que se trata de un estudio cinemático de recorrido, no de un mecanismo real aprobado ni validado para vuelo.

---

## 2. DISTINCIÓN METODOLÓGICA: DATOS MEDIDOS, SUPUESTOS Y CÁLCULOS

Para asegurar trazabilidad e integridad técnica:

### 2.1 Datos Medidos / Referencias CAD Confirmadas (desde `LEEME.md`)
* **Arquitectura:** Rotores fijos en fuselaje; ocho compuertas móviles (4 superiores, 4 inferiores).
* **Trayectoria candidata:**
  * Traslación exterior de $10.0\text{ mm}$ a escala $5\text{ kg}$.
  * Giro exterior de $110^\circ$ alrededor de un eje longitudinal transportado.
  * Escalamiento de desplazamientos con factor $\lambda = (M/5)^{1/3}$ ($7.37\text{ mm}$ en $2\text{ kg}$, $10.00\text{ mm}$ en $5\text{ kg}$, $12.60\text{ mm}$ en $10\text{ kg}$).
* **Ejes nominales y signos:** Documentados en la especificación geométrica A07 (superiores $+Z$, inferiores $-Z$; rotaciones exteriores alejándose del plano de simetría $Y=0$).
* **Estado de archivos no copiados:** Los archivos `propuesta_elevacion.json`, `VERIFICACION_RECORRIDO.json` y `C02_CANDIDATA.json` no fueron transferidos al directorio `entradas/` de esta sesión. Conforme a las instrucciones, **no se infiere que dichos archivos no existan**; sus datos tabulados se contrastan contra la especificación nominal A07.

### 2.2 Datos Supuestos (Hipótesis declaradas)
* **Masa e inercia de compuerta:** En los archivos de diseño preliminar figura `"actual_mass_kg": null`, `"actual_CG_m": null`, `"actual_inertia_kgm2": null`.  
  * **Regla estricta aplicada:** No se infiere que una reserva sin masa asignada tenga masa real nula o no nula; el valor real es **desconocido**.
  * Únicamente a modo de ilustración paramétrica de fuerzas inerciales, se adopta como hipótesis de trabajo una masa de referencia $m_{\text{tapa, 5kg}} = 0.050\text{ kg}$ ($50\text{ g}$) y un radio de giro $r_g = 0.040\text{ m}$ ($40\text{ mm}$).
  * Todos los cálculos primarios se reportan como magnitudes cinemáticas normalizadas ($a_{\max} = F/m$ en $\text{m/s}^2$ y $\alpha_{\max} = \tau/I$ en $\text{rad/s}^2$), independientes de cualquier supuesto de masa.

### 2.3 Cálculos Realizados
* Límites unilaterales y saltos analíticos en $t=0$, $t=T$ y $t=2T$.
* Evaluación de perfiles quíntico y cicloidal y sus derivadas analíticas.
* Matriz paramétrica de escalamiento temporal ($1/T^2$ para aceleración, $1/T^3$ para salto de jerk) y geométrico ($(M/5)^{1/3}$).
* Comprobaciones cruzadas contra diferencias finitas centradas de alta precisión ($dt = 10^{-5}\text{ s}$).

---

## 3. FORMULACIÓN CINEMÁTICA Y RESOLUCIÓN DE LA CONTRADICCIÓN DE JERK

### 3.1 Perfil Quíntico Normalizado
El perfil polinómico quíntico en tiempo normalizado $\tau = t/T \in [0, 1]$ es:
$$s(\tau) = 10\tau^3 - 15\tau^4 + 6\tau^5$$
Sus derivadas son:
$$\frac{ds}{d\tau} = 30\tau^2(1 - \tau)^2$$
$$\frac{d^2s}{d\tau^2} = 60\tau(1 - \tau)(1 - 2\tau)$$
$$\frac{d^3s}{d\tau^3} = 60(1 - 6\tau + 6\tau^2)$$

Condiciones de frontera del perfil normalizado:
* $s(0) = 0, \quad s(1) = 1$
* $s'(0) = 0, \quad s'(1) = 0$
* $s''(0) = 0, \quad s''(1) = 0$
* **$s'''(0) = 60, \quad s'''(1) = 60$**

### 3.2 Análisis de la Contradicción
El informe previo afirmaba:
> *"velocidad, aceleración y jerk nulos en reposo estático"*
y a la vez reconocía:
> *"En $\tau=0$ y $\tau=1$, $\frac{d^3s}{d\tau^3} = 60$"*

**Resolución física y matemática:**  
En reposo estático ($t < 0$, $t > 2T$ o durante la fase inactiva de una coordenada), la posición es constante y por tanto velocidad, aceleración y jerk son idénticamente nulos. Sin embargo, al iniciar o finalizar el movimiento polinómico quíntico, la derivada tercera evaluada desde el interior del intervalo de movimiento tiende a $\frac{\Delta}{T^3} s'''(0^+) = \frac{60\Delta}{T^3} \neq 0$.  

Por consiguiente, el jerk **no es nulo en las fronteras de movimiento**; presenta discontinuidades de salto finito.

---

## 4. DERIVACIÓN ANALÍTICA DE LÍMITES UNILATERALES FRENTE AL REPOSO

Sea $T$ la duración de cada fase. El movimiento total abarca $t \in [0, 2T]$.

### 4.1 Frontera Inicial: $t = 0$ (Transición de reposo previo a Fase 1)
* **Límite unilateral izquierdo ($t \to 0^-$ — reposo estático previo):**
  $$\lim_{t \to 0^-} q_1(t) = 0, \quad \lim_{t \to 0^-} \dot{q}_1(t) = 0, \quad \lim_{t \to 0^-} \ddot{q}_1(t) = 0, \quad \lim_{t \to 0^-} \dddot{q}_1(t) = 0$$
* **Límite unilateral derecho ($t \to 0^+$ — inicio de elevación):**
  $$\lim_{t \to 0^+} q_1(t) = 0, \quad \lim_{t \to 0^+} \dot{q}_1(t) = 0, \quad \lim_{t \to 0^+} \ddot{q}_1(t) = 0, \quad \lim_{t \to 0^+} \dddot{q}_1(t) = \frac{d_{\max}}{T^3} s'''(0^+) = +\frac{60 \, d_{\max}}{T^3}$$
* **Continuidad y saltos en $t = 0$:**
  * $\Delta q_1(0) = 0 \implies \text{Continuidad } C^0$
  * $\Delta \dot{q}_1(0) = 0 \implies \text{Continuidad } C^1$
  * $\Delta \ddot{q}_1(0) = 0 \implies \text{Continuidad } C^2$
  * **Salto de Jerk:** $\Delta \dddot{q}_1(0) = \lim_{t \to 0^+} \dddot{q}_1(t) - \lim_{t \to 0^-} \dddot{q}_1(t) = +\frac{60 \, d_{\max}}{T^3} \neq 0$

### 4.2 Frontera Intermedia: $t = T$ (Conmutación de Fase 1 a Fase 2)
* **Coordenada $q_1$ (traslación):**
  * $\lim_{t \to T^-} q_1 = d_{\max}, \quad \lim_{t \to T^-} \dot{q}_1 = 0, \quad \lim_{t \to T^-} \ddot{q}_1 = 0, \quad \lim_{t \to T^-} \dddot{q}_1 = +\frac{60 \, d_{\max}}{T^3}$
  * $\lim_{t \to T^+} q_1 = d_{\max}, \quad \lim_{t \to T^+} \dot{q}_1 = 0, \quad \lim_{t \to T^+} \ddot{q}_1 = 0, \quad \lim_{t \to T^+} \dddot{q}_1 = 0$ (Fase 2 fija)
  * **Salto de Jerk en $q_1$:** $\Delta \dddot{q}_1(T) = 0 - \frac{60 \, d_{\max}}{T^3} = -\frac{60 \, d_{\max}}{T^3} \neq 0$
* **Coordenada $q_2$ (rotación):**
  * $\lim_{t \to T^-} q_2 = 0, \quad \lim_{t \to T^-} \dot{q}_2 = 0, \quad \lim_{t \to T^-} \ddot{q}_2 = 0, \quad \lim_{t \to T^-} \dddot{q}_2 = 0$ (Fase 1 reposo)
  * $\lim_{t \to T^+} q_2 = 0, \quad \lim_{t \to T^+} \dot{q}_2 = 0, \quad \lim_{t \to T^+} \ddot{q}_2 = 0, \quad \lim_{t \to T^+} \dddot{q}_2 = +\frac{60 \, \theta_{\max}}{T^3}$
  * **Salto de Jerk en $q_2$:** $\Delta \dddot{q}_2(T) = +\frac{60 \, \theta_{\max}}{T^3} - 0 = +\frac{60 \, \theta_{\max}}{T^3} \neq 0$

### 4.3 Frontera Final: $t = 2T$ (Llegada a reposo en pose abierta)
* **Coordenada $q_2$:**
  * $\lim_{t \to (2T)^-} q_2 = \theta_{\max}, \quad \lim_{t \to (2T)^-} \dot{q}_2 = 0, \quad \lim_{t \to (2T)^-} \ddot{q}_2 = 0, \quad \lim_{t \to (2T)^-} \dddot{q}_2 = +\frac{60 \, \theta_{\max}}{T^3}$
  * $\lim_{t \to (2T)^+} q_2 = \theta_{\max}, \quad \lim_{t \to (2T)^+} \dot{q}_2 = 0, \quad \lim_{t \to (2T)^+} \ddot{q}_2 = 0, \quad \lim_{t \to (2T)^+} \dddot{q}_2 = 0$
  * **Salto de Jerk en $q_2$:** $\Delta \dddot{q}_2(2T) = 0 - \frac{60 \, \theta_{\max}}{T^3} = -\frac{60 \, \theta_{\max}}{T^3} \neq 0$

### 4.4 Comparativa con Perfil Cicloidal
Para el perfil cicloidal $s_{\text{cyc}}(\tau) = \tau - \frac{1}{2\pi}\sin(2\pi\tau)$, su tercera derivada es $s_{\text{cyc}}'''(\tau) = 4\pi^2\cos(2\pi\tau)$.  
En $\tau=0$ y $\tau=1$, $s_{\text{cyc}}''' = 4\pi^2 \approx 39.4784$.  
Por tanto, el perfil cicloidal **también experimenta saltos finitos de jerk**: $\Delta \dddot{q} = \pm \frac{4\pi^2\Delta}{T^3}$.

### Conclusión sobre Continuidad
Ambos perfiles garantizan continuidad estricta $C^0$, $C^1$ y $C^2$ (posición, velocidad y aceleración continuas). **Ninguno es de clase $C^3$**, ya que el jerk sufre saltos escalón instantáneos al conectarse con el reposo.

---

## 5. CORRECCIÓN: ACELERACIÓN PICO FRENTE A OTROS PERFILES

El informe anterior afirmaba sin demostración:
> *"El polinomio quíntico optimiza la suavidad y minimiza la aceleración pico y el jerk cuadrático integral."*

### Demostración de Refutación:
1. **Lo que realmente minimiza el quíntico:**  
   Es la solución variacional exacta a las ecuaciones de Euler-Lagrange para minimizar la integral cuadrática de jerk:
   $$\min \int_0^T (\dddot{q}(t))^2 \, dt \quad \text{sujeto a } q(0), \dot{q}(0), \ddot{q}(0), q(T), \dot{q}(T), \ddot{q}(T) \text{ fijos.}$$
2. **Comparativa de aceleración máxima normalizada ($a_{\max} \cdot T^2 / \Delta$):**
   * **Perfil parabólico (bang-bang con aceleración constante por tramos):**  
     $a_{\text{bang-bang, max}} = 4.0$ (30.7% menor que el quíntico).
   * **Perfil trapezoidal de velocidad:**  
     $a_{\text{trapezoidal, max}} \approx 4.5$ (22.1% menor que el quíntico).
   * **Perfil quíntico:**  
     $a_{\text{quíntico, max}} = \frac{10\sqrt{3}}{3} \approx 5.7735$.
   * **Perfil cicloidal:**  
     $a_{\text{cicloidal, max}} = 2\pi \approx 6.2832$.
3. **Corrección formal:**  
   El perfil quíntico reduce la aceleración pico respecto al perfil cicloidal en un $8.1\%$, pero **NO minimiza la aceleración pico global** entre todos los perfiles cinemáticos posibles. La afirmación anterior queda formalmente refutada y corregida.

---

## 6. MATRIZ DE ESCALAMIENTO Y CINEMÁTICA DE EXTREMOS

A continuación se resume la matriz corregida para las tres escalas de masa y duraciones de fase:

| Masa (kg) | $T_{\text{fase}}$ (s) | $d_{\max}$ (mm) | $v_{1, \max}$ (mm/s) | $a_{1, \max}$ ($\text{m/s}^2$) | $|\Delta \dddot{q}_1|$ ($\text{m/s}^3$) | $\omega_{2, \max}$ (rad/s) | $\alpha_{2, \max}$ ($\text{rad/s}^2$) | $|\Delta \dddot{q}_2|$ ($\text{rad/s}^3$) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2.0** | 0.5 | 7.37 | 27.63 | 0.1702 | **3.5367** | 7.20 | 44.3373 | **921.5338** |
| **2.0** | 1.0 | 7.37 | 13.82 | 0.0425 | **0.4421** | 3.60 | 11.0843 | **115.1917** |
| **2.0** | 2.0 | 7.37 | 6.91 | 0.0106 | **0.0553** | 1.80 | 2.7711 | **14.3990** |
| **5.0** | 0.5 | 10.00 | 37.50 | 0.2309 | **4.8000** | 7.20 | 44.3373 | **921.5338** |
| **5.0** | 1.0 | 10.00 | 18.75 | 0.0577 | **0.6000** | 3.60 | 11.0843 | **115.1917** |
| **5.0** | 2.0 | 10.00 | 9.38 | 0.0144 | **0.0750** | 1.80 | 2.7711 | **14.3990** |
| **10.0** | 0.5 | 12.60 | 47.25 | 0.2910 | **6.0476** | 7.20 | 44.3373 | **921.5338** |
| **10.0** | 1.0 | 12.60 | 23.62 | 0.0727 | **0.7560** | 3.60 | 11.0843 | **115.1917** |
| **10.0** | 2.0 | 12.60 | 11.81 | 0.0182 | **0.0945** | 1.80 | 2.7711 | **14.3990** |

### Leyes de Escalamiento Confirmadas:
1. **Desplazamiento:** Escala con $(M/5)^{1/3}$ ($7.37\text{ mm}$ a $2\text{ kg}$, $10.00\text{ mm}$ a $5\text{ kg}$, $12.60\text{ mm}$ a $10\text{ kg}$).
2. **Aceleración:** Escala con $1/T^2$ (una reducción de $T$ de $1.0\text{ s}$ a $0.5\text{ s}$ cuadruplica la aceleración).
3. **Salto de Jerk:** Escala con $1/T^3$ (una reducción de $T$ de $1.0\text{ s}$ a $0.5\text{ s}$ multiplica el salto de jerk por un factor de $8$).

---

## 7. AUDITORÍA GEOMÉTRICA DE LAS 8 COMPUERTAS A07

Se verificaron las 8 compuertas contra la especificación geométrica nominal A07:

| ID Compuerta | Eje Closed $[X, Y, Z]$ (mm) | Elevación (`out`) | Rotación (`sign`) | Comportamiento Geométrico |
|---|:---:|:---:|:---:|---|
| `compuerta_0_superior_enrasada` | $[-200.0, -124.0, +65.462]$ | $+1$ ($+Z$) | $+1$ | Sube $+10\text{ mm}$, gira exterior hacia $-Y$ |
| `compuerta_0_inferior_enrasada` | $[-200.0, -124.0, -51.813]$ | $-1$ ($-Z$) | $-1$ | Baja $-10\text{ mm}$, gira exterior hacia $-Y$ |
| `compuerta_1_superior_enrasada` | $[-200.0, +124.0, +65.462]$ | $+1$ ($+Z$) | $-1$ | Sube $+10\text{ mm}$, gira exterior hacia $+Y$ |
| `compuerta_1_inferior_enrasada` | $[-200.0, +124.0, -51.813]$ | $-1$ ($-Z$) | $+1$ | Baja $-10\text{ mm}$, gira exterior hacia $+Y$ |
| `compuerta_2_superior_enrasada` | $[+200.0, -124.0, +45.510]$ | $+1$ ($+Z$) | $+1$ | Sube $+10\text{ mm}$, gira exterior hacia $-Y$ |
| `compuerta_2_inferior_enrasada` | $[+200.0, -124.0, -34.382]$ | $-1$ ($-Z$) | $-1$ | Baja $-10\text{ mm}$, gira exterior hacia $-Y$ |
| `compuerta_3_superior_enrasada` | $[+200.0, +124.0, +45.510]$ | $+1$ ($+Z$) | $-1$ | Sube $+10\text{ mm}$, gira exterior hacia $+Y$ |
| `compuerta_3_inferior_enrasada` | $[+200.0, +124.0, -34.382]$ | $-1$ ($-Z$) | $+1$ | Baja $-10\text{ mm}$, gira exterior hacia $+Y$ |

Todas las compuertas se desplazan hacia el exterior del conducto ($+Z$ superiores, $-Z$ inferiores) y abren girando en alejamiento del plano de simetría $Y=0$.

---

## 8. COMPARATIVA DE CONCEPTOS MECÁNICOS

> **ADVERTENCIA FORMAL:** Ninguno de los dos conceptos mecánicos ha sido aprobado, fabricado ni sometido a estudio de empaquetamiento volumétrico. No se afirma que quepan ni se aprueba ningún mecanismo real para vuelo.

* **Concepto 1: Carro lineal + Bisagra transportada (Cadena serial Prismático-Revoluta)**  
  * *Ventajas:* Desacoplamiento cinemático total de traslación y rotación; contacto superficial (menor concentración de tensiones); facilidad de recalibración de límites por software o topes.  
  * *Riesgos:* Mayor masa móvil sobre el carro; susceptibilidad a bloqueo por ladeo (*cocking/binding*) bajo momentos aerodinámicos; dificultad de sellado contra flujo en conductos.
* **Concepto 2: Ranura / Cam con guiado de seguidor (Leva de ranura programada de 1-DOF)**  
  * *Ventajas:* Sincronización intrínseca garantizada geométricamente (imposible rotar antes de la traslación completa); actuador único y fijo a la estructura del fuselaje.  
  * *Riesgos:* Contacto de línea/puntual de Hertz con altas tensiones locales y riesgo de desgaste/picado; ángulo de presión crítico en la transición recto-curvo (riesgo de autoenclavamiento); rigidez total de ajuste post-fabricación.

---

## 9. DECLARACIÓN DE VARIABLES NO VERIFICABLES Y LIMITACIONES

Conforme a las instrucciones de distinguir estrictamente datos medidos, supuestos y cálculos:
1. **Masa e inercia real:** En los datos de entrada la masa figura como `null`. No se infiere masa nula ni no nula; el valor real es **desconocido**.
2. **Empaquetamiento y herrajes:** No existen guías, bielas, servomotores o bisagras dimensionados en el CAD A07. No se afirma mecanismo real aprobado.
3. **Cargas aerodinámicas y avance:** Conforme a `LEEME.md`, la trayectoria está destinada al estudio de baja velocidad; no se valida su uso en avance rápido y los solvers CFD continúan pausados.
4. **Respuesta del actuador y elasticidad:** Desconocida (`servo_response_s: null`); el cribado CAD es estático nominal y no evalúa deformaciones elásticas o vibraciones.

---

## 10. SUITE DE PRUEBAS AUTOMATIZADAS Y ENTREGABLES

### 10.1 Pruebas Unitarias Ejecutadas (`salidas/test_cinematica.py`)
Se ejecutaron 13 pruebas unitarias automatizadas con `unittest` (`Ran 13 tests, OK, skipped=2`):
* `test_quintic_boundary_conditions`: Comprueba $s, s', s''$ nulas en extremos y $s''' = 60 \neq 0$ (OK).
* `test_cycloidal_boundary_conditions`: Comprueba condiciones de contorno y $s''' = 4\pi^2 \neq 0$ (OK).
* `test_trajectory_extrema_and_endpoints`: Comprueba estados en $t=0$, $t=T$ y $t=2T$ (OK).
* `test_c2_continuity_and_jerk_jump_at_switch`: Comprueba continuidad $C^2$ y discontinuidad de jerk en $t=T$ (OK).
* `test_unilateral_limits_and_jerk_jumps_at_all_boundaries`: Prueba precisa de límites unilaterales frente a reposo en $0, T, 2T$ (OK).
* `test_peak_acceleration_not_globally_minimal`: Demuestra que el bang-bang supera al quíntico en aceleración pico (OK).
* `test_mass_scaling_values`: Comprueba $7.37$, $10.00$ y $12.60\text{ mm}$ (OK).
* `test_acceleration_time_scaling`: Comprueba escalamiento con $1/T^2$ (OK).
* `test_jerk_time_scaling_inverse_cube`: Comprueba escalamiento de jerk con $1/T^3$ (OK).
* `test_nominal_doors_geometry_and_signs`: Comprueba signos y coordenadas de las 8 compuertas (OK).
* `test_door_spatial_transform`: Comprueba transformaciones espaciales 3D (OK).
* `test_propuesta_elevacion_file_conditional`: Comprobación condicional omitida cleanly ante archivo no copiado (OK, skipped).
* `test_recorrido_file_conditional`: Comprobación condicional omitida cleanly ante archivo no copiado (OK, skipped).

### 10.2 Archivos Generados en `salidas/`
1. `salidas/cinematica_A07.py`: Motor cinemático portable, evaluador de límites unilaterales, matriz de escalamiento y comprobaciones.
2. `salidas/test_cinematica.py`: Suite de 13 pruebas unitarias portables.
3. `salidas/resultados_perfiles.json`: Matriz de cinemática temporal, límites unilaterales y precisión de derivadas.
4. `salidas/verificacion_signos_tapas.json`: Verificación de signos y geometría de las 8 compuertas A07.
5. `salidas/comparativa_mecanismos.json`: Detalle estructurado de la comparativa carro+bisagra vs ranura/cam.
6. `salidas/INFORME_PARAMETRIZACION_A07.md`: El presente informe técnico corregido.
