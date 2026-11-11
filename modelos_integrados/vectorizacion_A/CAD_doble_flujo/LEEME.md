# A: rama opcional de doble flujo

`neutro.step` y `omni_diagonal.step` contienen una propuesta geométrica de bancos de álabes a ambos lados del rotor. Cada STEP se reimportó con 149 piezas válidas. Es una variante de estudio dentro de la arquitectura A seleccionada; no sustituye automáticamente a la versión base ni acredita prestaciones de vuelo.

Para la escala de referencia de 5 kg supuestos: cuatro rotores representativos con plano de pala en z=7 mm y motores representativos centrados en z=−1 mm. Filas inferiores X/Y en −21/−39 mm y superiores X/Y en +19/+37 mm. Hay 48 álabes, 48 ejes y cuatro conductos. Los diámetros de las palas son ilustrativos y no proceden de un dimensionamiento propulsivo.

`VERIFICACION.json` registra 48 prismas conservadores del barrido mecánico ±45°, su contención en la envolvente, separación con los motores/rotores, ausencia de intersección rotor/conducto y los pasos geométricos de ejes en las paredes. Las separaciones entre filas y respecto a motor son aproximadamente 1,930 y 1,965 mm. No se ha realizado una aprobación de tolerancias, deformaciones, montaje o fabricación, ni una revisión de todas las parejas de piezas.

El modo diagonal ilustra bancos inferiores activos en dos canales y superiores activos en los otros dos. Los ángulos 35°/−35° son poses de presentación: no equivalen a un ángulo de fuerza medido. Los bancos de entrada se muestran neutros; sus pérdidas e interacción con el rotor están pendientes.

El rotor reversible, buje de paso, servos/transmisiones, rodamientos, sellos, protección de salida inferior y puertas de alta velocidad no están dimensionados. La envolvente exterior sigue siendo una representación de diseño industrial, no una carcasa de pared/material definidos.

Los volúmenes e inercias calculados son geométricos. La masa de 0,710 kg de conductos/álabes/ejes es solo un escenario con densidades supuestas: no incluye el resto del vehículo. No transferirla como peso del módulo completo.

Resultados y comparación con la versión base: `../reversibilidad_6DOF/INFORME.md`. Código de generación: `../../doble_flujo_A.py` desde `modelos_integrados`.
