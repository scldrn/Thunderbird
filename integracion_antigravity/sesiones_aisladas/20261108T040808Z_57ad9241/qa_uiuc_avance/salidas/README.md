# Paquete Autónomo de Procesamiento Aerodinámico UIUC
## Hélice Abierta Micro Invent 3.2x2.2 @ 20.051 RPM (Corrida UIUC 0544rd_20051)

Este paquete contiene la implementación autónoma, reproducible y verificada para el procesamiento analítico y metrológico de los datos de ensayo en túnel de viento de la hélice de microescala **Micro Invent 3.2x2.2** ensayada a una velocidad angular nominal de **20.051 RPM** en el túnel de viento de la Universidad de Illinois en Urbana-Champaign (UIUC).

---

### 1. Fuente Oficial y Créditos

- **Base de Datos:** UIUC Propeller Data Site (Volume 2)
- **Institución:** Applied Aerodynamics Group, Department of Aerospace Engineering, University of Illinois at Urbana-Champaign.
- **Investigadores:** Michael S. Selig, Robert W. Deters, Gavin K. Ananda et al.
- **URL Oficial:** [UIUC Propeller Data Site - Volume 2](https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html)
- **Archivo Fuente:** `mi_3.2x2.2_0544rd_20051.txt` (corrida de túnel 0544rd)
- **Geometría de Pala:** `mi_3.2x2.2_geom.txt` (distribución de cuerda y ángulo de paso)

---

### 2. Estructura del Paquete

```text
.
├── README.md                           <- Guía de uso, especificaciones y ejecución (este archivo)
├── informe_tecnico_uiuc_avance.md      <- Informe técnico integral con metodología y matrices
├── procesar_uiuc_prop.py               <- Script ejecutable de procesamiento aerodinámico y exportación
├── test_procesar_uiuc_prop.py          <- Suite de 11 pruebas unitarias y de restricciones físicas
├── uiuc_mi_3.2x2.2_20051_procesado.csv <- Tabla estructurada con datos medidos, supuestos y cálculos
└── datos/                              <- Datos brutos originales del túnel UIUC
    ├── mi_3.2x2.2_0544rd_20051.txt     <- Corrida de ensayo (J, CT, CP, eta) a 20.051 RPM
    └── mi_3.2x2.2_geom.txt             <- Distribución radial de cuerda c/R y ángulo beta
```

---

### 3. Requisitos del Sistema

- **Python:** Versión 3.8 o superior.
- **Dependencias:** Solo utiliza la biblioteca estándar de Python (`math`, `csv`, `pathlib`, `unittest`, `typing`, `sys`). **No requiere dependencias externas ni conexión a red**.

---

### 4. Instrucciones de Uso y Ejecución

Todos los scripts resuelven sus rutas relativas de forma autónoma con respecto a su ubicación (`__file__`). Pueden ejecutarse tanto desde el directorio que contiene los scripts como desde cualquier directorio superior:

#### 4.1. Ejecutar el Procesador Aerodinámico
Calcula las transformaciones dimensionales, comprueba las cotas de redondeo y regenera el archivo CSV:

```bash
# Desde la carpeta donde se encuentra procesar_uiuc_prop.py:
python3 procesar_uiuc_prop.py

# O desde el directorio raíz del proyecto:
python3 salidas/procesar_uiuc_prop.py
```

Salida esperada por consola:
- Verificación del punto de referencia ($J = 0.448667 \implies V \approx 12.19\text{ m/s}$).
- Resumen de variables medidas, supuestas y calculadas.
- Verificación de cotas de redondeo ($|\Delta \eta| \le \text{cota\_redondeo}$).
- Bloqueo y advertencias sobre extrapolación y compatibilidad.
- Generación de `uiuc_mi_3.2x2.2_20051_procesado.csv`.

#### 4.2. Ejecutar la Suite de Pruebas Automatizadas
Ejecuta las 11 pruebas unitarias y de validación de restricciones físicas:

```bash
# Ejecución estándar:
python3 test_procesar_uiuc_prop.py

# O con detalle verbose mediante unittest:
python3 -m unittest test_procesar_uiuc_prop.py -v
```

Resultado esperado:
```text
Ran 11 tests in 0.001s
OK
```

---

### 5. Clasificación de Variables

El paquete aplica una distinción rigurosa de las magnitudes:

1. **Datos Medidos / Registrados (UIUC):**
   - $J$: Coeficiente de avance adimensional ($0.044195$ a $0.448667$, 19 puntos).
   - $C_T$: Coeficiente de empuje aerodinámico ($0.041281$ a $0.124104$).
   - $C_P$: Coeficiente de potencia de eje ($0.035779$ a $0.058227$).
   - $\eta_{reg}$: Eficiencia propulsiva registrada en el banco ($0.094195$ a $0.562131$).
   - $\text{RPM}_{nominal}$: $20.051\text{ rpm}$.

2. **Supuestos de Ingeniería Adoptados:**
   - Diámetro del rotor: $D = 0.08128\text{ m}$ ($3.2\text{ pulgadas}$ exactas).
   - Densidad del aire estándar: $\rho = 1.225\text{ kg/m}^3$ (ISA nivel del mar, $15^\circ\text{C}$).
   - Frecuencia rotacional: $n = \text{RPM} / 60 = 334.1833\text{ rev/s}$.
   - Aceleración de la gravedad: $g = 9.80665\text{ m/s}^2$.
   - Geometría: Hélice abierta de 2 palas sin ducto en flujo incompresible libre.

3. **Cálculos Analíticos Derivados:**
   - Velocidad de avance: $V = J \cdot n \cdot D\text{ [m/s]}$, $V_{km/h} = V \cdot 3.6\text{ [km/h]}$.
   - Empuje aerodinámico: $T = C_T \cdot \rho \cdot n^2 \cdot D^4\text{ [N]}$, $T_{gf} = (T / g) \times 1000\text{ [gf]}$.
   - Potencia de eje: $P = C_P \cdot \rho \cdot n^3 \cdot D^5\text{ [W]}$.
   - Potencia útil de tracción: $P_{out} = T \cdot V\text{ [W]}$.
   - Eficiencia propulsiva: $\eta_{calc} = J \cdot C_T / C_P\text{ [-]}$.
   - Eficiencia ideal de Froude: $\eta_{ideal} = \frac{2}{1 + \sqrt{1 + \frac{8}{\pi}\frac{C_T}{J^2}}}\text{ [-]}$.
   - Residuo de redondeo: $\Delta \eta = \eta_{reg} - \eta_{calc}\text{ [-]}$.

---

### 6. Restricciones Físicas y Advertencias de Dominio

> [!WARNING]
> **Prohibición de Extrapolación a Alta Velocidad (p. ej. 600 km/h):**  
> El rango máximo ensayado es de $V = 12.19\text{ m/s}$ ($43.87\text{ km/h}$). Extrapolar hacia $600\text{ km/h}$ ($166.67\text{ m/s}$) exige un avance $J \approx 6.14$, donde la hélice opera en régimen de **molinillo severo / freno aerodinámico** ($C_T \ll 0$), con Mach en punta de pala $M \approx 0.55$ (aparición de ondas de choque locales y pérdidas por compresibilidad) y presiones dinámicas que provocarían **divergencia aeroelástica y rotura estructural**.

> [!CAUTION]
> **Prohibición de Asimilación al "Ventilador C02":**  
> Este conjunto de datos pertenece exclusivamente a una **hélice abierta libre de dos palas** operada en **aire atmosférico**. No puede utilizarse como modelo o medición de un ventilador entubado (*ducted fan*) ni para fluidos gaseosos como dióxido de carbono ($CO_2$, cuyas propiedades de densidad, velocidad del sonido y compresibilidad son termodinámicamente incompatibles).
