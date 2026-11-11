# Balance parcial del dominio exterior con series por paso

Se extrajo una instantánea de las series mientras foamRun seguía activo; no se modificaron sus campos. Se seleccionaron 54 tiempos comunes completos desde 5,0615e−6 hasta 3,02387e−5 s. La exclusión de los primeros microsegundos separa el arranque más inmediato, pero no elimina el transitorio físico. Densidad supuesta 1,225 kg/m³.

El balance usa acumulación de rho·integral(U dV), flujo convectivo saliente rho·suma(phi U) y carga opuesta a la tracción del fluido en toda la frontera. En los extremos abiertos esa carga es una contribución matemática, no una pieza del vehículo. Se conservan signos y normales salientes del fluido.

| Término medio, integración por extremo derecho | x / y / z (N) |
|---|---|
| Acumulación | 0.7117827 / 0.03437412 / -6.462001 |
| Transporte convectivo | 0.0001443482 / 2.454676e-06 / 10.90917 |
| Tracción opuesta al fluido | -0.7119377 / -0.03438202 / -4.447421 |
| Residuo | -1.072999e-05 / -5.443555e-06 / -0.0002568342 |

La norma del residuo es 0.000257116 N y la normalización respecto a la mayor norma de contribución da 0.00235688 %. La regla de extremo derecho usa la temporalidad Euler del solver, aunque la reconstrucción de tracciones y este balance no equivalen al residuo exacto de la matriz discreta.

Con trapecios sobre los mismos registros, el residuo es 0.00615534 N (0.0564236 %). La diferencia entre reglas muestra sensibilidad de cuadratura durante un arranque rápido. Ninguno de estos porcentajes es incertidumbre de fuerza, presión, velocidad o prestaciones.

El máximo desajuste relativo de caudal a la precisión escrita es 5.8658e-10. Todos los términos se compararon en los mismos tiempos completos, sin extrapolar ni combinar filas parciales de la copia en vivo.

La acumulación axial media es aproximadamente −6,462 N, frente a transporte convectivo de +10,909 N. No se puede omitir: el estado sigue muy lejos de una interpretación estacionaria. El campo inicial potencial ya tiene circulación en el exterior y no representa un encendido físico del propulsor.

No se compara este porcentaje directamente con el 0,383 % del canal anterior como si fuera una mejora de exactitud física: son dominios, ventanas y cuadraturas distintos. La nueva adquisición por paso permite un chequeo temporal más definido y conserva explícita la falta de convergencia física.

No hay rotor, carrocería instalada, potencia o modelo compresible. Los máximos locales aún corresponden al arranque de un campo potencial con picos altos; faltan desarrollo, sensibilidad de malla/dominio/paso y control de compresibilidad local. No se aceptan cargas medias ni se dimensionan servos.

Archivos: `snapshots_exterior_1/` conserva la instantánea; `BALANCE_EXTERIOR_PARCIAL_1.json` conserva el balance y estadísticas de lectura; `auditar_balance_exterior.py` puede repetirse con otra instantánea nueva. El solver original y sus vigilantes continúan en ejecución.
