# INFORME TÉCNICO: PROCESAMIENTO AERODINÁMICO UIUC

**Ensayo:** Hélice `mi_3.2x2.2` a 20051 RPM nominales (Corrida UIUC `0544rd_20051`)  
**Fuente de datos:** UIUC Propeller Data Site (Volume 2), https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html  
**Archivo fuente:** `salidas/datos/mi_3.2x2.2_0544rd_20051.txt`

---

### 1. Clasificación Rigurosa de Variables

1. **Mediciones registradas en banco (adimensionales):**
   - Coeficiente de avance: $J = V / (n D) \in [0.044195, 0.448667]$ (19 puntos).
   - Coeficiente de empuje: $C_T \in [0.041281, 0.124104]$.
   - Coeficiente de potencia: $C_P \in [0.035779, 0.058227]$.
   - Eficiencia propulsiva registrada: $\eta_{reg} \in [0.094195, 0.562131]$.
   - Frecuencia rotacional nominal: $20051\text{ rpm}$ ($n = 334.1833\text{ rev/s}$).
2. **Supuestos de ingeniería adoptados:**
   - Diámetro del propulsor: $D = 0.08128\text{ m}$ (3.2 in).
   - Densidad de referencia supuesta para dimensionalización: $\rho = 1.225\text{ kg/m}^3$.
   - Configuración: hélice abierta libre aislada en corriente subsónica incompresible.
3. **Cálculos analíticos derivados:**
   - Velocidad de avance: $V = J \cdot n \cdot D$ ($V \in [1.20, 12.19]\text{ m/s}$ / $[4.32, 43.87]\text{ km/h}$).
   - Empuje dimensional: $T = C_T \cdot \rho \cdot n^2 \cdot D^4$ ($T \in [0.2465, 0.7410]\text{ N}$).
   - Potencia mecánica de eje: $P = C_P \cdot \rho \cdot n^3 \cdot D^5$ ($P \in [5.80, 9.44]\text{ W}$).
   - Eficiencia calculada: $\eta_{calc} = J \cdot C_T / C_P$.
   - Eficiencia ideal de Rankine-Froude: $\eta_{ideal} = 2 / (1 + \sqrt{1 + \frac{8}{\pi} \frac{C_T}{J^2}})$.

---

### 2. Verificación de Referencia ($J_{max}$)

Para el punto de mayor avance ensayado ($J = 0.448667$) con $20051\text{ rpm}$ y $D = 0.08128\text{ m}$:
$$n = \frac{20051}{60} = 334.183333...\text{ rev/s}$$
$$V = 0.448667 \times 334.183333... \times 0.08128 = 12.18688...\text{ m/s} \approx 12.19\text{ m/s} \quad (43.87\text{ km/h})$$
El valor dimensional obtenido confirma exactamente la fórmula comprobable.

---

### 3. Evaluación de Eficiencia y Metrología

- **Dominio propulsivo:** En los 19 puntos se verifica $J > 0$, $C_T > 0$ y $C_P > 0$, cumpliéndose la cota teórica $0 < \eta_{calc} < \eta_{ideal} < 1$. La máxima eficiencia registrada es $56.21\%$ en $J = 0.380780$ ($V = 37.23\text{ km/h}$).
- **Residuo de redondeo tabular:** La diferencia máxima $|\eta_{reg} - \eta_{calc}|$ es $1.18 \times 10^{-5}$ ($0.0023\%$), atribuible por completo al truncamiento de 6 decimales del archivo ASCII.
- **Corrección metrológica:** Los archivos entregados no especifican incertidumbre experimental de los sensores. Se eliminan las tolerancias inventadas ($\pm 1\%$ a $\pm 3\%$) presentes en versiones anteriores, evitando confundir resolución numérica con precisión instrumental no sustentada.

---

### 4. Restricciones Físicas y Operativas

1. **No extrapolación a 600 km/h:** A $600\text{ km/h}$ ($166.67\text{ m/s}$), el avance hipotético sería $J \approx 6.14$, orden de magnitud superior al límite ensayado ($J_{max} = 0.448667$). No se extrapola porque los datos entregados no cubren ese dominio operativo, no porque se haya demostrado falla física. Se eliminan conjeturas de rotura instantánea o inestabilidad aeroelástica no sustentadas en los datos.
2. **No transferencia a C02 entubado:** Los datos describen una hélice abierta libre en aire. No deben transferirse a ventiladores entubados ni a conducciones de dióxido de carbono ("C02 entubado"), debido a las diferencias de confinamiento por conducto y propiedades del fluido.

---

### 5. Reproducibilidad

El procesamiento se reproduce íntegramente sin acceso a red ejecutando:
`python3 salidas/procesar_uiuc_prop.py` y `python3 salidas/test_procesar_uiuc_prop.py` (11 pruebas unitarias superadas).
