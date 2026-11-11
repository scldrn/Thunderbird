# Aceleración rectilínea ideal: 2, 5 y 10 kg

Este cribado compara distancias, energía cinética y potencia útil en 24
escenarios. No calcula la capacidad del C03 ni reemplaza los presupuestos de
hardware o las configuraciones propias de cada masa.

## Supuestos

Masa constante; partida desde reposo; movimiento horizontal rectilíneo y
aceleración constante de 0,5, 1, 2 o 5 veces 9,80665 m/s²; velocidades finales
de 600 o 1000 km/h. Se omiten arrastre, viento, sustentación, estacionario,
transición, frenado y reservas. Las fórmulas cinemáticas y de fuerza siguen las
[ecuaciones de movimiento de NASA](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/excess-thrust-thrust-drag/);
la [energía cinética](https://www.grc.nasa.gov/www/k-12/BGA/Mike/energy_act.htm)
es `m·V²/2`.

La potencia útil final `m·a·V` es trabajo sobre la traslación por unidad de
tiempo, no potencia de eje ni potencia eléctrica. En este modelo ideal sube
linealmente desde cero; esto **no representa la potencia estática de un
propulsor real**. Tampoco se sostiene que 2 g constantes sean alcanzables.

Para un ejemplo eléctrico se suponen simultáneamente eficiencia constante de
0,70, energía útil de pack de 150 Wh/kg y potencia específica de pack de
5000 W/kg. Son hipótesis ilustrativas, no especificaciones de una batería. La
masa de batería indicada es el máximo entre las masas calculadas por energía y
por potencia para esa fase, sin verificar duración del pico ni consumo adicional.

## Ejemplo calculado: aceleración longitudinal constante de 2 g

| Velocidad | Masa objetivo | Tiempo | Distancia | Energía cinética | Potencia útil final | Batería hipotética |
|---:|---:|---:|---:|---:|---:|---:|
| 600 km/h | 2 kg | 8,50 s | 708 m | 7,72 Wh | 6,54 kW | 1,87 kg |
| 600 km/h | 5 kg | 8,50 s | 708 m | 19,29 Wh | 16,34 kW | 4,67 kg |
| 600 km/h | 10 kg | 8,50 s | 708 m | 38,58 Wh | 32,69 kW | 9,34 kg |
| 1000 km/h | 2 kg | 14,16 s | 1967 m | 21,43 Wh | 10,90 kW | 3,11 kg |
| 1000 km/h | 5 kg | 14,16 s | 1967 m | 53,58 Wh | 27,24 kW | 7,78 kg |
| 1000 km/h | 10 kg | 14,16 s | 1967 m | 107,17 Wh | 54,48 kW | 15,57 kg |

Para la batería y eficiencia **supuestas**, el caso de 1000 km/h ya excede la
masa total objetivo antes de contar otros componentes. Esto descarta esa
combinación de supuestos, no todas las baterías, propulsores o trayectorias.
Una aceleración menor reduce el pico de potencia, pero aumenta el tiempo y la
distancia; la energía cinética final ideal es independiente de la aceleración.

## Reproducción y verificación

`ESCENARIOS.csv` contiene los 24 casos y `HIPOTESIS.json` sus parámetros. Desde
la raíz del proyecto:

```sh
python3 investigacion-aeronautica/ejecucion/G1/aceleracion_ideal_2_5_10/calcular.py
python3 investigacion-aeronautica/ejecucion/G1/aceleracion_ideal_2_5_10/verificar.py
```

Cuatro pruebas verifican cinemática, trabajo, unidades, escalado y rechazo de
entradas inválidas. Una revisión independiente de Antigravity contrastó las
ecuaciones y el caso de 5 kg, 1000 km/h y 2 g. Ninguna de estas comprobaciones
constituye una prueba de vuelo ni una selección de batería.
