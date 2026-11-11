# C10 — enlace ideal de longitud variable

**Estado: no se ha encontrado una conexión apta en los casos ensayados.** Se
probó una alternativa a los enlaces rígidos trasladados de C09: un cilindro
de radio 1,5 mm une un pivote supuesto fijo en una de las reservas C08 con un
punto que se mueve con la tapa C07. El cilindro cambia de longitud y dirección
según la posición. No existen en este CAD un mecanismo telescópico, sus
articulaciones, actuadores, soportes, unión a la tapa o sello.

## Qué se examinó

Se tomaron los 20 puntos de conexión C09 que en cerrado solo penetraban el
objeto combinado `camisa_cuna_y_soportes`. Se **permitió esa penetración como
hipótesis**; no hay un paso abierto ni sellado. Cada enlace se comprobó frente
a los demás obstáculos C03, las otras tapas en movimiento y cuatro envolventes
cilíndricas de rotor nominal. Se usan cajas óptimas ampliadas 0,05 mm, booleanos
y un umbral volumétrico de 1e−5 mm³. No se incluyen deformaciones ni
holguras mecánicas. La propia tapa y la propia reserva de guía se excluyen del
control de obstáculos por ser interfaces propuestas; el contacto volumétrico
con la tapa se comprueba de forma simplificada, no es una unión diseñada.

| Elevación de la tapa | Poses examinadas por caso | Primera colisión detectada | Contacto con tapa no establecido | Pasan las muestras |
|---|---:|---:|---:|---:|
| 10 mm | Hasta 7 | 19 de 20 | 1 de 20 | 0 |
| 30 mm | Hasta 8 | 19 de 20 | 1 de 20 | 0 |

La prueba termina en la primera colisión o en la falta de contacto; por eso
no identifica todos los obstáculos posteriores para cada candidato. La falta
de contacto puede depender del punto tomado de la malla y de la forma del
extremo del cilindro, y **no demuestra una colisión**. Los resultados no
excluyen enlaces curvos, otros pivotes, aberturas, accionamientos, tapas o
trayectorias. Son posiciones discretas y no una comprobación continua.

Para los dos enlaces más cortos se midieron los obstáculos durante ocho
posiciones de la opción de 30 mm (`RUTA_30.json`). En las poses ensayadas se
registran cruces con camisa–cuna–soportes, aro, junta y piel; no se registraron
cruces con los cilindros nominales de rotor en esas poses. No se ha dimensionado
ni aceptado ninguna modificación de esas piezas.

## CAD de diagnóstico

`C10_diagnostico.FCStd` y `C10_diagnostico.step` muestran un caso rechazado:
enlace ideal, tapa y piel en la posición donde se detectó una intersección.
`DIAGNOSTICO.json` conserva las coordenadas y volumen calculado. El objeto
`interseccion_piel` se superpone deliberadamente a las piezas para inspección;
no debe incluirse en una lista de piezas o masa. `C10_diagnostico.png` utiliza
piel y camisa translúcidas; el marcador rojo se amplía para hacer visible el
choque. El rotor sigue dentro del cuerpo.

La auditoría `AUDITORIA_CAD.json` comprueba reapertura, reimportación de ocho
objetos y reproducción de esa colisión; no prueba equivalencia completa entre
formatos ni viabilidad del mecanismo. `verificar.py` pasa tres controles de
consistencia de datos y clasificación, no pruebas de vuelo. `RESUMEN.json`
registra las huellas de entrada y resultados. FreeCAD puede terminar con
código 0 ante errores de script: revisar también los JSON y los marcadores de
fin en los logs. Los generadores sobrescriben archivos C10.

## Siguiente problema de diseño

Estudiar una unión que no requiera una barra recta desde esos pivotes durante
toda la carrera, o modificar coordinadamente piel, aro, camisa y sellos y
comprobar sus consecuencias estructurales y de flujo. Este estudio no cambia
la arquitectura seleccionada de ventiladores internos ni valida masa,
maniobrabilidad, velocidad o la variante de 10 kg. No reanuda CFD históricos.
