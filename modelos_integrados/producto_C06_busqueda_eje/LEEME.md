# C06 — alternativas para abrir una compuerta

Se comparan una bisagra interior y una tapa que se eleva y desliza, manteniendo
el rotor dentro del vehículo. **Ninguna alternativa es un mecanismo
funcional**: no se han diseñado guías, brazos de unión, actuadores, fijaciones,
topes, sellado, cargas ni respuesta aerodinámica. El trabajo corresponde a la
compuerta superior 0 de C03 de 5 kg objetivo, salvo donde se indique.

## Búsqueda de ejes

Se ensayaron 49 posiciones en una rejilla más el eje C04. Para cada eje en
cerrado se usó un cilindro de 56 mm de largo y radio 1,5 mm como reserva
hipotética de un pasador de radio 1 mm con 0,5 mm adicionales. Se evaluaron
seis objetos C03, con umbral de intersección de 0,00001 mm³ y rechazo de
contacto geométrico. De las 50 posiciones, 39 pasaron ese cribado puntual.
Una comprobación de hasta nueve rayos verticales a través de la carrocería y
la tapa dejó 11 ejes con superficie por encima en todas las muestras; esto no
prueba que el cilindro esté completamente confinado ni que exista soporte.

Para esos 11 ejes se evaluó el cilindro durante la elevación y la puerta en
siete posiciones discretas de elevación/giro, con los obstáculos enumerados
en `MOVIMIENTO.json` y umbral de 0,001 mm³. Los 11 pasaron las posiciones de
pasador muestreadas, pero la tapa colisionó en alguna posición. Como control,
el eje C04 no pasó el cribado del pasador y la puerta pasó las siete
posiciones muestreadas. No se puede extrapolar esto al espacio continuo.

Al ampliar la elevación a 20, 30 y 40 mm para cinco ejes interiores, dos de
los cinco con elevación de 40 mm superaron las posiciones discretas revisadas;
ninguno de los diez casos de 20 y 30 mm lo hizo. El ejemplo CAD elegido tiene
eje en y=−100 mm, z=65 mm y representa elevación 40 mm seguida de giro 110°.
El eje y la tapa no están unidos por herrajes modelados. El paso de aire puede
quedar obstruido. Véanse `ELEVACION.json`, `CASO_C06.json` y sus FCStd/STEP.

## Apertura deslizante

La tapa se eleva 10 mm y se traslada 100 mm en dirección longitudinal, con
orientación fija. Se probaron por separado ambas direcciones y elevaciones
10, 20 y 30 mm para la tapa superior 0. Las seis combinaciones superaron los
obstáculos y las posiciones muestreadas. Para la dirección elegida hacia la
nariz, la malla proyectada de la tapa en la posición final queda separada del
intervalo x del círculo nominal D84 por aproximadamente 12,2 mm; es una
medida de la **malla**, no una tolerancia de fabricación.

Además, se examinaron la tapa inferior del módulo delantero 0 y las tapas
superior e inferior del módulo posterior 2, cada una por separado mientras las
otras estaban cerradas: pasaron seis posiciones cada una. No se deduce de ello
el comportamiento simultáneo de ocho tapas; `../producto_C07_deslizante/`
contiene un estudio separado de ese movimiento.

Los archivos `C06_deslizante_cerrado.FCStd` y
`C06_deslizante_evaluacion.FCStd`, con sus STEP y PNG correspondientes,
contienen seis objetos locales y una tapa flotante en la posición abierta.
La ausencia de guías es visible y deliberada: son poses, no una unión. Ambos
pares se reabrieron/reimportaron con seis objetos válidos; sus centros de puerta
y rotor pasaron los contrastes de posición de `AUDITORIA_CASO_DESLIZANTE.json`.
El generador usó los resultados parciales ya disponibles; el mismo caso está
incluido en el archivo completo `DESLIZAMIENTO.json`.

## Comparación de proyección

Sobre un círculo nominal de diámetro 84 mm centrado en el módulo 0, la
proyección vertical de la tapa deslizante abierta cubre 0 % en las tres
resoluciones evaluadas. La tapa con bisagra y elevación de 40 mm cubre
aproximadamente 13,17–13,36 %. La diferencia entre resoluciones es una
sensibilidad del raster; no incluye el error de la teselación de 0,4 mm ni
otras fuentes de incertidumbre. La proyección no es área efectiva de flujo,
caudal, pérdida de presión ni eficiencia. `PROYECCION.json` conserva los
resultados; `verificar_proyeccion.py` pasa cuatro controles de círculo vacío,
completo, semicírculo y área.

## Reproducibilidad y límites

Los scripts `buscar_eje.py`, `auditar_cobertura.py`, `auditar_movimiento.py`,
`probar_elevacion.py`, `probar_deslizamiento.py` y
`probar_deslizamiento_familia.py` se ejecutan con el comando FreeCAD indicado
por el proyecto. Los resultados de cada etapa dependen de los JSON anteriores;
algunos cálculos tardan varios minutos. `verificar_operadores.py` contrasta
las operaciones booleanas y de giro con siete casos sintéticos; no valida la
geometría C03. Los renders usan mallas extraídas del CAD y piel/camisa
semitransparentes para inspección. Los archivos se sobrescriben al regenerar.
En este entorno, comprobar JSON y marcadores de fin: FreeCAD puede devolver
código 0 ante un fallo de script. Se conservó `render_bisagra_error.log` y se
corrigió su nombre de objeto.

Antigravity revisó posibles mecanismos y puntos ciegos; no se adoptaron como
resultados las afirmaciones no comprobadas de sus respuestas. La forma de la
tapa, la geometría C03, la masa objetivo y las prestaciones no quedan
validadas. Ninguno de estos estudios reanuda los CFD históricos.
