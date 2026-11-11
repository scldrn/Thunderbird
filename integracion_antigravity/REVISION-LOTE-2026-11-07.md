# Revisión del primer lote de Antigravity

Cuatro conversaciones distintas terminaron con `SUCCESS` y sus intervalos se
solaparon: iniciaron alrededor de las 21:02:31 y terminaron entre 21:03:37 y
21:05:54, hora de Bogotá, el 7 de noviembre de 2026. Los registros y respuestas
íntegras están en `resultados/20261108T020231Z_9ce7f4d6/`. Los cuatro agentes
recibieron tareas independientes con archivos de entrada concretos, modo de
planificación y reglas de denegación de escritura y comandos. El estado
`SUCCESS` solo acredita que cada proceso produjo una respuesta.

## Hallazgos útiles y revisión crítica

| Tarea | Aporte revisado | Límite o corrección |
|---|---|---|
| Flujo | Resume que r9 pasa los umbrales fijados, mientras la malla fina a 800 falla Ux/Uy/k; en ambos casos quedan cambios locales y sensibilidad de pared. | No atribuir la diferencia de RMS solo a más iteraciones: también cambia la malla. El informe de r9 es anterior a auditorías posteriores de la fuente de 1 N; la sugerencia de esperar su primer resultado ya está superada. |
| Masa y energía | Señala que una demanda vertical o de control puede coexistir con el avance y debe sumarse a la potencia de batería cuando corresponda. | Se rechaza la afirmación de que la arquitectura eléctrica queda «físicamente descartada» en general. Los umbrales dependen de propiedades de pack, masa, misión, eficiencia y arrastre supuestos. Los 54 registros son reservas/interfaces sin masa asignada, no 54 piezas necesariamente existentes. |
| Propulsión | Reproduce la falta de cobertura conjunta de polar/Re/Mach, y distingue convergencia de cuadratura de validación física. | Una nueva polar o medición del CAD es una propuesta; no se ha ejecutado ni sustituye la validación rotor–conducto. |
| Control | Identifica una sensibilidad útil al brazo vertical entre fuerza y CG, además de la diferencia entre estaciones C02 y la simulación anterior. | El brazo cero es una hipótesis explícita del modelo LP, no un defecto probado por sí mismo. El centroide geométrico parcial no es un CG físico y no prueba contradicción. Tampoco se acepta que cualquier ráfaga cause necesariamente pérdida de control. |

Para cuantificar el primer aporte se creó el cribado independiente
[`potencia_simultanea_c02/INFORME.md`](../ejecucion/G1/potencia_simultanea_c02/INFORME.md).
La sensibilidad ideal de brazo vertical se estudió por separado en
[`autoridad_C02/INFORME.md`](../ejecucion/G6/autoridad_C02/INFORME.md): sigue
requiriendo posiciones y fuerzas instaladas identificadas.

Las conversaciones consumieron según sus registros aproximadamente 31.340,
49.809, 32.568 y 42.631 tokens. La cuota o el coste dependen de la cuenta y el
plan: estos contadores no establecen un precio. No se ejecutaron ni reanudaron
los CFD históricos pausados.
