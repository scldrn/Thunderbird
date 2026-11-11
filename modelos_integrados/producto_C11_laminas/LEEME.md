# C11 — tapa segmentada en cuatro láminas

**Candidata geométrica para una sola tapa, no mecanismo funcional.** Se divide
la tapa superior 0 de C03 de 5 kg objetivo en cuatro sólidos y se examina su
giro alrededor de ejes ideales paralelos a x. Los rotores permanecen dentro
del cuerpo. No se han diseñado los ejes físicos, la elevación, la sincronización,
los actuadores, las fijaciones, los cierres o los sellos.

## CAD

- `C11_cerrado.FCStd` y `.step`: tapa dividida en cuatro láminas en posición
  cerrada, sobre la geometría local C03.
- `C11_elevado_60.FCStd` y `.step`: láminas desplazadas 20 mm en z y giradas
  60° sobre ejes ideales trasladados. Son poses, no un mecanismo animado.
- `C11_elevado_60.png`: render de mallas CAD con piel y camisa translúcidas
  y recortadas visualmente. En modo abierto las láminas sobresalen; no se ha
  evaluado su resistencia ni el límite de velocidad para abrirlas.

Ambos FCStd se reabrieron y los STEP se reimportaron con nueve objetos
geométricos válidos; se verificaron los centros de las láminas y que el centro
del rotor no se mueve (`AUDITORIA_CAD.json`). Esto no valida la equivalencia
STEP–FCStd completa ni el mecanismo.

## Geometría y comprobaciones

Se cortaron tres ranuras nominales de **0,3 mm** en la tapa original. La
suma de volúmenes de las láminas es aproximadamente 7.130,57 mm³, frente a
7.212,24 mm³ originales; la diferencia por las ranuras es unos 81,68 mm³,
según el kernel. Las ranuras requieren un diseño de cierre y sellado: la pose
cerrada no demuestra estanqueidad ni acabado aerodinámico adecuado.

Se ensayaron dos movimientos:

- **Giro sin elevación:** para ±15°, ±30°, ±45°, ±60°, ±75° y ±90° se
  detectaron intersecciones superiores a 0,001 mm³ en todos los ángulos. No se
  acepta esta disposición de ejes y láminas en su estado original.
- **Elevación y giro:** para la elevación vertical de 5, 10, 15 y 20 mm sin
  giro, y después para giros de 15°, 30°, 45°, 60°, 75° y 90° con elevación
  de 20 mm, no se detectaron intersecciones superiores a 0,001 mm³ en las
  parejas examinadas. Se cribaron **12.820 parejas** entre láminas, los 315
  registros restantes de C03 y cuatro cilindros nominales de rotor; 97 pares
  necesitaron booleanos, el resto se descartó por cajas disjuntas. No se
  comprobaron contactos tangenciales, holgura mínima, barrido continuo,
  ejes/soportes inexistentes, tolerancias ni deformaciones.

Los cilindros de rotor son los de C08, que contienen los rotores nominales
según el kernel; no incluyen vibración, excentricidad o deformación. El filtro
emplea `optimalBoundingBox` ampliadas 0,05 mm, y los resultados dependen del
kernel y de la geometría fuente. No se examinaron las otras siete tapas ni una
versión de 10 kg. Los informes están en `RESULTADOS.json`, `ELEVADAS.json` y
`ELEVACION_LINEAL.json`.

## Espacio proyectado y compromiso

A 60°, la proyección vertical de las láminas sobre el círculo nominal D84
cubre aproximadamente **21,16–21,41 %** en tres resoluciones de raster. Entre
los siete ángulos muestreados cada 15° fue la menor fracción en la resolución
intermedia; no es un óptimo continuo. En cerrado la cobertura proyectada es
aproximadamente 99,08–99,62 %, con sensibilidad a la resolución de los
huecos. Se usaron mallas CAD con teselación 0,4 mm y no se ha cuantificado su
error. Son áreas proyectadas: **no** son fuga, caudal, pérdida de presión,
empuje, eficiencia o resultados CFD.

La tapa deslizante C07 dejó libre esa proyección en el caso local comparado,
pero carece de unión mecánica viable. C11 también requiere elevación, ejes y
sellado, y cubre una parte de la proyección. No se selecciona una ganadora sin
resolver mecanismos, masa, cargas y flujo.

## Reproducción

Con FreeCAD y Blender, desde la raíz del proyecto, ejecutar en orden:

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C11_laminas/estudiar_laminas.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C11_laminas/estudiar_elevadas.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C11_laminas/estudiar_elevacion_lineal.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C11_laminas/crear_estudio.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C11_laminas/auditar_C11.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd investigacion-aeronautica/modelos_integrados/producto_C11_laminas/exportar_proyecciones.py
/Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C11_laminas/proyeccion.py
/Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C11_laminas/proyeccion_perfil.py
python3 investigacion-aeronautica/modelos_integrados/producto_C11_laminas/verificar.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python investigacion-aeronautica/modelos_integrados/producto_C11_laminas/render_C11.py
```

El rasterizador procede de C06 y sus cuatro pruebas analíticas pasan; las cuatro
pruebas de consistencia C11 también pasan. Los generadores sobrescriben
archivos. Comprobar los JSON y mensajes de fin, pues FreeCAD puede devolver
código 0 con una excepción. Se conserva `auditar_C11_error.log` del primer
intento y la auditoría corregida. No se reanudaron solvers CFD históricos.
