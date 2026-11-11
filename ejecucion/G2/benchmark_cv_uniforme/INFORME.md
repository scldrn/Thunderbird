# Verificación analítica del posprocesado de campos guardados

3 de noviembre de 2026. Alcance: operador de integración; no es validación del rotor ni del vehículo.

`../verificar_cv_uniforme.py` genera dos estados uniformes independientes en un cubo de 1 m de lado, con 64 hexaedros. Se prescribe U=(3,0,0) y (6,0,0) m/s, presión cinemática 5 m²/s², densidad 1,225 kg/m³ y flujo de cara calculado explícitamente para cada estado. No se infiere aceleración física entre sus índices.

| Magnitud, entrada/salida | Estado 3 m/s | Estado 6 m/s |
|---|---:|---:|
| Flujo volumétrico, m³/s | −3 / +3 | −6 / +6 |
| Integral Uφ, componente X, m⁴/s² | −9 / +9 | −36 / +36 |
| Integral pρn, componente X, N | −6,125 / +6,125 | −6,125 / +6,125 |

Las comparaciones contra esas expresiones pasan con tolerancia absoluta 10⁻¹². La resultante y el momento sobre todas las caras son cero; también pasa el esfuerzo viscoso nulo. `AUDITORIA.json` conserva valores y huellas de entradas/resultados.

Esto verifica, en este caso, signos, ponderación por φ, conversión de presión cinemática a fuerza y lectura de distintos campos guardados. La inspección de [foamPostProcess de OpenFOAM 13](https://cpp.openfoam.org/v13/foamPostProcess_8C_source.html) confirma la reconstrucción del solver en cada tiempo solicitado; no hay base para atribuir automáticamente el defecto de balance C02 a reutilización del primer φ.

La prueba no cubre gradientes no uniformes, turbulencia, correcciones no ortogonales ni equivalencia entre esfuerzos reconstruidos y términos discretos ensamblados. El defecto estacionario reconstruido de C02 r5 sigue pendiente de resolución. El contador de iteraciones estacionarias no permite introducir un término de acumulación física para hacerlo cerrar.

Reproducción, desde la raíz: `.venv-cad/bin/python investigacion-aeronautica/ejecucion/G2/verificar_cv_uniforme.py`. El script conserva salidas previas y rechaza duplicarlas; inspeccionar sus resultados antes de crear una nueva revisión. Contenedor `codex-aero-cv-uniforme-v1` terminado y detenido tras la prueba.
