# Conducto A: ejecución transitoria rechazada y diagnóstico numérico

Fecha: 1 de noviembre de 2026. Etapa digital del mismo objetivo de geometría, maniobrabilidad y mecanismos. **Aún no hay cargas medias aceptadas ni calibración de álabes.**

## Estado actual que sustituye a las instantáneas iniciales

La ejecución v2 dejó de avanzar a una tasa utilizable y desarrolló valores no físicos: se pidió una parada ordenada con `stopAt writeNow`. Se conservaron las series, el campo final y el diccionario final. El solver devolvió cero, pero **la ejecución está rechazada**; `REJECTION_AUDIT.json` reproduce la evidencia mediante `auditar_fallo_transitorio.py`.

Terminó a t=0,0005561922108 s, apenas el 1,854 % de los 0,03 s solicitados y antes del intervalo inicial a descartar. El paso cayó de aproximadamente 1,92e-6 a 1,05e-9 s, un factor de 1826. El módulo máximo de velocidad del campo final fue aproximadamente 698773 m/s frente a una entrada impuesta de 40 m/s. Son resultados de una patología numérica, no prestaciones del dispositivo. La causa concreta no ha sido aislada.

Se preparó un caso independiente `diagnostico_Euler_upwind_X35_Y-35_h0.006` manteniendo malla, geometría y campos iniciales. Cambia a Euler temporal y upwind de momento, dos bucles externos PIMPLE, tolerancias lineales 1e-8 y Courant objetivo 0,5. La duración diagnóstica es 0,001 s: está elegida para superar el punto de fallo anterior, pero es menor que el descarte inicial de 0,00725 s. **Aunque terminase estable, no permitiría calcular cargas medias aceptadas.** Cambiar varios controles simultáneamente tampoco permite atribuir el fallo anterior a uno solo.

El diagnóstico **terminó y fue auditado**: 903 pasos completados, t=0,001 s exacto, 536 s de reloj y campos finales finitos. El paso final fue aproximadamente 1,10e-6 s, sin el colapso observado en v2; Courant máximo registrado 0,50111. La velocidad máxima del campo final fue 96,14 m/s. El máximo desequilibrio relativo de caudal registrado fue 4,70e-5, incluyendo el campo inicial heredado. Es una comprobación numérica breve de 0,276 tiempos de paso, no validación física o estadística. `STABILITY_AUDIT.json` y `auditar_diagnostico_estabilidad.py` conservan la evidencia; las medias siguen retenidas porque no se alcanzó el descarte inicial.

El contenedor diagnóstico `codex-aero-diagnostico-estabilidad-A-v1` y el transitorio v2 anterior están detenidos. Se comprobó que no quedan contenedores del proyecto activos. No volver a ejecutar sus lanzadores sobre los mismos casos: los registros y campos son evidencia que debe conservarse. La comparación no aísla la causa de la divergencia anterior porque se cambiaron varios controles.

La siguiente etapa numérica requiere separar el efecto de esquema temporal, convección y acoplamiento, prolongar solo configuraciones estables y estudiar convergencia temporal/malla/dominio. Para cargas físicas faltará además resolver el rotor, las rejillas y la instalación, y contrastar el modelo con datos adecuados. Esta prueba breve no justifica dimensionar servos o prometer autoridad omnidireccional.

El análisis de series se implementó en `analizar_series_transitorias.py`: ponderación por tiempo para pasos adaptativos, interpolación sin extrapolar, separación fuerza/momento por álabe y suma de pares generalizados de cada fila antes de transmisión. Se retienen bloques completos de un tiempo de paso y la deriva entre ellos; no se inventan intervalos de confianza a partir de pasos correlacionados. Se comprobó con una señal lineal muestreada a tiempos irregulares, sus momentos exactos y el bloqueo de estadísticas antes del descarte. La auditoría de las series v2 retiene las seis series pero no emite medias.

Referencias de configuración: [control de solución de OpenFOAM 13](https://doc.cfd.direct/openfoam/user-guide-v13/fvsolution) y [explicación de PIMPLE por sus desarrolladores](https://doc.cfd.direct/notes/cfd-general-principles/the-pimple-algorithm). Sustentan las opciones del solver, no validan este conducto.

## Configuración de la ejecución v2 rechazada

Caso `transitorio_X35_Y-35_h0.006`, construido por `preparar_transitorio.py` desde los campos guardados de la iteración estacionaria 300. Esos campos son una condición inicial aproximada, no una solución convergida.

Misma malla de 170277 tetraedros, condiciones de entrada y modelo SST del caso anterior; integración temporal `backward`, PIMPLE con dos correcciones de presión y una corrección no ortogonal. Paso adaptativo con Courant objetivo 0,8 y techo de paso de 2e-5 s. El controlador temporal usa información previa: el Courant efectivo debe auditarse y puede sobrepasar ligeramente el objetivo.

Duración física prevista: 0,03 s, aproximadamente 8,28 tiempos de paso del aire por el dominio a 40 m/s. Se prevé descartar al menos los primeros dos tiempos de paso (0,00725 s) antes de examinar medias y fluctuaciones. Ese descarte y la duración elegida son criterios iniciales: no garantizan que la muestra posterior sea estacionaria o estadísticamente suficiente.

Se usa el contenedor `codex-aero-transitorio-A-v2`, red desactivada, 2 CPU y límite de memoria de 4 GB. El estado debe verificarse con el proceso/contendor real y el registro; `run_state.json` o `progress_audit.json` por sí solos NO prueban que siga ejecutándose.

## Corrección de inicialización verificada

La primera prueba heredó `0/uniform/time` del caso estacionario, de modo que el solver terminó sin avanzar pese a devolver código cero. No se cuenta como simulación física. Se conservó el registro como `log.initialisation_no_advance`, se eliminó ese metadato heredado del nuevo caso y se añadió una comprobación explícita de avance temporal en el lanzador. La ejecución v2 sí presenta tiempos físicos positivos, pasos adaptativos, resoluciones de velocidad/presión/turbulencia y correcciones de continuidad.

## Evidencia inicial histórica, anterior al fallo

`monitor_transitorio.py` lee únicamente pasos con tiempo de ejecución ya registrado. En el primer control había 263 pasos completados, t=0,000473683 s (0,131 tiempos de paso); Courant máximo registrado 0,835 y paso reciente aproximado 1,25e-6 s. El error global de continuidad máximo entre las últimas 100 correcciones era aproximadamente 2,29e-9 en el indicador normalizado del solver. Son diagnósticos de avance numérico, no prueba de precisión física ni estadísticas de cargas.

Se confirmó mediante Docker que `foamRun` estaba activo. Las cifras anteriores son una instantánea histórica; el progreso posterior se guarda en `transitorio_X35_Y-35_h0.006/progress_audit.json`. La ejecución sigue siendo una tarea de cálculo específica, no un bloqueo por falta de permiso o datos del usuario.

## Criterios pendientes antes de usar cargas

1. Alcanzar una duración física suficiente, registrando el Courant efectivo y sin divergencias o valores no físicos.
2. Comprobar el balance de masa y la convergencia interna por paso, no comparar residuos transitorios con un criterio estacionario de forma automática.
3. Analizar medias por bloques, deriva, fluctuaciones y correlación temporal de la fuerza y del momento de cada álabe respecto a su eje. Muchos pasos pequeños no equivalen a muchas muestras independientes.
4. Repetir con paso temporal menor y comprobar cambios en medias y fluctuaciones.
5. Mantener pendientes las sensibilidades de malla, capas de pared, dominio/salida y turbulencia. Una oscilación numérica no demuestra automáticamente inestabilidad física.

El caso sigue sin rotor, rejillas, eje, motor, instalación completa o chorro libre externo. No valida aún el ángulo efectivo del cono de fuerzas, los servos, el vuelo autónomo ni el régimen transónico.

## Continuar y auditar

- `monitor_transitorio.py`: progreso de pasos ya completados en el registro.
- `ejecutar_transitorio.py`: prepara contenedor, lanza solver, recupera posprocesado al terminar y lo detiene. No debe lanzarse de nuevo mientras exista una ejecución viva; conservar y continuar la existente.
- Registro de cálculo: `transitorio_X35_Y-35_h0.006/log.foamRun`.
- Metadatos y huellas de malla: `transitorio_X35_Y-35_h0.006/transient_assumptions.json`.

El cálculo transitorio es una parte de la investigación, no redefine el objetivo completo ni demuestra que esta sea la mejor geometría.
