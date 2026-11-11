# Convergencia de presión a 600 km/h: 200 iteraciones insuficientes

El diagnóstico LTS terminó sus 200 iteraciones, con U/p/T finitos y p/T positivos en el campo final. **No pasó el cribado de convergencia.** Se inició una continuación desde ese campo, preservando íntegros los datos anteriores. El pseudotiempo no es tiempo de vuelo.

## Criterios y método

`CRITERIOS-CONVERGENCIA-LTS.json` fija objetivos numéricos elegidos para este estudio: residuos iniciales de la primera iteración exterior, deriva/rango de coeficientes por bloques y desajuste de masa normalizado con escala corporal. No son normas de certificación ni incertidumbres físicas. Se exigen además comparación de campos y sensibilidad de esquema, malla y dominio antes de una aceptación física.

Se examina el residuo inicial de la primera corrección exterior, evitando confundir el pequeño residuo de la última solución lineal con una solución global convergida. Los bloques de 25 iteraciones sirven para detectar deriva algorítmica; sus medias no son estadísticas físicas de flujo turbulento.

| Iteraciones | Coeficiente medio Fx de presión del iterado | Coeficiente medio My de presión del iterado |
|---|---:|---:|
| 1–25 | 1.131276 | -0.095398 |
| 26–50 | 0.989289 | -0.079790 |
| 51–75 | 0.843721 | -0.060037 |
| 76–100 | 0.677034 | -0.039956 |
| 101–125 | 0.515276 | -0.021883 |
| 126–150 | 0.366026 | -0.006785 |
| 151–175 | 0.230421 | 0.004422 |
| 176–200 | 0.110948 | 0.012047 |

Los coeficientes se normalizan con q·A y q·A·L, respectivamente. A=0,049774748 m², L=1,340 m y q≈17013,9 Pa. La tabla muestra deriva pendiente de resolver, **no una curva de arrastre aceptada**.

| Indicador, último bloque completo | Calculado | Objetivo elegido |
|---|---:|---:|
| Máximo residuo inicial de p | 0.00165002 | 1e-05 |
| Máximo residuo inicial de Ux | 0.00215683 | 1e-05 |
| Máximo residuo inicial de Uy | 0.00310864 | 1e-05 |
| Máximo residuo inicial de Uz | 0.00333009 | 1e-05 |
| Máximo residuo inicial de h | 0.00243666 | 1e-05 |
| Cambio máximo de media de coeficiente de fuerza entre últimos bloques | 0.119474 | 0,0001 |
| Cambio máximo de media de coeficiente de momento | 0.00762511 | 0,00001 |
| Desajuste global de masa / (rho·U·A corporal), máximo del último bloque | 1.70069 | 0,001 |

## Escala del balance de masa

El máximo desajuste relativo al gran caudal de entrada de toda la caja exterior es aproximadamente 0,001310 (0,131 %). Al normalizar el mismo desajuste con rho·U·A del cuerpo, cuya escala es 10,1623 kg/s, el máximo del bloque final resulta 1,701. Esto no es una medición del error local de flujo a través del cuerpo: es un indicador global con una referencia más pertinente a su tamaño. Muestra por qué una normalización basada solo en la caja grande puede ocultar un desajuste relevante. En LTS queda una evolución artificial de densidad; no se sustituye por una acumulación física.

## Cambio de campos entre iteraciones 125 y 150

Se conservaron ambas carpetas antes de la eliminación automática de campos antiguos. Sobre la misma malla se midieron los siguientes cambios máximos:

| Campo | Cambio máximo | Normalización declarada | Cambio normalizado |
|---|---:|---|---:|
| Velocidad | 32.4556 m/s | U∞ | 0.194734 |
| Presión | 4198.2 Pa | q∞ | 0.246751 |
| Temperatura | 5.02577 K | U∞²/(2Cp) | 0.363551 |

Son cambios numéricos entre iterados, no incertidumbre experimental ni evolución de vuelo. El lector de campos se verificó con valores conocidos y rechazo de truncamiento, número de celdas incorrecto y no finitud. Los hashes de los campos quedan en los JSON.

## Continuación y alcance

Se inició `avance_A_compresible_600kmh_LTS_cont_1000` desde el campo 200, con la misma geometría, contornos y controles locales. El contador nuevo se reinicia en cero; la procedencia registra las 200 iteraciones anteriores. Los primeros pasos de historial/amortiguación del reinicio pueden diferir de una ejecución sin interrupción. No se declara una comparación aislada de precisión temporal.

Proceso: contenedor `codex-aero-avance-compresible-600-lts-cont-v1`, sesión 54702, objetivo 1000 iteraciones nuevas. La prueba anterior, sesión 16295, terminó normalmente y no debe reiniciarse. El ensayo exterior de los álabes sigue separado, con sesión 23250.

Faltan desarrollo de presión, contraste experimental y sensibilidad numérica. La pared deslizante omite fricción turbulenta; no se han modelado puertas, propulsión, tomas ni trimado. No se extrapola a 1000 km/h, no se determina Mach crítico y no se demuestra que la geometría sea óptima.

Archivos: `CONVERGENCE_AUDIT.json`, `FINAL_FIELDS_AUDIT.json` y `campos_intermedios/` en la carpeta LTS original; `CAMBIOS_LTS_125_150.json` y `VERIFICACION_LECTOR_CAMPOS.json` en CFD. Código `auditar_convergencia_LTS.py`, `auditar_campos_finales_LTS.py`, `auditar_cambios_campos_LTS.py`, `foam_fields.py` y `continuar_avance_LTS_A.py`.
