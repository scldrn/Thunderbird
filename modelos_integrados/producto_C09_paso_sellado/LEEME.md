# C09 — evaluación de pasos para enlaces de tapa

**Resultado: no se acepta aún un paso en el conducto.** Se analizaron los 36
 enlaces rectos del par de reservas C08 a alturas distintas, para una tapa de
la geometría C03/C07 de 5 kg objetivo. Son barras y trayectorias ideales; no
hay carros, uniones, actuadores o sellos diseñados.

En cerrado, 20 de 36 barras penetran únicamente el objeto CAD combinado
`camisa_cuna_y_soportes` entre los obstáculos evaluados; ese objeto no es
solo pared de conducto. Cada barra se evaluó frente a los restantes registros
C03 excepto su propia tapa —contacto intencional aún sin diseñar— y a cuatro
cilindros de barrido nominal de rotores. Las otras 16 chocan también con otras
piezas. Se usaron cajas óptimas ampliadas y booleanos, con umbral de volumen
1e−5 mm³; no se valida el filtrado de superficies continuas ni tolerancias.

Se estudiaron las 20 barras durante siete posiciones ideales de elevación y
traslación, permitiendo como hipótesis la intersección con el componente
combinado. **Ninguna de las 20 pasó todas las muestras**: la primera
interferencia adicional detectada fue el aro en siete casos y la carrocería
en 13. El ensayo se detuvo en el primer obstáculo; no es una lista exhaustiva
de colisiones por barra. Son posiciones discretas y no descartan enlaces
curvos, otras guías, otras trayectorias o cambios de arquitectura.

Para los dos enlaces más cortos, `RUTA_DETALLADA.json` registra todas las
interferencias con los obstáculos considerados en siete poses. En cerrado,
ambos atraviesan el componente combinado; al desplazar 25 mm, ambos atraviesan
la carrocería. El enlace del lado y=−25 mm también atraviesa aro y junta en
la posición elevada. Por ello **un recorte de la camisa únicamente sería
insuficiente para estos dos casos**; no se ha generado ni aceptado un recorte.

`ENLACES.json`, `MOVIMIENTO_ENLACES.json`, `MOVIMIENTO_RESTO.json` y
`RUTA_DETALLADA.json` contienen entradas y resultados. Los scripts de este
directorio se ejecutan con `freecadcmd` y dependen de C03 y C08; escriben y
pueden sobrescribir sus JSON. `python3 .../verificar.py` comprueba consistencia
entre los registros, no valida física. Antigravity aportó una revisión
conceptual de posibles sellos; no se han adoptado sus afirmaciones de
hermeticidad o rendimiento. No se reanudaron los CFD históricos.
