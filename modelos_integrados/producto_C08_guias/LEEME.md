# C08 — reservas internas para guías de tapa

**Estudio exploratorio; mecanismo aún no integrado.** C08 busca espacio para
una guía de la tapa superior 0 del C07 de 5 kg objetivo. Los cilindros dorados
son **reservas de espacio**, no guías fabricadas. No incluyen fijaciones,
carros, uniones a la tapa, accionamiento, topes ni sellos. Las posiciones
abiertas siguen siendo poses; el rotor permanece dentro del cuerpo. La versión
de 10 kg necesita un diseño y una verificación propios.

## CAD e imagen

- `C08_alt_cerrado.FCStd` y `C08_alt_abierto.FCStd`: estudio local con piel,
  camisa, rotor, aro, junta, tapa y dos reservas a distintas alturas.
- `C08_alt_cerrado.step` y `C08_alt_abierto.step`: formatos de intercambio.
- `C08_alt_abierto.png`: render de inspección de las caras CAD; la piel y la
  camisa son semitransparentes y están recortadas visualmente. La perspectiva
  puede superponer visualmente una reserva y el conducto; no es una sección
  ni prueba de que estén conectadas.
- `C08_local_*`: comparación previa con ambas reservas a la misma altura.
- `GUIAS.json`, `GUIAS_MOVIMIENTO.json`, `COMPARACION_PARES.json` y
  `UNION_ALT.json`: resultados y alcance de los cribados.

## Cómo se buscaron las reservas

Se ensayaron 72 posiciones de una reserva cilíndrica paralela al eje del
vehículo, desde x=−280 hasta −120 mm. La longitud de 160 mm, el diámetro
nominal supuesto de 4 mm y 0,5 mm adicionales por lado son hipótesis de
cribado, no componentes seleccionados ni tolerancias aprobadas. Los centros se
muestrearon en nueve coordenadas y y ocho coordenadas z.

Para la posición cerrada se comprobaron hasta nueve rayos por posición de y
frente a piel y tapas para detectar techo y suelo sobre/bajo la reserva. De
las 72 posiciones, 41 pasaron esas muestras y ocho no presentaron contacto
ni intersección detectada frente a los 316 registros geométricos de C03 y
cuatro envolventes cilíndricas nominales de rotor. El cribado usa cajas óptimas
FreeCAD ampliadas 0,05 mm y booleanos para los pares cuyas cajas se solapan;
la comprobación de 821.443 vértices de malla dentro de las cajas es discreta,
no una prueba de superficie continua. Los rayos tampoco prueban que toda la
reserva esté contenida en la carcasa.

Las envolventes de rotor se construyeron a partir de las dimensiones nominales
de cada rotor y se comprobó que el volumen del sólido de rotor fuera de cada
cilindro es cero según el kernel. No incluyen excentricidad, flexión, holguras
reales o vibración; no sustituyen un análisis del rotor en operación.

Las ocho reservas que pasaron en cerrado se cribaron contra las ocho tapas en
seis posiciones simultáneas cada una: 384 parejas de reserva–tapa. Las cajas
no se solaparon en esas muestras. No se comprobó el movimiento continuo ni la
interacción de futuros carros o uniones.

## Comparación y conexión pendiente

Se formaron 15 pares de reservas de lados opuestos, incluidas alturas
diferentes. Se ordenaron por la mayor distancia mínima reserva–tapa entre
cerrado y abierto; en empate se minimizó la suma de las distancias en abierto.
La alternativa representada usa:

| Reserva | y | z | Distancia mínima a tapa cerrada | Distancia mínima a tapa abierta |
|---|---:|---:|---:|---:|
| Lado 0 | −130 mm | 25 mm | 45,22 mm | 55,09 mm |
| Lado 1 | −25 mm | 75 mm | 27,80 mm | 37,61 mm |

Son distancias entre geometrías de reserva y tapa, no longitud ni diseño de un
brazo real. Los dos cilindros están separados nominalmente unos 111,30 mm de
superficie a superficie. Las franjas de su proyección vertical quedan fuera
del círculo nominal D84 del módulo, pero eso no demuestra ausencia de pérdida
de flujo, en especial cuando se añadan conexiones y soportes.

Se ensayaron 36 enlaces rectos en cerrado para este par, con puntos de la malla
de la tapa. Ninguno evitó todos los obstáculos evaluados: 33 encontraron
primero la camisa, dos la piel y uno el aro. Este resultado se refiere solo a
las barras, puntos, radios y posición muestreados; **no demuestra que todo
mecanismo sea imposible**. Es necesario estudiar otra ruta, un paso sellado o
un diseño que modifique el conducto, y comprobar estructura y flujo antes de
seleccionar. La unión intencional con la tapa se representó por penetración
geométrica y no está diseñada como interfaz mecánica.

## Verificación y reproducción

Las dos posiciones de cada alternativa se reabrieron y sus STEP se
reimportaron con ocho objetos válidos. En la alternativa de distinta altura,
la tapa se trasladó como se esperaba y los centros de rotor y reservas no se
desplazaron (`AUDITORIA_CAD_ALT.json`). Esto no verifica la equivalencia total
STEP–FCStd ni la funcionalidad. `verificar_registros.py` pasa cuatro pruebas
de consistencia de entradas, selección, huellas y resultados, no pruebas de
vuelo.

Con FreeCAD y Blender instalados, desde la raíz del proyecto:

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C08_guias/cribar_guias.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C08_guias/auditar_guias_movimiento.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C08_guias/comparar_pares.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C08_guias/explorar_union_alt.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C08_guias/crear_estudio_alt.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C08_guias/auditar_estudio_alt.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C08_guias/verificar_cajas_optimas.py
python3 investigacion-aeronautica/modelos_integrados/producto_C08_guias/verificar_registros.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python investigacion-aeronautica/modelos_integrados/producto_C08_guias/render_C08_alt.py
```

Los generadores sobrescriben sus salidas. Comprobar los JSON y los marcadores de
fin en los logs: FreeCAD puede devolver código 0 ante un error de script. Una
sesión de Antigravity aportó opciones conceptuales; otra agotó el tiempo y
produjo una respuesta parcial. No se aceptaron sus cifras o afirmaciones de
viabilidad sin comprobar. No se reanudaron solvers CFD históricos.
