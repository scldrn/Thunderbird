# C02 de 5 kg: sensibilidad a potencia simultánea en avance

**7 de noviembre de 2026, hora de Bogotá.** Se amplía el cribado eléctrico
[anterior](../decision_integrada_c02/INFORME.md) con una potencia eléctrica
adicional, constante y supuesta durante la aceleración y el crucero. Esta carga
puede representar una combinación de sustentación, control y servicios que
funcione simultáneamente con el propulsor axial. **No se conoce su valor real**:
la sustentación aerodinámica, la respuesta de los ventiladores y la transición
no están identificadas. Una potencia igual a la de estacionario en todo el
avance es solo un escenario, no una cota física ni una predicción.

## Modelo y supuestos

Se conserva la candidata C02 de 5 kg como caso de estudio: 30 s de estacionario
incluyen 3 s de maniobra lateral, seguidos por aceleración rectilínea uniforme y
30 s de crucero. Se mantienen las potencias exploratorias C01 de 2.968,81 W y
3.505,89 W para esas dos partes iniciales; no son mapas instalados de C02. Los
arrastres finales de 0, 10, 25 y 50 N, la eficiencia axial de 0,70 y el pack con
150 Wh/kg útiles y 5.000 W/kg son valores **supuestos simultáneamente**, no
componentes identificados.

La aceleración se busca entre 10–60 s o 10–180 s para minimizar la mayor de las
dos masas de batería exigidas por energía y potencia. Se añade una carga de 0,
1.000 o 2.968,81 W durante **toda** la aceleración y los 30 s de crucero. Se
suponen dos presupuestos geométricos parciales y, por separado, 0 o 0,5 kg de
hardware adicional aún no identificado. El caso de 0 kg es intencionalmente
optimista bajo estas hipótesis; las masas geométricas no son pesajes ni cotas
inferiores demostradas.

Para una velocidad final `V`, tiempo de aceleración `t`, arrastre final `D`,
eficiencia `η` y apoyo `P_aux`, se prescribe `D(v)=D(v/V)²`. El trabajo axial
es `½mV² + DVt/4 + DV·30`; se divide por `η`. El pico eléctrico supuesto es el
mayor entre la potencia inicial de maniobra y `(mV²/t + DV)/η + P_aux`. Se suma
`P_aux·(t+30)` a la energía eléctrica. El cálculo usa [energía cinética](https://www.grc.nasa.gov/www/k-12/BGA/Mike/energy_act.htm)
y [potencia mecánica](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/power/);
la ley de arrastre, misión y eficiencia son supuestos de este cribado.

La eficiencia axial constante hasta velocidad cero es una simplificación
limitante: el modelo asigna potencia axial instantánea cero en reposo aunque un
propulsor real que genere empuje estático necesite potencia. Tampoco se ha
validado que el coeficiente de arrastre permanezca constante hasta 1.000 km/h;
la dependencia con Mach, Reynolds e instalación puede cambiar el trabajo.
Por ello estas cifras no son un consumo real ni una cota universal.

## Ejemplo: 50 N supuestos a velocidad final

Se usa la hipótesis geométrica ligera de 2,04584 kg, reserva de 0,75 kg y
**ninguna masa adicional conocida**. Así quedan 2,20416 kg hipotéticos para
batería. Dentro del intervalo de 10–60 s, los seis casos siguientes seleccionan
60 s; la aceleración recorre 5,00 km a 600 km/h y 8,33 km a 1.000 km/h.

| Objetivo | Apoyo adicional supuesto | Pico de batería | Energía de misión | Batería exigida por el modelo | Saldo frente a 2,204 kg |
|---:|---:|---:|---:|---:|---:|
| 600 km/h | 0 W | 15,21 kW | 201,55 Wh | 3,04 kg | −0,84 kg |
| 600 km/h | 1.000 W | 16,21 kW | 226,55 Wh | 3,24 kg | −1,04 kg |
| 600 km/h | 2.968,81 W | 18,18 kW | 275,77 Wh | 3,64 kg | −1,43 kg |
| 1.000 km/h | 0 W | 29,03 kW | 349,75 Wh | 5,81 kg | −3,60 kg |
| 1.000 km/h | 1.000 W | 30,03 kW | 374,75 Wh | 6,01 kg | −3,80 kg |
| 1.000 km/h | 2.968,81 W | 32,00 kW | 423,97 Wh | 6,40 kg | −4,20 kg |

En estos seis ejemplos manda la potencia específica de batería supuesta; un
saldo negativo significa que **esa combinación de hipótesis** no cierra. No
permite descartar todos los sistemas eléctricos, híbridos, otras geometrías o
misiones. Además, exigir durante 60 s la potencia específica supuesta puede ser
incompatible con una batería concreta; eso no se ha establecido aquí.

## Umbral condicional de arrastre

La tabla calcula el mayor arrastre final compatible simultáneamente con los
límites hipotéticos de energía y potencia, variando el tiempo de aceleración de
10 a 60 s. Se asigna todo el remanente ligero a batería: no quedan asignados
motores, electrónica, cableado ni refrigeración pendientes.

| Velocidad | Apoyo 0 W | Apoyo 1.000 W | Apoyo 2.968,81 W |
|---:|---:|---:|---:|
| 600 km/h | 32,40 N | 28,20 N | 19,93 N |
| 1.000 km/h | 4,62 N | 2,10 N | Ningún arrastre ≥ 0 cumple |

Si se reserva además **0,5 kg supuesto** para hardware adicional, los
umbrales a 600 km/h bajan a 21,90, 17,70 y 9,43 N, respectivamente; en los
tres escenarios de 1.000 km/h ni siquiera D=0 cumple bajo el límite de 60 s.
Una aceleración de hasta 180 s modifica los resultados y exige distancias
mucho mayores: los 48 umbrales están en `RESULTADOS_r2.json`. No son predicciones
del arrastre C02 ni justifican tomar una decisión final de arquitectura.

## Verificación y límites

Se generaron **192 escenarios y 48 umbrales**. `verificar_r2.py` contiene siete
comprobaciones: reproduce el ejemplo anterior sin apoyo, verifica energía y
potencia añadidas, contrasta energía cinética y pico sin arrastre, compara la
optimización con un barrido denso y comprueba la raíz del umbral y un caso
inviable incluso con arrastre cero; también comprueba el inicio de la meseta de
potencia. Reproducir desde la raíz:

```sh
python3 investigacion-aeronautica/ejecucion/G1/potencia_simultanea_c02/verificar_r2.py
```

`calcular_r2.py` no sobrescribe `ESCENARIOS_r2.csv` ni `RESULTADOS_r2.json`;
registra huellas de las fuentes y del código. La primera versión se conserva:
su selección no identificaba el **primer** tiempo en una meseta de masa mínima.
La comparación de 192 filas muestra 20 tiempos corregidos, sin cambio en las
masas mínimas ni en los 48 umbrales; para 600 km/h y arrastre/apoyo cero, el
primer tiempo de la meseta es 56,59 s, no 180 s. Los seis ejemplos de 50 N de
esta nota no cambian. La verificación matemática no valida el
modelo de planta, las características simultáneas del pack ni el vehículo. No
se han modelado frenado, ascenso, virajes, transición, temperatura, límites de
voltaje/corriente, vida del pack ni masas de todos los equipos. Para las
versiones de 2 y 10 kg se necesitan sus propias geometrías, presupuestos y
mapas; no se ha trasladado automáticamente la candidata de 5 kg.
