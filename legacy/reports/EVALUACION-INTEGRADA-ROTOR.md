# Evaluación integrada del rotor: cierre del análisis de escritorio

## Conclusión de esta etapa

La configuración de5kg sigue siendo un candidato de investigación. No está demostrada una capacidad de1g en cualquier dirección ni un rotor listo para fabricar. Se completó el mapa numérico condicionado, la asignación de fuerzas con par de reacción, el chequeo eléctrico necesario y el análisis de requisitos del mecanismo. Lo pendiente requiere información adicional o ensayos, no más precisión decimal del mismo modelo.

La investigación global NO está terminada: quedan transición, velocidad600–1000km/h, estructura y comparación de arquitecturas. Este informe cierra solamente la evaluación de escritorio del rotor con datos disponibles.

## Configuración evaluada

SD8020, dos palas, diámetro457,2mm, cuerda30mm, raíz40mm, sin torsión. Masa supuesta15g/pala. Ocho rotores en dos estaciones separadas45,7cm, cuerpo91,4×22,9cm, masa fija5kg y CG supuesto50mm hacia reactor. Perfil y CL/CD procedentes deUIUC; no mediciones del rotor.

MotorMN5008KV170 y servoKSTX12-508 son referencias, no componentes aprobados. Dos packsGNB6S2200mAh en serie son la referencia de batería, con754g incluyendo40g de integración supuestos.

## Mapa bidireccional

Se intentaron324puntos: empuje−40a+40N, paso1N, cuatro regímenes5000–6500rpm. La inducción uniforme cambia de signo con el empuje. Se usaCL/CD experimental sin reflejar artificialmente la rama positiva. Al salir del dominio experimental se fija el valor de borde y se registra su contribución al par: cálculo de sensibilidad, no aerodinámica validada.

A6000rpm:

| Empuje | Paso estimado | Potencia eléctrica, eficiencia85% supuesta | Contribución de par fuera del dominio |
|---|---:|---:|---:|
| −30N | −10,15° | 400W | 28,4% |
| 0N | −0,008° | 60W | 0,16% |
| +30N | +10,28° | 414W | 0,21% |
| +39N | +12,88° | 612W | 8,5% |

A−39N no hay solución en la rama de polar limitada usada a6000rpm. NO significa que el rotor real no pueda producir−39N: la tabla negativa no cubre suficientes ángulos. Para invertir rápidamente importa precisamente esa región mal cubierta. La pequeña diferencia respecto al estudio anterior en porcentajes proviene de corregir el criterio de cobertura para que solo se comprueben los bloques deRe con peso no nulo y del discretizado radial.

Ocho rotores girando a6000rpm con empuje individualcero consumen unos482W en el modelo. No es estacionario del vehículo: en estacionario deben además sostener el peso.

## Fuerzas, momentos y control

Se resolvieron546solicitudes:26direcciones, tres niveles de fuerza y siete momentos (cero y±1Nm en los ejes). Se optimizó numéricamente el consumo usando el mapa interpolado; no se demuestra óptimo global ni máximo continuo.

Se examinaron128patrones de sentido de giro, fijando el primero por simetría. Nueve cancelan momento angular en la hipótesis de rotores idénticos y régimen igual. El patrón seleccionado en las posiciones del código hace girar una estación en un sentido y la otra en el opuesto. No basta describirlo como CW/CCW sin indicar la normal local de cada rotor.

El par de reacción no compensado puede alcanzar0,58Nm en las solicitudes muestreadas. Se volvió a resolver el reparto incorporando ese par;546/546casos tuvieron solución numérica, con limitación de empuje de la tabla−37a+40N. Este resultado sigue dependiendo de regiones extrapoladas.

| Conjunto solicitado | Máxima potencia muestreada con reacción |
|---|---:|
| Fuerza igual al peso y reserva de control | 1,20kW |
| Fuerza1,5veces el peso y reserva | 1,80kW |
| Fuerza2veces el peso y reserva | 2,52kW |

Auditoría adicional: con límites−37/+40N y1Nm de reserva, el conjunto continuo de fuerzas SIN reacción alcanza96,90N, equivalente a0,976g adicionales. Por tanto, pasar las546muestras no demuestra1g en todas las direcciones ni siquiera en esa versión simplificada. La reacción cambia el conjunto y no se ha demostrado su garantía continua. El límite inverso procede de cobertura insuficiente de polar, no de ensayo del rotor.

Estos conjuntos contienen aceleraciones adicionales de0,5gy1g con gravedad bajo la idealización estática, pero muestrearlos no garantiza todas las direcciones. Algunos casos de las dos ramas ágiles usan regiones en que casi98% del par de algún rotor depende de datos fuera del dominio. No deben anunciarse como capacidades verificadas.

Como auditoría de datos, imponiendo que menos de5% del par modelado dependa de datos fuera de rango, el intervalo queda aproximadamente−28a+38N. Con ese intervalo y momento1Nm, ignorando reacción, la bola estática equivale a0,68g adicionales. El umbral5% es arbitrario; NO es límite físico ni garantía de error5%.

## Momento giroscópico

Solo las palas supuestas suman inercia0,000630kgm² por rotor y momento angular0,396Nms a6000rpm. Una rotación del cuerpo de2rad/s perpendicular al eje puede generar0,792Nm por rotor. El patrón equilibrado cancela la suma ideal, no los esfuerzos locales en cada brazo. Diferencias deRPM, masa, eje o transición destruyen la cancelación exacta. No se incluye inercia del motor/buje en estas cifras.

## Compatibilidad eléctrica

La condición ideal sin carga delKV170 exige al menos35,3V para6000rpm. Superarla no demuestra capacidad bajo carga. No hay en las fuentes consultadas mapa completo de par/RPM/temperatura del rotor propuesto a tensión mínima. El punto+39N requiere aproximadamente0,83Nm y520W mecánicos según este modelo.

El presupuestoGNB conserva potencia y duración sin validar. A2,52kW y40V requiere unos63A de batería antes de consumos auxiliares. La etiqueta120C no sustituye curvas de descarga y límites del conector. Sin resistencia y temperatura medidas no se publica autonomía garantizada.

## Servo y mecanismo

Para cambiar entre−30y+30N, el mapa pide20,43° de recorrido de paso. Con relaciónpaso/servo0,5 se calculan47,7ms usando velocidad de catálogo a8,4V. El par resistente preliminar es0,228Nm. Una sensibilidad con curva velocidad-par lineal ideal da75,4ms, pero esa curva NO está publicada para este servo y no prueba la respuesta real. No incluye dinámica de motor/estela ni régimen de empuje±39N.

Se conserva requisito de retención de pala cercano a0,8kN por pala a6000rpm bajo masa supuesta. Material, laminado, rodamientos, fatiga, holgura y bloqueo siguen sin dimensionado aprobado. La cifra98g por estación parapalas+ESC+servo+buje sigue siendo un presupuesto, no una lista de componentes conseguida.

## Ensayo necesario y criterios de aceptación

| Subsistema | Dato o ensayo | Criterio para la rama1g |
|---|---|---|
| Rotor completo | Empuje/par/potencia vsRPM,paso,tensión | Demostrar envolvente que contenga las demandas; referencia±38,94N por módulo en modelo simétrico |
| Rama inversa | Medición explícita, sin reflejar curvas | Cubrir el mismo conjunto de fuerzas y momentos con asimetría medida |
| Motor/ESC | RPM y temperatura a tensión mínima | Mantener puntos de carga del mapa sin exceder límites documentados |
| Batería y conexiones | Descarga representativa, tensión/temperatura | Alimentar mapa completo y auxiliares durante misión acordada; sin inferirlo deCnominal |
| Servo/buje | Barridos de paso bajo rotor cargado | Medir tiempo, asentamiento, holgura y corriente; validar referencia70ms si se conserva como objetivo |
| Estructura | Retención, cargas combinadas, fatiga y vibración | Criterios de resistencia derivados de material y misión, aún por especificar |
| Vehículo | Reparto con mapas medidos y masa real | Mantener control ante cargas y transitorios; volver a calcular transición |

Los ensayos de rotor requieren banco instrumentado y retención/protección adecuados definidos por un equipo competente. No se incluyen instrucciones de fabricación ni se afirma que el mecanismo esté listo para girar.

## Fuentes

- UIUC, datos SD8020: https://m-selig.ae.illinois.edu/pd/pub/lsat/vol1/SD8020.DRG
- Condiciones y procedencia: https://m-selig.ae.illinois.edu/pd.html
- Motor de referencia: https://store.tmotor.com/product/mn5008-kv400-motor-antigravity-type.html
- FichaKST: https://www.intermodel.fr/fichiers/KSTX12-508.pdf
- BateríaGNB: https://www.gaoneng.shop/products/gaoneng-gnb-6s-22.2v-2200mah-120c-xt60-lipo-battery
- Paso variable experimentalMIT: https://acl.mit.edu/projects/variable-pitch-quadrotor

## Archivos y verificación

`evaluacion_rotor_completo.py`:324puntos y546asignaciones, residuos de empuje<1e-6, refinamiento240a480estaciones con diferencia de potencia<0,5% en los puntos comprobados. `reaccion_rotores.py`: patrón de giro y reparto no lineal con reacción, residuos<1e-5. `limite_cobertura.py`: auditoría del dominio de datos. LosCSV/JSON y figura están enresultados. Estas verificaciones son numéricas, no ensayos físicos.
