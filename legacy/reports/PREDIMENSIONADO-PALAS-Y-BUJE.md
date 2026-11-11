# Predimensionado de cargas: palas, buje y servo

## Alcance

Se evalúan36 escenarios, no una pala final. Geometría SUPUESTA: dos palas rectangulares, radio exterior228,6mm, raíz25mm, cuerda25o35mm, masa uniforme10/15/20g por pala, régimen5000/6000/7000rpm. No se ha demostrado que esas palas produzcan38,94N ni que una sección o material concreto satisfaga resistencia, fatiga o aeroelasticidad. No modificar una hélice comercial para convertirla en paso variable con estos cálculos.

## Caso central

A6000rpm,15g por pala y25mm de cuerda:

| Magnitud calculada | Resultado |
|---|---:|
| Velocidad periférica | 143,6m/s |
| Mach periférico en aire quieto | 0,422 |
| Fuerza centrífuga por pala | 751N |
| Empuje asignado por pala | 19,47N |
| Momento flector en raíz | 2,86Nm |
| Par centrífugo de paso por pala a25° | 0,118Nm |
| Par aerodinámico supuesto por pala | 0,006–0,030Nm |
| Par requerido en servo del ejemplo | 0,230–0,260Nm |

Fuerza centrífuga integrada con masa uniforme. Momento flector con sustentación distribuida proporcional al cuadrado del radio. Par de paso aerodinámico con coeficienteCm supuesto0,01–0,05, velocidad tangencial y cuerda constantes; se suma desplazamiento supuesto2mm entre eje de paso y aplicación de sustentación. Par centrífugo con lámina delgada respecto a eje radial por centro de cuerda. El eje real y reparto de masa pueden cambiar sustancialmente estos valores.

También se añaden magnitudes de fricción supuesta0,02Nm por pala e inercia para un cambio triangular de velocidad de50° en70ms. La suma de máximos es un cribado conservador, no historia temporal físicamente acoplada. Relación cinemática paso/servo0,5 y eficiencia mecánica0,8 supuestas. El barrido completo arroja fuerza centrífuga348–1363N por pala y par de servo0,148–0,701Nm.

## Servo contrastado

Ficha KST X12-508 de2021:20g±10%, par publicado0,42Nm a6V,0,52Nm a7,4V y0,62Nm a8,4V; velocidades0,09/0,08/0,07s por60° respectivamente. Recorrido por defecto100°. Documento del fabricante alojado por distribuidor: https://www.intermodel.fr/fichiers/KSTX12-508.pdf

Candidato solo para evaluación. La ficha no acredita par continuo ni curva simultánea de velocidad-par. Con reducción de paso0,5, mover palas de−25°a+25° requiere100° del servo: extrapolación cinemática150ms a6V o117ms a8,4V, antes de carga, aceleración y asentamiento. Por tanto no garantiza inversión en70ms.

Una transmisión1:1 reduciría el recorrido pero duplicaría aproximadamente el par requerido:0,46–0,52Nm en el caso central. No implica cumplimiento simultáneo de velocidad y carga. Los50° de paso son un supuesto de estudio: falta el mapa de empuje que determine el recorrido necesario.

## Rodamientos y soporte

La fuerza centrífuga debe cerrarse por portapalas y buje, no por la varilla del servo. El momento flector2,86Nm requiere un par de reacciones de aproximadamente238N si los apoyos se separan12mm, más las cargas directas. El reparto exacto exige geometría real.

Se contrastó NSK51100 como referencia:10×24×9mm,19g, capacidad estática axial14kN. Dos unidades por rotor, una por pala, suman38g y exceden ya el presupuesto residual del ejemplo. No se seleccionan: un rodamiento axial solo no resuelve las cargas radiales/flectoras ni asegura montaje o vida a fatiga. La capacidad estática catalogada no es una carga admisible del conjunto. Fuente: https://www.nsk.com/engineering/51100-tb-sd.html

Los rodamientos de paso oscilan respecto al buje; no debe aplicárseles sin más el régimen de6000rpm como velocidad relativa interna. Ese régimen corresponde al rotor completo. Los apoyos del eje motor son otro subsistema y necesitan su propia comprobación.

## Presupuesto de masa

De98,25g por estación, el ejemplo asigna20g a servo,30g a dos palas y20g a ESC (estos dos últimos son supuestos, no selección). Restan28,25g para buje, rodamientos, portapalas y mando. Aún faltan datos de masa de esas piezas; no hay cierre. El NSK51100 no cabe en esta asignación. Se requieren rodamientos compactos y análisis combinado de carga, masa y retención.

## Decisión resultante

No aprobar todavía el KST ni un rodamiento como componente definitivo. Mantenerlo como referencia y elegir primero perfil, distribución de cuerda/masa y eje de paso; con ello resolver conjuntamente empuje y par, luego seleccionar transmisión y servo. Un servo mayor podría resolver par, pero consumiría margen de masa. Las palas más ligeras reducen fuerza centrífuga y par de paso, pero necesitan verificación estructural.

La familia5kg sigue sin estar validada: ahora existen cargas cuantificadas que explican por qué el paso variable no se puede añadir con una masa arbitraria. Se requiere modelo aerodinámico de pala y caracterización de material/laminado antes de espesor, tornillería o plano de fabricación. La validación transónica y transición permanecen independientes y pendientes.

Código reproducible: cargas_pala_buje.py. Resultados: resultados/cargas_pala_buje_ESCENARIOS.csv y cargas_pala_buje_resumen.json. La comprobación numérica verifica finitud, no validez física ni resistencia.
