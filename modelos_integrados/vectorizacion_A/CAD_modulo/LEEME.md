# Alojamiento preliminar de álabes de vectorización del modelo A

Fecha: 1 de noviembre de 2026. Fuente reproducible: `../../alojamiento_vectorial_A.py` desde este directorio. Unidades STEP: mm.

## Geometría creada

Cuatro canales en las posiciones de los ventiladores del diseño deportivo A. Cada canal contiene dos filas ortogonales de tres álabes rectangulares: primera fila con eje de mando X a z=−12 mm, segunda con eje Y a z=−40 mm. Cuerda de 16 mm, espesor de 1,5 mm, centros transversales a −22/0/+22 mm y envergaduras recortadas para el alojamiento circular. Conducto de radio interior 42 mm y exterior 44 mm, recortado por la envolvente del cuerpo. Ejes de 1,2 mm de radio representativos, sin rodamientos ni acoplamientos dimensionados.

Los STEP `neutro.step` y `desviado.step` muestran los módulos en posición 0°/0° y 35°/−35°. Los movimientos geométricos analizados cubren −45° a +45° mecánicos. Eso NO implica 45° de desviación del chorro: no existe aún una calibración aerodinámica entre ambos ángulos.

`integracion_preliminar.step` incorpora los módulos neutros a una COPIA de la carrocería aprobada y abre pasos verticales de radio 42 mm hasta la parte inferior en las envolventes de presentación. El diseño aprobado original no se modifica. Esta rama no incluye una instalación interna de motor, baterías, reactor, depósitos y cableado ya resuelta. Los sólidos de carrocería originales son envolventes de presentación, no una distribución real de material y espesor; no se calcula su masa como si fueran sólidos macizos fabricables.

## Verificación geométrica y límites

- 168 posiciones de álabes: cuatro canales, dos filas, tres álabes y siete ángulos mecánicos.
- En todas esas posiciones, el volumen de álabe fuera de la envolvente original es cero dentro de la precisión del núcleo CAD.
- Adicionalmente, se comprobaron 24 prismas que contienen el barrido completo de cada álabe. Ninguno sobresale del cuerpo: esta es una comprobación conservadora entre las posiciones muestreadas.
- Radio máximo calculado de las esquinas de los álabes en la muestra: 39,320 mm; margen radial nominal frente al radio de conducto 42 mm: 2,680 mm. No incluye tolerancias, flexión o dilatación. La elección de envergaduras se basa en una cota radial conservadora para la rotación completa.
- Separación vertical conservadora de los barridos de ambas filas: al menos 11,930 mm. Cada fila tiene el mismo ángulo en sus tres álabes. Las filas distintas pueden moverse independientemente.
- La cota superior del barrido de la primera fila es z=−3,965 mm; el plano representativo de palas del rotor está en z=66 mm. Esto separa esos elementos geométricos, pero no verifica motor, buje, estatores, servo o transmisión.

Se detectó una pequeña salida de envolvente en una disposición inicial más baja (filas a −20/−48 mm); se sustituyó por la disposición anterior antes de exportar la rama final.

Los ejes pueden penetrar las paredes para alojar futuros apoyos: no se declara verificada su holgura radial o su unión con la carcasa. Tampoco se ha cerrado soporte estructural de los álabes, servo, sincronización de las tres piezas de una fila, transmisión, sellos, topes, fatiga, par bajo carga, masa, velocidad de mando o refrigeración. El modelo no prueba que la pérdida de flujo sea aceptable ni que el empuje útil de 22,7 N por ventilador sea alcanzable.

Resultados: `CHEQUEOS.json`, `RESUMEN.json` y `VERIFICACION_STEP.json`. Reimportar sólidos válidos comprueba integridad geométrica del archivo, no fiabilidad mecánica ni capacidad de vuelo.

## Próximo cierre técnico

Dimensionar los actuadores y su transmisión dentro de la envolvente, verificar su movimiento y construir un mapa de fuerza/par/pérdida de presión frente a ambos mandos. El estudio ideal de cono de fuerzas de `../INFORME.md` solo puede sustituirse por prestaciones del mecanismo cuando exista ese mapa. Siguen pendientes el empuje reversible o las rutas que permitan cualquier actitud, la masa/energía integrada, la autonomía virtual y el régimen de alta velocidad.

## Corrección de orientación para el caso CFD

Al construir el dominio de fluido se detectó que la primera versión dibujaba los álabes neutros con la cuerda en el plano transversal al flujo. Se corrigió: a 0° mecánicos, la cuerda de 16 mm queda alineada con z (flujo), y el espesor de 1,5 mm es transversal. Se regeneraron los tres STEP y se repitieron posiciones y prismas de barrido. Las cotas conservadoras de barrido usan el mismo radio de esquina y siguen siendo aplicables. Los archivos actuales sustituyen las posiciones neutras anteriores; ningún ángulo mecánico se equipara a un ángulo efectivo del chorro.
