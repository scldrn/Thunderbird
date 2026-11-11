# C02: autoridad ideal y sensibilidad al brazo vertical

**7 de noviembre de 2026, hora de Bogotá.** Este estudio cuantifica una
sensibilidad de asignación estática para la candidata C02 de 5 kg. **No es una
predicción de vuelo ni un mapa de los ventiladores instalados.** La posición
del centro de gravedad y la aplicación efectiva de las fuerzas siguen sin
identificarse; el centroide de la geometría parcial no es un CG del vehículo.

## Modelo y alcance

Se toman cuatro centros nominales en `x=±0,160 m`, `y=±0,076 m`, con fuerzas
dentro de conos ideales discretizados. Se fija la suma vertical en `mg`, la
componente lateral `Fy=0` y tres momentos, y se maximiza la fuerza en `+x` o
`−x`. El casco convexo de 65 rayos por módulo aproxima el cono supuesto por su
interior. Se exploran límites de 20,58 y 25 N por módulo, conos de 35° y 45° y
momentos de alabeo de 0 o 0,5 N·m: **son hipótesis, no capacidades medidas de
C02**. No se modelan retardos, un empuje mínimo, potencia, aerodinámica
exterior, par de reacción ni giroscopía.

Los signos de las tablas corresponden al **sistema CAD** de
`C02_CANDIDATA.json`: la nariz está en `−x`, por lo que `+x` apunta hacia la
cola; `z` apunta hacia arriba. Para convertir a ejes de vuelo FLU se cambian
los signos de `x` e `y`. No se han identificado las posiciones ni los signos
físicos de las fuerzas reales.

Primero `salida_r1/` resuelve 40 casos con brazo vertical nulo y dirección
`+x`. Después `sensibilidad_brazo_r1/` añade 400 combinaciones de cinco CG
longitudinales supuestos, cinco brazos verticales, dos direcciones y las dos
opciones de cono, fuerza y momento. El brazo es `z_fuerza − z_CG`, supuesto
igual para todos los módulos. El punto efectivo real depende del conjunto
ventilador–conducto–álabes; no se conoce por la posición del rotor en el CAD.

Para el modelo con brazo común, el equilibrio de cabeceo impone
`Σ(xᵢ Fzᵢ) = x_CG·mg + z_rel·Fx_total`. Así, un brazo vertical puede aliviar o
agravar la distribución de fuerza vertical según el signo de la aceleración y
el CG supuesto. La simetría del cuerpo no garantiza por sí sola simetría de
respuesta de esta instalación.

## Ejemplo ilustrativo

Con `x_CG=+0,096 m`, cono ideal de 45°, límite supuesto de 20,58 N por módulo y
momento de alabeo nulo:

| Brazo vertical supuesto | Aceleración máxima ideal en +x | Aceleración máxima ideal en −x |
|---:|---:|---:|
| −0,039 m | 0,731 g | 0,254 g |
| 0 m | 0,441 g | 0,441 g |
| +0,039 m | 0,254 g | 0,731 g |

Son máximos de equilibrio de fuerzas en un LP, no tiempos de respuesta ni
capacidad demostrada en vuelo. El valor `0,096 m` es un punto de sensibilidad
próximo al centroide de una suma geométrica parcial; **no se adopta como el CG
real**. El valor `±0,039 m` es una variación de prueba, no un brazo instalado
verificado. Con `x_CG=0` y esos mismos parámetros, el resultado es 1,000 g con
brazo cero y 0,951 g con cada brazo de ±0,039 m, para ambas direcciones.

De los 400 problemas, 360 tienen solución en esta aproximación y 40 se informan
como inviables por el LP. La inviabilidad del poliedro interior por sí sola no
demuestra que el cono ideal continuo o la aeronave real sean inviables. El
resultado tampoco valida una orden de giro: faltan fuerzas, inercia y dinámica
de actuadores identificadas. La estimación ideal de desplazamiento del script
anterior supone inversión instantánea y no se interpreta como tiempo real.

## Verificación

El script base contrasta el límite `a/g=tan(35°)` con fuerza abundante y el
equilibrio vertical simétrico con CG desplazado. `verificar_brazo_vertical.py`
añade siete comprobaciones: simetría con CG y brazo nulos, coincidencia con el
LP anterior, reflexión de dirección/brazo, reflexión de CG y dirección,
reflexión del signo de alabeo, límite analítico de CG en el caso sin brazo y
límite de cono con fuerza abundante. Las siete pasan con
SciPy 1.13.1 y NumPy 2.0.2; el máximo residuo de igualdad reportado entre los
360 casos resueltos es aproximadamente `5,45×10⁻¹²` en sus unidades mixtas.
Los chequeos numéricos no validan los supuestos físicos.

El barrido guardado cubre solo `x_CG≥0` y momentos de alabeo 0 o +0,5 N·m;
las reflexiones opuestas se contrastan en pruebas puntuales, no en un barrido
completo de asimetrías de hardware. Los máximos en frontera no incluyen
reserva para una demanda adicional de aceleración o momento no especificada.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv-aero/bin/python \
  investigacion-aeronautica/ejecucion/G6/autoridad_C02/verificar_brazo_vertical.py
```

`RESULTADOS.json` conserva las fuerzas por módulo y huellas de configuración y
código. La siguiente dependencia es determinar CG, fuerza y momento efectivos
del módulo instalado, incluyendo sus límites y respuesta temporal, antes de
reutilizar estos valores en el 6DOF.

La [extensión vertical](INFORME-VERTICAL.md) añade aceleración vertical
prescrita y cuantifica la interacción entre sostén y fuerza horizontal en
560 escenarios ideales.
