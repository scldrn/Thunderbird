# C19: barras rectas para sincronizar la elevación

Se examinaron seis barras rectas hipotéticas de diámetro 1 mm que conectan vástagos vecinos de la candidata C17: tres por cada fila de casquillos. Los extremos penetran intencionadamente los dos vástagos correspondientes, sin diseño de articulación o fijación. Se evaluó una sola combinación de direcciones de vástago, elegida en C17; el resultado no descarta otras rutas, formas o configuraciones.

Se comprobaron las barras contra las cinco piezas fijas locales en elevaciones de 0, 5, 10, 15 y 20 mm, y contra las cuatro láminas en giros sincronizados de 0°, 15°, 30°, 45° y 60° a elevación 20 mm. Se revisaron también, en cerrado, ejes, casquillos y vástagos distintos de los dos extremos previstos. El umbral de intersección es 0,001 mm³. **No son barridos continuos** ni se verificaron las barras entre sí o todo el montaje.

Las seis barras alcanzaron geométricamente sus dos vástagos previstos. No se detectaron intersecciones con las piezas fijas en las elevaciones muestreadas ni con los otros componentes revisados en cerrado. Sin embargo, **las seis interfirieron con láminas** en una o más poses de giro, por lo que esta disposición queda rechazada para integración:

| Fila de casquillos | Unión entre láminas | Longitud | Ángulos muestreados con intersección |
|---:|---|---:|---|
| 0 | 0–1 | 25,93 mm | 30°, 45°, 60° |
| 0 | 1–2 | 25,85 mm | 30°, 45°, 60° |
| 0 | 2–3 | 28,00 mm | 30°, 45°, 60° |
| 1 | 0–1 | 25,93 mm | 15°, 30°, 45°, 60° |
| 1 | 1–2 | 25,85 mm | 15°, 30°, 45°, 60° |
| 1 | 2–3 | 14,10 mm | 0° |

`C19_barra_rechazada.step` ilustra la primera barra en una pose con interferencia a 30°. Se reimportó con 30 objetos válidos; **es un ejemplo rechazado**, no un mecanismo ni una geometría aprobada. `RESULTADOS.json` documenta las colisiones, y `AUDITORIA.json` la reimportación. Una sesión Antigravity `97153ab2` notificó un documento externo de posibles opciones; no se incorporó como evidencia.

El siguiente estudio debe cambiar la ruta o la selección de vástagos y comprobar también los elementos de soporte, su trayectoria y su conexión a la estructura. Siguen pendientes actuador, sellos, cargas, rotor barrido, montaje completo y escala de 10 kg. No se reanudaron CFD pausados.

```sh
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C19_barras/cribar.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C19_barras/exportar_rechazo.py
```
