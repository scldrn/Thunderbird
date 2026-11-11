# C15: casquillos y recortes conceptuales

Este estudio añade dos casquillos anulares hipotéticos a cada segmento de eje corto de C14, más recortes locales en las cuatro láminas. Es una investigación geométrica de una tapa de 5 kg, no un mecanismo montado ni una selección de componentes.

Cada eje sigue siendo un cilindro supuesto de radio 1 mm y longitud 10 mm. Los casquillos tienen radio interior 1,1 mm, exterior 2 mm y ancho 2 mm; los recortes correspondientes en la lámina tienen radio 2,2 mm y longitud 2,1 mm. Las diferencias de radios son **holguras geométricas de escenario**, no tolerancias de fabricación, diseño de cojinete o garantías de funcionamiento. Se eliminó material solo donde están los casquillos; el eje conserva una penetración geométrica intencionada con el centro de la lámina, de aproximadamente 11,24 mm³ por lámina. No se ha diseñado cómo fijarlo ni transmitir el par.

En el STEP local cerrado, las cuatro láminas siguen teniendo un sólido válido cada una tras los recortes. La reducción es aproximadamente 18,25 mm³ por lámina; esto **no demuestra resistencia, rigidez, espesor mínimo ni vida a fatiga**. Se comprobaron los ocho casquillos contra los ejes y sus láminas recortadas: no se detectaron solapes volumétricos superiores a 0,001 mm³ en esas parejas.

Se evaluó el volumen barrido de la envolvente exterior de cada casquillo durante la elevación vertical ideal de 20 mm frente a la piel, camisa, rotor estático, aro y junta locales. Frente a las otras láminas se usó su posición relativa cerrada bajo la hipótesis de elevación sincronizada. No se detectaron intersecciones superiores a 0,001 mm³ ni errores booleanos en las parejas examinadas. **No se ha comprobado la rotación de estos casquillos frente a láminas, el barrido completo de láminas y apoyos, holgura de contacto, ni la envolvente del rotor en movimiento.** No se incluyen las 311 piezas omitidas del montaje completo, siete tapas ni variante de 10 kg.

`C15_apoyos_conceptuales.step` incluye cinco piezas de referencia, cuatro láminas recortadas, cuatro ejes y ocho casquillos. Se reimportó con 21 objetos válidos y se revisaron las ocho parejas de holguras descritas en `AUDITORIA.json`. El CAD carece de soportes que conecten los casquillos con la estructura, mecanismo de elevación, accionamiento, topes, sellos, seguridad ante fallo y fijación de ejes. Por ello **no se aprueba ni integra como mecanismo funcional**. La siguiente tarea es buscar rutas para soportes y verificar su trayectoria sin cortar el conducto o colisionar con el rotor, después validar estructura y cargas.

`RESULTADOS.json` conserva los datos, dimensiones, huellas y colisiones por lámina. Se utilizó CadQuery 2.8.0 temporal en `/private/tmp/codex-cad-runtime`; no se modificaron CAD anteriores ni se reanudaron CFD pausados.

```sh
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C15_apoyos/concepto.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C15_apoyos/auditar.py
```
