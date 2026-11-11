# C12: reservas geométricas de ejes para C11

Se creó un **estudio local de reservas**, no un mecanismo de apertura ni una modificación del CAD de referencia. Usa el STEP cerrado reducido de C11 (una tapa de cuatro láminas, piel, camisa, rotor, aro y junta). Los 311 registros restantes de C03 no están incluidos, tampoco uniones, cojinetes, actuadores, sellos ni otras tapas. La versión de 10 kg no se ha estudiado.

Se ensayaron cilindros rectos de radio 1 y 2 mm paralelos a x. Sus centros se definieron por el punto medio de las cajas de cada lámina y sus longitudes por la extensión en x de esa caja. **Estos ejes de prueba no son necesariamente los ejes de giro usados para generar C11** y atraviesan intencionadamente su propia lámina, que se excluye del cribado. Son solo una hipótesis para detectar interferencias; no demuestran sujeción ni transmisión de par. Se ensayaron dos posiciones independientes: cerrada y trasladada 20 mm en z. La posición elevada no comprueba que los ejes queden dentro de la envolvente exterior durante el vuelo.

| Elevación | Radio | Intersecciones superiores a 0,001 mm³ con las cinco piezas fijas o entre reservas | Errores booleanos |
|---:|---:|---:|---:|
| 0 mm | 1 mm | 12 pares | 0 |
| 0 mm | 2 mm | 16 pares | 0 |
| 20 mm | 1 mm | 0 pares | 0 |
| 20 mm | 2 mm | 0 pares | 0 |

En cerrado aparecen intersecciones con piel, camisa, aro o junta; los detalles y volúmenes están en `RESULTADOS.json`. Con las dos elevaciones de 20 mm no se detectaron intersecciones volumétricas contra esas cinco piezas o entre las reservas. No se examinaron las otras láminas en movimiento, el recorrido entre posiciones, contactos tangentes, distancias mínimas, tolerancias, sellos, cargas o el resto del vehículo. La posición elevada tampoco implica viabilidad mecánica. No se propone esta configuración para integración.

`C12_reservas_ejes_elevados.step` muestra la piel, camisa, rotor, aro, junta y las cuatro reservas de radio 1 mm en posición elevada. **No incluye las láminas**; no es un ensamblaje completo ni un CAD funcional. Se reimportó y se verificaron nueve objetos con sólidos válidos, registrado en `AUDITORIA.json`. El resultado no es una prueba de equivalencia dimensional completa ni de ausencia global de colisiones.

Se instaló CadQuery 2.8.0 en `/private/tmp/codex-cad-runtime`; la carpeta es temporal y no modifica el entorno anterior. FreeCAD desde línea de comandos devolvió error de características del procesador en esta sesión; no se concluye que la instalación gráfica esté dañada. Una sesión de Antigravity terminó sin respuesta útil, por lo que no se incorporaron conclusiones suyas.

```sh
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C12_ejes/cribar_ejes.py
PYTHONPATH=/private/tmp/codex-cad-runtime XDG_CACHE_HOME=/private/tmp/codex-cad-cache OPENBLAS_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/modelos_integrados/producto_C12_ejes/auditar.py
```

El siguiente estudio debe diseñar ejes y soportes coherentes con la cinemática real de las láminas, comprobar el barrido de todos los componentes y decidir cómo acomodar las interferencias en cerrado. No se reanudaron CFD pausados.
