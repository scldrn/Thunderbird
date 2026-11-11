# C05 — estudio del alojamiento de una compuerta

**Decisión: no integrar esta solución.** El estudio aborda la compuerta
superior 0 del C03 de 5 kg objetivo y la propuesta de guías de C04 v2. El
recorte propuesto elimina cruces de mecanismo con la piel en las posiciones
muestreadas, pero crea fragmentos en la carrocería y los brazos siguen
atravesando el aro y la junta. No hay accionador, sellado, anclajes, estructura
o mecanismo físico aprobados. No representa todavía la versión de 10 kg.

## Inspección del CAD

- `C05_contexto_cerrado.FCStd` y `.step`: carrocería superior recortada, junta,
  aro, compuerta, rotor y el conjunto mecánico propuesto, **16 objetos**. Es
  una visualización de la propuesta rechazada, no un vehículo completo.
- `C05_alojamiento_estudio.FCStd` y `.step`: piel recortada, material retirado,
  conjunto de cajas de reserva y elementos de referencia. Estos objetos se
  superponen deliberadamente para revisión; no se deben sumar como masa.
- `C05_inspeccion.png`: piel recortada y compuerta semitransparentes, zona
  local recortada para que se vea el mecanismo. Los dos puntos rojos son
  **marcadores ampliados**, situados cerca de las intersecciones reales; su
  tamaño no representa el volumen de colisión. El rotor permanece interno.
- `RESULTADOS.json`, `ARO_Y_JUNTA.json`, `AUDITORIA_C05.json`,
  `AUDITORIA_CONTEXTO.json`, `AUDITORIA_CAJAS_CAD.json` y
  `EXPLORACION_BRAZOS_V2.json`: mediciones y alcance de cada verificación.

## Método y resultados

El programa calcula para cada pieza de la propuesta C04 v2 una caja
conservadora de su movimiento secuencial ideal: traslación de 0 a 10 mm y,
para los brazos, giro de 0 a 110° alrededor del eje trasladado. Para el giro
se calculan extremos trigonométricos sobre las esquinas de la caja envolvente
inicial de cada sólido, y se amplía cada dirección 0,5 mm **como hipótesis de
estudio**, no como tolerancia de fabricación aprobada. La unión de esas cajas
se resta de la piel superior de C03. Las cajas pueden ocupar espacio que la
pieza real nunca ocupa; su intersección con otro objeto no demuestra por sí
sola una colisión física de la pieza.

En el modelo de piel, la intersección con la unión de cajas da unos **357,14
mm³** retirados. El volumen por diferencia de ambos sólidos es de unos 357,22
mm³: existe una discrepancia numérica de aproximadamente 0,079 mm³ entre
ambas operaciones booleanas, pendiente de investigar. El sólido fuente agrupa
cuatro componentes; tras el recorte se obtienen seis, incluidos dos fragmentos
de aproximadamente 4,60 y 0,97 mm³. La conectividad del CAD empeora; esto no
es por sí solo un cálculo de resistencia ni una medición física.

Las cajas también se intersecan con aro, junta y compuerta cerrada. Para
separar conservadurismo de colisión real se evaluaron los **sólidos reales**
de mecanismo contra aro y junta en tres posiciones. En cerrado, cada uno de
los dos brazos intersecta ambos; los cuatro volúmenes individuales son unos
3,289 y 3,611 mm³ contra aro, y 0,728 y 0,932 mm³ contra junta. En las
posiciones elevada y abierta no se detectó intersección de los elementos del
mecanismo con esos dos obstáculos. Tres posiciones no validan el recorrido.

En 11 posiciones de las dos fases se evaluaron 11 piezas propuestas contra
piel recortada, camisa y rotor. No hubo intersecciones superiores a
0,001 mm³ en esas parejas; la menor distancia a la piel recortada muestreada
fue 0,5 mm. Esto no abarca otros componentes, juego, deformación o cargas.
Las cajas son envolventes analíticas conservadoras para la trayectoria rígida
ideal asumida y las cajas iniciales del kernel; las 11 muestras no demuestran
por sí mismas continuidad, ni se ha certificado numéricamente el booleano o
la estanqueidad completa.

Se probaron **19 barras rectas** adicionales en cerrado con puntos candidatos
muestreados en la malla de la tapa. Ninguna de las 19 estuvo libre de todas
las interferencias comprobadas con aro, junta, piel recortada, camisa y rotor.
Es un cribado limitado de barras rectas y ejes elegidos: no demuestra que no
exista otro mecanismo viable. Deben estudiarse una interfaz y una ubicación
del pivote diferentes, no generalizar el resultado a todas las puertas.

## Verificación y reproducción

Se reabrieron los dos FCStd y reimportaron sus dos STEP: 6 y 16 objetos
respectivamente, todos geométricamente válidos según el kernel. Esto no prueba
identidad geométrica completa entre formatos. Cuatro pruebas independientes de
la función de envolvente pasan; 36.212 vértices de teselación de las 121
combinaciones pieza–posición muestreadas quedan dentro de sus cajas. Esa
verificación es discreta y no valida tolerancias, cargas ni montaje real.

Desde la raíz del proyecto, con FreeCAD y Blender instalados:

```sh
python3 investigacion-aeronautica/modelos_integrados/producto_C05_alojamiento/verificar_envolvente.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C05_alojamiento/estudiar_recorte.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C05_alojamiento/auditar_aro_junta.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C05_alojamiento/crear_contexto.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C05_alojamiento/auditar_C05.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C05_alojamiento/auditar_contexto.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C05_alojamiento/verificar_cajas_CAD.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C05_alojamiento/explorar_brazos_v2.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C05_alojamiento/exportar_vista.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python investigacion-aeronautica/modelos_integrados/producto_C05_alojamiento/render_C05.py
```

Los generadores sobrescriben resultados de esta carpeta. Comprobar los JSON y
marcadores de fin en los logs: en este entorno FreeCAD puede terminar con código
0 aun cuando un script falle. Se conservó `exportar_vista_error.log` de un
primer intento y se corrigió el manejo de geometría compuesta. La revisión
conceptual de dos sesiones de Antigravity contribuyó a identificar controles;
no se adoptaron sus tolerancias numéricas sin datos. No se reanudaron CFD
históricos ni se modificaron C03 o A07.
