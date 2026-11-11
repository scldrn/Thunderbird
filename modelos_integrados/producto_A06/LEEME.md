# A06 — Obsidian / Internal

Arquitectura A: cuatro ventiladores internos. Confirmada explícitamente por el usuario el 2 de noviembre de 2026. Los módulos de rotor permanecen dentro del fuselaje. No hay brazos ni casetes de rotor retráctiles. Esta entrega consolida A05, conserva su geometría exterior y aletas de control, y mejora el corte de inspección para mostrar los conductos y bancos de álabes. No representa una nueva optimización aerodinámica.

## Entrega CAD
Tres escalas de masa objetivo: 2, 5 y 10 kg. Cada carpeta incluye un STEP de configuración cerrada, un STEP de corte de inspección, un STEP con las cuatro aletas posteriores en pose demostrativa ±15°, STL exterior, lista de piezas y manifest. Los STEP de ensamble contienen 208 piezas válidas; la revisión se reimporta al generar. Código paramétrico CadQuery y base geométrica A04 incluidos, unidades mm.

Cuatro módulos internos: conductos, rotor/motor representativos, bancos de álabes y ejes. Canal axial central vacío, estructura y reservas de actuadores. Cuatro aletas posteriores móviles en X con carenados de raíz, ejes y cojinetes representativos. Carrocería deportiva negra con insertos enrasados. Los renders proceden de los STEP exportados, no de generación de imágenes por IA.

## Estados y límites
El STEP integrado representa cubiertas cerradas; no es una configuración de estacionario operativa. El corte de inspección elimina piezas de carrocería y porciones de dos camisas para mostrar mecanismos; esa sustracción es una vista de inspección, no un modo de vuelo ni una puerta que se mueve. Para el funcionamiento real de los ventiladores deben resolverse entradas/salidas y el mecanismo de sus cubiertas. La anterior pose de tapas abiertas no se incluye como mecanismo aprobado.

Se conservan las verificaciones geométricas locales de aletas en nueve ángulos entre −20° y +20° contra cuerpo y carenado. No sustituyen barrido continuo, tolerancias o comprobaciones bajo deformación. Los actuadores, rodamientos, perfiles de pala y propulsión no están seleccionados o dimensionados funcionalmente. El montaje de aletas requiere refuerzos y anclajes. Las masas indicadas son objetivos, no masas del ensamble físico.

Pendientes: cinemática y sellado de cubiertas; fuerza y potencia instaladas; control omnidireccional; motor axial y energía; cierre de masa/CG/inercia; materiales, laminados y estructura; análisis aeroelástico; fabricación y tolerancias. No se acredita velocidad de 600–1000 km/h, agilidad, estacionario ni mejora de estabilidad. Es CAD conceptual integrado, no planos listos para fabricar. La investigación CFD permanece pausada.

## Regeneración
Ejecutar crear_A06.py con CadQuery/numpy; render_A06.py --view hero, interior o control con Mitsuba/Pillow; preparar_entrega.py para generar ZIP, tablas y huellas.
