# Etapa 2 — control simultáneo y cribado de masa

## Resultado y alcance

Se ejecutaron SciPy/NumPy para estudiar una familia explícita de ocho fuerzas bidireccionales. El algoritmo construye la región convexa completa de fuerzas y momentos permitida por los límites individuales. La autoridad estática se verifica mediante programación lineal independiente; NO se deduce sumando motores ni mirando únicamente el rango de una matriz.

No es una validación del dibujo: la disposición matemática introduce ejes específicos que el dibujo nunca definió. Falta verificar interferencias, flujos y montaje físico. Una solución de fuerzas no prueba viabilidad de aeronave.

## Geometría de actuadores

Ocho centros en (±0.2L, ±r/√2, ±r/√2). Ejes unitarios n=(c1 sy sz, c2 sx sz, c3 sx sy), con c unitario optimizado. Es una familia propuesta aquí, no una reproducción certificada del Omnicopter. Se incluye fuerza y r×f. El cálculo principal usa torque aerodinámico de reacción cero: hipótesis de cancelación o despreciabilidad, no validada. La función permite un coeficiente de reacción, pero su sensibilidad sigue pendiente.

Matriz normalizada B=[n; (r×n)/L]. Fuerzas individuales fi∈[-T,T]. Se enumeran normales de faceta a partir de combinaciones de cinco generadores independientes. Para cada normal n se impone |n·w|≤T sum_i|n·Bi|. Este procedimiento representa el zonotopo completo cuando B tiene rango 6. La esfera de fuerza con reserva es la mayor que cabe simultáneamente con una esfera de momentos de radio tau. Gravedad en cualquier orientación resta mg a la fuerza isotrópica disponible.

La reserva se define como 2 rad/s² multiplicados por la mayor inercia principal, válida como reserva angular conservadora en reposo, NO para rotaciones rápidas con términos giroscópicos. El optimizador diferencial busca mejores ejes dentro de límites; no prueba optimalidad global. Se mantiene semilla 42.

## Verificación realizada

Caso 10 kg, r=2D: 150 pares de fuerzas y momentos aleatorios dentro de la región garantizada, todos factibles por programación lineal; residuo máximo 4.3e-14. Punto de faceta límite confirmado por LP independiente; un punto 0.001 N más allá se rechaza. Esto verifica el cálculo estático del modelo ideal, no la física de rotores ni la construcción.

## Ejemplo cuantitativo

Con suma de límites de empuje igual a 6 pesos (588.4 N), r=2D y 10 kg, el modelo encuentra una esfera de fuerza de 218.4 N con reserva de momento de 2.107 Nm. Equivale a una garantía estática ideal de 1.227 g de aceleración neta en cualquier dirección y orientación desde reposo.

Manteniendo esos ejes, para garantizar 1 g se necesitan aproximadamente 66.63 N por rotor, suma 533.0 N o 5.435 pesos. Son requisitos del candidato, no especificaciones de hardware seleccionado.

El barrido de despliegue no es monótono. Cada radio vuelve a optimizar los ejes. No puede interpretarse como una única máquina que cambia continuamente de radio sin cambiar ejes. Hay radios pequeños incompatibles con rotores finitos; son controles matemáticos, no propuestas mecánicas.

## Cribado energético y de masa

52 asignaciones de mínimo coste sum |fi|^1.5 (26 direcciones, dos niveles de fuerza) se resolvieron con SLSQP y límites individuales. Es una función convexa para discos aislados iguales, sin interacción. La máxima potencia es el máximo de las direcciones muestreadas: NO una cota superior continua.

Se aplican 648 combinaciones de sensibilidad de diámetro, eficiencia efectiva, relación empuje/masa de motores, masa auxiliar, tiempo eléctrico y potencia específica de batería. No son 648 diseños físicos.

Ejemplo: rotor Ø25 cm, eficiencia efectiva 0.65, 200 Wh/kg utilizables, 4 kW/kg de batería, reactor 2.155 kg, 2 kg asignados a otros sistemas, relación empuje/masa motores 111.6 N/kg. Esta última se calcula con 8×6.25 N / 0.448 kg de la tabla del Omnicopter; extrapolarla no demuestra que exista un motor de ese tamaño con esas prestaciones ni que sirva para paso variable.

Resultado condicionado: motores/rotores 4.776 kg, potencia hover muestreada 3.98 kW, potencia durante aceleración desde reposo muestreada 11.25 kW, batería limitada por potencia a 2.812 kg. Suma antes de combustible 11.743 kg. Este escenario no cumple 10 kg aun reduciendo la duración eléctrica a 30 segundos.

No prueba imposibilidad universal. La masa de módulos resultante contradice la hipótesis anterior de 20 % para las inercias. El siguiente cálculo debe iterar masa y tensor real antes de afirmar una configuración coherente. Tampoco se incluyen pérdidas de descarga dependientes de estado de carga, refrigeración, reserva ni volumen de repliegue.

El cociente de combustible sobrante y consumo máximo P250 es un presupuesto temporal al máximo consumo; NO duración a 1000 km/h. Faltan empuje instalado frente a Mach y arrastre total.

## Fuentes de entradas, revisadas 2026-10-29

- Tabla I, parámetros de motores y límites: https://brescianini.info/wp-content/uploads/publications/breMECH18.pdf
- Masa de reactor y consumo: https://www.jetcat.de/en/productdetails/produkte/jetcat/produkte/Professionell/p250%20pro%20s%20v2
- Advertencia sobre modelar conjuntamente energía y potencia de batería: https://ntrs.nasa.gov/citations/20240007599

## Reproducir

Desde la raíz del proyecto:

```
.venv/bin/python legacy/scripts/control.py
.venv/bin/python legacy/scripts/energia_control.py
```

Salidas principales: control_estatico_ESCENARIOS.csv, verificacion_control.json, configuracion_control_HIPOTESIS.json, masa_energia_10kg_CONDICIONAL.csv y gráficos PNG.

## Próximas verificaciones necesarias

Cerrar iterativamente masa-inercia-potencia; incluir torque de reacción; comparar familias de actuadores; integrar dinámica 6DOF y retardos; comprobar espacio de rotores y repliegue; completar aerodinámica y estructura. El objetivo general permanece activo.
