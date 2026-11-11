# Manifiesto Reproducible de Trazabilidad de Fuentes: Tablas UIUC y Nota NASA EDF

Este documento constituye el manifiesto técnico y reproducible de procedencia, integridad criptográfica y límites de aplicabilidad para las tres tablas públicas de la base de datos de hélices de la Universidad de Illinois en Urbana-Champaign (UIUC Propeller Database) y la nota técnica derivada sobre el ventilador eléctrico ensayado por NASA para el concepto SUSAN.

---

## 1. Tabla Consolidada de Integridad y Procedencia

| Archivo | Tamaño (bytes) | SHA-256 | Naturaleza | ¿Fuente Primaria? | URL Primaria |
| :--- | :---: | :--- | :--- | :---: | :--- |
| `mi_3.2x2.2_geom.txt` | 416 | `a709e55616905f8e626f4d83fa05d97f2e316e684afa418de972c38301ec3b61` | Medición geométrica tabulada | **Sí** | [UIUC Propeller Database](https://m-selig.ae.illinois.edu/props/propDB.html) |
| `mi_3.2x2.2_static_0519rd.txt` | 583 | `bfba6a17672b48b81d3fb1268c6d2156dda8070d1fb08d6a265241a82fa3a184` | Experimental directa (ensayo estático a punto fijo) | **Sí** | [UIUC Propeller Database](https://m-selig.ae.illinois.edu/props/propDB.html) |
| `mi_3.2x2.2_0544rd_20051.txt` | 795 | `6f3b8d49f0a4595059ea44befe8d946a6044c2a7b97e5eeeeab9051d02e22300` | Experimental directa (ensayo dinámico en túnel de viento) | **Sí** | [UIUC Propeller Database](https://m-selig.ae.illinois.edu/props/propDB.html) |
| `NOTA-NASA-EDF.md` | 1699 | `6da4e76950f8fc94aec9e17216fde93f2749c0e0a224ec1398394b3b96b35643` | Resumen derivado (nota secundaria interna) | **No** (Deriva de Weinstein et al., 2024) | [NASA NTRS 20230017299](https://ntrs.nasa.gov/api/citations/20230017299/downloads/Weinstein_SciTech2024_Final.pdf?attachment=true) |

---

## 2. Fichas Técnicas Detalladas por Fuente

### 2.1. Tabla Geométrica: `mi_3.2x2.2_geom.txt`

* **Ruta de referencia**: `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_geom.txt`
* **Tamaño**: 416 bytes (19 líneas, formato de terminación CRLF `\r\n`).
* **SHA-256**: `a709e55616905f8e626f4d83fa05d97f2e316e684afa418de972c38301ec3b61`
* **Naturaleza**: Medición geométrica tabulada (definición dimensional discreta de la geometría de pala).
* **Condición de fuente primaria**: **Sí**, es la fuente primaria pública distribuida por el repositorio de UIUC para la geometría adimensional de dicha pala.
* **URL Primaria**:
  * Portal oficial: `https://m-selig.ae.illinois.edu/props/propDB.html`
  * Recurso directo en repositorio: `https://m-selig.ae.illinois.edu/props/volume-3/data/mi_3.2x2.2_geom.txt`
* **Licencia**: No declarada en el archivo de datos (distribución de acceso abierto para fines académicos e investigación del UIUC Applied Aerodynamics Group).
* **Fecha de descarga**: No registrada en los archivos de entrada.
* **Límites de Transferencia**:
  1. *Adimensionalidad estricta*: Contiene únicamente relaciones relativas $r/R$, $c/R$ y ángulo geométrico $\beta$ [grados]. No define el diámetro absoluto en el cuerpo de la tabla (solo en la nomenclatura nominal 3.2" x 2.2").
  2. *Incompletitud aerodinámica para reconstrucción cerrada*: No contiene las coordenadas de perfil alar (airfoil coordinates) de cada estación radial ni el espesor máximo relativo ($t/c$). La reconstrucción tridimensional aerodinámica requiere supuestos adicionales no provistos en la tabla.
  3. *No transferibilidad a arquitecturas entubadas*: Inaplicable a geometrías con ducto o ventiladores entubados (como Jetfan 130 Pro o módulo D82).
  4. *Ausencia de propiedades mecánicas*: No contiene masa, centro de gravedad, distribución de inercia, módulo de elasticidad ni límites estructurales de deformación aeroelástica.
* **Distinción Metodológica y Unidades**:
  * **Datos medidos / tabulados**: $r/R$ (radio fraccionario), $c/R$ (cuerda normalizada al radio $R$), $\beta$ (ángulo de torsión local).
  * **Datos calculados**: Cocientes adimensionalizados $r/R$ y $c/R$.
  * **Supuestos**: Rigidez estructural y simetría nominal idéntica en todas las palas de la hélice.
  * **Unidades**:
    * $r/R$: Adimensional $[-]$ (rango: $0,15$ a $1,00$).
    * $c/R$: Adimensional $[-]$ (rango: $0,0021$ a $0,1977$).
    * $\beta$: Grados $[^\circ]$ (rango: $9,004^\circ$ a $25,417^\circ$).
* **Mediciones ausentes**: Coordenadas de perfiles aerodinámicos (airfoils), espesor relativo de perfil ($t/c$), masa total de la pala, material y módulo elástico, e incertidumbre geométrica de fabricación o medición.

---

### 2.2. Tabla de Ensayo Estático: `mi_3.2x2.2_static_0519rd.txt`

* **Ruta de referencia**: `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_static_0519rd.txt`
* **Tamaño**: 583 bytes (19 líneas, formato CRLF `\r\n`).
* **SHA-256**: `bfba6a17672b48b81d3fb1268c6d2156dda8070d1fb08d6a265241a82fa3a184`
* **Naturaleza**: Experimental directa (ensayo estático a punto fijo en banco / túnel con velocidad de avance nula).
* **Condición de fuente primaria**: **Sí**, es la tabla original de datos brutos procesados del ensayo estático de UIUC Propeller Database.
* **URL Primaria**:
  * Portal oficial: `https://m-selig.ae.illinois.edu/props/propDB.html`
  * Recurso directo en repositorio: `https://m-selig.ae.illinois.edu/props/volume-3/data/mi_3.2x2.2_static_0519rd.txt`
* **Licencia**: No declarada en el archivo de datos.
* **Fecha de descarga**: No registrada en los archivos de entrada.
* **Límites de Transferencia**:
  1. *Confinamiento al régimen estático*: Válido exclusivamente para velocidad de avance libre nula ($V_\infty = 0, J = 0$). No transferible a condiciones de vuelo con avance ($J > 0$).
  2. *Rendimiento propulsivo ausente*: A punto fijo, la eficiencia propulsiva clásica es $\eta = 0$ ($J = 0$), por lo que no se provee ni transfiere rendimiento propulsivo.
  3. *Acotación de rotación*: Datos medidos entre $2.950,000$ y $19.923,333\text{ RPM}$. No se debe extrapolar a regímenes fuera de este intervalo (donde varían fuertemente el número de Reynolds y los efectos de compresibilidad marginal).
  4. *No transferible a EDF ni a otras unidades*: No aplicable al Jetfan 130 Pro, ni al módulo D82, ni al motor C02.
* **Distinción Metodológica y Unidades**:
  * **Datos medidos**: Velocidad angular de rotación de la hélice en revoluciones por minuto ($\text{RPM}$); empuje $T$ y par $Q$ o potencia $P$ medidos en el banco.
  * **Datos calculados**:
    * $C_T = \frac{T}{\rho n^2 D^4}$ (coeficiente de empuje estático).
    * $C_P = \frac{P}{\rho n^3 D^5}$ (coeficiente de potencia estático).
  * **Supuestos**: Flujo estacionario incompresible libre de perturbaciones o recirculación de paredes del recinto; densidad atmosférica local estimada por el operador durante el ensayo.
  * **Unidades**:
    * $\text{RPM}$: Revoluciones por minuto $[\text{rev/min}]$ (rango: $2.950,000$ a $19.923,333$).
    * $C_T$: Adimensional $[-]$ (rango: $0,103654$ a $0,125828$).
    * $C_P$: Adimensional $[-]$ (rango: $0,051360$ a $0,059879$).
* **Mediciones ausentes**: Valores dimensionales directos de empuje $[N\text{ o lbf}]$, par $[N\cdot m]$ o potencia eléctrica $[W]$, densidad atmosférica $\rho$ del ensayo, temperatura y presión barométrica en el túnel, e incertidumbre instrumental individualizada.

---

### 2.3. Tabla de Ensayo Dinámico: `mi_3.2x2.2_0544rd_20051.txt`

* **Ruta de referencia**: `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/mi_3.2x2.2_0544rd_20051.txt`
* **Tamaño**: 795 bytes (20 líneas, formato CRLF `\r\n`).
* **SHA-256**: `6f3b8d49f0a4595059ea44befe8d946a6044c2a7b97e5eeeeab9051d02e22300`
* **Naturaleza**: Experimental directa (ensayo dinámico en túnel de viento con corriente incidente a RPM nominal fija).
* **Condición de fuente primaria**: **Sí**, es la tabla original de datos de túnel de UIUC Propeller Database.
* **URL Primaria**:
  * Portal oficial: `https://m-selig.ae.illinois.edu/props/propDB.html`
  * Recurso directo en repositorio: `https://m-selig.ae.illinois.edu/props/volume-3/data/mi_3.2x2.2_0544rd_20051.txt`
* **Licencia**: No declarada en el archivo de datos.
* **Fecha de descarga**: No registrada en los archivos de entrada.
* **Límites de Transferencia**:
  1. *Condición nominal de giro*: El ensayo se realizó a una rotación nominal fija próxima a $20.051\text{ RPM}$ (indicada en el nombre del archivo). A velocidades de rotación sustancialmente menores, las curvas de $C_T$, $C_P$ y $\eta$ se degradan sensiblemente debido a la caída del número de Reynolds.
  2. *Intervalo de avance acotado*: Datos tabulados estrictamente para $J \in [0,044195, 0,448667]$. Fuera de este rango (estático $J \to 0$ o avance alto / molinete $J > 0,45$) no existen datos medidos y no debe extrapolarse directamente.
  3. *Incompatibilidad con ventiladores entubados (EDF)*: Los coeficientes y eficiencias de una microhélice libre no son transferibles a ventiladores con conducto difusor (como Jetfan 130 Pro o D82).
  4. *Incompatibilidad con sistemas motrices ajenos*: No se transfiere a plantas motrices distintas (como motor C02).
* **Distinción Metodológica y Unidades**:
  * **Datos medidos**: Velocidad lineal de corriente libre en túnel $V_\infty$, frecuencia de rotación de eje $n$, empuje axial $T$, y par aerodinámico $Q$ registrados por la balanza aerodinámica.
  * **Datos calculados**:
    * $J = \frac{V_\infty}{n D}$ (coeficiente de avance).
    * $C_T = \frac{T}{\rho n^2 D^4}$ (coeficiente de empuje).
    * $C_P = \frac{P}{\rho n^3 D^5}$ (coeficiente de potencia).
    * $\eta = J \frac{C_T}{C_P}$ (eficiencia propulsiva).
  * **Supuestos**: Flujo uniforme libre de turbulencia excesiva; correcciones convencionales de bloqueo en túnel de viento aplicadas por UIUC.
  * **Unidades**:
    * $J$: Adimensional $[-]$ (rango: $0,044195$ a $0,448667$).
    * $C_T$: Adimensional $[-]$ (rango: $0,041281$ a $0,124104$).
    * $C_P$: Adimensional $[-]$ (rango: $0,035779$ a $0,058227$).
    * $\eta$: Adimensional $[-]$ (rango: $0,094195$ a $0,562131$, con pico de rendimiento de $0,562$ en $J \approx 0,381$).
* **Mediciones ausentes**: Velocidad dimensional directa de flujo $V_\infty$ $[m/s\text{ o ft/s}]$, valor exacto de RPM instantáneas para cada línea (solo se registra el nominal ~20.051 RPM en el título), parámetros termodinámicos ambientales del túnel (presión barométrica, temperatura, humedad y densidad $\rho$), e incertidumbre experimental tabulada.

---

### 2.4. Nota Técnica Secundaria: `NOTA-NASA-EDF.md`

* **Ruta de referencia**: `entradas/investigacion-aeronautica/fuentes/uiuc_propdb/NOTA-NASA-EDF.md`
* **Tamaño**: 1699 bytes (28 líneas, formato LF `\n`).
* **SHA-256**: `6da4e76950f8fc94aec9e17216fde93f2749c0e0a224ec1398394b3b96b35643`
* **Naturaleza**: **Resumen derivado** (documento técnico secundario interno recopilado a partir del informe primario de NASA/AIAA).
* **Condición de fuente primaria**: **NO ES FUENTE PRIMARIA**.
  * La fuente primaria real es: **Weinstein y colaboradores, NASA/AIAA, 2024, NTRS 20230017299** (*"Wind Tunnel Performance and Dynamic Characterization of a Small Electric Ducted Fan for SUSAN Subscale Concept"*).
  * Enlace al documento primario NTRS: [Weinstein_SciTech2024_Final.pdf](https://ntrs.nasa.gov/api/citations/20230017299/downloads/Weinstein_SciTech2024_Final.pdf?attachment=true)
  * Registro bibliográfico NTRS: [Citations 20230017299](https://ntrs.nasa.gov/citations/20230017299)
  * Menciona que el PDF original se conserva bajo la denominación `NASA_EDF_20230017299.pdf`.
* **Licencia**: No declarada en el archivo markdown de entrada (el informe público de la NASA es una obra del Gobierno Federal de los Estados Unidos sin derechos de autor comerciales, pero el archivo resumen local no declara formalmente una licencia SPDX).
* **Fecha de descarga**: No registrada en los archivos de entrada.
* **Límites de Transferencia Explícitos**:
  1. *Disparidad con módulo D82*: El rotor ensayado es un Jetfan 130 Pro (10 palas de 5,11 pulgadas de diámetro, 7 álabes fijos y conducto exterior de 5,23 pulgadas). Es físicamente más grande y distinto al módulo candidato D82; **no se transfiere la curva de empuje, la eficiencia, la masa ni la respuesta dinámica de esta unidad al vehículo ni a D82**.
  2. *Disparidad con motor C02*: El motor ensayado (1.100 g de masa, 56 mm de diámetro y 7 kW de potencia continua nominal) **NO es el motor C02**. Su masa, geometría y límites térmicos no son transferibles al motor C02.
  3. *No simultaneidad de extremos*: Los rangos de la Tabla 6 (velocidad 2.875–25.150 rpm, empuje estático 0–21,25 lbf, potencia 190–6.420 W) describen la envolvente de todas las pruebas y **no se asumen medidos en un mismo punto de operación**.
  4. *Potencia eléctrica CC*: La potencia del modelo de la sección G corresponde a potencia eléctrica continua suministrada al conjunto en ensayos de incidencia (0° a 30°) y presión dinámica (0 a 6 psf).
  5. *Intransferibilidad de la dinámica de control*: La respuesta de segundo orden ajustada en la sección VI.D depende de la rampa del controlador y del escalón del ensayo específico; **la configuración y sus tiempos de respuesta no se transfieren a C02**.
  6. *Requerimiento de consulta al original*: Para cualquier cifra adicional, modelado o análisis paramétrico, se requiere consultar obligatoriamente el PDF primario (`NASA_EDF_20230017299.pdf`), sus tablas y gráficas originales.
* **Distinción Metodológica y Unidades**:
  * **Datos medidos / tabulados en el informe**:
    * Diámetro de pala del Jetfan 130 Pro: 5,11 pulgadas.
    * Diámetro exterior del conducto: 5,23 pulgadas.
    * Masa del motor ensayado: 1.100 gramos.
    * Diámetro del motor: 56 milímetros.
    * Potencia continua máxima nominal del motor: 7 kilovatios.
    * Rango de velocidad de giro del ventilador: 2.875 a 25.150 rpm.
    * Rango de empuje estático: 0 a 21,25 lbf.
    * Rango de potencia eléctrica CC: 190 a 6.420 W.
    * Rango de incidencia angular: 0° a 30°.
    * Rango de presión dinámica: 0 a 6 psf.
  * **Datos calculados**: Modelo paramétrico de respuesta de segundo orden ajustado numéricamente a la velocidad del motor (Sección VI.D del informe).
  * **Supuestos**: Los valores extremos de la Tabla 6 representan los límites del espacio de prueba, no una condición simultánea acoplada; el motor y rotor ensayados no son equivalentes a C02 ni D82.
  * **Unidades Conservadas**:
    * Diámetro de pala y conducto: Pulgadas $[\text{in}]$.
    * Masa del motor: Gramos $[g]$.
    * Diámetro exterior de motor: Milímetros $[mm]$.
    * Potencia nominal continua: Kilovatios $[kW]$.
    * Velocidad de rotación: Revoluciones por minuto $[\text{rpm}]$.
    * Empuje estático: Libras-fuerza $[\text{lbf}]$.
    * Potencia eléctrica suministrada: Vatios $[W]$.
    * Ángulo de incidencia: Grados $[^\circ]$.
    * Presión dinámica: Libras por pie cuadrado $[\text{psf}]$.
* **Mediciones ausentes**: Tabulación punto por punto de puntos de operación simultáneos (empuje, potencia y RPM concurrentes); mediciones térmicas de devanado de motor; caracterización y mediciones del motor C02 (totalmente ausente); mediciones del módulo D82 (totalmente ausente).
* **Restricciones de Integridad Críticas**:
  * **Existencia de archivos no copiados**: No inferir que el archivo PDF original (`NASA_EDF_20230017299.pdf`) no existe por no encontrarse copiado en `entradas/`. La nota explicita que dicho PDF se conserva en el archivo histórico.
  * **Tratamiento de reservas de masa**: No inferir que una reserva sin masa asignada tenga masa real nula o no nula.

---

## 3. Scripts de Verificación y Detección de Cambios

Todos los entregables operan exclusivamente dentro del directorio de trabajo y se ubican en `salidas/`:

1. `salidas/manifiesto_fuentes.json`: Manifiesto formal estructurado y reproducible en formato JSON.
2. `salidas/verificar_manifiesto.py`: Script estándar en Python 3 para verificación criptográfica y detección de alteraciones.
3. `salidas/test_verificar_manifiesto.py`: Batería de pruebas unitarias con `unittest` que comprueba la detección infalible de manipulaciones de datos y de violaciones metodológicas.

### 3.1. Ejecución de la Verificación

Para ejecutar la verificación directa sobre los archivos de referencia:

```bash
python3 salidas/verificar_manifiesto.py --verbose
```

**Comportamiento del código de salida**:
* `0`: Verificación exitosa. Todos los archivos coinciden en tamaño, hash SHA-256 y reglas de metadatos.
* `1`: Discrepancia detectada (alteración de contenido o tamaño en algún archivo).
* `2`: Archivo faltante, manifiesto inválido o violación de metadatos (p. ej., categorizar la nota NASA como fuente primaria).

### 3.2. Ejecución de la Batería de Pruebas Automatizadas

Para validar las pruebas de detección de cambios de contenido:

```bash
python3 -m unittest salidas/test_verificar_manifiesto.py -v
```

La suite cubre:
* Verificación prístina de los 4 archivos en `entradas/`.
* Detección de alteración de un solo byte / valor numérico en cada archivo manteniendo tamaño exacto (`DISCREPANCIA_HASH`).
* Detección de alteración de tamaño por truncamiento o adición de líneas (`DISCREPANCIA_TAMANO`).
* Detección de archivos faltantes (`NO_ENCONTRADO`).
* Detección de intentos indebidos de asignar la nota NASA como fuente primaria (`ERROR_METADATOS`).
* Verificación de la no invención de licencias ni fechas de descarga.
* Verificación de la preservación estricta de unidades y de límites de transferencia.
