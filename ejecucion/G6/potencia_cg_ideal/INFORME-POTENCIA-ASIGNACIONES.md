# Potencia ideal asociada a las asignaciones de fuerza

Se calcularon referencias de potencia para los vectores guardados en `CONO_CONTINUO.json`. Se conservan únicamente las cajas que pasaron el límite hipotético de 21 N por módulo y la zona supuesta del equipo genérico. Para cada fuerza guardada se supone un disco libre independiente de diámetro 82 mm, orientado en la dirección de esa fuerza, aire de densidad 1,225 kg/m³ y estacionario ideal: `Pᵢ = |Fᵢ|^(3/2)/sqrt(2ρA)`. Es una comparación de cantidad de movimiento de discos libres, basada en la [teoría de NASA NDARC](https://ntrs.nasa.gov/citations/20170011656), no una potencia de los ventiladores entubados ni una cota universal de su consumo. No se incluye el flujo incidente del avance ni interacción entre discos.

Las fuerzas SOCP guardadas minimizan la mayor fuerza por módulo, **no** la suma de potencia; pueden existir otros repartos con distinta potencia. Para cada caja se informa la mayor potencia de los 64 repartos elegidos en sus esquinas, no una trayectoria, el óptimo energético, ni una medición. Por ello pequeñas diferencias entre configuraciones o ángulos no sirven para elegir un ganador.

| Reserva axial | Ángulo supuesto | Escenarios certificados evaluados | Mayor potencia ideal entre esquinas, por escenario |
|---:|---:|---:|---:|
| 38 mm | 35° / 45° | 5 / 5 | 2,411–2,418 kW / 2,459–2,465 kW |
| 60 mm | 35° / 45° | 5 / 5 | 2,412–2,413 kW / 2,480–2,484 kW |
| 80 mm | 35° / 45° | 5 / 5 | 2,432–2,433 kW / 2,564–2,580 kW |

Como sensibilidad aritmética, para el caso mayor de 80 mm y 45° se toma una demanda constante hipotética de 2,580 kW ideales, eficiencia global fija de 60 %, 150 Wh/kg útiles de batería y 5.000 W/kg de potencia del pack. Esos cuatro valores son supuestos, no ficha técnica ni validación. El cálculo da 4,300 kW eléctricos. Exigir simultáneamente los límites supuestos de energía y potencia produce:

| Duración de la carga supuesta | Energía eléctrica | Masa mínima por esas dos restricciones supuestas |
|---:|---:|---:|
| 30 s | 35,8 Wh | 0,86 kg |
| 120 s | 143,3 Wh | 0,96 kg |
| 300 s | 358,4 Wh | 2,39 kg |

Estas duraciones son **ensayos de carga constante**, no una misión ni una trayectoria: mantener una aceleración y un momento de esquina durante todo ese tiempo no equivale a mantener estacionario. La masa no incluye otros equipos, conectores, refrigeración, pérdidas transitorias, reserva ni degradación. Tampoco demuestra que la batería quepa o pueda entregar simultáneamente la densidad energética y potencia supuestas. La masa calculada es un mínimo solo dentro de esa hipótesis de pack; no es un límite de todas las tecnologías ni valida un vehículo de 5 kg.

`POTENCIA_FUERZAS_SOCP.json` contiene resultados por esquina, huellas del archivo de fuerzas y código, y los escenarios de batería. Cuatro pruebas de fórmula, escala y unidades pasan:

```sh
python3 investigacion-aeronautica/ejecucion/G6/potencia_cg_ideal/verificar_potencia_socp.py
python3 investigacion-aeronautica/ejecucion/G6/potencia_cg_ideal/potencia_fuerzas_socp.py
```

El siguiente cierre requiere optimizar fuerza y potencia conjuntamente con un mapa instalado y una trayectoria realista, y sumar el consumo de avance, la transición y los márgenes del presupuesto de masa. No se reanudaron CFD pausados.
