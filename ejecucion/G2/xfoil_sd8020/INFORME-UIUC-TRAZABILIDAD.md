# SD8020: trazabilidad de las mediciones y comparación de ramas

4 de noviembre de 2026, hora de Bogotá. Se revisó la documentación primaria de UIUC y se compararon archivos experimentales distintos. Los resultados son diagnósticos; **no autorizan una polar de rotor ni un cierre de potencia**.

## Qué documenta el ensayo

El [volumen 1 de UIUC](https://www3.nd.edu/~ame40462/SeligVol1.pdf), capítulo 2, describe modelos de cuerda nominal de **12 pulgadas** (0,3048 m), una intensidad de turbulencia del túnel inferior al **0,1 %** y velocidades y propiedades ambientales medidas durante los ensayos. El mismo volumen explica que las corridas de sustentación y arrastre utilizaban procedimientos de reducción diferentes; no se deduce de ello que esas diferencias expliquen cuantitativamente una discrepancia concreta. UIUC indica que los datos de los volúmenes 1–2 fueron [actualizados posteriormente](https://m-selig.web.engr.illinois.edu/pd.html); no se ha demostrado que todos los detalles de reducción del libro de 1995 describan exactamente la revisión digital local.

**Estimación, no medición del ensayo:** tomando Re=61.400, cuerda 0,3048 m y ν=1,46×10⁻⁵ m²/s, `U = Re·ν/c` da aproximadamente **2,94 m/s**. Con a=340,3 m/s resulta **M≈0,00865**. La temperatura y viscosidad efectivas deben recuperarse de la corrida para fijar sus valores reales. Ncrit=9 en XFOIL sigue siendo un supuesto y no se obtiene directamente de una única cifra de turbulencia.

El volumen original señala comportamiento no lineal cercano a sustentación nula para el **SD8020** y lo relaciona con burbujas de separación; también describe ensayos con dispositivos de transición. Eso aporta contexto al comportamiento observado, pero no demuestra que el cálculo actual reproduzca correctamente la física ni justifica modificar la superficie de la pala sin un estudio nuevo. [UIUC, capítulo 3](https://www3.nd.edu/~ame40462/SeligVol1.pdf).

UIUC indica que en torno a Re=60.000 y por debajo las variaciones de arrastre pueden dificultar una asignación fiable de exactitud. No se ha construido una incertidumbre numérica o experimental completa para esta comparación. [UIUC, sección 2.4](https://www3.nd.edu/~ame40462/SeligVol1.pdf).

## Dos series experimentales cercanas

El archivo `SD8020.LFT` contiene una corrida de sustentación a **Re medio 60.600** con registros de ángulo creciente y decreciente. `SD8020.DRG` contiene sustentación y arrastre a **Re medio 61.400**. Se interpolaron las dos ramas LFT en los ángulos DRG, sin extrapolar ángulos y sin corregir la diferencia de **−1,30 % en Re**. Las corridas no son mediciones idénticas ni simultáneas.

| α | Cl LFT creciente, Re 60.600 | Cl LFT decreciente, Re 60.600 | Cl DRG, Re 61.400 | Cl XFOIL exploratorio |
|---:|---:|---:|---:|---:|
| −0,29° | −0,04715 | −0,03820 | 0,0300 | 0,0022 |
| 1,17° | 0,02988 | 0,01082 | 0,1050 | 0,0138 |
| 2,72° | 0,25532 | 0,25481 | 0,3600 | 0,4003 |
| 5,89° | 0,51882 | 0,53203 | 0,6320 | 0,6621 |

Por ejemplo, a 1,17° el valor calculado queda cerca de la rama LFT decreciente, aunque difiere de la cifra DRG. A 2,72° difiere de ambas ramas LFT y de DRG. **No se elige la serie más favorable para declarar validación**: el origen de las diferencias entre corridas permanece sin resolver y todos los puntos XFOIL de esta comparación contienen avisos de marcha.

La comparación completa de diez ángulos, interpolación, ramas y huellas se reproduce con `comparar_ramas_UIUC.py` y queda en `uiuc_61400_r1/COMPARACION_RAMAS_LIFT.json`. El cálculo contrasta la interpolación con una referencia lineal simple. El RMSE exploratorio de Cl de XFOIL frente a LFT es 0,09926 para la rama creciente y 0,09244 para la decreciente; no son incertidumbres ni métricas con condiciones perfectamente igualadas.
