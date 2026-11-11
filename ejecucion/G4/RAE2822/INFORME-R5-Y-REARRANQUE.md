# RAE2822: piloto degenerado y recuperación del algoritmo

3 de noviembre de 2026. La rama LTS r5 terminó el contador600 con salida0, pero se **rechaza**: se formó presión casi nula en la región de salida y varias ecuaciones dejaron de actualizar sus campos. El resultado no valida el experimento ni permite aceptar CL/CD, aunque algunos residuos sean pequeños.

## Diagnóstico del piloto LTS

Se mantuvo la malla híbrida verificada y se continuó de100 a600 elevando el Courant local0,2→1. Los campos permanecen finitos, pero no físicamente admisibles en la zona de salida. La auditoría de `piloto_r5_continuacion_Co1/AUDITORIA_PILOTO.json` registra:

| Magnitud | Valor terminal |
|---|---:|
| Presión mínima absoluta | 0,0003313 Pa |
| Posición del mínimo | x=8,1701 m; y=0,9363 m, aproximadamente26,8 cuerdas aguas abajo |
| Densidad mínima | 5,95×10⁻⁹ kg/m³ |
| Mach local máximo | 1,411 |
| Cambio máximo de U entre580/600 | 50,93 m/s |
| Cambio de p/T/ρ entre580/600 | Exactamente0 en los campos escritos |
| Fracción de correcciones lineales nulas, últimas20 | Véase JSON |
| Residuo inicial p, máximo últimas20 | 9,37×10⁻¹⁰ |
| Error RMS Cp en103 puntos, diagnóstico | 0,56867 |

La reducción del error Cp respecto al arranque100 no hace aceptable este campo. Las variables termodinámicas congeladas y la velocidad cambiante contradicen una interpretación de convergencia basada solo en residuos. Los puntos de presión sobre el perfil no detectan por sí solos la degeneración del campo lejano.

El mínimo de presión cae de unos88 kPa en el contador400 a43 kPa en450,16 Pa en500 y0,000331 Pa al final. El paso pseudotemporal local mínimo alcanza aproximadamente1,15×10⁻¹² s. No es tiempo físico ni evidencia de una dinámica real del vehículo.

El auditor ahora incluye cambios normalizados de U/p/T/ρ, un centinela amplio de degeneración p/p∞ yρ/ρ∞>0,05, la fracción de correcciones lineales nulas y el rango de pasos locales. Ese centinela no es un dominio de aceptación física; sirve para rechazar estados degenerados. La auditoría anterior se conserva como `AUDITORIA_PILOTO_r1_SIN_ALERTA_VACIO.json`.

## Configuración estacionaria y fallos conservados

Se recuperó de la imagen instalada el tutorial oficial `fuentes/OpenFOAM13_aerofoilNACA0012Steady`. Sus archivos y huellas identifican la referencia utilizada. La nueva familia mantiene Mach0,729, Re6,5millones, geometría, gas perfecto, energía y Sutherland. Se reinicia desde el flujo uniforme original; no se reutiliza el estado de vacío de r5.

Cambios de la familia estacionaria: `steadyState`, presión Gauss conservativa, relajaciones de campo p=0,3 yρ=0,01, y condición freestream en la salida como en el tutorial. Se conserva upwind durante el arranque; el esquema convectivo de mayor orden del tutorial se estudiará después. Son cambios de paquete, no un experimento de un parámetro aislado.

- **r6 estacionaria:** el suavizador DIC del tutorial resultó incompatible con la matriz asimétrica creada al activar la opción de corrección transónica. Falló antes de completar una iteración. Se conserva íntegro.
- **r7 estacionaria asimétrica:** GaussSeidel elimina el error de tipo de matriz, pero la resolución de presión diverge a magnitudes enormes y posteriormenteNaN. La vigilancia solicita `stopAt writeNow`; se confirmó el proceso vivo con campos no finitos y se terminó exclusivamente ese `foamRun` medianteSIGTERM. Salida143, últimos2 contadores completados, contenedor detenido y registros preservados.
- **r8 estacionaria oficial:** usa la corrección de presión simétrica predeterminada del tutorial, con DIC. El selector `transonic no` modifica la estrategia de corrección de presión, no elimina la densidad dependiente de p/T, la energía compresible ni el objetivo Mach0,729. Su idoneidad debe demostrarse frente al experimento y la sensibilidad numérica.

## Vigilancia y criterio siguiente

El ejecutor puede solicitar escritura/parada cuando p oρ caen bajo el centinela y terminar solo el solver de su contenedor si apareceNaN/Inf o no responde en30 s. Se registra cualquier intervención y se guarda una copia del control efectivo; el archivo de entrada original del host permanece identificable. Un proceso que termina correctamente sigue necesitando auditoría de campos y balances.

Consultar el proceso real antes de intervenir en r8; `EJECUCION.json` es solo un registro. Si termina en500, auditar480/500, Cp, presión/densidad lejos del perfil, cambios de campo, masa, fuerzas y resolución de pared. Después siguen esquemas, mallas, condiciones lejanas y turbulencia/transición. G4 y T21 continúan abiertos; los solvers históricos permanecen pausados.

## Resultado del arranque r8 y segundo método

R8 también activa el centinela: presión mínima−1,033MPa tras el primer contador completo. La petición `writeNow` no finaliza a tiempo la siguiente resolución y el supervisor envíaSIGTERM a ese único proceso. Salida143, contenedor detenido y registros conservados. No hay resultado estacionario aceptado; no se continúa esa semilla divergente.

Se prepara SU2 como segundo método mediante la versión oficial8.6.0. El binario macOS publicado esIntel; se verificó suSHA-256 publicado, pero el equipoARM64 rechaza su ejecución. La compilación nativa y sus dependencias fijadas se registran en `integracion_apps/SU2/COMPILACION_NATIVA.json`. Todo queda dentro del proyecto.

El caso SST oficial coincide enMach0,729,Re6,5millones yα2,31°, pero usaT288,15K, cuerda1 yνt/ν=100; el caso NASA/OpenFOAM usaT255,5556K, cuerda0,3048m yνt/ν supuesto1. La malla oficialSU2 tiene13937nodos,22842elementos y192aristas de perfil; su mayor distancia unidireccional entre vértices y el polígono NASA es0,001509c. Son diferencias declaradas: ejecutar ese caso comprueba primero la operatividad/convergencia del segundo método, sin acreditar todavía identidad física ni validar el vehículo.

La [implementación oficial de presión](https://cpp.openfoam.org/v13/isothermalFluid_2correctPressure_8C_source.html) y la [clase del solver térmico](https://cpp.openfoam.org/v13/classFoam_1_1solvers_1_1fluid.html) documentan la distinción entre el selector de corrección de presión y las ecuaciones físicas compresibles. Los fallos no se reinterpretan como resultados de un flujo incompresible ni se usan para ajustar la geometría.
