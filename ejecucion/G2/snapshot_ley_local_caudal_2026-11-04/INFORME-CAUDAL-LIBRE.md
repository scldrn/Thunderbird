# Caudal libre: contraste analítico y resultado parcial

4 de noviembre de 2026. Prueba de contornos y operador, sin rotor ni vehículo. No se impone velocidad o caudal en la entrada.

## Problema analítico

Conducto recto de longitud L=0,2m y área A=0,04m²; paredes deslizantes, aceleración volumétrica G=5m/s², presión total cinemática cero en entrada y presión estática cero en salida. Para flujo uniforme positivo, la conservación de momento y el contorno dan:

`dU/dt = G - U²/(2L)`, `Q=A·U`, `p_kin(x,t)=U(t)²·(x-L)/(2L)`.

La velocidad estacionaria es sqrt(2GL)=1,41421356237m/s. La solución temporal se evalúa para velocidades iniciales0,5 y2m/s, con4y20celdas longitudinales. Los campos y contornos se generaron y calcularon en la misma imagen OpenFOAM13 identificada; se inspeccionó la implementación instalada de `totalPressure` antes del ensayo.

## Primer intento y lector

`benchmark_caudal_libre_r1` ejecutó200iteraciones estacionarias. Los casos20celdas no habían llegado a la solución: errores máximos de U≈40,18% y20,89%, según la inicialización. No se aceptaron por haber terminado con salida0. Además, el lector no admitía el formato compacto válido `List<vector> 4((...) ...)` de los casos pequeños.

Se conservó el lector anterior y se extendió `../../CFD/foam_fields.py` para listas ASCII compactas o multilínea, manteniendo comprobaciones de tipo, cantidad de valores y finitud. `benchmark_caudal_libre_r1/REGRESION_LECTOR.json` verifica igualdad exacta frente al lector anterior en U/p/k/omega/nut del caso581786celdas, además de leer los cuatro casos compactos/multilínea. No se modificaron los campos CFD.

## Segundo intento transitorio

`benchmark_caudal_libre_r2_transitorio` calcula4s con paso0,01s, esquema backward y10correctores PIMPLE. Los cuatro casos terminan con salida0 y campos finales que reproducen la solución analítica. Máximos de los cuatro casos:

| Diagnóstico | Error calculado |
|---|---:|
| Velocidad relativa | 1,36e−13 |
| Presión cinemática normalizada por GL | 2,14e−12 |
| Caudal relativo | 1,40e−13 |
| Continuidad relativa | 1,72e−13 |

Pasan los límites declarados previamente de2e−4 en velocidad/presión/caudal y1e−9 en continuidad. **No pasa el criterio de ausencia de soluciones lineales alcanzando500iteraciones.** Se conserva el rechazo del verificador principal; `AUDITORIA_PARCIAL.json` registra por separado el acuerdo de campos y el fallo del criterio lineal. No se relajó ese criterio para obtener una aprobación global.

La fuente instalada `benchmark_caudal_libre_r2_transitorio/lduMatrixSolver_instalado.C` muestra que `normFactor` resta un campo de referencia basado en el promedio de la incógnita. Por esa fórmula, la normalización puede perder escala en un campo uniforme. La cancelación numérica es una hipótesis compatible con los datos; no se midió el residual absoluto exacto de cada matriz ensamblada. Tampoco se deduce de estos campos finales un orden de precisión temporal o acuerdo durante el transitorio temprano.

## Consecuencia para C02

Se verificó de forma limitada la respuesta final de esos contornos: la velocidad se calcula sin prescribirQ. El flujo uniforme sin fricción y la configuración estacionaria original no se dan por validados íntegramente. C02 requerirá sus propios residuos, balances, sensibilidad y comprobación de contornos, con paredes/álabes y campos no uniformes.

Una entrada de depósito y salida a presión ambiente siguen siendo una aproximación del entorno. No incluyen fuerzas del labio/exterior ni implican empuje en estacionario. La presión total por sí sola no convierte el banco cilíndrico en el módulo instalado. No se aplicó aún esa modificación a C02 y no se inicia una curva de ventilador aceptada con este resultado parcial.
