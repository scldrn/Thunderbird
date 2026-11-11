# Informe Técnico: Análisis Aerodinámico Estático de la Hélice UIUC (Micro Invent 3.2x2.2)

## 1. Alcance y Contexto Experimental

Este informe resume el análisis aerodinámico en condición estática ($V_\infty = 0\text{ m/s}$) de la hélice abierta bipala Micro Invent 3.2x2.2, a partir de los datos experimentales de la base de datos de hélices de la Universidad de Illinois en Urbana-Champaign (UIUC Propeller Database, Volume 2).

## 2. Taxonomía de Variables y Metodología de Cálculo

Se distinguen explícitamente los datos medidos en banco, las propiedades físicas supuestas y los resultados calculados:

- **Datos medidos:**
  - Frecuencia tacométrica: $\text{RPM} \in [2950.000, 19923.333]\text{ rpm}$.
  - Coeficientes adimensionales de empuje y potencia en banco UIUC: $C_T \in [0.103654, 0.125828]$ y $C_P \in [0.051360, 0.059879]$.
  - Diámetro de la hélice: $D = 0.08128\text{ m}$ ($3.2\text{ in}$).
  - Cuerda normalizada seccional en $r/R = 0.75$: $(c/R)_{0.75} = 0.1799$ ($c_{0.75} = 0.007311\text{ m}$).
- **Valores supuestos:**
  - Densidad del aire estándar supuesta: $\rho = 1.225\text{ kg/m}^3$.
  - Velocidad del sonido supuesta: $a = 340.3\text{ m/s}$.
  - Viscosidad cinemática supuesta: $\nu = 1.46 \times 10^{-5}\text{ m}^2/\text{s}$.
  - Velocidad de avance nula: $V_\infty = 0\text{ m/s}$ (condición estática / *hover*).
- **Formulaciones y cálculos:**
  - Frecuencia rotacional: $n = \text{RPM} / 60\text{ [rev/s]}$.
  - Empuje estático: $T = C_T \cdot \rho \cdot n^2 \cdot D^4\text{ [N]}$.
  - Potencia mecánica de eje: $P = C_P \cdot \rho \cdot n^3 \cdot D^5\text{ [W]}$.
  - Número de Mach en la punta: $M_{\text{tip}} = (\pi n D) / a$.
  - Número de Reynolds a $0.75R$: $Re_{0.75R} = (0.75 \pi n D \cdot c_{0.75}) / \nu$.
  - Figura de Mérito ideal: $FM = \sqrt{2/\pi} \cdot C_T^{1.5} / C_P$.

## 3. Resultados y Punto Extremo Medido

A partir de los 18 registros experimentales disponibles:
- A $2950.000\text{ rpm}$ ($n \approx 49.167\text{ rev/s}$): $T \approx 0.0134\text{ N}$, $P \approx 0.0265\text{ W}$, $M_{\text{tip}} \approx 0.0369$, $Re_{0.75R} \approx 4715$, $FM \approx 0.5184$.
- En el extremo experimental medido:
  - $\text{RPM} = 19923.333\text{ rpm}$ ($n \approx 332.056\text{ rev/s}$)
  - Coeficientes medidos: $C_T = 0.125828$, $C_P = 0.059879$
  - Magnitudes calculadas ($D = 0.08128\text{ m}$, $\rho = 1.225\text{ kg/m}^3$ supuesta):
    - Empuje estático: $T \approx 0.74177\text{ N}$
    - Potencia de eje: $P \approx 9.527\text{ W}$
    - Mach de punta: $M_{\text{tip}} \approx 0.2492$ ($M < 0.3$, régimen subsónico incompresible)
    - Reynolds seccional: $Re_{0.75R} \approx 31845$
    - Figura de Mérito ideal: $FM \approx 0.5947$

## 4. Distinciones Clave y Límites del Estudio

1. **Naturaleza de la potencia dimensional calculada:** La potencia dimensional calculada ($P \approx 9.527\text{ W}$) representa exclusivamente la potencia mecánica absorbida por el eje. No es una magnitud directamente medida en el ensayo ni debe denominarse potencia eléctrica.
2. **Incompatibilidad con C02:** Los resultados de esta hélice bipala abierta no validan ni son aplicables al ventilador entubado C02.
3. **Criterio de no extrapolación:** El rango de validez está estrictamente limitado al intervalo ensayado de $2950.000$ a $19923.333\text{ rpm}$. El motivo para no extrapolar es únicamente la falta de datos fuera del dominio proporcionado.

## 5. Referencias

- UIUC Propeller Database (Volume 2): https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html
- Deters & Selig (figura 38 geometría): https://m-selig.ae.illinois.edu/pubs/DetersSelig-2008-AIAA-2008-6246-MicroProps.pdf
