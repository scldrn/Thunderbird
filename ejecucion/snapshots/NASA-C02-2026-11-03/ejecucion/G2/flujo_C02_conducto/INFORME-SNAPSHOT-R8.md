# C02 r8: balance de dos campos guardados durante la corrida

3 de noviembre de 2026. El defecto de balance reconstruido ha descendido a aproximadamente 0,019% de ρU²A. Se comprobó usando copias de los campos 780 y 800, sin detener ni reiniciar el solver. Es progreso numérico; todavía no se aceptan cargas instaladas ni convergencia terminal.

## Procedencia y método

La observación de `Docker top` confirmó el mismo `foamRun` de r8 en ejecución. Su registro había completado el contador 825 cuando se copiaron los directorios 780/800, ya cerrados y sin purga. `snapshot_r8_780_800/INSTANTANEA_GUARDADA.json` identifica origen, fecha, proceso y hashes de todos los campos copiados. Los contadores de SIMPLE no representan segundos de vuelo.

Un contenedor auxiliar separado aplica `foamPostProcess` sobre esas copias. Verifica que las fuerzas de todas las fronteras son la suma de sólidos y extremos abiertos, e integra la convección con el flujo de caras guardado. No ejecuta un solver de flujo; el contenedor auxiliar terminó y se detuvo. Los campos originales y copiados permanecen sin cambios de contenido durante el posprocesado.

| Magnitud calculada | Contador 780 | Contador 800 |
|---|---:|---:|
| Defecto CV /ρU²A | 0,02089% | 0,01892% |
| Residuo X, N | −0,0003092 | −0,0003027 |
| Residuo Y, N | −0,0004716 | −0,0003941 |
| Residuo Z, N | −0,0000613 | −0,0001308 |
| Fuerza Z sobre sólidos, N | −1,089413 | −1,089383 |

El campo r7 de contador 500 tenía un defecto de 2,072%. Esta comparación incluye 300 iteraciones más y el cambio declarado de relajación de r8; no aísla todos sus efectos. La fuerza de la tabla corresponde al conducto pasivo con entrada impuesta a 20 m/s, sin rotor ni exterior. No es empuje del vehículo ni una pérdida total de presión medida.

## Cambios locales que todavía quedan

`auditar_instantanea.py` comprueba hashes, campos finitos, turbulencia no negativa y geometría tetraédrica: cuatro caras por celda, volúmenes positivos, cierre de normales y volumen total consistente con la auditoría Gmsh. Calcula cambios con pesos de volumen reales, además de las normas aritméticas por celda.

Entre 780/800, ΔU tiene RMS ponderado por volumen de 0,01222 m/s y RMS aritmético de 0,02163 m/s. Su máximo es 2,0671 m/s en una celda centrada en (11,686;−0,0028;−11,800) mm. Solo 2,52×10⁻⁶ del volumen cambia más de 1 m/s; 0,2499% cambia más de 0,1 m/s. La localización no demuestra por sí sola la causa del cambio.

La velocidad máxima a 800 es 36,3096 m/s. La presión guardada está entre −878,16 y 372,25 m²/s²: es presión cinemática de referencia, no presión absoluta negativa. Persisten cambios locales de k y ω. Que el balance global sea pequeño no prueba que todas las regiones o variables estén estacionarias.

## Siguiente criterio

R8 mantiene su objetivo 1000. Comprobar el proceso real antes de intervenir; el registro de la instantánea solo acredita vida en su fecha. Al terminar se requieren la auditoría terminal de residuos, cargas, momentos, continuidad y campos 980/1000. Después siguen sensibilidad de pared/malla/esquinas, acoplamiento del rotor, entrada/salida exteriores y mapa fuerza–momento–potencia. No se alteraron A07, C02 ni los dos solvers históricos pausados.

Reproducción desde la raíz:

```sh
.venv-cad/bin/python investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/auditar_instantanea.py --snapshot investigacion-aeronautica/ejecucion/G2/flujo_C02_conducto/snapshot_r8_780_800
```

El balance reproducible se encuentra en `balance_r8_snapshot_780_800/BALANCE.json`. `balance_estacionario_guardado.py --saved-snapshot` exige un registro de instantánea y sus hashes; conserva los requisitos de terminación originales cuando se audita una corrida terminal.
