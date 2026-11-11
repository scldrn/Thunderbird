# Paquete Reproducible de Escalado Matemático (2 kg, 5 kg, 10 kg)
## Análisis Aerodinámico Condicional de Rotores Ideales Abiertos: Base D82 vs Base D84

Este paquete contiene la implementación autocontenida y reproducible del estudio de **escalado geométrico semejante** ($D \propto m^{1/3}$) para objetivos de masa de 2 kg, 5 kg y 10 kg, basado en la configuración `C02_CANDIDATA` (`C02_COMPACTA_x160_5kg_2026-11-03_r2`) del proyecto aeronáutico.

El paquete evita el uso de rutas absolutas o temporales, almacena las copias de entrada requeridas en `salidas/datos/` y resuelve todas las rutas de lectura y escritura de manera relativa a `__file__`.

---

## 1. Instrucciones de Ejecución y Reproducción

Para ejecutar los scripts dentro de este paquete se requiere únicamente `python3` (estándar, sin dependencias externas):

### Ejecutar el cálculo y regenerar tablas:
```bash
python3 salidas/escalado_geometrico.py
```
*O ejecutando directamente dentro del directorio `salidas/`:*
```bash
cd salidas && python3 escalado_geometrico.py
```

### Ejecutar la suite de pruebas y verificación independiente:
```bash
python3 salidas/test_escalado.py
```
*O ejecutando directamente dentro del directorio `salidas/`:*
```bash
cd salidas && python3 test_escalado.py
```

---

## 2. Verificación Independiente del Escalado y Potencias de Hover

Bajo las condiciones de referencia de atmósfera estándar ($\rho = 1.225\text{ kg/m}^3$, $g = 9.80665\text{ m/s}^2$), para **4 discos ideales abiertos** con diámetro de referencia en 5 kg de $D_5 = 82\text{ mm}$ ($0.082\text{ m}$), la teoría unidimensional de cantidad de movimiento (Rankine-Froude) en condición de estacionario puro ($a = 0\text{ g}$, $T = m \cdot g$) arroja los siguientes resultados verificados independientemente:

| Masa Objetivo ($m$) | Diámetro Rotor ($D$) | Área Total ($A_{\text{tot}}$) | Empuje Requerido ($T$) | Velocidad Inducida ($v_i$) | Potencia Inducida Ideal ($P_i$) | Potencia Aproximada |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2 kg** | 60.42 mm (0.060418 m) | 0.011468 m² (114.68 cm²) | 19.613 N | 26.42 m/s | **518.20 W** | **≈ 518 W** |
| **5 kg** | 82.00 mm (0.082000 m) | 0.021124 m² (211.24 cm²) | 49.033 N | 30.78 m/s | **1509.26 W** | **≈ 1509 W** |
| **10 kg** | 103.31 mm (0.103314 m) | 0.033532 m² (335.32 cm²) | 98.066 N | 34.55 m/s | **3388.18 W** | **≈ 3388 W** |

### Ecuaciones Gobernantes de Cantidad de Movimiento:
1. **Empuje total:**  
   $$T = m \cdot g \cdot (1 + a)$$
2. **Área total de 4 rotores:**  
   $$A_{\text{tot}} = 4 \times \left(\pi \frac{D^2}{4}\right) = \pi D^2$$
3. **Velocidad inducida ideal en el plano del rotor:**  
   $$v_i = \sqrt{\frac{T}{2 \rho A_{\text{tot}}}}$$
4. **Potencia inducida ideal:**  
   $$P_i = T \cdot v_i = \frac{T^{3/2}}{\sqrt{2 \rho A_{\text{tot}}}}$$

### Leyes de Escala Analíticas ($D \propto m^{1/3}$):
- **Factor de escala lineal:** $\lambda_m = (m / 5.0)^{1/3}$
- **Diámetro:** $D(m) = D_5 \cdot (m / 5.0)^{1/3} \propto m^{1/3}$
- **Área total:** $A_{\text{tot}}(m) = A_5 \cdot (m / 5.0)^{2/3} \propto m^{2/3}$
- **Velocidad inducida:** $v_i(m) = v_{i,5} \cdot (m / 5.0)^{1/6} \propto m^{1/6}$
- **Potencia inducida ideal:** $P_i(m) = P_{i,5} \cdot (m / 5.0)^{7/6} \propto m^{7/6} \approx m^{1.1667}$

Comprobación de la ley de potencia:
- $518.204\text{ W} \times (5/2)^{7/6} = 518.204 \times 2.912484 = 1509.26\text{ W}$
- $1509.260\text{ W} \times (10/5)^{7/6} = 1509.260 \times 2.244924 = 3388.18\text{ W}$

---

## 3. Aclaraciones Críticas y Delimitación de Alcance

### A. NO es la potencia eléctrica instalada ni el consumo real del propulsor
Los valores de 518 W, 1509 W y 3388 W corresponden **exclusivamente a la potencia inducida ideal** de un disco actuador abierto sin fricción ni viscosidad.
En un ventilador entubado real, existen múltiples fuentes de disipación y penalización:
- **Pérdidas de punta (*tip clearance*):** El huelgo radial de 1.0 mm genera recirculación de vórtices.
- **Bloqueo del buje (*hub blockage*):** El motor central obstruye entre 15% y 25% del área de paso.
- **Arrastre de perfil de pala (*profile drag*):** La rotación de las palas a alta velocidad introduce fricción viscosa (Figura de Mérito típica $FM = P_i / P_{\text{eje}} \approx 0.55 - 0.70$).
- **Pérdidas por remolino (*swirl*):** Energía cinética residual no recuperada.
- **Eficiencia electromecánica:** Eficiencia del motor brushless ($\approx 80\% - 85\%$) y del ESC ($\approx 95\%$).

Por tanto, la **potencia eléctrica instalada real** es típicamente **1.8 a 2.5 veces mayor**:
$$P_{\text{eléctrica real}} \approx \frac{P_i}{FM \cdot \eta_{\text{motor}} \cdot \eta_{\text{ESC}}} \approx \frac{1509\text{ W}}{0.60 \times 0.83 \times 0.95} \approx 3190\text{ W} \quad (\approx 800\text{ W por ventilador a 5 kg})$$

### B. NO es un diseño aceptado ni validado de ninguna escala
- En el archivo canónico de configuración (`C02_CANDIDATA.json`), las variantes de 2 kg y 10 kg están expresamente marcadas como `pending_own_configuration` (no disponen de CAD, ni balance de componentes, ni arquitectura estructural).
- La configuración de 5 kg es un candidato preliminar de empaquetamiento e integración CAD (`partial_CAD_candidate`), con estado `rotor_motor_servo_and_cooling_qualified: false`.
- Los campos de masa real, centro de gravedad e inercias son no cuantificados (`actual_mass_kg: null`, `actual_CG_m: null`, `actual_inertia_kgm2: null`).
- El propio registro formal declara: `mass_targets_are_actual_masses: false`. Por tanto, este escalado es un ejercicio matemático analítico condicional, no un vehículo validado.

### C. D84 es otra hipótesis de referencia (Diámetro de Conducto / Bore)
En la iteración previa (`REFERENCIA_DISCO.csv`), se utilizó como referencia a 5 kg el diámetro $D = 0.084\text{ m}$ ($84\text{ mm}$).
- **Origen de D84:** Corresponde al diámetro interno del conducto (`nominal_bore_diameter_m = 0.084` en `C02_CANDIDATA.json`).
- **Origen de D82:** Corresponde al radio aerodinámico nominal BEM de la pala del rotor (`BEM_nominal_radius_m = 0.041` $\implies D = 82\text{ mm}$).
- **Diferencia física:** La diferencia radial de 1 mm ($R_{\text{bore}} - R_{\text{BEM}} = 42 - 41 = 1\text{ mm}$) es el huelgo de punta (*tip clearance*).
- **Relaciones analíticas exactas entre D82 y D84:**
  - $\frac{D_{82}}{D_{84}} = \frac{82}{84} = \frac{41}{42} \approx 0.976190 \quad (-2.381\%)$
  - $\frac{A_{82}}{A_{84}} = \left(\frac{41}{42}\right)^2 = \frac{1681}{1764} \approx 0.952948 \quad (-4.705\%)$
  - $\frac{v_{i,82}}{v_{i,84}} = \frac{42}{41} \approx 1.024390 \quad (+2.439\%)$
  - $\frac{P_{i,82}}{P_{i,84}} = \frac{42}{41} \approx 1.024390 \quad (+2.439\%)$

Al pasar de la hipótesis de conducto (D84) a la hipótesis de rotor físico (D82), el área del disco se reduce un 4.71% y la potencia inducida aumenta sistemáticamente un +2.44% en todas las masas y aceleraciones.

### D. NO se declara regla universal de límite para ventiladores entubados
El disco actuador abierto ideal **no constituye una regla ni cota universal de límite para un propulsor entubado** (*ducted fan*):
1. **Efecto de labio y difusión (reducción de potencia teórica):** Un conducto bien conformado puede generar sustentación por succión en el labio y expandir el área del chorro en la salida ($A_e > A_{\text{rotor}}$). En tal caso, la teoría de cantidad de movimiento entubada muestra que la potencia inducida teórica para producir el mismo empuje total puede ser **inferior** a la de un disco abierto del mismo diámetro.
2. **Pérdidas reales de instalación (aumento de potencia):** En contraposición, las pérdidas viscosas, fricción en conducto, vórtices de huelgo y arrastre de perfil hacen que la potencia real demandada sea sustancialmente **superior**.

Dado que los efectos favorables (difusión aerodinámica) y desfavorables (fricción y pérdidas de punta) compiten entre sí según el diseño del conducto, **el disco abierto ideal no es ni una cota superior ni una cota inferior universal** de un ventilador entubado.

---

## 4. Clasificación Rigurosa de Datos

| Parámetro | Tipo | Valor | Unidades | Fuente |
|:---|:---:|:---:|:---:|:---|
| Densidad del aire ($\rho$) | Supuesto de referencia | 1.225 | kg/m³ | `C02_CANDIDATA.json` (`operating_reference`) |
| Aceleración gravedad ($g$) | Constante física | 9.80665 | m/s² | `C02_CANDIDATA.json` (`operating_reference`) |
| Diámetro de conducto ($D_{\text{bore}}$) | Medido / CAD nominal | 0.084 (84.0) | m (mm) | `C02_CANDIDATA.json` (`nominal_bore_diameter_m`) |
| Radio BEM de pala ($R_{\text{BEM}}$) | Medido / CAD nominal | 0.041 (41.0) | m (mm) | `C02_CANDIDATA.json` (`BEM_nominal_radius_m`) |
| Diámetro rotor base D82 | Cálculo geométrico | 0.082 (82.0) | m (mm) | $2 \times R_{\text{BEM}}$ |
| Huelgo radial de punta ($\delta$) | Cálculo geométrico | 0.001 (1.0) | m (mm) | $R_{\text{bore}} - R_{\text{BEM}}$ |
| Número de ventiladores | Nominal CAD | 4 | unidades | `C02_CANDIDATA.json` (`fan_reference.count`) |
| Centros de propulsores | Nominal CAD | $(\pm 0.16, \pm 0.076)$ | m | `C02_CANDIDATA.json` (`centres_xy_m`) |
| Masa real de la variante 5 kg | No cuantificada | `null` | kg | `C02_CANDIDATA.json` (`actual_mass_kg: null`) |
| Masas de variantes 2 y 10 kg | No diseñadas | `pending` | - | `C02_CANDIDATA.json` (`variants`) |
| Flujo y disco actuador | Supuesto de cálculo | 1D incompresible | - | Teoría de Rankine-Froude |

*Nota sobre reservas:* En concordancia con los principios del proyecto, no se infiere que reservas o componentes sin masa asignada tengan masa nula o no nula; se declaran estrictamente como no cuantificadas.

---

## 5. Estructura de Archivos del Paquete

```
salidas/
├── datos/
│   ├── C02_CANDIDATA.json              # Copia local de referencia de configuración C02
│   └── REFERENCIA_DISCO.csv            # Copia local de la línea base previa (D84)
├── escalado_geometrico.py              # Script principal de escalado y generación de entregables
├── test_escalado.py                    # Suite de pruebas unitarias y verificación matemática
├── TABLA_ESCALADO_D82.csv              # Resultados completos de la base D82 (2, 5, 10 kg; 0g, 0.5g, 1.0g)
├── COMPARATIVA_D82_VS_D84.csv          # Tabla comparativa completa punto a punto D82 vs D84
├── TABLA_ESTACIONARIO_COMPARADA.md     # Tabla Markdown comparativa resumida para estacionario (hover)
├── README.md                           # Esta guía técnica de reproducción y alcance
└── INFORME_ESCALADO_2_5_10.md          # Informe técnico detallado de ingeniería aeronáutica
```
