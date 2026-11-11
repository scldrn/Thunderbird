# Ensayo pareado Euler/backward: terminado y auditado

Ambos procesos llegaron a t=0,0015 s del reinicio con salida normal. Se verificaron valores finitos en U, p, k, omega, nut y phi del campo final, ausencia de parada del vigilante, presencia de End y conservación de los campos iniciales. Los solvers y su vigilante terminaron: no reiniciarlos.

Los campos iniciales, modelo, propiedades y control PIMPLE coinciden. En fvSchemes solo cambia Euler por backward. Ambos usan la misma malla y convección upwind; no se hizo un refinamiento de paso ni de malla. El arranque sin historial suficiente de backward no se usa para afirmar segundo orden.

## Comparación de cargas locales

Ventana común: 0,00005–0,00150 s. Se comparan tiempos físicos interpolados, con integrales ponderadas en tiempo. El máximo RMS de diferencia de componente de fuerza entre los seis álabes es 0,004214 N; el máximo RMS de diferencia de par sobre eje de bisagra es 6,229e−6 N·m. Son diferencias entre esquemas, no incertidumbres físicas.

| Álabe | RMS ΔFx / ΔFy / ΔFz (N) | RMS ΔM sobre eje local (N·m) |
|---|---|---|
| force_vaneX0 | 9.793e-05 / 0.00045388 / 0.00098807 | 5.8643e-06 |
| force_vaneX1 | 7.391e-05 / 0.0013435 / 0.0017076 | 3.4745e-06 |
| force_vaneX2 | 3.1904e-05 / 0.00034097 / 0.00078102 | 6.2287e-06 |
| force_vaneY0 | 0.0042137 / 0.00021479 / 0.0036207 | 5.2953e-06 |
| force_vaneY1 | 0.00069095 / 7.8818e-05 / 0.0015455 | 1.2299e-06 |
| force_vaneY2 | 0.00098069 / 6.9769e-05 / 0.00056116 | 1.1747e-06 |

El mayor cociente relativo por componente de fuerza es aproximadamente 2,73 %, en una componente pequeña. No se usa como error global del modelo. La coincidencia entre dos esquemas en una malla puede ocultar sesgos comunes.

## Qué permite concluir

La patología catastrófica del ensayo original con backward + linearUpwind no se reprodujo durante esta ventana con backward + upwind y los restantes controles conservadores. La comparación pareada aísla aquí el esquema temporal; no identifica retrospectivamente la causa única del fallo original, que también tenía otros controles distintos.

No se aceptan cargas medias. La edad total del campo al final es 0,0025 s y no alcanza el descarte físico previsto de 0,00725 s de edad total. `analizar_series_transitorias.py` retiene las estadísticas de ambos casos por esa razón. No se acredita estacionariedad, independencia temporal/espacial, resolución de pared o sensibilidad de salida.

Las fuerzas son sobre álabes del canal antiguo, no empuje del vehículo instalado. `INFORME-REACCION-CONDUCTO.md` demuestra que deben incluirse paredes y `INFORME-BALANCE-MOMENTO.md` incorpora acumulación transitoria. La rama exterior ya inició una prueba propia, documentada en `ESTADO-SALIDA-EXTERIOR.md`; no constituye validación del CAD A.

Archivos de evidencia: `AUDITORIA_PAREADA_FINAL.json`, `COMPARACION_PAREADA_FINAL.json`, `COMPARACION_TEMPORAL_CONFIGURACION.json`, los dos `run_state.json`, campos finales, registros y `force_statistics_audit.json`. La auditoría numérica parcial no completa el objetivo de diseño global.
