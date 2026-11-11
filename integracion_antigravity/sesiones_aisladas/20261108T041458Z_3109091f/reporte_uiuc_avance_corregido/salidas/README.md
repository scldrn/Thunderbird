# Procesamiento de Datos Aerodinámicos UIUC (Hélice mi_3.2x2.2)

Paquete autónomo y reproducible para el procesamiento del ensayo de la hélice `mi_3.2x2.2` a 20051 rpm nominales.

- **Fuente oficial:** UIUC Propeller Data Site (Volume 2), https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html
- **Archivo de ensayo:** `salidas/datos/mi_3.2x2.2_0544rd_20051.txt`
- **Archivo geométrico:** `salidas/datos/mi_3.2x2.2_geom.txt`

## 1. Clasificación de Variables

- **Datos Medidos (adimensionales, túnel UIUC):**
  - Coeficiente de avance: $J = V / (n D) \in [0.044195, 0.448667]$ (19 puntos).
  - Coeficiente de empuje: $C_T \in [0.041281, 0.124104]$.
  - Coeficiente de potencia: $C_P \in [0.035779, 0.058227]$.
  - Eficiencia en tabla: $\eta_{reg} \in [0.094195, 0.562131]$.
  - Frecuencia rotacional nominal: $20051\text{ rpm}$ ($n = 334.1833\text{ rev/s}$).

- **Supuestos de Ingeniería Adoptados:**
  - Diámetro: $D = 0.08128\text{ m}$ (3.2 in).
  - Densidad del aire supuesta para dimensionalizar: $\rho = 1.225\text{ kg/m}^3$.
  - Configuración: hélice abierta libre sin ducto en flujo incompresible.

- **Magnitudes Dimensionalizadas y Cálculos:**
  - Velocidad de avance: $V = J \cdot n \cdot D$ ($V \in [1.20, 12.19]\text{ m/s}$ o $[4.32, 43.87]\text{ km/h}$).
  - Empuje: $T = C_T \cdot \rho \cdot n^2 \cdot D^4$ ($T \in [0.2465, 0.7410]\text{ N}$).
  - Potencia de eje: $P = C_P \cdot \rho \cdot n^3 \cdot D^5$ ($P \in [5.80, 9.44]\text{ W}$).
  - Eficiencia calculada: $\eta_{calc} = J \cdot C_T / C_P$.
  - Eficiencia ideal de Froude: $\eta_{ideal} = 2 / (1 + \sqrt{1 + \frac{8}{\pi} \frac{C_T}{J^2}})$.

## 2. Verificación de Referencia y Dominio de Validez

- Para $20051\text{ rpm}$, $D = 0.08128\text{ m}$ y $J_{max} = 0.448667$:
  $$V = 0.448667 \times \left(\frac{20051}{60}\right) \times 0.08128 = 12.1869\text{ m/s} \approx 12.19\text{ m/s} \quad (43.87\text{ km/h})$$
- **No extrapolación a 600 km/h:** No se extrapola a $600\text{ km/h}$ debido a que los datos experimentales no cubren ese dominio operativo ($V \le 12.19\text{ m/s}$), no porque se haya demostrado falla física o rotura.
- **No transferencia a C02 entubado:** Los datos caracterizan una hélice abierta libre en aire; no deben transferirse a ventiladores entubados ni a flujo de CO2 en conductos.
- **Metrología:** Las discrepancias entre $\eta_{reg}$ y $\eta_{calc}$ son $\sim 10^{-5}$ ($< 0.0023\%$), producto exclusivo del formato de 6 decimales. Se descartan porcentajes de incertidumbre instrumental inventados en textos previos.

## 3. Reproducción Autónoma

Comandos ejecutables localmente sin conexión a red:

```bash
# Procesamiento y generación de tabla CSV
python3 salidas/procesar_uiuc_prop.py

# Suite de pruebas unitarias
python3 salidas/test_procesar_uiuc_prop.py
```

## 4. Archivos en `salidas/`

- `salidas/datos/`: Copias locales de los archivos fuente UIUC.
- `salidas/procesar_uiuc_prop.py`: Script de cálculo dimensional y validación.
- `salidas/test_procesar_uiuc_prop.py`: Suite de 11 pruebas unitarias.
- `salidas/uiuc_mi_3.2x2.2_20051_procesado.csv`: Resultados tabulados.
- `salidas/README.md`: Este resumen del paquete.
- `salidas/INFORME.md`: Informe técnico del ensayo.
