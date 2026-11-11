# Evidencia transónica y nueva malla de la envolvente A

## Evidencia primaria revisada

[Wetmore, NACA, 1947](https://ntrs.nasa.gov/api/citations/19790079920/downloads/19790079920.pdf), figura 9, compara cuerpos de finura 6/9/12 mediante caída libre e incluye colas estabilizadoras. El texto indica que, por debajo de Mach 0,94, la mayor fricción del cuerpo de finura 12 supera su ventaja de retrasar el aumento transónico de arrastre. Cerca de Mach 1 su coeficiente es aproximadamente 60 % del correspondiente al cuerpo de finura 6.

La figura 11 presenta presiones wing-flow de un cuerpo parabólico de finura 6, con soporte, y comparación con caída libre de otro cuerpo similar. No es una medición de nuestra carrocería. La copia descargada y las figuras 9–12 se revisaron visualmente; no se digitalizaron curvas.

Esta evidencia no establece un óptimo universal L/D=6 ni un Mach crítico universal según esbeltez. Tampoco cubre la validación específica de Mach 0,5–0,85 requerida para la forma A. Se conservan separados Mach crítico, aumento del arrastre y métodos de ensayo.

## Relación con la investigación aportada

El texto pegado por el usuario propone un Sears–Haack modificado circular de L/D=6 y afirma ausencia de onda a Mach 0,82. La forma A aprobada tiene sección facetada no circular, otra distribución de área y extremos de tamaño finito. Sus coeficientes, presiones y Mach crítico no pueden obtenerse copiando aquella tabla. La metrología vigente ya verifica esas diferencias; el nuevo cálculo conserva esta identidad geométrica.

## Malla de la envolvente A cerrada

Se importó directamente `envolvente_cerrada_referencia.step` y se verificó la conversión mm→m mediante volumen CAD. Es el loft antes de puertos, insertos y detalles. No representa puertas de crucero diseñadas ni el vehículo instalado completo. No se modificó el CAD aprobado.

| Propiedad verificada | Resultado |
|---|---:|
| Longitud del cuerpo | 1,340 m |
| Volumen CAD | 0,0400879071 m³ |
| Área CAD | 0,830423568 m² |
| Área de referencia frontal muestreada | 0,049774748 m² |
| Celdas tetraédricas | 326.013 |
| Triángulos de la pared del cuerpo | 31.546 |
| Error de volumen discretizado respecto al cuerpo CAD | 0,00403 % |
| Error de área discretizada respecto al cuerpo CAD | 0,00287 % |
| Margen de dominio aguas arriba / abajo / lateral | 3 / 5 / 3 longitudes |

Todos los tetraedros tienen volumen orientado positivo; la pared triangulada está cerrada, con dos incidencias por arista. Se comprobó volumen del aire más cuerpo respecto a la caja exterior. Esos errores se normalizan con el tamaño del cuerpo, para que el volumen mucho mayor del aire no oculte una pared mal representada.

OpenFOAM13 verificó topología y geometría mediante `checkMesh -allGeometry -allTopology`, con resultado Mesh OK. El contenedor de conversión volvió a iniciarse únicamente para consultar ejemplos y fuentes instaladas de flujo compresible; no se ha lanzado un solver de avance. Sus campos aún no se prepararon.

## Qué se puede calcular después

Esta malla sin capas prismáticas prepara un diagnóstico de presión y compresibilidad exterior. No basta para declarar fricción viscosa o arrastre total resueltos a Reynolds del orden de 10⁷. Se requiere elegir contornos y formulación compresible, comprobar arranque, contrastar presiones con un caso experimental y demostrar sensibilidad de malla y dominio. Una pared deslizante, si se usa, separaría el ensayo de presión del posterior modelo viscoso; no acreditaría el arrastre total.

Habrá que calcular mapas de presión y Mach local, fuerzas de presión y fricción por separado, cargas de base, incidencia, estabilidad y su dependencia de la velocidad. Para declarar Mach de divergencia debe indicarse el criterio elegido y presentar la curva de arrastre; una sola solución a Mach 0,82 no lo determina. Ninguna malla por sí sola valida Mach crítico o geometría óptima.

El ensayo exterior de los álabes sigue en ejecución; sus picos iniciales están disminuyendo, pero no sustituye esta evaluación compresible de avance.

Archivos: `CFD/avance_A_cerrada_h0.008/mesh_metadata.json`, `GEOMETRY_AUDIT.json`, `OPENFOAM_MESH_AUDIT.json`, `log.checkMesh`; código `mallar_avance_A.py`, `auditar_malla_avance_A.py` y `convertir_verificar_malla.py`. Fuente y páginas renderizadas en `fuentes/naca_transonico/`, con hash y procedencia.
