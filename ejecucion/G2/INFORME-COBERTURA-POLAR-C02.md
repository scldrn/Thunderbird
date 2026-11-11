# Cobertura de datos de pala y condición geométrica C02

4 de noviembre de 2026, hora de Bogotá. Este análisis identifica dónde faltan datos para el modelo de pala; **no estima prestaciones instaladas ni demuestra que un rediseño funcione**. A07 sigue como referencia canónica y C02 como candidata de integración.

## Datos comprobados

El [archivo SD8020.DRG de UIUC](https://m-selig.web.engr.illinois.edu/pd/pub/lsat/vol1/SD8020.DRG), conservado en `../../fuentes/uiuc/`, contiene tablas de sustentación y arrastre con Reynolds medios 61.400, 101.500, 203.300 y 304.800. Sus intervalos angulares son diferentes por bloque. La implementación actual de `bem_hover.py` interpola entre los bloques y señala la extrapolación; la interpolación no equivale a nuevos ensayos. UIUC documenta la procedencia y las condiciones de distribución en su [página de datos](https://m-selig.web.engr.illinois.edu/pd.html); se conservan licencia y manifiesto locales.

El [archivo SD8020.LFT](https://m-selig.web.engr.illinois.edu/pd/pub/lsat/vol1/SD8020.LFT) contiene **datos adicionales de sustentación**, desde Re medio 30.500 y hasta ángulos alrededor de 17,7°. No proporciona el coeficiente de arrastre requerido por la ley de potencia. Las ocho series contienen una rama de ángulos crecientes y otra decreciente: ordenarlas juntas y aplicar una interpolación que exija valores crecientes podría borrar la distinción. No se atribuye una causa concreta a sus diferencias sin documentación experimental adicional.

`dominio_polar_C02_r2/RAMAS_LIFT.json` compara ambas ramas dentro de su intervalo común. Ejemplo calculado por interpolación lineal: a Re medio 30.500 y 5°, la diferencia Cl(creciente)−Cl(decreciente) es **−0,07358**. Esta comparación no identifica histéresis como mecanismo ni permite inferir el comportamiento de la pala giratoria.

## Condición cinemática deducida

Por definición, con velocidad relativa local W, cuerda c, viscosidad cinemática ν y velocidad del sonido a, `Re = W·c/ν` y `M = W/a`. Por tanto, exigir simultáneamente `Re ≥ Re_min` y `M ≤ M_lim` implica `c ≥ Re_min·ν/(M_lim·a)`. Las definiciones y el papel de la similitud se resumen en [NASA Glenn](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/similarity-parameters/). La relevancia de resolver el comportamiento de perfiles a bajo Reynolds se estudia también en el [artículo de NASA sobre evaluación de perfiles](https://rotorcraft.arc.nasa.gov/Publications/files/1.c037023.pdf); ese estudio no valida este rotor.

Con **supuestos** ν=1,46×10⁻⁵ m²/s, a=340,3 m/s, Re_min=61.400 de la tabla combinada DRG y M_lim=0,3, resulta una cuerda mínima **8,781 mm**. Mach 0,3 es el límite preliminar escogido para este cribado, no un límite físico universal de compresibilidad. Esta condición se refiere exclusivamente a utilizar ese límite y el intervalo de Reynolds de DRG: existen datos LFT a Reynolds menores, pero carecen de arrastre.

Para la cuerda nominal interpolada de las 64 secciones guardadas de C01, con radio 41 mm y cubo sellado 0,315R, la cuerda queda por debajo de 8,781 mm aproximadamente desde **r/R=0,9205 hasta 1**. La zona representa **11,60 % del tramo radial activo y 16,94 % de su área anular**. Esto es una cuenta geométrica: no es porcentaje de empuje, de par, de pérdida ni del área real de pala. Se extrapola la última cuerda guardada hasta la punta; no se ha recuperado la sección exacta del CAD continuo.

Por tanto, con esa geometría nominal y esos supuestos, no puede mantenerse simultáneamente `Re ≥ 61.400` y `M ≤ 0,3` en toda esa región cambiando solo velocidad o torsión. Esta conclusión no impide usar otras mediciones, modelos adecuados de compresibilidad o una geometría diferente, y no demuestra por sí misma que el rotor sea inviable.

## Cobertura de tres puntos prescritos

Se reclasificaron los 21 puntos del cubo 0,315R guardados anteriormente, con 128 anillos por punto. Se reproducen sus marcas de interpolación y se comprueban velocidad relativa, Reynolds y Mach. La velocidad axial de disco y el remolino cero son **entradas impuestas**, no un punto de equilibrio calculado. Las fracciones de la tabla están ponderadas por área anular; las causas pueden solaparse.

| RPM supuestas | Velocidad axial impuesta | Área con Re menor que 61.400 | Área fuera del intervalo angular DRG | Área con M > 0,3 | Área conjunta dentro de DRG y M ≤ 0,3 |
|---:|---:|---:|---:|---:|---:|
| 23.116 | 20 m/s | 54,16 % | 7,01 % | 0 % | 45,84 % |
| 34.674 | 20 m/s | 10,96 % | 100 % | 60,65 % | 0 % |
| 46.231 | 20 m/s | 4,50 % | 100 % | 83,01 % | 0 % |

`dominio_polar_C02_r2/COBERTURA.csv` conserva los 21 puntos; `RESULTADOS.json` registra supuestos, comprobaciones y huellas. El cálculo de los intervalos de cuerda usa integración exacta por tramos lineales y pasó tres referencias analíticas. `auditar_ramas_lift_C02.py` comprueba interpolaciones sintéticas y nunca extrapola ángulos. Estos contrastes verifican el procesamiento de datos, no la validez aerodinámica del modelo.

## Decisiones de trabajo

1. **No seleccionar RPM ni potencia** a partir de esta tabla: no incluye balance de inducción, pérdidas de punta, interacción con conducto o motor, ni datos de arrastre válidos para toda la pala.
2. Precisar las secciones reales del STEP y sus tolerancias antes de fijar el área problemática. Explorar cambios de cuerda y torsión como candidatos separados, revisando solidez, interferencias, estructura e inercia. Aumentar cuerda no garantiza una mejora global.
3. Buscar o calcular datos de arrastre pertinentes a Re ≈20.000–100.000 y al rango angular requerido, con una evaluación de incertidumbre y contraste independiente. Aprovechar las ramas LFT para contrastar sustentación sin presentarlas como arrastre ni asignar extrapolaciones a datos medidos.
4. Solo después combinar las polares pertinentes con modelos de rotación, interacción y flujo instalado. Mantener la validación experimental y el mapa de fuerza/par/potencia como pendientes.
