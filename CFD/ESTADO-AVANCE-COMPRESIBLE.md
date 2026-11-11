# Diagnóstico compresible de avance de A a 600 km/h

## Modelo y alcance

Se conserva la malla exterior de la envolvente cerrada A: 326.013 tetraedros, antes de aberturas, insertos y detalles. El CAD aprobado no se modificó. El solver es `fluid` de OpenFOAM Foundation13, gas perfecto, entalpía sensible, transporte constante y pared deslizante adiabática. Se usa el modelo laminar por defecto para este diagnóstico de presión: no hay modelo de fricción turbulenta ni arrastre total aceptado.

Condiciones supuestas: U∞=166,6667 m/s, p∞=101325 Pa, T∞=288,15 K, R nominal=287,05287 J/(kg·K), gamma nominal=1,4, mu=1,7894e−5 Pa·s y Pr=0,72. Los contornos exteriores usan freestreamVelocity/freestreamPressure y temperatura inletOutlet. La configuración se contrastó con los ejemplos instalados `fluid/aerofoilNACA0012Steady`, `fluid/aerofoilNACA0012` y la rama transónica de `isothermalFluid/correctPressure.C`.

La comprobación previa cargó el paquete termodinámico y registró rho inicial=1,224999285 kg/m³, presión/temperatura positivas y fuerza de presión uniforme nula con pRef=p∞. Esto verifica lectura y una identidad de integración, no valida la solución aerodinámica.

## Intentos conservados y descartados

1. `avance_A_compresible_600kmh_diag`: el arranque estacionario directo diverge y aborta al intentar la iteración 3. El registro llega a temperatura negativa y velocidades de miles de m/s. Se rechaza íntegramente para estimar cargas. La causa numérica única no está aislada; no demuestra inviabilidad geométrica.

2. `avance_A_compresible_600kmh_Euler_diag`: error de preparación por referencia adelantada a p en pFinal; no inicia el bucle temporal. El posprocesado ausente también dejó incompleta la actualización automática de estado; se corrigió el estado mediante auditoría del registro y el lanzador ya tolera ausencia de resultados.

3. `avance_A_compresible_600kmh_Euler_diag_v2`: falta la entrada del solucionador de rho; falla al entrar en el primer paso, sin completar ninguno. La corrección se contrastó con el diccionario transitorio del ejemplo instalado. Ningún campo de estas ejecuciones fallidas se reutilizó para arrancar v3.

Los registros, diccionarios y auditorías de rechazo se conservan por separado. Estos errores de preparación y estabilidad no se cuentan como curvas de arrastre o validación física.

## Prueba transitoria corregida

`avance_A_compresible_600kmh_Euler_diag_v3` parte de campos uniformes originales, con Euler, convección upwind conservativa, dos iteraciones exteriores y dos correcciones de presión, sin relajación estacionaria y con Courant máximo 0,2. Paso inicial 1e−7 s y máximo 1e−6 s. El objetivo es solo 1e−4 s de tiempo físico. Terminó y se auditaron los campos finales con valores positivos de p/T en todas las celdas.

El tiempo de recorrido convectivo por longitud del cuerpo es aproximadamente 0,00804 s; el objetivo diagnóstico abarca solo 0,0124 recorridos. No es una simulación de vuelo desarrollado ni de transición del vehículo. El contador de los casos estacionarios anteriores representa iteraciones; el de v3 representa segundos físicos.

Solver v3 terminado: contenedor `codex-aero-avance-compresible-600-euler-v3` detenido y sesión 24226 completada. El lanzador incorpora vigilancia de valores no físicos y registra estados terminales. `monitor_compresible.py` cuenta bloques con ClockTime, no simples cabeceras de pasos intentados. `auditar_avance_compresible.py` ya verificó los campos finales y el tiempo alcanzado; la auditoría numérica no acepta cargas estacionarias.

Los extremos separados de U y T permiten calcular una cota numérica de Mach con las constantes declaradas. No es el máximo puntual medido, no determina el Mach crítico y no sustituye el cálculo punto a punto sobre campos guardados. Tampoco se inferirá Mach local de Cp durante el arranque mediante una relación isentrópica estacionaria.

## Cierre pendiente

Finalizar y auditar este arranque; comprobar límites termodinámicos y balances; avanzar a una solución desarrollada de presión y demostrar sensibilidad de esquema, malla y dominio, además del contraste experimental. El paso local (localEuler) está soportado por el solver instalado y se revisó en `angledDuctLTS` y `setRDeltaT.C` como opción para converger el estado estacionario; no se activó en este ensayo físico ni se presentan sus contadores como tiempo real.

Después se requiere un modelo viscoso resuelto, instalación de puertas/tomas/propulsión, incidencia y trimado para evaluar arrastre total y estabilidad. No se acepta velocidad máxima, Mach crítico/divergencia o geometría óptima a partir de este diagnóstico. El ensayo separado del chorro de álabes sigue activo en su contenedor original.

## Auditoría terminal del arranque y nueva rama LTS

El arranque v3 completó 144 pasos hasta t=0,0001 s. Se comprobaron U/p/T finitos en las 326.013 celdas, con temperaturas 269,164–308,263 K y presiones 63.006,9–123.208,8 Pa. El máximo Mach interior calculado con las constantes declaradas es 0,64599; ninguna celda interior supera uno. Esto no determina el Mach crítico ni resuelve todos los extremos superficiales.

La fuerza instantánea de presión al terminar es aproximadamente (1030,78; 1,83; −47,52) N. No se interpreta como arrastre/lift de crucero: corresponde a un arranque que solo recorrió 0,0124 longitudes. No se dimensionará propulsión con esa fuerza. `FINAL_STARTUP_AUDIT.json` conserva valores, alcances y hashes.

Se inició `avance_A_compresible_600kmh_LTS_diag` desde el campo auditado v3, con localEuler y objetivo de 200 iteraciones de pseudotiempo. Control local maxCo=0,2, maxDeltaT=0,001 s, suavizado=0,1 y amortiguación=0,2 según el soporte instalado. No es una trayectoria física ni un ensayo de exactitud temporal. Se preserva el contador como `local_pseudo_iterations`. Solver: contenedor `codex-aero-avance-compresible-600-lts-v1`, sesión 16295; comprobar proceso y registro, sin reiniciar por una consulta que ceda el control.

## LTS 200 terminado: no convergido

El caso LTS inicial completó 200 iteraciones y pasó finitud/positividad de campos, pero no los objetivos numéricos de residuos, deriva y balance de masa. `INFORME-CONVERGENCIA-AVANCE-A.md` contiene el cribado y los cambios de campos. Se inició una continuación separada de 1000 iteraciones, sesión 54702, contenedor `codex-aero-avance-compresible-600-lts-cont-v1`. La sesión original 16295 terminó; no reiniciarla. No se acepta arrastre estacionario.
