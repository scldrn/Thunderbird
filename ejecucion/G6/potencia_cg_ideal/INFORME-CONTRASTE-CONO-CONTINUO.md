# Contraste de los conos de empuje con optimización continua

Se contrastó el método de rayos y programación lineal (LP) con un modelo independiente de cono de segundo orden (SOCP) usando Clarabel 0.11.1. Para cada ventilador, el SOCP exige simultáneamente `sqrt(Fx²+Fy²) ≤ tan(ángulo)·Fz`, `Fz ≥ 1 N` y `sqrt(Fx²+Fy²+Fz²) ≤ capacidad común`. Minimiza esa capacidad con las mismas ecuaciones ideales de fuerza y momento, masas hipotéticas y palancas del análisis anterior. La formulación de conos sigue la [documentación de Clarabel](https://clarabel.org/stable/python/getting_started_py/). Es un cono geométrico continuo ideal, no un mapa físico de la instalación.

Se calcularon los 64 vértices conjuntos de aceleración ±0,25 g y momento ±0,5 N·m, para 36 distribuciones hipotéticas de masa y ángulos de 35°, 40° y 45°: **6.912 problemas**. Clarabel informó 6.624 soluciones y 288 estados de inviabilidad primal en su formulación numérica; el mayor residuo primal reconstruido fue 3,57e−7 en unidades mixtas. La condición de zona de ubicación del equipo restante se comprobó por separado.

| Reserva | Equipo genérico | Certificados de caja y zona, 35°/40°/45° | Capacidad máxima de las cajas resueltas a 35°, N por módulo |
|---:|---|---|---:|
| 38 mm | x=0 | 0/6 en cada ángulo | 21,335–21,479 |
| 60 mm | x=0 | 0/6 en cada ángulo | 23,228–23,286 |
| 80 mm | x=0 | 0/6 en cada ángulo | caja sin solución completa |
| 38 mm | CG equilibrado | 5/6 en cada ángulo | 18,364–18,479 |
| 60 mm | CG equilibrado | 5/6 en cada ángulo | 17,964–18,066 |
| 80 mm | CG equilibrado | 5/6 en cada ángulo | 18,228–18,313 |

Los resultados mantienen el patrón de clasificación anterior para capacidad supuesta de 21 N. Un caso equilibrado por grupo queda fuera de la zona supuesta para el equipo genérico. No se verifica que componentes reales quepan o puedan lograr la potencia y las fuerzas requeridas. Las masas se completaron aritméticamente a 5 kg; no son un presupuesto de hardware validado.

La comprobación independiente `verificar_matriz_cono.py` contrastó las 6.624 soluciones LP guardadas contra SOCP: ninguna capacidad continua superó a su correspondiente solución LP más allá de 2e−5 N; la mayor diferencia observada LP−SOCP fue 0,117 N. También confirmó la monotonicidad angular de cada tripleta continua resuelta con tolerancia 2e−5 N. Los dos casos antes no clasificados por HiGHS fueron informados como inviables por Clarabel; esa clasificación es numérica y no es una demostración física. Tres pruebas analíticas pasaron: estacionario simétrico, una fuerza fuera de cono y relajación/monotonicidad frente a LP.

`CONO_CONTINUO.json` contiene fuerzas, estados, residuos y huellas de código y fuente. Reproducción con el entorno temporal de esta sesión:

```sh
PYTHONPATH=/private/tmp/codex-aero-scipy OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/ejecucion/G6/potencia_cg_ideal/verificar_cono_continuo.py
PYTHONPATH=/private/tmp/codex-aero-scipy OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /Users/sam/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 investigacion-aeronautica/ejecucion/G6/potencia_cg_ideal/comparar_cono_continuo.py
python3 investigacion-aeronautica/ejecucion/G6/potencia_cg_ideal/verificar_matriz_cono.py
```

El entorno temporal incluye NumPy 2.5.4, SciPy 1.18.1 y Clarabel 0.11.1 y puede desaparecer. El método no incluye fuerzas y pares aerodinámicos acoplados de los conductos, interacción, consumo, retrasos, viento ni estructura: verificar la optimización no valida la aeronave. No se reanudaron CFD pausados.
