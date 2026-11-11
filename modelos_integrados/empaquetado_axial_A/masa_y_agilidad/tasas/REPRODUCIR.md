# Reproducir límites de tasa y dinámica rígida ideal

Desde la raíz del proyecto, con los escenarios de masa y geometrías previamente generados:

```sh
.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/asignacion_tasas_A.py
.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/verificar_tasas_A.py
```

El primer programa resuelve conjuntamente fuerzas en todos los nodos con restricciones de cambio por componente. Solo se conserva como seleccionada la primera duración de la malla que pasa 41 y 81 nodos para cada caso; no representa un mínimo global. El segundo reabre los datos, verifica límites de fuerza y cambio, calcula el máximo continuo de velocidad de dirección para cada segmento lineal e integra el cuerpo rígido con cuaternión.

Los perfiles se identifican por la reserva axial, el parámetro S, la duración y el número de nodos. El NPZ original contiene fuerzas y demandas; el archivo terminado en `_forward.npz` contiene los estados integrados. Los equilibrios analíticos de prueba y el refinamiento numérico no validan un motor, servo o flujo real.

Las fuerzas interpoladas son continuas y cumplen las cotas convexas entre nodos. La demanda no lineal de movimiento solo se aproxima; las desviaciones se informan. Las pendientes de fuerza pueden saltar. No se imponen aceleración de álabe, segunda derivada de fuerza, potencia, interacción de chorros o respuesta de planta, ni correcciones de perturbación con restricciones temporales conjuntas.
