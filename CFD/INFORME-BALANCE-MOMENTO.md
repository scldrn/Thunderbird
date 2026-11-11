# Balance integral de cantidad de movimiento del canal

Se evaluaron los campos guardados a 0, 0,00025 y 0,00050 s del reinicio Euler mediante un caso aislado de posprocesado. No se avanzó ni se modificó el solver original. Densidad supuesta: 1,225 kg/m³.

Se comprueba la ecuación integral: acumulación de momento del fluido + flujo convectivo saliente + carga opuesta a la fuerza sobre el fluido en toda la frontera = 0. En las paredes, esa última contribución coincide con la carga del fluido sobre el sólido. En los extremos abiertos es una tracción matemática de control, no una pieza del vehículo.

| Contribución media en la ventana | x / y / z (N) |
|---|---|
| Acumulación | -0.315505 / -0.232726 / -0.001446 |
| Flujo convectivo | 2.326031 / -0.041352 / -4.109652 |
| Tracción opuesta al fluido | -2.020549 / 0.259017 / 4.111138 |
| Residuo | -0.010022 / -0.015061 / 0.000040 |

La norma del residuo es 0,01809 N, normalizada con la mayor norma de las tres contribuciones (4,7224 N): 0,383 %. No es una incertidumbre física ni una prueba de convergencia.

La integración temporal usa trapecios con los tres campos. Usar solo los dos extremos cambia el término integrado medio aproximadamente (0,0340; 0,0446; −0,00082) N, más que el residuo observado. Por tanto, esta cuadratura no tiene sensibilidad temporal demostrada y no se adopta un umbral de aprobación. Se necesita muestrear más densamente para separar error de cuadratura de inconsistencias espaciales/iterativas.

La suma de las tracciones en sólidos y extremos coincide con la integración de toda la frontera hasta el redondeo de salida. El flujo volumétrico entra y sale con la misma magnitud a la precisión escrita; esto verifica continuidad registrada, no suficiencia del modelo de empuje. La acumulación lateral no es despreciable y confirma que sería incorrecto exigir balance estacionario en esta ventana.

Las operaciones se contrastaron con la implementación instalada de Foundation13: `surfaceFieldValue` operación `sum` con `weightField phi` integra Σ(phi·U); `volFieldValue` operación `volIntegrate` integra U·dV; `forcesBase` integra presión y esfuerzo viscoso efectivo SST con conversión de presión cinemática mediante rhoInf. Las normales están orientadas hacia fuera del fluido.

No es el residuo exacto de las ecuaciones discretizadas del solver. Las tracciones reconstruidas, la cuadratura temporal, los operadores espaciales y las iteraciones PIMPLE pueden contribuir a la diferencia. No se valida el rotor, potencia, autoridad de control instalada ni geometría óptima.

Archivos: `preparar_balance_momento.py`, `auditar_balance_momento.py` y `auditoria_momento_Euler_0_0.0005/MOMENTUM_AUDIT.json`. La salida exterior se prepara en una rama independiente para estudiar el chorro sin imponer el plano de salida justo debajo de los álabes.
