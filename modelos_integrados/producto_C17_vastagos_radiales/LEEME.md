# C17: vástagos radiales para las cuatro láminas

Se amplió el cribado C16 a ocho direcciones radiales de vástago por cada uno de los ocho casquillos C15. El radio supuesto es 0,75 mm y la longitud 5 mm. Cada vástago penetra intencionadamente su casquillo para representar una futura unión; eso no define cómo se fija ni prueba resistencia. Los ángulos se miden en el plano yz desde +y hacia +z.

Se probaron **64 candidatos**. Para cada uno se comprobó primero contra las cuatro láminas en cinco giros conjuntos de 0°, 15°, 30°, 45° y 60°, con elevación de 20 mm. Si encontraba una primera colisión se detenía ese candidato. Los restantes se cribaron contra las cinco piezas fijas locales en elevaciones de 0, 5, 10, 15 y 20 mm. Se asume que las láminas y vástagos se elevan juntos, sin movimiento relativo, y se usa un umbral de volumen de 0,001 mm³.

De los 64 candidatos, 24 pasaron y 40 se rechazaron por una primera intersección durante el giro; no se reportaron errores de booleanos. En cada uno de los ocho casquillos pasaron tres de las ocho direcciones. El registro guarda solo la primera colisión de los candidatos rechazados, no todas las posibles colisiones. Los recuentos son de las geometrías ensayadas, no de soluciones físicas posibles.

Se eligió la primera dirección aprobada de cada casquillo para formar `C17_candidata_local.step`: contiene las cinco piezas fijas, cuatro láminas recortadas, cuatro ejes, ocho casquillos y ocho vástagos. Se reimportaron **29 objetos válidos**. En cerrado se comprobaron los 28 pares de vástagos entre sí y otras 88 parejas vástago–eje o vástago–casquillo distinto del propio; no se detectaron intersecciones volumétricas superiores al umbral. El casquillo propio se excluye intencionadamente porque se ha previsto penetración para estudiar una unión.

Esta evidencia **no cierra el mecanismo**: la elevación y el giro son discretos; faltan barridos continuos, contacto tangente, tolerancias, rotor en rotación, interacción de casquillos con las láminas durante el giro, fijaciones, guías, un elevador común, accionamiento, sellos, cargas y fallos. El STEP corresponde a una sola tapa local de 5 kg y omite el resto del montaje. La posición abierta puede sobresalir del cuerpo; no se aprueba para vuelo rápido. Tampoco se verifica la versión de 10 kg. Las geometrías anteriores no se sustituyen.

`RESULTADOS.json` guarda cada candidato y su primera colisión; `AUDITORIA.json` registra las direcciones elegidas y `REVISION_CONJUNTO.json` las 88 parejas adicionales. Una sesión Antigravity `cf86cc2c` notificó un documento externo de revisión; no se incorporó como evidencia de estas comprobaciones. Se utilizó CadQuery 2.8.0 en `/private/tmp/codex-cad-runtime`, instalación temporal. No se reanudaron CFD pausados.

```sh
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C17_vastagos_radiales/cribar.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C17_vastagos_radiales/exportar.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C17_vastagos_radiales/verificar_conjunto.py
```
