# Reacción de paredes y álabes: auditoría de un campo guardado

## Resultado y alcance

En el campo de Euler a t=0,0005 s del reinicio, la magnitud lateral de las cargas sumadas sobre álabes es 6,976 N y la de todos los sólidos mojados del dominio es 2,110 N. La razón es 0,303. Esta diferencia es numérica e instantánea: no demuestra una eficiencia instalada del 30 %, ni valida cargas físicas. El flujo inicial no está desarrollado y faltan rotor y dominio exterior.

Se ejecutó `foamPostProcess -solver incompressibleFluid -time 0.0005` sobre una copia aislada, sin avanzar el tiempo ni modificar el solver activo. Las fuerzas incluyen presión y esfuerzo viscoso efectivo del modelo SST, con densidad supuesta 1,225 kg/m³.

| Grupo | Fx / Fy / Fz (N) | Mx / My / Mz respecto al origen (N·m) |
|---|---|---|
| vanes | -4.46834 / -5.35678 / -8.06064 | -0.048996 / 0.183946 / 0.000830 |
| walls | 2.37889 / 5.65198 / -0.21616 | 0.073937 / -0.091241 / 0.000101 |
| all_solid | -2.08944 / 0.29520 / -8.27680 | 0.024941 / 0.092706 / 0.000931 |

## Comprobaciones

La suma de los seis álabes coincide con su integración agrupada; esa suma más paredes coincide con la integración de todos los sólidos. Se verificaron además las seis transformaciones M_origen = M_centro + r × F contra los registros de la ejecución original. Las tolerancias (5e−6 N y 5e−8 N·m) responden al redondeo de salida del posprocesado; no representan exactitud física.

La implementación instalada de OpenFOAM13 `forcesBase.C` integra presión como rho(p)·Sf·(p−pRef), con Sf orientada hacia fuera del fluido, y calcula momentos respecto al CofR elegido. Las cargas de este informe son del fluido sobre los sólidos y usan un origen común. Los antiguos momentos locales de bisagra no se suman directamente como momento del vehículo.

## Consecuencia para el diseño

No se calibrará el cono efectivo de control a partir de las fuerzas sobre álabes aisladas. El dominio actual es un cilindro de radio 42 mm, desde z=−65 hasta +80 mm, con bancos centrados en z=−12 y −40 mm. La pared después del último banco, la interacción entre bancos y la condición de salida pueden cambiar la dirección del flujo; este único campo no permite separar sus contribuciones ni concluir qué geometría es óptima.

El siguiente ensayo físico-numérico debe incluir una salida a dominio exterior, fuerzas en todos los sólidos y un balance de cantidad de movimiento con términos de presión, flujo convectivo y acumulación transitoria. La instalación posterior debe añadir rotor, carrocería, accionamientos y potencia. Debe comprobarse sensibilidad a longitud/salida y malla antes de trasladar resultados al CAD A. La elección estética y de arquitectura A sigue vigente, pero el ángulo efectivo de vectorización de 45° usado en modelos ideales continúa siendo un supuesto.

## Reproducción y archivos

`preparar_auditoria_reaccion.py` crea el caso sin sobrescribirlo. El campo original t=0,0005 se copia explícitamente desde la ejecución existente. `auditar_reaccion_conducto.py` valida particiones y cambio de origen con los registros conservados en `snapshots_pareados/euler`. `auditoria_reaccion_Euler_t0.0005/REACTION_AUDIT.json` contiene las integrales y errores de comprobación.
