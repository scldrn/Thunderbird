# C18: interacción casquillo–lámina y pose abierta local

Se revisó una parte pendiente de C17: los ocho casquillos frente a las cuatro láminas recortadas, con elevación ideal común de 20 mm y giros sincronizados de 0°, 15°, 30°, 45° y 60°. Se comprobaron 160 parejas; no se detectaron intersecciones volumétricas superiores a 0,001 mm³ ni errores booleanos. El resto de las interacciones del conjunto no se recalculó aquí y las posiciones entre esos ángulos no se cubren por muestreo.

Para cada uno de los ocho pares de casquillo y **su propia lámina** se verificó además el recorte cilíndrico nominal de C15: el volumen del casquillo fuera del cilindro de recorte y el volumen de lámina dentro de él fueron cero según el kernel. El cilindro de recorte es coaxial con el giro y, como superficie de revolución ideal, es invariante ante cualquier ángulo; por ello, si se mantienen exactamente esas condiciones geométricas, el casquillo permanece dentro del espacio recortado durante el giro de su propia lámina. Se comprobó además una rotación representativa del cilindro: la diferencia de volumen calculada fue cero. Esto es un razonamiento sobre la geometría nominal, no una validación de fabricación, de holguras bajo deformación, de otras láminas o de todo el mecanismo.

`C18_abierto_local.step` muestra la última pose: cinco piezas locales fijas, cuatro láminas recortadas giradas, cuatro ejes, ocho casquillos y ocho vástagos elevados. Se reimportó con 29 objetos válidos; la auditoría verificó que los centros de piezas fijas no se movieran y que ejes, casquillos y vástagos se trasladaran 20 mm. No se verificó equivalencia completa de STEP ni posiciones de centros de lámina en esa auditoría. La pose abierta puede sobresalir y no se aprueba para vuelo rápido.

`RESULTADOS.json` contiene las 160 parejas, `ALOJAMIENTOS.json` la comprobación de recortes propios y `AUDITORIA.json` la reimportación. La revisión conceptual Antigravity `ee92fb55` coincidió en la importancia de coaxialidad e invariancia; las conclusiones aquí se basan en geometría y comprobaciones locales.

Siguen faltando la conexión de los vástagos a una estructura y a un elevador, la trayectoria continua de esas conexiones, tolerancias, interferencias en el montaje completo, el rotor en giro, cargas, accionamiento y sellos. Se trata de una sola tapa local de 5 kg, no de un producto o mecanismo funcional ni de una verificación de 10 kg. No se reanudaron CFD pausados.

```sh
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C18_revision_giro/revisar.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C18_revision_giro/auditar.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C18_revision_giro/verificar_alojamientos.py
```
