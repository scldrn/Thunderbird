# Comparación temporal parcial: sensibilidad de cargas locales

Se extrajeron instantáneas de los dos procesos foamRun mientras seguían activos, sin modificar sus diccionarios. Se comparan Euler y backward desde los mismos campos, malla, modelo y condiciones de contorno.

La ventana común disponible es 0,00005–0,00050 s del reloj de reinicio. La exclusión inicial de 50 microsegundos sirve para separar el arranque numérico sin historial; no certifica desarrollo físico ni estacionariedad. El descarte físico previsto de 0,00625 s no se ha alcanzado.

Las diferencias se integran en tiempo sobre la unión de los nodos de ambas series mediante interpolación lineal, sin extrapolación. La tabla muestra diferencias RMS por componente; no son incertidumbres físicas.

| Álabe | RMS ΔFx / ΔFy / ΔFz (N) | RMS ΔMx / ΔMy / ΔMz (N·m) |
|---|---|---|
| force_vaneX0 | 7.674e-05 / 0.0007012 / 0.001267 | 3.873e-06 / 3.573e-06 / 1.159e-05 |
| force_vaneX1 | 8.272e-05 / 0.001064 / 0.00167 | 2.321e-06 / 8.749e-06 / 3.563e-06 |
| force_vaneX2 | 6.651e-06 / 0.0004306 / 0.0009572 | 3.51e-06 / 1.699e-06 / 4.156e-06 |
| force_vaneY0 | 0.002112 / 0.0001584 / 0.002137 | 4.749e-06 / 1.171e-06 / 8.856e-06 |
| force_vaneY1 | 0.0005202 / 0.0001016 / 0.001723 | 5.17e-06 / 3.198e-07 / 1.064e-05 |
| force_vaneY2 | 0.0003792 / 3.578e-05 / 0.000894 | 1.613e-06 / 1.09e-06 / 3.846e-06 |

La máxima diferencia RMS de componente de fuerza en esta ventana es aproximadamente 0,00214 N. No constituye un criterio de aceptación: los dos esquemas pueden compartir errores de malla, modelo, contorno y difusión espacial. Los caudales coinciden casi exactamente, como es esperable con velocidad impuesta y continuidad; esto no valida la deflexión del chorro ni la potencia.

Los momentos se refieren al centro local de cada álabe, no al centro de masa del vehículo. Faltan fuerzas en paredes y rotor, balance de cantidad de movimiento transitorio, potencia y sensibilidad de paso/malla/dominio. No se transfieren estas cargas del canal antiguo al CAD instalado.

`VERIFICACION_COMPARADOR.json` registra pruebas con señales afines de integrales conocidas y mallas temporales desiguales, además del rechazo de extrapolación. `COMPARACION_PAREADA_PARCIAL.json` conserva resultados y rutas. Repetir la comparación con los archivos finales cuando los solvers terminen; esta instantánea no los sustituye.

Conclusión: se dispone de una comparación numérica parcial coherente, sin aceptación de cargas ni cambio de arquitectura.
