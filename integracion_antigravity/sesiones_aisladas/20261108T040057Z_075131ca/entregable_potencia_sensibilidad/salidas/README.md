# Paquete Autónomo: Sensibilidad de Arrastre Hipotético $p \in \{1, 2, 4\}$ para C02 (5,0 kg)

Este paquete contiene la evaluación aerotécnica y energética independiente de la sensibilidad al exponente de la ley de arrastre:

$$D(v) = D_{\text{final}} \left( \frac{v}{V} \right)^p, \quad p \in \{1, 2, 4\}$$

aplicada a la candidata **C02 (5,0 kg)** durante su fase de aceleración rectilínea uniforme.

El paquete es completamente autónomo, reproducible y no depende de rutas temporales absolutas.

---

## Estructura de Entregables en `salidas/`

- **[`sensibilidad_ley_arrastre.py`](sensibilidad_ley_arrastre.py)**: Módulo principal de cálculo paramétrico, integración analítica y numérica (Simpson), modelado de misión por etapas, dimensionamiento bi-criterio de batería y exportación de resultados.
- **[`test_sensibilidad.py`](test_sensibilidad.py)**: Suite de 11 pruebas unitarias automatizadas (`unittest`) que verifican la integridad física, la exactitud de la integral, la convergencia numérica, el cotejo contra el modelo $r2$ de entrada y la auditoría anti-duplicación de energía.
- **[`REPORTE_SENSIBILIDAD_ARRASTRE.md`](REPORTE_SENSIBILIDAD_ARRASTRE.md)**: Informe técnico exhaustivo con deducciones matemáticas completas, análisis físico, tablas comparativas, advertencias aerodinámicas y trazabilidad criptográfica.
- **[`tabla_comparacion_casos.csv`](tabla_comparacion_casos.csv)**: Matriz con los 12 casos centrales comparativos ($V \in \{600, 1000\}\text{ km/h}$, $D_{\text{final}} = 50\text{ N}$, $t = 60\text{ s}$, $P_{\text{aux}} \in \{0, 1000\}\text{ W}$, $p \in \{1, 2, 4\}$).
- **[`tabla_sensibilidad_completa.csv`](tabla_sensibilidad_completa.csv)**: Matriz extendida de 360 escenarios paramétricos que barren velocidades ($600, 1000\text{ km/h}$), arrastres ($0, 10, 25, 50\text{ N}$), cargas de apoyo ($0, 1000, 2968.81\text{ W}$), tiempos de aceleración ($10, 30, 60, 120, 180\text{ s}$) y exponentes ($1, 2, 4$).
- **[`resultados_sensibilidad.json`](resultados_sensibilidad.json)**: Archivo JSON estructurado con metadatos de ejecución, verificación analítica vs Simpson, cotejo contra $r2$, tiempos de cruce $t^*$ y conclusiones.
- **[`README.md`](README.md)**: Esta guía de uso y documentación.

---

## Instrucciones de Reproducción

Todas las operaciones se ejecutan con Python 3 estándar (sin dependencias externas):

```sh
# 1. Ejecutar el cálculo y generar tablas y resumen JSON:
python3 salidas/sensibilidad_ley_arrastre.py

# 2. Ejecutar la suite completa de pruebas unitarias:
python3 -m unittest salidas/test_sensibilidad.py
```

---

## Formulación Matemática Fundamental

### 1. Integral Exacta del Trabajo de Arrastre en Aceleración
Para una aceleración rectilínea constante $a = V/t$ desde el reposo hasta $V$:
$$W_{\text{arrastre, acel}} = \int_0^t D_{\text{final}} \left(\frac{\tau}{t}\right)^p \cdot V \left(\frac{\tau}{t}\right) d\tau = \frac{D_{\text{final}} \cdot V \cdot t}{p + 2} \quad \text{[J]}$$

- **Caso lineal ($p = 1$):** $W = \frac{D V t}{3} \quad (+33,33\% \text{ respecto a } p=2)$
- **Caso cuadrático ($p = 2$):** $W = \frac{D V t}{4} \quad (\text{caso base de referencia } r2)$
- **Caso cuártico ($p = 4$):** $W = \frac{D V t}{6} \quad (-33,33\% \text{ respecto a } p=2)$

### 2. Invariancia de la Potencia de Pico Axial
La potencia mecánica instantánea es máxima en el punto terminal $\tau = t$ ($v = V$):
$$P_{\text{mec, pico}} = \left( m \frac{V}{t} + D_{\text{final}} \left(\frac{V}{V}\right)^p \right) V = m \frac{V^2}{t} + D_{\text{final}} V$$
Dado que $(V/V)^p = 1^p = 1$ para todo $p > 0$, la potencia de pico es **estrictamente invariable respecto a $p$**.

### 3. Partición de Energía por Etapas y Auditoría Anti-Duplicación
La energía total de la misión se descompone en tres intervalos temporales disjuntos:
$$E_{\text{total}} = E_{\text{etapa 1 (estacionario)}} + E_{\text{etapa 2 (aceleración)}} + E_{\text{etapa 3 (crucero)}}$$

- **Sin doble conteo inercial:** La energía cinética $\frac{1}{2} m V^2$ se computa una única vez (en aceleración); en crucero la aceleración es nula ($a = 0, \Delta E_k = 0$).
- **Sin doble conteo de arrastre:** El arrastre de aceleración se integra únicamente sobre $[0, t]$ y el de crucero sobre $[t, t + 30]$.
- **Sin confusión potencia-energía:** La potencia de pico simultánea no se multiplica por el tiempo para sumar energía; solo dimensiona la masa por potencia de la batería.

---

## Clasificación de Parámetros

- **Datos Medidos:** Ninguno. No existen ensayos de túnel ni vuelos de C02 en los registros disponibles.
- **Supuestos:**
  - Vehículo C02: $m = 5,0\text{ kg}$.
  - Presupuesto ligero CAD: parcial asignado $2,04584\text{ kg}$, reserva $0,75\text{ kg}$, masa disponible para batería $2,20416\text{ kg}$.
  - Batería: densidad de energía $150\text{ Wh/kg}$, densidad de potencia $5.000\text{ W/kg}$.
  - Misión: $30\text{ s}$ estacionario ($27\text{ s}$ a $2.968,81\text{ W} + 3\text{ s}$ a $3.505,89\text{ W}$), aceleración uniforme ($10 - 180\text{ s}$), $30\text{ s}$ crucero.
  - Eficiencia axial constante $\eta = 0,70$.
  - Carga de apoyo constante $P_{\text{aux}} \in \{0, 1000, 2968.81\}\text{ W}$.
- **Cálculos:** Cinemática, integrales de trabajo mecánico, energías eléctricas por etapa, potencia pico simultánea y masa requerida de batería por el criterio $\max(m_E, m_P)$.

---

## Advertencias Físicas y Limitaciones Explícitas

1. **Limitación a $v = 0$:** Asumir eficiencia constante $\eta = 0,70$ produce una potencia mecánica cero en reposo ($P = F \cdot v = 0$). Un propulsor real (rotor o fan) requiere una potencia estática no nula para generar empuje a velocidad cero.
2. **Limitación en Régimen Transónico ($M \approx 0,75 - 1,2$):** Ninguna ley de potencias simple $(v/V)^p$ reproduce los fenómenos de compresibilidad transónica: divergencia de Mach ($M_{dd}$), ondas de choque locales, arrastre de onda, interacción choque-capa límite ni la regla de las áreas de Whitcomb.
3. **No Extrapolación:** Este análisis es estrictamente condicional al modelo paramétrico de C02 (5,0 kg). No certifica prestaciones reales de vuelo ni puede trasladarse a variantes físicas de 2 kg o 10 kg sin sus propios modelos y presupuestos geométricos.
