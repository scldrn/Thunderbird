# C13: ejes de prueba y poses de una tapa C11

Este estudio local añade cuatro cilindros hipotéticos de radio 1 mm a las láminas de C11. Sus ejes se reconstruyen en el centro de y de cada lámina y a media altura de la intersección con una recta vertical en x=−160 mm, siguiendo el criterio geométrico descrito en el generador C11. La reconstrucción usa el STEP cerrado reducido, no se ha comparado con las coordenadas del informe C11 original y no demuestra identidad exacta de ejes ni uniones mecánicas.

Se muestrearon seis elevaciones de 0, 2, 5, 10, 15 y 20 mm sin giro y cuatro posiciones con elevación 20 mm y giro de 15°, 30°, 45° y 60°. Cada cilindro se comprueba contra las cinco piezas locales fijas, las otras tres láminas y los cilindros siguientes. Se excluye deliberadamente su propia lámina: la penetración de ese cilindro representa una unión todavía sin diseñar. El umbral de intersección volumétrica es 0,001 mm³.

| Poses | Resultado para los ejes de prueba |
|---|---|
| Elevación 0 mm | 10 pares con intersección detectada |
| Elevación 2 mm | 12 pares con intersección detectada |
| Elevaciones 5, 10, 15 y 20 mm, sin giro | 0 pares detectados en cada pose |
| Elevación 20 mm con giros 15°, 30°, 45° y 60° | 0 pares detectados en cada pose |

Se comprobaron 38 parejas por pose, 380 en total, usando cajas de cribado y booleanos. No hubo errores de booleanos en las parejas procesadas. El resultado a 5 mm **no** implica que el recorrido de 2 a 5 mm esté libre, ni que el mecanismo pueda salir de la posición cerrada. No se incluyen ejes, uniones o apoyos reales, juegos, contactos tangenciales, distancia mínima, deflexiones, sello, motores o cargas. El rotor se evalúa como la geometría fija del STEP, no como envolvente barrida en giro. Tampoco se revisan de nuevo entre sí las láminas y las piezas fijas; el estudio C11 anterior cubre solo sus propias poses y alcances.

El archivo `C13_abierto_local.step` contiene piel, camisa, rotor, aro, junta, cuatro láminas y cuatro cilindros en la última pose. Su reimportación confirmó 13 objetos con sólidos válidos y errores de posición de centro de lámina menores de 1e−4 mm respecto a la transformación aplicada. Eso no verifica coincidencia completa de formas, todas las colisiones ni movimiento continuo. La pose abierta puede sobresalir de la envolvente; no se aprueba para vuelo rápido. Se han omitido 311 registros del montaje completo, siete tapas y toda variante propia de 10 kg. El CAD no se promueve como mecanismo funcional.

`RESULTADOS.json` conserva los ejes, todas las colisiones, datos fuente y huella del código; `PARCIAL.json` conserva el último avance, y `AUDITORIA.json` la reimportación. Ambos scripts usan la instalación temporal CadQuery 2.8.0 de `/private/tmp/codex-cad-runtime`. La revisión de Antigravity `2a5e66af` fue conceptual, sin datos geométricos propios, y no sustituye las comprobaciones del CAD. No se reanudaron CFD pausados.

```sh
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C13_ejes_cinematicos/cribar.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C13_ejes_cinematicos/auditar.py
```
