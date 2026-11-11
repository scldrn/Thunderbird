# C03 — CAD conceptual de ventiladores internos

C03 reúne la candidata geométrica C02 de 5 kg con las posiciones conceptuales
de las ocho compuertas y genera también una variante de 10 kg por semejanza
geométrica. Conserva los cuatro rotores dentro de sus conductos, las aletas
posteriores y las reservas geométricas de equipos de C02. Los rotores no se
despliegan. La revisión no sustituye automáticamente la referencia A07.

## Archivos

| Variante | FreeCAD | STEP | Vistas |
|---|---|---|---|
| 5 kg, cerrado | `5kg/C03_5kg_cerrado.FCStd` | `5kg/C03_5kg_cerrado.step` | `5kg/C03_5kg_cerrado.png` |
| 5 kg, abierto | `5kg/C03_5kg_abierto.FCStd` | `5kg/C03_5kg_abierto.step` | `5kg/C03_5kg_abierto.png`, `5kg/C03_5kg_interior.png` |
| 10 kg, cerrado | `10kg/C03_10kg_cerrado.FCStd` | `10kg/C03_10kg_cerrado.step` | `10kg/C03_10kg_cerrado.png` |
| 10 kg, abierto | `10kg/C03_10kg_abierto.FCStd` | `10kg/C03_10kg_abierto.step` | `10kg/C03_10kg_abierto.png`, `10kg/C03_10kg_interior.png` |

Los archivos FCStd contienen sólidos importados organizados por pieza y son
editables como geometría. No reconstruyen un historial paramétrico de
fabricación. La vista interior oculta piezas para inspección; no es un corte
estructural ni una configuración de vuelo. Los materiales de los renders son
cosméticos y las imágenes proceden de las caras del CAD.

## Dimensiones aproximadas

Dimensiones exteriores estimadas a partir de la malla de presentación; incluyen
las aletas. La masa indicada es un **objetivo**, no una masa calculada o pesada.

| Estado | 5 kg: largo × ancho × alto | 10 kg: largo × ancho × alto |
|---|---:|---:|
| Cerrado | 1341 × 322 × 243 mm | 1690 × 405 × 306 mm |
| Abierto | 1341 × 403 × 299 mm | 1690 × 508 × 376 mm |

La referencia de 5 kg conserva rotor nominal Ø82 mm y conducto Ø84 mm; al
escalar geométricamente por 1,259921, la variante de 10 kg pasa a Ø103,3 y
Ø105,8 mm respectivamente. El escalado no selecciona componentes ni demuestra
que la variante pese 10 kg.

## Compuertas y alcance

La pose abierta aplica la regla heredada: traslación exterior de 10 mm en la
escala de 5 kg y giro de 110°; en 10 kg la traslación se escala a 12,6 mm.
Las tapas aparecen separadas en los renders porque aún **no hay bisagras,
guías, actuadores ni cierres diseñados**. Las posiciones son una propuesta para
estudiar el alojamiento, no un mecanismo funcional aprobado.

Cada ensamblaje se generó con 316 registros geométricos; la auditoría reimportó
los cuatro STEP y reabrió los cuatro FCStd. Los sólidos STEP importados fueron
válidos y las comprobaciones locales entre cada tapa y su rotor dieron volumen
de intersección cero. Las posiciones finales de las tapas y los centros de los
rotores concordaron con las transformaciones calculadas. Esto no comprueba el
recorrido continuo, tolerancias, cargas, rotor bajo deformación ni el resto de
posibles interferencias.

La primera comparación estricta entre STEP y FCStd señaló diferencias en
etiquetas automáticas de dos conjuntos de carrocería y en volúmenes de algunas
piezas, con un máximo relativo aproximado de 0,0335 % en una junta fina. El
fallo y las mediciones se conservan en `AUDITORIA.json` y `auditoria_r2.log`;
la equivalencia completa de intercambio no se considera demostrada por esa
auditoría. Un diagnóstico posterior emparejó los 316 registros de la variante
cerrada de 5 kg tras normalizar los nombres de las dos carrocerías. En tres
piezas seleccionadas, las restas booleanas en ambos sentidos tuvieron volumen
cero y los vértices muestreados tuvieron distancia cero según el kernel. Esta
comprobación parcial no demuestra equivalencia continua ni explica por sí sola
las diferencias de volumen. Véase `DIAGNOSTICO_INTERCAMBIO.json`. Usar FCStd
como referencia de esta entrega y revisar STEP antes de utilizarlo en otro
proceso.

No se han seleccionado motores, baterías, materiales o actuadores; tampoco se
han validado la masa, la potencia, las prestaciones o la resistencia. No se
reanudó ningún solver CFD histórico.

## Reproducción

En macOS, desde la raíz del proyecto, con FreeCAD instalado:

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C03/crear_C03.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C03/auditar_C03.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C03/regenerar_mallas_C03.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python investigacion-aeronautica/modelos_integrados/producto_C03/render_C03.py -- abierto
/Applications/Blender.app/Contents/MacOS/Blender --background --python investigacion-aeronautica/modelos_integrados/producto_C03/render_C03.py -- cerrado
```

El generador **sobrescribe los archivos generados de C03**; conservar copias
antes de regenerar. `MANIFIESTO.json` contiene las huellas de los CAD y la
fuente C02. `regenerar_mallas_C03.py` y `render_C03.py` preparan y renderizan
las vistas con FreeCAD y Blender, respectivamente.
