# A05 — Obsidian / X-Control

Ensamble CAD conceptual integrado con cuatro aletas posteriores móviles en X, a 45°, 135°, 225° y 315° alrededor del eje longitudinal. Conserva la envolvente y los mecanismos internos A04. Escalas geométricas de masa objetivo 2, 5 y 10 kg; masa real sin cerrar.

## Archivos
Cada escala incluye STEP neutro, STEP con controles en pose ±15°, STEP de inspección y STL exterior. STEP contiene 208 piezas válidas reimportadas. El render procede de los STEP; no se utilizó generación de imágenes. Código editable CadQuery y base A04 incluidos.

## Geometría de referencia 5 kg
Cada aleta: cuerda raíz 155 mm; cuerda punta 95 mm; longitud radial expuesta 70 mm; espesor máximo raíz 6 mm y punta 3 mm. Tres secciones hexagonales de doble cuña, loft reglado. Estas proporciones son hipótesis de diseño, no una optimización aerodinámica.
Eje radial situado en x=555 mm; aleta entre radios 100 y 170 mm. Eje de 5 mm de diámetro; agujero de 5,6 mm. Cojinete representativo de diámetro exterior 11,6 mm, longitud 7 mm. Reserva de actuador 24×22×10 mm. Carenado de raíz adaptado por sustracción de la envolvente exterior. No existe selección de actuador ni comprobación de par; acoplamiento directo representativo.

## Verificación y límites
Se comprobaron sólidos válidos y reapertura de todos los STEP. Se muestrearon nueve posiciones de cada aleta entre −20° y +20°, sin intersección volumétrica con el cuerpo de referencia ni con su propio carenado. Esto no constituye barrido continuo, análisis de tolerancias o verificación completa de interferencias. La pose ±15° es demostrativa, no una orden de maniobra validada.

Los carenados requieren definir sus anclajes, refuerzos y sellos. No hay laminado estructural, análisis de flutter ni dimensionamiento de cojinetes/ejes. No se acredita estabilidad, velocidad, aceleración ni alcance. Los motores/rotores internos siguen siendo representativos, el canal axial sigue vacío y la cinemática de apertura de cubiertas está pendiente. Las aletas exteriores no resuelven el estacionario en aire quieto. No se han añadido flaps, slats ni spoilers. Ninguna mejora de prestaciones se deduce del acabado visual.

Este paquete es un CAD conceptual completo del ensamble propuesto; todavía requiere ingeniería para convertirse en planos de fabricación. La investigación CFD pausada no se reanudó para esta entrega.

## Regeneración
Con CadQuery, numpy y Mitsuba/Pillow instalados: ejecutar crear_A05.py y después render_A05.py --view hero (o control/interior). preparar_entrega.py genera CSV y ZIP. Unidades CAD: mm.
