# Contraste con polares experimentales: SD8020

## Qué se ha conseguido

Se descargaron datos originales UIUC de sustentación y arrastre del SD8020. Es un perfil simétrico alternativo, NO el NACA0012. La geometría anterior no queda validada por cambiarle la polar. La tabla de arrastre incluyeCL/CD simultáneos aRe61400,101500,203300,304800. Se interpolan esos datos en ángulo y Reynolds. Fuentes:
- https://m-selig.ae.illinois.edu/pd/pub/lsat/vol1/SD8020.DRG
- https://m-selig.ae.illinois.edu/pd/pub/lsat/vol1/SD8020.LFT
- Clasificación simétrica: https://m-selig.ae.illinois.edu/sym_afs_v2.html

Datos producidos por UIUC Low-Speed Airfoil Test program, Summary of Low-Speed Airfoil Data, Vol.1. Originales sin modificar, licencia y manifiesto en fuentes/uiuc. No se interpreta la columnaCm igual a cero del archivoLFT como una medida confirmada de par aerodinámico. El cálculo empleaCL/CD del archivoDRG.

## Cobertura y resultados

Se conserva modelo de elementos de pala con inducción uniforme; dos palas, diámetro457,2mm, raíz40mm y sin torsión. Fuera del dominio tabulado se congela el coeficiente al borde SOLO como sensibilidad y se marca la fracción afectada. Esto no es extrapolación físicamente validada. Tampoco se corrige Mach local, pérdidas de punta o rotación de estela.

La alternativa con mejor cobertura entre los casos revisados es cuerda30mm y6000rpm:

| Empuje por rotor | Paso calculado | Potencia de eje | Potencia eléctrica con85% supuesto | Tramo fuera del dominio | Fracción del integral de par absoluto fuera del dominio |
|---|---:|---:|---:|---:|---:|
| 29,68N | 10,19° | 346W | 408W | 3,3% | 0,22% |
| 38,94N | 12,86° | 519W | 611W | 5,0% | 6,88% |

Los porcentajes de contribución son indicadores del propio modelo, NO cotas del error: la verdadera aerodinámica fuera del dominio podría cambiar la solución. La polar de túnel a baja velocidad no valida todo el rotor aMach periférico cercano a0,42.

La alternativa35mm y6000rpm queda fuera del rango deRe en la punta; aproximadamente39–40% del integral de par absoluto depende de esa zona/fuera de dominio. No se retiene como candidata mejor respaldada por ESTOS datos. A5500rpm y30mm, el objetivo39N llega a tener91% del tramo fuera del dominio: se descarta su resultado como base de decisión.

La comprobación numérica reproduce los nodos tabulados deCL/CD con error menor que1e-12. Esto verifica el interpolador, no el modelo rotor.

## Motor a tensión mínima

La tabla pública consultada paraMN5008KV170 contiene ensayos con hélices fijas cerca de47V y distintos mandos; NO contiene el mapa necesario de par/RPM/eficiencia a36–42V con nuestro rotor de paso variable. No se ha encontrado ese mapa en la fuente consultada. No se confunden datos del bobinadoKV340 a23V con los delKV170.

Fuente: https://store.tmotor.com/product/mn5008-kv400-motor-antigravity-type.html

El resultado611W no basta para aprobar un motor porque sea inferior a su potencia máxima publicada: falta sostener6000rpm y aproximadamente0,83Nm de eje a tensión mínima, con límites térmicos y controlador. La cifra85% es una hipótesis, no eficiencia medida en ese punto. No se ha verificado inversión de empuje.

## Consecuencia para el vehículo

No se sustituye todavía el presupuesto conjunto de2,36kW por una cifra nueva supuestamente validada. El reparto de cargas necesita un mapa completo de cada rotor desde empuje negativo a positivo, incluido consumo a paso cero. Los dos puntos de empuje aquí evaluados no son ese mapa. La cifra733W del estudio sintético anterior tampoco queda confirmada: corresponde a otra polar y cuerda.

Decisión: estudiarSD8020/30mm/6000rpm como alternativa mejor cubierta por datos disponibles, manteniendoNACA0012 como candidato pendiente. Para cerrar el diseño hay que completar el dominio aerodinámico (especialmente inversión yMach), conseguir caracterización del motor a tensión mínima y luego repetir masa/potencia/control. No hay aprobación de compra, fabricación ni garantía de5kg o600–1000km/h.

Reproducción: polar_experimental.py. Resultados: resultados/polar_experimental_resumen.json. Originales UIUC y condiciones de redistribución se conservan junto al código.
