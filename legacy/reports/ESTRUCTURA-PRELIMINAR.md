# Estructura: flexión global, paneles locales y límites del cálculo

## Resultado que afecta a la geometría

Un cuerpo más largo ofrece ventajas en algunos modelos de arrastre y de brazo de cola, pero aumenta flexibilidad y masa superficial. A la vez, el cascarón continuo ideal no representa las zonas debilitadas por tomas, tapas y alojamientos de rotores. Por eso la comparación aerodinámica anterior no permite elegir L/D 12 como ganador sin dimensionar estos detalles.

Se calcularon 324 escenarios de flexión global y 27 de paneles bajo presión, mediante Python y elementos finitos de viga. El análisis está verificado frente a una solución analítica, pero **no es un modelo de cascarón completo, cálculo de pandeo ni validación aeroelástica**.

## Evidencia documental

La presión dinámica sirve como escala para las fuerzas aerodinámicas; no especifica por sí sola la distribución de presión sobre la superficie. Las fuerzas resultan de integrar esa distribución. Fuentes: [NASA, presión dinámica](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/dynamic-pressure-2/) y [NASA, fuerzas aerodinámicas](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/aerodynamic-forces/).

NASA SP-8007 revisa el diseño frente al pandeo de cilindros de pared delgada y su sensibilidad a imperfecciones. No se ha aplicado una fórmula cilíndrica como garantía para nuestro cuerpo esferoidal con aberturas. El boletín NASA de 2023 también advierte que un factor universal de reducción para laminados compuestos carece de justificación general. Fuentes: [SP-8007, revisión 2](https://ntrs.nasa.gov/citations/20205011530) y [boletín técnico sobre cascarones compuestos](https://www.nasa.gov/wp-content/uploads/2023/10/tb-summary-100223.pdf).

## Modelo global y supuestos

- Cuerpo esferoidal cerrado de volumen igual a masa / 200 kg/m³; L/D 4, 6, 8 o 12.
- Material isotrópico hipotético: módulo 70 GPa, densidad 2700 kg/m³. No se identifica con una aleación concreta ni se usan propiedades certificadas. Umbral de tensión de cribado: 100 MPa, arbitrario.
- Espesores constantes de 0,2, 0,5 y 1,0 mm; sin juntas, nervaduras, aberturas ni concentraciones de tensión.
- Se representa cada mitad como viga de sección circular variable empotrada en el centro. Su rigidez usa el momento de área de un anillo delgado según el radio local del esferoide.
- El 30%, 60% o 100% de la masa se distribuye uniformemente a lo largo del cuerpo; el resto se concentra idealmente en el apoyo central. La masa distribuida ya incluye la estructura: no se suma otra vez al ensamblar la matriz de masa.
- La carga es la inercia de esa masa distribuida bajo aceleración transversal de 5, 10 o 20 g, con reacción central. Es un caso de trayectoria de cargas elegido, no la distribución real de sustentación, empuje y masas del avión.
- La frecuencia calculada corresponde al empotramiento central ideal. No es un modo de vuelo libre ni de la aeronave completa; no debe compararse directamente con armónicos de rotor para afirmar ausencia de resonancia.

El modelo de viga pierde validez local cerca de las puntas, donde el espesor deja de ser pequeño frente al radio. No analiza aplastamiento de la sección, ovalización, torsión, pandeo local ni acoplamientos de material compuesto.

## Ejemplo: 5 kg, 60% de masa distribuida, pared de 0,5 mm, 20 g

| L/D | Masa de piel | Tensión de flexión estimada | Desplazamiento de la punta | Frecuencia con apoyo central |
|---|---:|---:|---:|---:|
| 4 | 0,714 kg | 3,22 MPa | 0,025 mm | 563 Hz |
| 6 | 0,806 kg | 5,54 MPa | 0,083 mm | 307 Hz |
| 8 | 0,883 kg | 8,12 MPa | 0,197 mm | 199 Hz |
| 12 | 1,007 kg | 13,95 MPa | 0,665 mm | 108 Hz |

Estas bajas tensiones no prueban que una carcasa real soporte 20 g. El anillo continuo ideal es muy eficaz en flexión; una abertura interrumpe esa continuidad y puede alterar significativamente rigidez y resistencia. El ejemplo cuantifica la tendencia geométrica, no un espesor aprobado.

La piel de 0,5 mm del ejemplo L/D 6 pesa unos 806 g, frente a los 350 g asignados como hipótesis de piel en un presupuesto anterior de 5 kg. Son geometrías/materiales de referencia distintos: la diferencia muestra que aquella partida no estaba dimensionada. Con 0,2 mm, la masa de esa piel sería unos 323 g, pero su aceptación exige resolver paneles, pandeo, uniones y cargas reales; no basta con que quepa en el presupuesto.

## Presión local: estudio separado de una tapa plana

Se analiza una tira plana de ancho unitario simplemente apoyada bajo presión uniforme. Es una sensibilidad para zonas planas o tapas, no un sustituto del cascarón curvo. Se evalúan distancias entre apoyos de 20, 50 y 100 mm, los tres espesores anteriores y diferencias de presión equivalentes a 0,05, 0,2 y 1 veces la presión dinámica a 1000 km/h. Se presupone presión interior próxima a la referencia exterior para interpretar estos escenarios; el diferencial real requiere datos de ventilación y presión superficial.

Ejemplo de 50 mm entre apoyos y 0,5 mm de espesor:

| Diferencia de presión supuesta | Tensión lineal | Deflexión lineal | Deflexión / espesor |
|---|---:|---:|---:|
| 2,36 kPa | 17,7 MPa | 0,264 mm | 0,53 |
| 9,45 kPa | 70,9 MPa | 1,055 mm | 2,11 |
| 47,26 kPa | 354,5 MPa | 5,275 mm | 10,55 |

Los tres ejemplos exceden el filtro elegido de deflexión/espesor menor que 0,5. **Sus resultados lineales no predicen con fiabilidad la deformación final ni el colapso**: señalan la necesidad de análisis no lineal o de cambiar apoyos/espesor. La curvatura, el trabajo de membrana, los bordes reales y las cerraduras pueden cambiar mucho la respuesta.

La presión dinámica no es un diferencial uniforme ni una cota universal de presión local. Estos escenarios no reemplazan un mapa de coeficientes de presión a cada incidencia y velocidad.

## Consecuencias para los mecanismos

1. El alojamiento de cada rotor debe incorporarse al modelo estructural como abertura y conjunto de bordes reforzados; no como piel intacta con un componente añadido encima.
2. Las tapas y superficies plegables necesitan apoyos y cierres que transmitan presión y fuerzas de maniobra. La masa de un servo no representa la masa del sistema de cierre estructural.
3. El camino de cargas entre motor, brazos, batería, reactor y cola debe definirse antes de calcular la resistencia global definitiva. Una masa central mejora inercia, pero no elimina cargas concentradas en las uniones.
4. Para flutter y divergencia hacen falta rigidez torsional, modos de la configuración real, holgura de bisagras y fuerzas aerodinámicas no estacionarias. Las frecuencias de esta viga no permiten declarar ninguna velocidad libre de flutter.

## Verificación numérica

La formulación usa elementos Euler–Bernoulli de dos nodos con matriz de masa consistente. Se verificó la viga prismática empotrada bajo carga uniforme: error relativo de desplazamiento inferior a 10⁻⁹ y de primera frecuencia inferior a 3×10⁻⁷. Para el cuerpo variable de referencia, pasar de 60 a 120 elementos por mitad cambió desplazamiento y frecuencia menos del 0,01%. No se afirma convergencia de concentraciones de tensión en puntas ni de cargas que el modelo no contiene.

Código: `estructura_preliminar.py`. Resultados: `resultados/estructura_viga_CONDICIONAL.csv`, `resultados/estructura_panel_presion_CONDICIONAL.csv` y `resultados/estructura_preliminar_RESUMEN.json`.

La etapa cierra la comparación estructural preliminar y expone qué partes no cubre. Continúan pendientes el material real, los detalles y espesores, modos de vuelo libre, pandeo con imperfecciones, fatiga y aeroelasticidad. El objetivo global sigue sin estar demostrado.
