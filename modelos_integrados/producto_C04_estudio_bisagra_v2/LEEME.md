# C04 v2 — estudio local de compuerta con guías

**Estado: propuesta geométrica rechazada para integración tal como está.** Es
un estudio CAD de la compuerta superior 0 del C03 de 5 kg objetivo. El resto
del vehículo y su conducto se ocultan para inspección. El rotor real sigue
dentro del cuerpo en la arquitectura seleccionada; la vista no representa una
hélice desplegable. Las piezas doradas y grises son reservas geométricas para
un posible mecanismo, no elementos seleccionados ni fabricables.

La candidata representa dos guías verticales, patines, puentes, cojinetes, un
pasador y dos brazos conceptuales junto con la compuerta, el aro y el rotor
procedentes del C03. No hay accionamiento, uniones al chasis, topes ni bloqueo
mecánico. Los brazos se solapan con la tapa: no se ha diseñado su unión. La
regla de dos movimientos heredada no demuestra que el mecanismo pueda
reproducirla bajo carga.

## Archivos

- `C04_cerrado.FCStd`, `C04_elevado.FCStd` y `C04_abierto.FCStd`: geometría
  editable de una compuerta y el estudio, con 14 objetos cada uno.
- Sus respectivos `.step`: intercambio; reimportación geométrica básica
  comprobada, equivalencia total no establecida.
- `C04_tres_estados.png`: vista comparativa generada desde las mallas de CAD.
- `RESULTADOS.json`: geometría fuente, huellas, distancias e intersecciones.
- `AUDITORIA_REIMPORTACION.json`: reapertura y comprobación de los tres pares.
- `../producto_C04_estudio_bisagra/`: primera propuesta, conservada.

## Resultados de cribado

Las tres posiciones estudiadas son cerrado, traslación exterior de 10 mm y
posterior giro de 110° alrededor del eje conceptual C03. Son **tres muestras
estáticas**, no un análisis continuo ni una animación dinámica. Se calculó
intersección booleana de cada pieza propuesta con el rotor, la carrocería
superior y la camisa del módulo 0. Se consideró significativa una intersección
mayor de 0,001 mm³. La inspección no abarca el resto de piezas, tolerancias o
deformaciones.

| Variante | Posición de guías en y | Cruces guía–carrocería | Cruces de otras piezas con los tres obstáculos, cerrado |
|---|---:|---:|---:|
| Primera | −128 mm | 2 en cada estado | 9 |
| v2 | −140 mm | 0 en los tres estados | 7 |

En v2 los siete cruces cerrados son con la carrocería superior: dos puentes,
dos cojinetes, pasador y dos brazos. El mayor volumen de intersección
individual es 27,294 mm³ en v1 y 27,227 mm³ en v2. En las posiciones elevada
y abierta de v2 no se detectaron intersecciones superiores al umbral para
estas parejas seleccionadas. Eso no implica holgura suficiente ni que la
trayectoria entre posiciones sea libre. Los anclajes tampoco se evaluaron
porque no están modelados.

Los tres FCStd se reabrieron y los STEP se reimportaron con 14 objetos válidos
cada uno. Su volumen agregado difiere alrededor de 0,00086 %: es una
comparación global orientativa, no demuestra equivalencia por pieza. El
resultado no corrige la discrepancia de intercambio previamente detectada en
C03. La masa de 5 kg es objetivo y no se han recalculado masas o inercias.
La variante de 10 kg requiere su propio diseño: no se ha producido por
escalado de estos componentes mecánicos.

## Reproducción

En macOS, desde la raíz del proyecto:

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C04_estudio_bisagra_v2/crear_C04.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C04_estudio_bisagra_v2/verificar_C04.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python investigacion-aeronautica/modelos_integrados/producto_C04_estudio_bisagra_v2/render_C04.py
```

**El generador sobrescribe archivos de esta carpeta.** Se usó Antigravity para
una revisión independiente conceptual; sus sugerencias no constituyen prueba.
Los scripts no reanudan casos CFD.
