# C07 — vehículo conceptual con compuertas deslizantes

C07 es una **candidata geométrica**, derivada de C03, con cuatro rotores
internos fijos y ocho tapas en posición abierta deslizante. No sustituye la
referencia de investigación A07 ni acredita vuelo, estabilidad, potencia,
masa, velocidades o fabricación. No se han diseñado guías, actuadores,
soportes, cierres o sellos compatibles con esta apertura. Las tapas se ven
separadas porque solo se han representado sus poses geométricas.

## Archivos

| Objetivo de masa | FreeCAD abierto | STEP abierto | Vista desde el CAD |
|---|---|---|---|
| 5 kg | `5kg/C07_5kg_deslizante_abierto.FCStd` | `5kg/C07_5kg_deslizante_abierto.step` | `5kg/C07_5kg_abierto.png` |
| 10 kg | `10kg/C07_10kg_deslizante_abierto.FCStd` | `10kg/C07_10kg_deslizante_abierto.step` | `10kg/C07_10kg_abierto.png` |

Las posiciones cerradas corresponden a `../producto_C03/5kg/` y
`../producto_C03/10kg/`. Las vistas de inspección `C07_*_interior.png` ocultan
piezas; no son cortes estructurales ni condiciones de vuelo. Los renders usan
mallas de las caras CAD y materiales cosméticos. El objeto de 10 kg es una
**semejanza geométrica**, no una configuración de propulsión o masa validada.

## Movimiento propuesto

Para la referencia de 5 kg, cada compuerta se separa 10 mm hacia el exterior y
luego se desplaza 100 mm longitudinalmente, sin girar: las delanteras hacia la
nariz y las posteriores hacia la cola. En la escala geométrica de 10 kg los
desplazamientos son aproximadamente 12,60 y 125,99 mm. No se ha demostrado
que estas trayectorias puedan generarse con un mecanismo instalado ni que
puedan realizarse bajo cargas de aire.

C06 comparó una compuerta deslizante con una bisagra interior: en la
proyección vertical de la tapa sobre un círculo nominal D84, el caso
seleccionado deslizante mostró 0 % de cobertura en tres rasterizaciones y el
caso abatible mostró aproximadamente 13,17–13,36 %. Esta comparación describe
siluetas de mallas para un módulo; **no** es caudal ni pérdida aerodinámica.
Método, controles y límites: `../producto_C06_busqueda_eje/LEEME.md`.

## Comprobaciones efectuadas

- Las dos variantes abiertas se reabrieron como FCStd y sus STEP se
  reimportaron con 316 objetos válidos cada uno. Se verificaron las
  traslaciones de las ocho tapas y que los centros de los cuatro rotores no se
  desplazan. `AUDITORIA.json` conserva detalles y huellas. Esto no prueba la
  equivalencia STEP–FCStd completa; las diferencias anteriores de C03 siguen
  sin resolverse globalmente.
- Para 5 kg, `TRAYECTORIA.json` evalúa las ocho tapas a la vez en seis poses:
  elevación de 5 y 10 mm y desplazamiento de 25, 50, 75 y 100 mm. Se
  cribaron **1.416 parejas** contra las dos pieles, cuatro camisas, cuatro
  rotores, ocho aros, ocho juntas y las otras tapas. No hubo intersecciones
  mayores de 0,001 mm³ ni errores; 720 parejas necesitaron booleanos y las
  demás tenían cajas disjuntas. Son solo posiciones discretas y obstáculos
  seleccionados; no garantizan holgura ni ausencia de contactos intermedios.
- En la posición final de 5 kg, `POSICION_GLOBAL.json` cribó las ocho tapas
  contra los 308 registros restantes y entre sí: **2.492 parejas**, 20 con
  booleanos, sin intersecciones superiores a 0,001 mm³ ni errores. El filtro
  usó cajas `optimalBoundingBox` de FreeCAD ampliadas 0,05 mm. Como control,
  los 821.443 vértices de la malla derivada del mismo CAD quedaron dentro de
  esas cajas ampliadas (`AUDITORIA_CAJAS_OPTIMAS.json`). Es una verificación de
  teselación, no una prueba de que todas las superficies continuas estén
  contenidas ni del comportamiento bajo deformación.

No se han comprobado todas las 316 piezas en las posiciones intermedias, ni el
barrido continuo, holguras de fabricación, sellado, cargas, vibración,
aeroelasticidad, respuesta del ventilador ni obstrucción real del flujo. La
versión de 10 kg conserva semejanza geométrica, pero sus componentes, carga,
masa e inercias deben recalcularse y su mecanismo comprobarse por separado.

## Reproducción

Desde la raíz del proyecto, con FreeCAD y Blender instalados:

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C07_deslizante/crear_C07.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C07_deslizante/auditar_C07.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C07_deslizante/auditar_trayectoria.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C07_deslizante/auditar_posicion_global.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C07_deslizante/verificar_cajas_optimas.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python investigacion-aeronautica/modelos_integrados/producto_C07_deslizante/render_C07.py -- abierto
```

Los generadores sobrescriben sus archivos C07. Comprobar los JSON y mensajes
finales en los logs; FreeCAD puede terminar con código 0 cuando un script
falla. Los nombres PNG de la primera ejecución se corrigieron de C03 a C07
tras generar las imágenes; el script actual escribe los nombres C07. No se
reanudaron solvers CFD históricos.
