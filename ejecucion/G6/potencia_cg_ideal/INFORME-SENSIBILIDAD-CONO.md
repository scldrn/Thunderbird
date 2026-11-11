# Sensibilidad del control conjunto al cono de empuje

Para los 36 escenarios hipotéticos de masa de 5 kg se repitió el certificado estático de la caja de aceleración de ±0,25 g por componente y momentos simultáneos de ±0,5 N·m por eje, sustituyendo el cono ideal de 45° por 35° y 40°. Se mantuvieron 21 N por módulo, 1 N de precarga vertical y las demás hipótesis de `INFORME-ACELERACION-MOMENTOS.md`.

| Reserva axial | Equipo genérico | Certificados a 35° | Certificados a 40° | Capacidad de la aproximación a 35°, N por módulo |
|---:|---|---:|---:|---:|
| 38 mm | x=0 | 0/6 | 0/6 | 21,39–21,53 |
| 60 mm | x=0 | 0/6 | 0/6 | 23,27–23,33 |
| 80 mm | x=0 | 0/6 | 0/6 | no determinada para la caja completa |
| 38 mm | CG equilibrado | 5/6 | 5/6 | 18,39–18,51 |
| 60 mm | CG equilibrado | 5/6 | 5/6 | 17,99–18,09 |
| 80 mm | CG equilibrado | 5/6 | 5/6 | 18,25–18,34 |

Cada certificado requiere que las 64 esquinas conjuntas de la caja de aceleración y de momentos cumplan el límite hipotético de 21 N y que el centro de masa genérico restante esté en su zona asumida. El caso equilibrado restante por grupo viola esta última restricción. Las capacidades indicadas son las mayores de las esquinas de cada escenario, para una aproximación discreta interior; son comparaciones ideales, no especificaciones de un ventilador real. Que falte un certificado no prueba imposibilidad física.

Se intentaron 4.608 asignaciones: 4.416 resueltas, 190 marcadas inviables por HiGHS y **dos con estado numérico desconocido**, que se conservan como tales en `SENSIBILIDAD_CONO_ACELERACION.json`. No se reclasifican los dos errores como inviabilidad. El máximo residuo de igualdad en las soluciones es 1,18e−8 en unidades mixtas. Pasaron dos pruebas analíticas adicionales de ángulo y estacionario.

El primer ensayo se detuvo por una aserción de monotonicidad errónea; después de retirarla se obtuvo el resultado anterior. Los conos discretizados por rayos tienen diferentes orientaciones polares y no son conjuntos anidados cuando también se limita la suma de coeficientes. Aunque los conos continuos geométricos sí están anidados, entre las soluciones del barrido hay 774 comparaciones de esquinas con capacidad calculada menor que para el cono discreto de 45°, por un máximo de 0,061 N. No debe interpretarse esa reducción como una mejora física; es una sensibilidad numérica del método. La discretización debe refinarse o contrastarse con optimización de cono de segundo orden antes de usar pequeñas diferencias para elegir una configuración.

Este resultado no acredita que pueda lograrse un cono útil de 35° o 40° con los conductos y álabes: la fuerza neta y las palancas instaladas siguen sin caracterizarse. Tampoco cubre retardos, potencia eléctrica, ráfagas, flujo cruzado o dinámica estructural. El archivo JSON conserva huellas de datos y código. No se reanudaron CFD pausados.
