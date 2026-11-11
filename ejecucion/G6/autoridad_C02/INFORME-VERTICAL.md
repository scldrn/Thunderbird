# C02: envolvente ideal vertical y horizontal simultánea

**7 de noviembre de 2026, hora de Bogotá.** Este cálculo amplía la
[sensibilidad de autoridad horizontal](INFORME.md) con aceleraciones verticales
prescritas. Es un modelo estático de cuatro conos de empuje **unidireccional**,
no una demostración de vuelo omnidireccional. La masa de 5 kg, el CG, el cono,
el límite de cada ventilador y el brazo efectivo siguen siendo supuestos.

## Hipótesis y cálculo

En el eje vertical del modelo se incluyen solo gravedad y fuerzas ideales de
los cuatro módulos; no se agregan sustentación aerodinámica, empuje axial,
reversibilidad, inercia de actuadores ni perturbaciones. A actitud fija se
prescribe `ΣFz_ventiladores = m·g·(1 + a_z/g)` y momento total nulo, y se maximiza la
aceleración horizontal en cada sentido. El semicono de fuerza se discretiza en
65 rayos por módulo, como en el estudio anterior. El modelo incluye cinco CG
longitudinales, dos brazos verticales, dos semiconos, dos límites por módulo,
siete aceleraciones verticales y dos sentidos: **560 escenarios**. Otros
**40 problemas** maximizan fuerza vertical con fuerza horizontal y momentos
iguales a cero.

Los signos longitudinales son del sistema CAD: `+x` apunta hacia la cola y
`−x` hacia la nariz. En el sistema FLU de vuelo ambos ejes horizontales cambian
de signo; el eje `+z` permanece hacia arriba.

La inclinación y la forma del cono son supuestos geométricos ideales, no una
identificación del ventilador con sus álabes y conductos. El CG geométrico
parcial de C02 no equivale al CG real, y los 20,58 N usados en el ejemplo
proceden de un caso ideal previo, no de una medición instalada C02.

## Límite vertical en el ejemplo de 5 kg

Para `x=±0,160 m`, CG transversal nulo, demanda horizontal y momentos nulos,
si `|x_CG|≤0,160 m`, el equilibrio ideal da
`Fz_max = 4·F_máx / (1 + |x_CG|/0,160)`. En el borde todavía pueden actuar los
dos módulos de ese extremo; fuera de la base longitudinal el máximo pasa a cero
bajo las mismas hipótesis. Con
`F_máx=20,58 N`, se obtienen estos máximos:

| CG longitudinal supuesto | Fuerza vertical total máxima | Aceleración vertical neta máxima | ¿Puede equilibrar el peso en este LP? |
|---:|---:|---:|---|
| 0 m | 82,32 N | +0,679 g | Sí |
| +0,040 m | 65,86 N | +0,343 g | Sí |
| +0,080 m | 54,88 N | +0,119 g | Sí |
| +0,096 m | 51,45 N | +0,049 g | Sí, con poco margen ideal |
| +0,120 m | 47,04 N | −0,041 g | No |

Por ejemplo, para el CG supuesto de +0,096 m, alcanzar **+0,5 g vertical** con
fuerza horizontal y momentos nulos requeriría al menos **29,42 N por módulo**
en este modelo ideal. La exigencia puede cambiar al considerar el conjunto real,
y el cálculo no demuestra que ese empuje sea alcanzable o sostenible.

## Movimiento simultáneo y descenso

Para `x_CG=+0,096 m`, brazo cero, semicono ideal de 45° y 20,58 N por módulo:

| Aceleración vertical impuesta | Aceleración horizontal máxima ideal en +x |
|---:|---:|
| −1,2 g | No hay solución para el cono unidireccional |
| −1,0 g | 0,000 g |
| −0,5 g | 0,500 g |
| 0 g | 0,441 g |
| +0,05 g | Supera el máximo vertical analítico de este caso ideal |

En ausencia de otras fuerzas, los conos que solo empujan hacia arriba no pueden
producir `a_z < −g`: para `a_z = −g` el modelo requiere fuerza propulsora cero
y, con estos conos, también fuerza horizontal propulsora cero. El peso sigue
actuando y la fuerza neta es hacia abajo. Esto **no dice** que todo
vehículo real esté limitado así: aerodinámica, orientación y mecanismos de
empuje reversible pueden cambiar el balance. Si se exige una aceleración
descendente mayor que `g` conservando actitud y sin otras fuerzas, hace falta
alguna capacidad de fuerza descendente que este modelo no representa.

La falta de solución de la aproximación poligonal interior no demuestra en
general imposibilidad para el cono continuo. Los límites verticales de la
primera tabla sí se contrastan con la identidad analítica indicada, dentro de
las hipótesis del ejemplo.

## Verificación y uso

Seis pruebas verifican el límite vertical analítico para varios CG, incluido el
borde de la base, el CG fuera de esa base, el caso
de caída libre, el rechazo de `−1,2 g` bajo empuje unidireccional, la igualdad
con el cálculo horizontal previo y una demanda superior al límite vertical.
Reproducir desde la raíz:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv-aero/bin/python \
  investigacion-aeronautica/ejecucion/G6/autoridad_C02/verificar_vertical.py
```

`envolvente_vertical_r1/RESULTADOS.json` conserva los 560 problemas, los 40
límites y las huellas de los archivos utilizados. Hay 372 soluciones del LP y
188 casos sin solución del poliedro. No se calculan tiempo de respuesta,
consumo ni márgenes ante viento; se requieren el CG completo y los mapas
instalados de fuerza/momento, potencia y respuesta antes de usar la envolvente
como planta del simulador 6DOF.
