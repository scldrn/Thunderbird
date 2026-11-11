# Referencia experimental UIUC: hélice MI 3.2×2.2 en estático

Esta carpeta reproduce datos de una **hélice abierta**, no del ventilador interno
C02. El archivo original UIUC contiene 18 puntos con RPM, coeficiente de empuje
`CT` y coeficiente de potencia `CP`. La geometría de referencia tiene diámetro
nominal 3,2 pulgadas (0,08128 m).

Con la **densidad supuesta** ρ = 1,225 kg/m³, el último punto del archivo
(19 923,333 rpm, CT = 0,125828 y CP = 0,059879) proporciona por cálculo
aproximadamente 0,74177 N y 9,5271 W **en el eje**. Esas magnitudes
dimensionalizadas no son mediciones eléctricas ni parámetros del vehículo. El
rango medido del archivo no permite validar extrapolaciones fuera de él.

## Reproducir

```sh
python3 analizar.py
python3 test_analizar.py
```

`analizar.py` reconstruye `puntos.csv`. El registro de una revisión separada en
sandbox contiene 18 pruebas satisfactorias y una reconstrucción de tabla; la
sesión también registró un error posterior de shell y quedó marcada para
revisión. Las pruebas comprueban cálculo y software, no validez física de C02.

Fuentes: [UIUC Propeller Database, volumen 2](https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html) y [Deters y Selig, AIAA 2008, figura 38](https://m-selig.ae.illinois.edu/pubs/DetersSelig-2008-AIAA-2008-6246-MicroProps.pdf).
