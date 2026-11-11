# Referencia experimental NASA: ventilador eléctrico en estático

## Resultado y decisión

El ventilador NASA es útil para contrastar procedimientos, pero **no cabe en
la reserva del candidato C02 y sus curvas no son un mapa del vehículo**. El
rotor ensayado tiene diámetro de pala 5,11 in = 129,79 mm y el motor tiene
un diámetro especificado de 56 mm y masa especificada de 1,1 kg. Las reservas
C02 de referencia son rotor nominal Ø82 mm y motor Ø21,8 × 16,1 mm. Cuatro
motores de la referencia NASA sumarían 4,4 kg por especificación, dejando
0,6 kg en una masa total hipotética de 5 kg para ventiladores, estructura,
energía, electrónica y demás. La diferencia de diámetro del rotor es un factor
1,58 y la relación de áreas circulares frontales es aproximadamente 2,51.
Esta comparación descarta la **sustitución directa en ese alojamiento**, no
otras tecnologías ni la viabilidad general de un vehículo de 5 kg.

Fuente primaria: [Weinstein y Simmons, NASA/AIAA SciTech 2024, NTRS
20230017299](https://ntrs.nasa.gov/citations/20230017299), tablas 1–2 y 14–15,
figura 14 y secciones V.A y VI.E. El artículo local es
`../../../fuentes/uiuc_propdb/NASA_EDF_20230017299.pdf`; su SHA-256 consta en
`RESULTADOS.json`. Dimensiones C02: [informe C02](../../G3/C02/INFORME-C02.md).

## Modelo de referencia y procedencia

NASA ensayó un Jetfan 130 Pro con diez palas y siete álabes fijos; los datos
de motor de la tabla 2 son atributos de hardware y no se presentan aquí como
pesaje propio. La tabla 6 informa los intervalos de los ensayos OFAT: velocidad
2.875–25.150 rpm, empuje estático 0–21,25 lbf y potencia 190–6.420 W. Son
**extremos separados**, no un par de empuje y potencia medidos simultáneamente.

Las ecuaciones 10–11 y tablas 14–15 dan ajustes para el ensayo DOE 2F sin
viento. En V.A se indica que las variables explicativas de la mayoría de los
modelos están centradas en sus medianas y en la tabla 7 se indica
`n_mediana = 285,94 rev/s` para el ensayo 116. Se interpreta aquí que ese
centrado se aplica a las ecuaciones 10–11. Esta interpretación es consistente
con la figura 14: en 17.156,4 rpm el ajuste da 9,806 lbf y 1,998 kW, acordes
con la escala de las curvas. La figura permite un control visual aproximado;
no sustituye puntos numéricos originales ni una confirmación independiente del
tratamiento de datos de los autores.

Con `d = rpm/60 − 285,94`, la reproducción usa:

```
T_lbf = 9,806 + 0,06922 d + 0,0001204 d²
P_kW  = 1,998 + 0,02040 d + 0,00007476 d² + 0,0000001119 d³
```

`T` se convierte usando 1 lbf = 4,4482216152605 N; `P` es el ajuste de potencia
eléctrica de CC suministrada en el ensayo. Se impuso de forma **provisional**
un intervalo exploratorio de 8.000–24.000 rpm, situado visualmente dentro de
las curvas de validación de la figura 14. No representa un dominio conjunto
DOE certificado: las relaciones entre tensión, mando, velocidad, temperatura y
límite de potencia no se han reconstruido. No se usa el modelo fuera de ese
intervalo. Ni la curva ajustada ni los puntos calculados son datos medidos
individualmente.

## Escenario ilustrativo de sustentación

Suposiciones: cuatro unidades NASA idénticas en aire quieto; reparto igual de
empuje vertical; gravedad 9,80665 m/s²; sin pérdidas de instalación,
inclinación, necesidad de control, reserva de empuje, otros consumos o
transición. Se invierte el ajuste solo dentro del intervalo exploratorio.
Estos valores comparan demanda ideal con el ajuste del banco; **no predicen
estacionario del C02 ni potencia de vuelo real**.

| Masa total supuesta | Empuje por unidad | Velocidad del ajuste | Potencia CC total del ajuste | Masa especificada de cuatro motores |
|---|---:|---:|---:|---:|
| 2 kg | 4,90 N | Fuera del intervalo exploratorio | No calculada | 4,4 kg |
| 5 kg | 12,26 N | 9.219 rpm | 1,39 kW | 4,4 kg |
| 10 kg | 24,52 N | 12.912 rpm | 3,56 kW | 4,4 kg |

Para 2 kg, los cuatro motores de referencia ya exceden la masa total supuesta;
además, el empuje por unidad está bajo el límite del intervalo adoptado. Para
5 kg, el valor 1,39 kW no contiene pérdidas de los conductos de C02 ni el
margen necesario para aceleración. La comparación a 10 kg tampoco incluye
masa ni potencia de los demás componentes. No se convierte ninguna de estas
cifras en una autonomía o una prestación del vehículo.

## Verificación y límites

`modelo.py` aplica unidades y rechazo explícito fuera del intervalo;
`generar.py` produce `RESULTADOS.json`. Cinco pruebas (`verificar.py`) cubren
el punto centrado, dos lecturas gráficas aproximadas, inversión, rechazo fuera
del intervalo y coherencia del presupuesto de masa. Una primera prueba usó
por error una lectura visual de 4,5 lbf a 10.000 rpm; se corrigió a una
comprobación **aproximada** de 3,3 ± 0,3 lbf al revisar la figura 14. No se
considera un punto experimental digitalizado. Antigravity reprodujo de forma
independiente el caso algebraico de 5 kg a partir de los coeficientes
suministrados; eso no es una segunda validación experimental.

No se han implementado los modelos con viento, sus dominios conjuntos ni los
mapas de fuerzas/momentos instalados. No se han medido C02/C07, ni se ha
probado su control, masa, temperatura o velocidad. No se reanudaron CFD.

```sh
python3 investigacion-aeronautica/ejecucion/G2/referencia_nasa_edf/verificar.py
python3 investigacion-aeronautica/ejecucion/G2/referencia_nasa_edf/generar.py
```
