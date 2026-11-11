# DICTAMEN DE AUDITORÍA TÉCNICA INDEPENDIENTE
## Paquete de Procesamiento Aerodinámico de Avance UIUC
### Hélice Abierta Micro Invent 3.2x2.2 @ 20.051 RPM (Corrida UIUC 0544rd_20051)

**Fecha de Auditoría:** Noviembre 2026  
**Auditor:** Agente Independiente de Auditoría y Aseguramiento de Calidad Aeroespacial  
**Entorno de Trabajo:** Directorio aislado de auditoría temporal (`qa_uiuc_avance`)  
**Fuentes de Referencia:** `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/` (solo lectura)  
**Paquete Auditado:** `entradas/investigacion-aeronautica/integracion_antigravity/sesiones_aisladas/20261108T040057Z_075131ca/entregable_uiuc_avance/salidas/` (solo lectura)  
**Entorno de Prueba Aislado:** `salidas/prueba/` (copia autónoma efectuada mediante `shutil.copyfile`)

---

### 1. Resumen y Dictamen Global

Se realizó una auditoría técnica e independiente completa del paquete de procesamiento aerodinámico de avance UIUC. La auditoría comprendió:
1. Verificación de **integridad byte a byte** de los archivos copiados contra las fuentes originales de la base de datos de hélices UIUC (Volumen 2).
2. Verificación analítica y numérica de las **fórmulas aerodinámicas**, conversiones dimensionales y cotas de propagación de redondeo.
3. Evaluación del **dominio de validez física de datos**, límites de aplicabilidad y cumplimiento estricto de las restricciones (no extrapolación a alta velocidad y no asimilación a ventilador C02).
4. Análisis de **rutas relativas y portabilidad** en scripts, pruebas y documentación.
5. Ejecución autónoma y reproducibilidad en la réplica aislada `salidas/prueba/`.

**DICTAMEN FINAL: APROBADO CON OBSERVACIONES (DEFECTOS MENORES DOCUMENTALES Y DE ENLACES).**
- La base numérica, matemática y física es **100% correcta y reproducible**.
- Los 11 ensayos unitarios pasaron exitosamente (`Ran 11 tests in 0.001s, OK`).
- El CSV exportado coincide bit a bit con el entregable preexistente.
- Se detectaron **6 defectos** (ausencia de README de uso, rutas absolutas obsoletas en la documentación, docstrings con rutas inexactas, omisión de prueba para el archivo geométrico, falta de argumentos CLI y una discrepancia marginal de redondeo en una aserción de test). Se generó el `README.md` ausente para subsanar la carencia.

---

### 2. Integridad Byte a Byte contra Originales

Se compararon los archivos de datos presentes en el paquete (`datos/`) frente a los originales de referencia en `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/`:

| Archivo | Tamaño Original [bytes] | Tamaño en Paquete [bytes] | Hash SHA-256 (Original) | Hash SHA-256 (Paquete) | Integridad Byte a Byte |
|:---|:---:|:---:|:---:|:---:|:---:|
| `mi_3.2x2.2_0544rd_20051.txt` | 795 | 795 | `6f3b8d49f0a4595059ea44befe8d946a6044c2a7b97e5eeeeab9051d02e22300` | `6f3b8d49f0a4595059ea44befe8d946a6044c2a7b97e5eeeeab9051d02e22300` | **IDÉNTICO (100%)** |
| `mi_3.2x2.2_geom.txt` | 416 | 416 | `a709e55616905f8e626f4d83fa05d97f2e316e684afa418de972c38301ec3b61` | `a709e55616905f8e626f4d83fa05d97f2e316e684afa418de972c38301ec3b61` | **IDÉNTICO (100%)** |
| `uiuc_mi_3.2x2.2_20051_procesado.csv` | 3735 | 3735 (regenerado) | `c4ea07cc12d12303f32e0237c1fceae3239890218c2890c7f9cfcc9bb808cf88` | `c4ea07cc12d12303f32e0237c1fceae3239890218c2890c7f9cfcc9bb808cf88` | **REPRODUCIBLE BIT A BIT** |

**Conclusión de Integridad:** Se constata integridad criptográfica absoluta contra los originales copiados. No se detectaron alteraciones, corrupciones ni truncamientos en los datos de entrada ni en la salida procesada.

---

### 3. Clasificación Rigurosa de Variables

En concordancia con los principios metrológicos y las directrices del proyecto, se valida la distinción categórica de variables:

1. **Datos Medidos / Registrados (19 puntos tabulados en túnel UIUC):**
   - $J$: Coeficiente de avance adimensional, medido en el rango $[0.044195, 0.448667]$.
   - $C_T$: Coeficiente de empuje aerodinámico, medido en el rango $[0.041281, 0.124104]$.
   - $C_P$: Coeficiente de potencia consumida, medido en el rango $[0.035779, 0.058227]$.
   - $\eta_{reg}$: Rendimiento propulsivo registrado en la tabla, medido en el rango $[0.094195, 0.562131]$.
   - $\text{RPM}_{nominal}$: $20.051\text{ rpm}$ (velocidad rotacional de ensayo).

2. **Supuestos de Ingeniería Adoptados (Parámetros Fijos y Entorno):**
   - Diámetro del rotor: $D = 0.08128\text{ m}$ ($3.2\text{ pulgadas}$ nominales exactas, $3.2 \times 0.0254\text{ m}$).
   - Densidad atmosférica de referencia: $\rho = 1.225\text{ kg/m}^3$ (condición estándar ISA a nivel del mar, $15^\circ\text{C}$, $1013.25\text{ hPa}$).
   - Frecuencia rotacional nominal: $n = \text{RPM} / 60 = 20051.0 / 60.0 = 334.183333...\text{ rev/s}$ (constante durante la corrida).
   - Aceleración estándar de la gravedad: $g = 9.80665\text{ m/s}^2$ (CODATA / OIML).
   - Régimen y geometría: Hélice abierta libre de microescala de dos palas, flujo incompresible libre, sin carenado ni ducto.

3. **Cálculos Analíticos Derivados:**
   - Velocidad de avance: $V = J \cdot n \cdot D\text{ [m/s]}$, $V_{km/h} = V \cdot 3.6\text{ [km/h]}$.
   - Empuje dimensional: $T = C_T \cdot \rho \cdot n^2 \cdot D^4\text{ [N]}$, $T_{gf} = (T / g) \times 1000\text{ [gf]}$.
   - Potencia de eje absorbida: $P = C_P \cdot \rho \cdot n^3 \cdot D^5\text{ [W]}$.
   - Potencia útil de tracción: $P_{out} = T \cdot V\text{ [W]}$.
   - Eficiencia propulsiva clásica: $\eta_{calc} = J \cdot C_T / C_P\text{ [-]}$.
   - Eficiencia ideal de Rankine-Froude: $\eta_{ideal} = \frac{2}{1 + \sqrt{1 + \frac{8}{\pi}\frac{C_T}{J^2}}}\text{ [-]}$.
   - Discrepancia residual tabular: $\Delta \eta = \eta_{reg} - \eta_{calc}$.
   - Cota de propagación de redondeo ASCII: $\epsilon_{cota} = \eta_{calc} \cdot \left( \frac{\epsilon}{J} + \frac{\epsilon}{C_T} + \frac{\epsilon}{C_P} \right) + \epsilon$, con $\epsilon = 0.5 \times 10^{-6}$.

---

### 4. Auditoría de Fórmulas y Consistencia Numérica

Se auditaron todas las expresiones analíticas programadas en `procesar_uiuc_prop.py`:

1. **Relación de Avance $J = V / (nD) \implies V = J \cdot n \cdot D$:**
   - Para el punto de referencia solicitado ($J = 0.448667$, $\text{RPM} = 20051.0$, $D = 0.08128\text{ m}$):
     $$V = 0.448667 \times \left(\frac{20051.0}{60.0}\right) \times 0.08128 = 12.18688229...\text{ m/s} \approx 12.19\text{ m/s} \quad (43.8728\text{ km/h})$$
   - El resultado numérico es rigurosamente exacto y coincide con la especificación de referencia.

2. **Escalado Dimensional de Empuje y Potencia:**
   - Factor de empuje: $\rho \cdot n^2 \cdot D^4 = 1.225 \times (334.183333)^2 \times (0.08128)^4 = 5.970834\text{ N}$.
   - Factor de potencia: $\rho \cdot n^3 \cdot D^5 = 1.225 \times (334.183333)^3 \times (0.08128)^5 = 162.179048\text{ W}$.
   - Se verificó el balance idéntico:
     $$\frac{P_{out}}{P} = \frac{T \cdot V}{P} = \frac{C_T \cdot \rho n^2 D^4 \cdot J n D}{C_P \cdot \rho n^3 D^5} = J \cdot \frac{C_T}{C_P} = \eta_{calc}$$

3. **Eficiencia Ideal de Rankine-Froude:**
   - La derivación a partir de la teoría del disco actuador unidimensional:
     $$C_{T,disk} = \frac{T}{\frac{1}{2}\rho V^2 A} = \frac{C_T \rho n^2 D^4}{\frac{1}{2}\rho (J n D)^2 \frac{\pi}{4} D^2} = \frac{8}{\pi} \frac{C_T}{J^2}$$
     $$\eta_{ideal} = \frac{2}{1 + \sqrt{1 + C_{T,disk}}} = \frac{2}{1 + \sqrt{1 + \frac{8}{\pi}\frac{C_T}{J^2}}}$$
   - Se comprobó en los 19 puntos que:
     $$0 < \eta_{calc} < \eta_{ideal} < 1.0$$
   - Las pérdidas $\eta_{ideal} - \eta_{calc}$ (entre $0.05$ y $0.38$) son físicamente coherentes con la alta disipación viscosa y pérdidas en punta de pala de microhélices a números de Reynolds subcríticos ($Re \sim 20.000$).

4. **Metrología: Discrepancia Tabular vs. Error Experimental:**
   - La discrepancia absoluta $|\Delta \eta| = |\eta_{reg} - \eta_{calc}|$ oscila entre $2.73 \times 10^{-8}$ y $1.18 \times 10^{-5}$ ($0.0000\%$ a $0.0023\%$).
   - En el 100% de los 19 puntos se cumple $|\Delta \eta| \le \epsilon_{cota}$.
   - Se valida la conclusión del autor: este residuo proviene exclusivamente de la representación ASCII de 6 dígitos de la base UIUC y es entre 400 y 1000 veces menor que la incertidumbre real de los instrumentos en túnel ($\pm 1\%$ a $\pm 3\%$).

---

### 5. Auditoría de Dominio de Datos y Restricciones Físicas

1. **Dominio Propulsivo Válido ($J > 0$, $C_T > 0$, $C_P > 0$):**
   - El script y las pruebas verifican que las formulaciones de eficiencia sólo son físicamente válidas en el régimen propulsor de avance.
   - En punto fijo ($J = 0$), $\eta = 0$ por definición cinemática (trabajo útil nulo), no reflejando la calidad estática de empuje (para la cual rige la Figura de Mérito $FM$ o empuje específico $T/P$).
   - Para $C_T \le 0$ la hélice entra en régimen molinillo/freno aerodinámico, donde la eficiencia propulsiva pierde significado físico.

2. **Prohibición de Extrapolación a Alta Velocidad ($600\text{ km/h}$):**
   - Rango medido real: $V \in [4.32\text{ km/h}, 43.87\text{ km/h}]$ ($V \in [1.20\text{ m/s}, 12.19\text{ m/s}]$).
   - $600\text{ km/h}$ ($166.67\text{ m/s}$) representa un factor de extrapolación de **$13.68\times$** y un déficit de $556.13\text{ km/h}$.
   - A $600\text{ km/h}$, el coeficiente de avance hipotético sería $J \approx 6.14$, situándose muy por encima del límite de empuje nulo ($J_{C_T=0} \approx 0.55 - 0.60$).
   - Consecuencias físicas que invalidan cualquier extrapolación:
     1. Régimen de molinillo con frenado aerodinámico masivo ($C_T \ll 0$).
     2. Efectos severos de compresibilidad en punta de pala ($M_{punta} \approx 0.55$ frente a $M < 0.05$ ensayado), provocando desprendimiento de capa límite y ondas de choque locales sobre una micro-pala arqueada.
     3. Presión dinámica $180\times$ superior ($17.014\text{ Pa}$ frente a $91\text{ Pa}$), con destrucción aeroelástica inmediata de la pala por flexo-torsión y divergencia.

3. **Prohibición de Asimilación al "Ventilador C02":**
   - La Micro Invent 3.2x2.2 es una hélice libre abierta de 2 palas con solidez baja ($\sigma \ll 0.1$).
   - Un ventilador de máquina opera entubado (*ducted fan*), con tolerancia mínima en la punta del álabe (*tip clearance*), alta solidez ($\sigma > 0.6$), múltiples álabes y eventual difusión de presión en tobera o interacción con estatores.
   - No mide ni representa $CO_2$: el ensayo se ejecutó en aire ambiental ($\rho \approx 1.225\text{ kg/m}^3, a \approx 340\text{ m/s}, \gamma = 1.40$). El dióxido de carbono posee propiedades termodinámicas marcadamente distintas ($\rho \approx 1.84\text{ kg/m}^3, a \approx 268\text{ m/s}, \gamma \approx 1.28$).
   - Por tanto, se valida que el paquete auditado rechaza formalmente clasificar esta hélice como prueba o modelo del ventilador C02.

---

### 6. Auditoría de Rutas y Estructura

1. **Rutas en Código Python:**
   - Tanto `procesar_uiuc_prop.py` como `test_procesar_uiuc_prop.py` utilizan resolución autónoma mediante `Path(__file__).resolve().parent`.
   - Esto permite que el paquete sea autocontenido y se ejecute sin fallar indistintamente si el comando se invoca desde la raíz del proyecto o desde el interior de la carpeta donde yacen los scripts.
2. **Defecto de Enlaces Absolutos en Documentación:**
   - En `informe_tecnico_uiuc_avance.md`, líneas 267-272, los enlaces markdown apuntan a un directorio temporal foráneo y caduco (`file:///private/tmp/aero_20261108T040057Z_075131ca_9_f47he_/...`). Este defecto rompe la navegabilidad de la documentación fuera de esa sesión original.
3. **Ausencia de `README.md`:**
   - El paquete carece de un archivo `README.md` estándar en su raíz que explique cómo usar el paquete, las dependencias y la secuencia de ejecución de scripts y tests.

---

### 7. Matriz de Defectos y Hallazgos

| ID | Componente Afectado | Severidad | Descripción del Defecto | Impacto | Recomendación / Solución |
|:---:|:---|:---:|:---|:---|:---|
| **DEF-01** | Raíz del paquete | **Media** | Ausencia de archivo `README.md` de uso e instalación. | Dificulta la inducción de nuevos usuarios e integración en pipelines automatizados. | **Subsanado:** Se generó `salidas/README.md` y `salidas/prueba/README.md`. |
| **DEF-02** | `informe_tecnico_uiuc_avance.md` (L267-272) | **Media** | Hipervínculos markdown contienen rutas absolutas obsoletas de una sesión temporal anterior (`/private/tmp/aero_..._9_f47he_/...`). | Enlaces rotos si se abren desde un visor markdown fuera de la máquina original. | Reemplazar las rutas absolutas por rutas relativas al repositorio o basenames. |
| **DEF-03** | `procesar_uiuc_prop.py` (L18-19) / `test_procesar_uiuc_prop.py` (L46) | **Baja** | Inconsistencia textual entre docstrings (`salidas/datos/...`) y código real (`datos/` relativo a `__file__`). | Confusión menor en desarrolladores al leer la cabecera. | Actualizar la documentación interna para aclarar que `datos/` es un subdirectorio hermano de `__file__`. |
| **DEF-04** | `test_procesar_uiuc_prop.py` / `procesar_uiuc_prop.py` | **Baja** | El archivo `mi_3.2x2.2_geom.txt` está presente en `datos/`, pero ningún script lo procesa ni ningún test valida su presencia. | Archivo entregable huérfano sin verificación automatizada en la suite de pruebas. | Añadir prueba unitaria `test_geometry_file_integrity` que valide los 18 radios tabulados de $r/R, c/R, \beta$. |
| **DEF-05** | `procesar_uiuc_prop.py` (`main()`) | **Baja** | No admite parámetros por línea de comandos (`sys.argv` / `argparse`). Parámetros ($D, \rho, \text{RPM}$) fijos en código. | Rigidez para reprocesar otras corridas de la base UIUC sin editar código. | Incorporar `argparse` con banderas opcionales `--input`, `--output`, `--rpm`, `--diameter`. |
| **DEF-06** | `test_procesar_uiuc_prop.py` (L74) | **Informativa** | En `test_02`, se compara `v_ref` contra $12.186884$ en vez del valor de doble precisión exacta $12.186882\text{ m/s}$ ($V = 0.448667 \times \frac{20051}{60} \times 0.08128$). | Pasa la prueba con `places=5`, pero introduce un desfase de $1.7 \times 10^{-6}\text{ m/s}$ por redondeo manual intermedio. | Ajustar la constante de prueba al valor exacto de coma flotante. |

---

### 8. Pruebas Realizadas en Réplica Aislada (`salidas/prueba/`)

Se clonó el paquete completo hacia `salidas/prueba/` utilizando `shutil.copyfile` para garantizar permisos de lectura/escritura (`rw-r--r--`). Se ejecutaron las siguientes validaciones:

1. **Ejecución de Suite de Pruebas Unitarias (`test_procesar_uiuc_prop.py`):**
   - Comando desde la raíz: `python3 salidas/prueba/test_procesar_uiuc_prop.py`
   - Comando dentro de la carpeta: `cd salidas/prueba && python3 test_procesar_uiuc_prop.py`
   - Resultado: **11/11 tests superados exitosamente (`OK`) en 0.001s**.
2. **Ejecución del Procesador Aerodinámico (`procesar_uiuc_prop.py`):**
   - Comando: `python3 salidas/prueba/procesar_uiuc_prop.py`
   - Generación del archivo CSV: `salidas/prueba/uiuc_mi_3.2x2.2_20051_procesado.csv`
   - Validación cruzada criptográfica SHA-256: Coincidencia 100% idéntica (`c4ea07cc12d12303f32e0237c1fceae3239890218c2890c7f9cfcc9bb808cf88`).
3. **Verificación de Fórmulas y Columnas del CSV:**
   - 19 filas de datos numéricos validadas una a una contra cálculos analíticos independientes.
   - Máximo error relativo de fórmulas: $0.00\%$.
4. **Validación de la Tabla Markdown en Informe Técnico:**
   - Los 19 puntos tabulados en el informe coinciden con los valores del CSV exportado.

---

### 9. Limitaciones Metodológicas y de Alcance

1. **Validez Estrictamente Acotada al Dominio Medido:**
   - Los datos solo son válidos para $J \in [0.044195, 0.448667]$ ($V \in [4.32, 43.87]\text{ km/h}$) a una rotación nominal de $20.051\text{ rpm}$.
2. **Efectos de Escala de Microhélice:**
   - Los números de Reynolds del ensayo ($Re_c \sim 15.000 - 30.000$) corresponden al régimen laminar con separación subcrítica propio de micro-drones. No es aplicable a hélices de aviación general sin correcciones de escala.
3. **No Extrapolable a Turbomaquinaria ni Ventiladores:**
   - No es admisible transferir estos datos a ductos o ventiladores axiales/centrífugos.
4. **Condiciones Ambientales Asumidas:**
   - Los valores dimensionales ($T, P$) dependen del supuesto $\rho = 1.225\text{ kg/m}^3$ y $n = 334.1833\text{ rev/s}$. Variaciones en temperatura, presión atmosférica o dispersión de tacómetro requieren recalcular los coeficientes dimensionales.
