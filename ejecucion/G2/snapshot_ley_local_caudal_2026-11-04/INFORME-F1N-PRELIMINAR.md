# C02: primer contraste de fuente prescrita

4 de noviembre de 2026. Resultado numérico preliminar con caudal impuesto, no un ventilador calibrado ni empuje instalado.

`actuador_r1_h4_F1N` alcanzó 1200, salida 0, reconstrucción 1180/1200 correcta y contenedor detenido. La fuente axial sobre el fluido es −1 N en Z, distribuida en una banda de 4 mm y 6000 tetraedros. Densidad de referencia: 1,225 kg/m³. La entrada permanece a 20 m/s, con caudal real de malla de 0,1108118473 m³/s.

## Comparación a contador 1200

`COMPARACION_F1N_PRELIMINAR_1200.json` verifica 21 archivos numéricos comunes idénticos y la misma imagen del solver. La única entrada numérica añadida es `constant/fvModels`. Ambos casos partieron de los mismos campos 1000. Esta identidad de entradas no demuestra convergencia del resultado forzado.

| Diagnóstico calculado | Pasivo r9 | Con fuente −1 N |
|---|---:|---:|
| Cinco cribados de arranque | Pasan | Fallan residuos |
| Presión estática entrada–salida, Pa | 200,5090 | −0,4999 |
| Fuerza Z sobre paredes, N | −1,088964 | −0,986409 |
| Defecto CV / rho·U²·A | 0,001693 % | 0,346214 % |
| Flujo mecánico nominal entrada menos salida, W | 21,564149 | −0,655892 |
| Trabajo de la fuente sobre el flujo medio, W | 0 | 22,649994 |

La suma del último flujo nominal y el trabajo de fuente da 21,994101 W, frente a 21,564149 W pasivo. Su diferencia de 0,429952 W no se considera una pérdida instalada aceptada: faltan convergencia, transporte de energía turbulenta y trabajo viscoso en extremos, entre otras comprobaciones. No se calcula eficiencia ni potencia de eje.

El posprocesado integra fuerza sobre fluido de −0,999999999999998 N, momentos locales de orden 1e−18 N·m y trabajo mediante velocidades guardadas. Regenera el diccionario esperado y verifica identidad antes de incluir la fuerza en el balance: convección saliente + tracción opuesta al fluido − fuente. Ignorar la fuente produciría un balance incorrecto.

Paredes más reacción de la fuente dan Z≈+0,0135914 N en este banco. **No es empuje del vehículo ni del módulo en estacionario**: no incluye exterior y el caudal de entrada es impuesto. Tampoco se extrapola linealmente este punto a la demanda de sustentación de 5 kg.

## Convergencia y continuación

Pasan finitud, Mach, continuidad relativa (máximo últimas20: 1,10073e−10) y deriva de fuerza/momento. No pasan residuos: p máximo2,61391e−4, Ux/Uy/Uz8,12761e−5/8,94204e−5/1,16666e−4, k6,55984e−5 y omega1,80908e−5; se conservan los umbrales anteriores. El defecto CV también disminuye de 0,454460 % en1180 a0,346214 % en1200, y se conserva como defecto medido, sin declarar cierre del balance mientras faltan residuos y sensibilidades.

Se inició una rama distinta `actuador_r2_h4_F1N_1400`, desde1200 hasta1400, sin cambio físico. Se comprobó identidad exacta del diccionario, metadata del actuador y seis campos de rearranque. Cuatro procesos efectivos UID1000 observados: se conserva la protección de OpenFOAM frente a código dinámico cargado como administrador. No se reinició el contenedor terminado ni se modificaron sus campos.

El paso siguiente es auditar1380/1400, incluyendo balance con fuente, antes de aceptar o continuar. En paralelo se calcula el pasivo de malla fina. Siguen pendientes sensibilidad de banda/malla, caudal libre, curva de rotor, remolino/par, potencia de eje, exterior e integración completa. T12 y el objetivo global permanecen abiertos.

## Actualización: continuación1400 terminada

`actuador_r2_h4_F1N_1400` terminó con salida0 y reconstrucción1380/1400 correcta. Pasa Mach, continuidad y deriva, pero los residuos p=1,03901e−4 yk=1,12067e−5 aún superan1e−4/1e−5. Los restantes residuos pasan. No se cambian umbrales.

`balance_actuador_r2_1380_1400/BALANCE.json` registra CVfinal/rho·U²·A=**0,00187422 %**, trabajo de la fuente22,650112W y flujo mecánico nominal entrada menos salida−0,470726W. La diferencia de presión estática es+0,920094Pa; el cambio respecto a1200 se conserva, sin seleccionar el valor más favorable. La máxima deltaU entre1380/1400 es0,557023m/s, con RMS aritmético0,00190983m/s.

Se inició `actuador_r3_h4_F1N_1500`, cien iteraciones adicionales, con el mismo actuador y modelo. Inspeccionar proceso y estado actual antes de esperar o interpretar resultados. La auditoría siguiente usará1480/1500. El trabajo de fuente sigue sin ser potencia de eje.
