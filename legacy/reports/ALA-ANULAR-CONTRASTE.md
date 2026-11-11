# Ala anular: contraste experimental y dimensionamiento condicionado

## Resultado para la selección

El anillo merece conservarse como candidato para la transición: bajo las hipótesis descritas puede reemplazar la contribución sustentadora del ala central con dimensiones transversales moderadas. Sin embargo, no se ha demostrado que gane en arrastre total, masa instalada o capacidad transónica. Tampoco proporciona movimiento estacionario por su geometría pasiva.

Se calcularon 15 casos, combinando tres masas con cinco alargamientos anulares. Se iguala la pendiente de fuerza del ala central de la comparación integrada; **no se resuelve el equilibrio del vehículo completo con el anillo instalado**.

## Evidencia verificada y lectura de gráficas

[NACA TN 4117](https://ntrs.nasa.gov/citations/19930084906) ensayó anillos Clark Y de espesor relativo 11,7%, a Mach 0,13 y Reynolds de cuerda entre 0,704 y 2,11 millones. Define área de referencia como diámetro interior por cuerda y alargamiento como diámetro/cuerda. Las figuras 10–12 permiten las siguientes lecturas aproximadas:

| Alargamiento | Pendiente CL por grado | CD a incidencia cero | Máxima sustentación/arrastre |
|---|---:|---:|---:|
| 1/3 | 0,018 | 0,024 | 4,7 |
| 2/3 | 0,034 | 0,017 | 6,7 |
| 1 | 0,049 | 0,012 | 9,7 |
| 1,5 | 0,069 | 0,028 | 11,0 |
| 3 | 0,102 | 0,035 | 12,3 |

Son lecturas visuales, no datos tabulados originales. Se asignaron sensibilidades de lectura ±0,002, ±0,004 y ±0,2 respectivamente; no representan incertidumbre experimental. El informe contrasta una aproximación de arrastre inducido con sus ensayos. No aporta validación a Mach 0,82 para esta integración.

## Qué se iguala en la comparación

Se toma la geometría corporal L/D 6 y el área central dimensionada previamente para cada masa. Aquella ala tenía pendiente supuesta de sustentación 2 por radián. Se elige el área de referencia del anillo para igualar el producto área por pendiente. Así, a 8° y 150 km/h genera la misma contribución central en el modelo lineal.

Se conservan, sin recalcular, cuerpo y cola de referencia. El anillo se coloca idealmente con su centro aerodinámico en el centro de masa. Se omiten momento propio, soportes e interferencia; por eso igualar la fuerza central no demuestra que se conserve el trimado o la estabilidad del conjunto.

La estimación geométrica usa diámetro interior y espesor máximo del perfil para aproximar el diámetro exterior. El área de lámina se aproxima por una superficie cilíndrica intermedia usando ese espesor: no es una integración precisa del perfil. No debe confundirse con área de referencia ni con superficie mojada, aproximadamente dos caras.

## Ejemplo de anillo con alargamiento 1,5

| Masa | Diámetro interior | Diámetro exterior aproximado | Cuerda | Área de referencia |
|---|---:|---:|---:|---:|
| 2 kg | 0,165 m | 0,190 m | 0,110 m | 0,0181 m² |
| 5 kg | 0,288 m | 0,333 m | 0,192 m | 0,0553 m² |
| 10 kg | 0,428 m | 0,495 m | 0,286 m | 0,1223 m² |

La contribución sustentadora central calculada es de 10,6, 32,5 y 71,8 N respectivamente, a 150 km/h y 8°. No corresponde a todo el peso: el modelo precedente asignaba el resto a cuerpo y cola. Aplicando la aproximación de polar descrita, el arrastre del anillo aislado sería de 1,16, 3,55 y 7,85 N, sin soportes ni interferencia. Son extrapolaciones condicionadas a los coeficientes leídos.

El Reynolds calculado de estos anillos a 150 km/h es aproximadamente 0,313, 0,548 y 0,814 millones. **Los dos menores quedan por debajo incluso del intervalo global de ensayos**; el mayor está dentro de ese intervalo, pero eso no demuestra coincidencia con el Reynolds del modelo experimental de igual alargamiento. No deben presentarse estos tres tamaños como configuraciones experimentalmente validadas.

## Interferencia y espacio: una limitación material

En el plano de diámetro corporal máximo, el cuerpo ocuparía aproximadamente el 80%, 48% y 34% del área interior circular del anillo, respectivamente. Esa fracción es una medida geométrica, no un coeficiente de bloqueo aerodinámico. Muestra por qué los datos del anillo aislado no pueden trasladarse directamente al conjunto.

La holgura radial sería de unos 9, 44 y 88 mm. La versión de 2 kg ni siquiera pasa el filtro geométrico elegido de 10 mm, sin contar soportes, vibraciones ni tolerancias. No es imposibilidad del anillo: obliga a redimensionarlo o cambiar de alargamiento y volver a calcular.

Si además se pretendiera usar el hueco anular como disco propulsor, su área libre sería aproximadamente 0,0043, 0,0339 y 0,0944 m². El código calcula la potencia ideal de estacionario asociada a esa área. Se trata de un disco actuador ideal, sin pérdidas ni interacción; no selecciona un ventilador y no demuestra control omnidireccional. Un conducto axial único tampoco sustituye automáticamente los actuadores distribuidos.

## Comparación de superficie y penalización rápida

En el ejemplo de alargamiento 1,5, la lámina anular estimada es aproximadamente el 86% de la superficie física de las cuatro alas centrales comparadas a igual pendiente de fuerza. **No equivale a ahorrar 14% de masa instalada**: faltan estructura, soportes, perfil hueco o macizo, actuadores y posibilidad de plegado.

Como sensibilidad deliberadamente extrapolada, mantener el CD de incidencia cero sin cambios hasta 1000 km/h daría unos 24, 73 y 162 N de arrastre parasitario del anillo. No son predicciones transónicas: ignoran compresibilidad, ondas e interferencia. Solo muestran que una superficie eficiente sustentando a baja velocidad puede consumir un margen importante cuando permanece expuesta en vuelo rápido.

Tampoco se puede comparar la máxima relación sustentación/arrastre de un anillo aislado con el arrastre de un fuselaje a sustentación cero para proclamar un ganador. La comparación correcta requiere mismo peso, velocidad, estado de equilibrio y sistema completo.

## Decisión y validación pendiente

Se conserva el anillo para estudiar una transición de baja velocidad, especialmente en 5 y 10 kg. No se selecciona como configuración permanente para 600–1000 km/h con la evidencia actual. Para compararlo de verdad con alas retráctiles hacen falta polares del anillo con cuerpo y soportes, su momento, pérdida a Reynolds representativo, arrastre transónico y cierre estructural/de masa. Un anillo segmentado plegable añade un mecanismo aún no diseñado.

## Archivos y verificaciones

- Fuente local: `fuentes/nasa/19930084906.pdf`; se inspeccionaron visualmente las figuras pertinentes.
- Lecturas y procedencia: `resultados/anular_lecturas_GRAFICAS.json`.
- Código: `ala_anular.py`.
- Quince comparaciones: `resultados/ala_anular_COMPARACION_CONDICIONAL.csv`.
- Resumen y limitaciones: `resultados/ala_anular_RESUMEN.json`.

Se comprobó numéricamente que cada anillo dimensionado reproduce la fuerza central objetivo en el modelo lineal. Eso verifica la normalización de áreas, no la física de la configuración integrada. El objetivo global permanece abierto.
