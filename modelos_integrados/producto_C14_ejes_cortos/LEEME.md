# C14: segmentos cortos de eje y barrido de elevación

Se ensayó una alternativa local a los ejes largos de C13: cilindros de prueba de **10 mm de longitud y 1 mm de radio**, centrados en siete posiciones longitudinales para cada una de las cuatro láminas. Son reservas geométricas, no ejes instalados ni bisagras. Se usa el STEP local reducido de C11 y los ejes reconstruidos por C13, sin confirmar su identidad con las coordenadas originales de C11.

Para cada cilindro se construyó su volumen barrido geométrico durante una traslación vertical ideal continua de 0 a 20 mm. El sólido se forma con los cilindros en ambos extremos y un prisma intermedio; su volumen se compara con `L·(πr²+2rh)`. Se contrasta contra las cinco piezas fijas locales. Frente a las otras láminas se comprueba la posición relativa cerrada, que permanece constante durante la traslación **solo bajo la hipótesis de que las cuatro se elevan exactamente juntas**. La lámina propia se excluye intencionadamente: falta diseñar la unión. No se incluyen los 311 registros ausentes del montaje, holguras, contacto tangente, deformaciones ni envolvente del rotor en giro.

| Lámina | Posiciones que pasaron el barrido local | Posiciones ensayadas |
|---:|---:|---:|
| 0 | 5 | 7 |
| 1 | 7 | 7 |
| 2 | 7 | 7 |
| 3 | 5 | 7 |

Los centros x ensayados fueron −190, −180, −170, −160, −150, −140 y −130 mm. Para cada lámina se seleccionó **solo como ejemplo de estudio** el segmento centrado en x=−160 mm, que pasó el barrido local. A continuación se comprobaron esos cuatro cilindros contra las otras láminas en cinco giros simultáneos de 0°, 15°, 30°, 45° y 60° con elevación 20 mm: no se detectaron intersecciones de volumen superiores a 0,001 mm³ ni errores booleanos en esas parejas. No se ha comprobado el giro continuo ni la colisión entre todos los demás componentes. Las piezas y su elevación pueden sobresalir del cuerpo; no se aprueba esa pose para vuelo rápido.

Se generaron `C14_cerrado_local.step` y `C14_abierto_local.step`, cada uno con las cinco piezas locales de referencia, cuatro láminas y cuatro segmentos. Ambos se reimportaron con 13 objetos válidos. Tres pruebas del sólido de barrido verificaron volumen, varias posiciones interiores y un punto exterior. `RESULTADOS.json`, `POSES.json` y `AUDITORIA.json` conservan datos y huellas. La revisión conceptual Antigravity `73fe1753` corroboró la fórmula de volumen; sus recomendaciones de tolerancias no se adoptan como especificación.

**No hay todavía un mecanismo funcional.** Un segmento alojado dentro de la lámina necesita apoyos, acoplamiento, transmisión y una forma de elevarse; ninguno está diseñado ni comprobado. Tampoco se demuestra que existan soportes sin interferencia, que el sistema resista cargas o que funcione para las demás tapas y la versión de 10 kg. La solución no sustituye la arquitectura ni el CAD de referencia. Se usa CadQuery 2.8.0 instalado temporalmente en `/private/tmp/codex-cad-runtime`. No se reanudaron CFD pausados.

```sh
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C14_ejes_cortos/verificar.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C14_ejes_cortos/barrido.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C14_ejes_cortos/crear_poses.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C14_ejes_cortos/auditar.py
```
