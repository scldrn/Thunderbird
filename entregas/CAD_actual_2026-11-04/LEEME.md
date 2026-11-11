# CAD actual — integración C02

Entrega visual del 4 de noviembre de 2026. Representa la candidata geométrica de integración más reciente, sin modificar la geometría para esta presentación. A07 continúa como referencia canónica del proyecto; C02 es una candidata separada.

## Abrir el modelo

- `C02_actual.FCStd`: documento nativo FreeCAD con jerarquía importada del STEP; no es un árbol completo de operaciones paramétricas.
- `C02_actual_cerrado.step`: conjunto completo, 316 registros de diseño.
- `C02_actual_corte.step`: corte de inspección para ver el interior; la carcasa recortada no corresponde a una pieza fabricable en ese estado.
- `C02_actual_exterior.blend` y `C02_actual_interior.blend`: escenas Blender con materiales, cámaras e iluminación de presentación.
- `C02_actual_exterior.png` y `C02_actual_interior.png`: renders nativos del CAD, sin generación de imágenes por IA.

## Configuración representada

Cuatro módulos de ventiladores internos, rotores de diámetro nominal 82 mm, estaciones longitudinales ±160 mm y laterales ±76 mm, conductos con bancos de álabes, reservas de accionamientos y superficies posteriores. El corredor axial representado no acredita un propulsor de alta velocidad instalado.

Envolvente aproximada de la teselación del conjunto cerrado: **1341 × 321,8 × 242,5 mm**, incluyendo elementos posteriores. Son medidas geométricas del modelo, no tolerancias de fabricación. La masa de 5 kg es objetivo y no está cerrada. Las configuraciones propias de 2 y 10 kg siguen pendientes.

## Trazabilidad y alcance

`PROCEDENCIA.json` identifica los archivos fuente y sus SHA-256. Las copias STEP/FreeCAD son idénticas a los archivos identificados de C02. La importación y reapertura previa de FreeCAD no encontró formas inválidas; no equivale a aprobación estructural o funcional.

Los cálculos recientes de fuerza prescrita no se convierten en piezas nuevas ni en un motor ficticio. Siguen pendientes motor definitivo, energía, refrigeración, mecanismos completos, cargas, estructura y prestaciones. Las reservas de equipos se distinguen visualmente en azul. Materiales y acabados del render son cosméticos.

El plan de investigación permanece pausado. Esta entrega solo empaqueta el CAD existente y genera nuevas vistas.
