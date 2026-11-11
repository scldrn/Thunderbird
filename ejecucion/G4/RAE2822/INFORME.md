# Benchmark transónico RAE2822: malla verificada y piloto

3 de noviembre de 2026. Se resolvió la calidad de la conversión a volúmenes finitos conservando la geometría del perfil y del dominio. La malla r4 pasa `checkMesh -allGeometry -allTopology` sin relajar umbrales. El piloto de flujo es independiente de C02; ni este documento ni la malla acreditan velocidad del vehículo.

## Procedencia y condiciones

El [estudio 4 de NASA/NPARC](https://www.grc.nasa.gov/www/wind/valid/raetaf/raetaf04/raetaf04.html) proporciona una malla C 369×65 y datos de presión. Su archivo experimental especifica Mach 0,729 y α=2,31°, con Re de referencia 6,5 millones. No mezclar estos valores con los nominales 0,725/2,92° de la página general del caso 6. Los archivos originales están en `../../../fuentes/benchmark_RAE2822/`; sus huellas figuran en los manifiestos.

Se adopta cuerda 0,3048 m, p∞=108987,773 Pa y T∞=255,5556 K a partir de las condiciones del estudio. Con gas perfecto R=287,05287 J/(kg K) y γ=1,4 se calculan U∞=233,6228 m/s y ρ∞=1,485697 kg/m³. La viscosidad de referencia 1,62759865×10⁻⁵ Pa s se fija para reproducir Re; no es una medición propia. La extrusión de 0,003048 m tiene condiciones `empty` y representa flujo 2D, no una envergadura experimental finita.

## Modificaciones y auditoría geométrica

La identificación de los nodos duplicados del corte de estela produce conectividad conforme. La conversión directa r1 tiene 23.552 hexaedros, pero celdas de estela muy anisótropas y caras casi tangentes al enlace entre centros. No se ejecutó flujo en r1–r3.

R2 conserva las primeras 20 filas radiales del perfil de NASA y remalla el exterior con triángulos. R3 subdivide los extremos de esa franja para evitar un salto fuerte de tamaños. R4 subdivide también las columnas largas; mantiene los polígonos de pared, filas radiales y contorno exterior, añadiendo vértices sobre sus segmentos. La malla resultante es propia: no es reproducción de la discretización original de WIND.

| Revisión | Celdas | Aspecto máx. | No ortogonalidad máx. | Determinante mín. | `checkMesh` |
|---|---:|---:|---:|---:|---|
| r1 original convertida | 23.552 | 640.399 | 89,99° | 2,47×10⁻¹¹ | Rechazada |
| r2 híbrida | 113.966 | 1180,31 | 63,72° | 6,15×10⁻⁵ | Rechazada |
| r3 unión refinada | 117.660 | 1180,31 | 45,38° | 6,15×10⁻⁵ | Rechazada |
| r4 subdividida | 365.478 | 98,64 | 36,58° | 0,007087 | Mesh OK |

R4 contiene 45.640 hexaedros y 319.838 prismas, con 413.822 puntos. El volumen integrado por polígonos y convertido a OpenFOAM es 0,585458041651 m³; el cierre relativo geométrico independiente es aproximadamente 2×10⁻¹⁴. Todas las celdas planas son convexas, positivas, y todas las aristas no compartidas corresponden a fronteras declaradas. Persisten avisos informativos de aristas pequeñas por la resolución micrométrica de pared. La escala mínima no es prueba de resolución viscosa suficiente.

`AUDITORIA_MALLAS.json` conserva cifras y huellas de los cuatro registros. `COMPARACION-MALLAS.png` muestra la discretización, no un campo calculado.

## Piloto físico y numérico

`preparar_caso.py` utiliza OpenFOAM 13, solver `fluid`, gas perfecto, entalpía sensible, Sutherland y RANS k–ω SST. La intensidad turbulenta 0,1% y νt/ν=1 son supuestos de arranque, no datos experimentales. Se prescribe pared sin deslizamiento y adiabática; su tratamiento real debe evaluarse mediante y+ y sensibilidad. La conductividad de `sutherlandTransport` sigue la expresión Eucken de la implementación: κ=μ(1,32Cv+1,77R). No se declara Pr=0,72: ese parámetro independiente no se lee en este modelo. Véase la [implementación oficial](https://cpp.openfoam.org/v13/classFoam_1_1sutherlandTransport.html).

El arranque usa `localEuler`, upwind, presión transónica y 100 iteraciones acotadas. Es una prueba de arranque y coste, no un esquema final ni 100 segundos físicos. El constructor de modelos pasó con salida cero; la ejecución se registra en `piloto_r4_hibrido_resuelto/EJECUCION.json`. Verificar además el proceso real antes de continuar: un archivo de estado por sí solo no prueba que siga activo. El ejecutor guarda campos 80/100 y detiene su contenedor al terminar.

## Criterios pendientes y reproducción

`auditar_piloto.py` comprueba campos finitos, Mach local, gas perfecto, residuos iniciales, deriva de cargas, flujo neto exterior, cambios de campo y y+. Reconstruye independientemente la fuerza de presión usando la condición de pared `zeroGradient`. Interpola los 103 datos experimentales sobre la longitud de arco del polígono completo, separando ambas caras y sin extrapolar el punto del borde de ataque. Una comparación de arranque no acepta cargas, choque ni validación.

Faltan convergencia iterativa, estabilidad del choque, sensibilidad de malla/esquema/dominio, tratamiento de pared y turbulencia/transición. Tampoco sustituye el contraste tridimensional ONERA M6 ni la CFD del vehículo, tomas, tapas y aletas. T21 y G4 permanecen abiertos.

Desde la raíz, el generador r4 se reproduce con `.venv-cad/bin/python investigacion-aeronautica/ejecucion/G4/RAE2822/preparar_malla_hibrida.py --case RUTA_NUEVA --refine-cap --max-core-aspect 100`. Los ejecutores rechazan sobreescribir o duplicar casos: inspeccionar el estado y usar una revisión identificada para cualquier modificación.

## Resultado terminal del piloto y continuación identificada

El piloto r4 terminó 100 iteraciones, salida0, campos finitos/positivos, 371s de reloj del solver y sin OOM. No convergió: el primer residuo de presión de las últimas20 alcanza0,00219 y la deriva entre medias de20 es0,00571 enCL y0,01032 enCD. Entre80/100, ΔU máximo146,33m/s y Δp máximo92958Pa. Los valores diagnósticos finales CL=0,21716 yCD=0,18548 no son coeficientes aceptados. Mach local máximo0,7784.

Se corrigió una convención de entrada detectada al revisar la figura: el archivo NASA experimental almacena **−Cp**, con recorrido extrados→borde de ataque→intrados, contrario al orden de la malla. El [archivo oficial CFPOST](https://www.grc.nasa.gov/www/wind/valid/raetaf/raetaf04/cfpost.cp.com) prescribe `Cp scale -1`. `verificar_convencion_cp.py` comprueba el orden con los datos publicados WIND, sin usar el CFD propio para elegirlo: RMS0,10683 en el orden correcto frente a1,03526 en el contrario, en la ordenada publicada. Es un contraste de convención, no validación del solver propio.

La auditoría corregida de los103 puntos da **RMS de error Cp=1,19972**; no reproduce todavía el experimento. El valor anterior1,36140, suCSV y figura se conservan como `r1_CONVENCION_INVALIDA` y se retiran como comparación válida. Los CSV históricos de entrada con encabezadoCp contienen la ordenada cruda−Cp; el auditor corrige signo y recorrido explícitamente. No se modificaron los archivos originales de NASA ni los campos de flujo.

Se preparó una continuación r5 separada desde el campo100 hasta600, elevando únicamente el máximo Courant local0,2→1 además del intervalo de ejecución. Se conservan malla, modelos y esquema upwind. `piloto_r5_continuacion_Co1/DERIVACION.json` identifica la procedencia; `EJECUCION.json` y `OBSERVACION_PROCESO.json` permiten localizar el proceso, pero requieren verificar su vigencia. La siguiente auditoría debe usar los campos580/600. La corrida queda acotada y su ejecutor detendrá su propio contenedor al terminar.
