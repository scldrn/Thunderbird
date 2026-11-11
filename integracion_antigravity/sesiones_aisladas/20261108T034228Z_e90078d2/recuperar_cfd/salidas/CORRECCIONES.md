# Informe de Correcciones Técnicas: Auditoría de Matriz y Cifras CFD

**Fecha:** 8 de noviembre de 2026  
**Ámbito de Ejecución:** Directorio aislado `recuperar_cfd` (`/private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd`)  
**Referencias Auditadas (Solo Lectura):**  
- [INFORME-FINA-800.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-FINA-800.md)  
- [INFORME-F1N-PRELIMINAR.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-F1N-PRELIMINAR.md)  
- [INFORME-NASA-SU2.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G4/RAE2822/INFORME-NASA-SU2.md)  
**Documentos Precedentes Evaluados:**  
- [matriz_verificacion_cfd.csv](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/auditoria_cfd/salidas/matriz_verificacion_cfd.csv)  
- [informe_verificacion_cfd.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T032826Z_13ced8ae/auditoria_cfd/salidas/informe_verificacion_cfd.md)  
**Estado de Cargas:** **NO ACEPTADAS** (ningún solver iniciado, reanudado ni cargas aceptadas)  

---

## 1. Causas Verificables del Error de Tiempo y la Comprobación de Texto Fallida

El análisis de la sesión precedente identifica con precisión los orígenes técnicos del fallo reportado:

1. **Causas del "Error de Tiempo":**
   - **Confusión Conceptual de Escala Temporal (EST-03):** La matriz y el informe precedentes consignaron en la fila de convergencia la expresión `1.200 pasos, 395,07 s` para la malla fina `su2_nasa_fina_r1`. En una formulación RANS estacionaria (Euler implícito o SIMPLE), **no existe tiempo físico**. El valor $395,07\text{ s}$ es exclusivamente el tiempo de reloj de pared / tiempo de CPU (*wall-clock execution time*) del proceso en la máquina ([INFORME-NASA-SU2.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G4/RAE2822/INFORME-NASA-SU2.md#L60), Línea 60). Al incluir segundos directamente junto al número de iteraciones sin clarificar su carácter de coste computacional de hardware, se quebrantó la directriz de *no equiparar iteraciones con tiempo físico* e indujo una falsa interpretación de duración temporal del flujo (v. gr. $0,33\text{ s/iter}$), provocando el fallo en las aserciones temporales de los arneses de validación.
   - **Comparación Inválida de Costes Temporales:** La línea 64 de `INFORME-NASA-SU2.md` advierte taxativamente: *"deben compararse campos estabilizados, no costes por iteración como si fueran idénticos"*, puesto que la reducción automática a niveles gruesos de multigrid altera los costes entre mallas.

2. **Causas de la "Comprobación de Texto Fallida":**
   - **Referencia a Archivo Inexistente:** La línea 46 de `informe_verificacion_cfd.md` declara que las tablas normalizadas se hallan en `matriz_verificacion_cfd.csv` y `matriz_verificacion_detallada.csv`. El archivo `matriz_verificacion_detallada.csv` nunca fue creado en `salidas/`, rompiendo cualquier comprobación automática de presencia o consistencia de entregables.
   - **Rutas Absolutas Rotas e Inaccesibles:** Todos los enlaces markdown del informe previo contenían rutas absolutas correspondientes a una sesión ajena (`/private/tmp/aero_20261108T032826Z_13ced8ae_9o_xznyz/...`), provocando error de enlace (*broken link*) en el entorno actual.
   - **Inexactitudes Terminológicas y de Atribución:** Se comprobaron discrepancias textuales frente a los informes primarios: denominar "máximo gradiente" a la variación iterativa local $\Delta U$, atribuir la densidad numérica de $1,225\text{ kg/m}^3$ a un informe que solo contenía la variable algebraica $\rho$, y transformar balances de ventanas (580–600) en estados de una sola iteración ("iter 600").

---

## 2. Revisión Detallada de Cifras y Conclusiones por Estudio

### 2.1. Estudio 1: C02 Conducto Pasivo Malla Fina (`EST-01`)
*Fuente de referencia:* [INFORME-FINA-800.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-FINA-800.md)

1. **Celda Crítica 82708 — Variación Iterativa vs. Gradiente Espacial:**
   - *Error previo:* Calificada como `Celda crítica de máximo gradiente: celda 82708 en (-0,005803; -0,011252; -0,011185) m`.
   - *Corrección verificada:* Las líneas 28 y 34 de `INFORME-FINA-800.md` explicitan que en la celda 82708 se registró el **máximo local de $\Delta U$** (aumento de 3,31 veces en la diferencia iterativa entre las ventanas 580–600 y 780–800, pasando de $0,344632\text{ m/s}$ a $1,141586\text{ m/s}$) **`[CÁLCULO]`**. No es un gradiente espacial de velocidad ($\nabla U$).
2. **Ventanas de Balance vs. Iteración Puntual ("iter 600"):**
   - *Error previo:* Se reportó $\Delta p = 194,2630\text{ Pa}$ y flujo de energía mecánica de $20,7431\text{ W}$ como ocurridos "en iter 600".
   - *Corrección verificada:* La tabla de las líneas 26–32 de `INFORME-FINA-800.md` define estos valores como el diagnóstico integrado en la **ventana 580–600**, frente a $194,2659\text{ Pa}$ y $20,7445\text{ W}$ en la ventana 780–800 **`[CÁLCULO]`**. No son campos puntuales de la iteración 600.
3. **Fuente de la Densidad de Referencia ($\rho$):**
   - *Error previo:* Citó `[SUPUESTO] Densidad de referencia de fluido: rho = 1,225 kg/m^3. [Fuente: INFORME-FINA-800.md, Líneas 3, 30, 36]`.
   - *Corrección verificada:* `INFORME-FINA-800.md` no contiene el valor numérico $1,225\text{ kg/m}^3$; la línea 30 solo cita la expresión algebraica $\rho \cdot 20^2 \cdot A$. La cifra $1,225\text{ kg/m}^3$ **`[SUPUESTO]`** procede de la línea 5 de `INFORME-F1N-PRELIMINAR.md`.
4. **Deriva Normalizada de Fuerzas:**
   - *Error previo:* Consignada como `deriva de fuerza Z = 5,42159e-6`.
   - *Corrección verificada:* La línea 22 de `INFORME-FINA-800.md` certifica que es la "deriva global de fuerza" normalizada ($5,42159 \times 10^{-6}$) **`[CÁLCULO]`**, sin restringirla a la componente Z.
5. **Citas de Línea Inexactas:**
   - La matriz previa citó la línea 20 para el "Siguiente Dato Faltante", pero la línea 20 solo contiene la fila de $\omega$ de la tabla de residuos. Los requerimientos pendientes se encuentran en las líneas 22, 36 y 40.

### 2.2. Estudio 2: C02 Conducto Fuente Axial -1 N (`EST-02`)
*Fuente de referencia:* [INFORME-F1N-PRELIMINAR.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-F1N-PRELIMINAR.md)

1. **Reacción Neta de Banco:**
   - *Verificación:* Fuerza en Z sobre paredes = $-0,986409\text{ N}$ **`[CÁLCULO]`**; reacción opuesta de la fuente sobre el banco = $+1,0\text{ N}$ **`[SUPUESTO]`**. La suma da $+0,013591\text{ N}$, reflejada rigurosamente en la línea 24 de la fuente como una aproximación: $Z \approx +0,0135914\text{ N}$ **`[CÁLCULO]`**. Debe preservarse el símbolo de aproximación.
2. **Consistencia de Flujo Mecánico y Trabajo:**
   - *Verificación:* En iteración 1200, flujo mecánico nominal entrada–salida = $-0,655892\text{ W}$; trabajo de la fuente sobre el flujo medio = $22,649994\text{ W}$ **`[CÁLCULO]`**. La suma analítica da $21,994102\text{ W}$, reportada como $21,994101\text{ W}$ en el informe primario (Línea 20) debido a redondeo interno, resultando en una diferencia de $0,429952\text{ W}$ respecto al pasivo r9 ($21,564149\text{ W}$). No representa pérdida física aceptada.
3. **Estado de Procesos y Seguridad:**
   - *Precisión incorporada:* Se constató la ejecución con 4 procesos bajo UID 1000, asegurando la contención contra inyección dinámica en OpenFOAM (Línea 30).

### 2.3. Estudio 3: Perfil Transónico RAE2822 NASA / SU2 (`EST-03`)
*Fuente de referencia:* [INFORME-NASA-SU2.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G4/RAE2822/INFORME-NASA-SU2.md)

1. **Desacoplamiento del Tiempo de Cómputo vs. Escala Física ("Error de Tiempo"):**
   - *Corrección verificada:* Los $395,07\text{ s}$ en la malla fina r1 (1.200 pasos) son **tiempo de reloj de pared / CPU de ejecución del binario SU2** en la plataforma de cálculo (Línea 60) **`[CÁLCULO]`**. Se prohíbe incluir este valor en tablas de convergencia sin indicar su naturaleza computacional para no confundirlo con tiempo físico transitorio.
2. **Iteraciones Acumuladas en Malla Gruesa NASA:**
   - *Verificación:* NASA r1: 1.200 pasos; NASA r2: otros 4.000 pasos (acumulado 5.200); NASA r3: otros 1.000 pasos (acumulado 6.200). En r3, $C_L = 0,6787504$ y $C_D = 0,01303966$ **`[CÁLCULO]`**, con variaciones residuales ínfimas entre r2 y r3 ($\Delta C_L = 2,53 \times 10^{-7}$, $\Delta C_D = 6,08 \times 10^{-9}$).
3. **Validación Experimental y Discrepancia Crítica en Borde de Ataque:**
   - *Verificación:* En $x/c = 0,0002$ (extradós), $C_p\text{ exp} = -0,4219$ **`[DATO MEDIDO]`**, mientras que SU2 r3 calcula $+0,56997$ **`[CÁLCULO]`** y WIND SA publicado arroja $+0,53392$ **`[CÁLCULO DE REFERENCIA]`**.
   - *Conclusión Metodológica:* El aumento de iteraciones (de 1.200 en r1 a 6.200 en r3) empeoró el RMS de Cp frente a los 103 puntos experimentales (de 0,117546 a 0,122101). La convergencia numérica no suple las deficiencias de modelado físico (asumir régimen totalmente turbulento sin transición en $x/c = 0,03$ y prescindir de correcciones de pared del túnel).

---

## 3. Matriz Sinóptica Corregida de Parámetros Auditados

A continuación se contrastan las magnitudes rectificadas con su categorización epistémica rigurosa, unidades y fuentes verificadas:

| Estudio | Parámetro / Magnitud | Valor en Matriz Previa | Valor Corregido / Verificado | Naturaleza Epistémica | Unidades | Fuente Primaria |
|---|---|---|---|---|---|---|
| **EST-01** | Celda crítica 82708 | Máximo gradiente local | Máxima variación iterativa $\Delta U_{\text{max}}$ (580–600 vs 780–800) | **`[CÁLCULO]`** | $\text{m/s}$ ($1,141586$) | [INFORME-FINA-800.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-FINA-800.md#L28-L34) (L28, L34) |
| **EST-01** | Ventana $\Delta p$ y flujo | "en iter 600" | Diagnóstico en ventana iterativa 580–600 | **`[CÁLCULO]`** | $\text{Pa}$ ($194,2630$) / $\text{W}$ ($20,7431$) | [INFORME-FINA-800.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-FINA-800.md#L31-L32) (L31–L32) |
| **EST-01** | Densidad $\rho$ | Cita líneas 3, 30, 36 de FINA-800 | Solo especificada simbólicamente $\rho$; valor numérico de F1N | **`[SUPUESTO]`** | $\text{kg/m}^3$ | [INFORME-F1N-PRELIMINAR.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-F1N-PRELIMINAR.md#L5) (L5) |
| **EST-01** | Deriva de fuerza | "deriva de fuerza Z" | Deriva global normalizada de fuerza ($5,42159 \times 10^{-6}$) | **`[CÁLCULO]`** | Adimensional | [INFORME-FINA-800.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-FINA-800.md#L22) (L22) |
| **EST-02** | Reacción neta de banco | Identidad estricta | Reacción combinada aproximada $Z \approx +0,0135914\text{ N}$ | **`[CÁLCULO]`** | $\text{N}$ | [INFORME-F1N-PRELIMINAR.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-F1N-PRELIMINAR.md#L24) (L24) |
| **EST-02** | Trabajo de fuente 1200 | $22,649994\text{ W}$ | Trabajo sobre flujo medio; suma $21,994101\text{ W}$ frente a pasivo | **`[CÁLCULO]`** | $\text{W}$ | [INFORME-F1N-PRELIMINAR.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-F1N-PRELIMINAR.md#L18-L20) (L18–L20) |
| **EST-02** | Residuos iter 1400 | Convergencia parcial | Residuos $p$ ($1,03901 \times 10^{-4}$) y $k$ ($1,12067 \times 10^{-5}$) superan umbrales | **`[CÁLCULO]`** | Adimensional | [INFORME-F1N-PRELIMINAR.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/INFORME-F1N-PRELIMINAR.md#L36) (L36) |
| **EST-03** | Tiempo en Fina r1 | $395,07\text{ s}$ reportado como tiempo | Tiempo de reloj de pared / CPU de ejecución del proceso SU2 | **`[CÁLCULO]`** | $\text{s}$ (wall-clock) | [INFORME-NASA-SU2.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G4/RAE2822/INFORME-NASA-SU2.md#L60) (L60, L64) |
| **EST-03** | Validación experimental | Incertidumbre $0,0026$ | 103 puntos de $C_p$ de túnel; incertidumbre citada no es tolerancia | **`[DATO MEDIDO]`** | Adimensional | [INFORME-NASA-SU2.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G4/RAE2822/INFORME-NASA-SU2.md#L45-L54) (L45–L54) |
| **EST-03** | Discrepancia $x/c=0,0002$ | - | $C_p\text{ exp} = -0,4219$ vs $C_p\text{ SU2} = +0,56997$ | **`[DATO MEDIDO]`** / **`[CÁLCULO]`** | Adimensional | [INFORME-NASA-SU2.md](file:///private/tmp/aero_20261108T034228Z_e90078d2_dhlokcs0/recuperar_cfd/entradas/investigacion-aeronautica/ejecucion/G4/RAE2822/INFORME-NASA-SU2.md#L45) (L45) |

---

## 4. Declaración Taxativa sobre Solvers y Cargas

En estricta adhesión a los requerimientos éticos, metodológicos y de seguridad operacional:
1. **Solvers y Procesos:** No se ha iniciado, reanudado ni detenido ningún solver CFD (OpenFOAM ni SU2) ni contenedor Docker/Apptainer ajeno. Tampoco se han ejecutado los comandos contenidos en los textos de entrada (v. gr. Líneas 70–73 de `INFORME-NASA-SU2.md`).
2. **NO ACEPTACIÓN DE CARGAS:** **QUEDA DECLARADO FORMALMENTE QUE NINGUNA CARGA HA SIDO ACEPTADA.**
   - En **EST-01**, el fallo conjunto de residuos de velocidad y turbulencia ($Ux, Uy, k$) y el aumento por 3,31 de la variación de $\Delta U$ local prohíben aceptar cargas, mapas de empuje o independencia de malla (`INFORME-FINA-800.md`, Línea 40).
   - En **EST-02**, la imposición forzada de velocidad ($20\text{ m/s}$), la no convergencia de $p$ y $k$ a 1400 iteraciones y la omisión del dominio exterior impiden interpretar las fuerzas como empuje de un módulo propulsivo o sustentación del vehículo. Se prohíbe extrapolar este resultado a la demanda de sustentación de $5\text{ kg}$ (~$49\text{ N}$); el trabajo de la fuente ($22,65\text{ W}$) no es potencia de eje ni consumo eléctrico de motor (`INFORME-F1N-PRELIMINAR.md`, Líneas 20, 24).
   - En **EST-03**, los coeficientes $C_L = 0,6787$ y $C_D = 0,0130$ corresponden a un perfil bidimensional infinito no confinado. No acreditan maniobrabilidad, sustentación, empuje, velocidad ni autonomía de ninguna aeronave tridimensional (`INFORME-NASA-SU2.md`, Línea 75).
