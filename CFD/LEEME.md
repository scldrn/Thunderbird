# Preparación CFD del conducto vectorial A

Objetivo: calcular el campo de flujo, pérdidas y fuerzas/momentos sobre los seis álabes; después construir una relación entre mandos mecánicos y fuerza útil. Esta carpeta no contiene todavía una validación del vehículo completo.

## Caso prototipo

Conducto circular aislado de radio 42 mm, entrada z=80 mm y salida z=−65 mm. Dos filas de tres álabes rectangulares según el CAD corregido: centros z=−12/−40 mm, cuerda 16 mm alineada con el flujo en neutro, espesor 1,5 mm y envergaduras limitadas por alojamiento. Las superficies de cada álabe se etiquetan por fila y posición para calcular su fuerza y momento respecto a su eje.

Se generan mallas tetraédricas con Gmsh 4.15.2. No tienen capas prismáticas: son un inicio para verificar caso y solución, no una malla final para cargas. Las dos resoluciones geométricas nominales son h=6 y 4 mm, con refinamiento local a h/4 cerca de los álabes. El tamaño nominal no equivale al tamaño de todas las celdas. El total y las etiquetas están en cada `mesh_metadata.json`.

Modelo previsto: OpenFOAM Foundation 13, RANS incompresible estacionario k-omega SST, aire con ν=1,46e-5 m²/s y ρ=1,225 kg/m³. Entrada uniforme −40 m/s, intensidad de turbulencia supuesta 5 % y longitud de referencia 5 mm; salida a presión de referencia. Estos parámetros son hipótesis para caracterizar el conducto, no un punto de operación de un rotor seleccionado.

Se omiten rotor, buje, motor, rejillas, ejes de álabes, carcasa exterior y flujo libre posterior. El ángulo a la salida puede depender de la posición de esa frontera y no representa todavía la dirección de un chorro libre. El caso no puede usarse para certificar 600–1000 km/h ni para predecir la potencia eléctrica del vehículo.

## Archivos reproducibles

- `mallar_conducto.py`: construye y malla el volumen fluido con seis obstáculos.
- `preparar_caso.py`: escribe campos, propiedades, modelos, esquemas y funciones de fuerzas, presión y flujo.
- `ejecutar_caso.py`: convierte la malla, marca las paredes, exige `Mesh OK.` y ejecuta el solver en Docker con 2 CPU y límite de memoria de 4 GB.
- `solver/Dockerfile`: instalación aislada a partir de Ubuntu 24.04 y el paquete oficial arm64 de OpenFOAM 13. El SHA256 del paquete local debe coincidir con el del índice apt firmado antes de instalar.

La preparación o generación de una malla no equivale a un resultado CFD. Incluso si el solver termina, hay que auditar residuos, balance de masa, estabilidad de fuerzas, yPlus, resolución de capas límite y sensibilidad a malla, dominio, turbulencia y condiciones de entrada. También hay que estudiar si el flujo desviado necesita una simulación transitoria.

## Fuentes de instalación

OpenFOAM Foundation, instalación Ubuntu 13: https://openfoam.org/download/13-ubuntu/
OpenFOAM Foundation, arquitectura arm64 en macOS: https://openfoam.org/download/13-macos/

Las versiones se fijan para reproducibilidad del caso; no se afirma que OpenFOAM 13 sea la versión más reciente.
