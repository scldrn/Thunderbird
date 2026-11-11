# Candidato con ejes revisados: mejora estática y comprobación CAD

La pérdida de autoridad encontrada en el CAD inicial se reduce reorientando los módulos. Esta entrega conserva las posiciones de los centros de disco, el fuselaje, las áreas de paneles y las hipótesis de masa. Genera ensamblajes nuevos en `candidato_ejes/`; no sobrescribe el CAD anterior ni sus renders.

## Búsqueda y alcance

`optimizar_ejes.py` busca dos ángulos de una familia simétrica de ocho ejes mediante evolución diferencial. Objetivo: minimizar la mayor exigencia de empuje por unidad de peso entre las dos variantes, para aceleración adicional de 1 g omnidireccional y aceleración angular simultánea de 2 rad/s² desde reposo. Tres inicializaciones (17, 29 y 43): dos convergieron a valores próximos de 0,70423 y otra a 0,71391. Esto muestra dependencia de mínimos y NO prueba un óptimo global. Tampoco optimiza longitud, radio de brazos, posiciones axiales, retracción, potencia o masa de hardware.

Durante la búsqueda se congelaron CG e inercias iniciales. Después se regeneraron brazos y posiciones de módulos de acuerdo con los nuevos ejes, se recalcularon CG y tensor provisional, y se repitieron las 108 combinaciones estáticas con 1080 comprobaciones LP. Residuo máximo de ecuaciones normalizadas: 8,53e-14. No se realizó una segunda búsqueda con estas inercias actualizadas; se informa el comportamiento del candidato obtenido, no estacionariedad del problema acoplado.

Ángulos del candidato: theta=1,0431733879 rad y phi=2,3342806835 rad, según la convención exacta de `control.allocation`. Para evitar ambigüedad, los vectores unitarios de cada rotor y sus coordenadas están en cada `configuracion.json`.

## Resultados después de actualizar el CAD

Hipótesis de tabla: partidas de masa sin posición concentradas en CG; ninguna masa adicional aún desconocida; empuje firmado simétrico ideal; reserva angular 2 rad/s² simultánea.

| Variante objetivo | Presupuesto kg | Empuje/rotor, sostener toda orientación | Empuje/rotor, +0,5 g | Empuje/rotor, +1 g | Mayor inercia principal provisional kg·m² |
|---|---:|---:|---:|---:|---:|
| 5 kg | 5,498 | ±19,29 N | ±28,52 N | ±37,85 N | 0,4980 |
| 10 kg | 10,685 | ±38,50 N | ±55,59 N | ±73,70 N | 1,5322 |

Los presupuestos no cambian porque las masas asignadas a brazos y módulos estaban fijadas, no dimensionadas desde resistencia. Cambiar su forma no demuestra masa real constante. La masa de palas/servos/ESC todavía se concentra en la envolvente asignada al módulo: las inercias siguen siendo aproximaciones, no mediciones del conjunto real.

Estos requisitos NO son prestaciones demostradas de un motor. No se dispone de mapas positivos/negativos completos del módulo propuesto; en 10 kg sigue sin seleccionarse hardware. El resultado excluye reacción de rotor, giroscopía, aire incidente, interferencias de flujo, consumo, temperatura y respuesta del mecanismo de paso variable. No acredita giros bruscos reales ni autonomía.

## Geometría desplegada comprobada

`holguras_candidato.py` reimportó ambos STEP y comprobó validez de sólidos. Hay ocho intersecciones intencionales brazo-módulo por variante y ninguna otra entre las envolventes examinadas; los barridos no atraviesan el fuselaje. Distancias calculadas entre sólidos nominales:

| Variante | Distancia mínima entre barridos de rotores | Menor distancia entre barrido y otro sólido examinado |
|---|---:|---:|
| 5 kg | 163,62 mm | 43,00 mm, módulo a su propio barrido |
| 10 kg | 206,15 mm | 54,18 mm, módulo a su propio barrido |

La separación módulo-barrido refleja un tramo de eje/buje todavía no resuelto en el CAD de ingeniería; no significa que haya una conexión mecánica diseñada. Los ejes y bujes dibujados en renders son ilustrativos. No se incorporan tolerancias, flexión ni barridos durante el plegado; tampoco se interpreta la separación entre discos como ausencia de interferencia aerodinámica.

## Siguiente requisito para avanzar

Actualizar la distribución real de masas de rotor, buje y servo, y enlazar la asignación de fuerzas con mapas firmados y su respuesta temporal. Diseñar la retracción antes de afirmar compatibilidad con crucero rápido. Cerrar las masas faltantes y recalcular el flujo instalado sigue siendo indispensable para el objetivo completo.

Los renders previos muestran la disposición anterior y quedan como documentación de esa iteración, no como visualización de los ejes revisados.
