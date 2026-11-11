# Verificación del salto de presión

Se aplicó `fanPressureJump` de OpenFOAM Foundation 13 al canal newtoniano de G0, retirando la fuente volumétrica. El salto cinemático 1 m²/s² a lo largo de L=0,2 m equivale a |G|=5 m/s². Se mantiene H=1 m, ν=0,1 m²/s y comparación transitoria a t=4 s.

La [API oficial](https://cpp.openfoam.org/v13/classFoam_1_1fanPressureJumpFvPatchScalarField.html) describe `fanCurve` en función del caudal. El campo p usado tiene dimensiones [0 2 −2], por lo que hay que multiplicar por ρ para expresar el salto en Pa.

| Caso | Máximo de iteraciones de presión | Alcances del límite 1000 | CPU (s) | Estado |
|---|---:|---:|---:|---|
| 1×40, signo normal | 1000 | 45.933 | 736,8 | Rechazado como configuración de producción |
| 1×40, signo inverso | 1000 | 46.885 | 302,6 | Rechazado como configuración de producción |
| 4×40, signo normal | 30 | 0 | 10,89 | Aceptado para este contraste del operador |
| 4×40, signo inverso | 30 | 0 | 10,94 | Aceptado para este contraste del operador |

Los cuatro campos presentan error máximo normalizado de velocidad de 0,03317%. La primera familia tiene presión interna casi nula y normalización degenerada; resolver el gradiente longitudinal elimina el comportamiento de iteraciones observado. Esto no es una demostración general de causalidad de todos los fallos de presión. No se relajó la tolerancia para hacer pasar la primera familia.

En la malla usada, `left` es owner: `reverse=false` impulsa −X y `reverse=true`, +X. Los casos 4×40 verifican gradiente ±5, inversión de signo, caudales opuestos e identidad del trabajo del salto y de la fuente equivalente. `auditar_benchmark_salto.py` produce `AUDITORIA.json` y comprueba campos/registros.

Los dos contenedores de estos benchmarks terminaron con salida 0; los solvers históricos pausados no se reanudaron. Son verificaciones de ecuaciones y condición de contorno, no ensayos del ventilador, validación del C02 o estimación de coste de una campaña tridimensional. Se conservan entradas, campos finales y logs de los cuatro casos.
