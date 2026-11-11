# C02: segunda malla y semilla transferida

4 de noviembre de 2026. Sensibilidad numérica en preparación; no se aceptan prestaciones físicas.

## Geometría y mallado

Se conserva el mismo STEP del banco interno pasivo y el mismo campo de distancias físicas de gradación. `Mesh.MeshSizeFactor=0.75` reduce globalmente las longitudes objetivo. No se incorporan prismas ni se cambia el modelo de pared.

| Magnitud | Malla inicial | Segunda malla |
|---|---:|---:|
| Tetraedros | 581.786 | 1.283.005 |
| Razón de número de celdas | 1 | 2,20529 |
| Razón efectiva de longitud por conteo volumétrico | 1 | 0,768266 |
| STEP | Identificado | Misma huella SHA-256 |

La razón efectiva es `(N_inicial/N_fina)^(1/3)`, una descripción global; no demuestra refinamiento idéntico en cada celda ni un régimen asintótico de error. Dos niveles no bastan para declarar un GCI observado o independencia de malla.

`neutro_malla_r2_factor075/MALLA.json` verifica tetraedros positivos y discrepancia relativa de volumen CAD de 1,11313e−5. La conversión inicial falló por ausencia de `system/controlDict`; se conservan entrada, registro y contenedor detenido. Se reutilizó la malla idéntica en `neutro_malla_r2_factor075_conversion_r2`, preparando primero los diccionarios del caso. No se remalló para ocultar el fallo.

La segunda conversión pasa `checkMesh -allGeometry -allTopology`, con 13 grupos de pared, no ortogonalidad máxima 69,8825°, aspecto máximo 8,33205 y skewness máximo 0,873145. Esto acredita los controles de geometría/topología ejecutados, no la precisión de cargas, pared o separación. El contenedor auxiliar quedó detenido sin ejecutar flujo.

## Transferencia y nuevo cálculo

`inicializar_malla_fina.py` usa la misma imagen OpenFOAM 13 y `mapFields -consistent -mapMethod interpolate -sourceTime 1200 -noFunctionObjects`. El código instalado confirma las opciones `mapNearest`, `interpolate` y `cellPointInterpolate`; no se supone la sintaxis de otra distribución de OpenFOAM. Los campos se transfieren desde r9 a un caso distinto con contador inicial 0.

`neutro_fino_inicializacion_r1/INICIALIZACION_VERIFICADA.json` verifica los cinco campos requeridos con la cardinalidad de la malla nueva, finitud y turbulencia no negativa. La velocidad máxima de la semilla es 34,4341 m/s, por debajo del cribado Mref 0,3. La transferencia no se presenta como conservativa ni como verificación independiente de cobertura completa. Se conserva la semilla uniforme anterior. La convergencia del caso grueso **no se transfiere**.

`neutro_fino_r1_mpi4` inicia una solución independiente acotada hasta 100 iteraciones, desde esa semilla, con los esquemas, relajaciones, condiciones y SST del pasivo r9. Se observaron cuatro procesos `foamRun -parallel` y el inicio de la primera iteración. Consultar proceso y `EJECUCION.json` antes de asumir actividad o terminación. No son 100 segundos de vuelo.

## Qué falta

Al terminar: reconstruir 80/100, revisar campos/residuos/continuidad/deriva y decidir si extender antes de comparar con r9. Después, balance CV y flujo mecánico con las mismas convenciones, distribución de yPlus y diferencias de cargas/presión. No interpretar cambios entre soluciones sin convergencia como error de malla puro. Quedan abiertos resolución de pared, régimen de error, dominio, rotor y exterior. Este caso pasivo no contiene fuente de ventilador ni predice estacionario, vuelo omnidireccional o 600–1000 km/h.

## Actualización: primeras100iteraciones terminadas

El solver y la reconstrucción80/100 terminaron con salida0. `neutro_fino_r1_mpi4/AUDITORIA_ARRANQUE.json` pasa Mach, continuidad y deriva, pero falla residuos: p=2,23299e−3, Ux/Uy/Uz=6,48026e−4/7,13788e−4/3,11598e−4, k=5,17265e−4 yomega=1,03050e−4.

La presión estática entrada–salida es194,183Pa y la fuerza Z sobre paredes−1,051879N. No se atribuyen sus diferencias respecto a r9 exclusivamente a la malla: entre80/100 hay cambios locales de velocidad de hasta12,0086m/s, RMS aritmético0,120323m/s. Esos datos se retienen completos; finitud y cargas globales estables no equivalen a convergencia de todo el campo.

Se inició `neutro_fino_r2_mpi4_200` desde100 hasta200, conservando geometría, malla, contornos, SST, esquemas y relajación. Consultar proceso real; después de reconstruir180/200 se repetirán los mismos criterios antes de una comparación de malla aceptada.
