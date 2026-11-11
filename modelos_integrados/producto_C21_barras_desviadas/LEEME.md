# C21: rutas desviadas alrededor de las láminas

Se ensayaron dos rutas compuestas por tres tramos rectos y dos nodos esféricos para cada una de las seis conexiones de C19. Las rutas se desvían hacia x=−215 o −105 mm y vuelven a los extremos de los vástagos seleccionados en C17. Los segmentos tienen radio 0,5 mm. Solo se estudia esa selección de orientaciones y la geometría local de una tapa de 5 kg; las conexiones por penetración geométrica no son un diseño de articulación.

Cada ruta se examinó contra las láminas en cinco ángulos de giro y, si no encontraba una intersección, contra cinco piezas fijas en cinco alturas de elevación. El umbral de volumen es 0,001 mm³; los candidatos se detienen en su primera colisión. De las 12 rutas, las seis de la fila de casquillos 0 pasaron esas pruebas individuales y las seis de la fila 1 encontraron una primera intersección con lámina o pieza fija. Esto no cubre movimiento continuo, contactos tangenciales, ejes/casquillos en esta primera fase o geometría de todo el vehículo.

Se eligió para la fila 0 la primera ruta aprobada en cada conexión y se revisaron **57 parejas** contra ejes, casquillos, otros vástagos y entre rutas, excluyendo las penetraciones previstas en sus vástagos de extremo y descontando el vástago compartido de las intersecciones entre rutas adyacentes. La revisión encontró **una intersección fuera del vástago compartido y un error de booleano** en otra pareja. La segunda fila tampoco tiene rutas aprobadas en este conjunto. Por tanto, **el conjunto ensayado queda rechazado**; no demuestra que toda combinación de rutas desviadas sea inviable.

`C21_rechazado_local.step` muestra la candidata parcial rechazada y se reimportó con 32 registros de geometría válidos. No es un elevador ni una arquitectura funcional. `RESULTADOS.json` conserva las pruebas individuales, `REVISION_CONJUNTO.json` la colisión y el error sin resolver, y `AUDITORIA.json` la reimportación. Faltan un análisis de otras combinaciones y uniones, guías, accionamiento, verificación de giro continuo, holguras, estructura, rotor en giro, montaje completo y 10 kg. No se reanudaron CFD pausados.

```sh
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C21_barras_desviadas/cribar.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C21_barras_desviadas/revisar_conjunto.py
```
