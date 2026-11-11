# CAD con detalle de presentación

Variantes A (ventiladores internos), B (casetes retráctiles, dos estados) y C (conductos exteriores). Fuselaje de comparación: longitud 1400 mm, diámetro máximo 420 mm. STEP en milímetros. Renders Mitsuba CPU de los mismos sólidos; fuente paramétrica en `../cad_protegidos_detallados.py`.

## Detalles añadidos

Palas con torsión y secciones elípticas mediante loft CAD; motor con camisa, bandas y buje; eje; estatores de soporte; labios redondeados de conducto; rejillas anulares con barras; tornillos con alojamiento central; junta central; panel conformado de acceso y fijaciones. En A, tapas abatidas con bisagras, pasadores y nervios representativos. En B, mangas telescópicas, guías, carros, tapas y cierres. En C, sujeciones cortas con radios y fijaciones.

Los detalles son geometría sólida editable, no texturas añadidas para simular mecanismos inexistentes. Sus dimensiones y materiales visuales son representativos: no están seleccionados desde cargas, catálogo de piezas o procesos de fabricación. Los anillos de motor no representan un bobinado eléctrico dimensionado. El perfil elíptico de pala no constituye un perfil aerodinámico validado.

## Alcance

Acabado de producto para estudiar apariencia y alojamiento. NO es un diseño listo para fabricar ni una demostración de viabilidad de vuelo. La masa, potencia y control calculados anteriormente no se transfieren a estos conceptos. Las rejillas alteran el flujo y sus pérdidas no están calculadas. Falta control en seis grados de libertad/vectorización, instalación propulsiva de alta velocidad, sellos, cinemática continua, tolerancias, análisis estructural/térmico y cálculo de empuje de estos ventiladores. Las tapas de B requieren adaptarse al contorno curvo y resolver sus juntas. Los estados guardado y desplegado no demuestran una trayectoria libre de colisiones.

El registro `manifest.json` identifica cada STEP y número de piezas, y `verificacion_reimportacion.json` comprueba su relectura en el núcleo CAD. Esa validez geométrica no equivale a validez mecánica o de fabricación.

## Visualización final

Para evitar artefactos de sombreado, el render de la carcasa utiliza su cara exterior y materiales de doble cara. El STEP conserva el sólido completo. El panel de acceso se representa ligeramente elevado, con su cota superior en z=214 mm; no implica que exista un sello o una holgura de fabricación resuelta. Los renders finales son PNG de 2000 × 1350 píxeles. Los colores representan acabados propuestos, no materiales estructurales seleccionados.
