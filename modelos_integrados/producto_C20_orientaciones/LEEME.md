# C20: barras rectas con orientaciones alternativas

Se ensayaron las tres orientaciones de vástago que habían pasado C17 en cada casquillo, combinándolas dos a dos para cada una de las seis conexiones rectas de C19: **54 barras**. Cada barra de radio 0,5 mm debía alcanzar sus dos vástagos y, en las poses muestreadas, evitar láminas, piezas fijas locales, ejes y casquillos. El umbral de intersección es 0,001 mm³. Se rechaza cada candidato al encontrar su primera colisión, por lo que no se enumeran todas sus posibles interferencias.

Ninguna de las 54 barras pasó: 42 tuvieron su primera intersección a 60° y 12 a 0° en el orden de ensayo. No hubo errores booleanos. La comprobación de consistencia entre las tres conexiones de cada fila no encontró ningún recorrido de cuatro orientaciones que conectara la fila en esta malla. Esto descarta únicamente las barras rectas y orientaciones muestreadas; **no prueba que una ruta curva, desviada, articulada o con otra orientación sea imposible**. No se obtuvo un mecanismo funcional.

`RESULTADOS.json` conserva los candidatos y las primeras colisiones. Se usan las mismas hipótesis locales, movimiento sincronizado y limitaciones de C17 y C19; faltan el movimiento continuo, contactos tangenciales, la geometría completa, guías, accionamiento, cargas y 10 kg. No se reanudaron CFD pausados.

```sh
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C20_orientaciones/cribar.py
```
