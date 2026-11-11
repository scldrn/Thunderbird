# RAE2822 en SU2: campos estables y contraste todavía provisional

3 de noviembre de 2026. SU2 8.6.0 ARM64 funciona dentro del proyecto. La continuación adaptativa alcanza el criterio configurado para densidad, con presión/densidad positivas y cargas casi constantes. Esto mejora la base computacional; todavía no valida el experimento completo ni las prestaciones del vehículo.

Actualización: r3 terminó y se auditó frente a r2. La reconstrucción posterior de tracción completa coincide con las cargas nativas; la integral tangencial incompleta descrita abajo se conserva como antecedente. [INFORME-NASA-SU2.md](INFORME-NASA-SU2.md) documenta además tres corridas separadas con la malla y condiciones dimensionales de NASA, así como el refinamiento en curso. No mezclar las dos familias de geometría/condiciones.

## Configuración y alcance

Se emplea el casoSST de la fuente oficial8.6.0 y una malla del repositorioTestCases en la revisión4d2b3728e93f657199c9eec1919c4a752e1159cb. `AUDITORIA_MALLA_SU2.json` verifica13937puntos,22842elementos positivos, conectividad de frontera y perfil cerrado. Es un método de volúmenes de control duales por nodo, distinto del casoOpenFOAM anterior.

Se conservan Mach0,729, α2,31°, Re6,5millones, cuerda1m, T∞288,15K, intensidad0,1% yνt/ν=100 del caso oficial. El log confirmaSST-2003m, aire estándar, R287,058J/(kgK), γ1,4, Sutherland y Pr0,72/0,9. La reconstrucción independiente de la referencia da p∞≈38779,2Pa, ρ∞≈0,468824kg/m³, U∞≈248,077m/s y q∞≈14426,19Pa.

Se conserva JST, Euler implícito, multigrid3 yFGMRES/LU_SGS. R1completa600iteraciones conCFL100, sin convergencia. R2continúa por reinicioASCII y activa el controlCFL adaptativo cuyos parámetros ya figuran en el caso oficial; los modelos y la geometría permanecen iguales. Estos casos son una referencia de operatividad y convergencia del segundo método, con diferencias físicas respecto aNASA declaradas más abajo.

## Resultados auditados de r2

R2termina con salida0 en62,87s de reloj. Realiza1085pasos adicionales, índices0–1084, después de los600del arranque. El programa informa que cumple sus criterios, pero el log identifica exclusivamente `RMS_DENSITY` como campo de parada. Esa declaración no cubre por sí sola todas las ecuaciones.

| Magnitud final | Resultado calculado |
|---|---:|
| CL | 0,7076833 |
| CD | 0,01285339 |
| Deriva entre medias de20, CL/CD | 3,72×10⁻⁷ / 2,42×10⁻⁹ |
| Presión absoluta, rango | 21649–55164Pa |
| Temperatura, rango | 243,10–318,70K |
| Mach local máximo | 1,24786 |
| y+ reportado sobre nodos de pared | 0,965–3,515 |
| ErrorRMS deCp,103puntos | 0,103901 |
| Mayor error absolutoCp | 0,934911 |

El error máximo corresponde al punto superior x/c=0,0002. El contraste conserva los103puntos; no se elimina ese valor. Su posición y la separación de nodos cerca del borde de ataque justifican estudiar resolución/interpolación local, pero no prueban que toda la diferencia sea de malla.

El máximo del residuo log10 de densidad en las últimas20es−7,9387; los de momentoX/Y son−5,6234/−6,0731, el de energía−2,7892, k−4,3467 yω+4,4528. Debe revisarse la definición, escala y tratamiento de frontera de esos residuos, y verificar cambios reales del estado turbulento antes de declarar convergencia completa.

## Comprobaciones y límites del posprocesado

`auditar_su2.py` comprueba todos los camposCSV/VTK finitos, identifica los nodos por coordenadas, reconstruye la referencia dimensional y verifica el coeficienteCp usando la presión exportada. Se normaliza correctamente la ordenadaNASA−Cp y se asignan los103puntos a las dos caras del polígono real sin extrapolar x/c.

La presión reconstruida desde la energía conservada y k difiere hasta0,001903Pa de la primitiva guardada, unos4,11×10⁻⁸relativos. La [fórmula de la variableNavier–Stokes](https://github.com/su2code/SU2/blob/v8.6.0/SU2_CFD/src/variables/CNSVariable.cpp) resta k de la energía interna; el [orden segregado de actualización](https://github.com/su2code/SU2/blob/v8.6.0/SU2_CFD/src/iteration/CFluidIteration.cpp) actualiza flujo y turbulencia en etapas distintas. Se mide esa discrepancia, compatible con el desfase de actualización, sin imponer una identidad termodinámica exacta entre estados de etapas diferentes.

Se evaluó una integración independiente de presión y esfuerzo tangencial sobre el polígono. Su diferencia con la fuerza total del solver es aproximadamente(1,17×10⁻⁵;2,33×10⁻⁶)en coeficientesX/Y. La [implementación de fuerza viscosa](https://github.com/su2code/SU2/blob/v8.6.0/SU2_CFD/include/solvers/CFVMFlowSolverBase.inl) usa la tracción completaTau·n y áreas duales; el campo `Skin_Friction_Coefficient` exporta solo la parte tangencial. Por ello esta reconstrucción incompleta no se etiqueta como un balance total verificado. Faltan tensión normal y pesos de área correspondientes.

## Convergencia completa y similitud experimental pendientes

R3 terminó 200 iteraciones adicionales, salida 0. Su auditoría compara todos los campos: la mayor diferencia relativa L2 es 2,09×10⁻⁴ en k, con máximo absoluto 1,287 m²/s² en un nodo cercano al borde de ataque inferior. Los coeficientes permanecen casi constantes, pero no se declara convergencia completa por el criterio de densidad. No cambian modelos, malla ni condiciones libres.

`su2_r3_estado_completo/TRACCION_RECONSTRUIDA.json` verifica posteriormente la tracción completa y las normales duales: la mayor discrepancia de coeficiente de fuerza es 2,4×10⁻¹¹. El cálculo original con fricción tangencial continúa etiquetado como incompleto; no se lo convierte en una identidad total. El balance exterior y la validación experimental son comprobaciones distintas.

El estudioNASA usado enOpenFOAM tieneT∞255,5556K, cuerda0,3048m yνt/ν supuesto1. La mallaSU2 difiere del polígonoNASA hasta0,001509c en distancia unidireccional de vértices. Temperatura, transporte, turbulencia y geometría deben alinearse o tratarse mediante sensibilidades para un contraste físico defendible. También faltan refinamiento de pared/borde de ataque, presupuesto completo de fuerzas y comparación de modelos. Los coeficientes de esta tabla siguen siendo diagnósticos; no se transfieren al cuerpoC02, a sus ventiladores ni a600–1000km/h.
