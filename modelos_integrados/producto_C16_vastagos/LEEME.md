# C16: cribado local de vástagos para casquillos

Se examinaron vástagos cilíndricos conceptuales, de radio 0,75 mm y longitud 5 o 10 mm, conectados geométricamente a cada uno de los ocho casquillos de C15. Se probaron dos sentidos verticales: 32 alternativas en total. Cada vástago penetra intencionadamente el casquillo al menos 0,001 mm³ para representar una posible unión; no hay diseño de fijación, material, tolerancia o capacidad de carga.

Se comparó el volumen barrido del cilindro durante una elevación vertical ideal de 20 mm contra las cinco piezas locales fijas. Frente a las cuatro láminas en la elevación se comprobó la posición relativa cerrada, bajo elevación perfectamente sincronizada. Después se comprobó cada vástago elevado contra las cuatro láminas en giros conjuntos de 0°, 15°, 30°, 45° y 60°. Se contabilizan como intersecciones los volúmenes mayores que 0,001 mm³; el giro es muestreado, no continuo.

Los 32 vástagos tuvieron penetración intencionada con su casquillo y ninguno presentó intersecciones en las parejas examinadas durante la elevación ideal; 28 presentaron al menos una intersección en las posiciones de giro. Los cuatro que pasaron las comprobaciones locales corresponden a los dos casquillos de la **lámina 3**: dirección positiva para el casquillo 0 y negativa para el 1, ambas longitudes. Estos cuatro son candidatos geométricos, no soluciones funcionales. No se descartan otras rutas para las láminas 0–2.

`C16_vastagos_lamina3_local.step` muestra el subconjunto C15 en cerrado con dos vástagos de 5 mm de la lámina 3; contiene 23 objetos válidos reimportados. Los vástagos penetran los casquillos a propósito, pero no están conectados a un elevador o a la estructura. La forma de la lámina, la rotación de los casquillos frente a las láminas, la interacción entre vástagos, el rotor barrido, contacto tangencial, holguras y cargas no quedan validados. Se omiten el montaje global, siete tapas y la escala de 10 kg. No se valida ni aprueba este diseño para fabricación o vuelo.

`RESULTADOS.json` registra todos los casos, errores y huellas; `AUDITORIA.json` documenta la reimportación. El primer intento de exportar falló por una importación circular de dos módulos llamados `cribar`; se ajustó el exportador y la ejecución posterior terminó. El entorno CadQuery 2.8.0 está en `/private/tmp/codex-cad-runtime`, por lo que es temporal. No se reanudaron CFD pausados.

```sh
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C16_vastagos/cribar.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C16_vastagos/exportar.py
```
