# Cargas centrífugas y secciones del rotor C02

3 de noviembre de 2026. Trabajo parcial T26/T27 del plan maestro. **Cálculo geométrico condicionado, no FEM, selección de material o aprobación de resistencia.**

## Modelo y comprobaciones

Se utilizaron los rotores ahuecados D82 y D102,5 de los STEP C02 identificados en `RESULTADOS.json`. El segundo es un prototipo separado: no se declara instalado en el mismo cuerpo. Se retiró un cilindro central R=0,32R nominal para aislar las ocho palas conectadas por el cubo; se comprobaron ocho sólidos de igual volumen. Las secciones estudiadas x/R=0,33–0,95 quedan completamente fuera de ese cilindro y no se recortan con sectores angulares.

Un primer corte sectorial se rechazó: recortaba parte de la cuerda e incluía una esquina de la pala vecina. Se conservan registro y generador rechazados. Elegir la componente de mayor área habría ocultado material perdido; por ello se aislaron las palas completas por conectividad.

Se integraron volumen, centroide e inercia mediante cuadratura adaptativa. Para cada parte exterior al plano de corte, se calculó la fuerza de inercia saliente en el marco rotatorio:

```
F = ρ Ω² ∫ (x, y, 0) dV
M_en_sección = ∫ [(r−r0) × ρ Ω² (x,y,0)] dV
```

El origen r0 es el centroide de la sección. Las componentes transversales y momentos no se descartan: la masa de una pala de cuerda finita no está concentrada en su línea radial nominal.

Para el cribado de tensión normal se supone una distribución lineal y módulo longitudinal uniforme sobre cada sección. Definiendo S con las integrales de y², yz y z² respecto al centroide:

```
σxx = N/A + (y−yc, z−zc) · S⁻¹ · (−Mz, My)
```

Se utiliza una convención explícita de momento como r×F. Las [notas de mecánica estructural de MIT, unidad14](https://ocw.mit.edu/courses/16-20-structural-mechanics-fall-2002/resources/unit14/) explican el equilibrio de resultantes y la flexión de secciones no simétricas, con sus hipótesis. El presente cálculo no evalúa deformación, alabeo, cortante, torsión, laminado o concentraciones tridimensionales. Las palas cortas y la transición al cubo requieren un modelo superior antes de aceptar tensiones locales.

Pasaron dos referencias analíticas: fuerza centrífuga integrada de un prisma radial y tensión de una sección rectangular con flexión conocida. Comparar rebanadas de 0,02/0,04 mm en dos estaciones por tamaño cambia el área como máximo 4,83×10⁻⁶ relativo y el tensor de área 1,75×10⁻⁵. Ese contraste verifica la extracción de sección, no la aproximación estructural.

## Supuestos de operación

Se conservaron las tres velocidades del C01 de referencia 5 kg, κ=0,85: estacionario, demanda lateral0,5g y demanda vertical ascendente1g. Son escenarios de diseño calculados, sin capacidad de maniobra demostrada. Se estudiaron densidades homogéneas **1200/1600/2700kg/m³**, sin asociarlas a un material aprobado. Total:144 combinaciones de sección, densidad, régimen y diámetro.

Los resultados siguientes usan 1600kg/m³. Corresponden a la primera sección muestreada x/R=0,33, situada fuera del cubo; **no es la raíz real ni una búsqueda de máximo global**. Allí aparece el mayor valor de tensión normal entre las ocho estaciones muestreadas.

| Diámetro | Escenario C01 | rpm supuestas | Fx de parte exterior por pala | Media N/A | Mayor normal absoluta muestreada |
|---|---|---:|---:|---:|---:|
|82mm|Estacionario|46.231|266,1N|41,85MPa|116,75MPa|
|82mm|Demanda lateral0,5g|48.901|297,7N|46,83MPa|130,62MPa|
|82mm|Demanda vertical+1g|65.376|532,1N|83,69MPa|233,46MPa|
|102,5mm|Estacionario|29.588|266,1N|26,79MPa|74,71MPa|
|102,5mm|Demanda lateral0,5g|31.297|297,7N|29,97MPa|83,59MPa|
|102,5mm|Demanda vertical+1g|41.840|532,1N|53,56MPa|149,39MPa|

La sección D82 tiene área6,358mm² y la ampliada9,934mm². En D82/estacionario también aparecen Fy=−19,47N y momentos respecto al centroide (−0,0341;0,000301;−0,0996)N·m. La componente Mx no se convierte en tensión de torsión en esta tabla: falta esa contribución. Los signos dependen de la mano y marco del rotor identificado.

En estas velocidades C01 la ampliación conserva casi la fuerza centrífuga exterior y reduce la tensión normal calculada a aproximadamente0,64 veces. Las72 parejas de semejanza dan0,63990–0,64000. Es una consecuencia condicionada del escalado y sus rpm, no una superioridad estructural global. El rotor mayor ocupa más espacio, cambia masa/inercia y todavía no tiene integración aceptada.

## Consecuencia para el diseño

El cálculo muestra que N/A por sí solo omite una parte importante de la tensión normal de esta geometría. Las zonas próximas al cubo necesitan estudiar transición, radios y orientación del material, incluyendo torsión y cortante. No se calcula un margen contra resistencia sin propiedades, proceso, orientación, temperatura y criterio de fallo. Tampoco se deducen rpm máximas admisibles de esta tabla.

Faltan cargas aerodinámicas y de maniobra sobre el rotor, giroscopía, vibración, equilibrio, dilatación, fatiga, deformaciones/holguras y unión cubo–eje. Estas contribuciones impiden dar por aprobada la separación radial0,5mm o los apoyos actuales. El análisis de carcasa y aletas a47kPa es otro caso, todavía pendiente.

`RESULTADOS.csv`/`RESULTADOS.json` conservan las144 combinaciones. Reproducción desde raíz: `.venv-cad/bin/python investigacion-aeronautica/ejecucion/G5/test_cargas_rotor.py`; después `cargas_rotor.py`, que se detiene si ya existe la entrega para preservar resultados. G5 y el plan global permanecen abiertos.
