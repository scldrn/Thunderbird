# C02 de 5 kg: decisión integrada de masa y misión eléctrica

4 de noviembre de 2026. **Resultado:** las combinaciones eléctricas ilustradas abajo no caben en el presupuesto de masa supuesto. Esto no demuestra que C02 o un vehículo híbrido sean imposibles: las características de batería, arrastre, potencia de los ventiladores y masa siguen sin verificarse. La prioridad inmediata es medir o justificar esos cuatro datos, no seleccionar un motor definitivo.

## Base y contabilidad

La candidata C02 tiene masa objetivo de **5 kg**, cuatro módulos internos D82 y un corredor axial reservado; no hay propulsor de avance instalado ni masa final cerrada. En la [auditoría C02](../../G3/C02/INFORME-C02.md), la suma geométrica parcial asignada es 2,04584 kg con densidades ligeras o 2,78399 kg en la hipótesis mixta. Son supuestos sobre sólidos nominales, no cotas inferiores ni mediciones. Con la reserva de masa provisional del 15 % (0,75 kg), quedan respectivamente **2,20416 y 1,46601 kg** para batería y todo el hardware no identificado. Los 54 registros desconocidos no se declaran de masa cero.

Los cuatro conjuntos de geometría de rotor y cubo ya aparecen en la suma C02: **no se añade de nuevo la masa de rotores de C01**. El motor anular, partes de apoyos y accionamientos, corredor axial y equipos siguen como reservas o elementos no identificados. La suma nominal puede contener encuentros geométricos no resueltos; no es una lista de fabricación aprobada.

## Misión y supuestos, no prestaciones

Se estudian 144 combinaciones **totalmente eléctricas hipotéticas**, sin preseleccionar una batería. Se usan simultáneamente 150 Wh/kg útiles y 5.000 W/kg de pack, y 70 % de eficiencia global del sistema de avance: valores de escenario, no fichas de un producto. Se supone motor eléctrico separado para el avance y batería compartida. No incluye masa de ese motor ni de otros componentes desconocidos.

- 30 o 120 s de estacionario, que incluyen 3 s de una demanda lateral de 0,5 g con actitud fija. Se reutilizan como **demandas C01 no validadas** 2.968,81 W en estacionario y 3.505,89 W en el tramo lateral, tomadas de [C01](../../G2/INFORME-C01.md). No son potencia instalada de C02 ni demuestran control.
- Aceleración recta uniforme durante 10, 30 o 60 s desde reposo a 600 o 1.000 km/h, seguida de 30 o 120 s a velocidad constante. Las fases son secuenciales; se omiten transición, cambios de altura, giro, frenado y recuperación de energía.
- Arrastre a velocidad final de 25, 50 o 100 N **supuesto para sensibilidad**. Durante la aceleración se supone `D(v)=D_final·(v/V)²`. Ninguno de esos valores es una predicción de arrastre de C02; tampoco se han incluido el equilibrio aerodinámico, elevación, toberas, tomas o pérdidas adicionales.

Para evitar contar dos veces la aceleración, se suma una vez `½mV²` a los trabajos de arrastre. Se usa `P = F·V` y se divide el trabajo mecánico de avance por la eficiencia supuesta. [NASA Glenn: potencia](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/power/); [NASA: energía cinética](https://www.grc.nasa.gov/www/k-12/BGA/Mike/energy_act.htm). La masa de batería del cribado es el mayor de `energía necesaria / energía específica` y `potencia pico / potencia específica`; no incluye degradación térmica, caída de voltaje ni duración admisible de pico.

## Ejemplo con arrastre final supuesto de 50 N

Los resultados siguientes usan 30 s de estacionario incluyendo la maniobra de 3 s, más la aceleración indicada y **30 s adicionales** de avance a velocidad constante. La última columna utiliza la hipótesis de masa ligera y resta batería y reserva; todavía debe cubrir **todo** el hardware desconocido.

| Velocidad | Tiempo de aceleración | Energía eléctrica total | Pico eléctrico | Batería mínima por hipótesis | Saldo para hardware desconocido |
|---:|---:|---:|---:|---:|---:|
| 600 km/h | 10 s | 160,22 Wh | 31,75 kW | 6,35 kg | −4,14 kg |
| 600 km/h | 30 s | 176,75 Wh | 18,52 kW | 3,70 kg | −1,50 kg |
| 600 km/h | 60 s | 201,55 Wh | 15,21 kW | 3,04 kg | −0,84 kg |
| 1.000 km/h | 10 s | 280,86 Wh | 74,96 kW | 14,99 kg | −12,79 kg |
| 1.000 km/h | 30 s | 308,42 Wh | 38,21 kW | 7,64 kg | −5,44 kg |
| 1.000 km/h | 60 s | 349,75 Wh | 29,03 kW | 5,81 kg | −3,60 kg |

Alargar la aceleración baja el pico inercial, pero incrementa el tiempo y trabajo contra el arrastre. La aceleración uniforme de 60 s a 600 km/h recorre 5 km antes del tramo rápido constante; a 1.000 km/h recorre 8,33 km. Son consecuencias del escenario idealizado, no un plan de operación.

La energía cinética sola de 5 kg es **19,29 Wh a 600 km/h** y **53,58 Wh a 1.000 km/h**, antes de pérdidas y resistencia. Para evaluar versiones 2 y 10 kg esos valores se escalan por masa, pero la forma, área de rotor, batería y estructura requieren configuraciones propias.

## Condición necesaria de potencia bajo esas hipótesis

Si se asignara *todo* el saldo de masa de la hipótesis ligera a la batería y se supusiera que los componentes restantes no pesan nada —límite deliberadamente optimista—, la potencia de pack de 5 kW/kg solo permitiría los siguientes máximos de arrastre a velocidad final. Son límites aritméticos del escenario eléctrico, **no mediciones del vehículo**; cualquier masa adicional real los reduce.

| Objetivo | 10 s de aceleración | 30 s | 60 s | Solo crucero, sin aceleración |
|---|---:|---:|---:|---:|
| 600 km/h | Ningún D≥0 cumple | 18,51 N | 32,40 N | 46,29 N |
| 1.000 km/h | Ningún D≥0 cumple | Ningún D≥0 cumple | 4,62 N | 27,77 N |

Estos límites solo controlan potencia; también hay que cumplir energía, temperatura, geometría, empuje, control y masa. En la hipótesis mixta, los límites de crucero bajan a 30,79 N y 18,47 N, respectivamente. El modelo no contempla una turbina con combustible separado ni un sistema híbrido; ninguno queda seleccionado o validado.

## Qué decisión permite hoy

1. **No comprometer el producto con un sistema eléctrico único de estas características**: los ejemplos no cierran y la potencia específica del pack es solo una hipótesis.
2. Medir o calcular con trazabilidad el arrastre instalado de C02 a 600 km/h, la masa y entrega de potencia de baterías reales, y la curva completa del sistema de empuje interno. Priorizar una comparación coherente entre eléctrico y alternativas con combustible o híbridas, incluyendo masa de motor, combustible, depósitos, refrigeración y transición.
3. Mantener los objetivos de 600–1.000 km/h y movimientos abruptos como objetivos abiertos. Una simulación de control puede desarrollarse con estos escenarios, pero no representa vuelo predictivo sin una planta identificada y un tensor de inercia cerrado.

`calcular.py` incluye comprobaciones analíticas de unidades y trabajo, y genera `ESCENARIOS.csv` y `METODO.json`. Estos 144 casos son un cribado para decidir qué datos buscar, no 144 validaciones. Los archivos `_r1` conservan la primera emisión antes de añadir los límites analíticos de potencia.
