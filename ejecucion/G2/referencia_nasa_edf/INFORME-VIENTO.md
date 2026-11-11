# Referencia NASA EDF con viento: dominio y reproducción tentativa

## Resultado principal

El ensayo **DOE 3F** de la referencia NASA cubrió presiones dinámicas de
0,25–6 psf, incidencia 0–30°, tensión 75 V y mando PWM 1.350–1.765 μs
([tabla 4, informe NASA](https://ntrs.nasa.gov/citations/20230017299)). Con
densidad **supuesta** de 1,225 kg/m³, 6 psf equivalen a unos 287,3 Pa y a
77,97 km/h de velocidad uniforme. En la misma atmósfera supuesta, una
corriente libre de 600 km/h tiene q≈17,01 kPa (355 psf), y a 1.000 km/h
q≈47,26 kPa (987 psf): aproximadamente 59 y 165 veces el máximo de q de ese
ensayo, respectivamente. Son comparaciones de **corriente libre**, no fuerzas
del vehículo.

No debe alimentarse el ajuste del ventilador aislado con esas presiones
externas y presentarlo como rendimiento a alta velocidad. El flujo en un
conducto instalado puede diferir de la corriente libre; incluso si su estado
local cae en límites parecidos, sería necesario comprobar la geometría, las
condiciones conjuntas y la interacción con el vehículo.

## Ajustes y alcance

El artículo da el coeficiente de empuje `CT = T/(rho n² D⁴)`, la razón de
avance `J = V/(nD)`, sus componentes `Jx = J cos(i)` y `Jz = J sin(i)`, y
`Mtip = pi n D/a` (ecuaciones 1–3). Para el modelo 3F de empuje, las
constantes están en la tabla 16 y la estructura en la ecuación 13; para la
potencia eléctrica CC están en la tabla 18 y la ecuación 15. La tabla 8
proporciona medianas `Jx=0,313`, `Jz=0,074`, `J=0,324` y `Mtip=0,374`.

`modelo_viento.py` reproduce **tentativamente** ambos polinomios con variables
centradas en esas medianas, interpretando la descripción general de V.A. El
cálculo coincide cualitativamente con las escalas de las figuras 15–16, pero
no se ha contrastado con los puntos digitales originales ni confirmado el
centrado con los autores. Las medianas se calculan por variable: el conjunto de
sus cuatro valores no debe presentarse como una observación física simultánea.
La evaluación calcula `J`, `Jx` y `Jz` desde una misma velocidad e incidencia.

El informe NASA publica métricas para los conjuntos de modelado y validación
3F; no se trasladan como incertidumbre a otros puntos, a C02, ni al vehículo.
El motor, rotor, conducto, estatores e instalación de NASA no son los de C02.
La fuerza axial del modelo tampoco es un mapa completo de seis componentes.

## Ejemplo sintético y controles

Con q=3 psf, incidencia 15°, 15.000 rpm, 75 V, densidad supuesta
1,225 kg/m³ y velocidad del sonido supuesta 340,3 m/s, el cálculo produce
V≈15,31 m/s, J≈0,472, Mtip≈0,300, CT≈1,098, empuje axial≈23,86 N y
potencia CC≈1,31 kW. **Este punto es sintético:** no se conoce si esa
combinación fue ensayada, ni su PWM, ni su incertidumbre. Son salidas de una
interpretación tentativa del ajuste, no mediciones ni prestaciones de C02.

El código rechaza presiones e incidencias fuera de los límites de factores
DOE 3F, tensiones diferentes de 75 V, atmósferas no físicas y velocidades de
rotación fuera de la ventana numérica provisional 8.000–24.000 rpm heredada
del cribado estático. Esa ventana no es un dominio validado del DOE 3F. Pasar
las comprobaciones individuales **no demuestra cobertura conjunta** de q,
incidencia, PWM, velocidad, temperatura y potencia. Toda salida lleva la
etiqueta `EXPLORATORIO_COBERTURA_CONJUNTA_NO_DEMOSTRADA`; no se conecta al
simulador de vuelo.

Cuatro pruebas en `verificar_viento.py` comprueban interceptos algebraicos,
consistencia de J, q y unidades, rechazos y rechazo de las corrientes libres
de 600 y 1.000 km/h bajo las hipótesis indicadas. `RESULTADOS_VIENTO.json`
registra entradas, resultados sintéticos, rechazos y huella SHA-256 del PDF.
Son pruebas de software y cálculos dimensionales, no validación experimental
del modelo ni del vehículo. No se reanudaron CFD históricos.

```sh
python3 investigacion-aeronautica/ejecucion/G2/referencia_nasa_edf/verificar_viento.py
python3 investigacion-aeronautica/ejecucion/G2/referencia_nasa_edf/generar_viento.py
```
