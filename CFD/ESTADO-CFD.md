# Primera ejecución CFD del conducto A

Fecha: 1 de noviembre de 2026. **No se acepta aún un mapa de fuerzas o pérdidas para dimensionar actuadores o garantizar maniobras.** Se ha instalado y ejecutado un solver real y se han detectado los siguientes requisitos de mejora.

## Avances verificables

- Docker Desktop iniciado; imagen local `codex-aero-openfoam:13`, Ubuntu 24.04 arm64 y OpenFOAM Foundation 13, build 13-18870c24d21c. Paquete `20260624`; su SHA256 se comprobó contra el índice apt firmado antes de instalar. Evidencia: `solver/build.log`.
- Gmsh 4.15.2 instalado en el entorno Python del proyecto.
- Se corrigió la orientación neutra de los álabes: cuerda paralela al flujo, espesor transversal. Los STEP del módulo y su integración se regeneraron y reimportaron.
- Se construyó el volumen fluido de un conducto con seis álabes, identificando las seis caras de cada pieza por separado. Hay entrada, salida y pared de conducto.
- Malla neutra: 181015 tetraedros. Malla desviada (35°/−35° mecánicos): 170277 tetraedros. Ambas pasaron `checkMesh -allGeometry -allTopology` con `Mesh OK.`.
- Existe una malla neutra más fina de 606177 tetraedros; NO ha sido resuelta y no se ha demostrado independencia de malla.
- Se ejecutó el caso neutro hasta 300 iteraciones, se continuó desde su solución guardada hasta 600 y se ejecutó el desviado hasta 300.
- Se recuperaron campos y posprocesado, y se calculó yPlus. Los contenedores de cálculo se detuvieron tras recuperar resultados.

## Condiciones y exclusiones

Radio interior 42 mm, longitud del dominio 145 mm, entrada z=80 mm y salida z=−65 mm. Entrada uniforme de 40 m/s hacia −z; aire incompresible, ν=1,46e-5 m²/s y ρ=1,225 kg/m³; SST RANS estacionario con funciones de pared. Intensidad de turbulencia supuesta 5 % y longitud de referencia 5 mm. Estos son parámetros de estudio, no un punto medido de rotor.

No hay rotor giratorio, fuente de presión de ventilador, motor, ejes, rejillas, carcasa completa ni chorro libre exterior. El modelo usa perfiles rectangulares de álabe, no un diseño aerodinámico final. No se aplica al régimen transónico ni a la autonomía eléctrica del vehículo. La salida de presión cercana al álabe puede influir en la dirección de flujo calculada.

## Auditoría numérica

Resultados completos en `AUDITORIA_RESULTADOS.json`. La tabla siguiente se limita a indicadores de aceptación, no prestaciones del vehículo.

| Indicador | Neutro, 600 iteraciones | Desviado, 300 iteraciones |
|---|---:|---:|
| Todos los residuos prefijados satisfechos | No | No |
| Residuo inicial de presión en última iteración | 1,75e-4 | 2,49e-2 |
| Mayor residuo inicial de velocidad en última iteración | 6,77e-5 | 6,79e-3 |
| Desequilibrio relativo de caudal en última iteración | 8,42e-8 | 4,70e-5 |
| yPlus promedio por álabe, intervalo entre seis piezas | 41,5–44,5 | 56,8–95,7 |
| Mayor yPlus local registrado sobre álabes | 107,4 | 282,3 |

Umbrales empleados: p<1e-4 y U/k/omega<1e-5 para residuos iniciales. La malla usa tetraedros isotrópicos sin capas prismáticas; los valores de yPlus son diagnósticos, no una aprobación general de tratamiento de pared. La media yPlus no sustituye su distribución espacial, especialmente en bordes/separación.

La buena conservación global de caudal NO demuestra convergencia de fuerzas y momentos. Prolongar el neutro de 300 a 600 no resolvió todos los residuos. El desviado muestra una dificultad clara para un cálculo estacionario; eso no prueba por sí solo que el flujo real sea inestable: hay que distinguir dependencia de malla, condiciones de frontera, discretización y falta de convergencia de una inestabilidad física.

Los archivos guardan fuerzas y diferencias de presión brutas para diagnóstico. No se denominan mapa validado de empuje, pérdida total de energía o par requerido de servo. Tampoco se convierte el promedio de velocidad de salida en una calibración de ángulo de chorro libre.

## Qué sigue

1. Auditar resolución de pared y geometría de bordes; generar una malla adecuada para las cargas, con estrategia de capas y estudio de refinamiento.
2. Ampliar el dominio para comprobar sensibilidad de salida y chorro libre.
3. Ejecutar una formulación transitoria cuando proceda y comprobar sensibilidad temporal, estadísticas y balance.
4. Comparar casos con/sin álabes a las mismas condiciones antes de atribuir pérdidas al mecanismo.
5. Incorporar después el rotor y el resto de obstáculos, y construir el mapa acoplado de fuerza/momento frente a mandos y caudal/presión.
6. Usar ese mapa para dimensionar transmisión/servos y cerrar la simulación del vehículo.

Esta etapa mejora el prototipo digital y corrige una geometría neutra anterior. No cierra la masa, control a cualquier actitud, propulsión de alta velocidad, autonomía, estructura o selección óptima global.

## Reproducibilidad y fuentes

`mallar_conducto.py`, `preparar_caso.py`, `ejecutar_caso.py`, `auditar_resultados.py` y `graficar_diagnostico.py` contienen el procedimiento. Se usaron copia directa y `docker exec` al no arrancar el montaje compartido de esta sesión. Los cambios de diccionario se verificaron contra los ejemplos incluidos en la versión instalada: distancia de pared `meshWave` y selección `patch` para `surfaceFieldValue`.

Instalación oficial de OpenFOAM 13: https://openfoam.org/download/13-ubuntu/
Información oficial de arquitectura arm64 en macOS: https://openfoam.org/download/13-macos/

Estos enlaces sustentan la instalación; los diagnósticos anteriores proceden de nuestras ejecuciones y no de validación externa del diseño.
