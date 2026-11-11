# Entregable Autónomo y Reproducible: Análisis Estático de Hélice UIUC (Micro Invent 3.2x2.2)

Este paquete contiene el análisis aerodinámico estático completo, autónomo y reproducible de la hélice ultraligera abierta Micro Invent 3.2x2.2 ensayada en la base de datos de hélices de la Universidad de Illinois en Urbana-Champaign (UIUC Propeller Database, Volume 2).

Todos los scripts y pruebas leen los datos exclusivamente desde rutas relativas a `__file__`, lo que permite ejecutar el paquete de forma autónoma desde cualquier ubicación sin depender de rutas fijas del sistema.

---

## 1. Estructura de Archivos

```text
salidas/
├── README.md                    # Este documento con instrucciones de uso y verificación
├── INFORME.md                   # Informe técnico aerodinámico detallado
├── analizar.py                  # Script ejecutable de cálculo y reconstrucción de datos
├── test_analizar.py             # Batería de 18 pruebas unitarias e independientes
├── puntos.csv                   # CSV reconstruido con los 18 puntos calculados
└── datos/                       # Copia local de datos experimentales de entrada
    ├── mi_3.2x2.2_static_0519rd.txt  # Mediciones tacométricas, CT y CP
    └── mi_3.2x2.2_geom.txt           # Geometría radial (cuerda c/R y ángulo beta)
```

---

## 2. Instrucciones de Ejecución y Comandos

El entorno requiere únicamente **Python 3.8+** con la biblioteca estándar (sin dependencias externas adicionales).

### 2.1 Reconstrucción del Análisis y Generación del CSV

Para procesar los datos de ensayo estático, mostrar la tabla de resultados en consola y regenerar `puntos.csv`:

```bash
# Opción A: Desde el directorio salidas/
cd salidas
python3 analizar.py

# Opción B: Desde el directorio raíz
python3 salidas/analizar.py
```

### 2.2 Ejecución de la Suite de Pruebas Unitarias

Para ejecutar las 18 pruebas unitarias automatizadas (incluyendo verificación física, leyes de semejanza, bloqueo de extrapolación y verificación independiente del último punto):

```bash
# Opción A: Desde el directorio salidas/
cd salidas
python3 test_analizar.py -v

# Opción B: Desde el directorio raíz
python3 salidas/test_analizar.py -v

# Opción C: Mediante el módulo unittest estándar
python3 -m unittest salidas/test_analizar.py -v
```

---

## 3. Fuentes Primarias

1. **Base de Datos Experimental:** UIUC Propeller Database (Volume 2), Department of Aerospace Engineering, University of Illinois at Urbana-Champaign.
   * Archivo de ensayo estático: `datos/mi_3.2x2.2_static_0519rd.txt` (18 puntos medidos).
   * Archivo de distribución geométrica: `datos/mi_3.2x2.2_geom.txt` (18 estaciones radiales).
   * URL de referencia: `https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html`
2. **Publicación Metodológica:**
   * Deters, R. W., Ananda, G. K., & Selig, M. S. (2014). *"Reynolds Number Effects on the Performance of Small-Scale Propellers."* AIAA Paper 2014-2151, 32nd AIAA Applied Aerodynamics Conference, Atlanta, GA.
   * URL de publicación: `https://m-selig.ae.illinois.edu/pubs/DetersAnandaSelig-2014-AIAA-2014-2151.pdf`

---

## 4. Taxonomía de Parámetros: Medidos, Supuestos y Calculados

| Tipo de Parámetro | Magnitud | Símbolo | Valor / Rango | Unidad | Origen / Justificación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Medido** | Frecuencia de rotación | $\text{RPM}$ | $2,950.000$ a $19,923.333$ | $\text{rev/min}$ | Tacómetro en banco UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Medido** | Coeficiente de empuje | $C_T$ | $0.103654$ a $0.125828$ | $-$ | Célula de carga UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Medido** | Coeficiente de potencia | $C_P$ | $0.051360$ a $0.059879$ | $-$ | Sensor de par UIUC (`mi_3.2x2.2_static_0519rd.txt`) |
| **Medido** | Diámetro de hélice | $D$ | $3.2\text{ in} = 0.08128$ | $\text{m}$ | Especificación nominal Micro Invent / UIUC |
| **Medido** | Número de palas | $B$ | $2$ | $-$ | Configuración física bipala Micro Invent |
| **Medido** | Cuerda a $0.75R$ | $(c/R)_{0.75}$ | $0.1799$ | $-$ | Tabla geométrica UIUC (`mi_3.2x2.2_geom.txt`) |
| **Supuesto** | Densidad del aire | $\rho$ | $1.225$ | $\text{kg/m}^3$ | Atmósfera estándar ISA a nivel del mar ($15^{\circ}\text{C}$, $101,325\text{ Pa}$) |
| **Supuesto** | Velocidad del sonido | $a$ | $340.3$ | $\text{m/s}$ | Atmósfera estándar ISA |
| **Supuesto** | Viscosidad cinemática | $\nu$ | $1.46 \times 10^{-5}$ | $\text{m}^2/\text{s}$ | Aire estándar a $15^{\circ}\text{C}$ |
| **Supuesto** | Velocidad de avance | $V_\infty$ | $0.0$ | $\text{m/s}$ | Ensayo puramente estático ($J = 0$, punto fijo / *hover*) |
| **Calculado** | Frecuencia angular | $n$ | $49.167$ a $332.056$ | $\text{rev/s}$ | $n = \text{RPM} / 60$ |
| **Calculado** | Empuje estático | $T$ | $0.013397$ a $0.741771$ | $\text{N}$ | $T = C_T \rho n^2 D^4$ |
| **Calculado** | Potencia mecánica de eje | $P$ | $0.026527$ a $9.527113$ | $\text{W}$ | $P = C_P \rho n^3 D^5$ |
| **Calculado** | Mach de punta | $M_{\text{tip}}$ | $0.036893$ a $0.249162$ | $-$ | $M_{\text{tip}} = (\pi n D) / a$ |
| **Calculado** | Reynolds a $0.75R$ | $Re_{0.75R}$ | $4,715$ a $31,845$ | $-$ | $Re = (0.75 \pi n D \cdot c_{0.75}) / \nu$ |
| **Calculado** | Figura de Mérito | $FM$ | $0.518435$ a $0.594746$ | $-$ | $FM = \sqrt{2/\pi} \cdot C_T^{3/2} / C_P$ |

---

## 5. Verificación Independiente del Último Punto Experimental

Para el punto 18 (régimen operativo máximo del ensayo UIUC):
* **Condiciones de entrada:**
  * $\text{RPM} = 19,923.333\text{ rev/min} \implies n = 332.055556\text{ rev/s}$
  * $C_T = 0.125828$
  * $C_P = 0.059879$
  * $\rho = 1.225\text{ kg/m}^3$ (supuesta)
  * $D = 0.08128\text{ m}$ ($3.2\text{ in}$)
* **Cálculo de Empuje:**
  $$T = C_T \cdot \rho \cdot n^2 \cdot D^4 = 0.125828 \cdot 1.225 \cdot (332.055556)^2 \cdot (0.08128)^4 = 0.74177098\text{ N} \approx \mathbf{0.74177\text{ N}}$$
* **Cálculo de Potencia Mecánica de Eje:**
  $$P = C_P \cdot \rho \cdot n^3 \cdot D^5 = 0.059879 \cdot 1.225 \cdot (332.055556)^3 \cdot (0.08128)^5 = 9.52711317\text{ W} \approx \mathbf{9.5271\text{ W}}$$

Ambos valores concuerdan de forma exacta con la especificación requerida.

---

## 6. Distinción Crítica: Potencia de Eje vs. Potencia Eléctrica

> [!IMPORTANT]
> Los valores de potencia dimensional obtenidos en este análisis representan exclusivamente la **potencia mecánica entregada al eje de la hélice** ($P = 2\pi n Q = \omega \cdot \tau$).
>
> **NO corresponden a la potencia eléctrica consumida de la batería.**
> Para conocer la potencia eléctrica de entrada ($P_{\text{elec}} = V \cdot I$), es imperativo aplicar las pérdidas de la planta motopropulsora:
> $$P_{\text{elec}} = \frac{P}{\eta_{\text{motor}} \cdot \eta_{\text{esc}}}$$
> En micro-motores brushless típicos de esta escala, los rendimientos oscilan en $\eta_{\text{motor}} \approx 0.55 - 0.70$ y $\eta_{\text{esc}} \approx 0.85 - 0.90$. En consecuencia, para generar los $9.5271\text{ W}$ mecánicos en el eje a 19,923 RPM, la batería debe suministrar típicamente entre **$15\text{ W}$ y $19\text{ W}$ eléctricos**.

---

## 7. Diferencias Aerodinámicas con Ventilador Interno / Entubado (EDF C02)

Los datos de la hélice abierta Micro Invent 3.2x2.2 **no son aplicables ni extrapolables al ventilador entubado C02 (EDF de 8 palas)** por motivos aerodinámicos fundamentales:

1. **Efecto de contorno (Ducto vs. Estela Libre):** En la hélice libre, los vórtices marginales de punta inducen pérdidas 3D y contracción libre de la estela ($A_{\infty} \to A/2$). En un ventilador entubado, la carcasa confina las puntas de pala eliminando los vórtices convencionales, y la succión sobre el labio de entrada (*lip suction*) aporta típicamente entre el 30% y 50% del empuje estático total.
2. **Solidez y número de palas (2 vs. 8):** Un rotor de 8 palas opera en régimen de cascada de perfiles de alta solidez, con fuerte interferencia aerodinámica pala a pala y fenómenos de bloqueo aerodinámico inexistentes en una hélice bipala abierta.
3. **Pérdidas viscosas internas:** El conducto genera pérdidas por fricción sobre la superficie interna y efectos difusores que no intervienen en una hélice libre.

---

## 8. Prohibición de Extrapolación de RPM

* El análisis se encuentra estrictamente delimitado al intervalo experimental ensayado: **$[2,950.000, \, 19,923.333]\text{ RPM}$**.
* Operar por encima de 19,923 RPM provocaría deformaciones aeroelásticas no medidas en palas ultraligeras, desalineación de paso, vibraciones por flutter y potencial rotura mecánica.
* Operar por debajo de 2,950 RPM sitúa el flujo en regímenes de Reynolds ultra-bajos ($Re < 4,000$) donde la separación laminar profunda invalida la semejanza.
