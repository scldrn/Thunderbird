# Masa hipotética y reparto de sustentación en tres reservas axiales

Se conectaron los 36 escenarios de masa ya calculados para la arquitectura A de 5 kg con el modelo de reparto de cuatro discos libres ideales. La comparación incluye las tres posiciones de estaciones de `modelos_integrados/empaquetado_axial_A/INFORME.md`: reservas exteriores de 38, 60 y 80 mm. Son alternativas de empaquetado anteriores, no configuraciones de hardware C02 aprobadas ni motores seleccionados.

Las masas y posiciones del estudio de origen son hipotéticas: incluyen un módulo de 1 kg en x=400 mm y una masa restante artificialmente ajustada para sumar 5 kg. Equilibrar esa masa no demuestra que el equipo quepa, tenga propiedades reales ni que la estructura soporte las cargas. Se conserva la condición previa de su centro en [−350, +50] mm. La posición de estaciones de 38 mm es asimétrica (−300/+275 mm), por lo que el punto medio está en −12,5 mm, no en cero.

En estacionario vertical, con empujes paralelos, límite hipotético de 21 N por módulo, sin reserva de momento ni precarga mínima y diámetro de disco supuesto 82 mm:

| Reserva axial | Centro de equipo restante | CG longitudinal supuesto | Casos que cumplen límite de fuerza y zona supuesta | Potencia inducida ideal, discos libres |
|---:|---|---:|---:|---:|
| 38 mm | x=0 | 73,4–76,6 mm | 6/6 | 1.560–1.564 W |
| 60 mm | x=0 | 78,1–78,8 mm | 6/6 | 1.596–1.598 W |
| 80 mm | x=0 | 78,7–79,3 mm | 0/6 | 1.877–1.883 W, contrafactual |
| 38, 60 o 80 mm | CG equilibrado a x=0 | 0 mm | 5/6 por reserva | ≈1.509–1.510 W |

En cada grupo equilibrado, uno de seis escenarios exige situar el centro del equipo restante fuera de la zona supuesta y se rechaza por esa restricción. Los cinco que pasan **no prueban la contención geométrica de un equipo real**. Para los seis casos de 80 mm con equipo restante en x=0, el centro de masa queda cerca de la estación delantera/trasera según el eje CAD y la demanda máxima por módulo excede 21 N; la potencia mostrada omite el límite de módulo y no es factible bajo ese supuesto. Los recuentos no son probabilidades.

Los resultados no garantizan reserva para controlar actitud, ráfagas, ascenso o movimiento lateral. La comparación solo aplica al instante vertical sin aceleración: en esa condición, la altura del CG no introduce momento para fuerzas estrictamente verticales. Los conductos, pérdidas, flujo recirculado, rotores reales y potencia eléctrica no se modelan. No se transfieren los valores numéricos como mapa de fuerza o consumo de C02. La potencia ideal de disco libre sigue las hipótesis y fuente señaladas en `INFORME.md`.

`MASAS_INTEGRADAS.json` registra la huella del archivo de escenarios, posiciones, restricciones y resultados individuales. Ejecutar desde la raíz:

```sh
python3 investigacion-aeronautica/ejecucion/G6/potencia_cg_ideal/verificar_integracion.py
python3 investigacion-aeronautica/ejecucion/G6/potencia_cg_ideal/integrar_masas.py
```

Cuatro pruebas pasan para cobertura, origen asimétrico, saturación y zona de equipos. Las sesiones Antigravity `090f680c` y `a354342b` terminaron con respuesta vacía; no se incorporaron conclusiones de ellas. El siguiente cierre de ingeniería debe sustituir la masa genérica por componentes y envolventes trazables, resolver empuje y momentos simultáneos con margen y contrastar los mapas de los ventiladores instalados.
