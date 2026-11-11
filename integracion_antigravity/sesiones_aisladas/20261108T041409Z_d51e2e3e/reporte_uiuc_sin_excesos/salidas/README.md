# Paquete de Análisis Estático UIUC: Hélice Micro Invent 3.2x2.2

Este paquete procesa y verifica los datos aerodinámicos en régimen estático ($V_\infty = 0\text{ m/s}$) de la hélice Micro Invent 3.2x2.2 a partir de los datos experimentales de la Universidad de Illinois en Urbana-Champaign (UIUC).

## Instrucciones de Ejecución

Una vez situados este `README.md` e `INFORME.md` junto a los códigos (`analizar.py`, `test_analizar.py`) y datos (`puntos.csv`, subdirectorio `datos/` con `mi_3.2x2.2_static_0519rd.txt` y `mi_3.2x2.2_geom.txt`), ejecutar:

1. **Procesamiento de datos y exportación de resultados:**
   ```bash
   python3 analizar.py
   ```
2. **Ejecución de las pruebas unitarias y de verificación:**
   ```bash
   python3 test_analizar.py
   ```
   o bien:
   ```bash
   python3 -m unittest test_analizar.py
   ```

## Taxonomía de Parámetros

- **Datos medidos:**
  - Frecuencia de rotación: $\text{RPM} \in [2950.000, 19923.333]\text{ rpm}$.
  - Coeficientes adimensionales en banco UIUC: $C_T \in [0.103654, 0.125828]$, $C_P \in [0.051360, 0.059879]$.
  - Diámetro de la hélice: $D = 0.08128\text{ m}$ ($3.2\text{ in}$).
  - Cuerda relativa en $0.75R$: $(c/R)_{0.75} = 0.1799$.
- **Valores supuestos:**
  - Densidad del aire supuesta: $\rho = 1.225\text{ kg/m}^3$.
  - Velocidad del sonido supuesta: $a = 340.3\text{ m/s}$.
  - Viscosidad cinemática supuesta: $\nu = 1.46 \times 10^{-5}\text{ m}^2/\text{s}$.
  - Condición de ensayo estático: $V_\infty = 0\text{ m/s}$.
- **Cálculos:**
  - Frecuencia de giro: $n = \text{RPM} / 60\text{ [rev/s]}$.
  - Empuje estático: $T = C_T \cdot \rho \cdot n^2 \cdot D^4\text{ [N]}$.
  - Potencia mecánica de eje: $P = C_P \cdot \rho \cdot n^3 \cdot D^5\text{ [W]}$.
  - Mach de punta: $M_{\text{tip}} = (\pi n D) / a$.
  - Reynolds a $0.75R$: $Re_{0.75R} = (0.75 \pi n D \cdot c_{0.75}) / \nu$.
  - Figura de Mérito ideal: $FM = \sqrt{2/\pi} \cdot C_T^{1.5} / C_P$.

## Extremo Medido y Cálculos

En el punto extremo medido de la serie experimental:
- $\text{RPM} = 19923.333\text{ rpm}$
- $C_T = 0.125828$
- $C_P = 0.059879$

Con $D = 0.08128\text{ m}$ y $\rho = 1.225\text{ kg/m}^3$ supuesta, se calculan:
- Empuje estático: $T \approx 0.74177\text{ N}$
- Potencia de eje: $P \approx 9.527\text{ W}$

## Distinciones y Limitaciones

1. **Potencia calculada vs. potencia eléctrica:** La potencia dimensional calculada es potencia mecánica de eje; no está directamente medida ni equivale a la potencia eléctrica.
2. **Incompatibilidad con C02:** Los resultados de esta hélice bipala abierta no validan ni son aplicables al ventilador entubado C02.
3. **Criterio de no extrapolación:** No se debe extrapolar fuera del rango medido ($2950.000$ a $19923.333\text{ rpm}$). El motivo para no extrapolar es únicamente la falta de datos fuera del dominio proporcionado.

## Referencias

- UIUC Propeller Database (Volume 2): https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html
- Deters & Selig (figura 38 geometría): https://m-selig.ae.illinois.edu/pubs/DetersSelig-2008-AIAA-2008-6246-MicroProps.pdf
