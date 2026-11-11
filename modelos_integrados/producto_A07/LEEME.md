# A07 — Estudio de apertura para ventiladores internos

Arquitectura A confirmada. Los cuatro rotores permanecen fijos dentro del fuselaje. Esta revisión estudia las ocho compuertas, corrige los extremos de las camisas y exporta tres estados: cerrado, elevado y abierto. Es un estudio de recorrido geométrico, no un mecanismo fabricable resuelto.

## Hallazgos y cambios
La auditoría del A06 cerrado detectó solapes nominales entre tapas y camisas, de aproximadamente 584–691 mm³ por pareja superior y 592–668 mm³ por pareja inferior. Son intersecciones del CAD; no mediciones físicas. cerrado.log conserva las ocho parejas. Las verificaciones locales anteriores de aletas y posición de rotores no examinaban estas parejas.

Una apertura directa por giro en el primer eje lateral candidato también atravesaba la envolvente durante posiciones intermedias. cribado_apertura.json conserva ese candidato rechazado, sin atribuir el resultado a todas las bisagras posibles.

En A07, las camisas se recortan con un loft interior de secciones desplazadas 2 mm. No es una distancia normal constante ni una tolerancia de fabricación garantizada. No se modifica la posición de los rotores. El recorte es geométrico; sus pérdidas y continuidad aerodinámica requieren análisis.

## Trayectoria candidata, referencia 5 kg
1. Traslación de cada tapa 10 mm hacia el exterior: +Z en las superiores, −Z en las inferiores.
2. Giro de 110° hacia el exterior alrededor de un eje longitudinal que se traslada con la tapa. propuesta_elevacion.json contiene los ejes y signos exactos.

Los desplazamientos se escalan geométricamente con (m/5)^(1/3). Para 2/5/10 kg son aproximadamente 7,37/10/12,60 mm. Los 110° son una pose de estudio, no un recorrido especificado de servo ni una condición de vuelo validada. La búsqueda utilizó alturas discretas y añadió 5 mm al primer candidato que pasó; no demuestra elevación óptima o mínima global.

## Verificación
VERIFICACION_RECORRIDO.json registra las posiciones muestreadas y las intersecciones. Se comprueba contra la envolvente de referencia menos las ocho tapas originales, las aletas/carenados posteriores reales y las demás tapas móviles en aperturas simultáneas. Se comprueban por separado las parejas reales de tapa cerrada/camisa recortada. Este cribado no es un barrido continuo ni una auditoría de todos los componentes internos, deformaciones o tolerancias. Los tres STEP por escala se reimportan y se comprueba validez de sus 208 piezas. La evaluación del recorrido se hace en la referencia 5 kg; las otras dos son semejanzas geométricas.

## Qué falta
No hay todavía guías, bisagras, soportes, cierres, sellos, cableado o actuadores de compuerta dimensionados. La trayectoria impone dos coordenadas cinemáticas; falta sintetizar y alojar el mecanismo que las produzca. Los ejes de movimiento están documentados como geometría de construcción, no como herrajes instalados. No se afirma que todos los actuadores quepan, que las tapas no obstruyan el flujo, o que el dispositivo pueda volar. La apertura está destinada al estudio de baja velocidad; no se valida su uso en avance rápido.

Pendientes también: empuje/potencia, cierre de masa, propulsión axial, estructura, aeroelasticidad y control. Ninguna prestación del A06 se considera verificada por este CAD. Los solvers CFD pausados no se reanudaron.

## Archivos
Cada escala contiene A07_cerrado.step, A07_elevado.step y A07_abierto.step. El código y los JSON permiten reproducir la propuesta. base_A06 contiene el origen nominal. Las imágenes se renderizan directamente desde STEP, sin generador de imágenes por IA.
