# A03 · Plataforma deportiva integrada

Revisión CAD de presentación de producto, derivada de la arquitectura A y del diseño industrial aprobado. Es geometría tridimensional editable, no una imagen generada por IA. La apariencia se presenta como producto; el dimensionamiento funcional continúa en desarrollo.

## Entrega

- `2kg/`, `5kg/`, `10kg/`: conjuntos STEP coloreados, corte de inspección STEP, exterior STL, visor GLB y lista de piezas CSV. Las masas son objetivos, no masas cerradas o pesadas.
- `crear_A03.py`: construcción paramétrica en CadQuery, con 5 kg como escala de referencia.
- `render_A03.py`: trazado de rayos desde los STEP exportados mediante Mitsuba.
- `VERIFICACION.json` y manifiestos: comprobaciones geométricas y medidas del conjunto.

## Dimensiones del CAD exportado

| Escala objetivo | Longitud | Anchura | Altura | Paso de ventilador | Interfaz axial exterior |
|---|---:|---:|---:|---:|---:|
| 2 kg | 988.1 mm | 237.1 mm | 143.0 mm | 61.9 mm | 44.2 mm |
| 5 kg | 1341.0 mm | 321.8 mm | 194.1 mm | 84.0 mm | 60.0 mm |
| 10 kg | 1689.6 mm | 405.5 mm | 244.6 mm | 105.8 mm | 75.6 mm |

## Cambios integrados

Se mantiene la carrocería facetada y deportiva en grafito/cobre. Se propone para esta revisión la distribución intermedia estudiada: centros x=±200 mm, y=±76 mm en la escala de 5 kg, con reserva axial exterior de 60 mm. Es una propuesta equilibrada de empaquetado, no una demostración de óptimo global ni sustitución de la arquitectura A seleccionada.

Los cuatro módulos giratorios quedan dentro del cuerpo y las ocho cubiertas siguen la superficie exterior en la pose cerrada de avance. Se conservan los bancos de álabes superior/inferior y sus ejes, se perforan sus pasos en las camisas y se añaden alojamientos de actuación fuera del flujo principal. El tubo central vacío tiene diámetro exterior de 60 mm e interior de 56 mm en la referencia; no representa un motor. La interfaz posterior tampoco es una tobera dimensionada.

La estructura visible incorpora cuadernas y apoyos del canal axial. La piel se construye con un loft interior desplazado 1 mm en las secciones transversales: no es una pared de espesor normal uniforme ni un laminado dimensionado. El espesor, los refuerzos y sus uniones requieren cálculo estructural y cierre de masa. No se han trasladado inercias o tiempos de giro de carcasas anteriores a este nuevo conjunto.

Las cubiertas de sensores, paneles laterales, tornillería, juntas de panel y aros son piezas separadas. Las superficies principales tienen recortes para los insertos; el render no usa piezas superpuestas para simular cambios de color.

## Alcance mecánico y verificación

Los STEP se reimportan y se verifica que todas las piezas son geométricamente válidas. Se comprueba la contención del loft interior, alojamientos de actuador, paso axial y apoyos, así como la ausencia de volumen de intersección de ejes con los conductos perforados en los casos locales evaluados. Estas comprobaciones no constituyen una revisión global de todas las interferencias, tolerancias o cargas.

El corte de inspección retira la cubierta superior y secciona parcialmente dos camisas para que se vea el interior. No es una pose operativa de las compuertas. La cinemática de apertura/retracción, transmisiones, cojinetes/sellos y el rotor reversible siguen por desarrollar. Los rotores/motores procedentes del estudio anterior son representativos; no se presentan como componentes funcionales seleccionados.

Los ensayos CFD y las asignaciones ideales de fuerza no validan todavía el mapa instalado, el arrastre total, la velocidad de 600–1000 km/h ni el vuelo autónomo. El CAD conserva esa distinción: se integran hallazgos de espacio y protección, sin convertir hipótesis de fuerza o material en prestaciones demostradas.

## Abrir y modificar

Los STEP pueden abrirse en FreeCAD, Fusion, SolidWorks, Onshape u otro modelador compatible. Los GLB sirven para inspección/presentación, no sustituyen las superficies editables STEP. Los STL contienen solo el exterior para visualización y no son instrucciones de fabricación. Para regenerar con el entorno existente: `.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/producto_A03/crear_A03.py`. No se necesita instalar software adicional para esta entrega.
