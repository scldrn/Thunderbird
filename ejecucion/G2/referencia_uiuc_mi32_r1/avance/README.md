# Referencia experimental UIUC: hélice MI 3.2×2.2 en avance

La tabla procede de una hélice abierta UIUC girando a 20 051 rpm. No representa
el ventilador entubado C02. Para un diámetro nominal de 0,08128 m, el mayor
coeficiente de avance proporcionado, J = 0,448667, corresponde por cálculo a
unos 12,19 m/s (43,87 km/h). Este conjunto no fundamenta extrapolaciones a
600–1000 km/h. La densidad utilizada por el código es una hipótesis; empuje y
potencia dimensionalizados son cálculos y la potencia es de eje, no eléctrica.

Ejecuta `python3 procesar_uiuc_prop.py` para regenerar la tabla y
`python3 test_procesar_uiuc_prop.py` para comprobar el código. Se eliminaron
afirmaciones sobre daño estructural y porcentajes de incertidumbre no respaldados
por las fuentes suministradas, incluida una aserción basada en una incertidumbre
supuesta. El cambio no modifica las fórmulas ni los datos de entrada.

[UIUC Propeller Database, volumen 2](https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html).
