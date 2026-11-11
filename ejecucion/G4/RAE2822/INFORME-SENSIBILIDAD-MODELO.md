# Sensibilidad SST frente a Spalart–Allmaras

4 de noviembre de 2026. Dos modelos RANS sobre la misma malla dan diferencias calculadas de 4,80% en CL y 5,38% en CD. Esta dispersión no es un intervalo de confianza ni valida el vehículo. Confirma que la elección del modelo debe figurar en el presupuesto de incertidumbre.

## Comparación controlada

Se reutilizan los 97.152 cuadriláteros del perfil NASA y el mismo binario SU2 8.6.0. El comparador comprueba hashes de malla/binario, condiciones medias, transporte, referencias y opciones numéricas. Las diferencias permitidas son el modelo, sus variables de entrada, límites de iteración y salida. Mach=0,729, α=2,31°, Re=6,5 millones y cuerda=0,3048 m permanecen iguales.

La variante ejecutada es **SA-noft2**, sin correcciones, según el registro y las opciones de SU2. No se presume identidad con el SA histórico de WIND. Las variantes se distinguen en el [Turbulence Modeling Resource](https://tmbwg.github.io/turbmodels/spalart.html). El cambio de dirección del recurso se verificó mediante la [página oficial de NASA](https://www.nasa.gov/nasa-turbulence-modeling-resource/).

Para preservar presión al pasar de SST a SA se usa ρE_SA=ρE_SST−ρk. Se reconstruye ν̃ invirtiendo νt/ν=χ⁴/(χ³+7,1³), con χ=ν̃/ν, usando la [implementación SA fijada](https://github.com/su2code/SU2/blob/v8.6.0/SU2_CFD/src/solvers/CTurbSASolver.cpp). Así se conserva la viscosidad turbulenta inicial; el factor de entrada 4,622838 produce νt/ν=1. Las diferencias máximas de conversión son 2,91×10⁻¹¹ Pa y 6,94×10⁻¹⁸ Pa·s. La intensidad de turbulencia no representa una variable transportada por SA.

El auditor ahora distingue los campos de cada modelo. La regresión sobre SST conserva exactamente coeficientes, termodinámica, cambios de estado, tracción y reconstrucción Roe anteriores. No se rebajaron sus comprobaciones.

## Resultados y límites

| Cálculo | SST fino, 3.600 pasos | SA-noft2, 1.800+600 pasos |
|---|---:|---:|
| CL | 0,67880791 | 0,71142410 |
| CD | 0,01259346 | 0,01327139 |
| RMS Cp, todos los 103 puntos | 0,123141 | 0,108282 |
| Indicador de recuperación superior, x/c | 0,51230 | 0,53105 |

El indicador es el punto medio del mayor gradiente positivo de Cp de pared en la ventana fija 0,2≤x/c≤0,8; no es una posición exacta de choque. Los intervalos de nodos correspondientes están guardados en `COMPARACION_MODELOS_r2.json`.

La sonda SA de 600 pasos cambia CL en 2,78×10⁻⁵ y CD en −2,71×10⁻⁷. La diferencia relativa L2 de ν̃ es 0,398%; sigue habiendo evolución del campo turbulento aunque las cargas varíen poco. La reconstrucción completa de fuerza pasa con error máximo de coeficiente 1,41×10⁻¹¹. La presión derivada de la energía SA coincide con la exportada dentro de 7,3×10⁻¹¹ Pa; la viscosidad turbulenta retenida muestra el desfase segregado medido, sin imponer una identidad de etapas distintas.

El menor RMS de SA en este caso no demuestra superioridad general. Se conservan todos los puntos, incluida la gran discrepancia de borde de ataque. Transición, resolución adicional, condiciones turbulentas supuestas y magnitudes integrales requieren sensibilidad. El experimento procede del [estudio NASA RAE2822](https://www.grc.nasa.gov/www/wind/valid/raetaf/raetaf04/raetaf04.html); la curva WIND publicada usa SA, pero no sustituye los datos experimentales.

No se transfieren estos porcentajes al cuerpo A07/C02 ni se selecciona un modelo solo por ajustar mejor esta curva. T21 y G4 permanecen abiertos. El paso siguiente es usar esta evidencia para fijar el alcance de cálculos del vehículo y las sensibilidades que requieren sus decisiones.
