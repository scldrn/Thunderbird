# SU2 8.6.0 nativo ARM64: instalación local y primera ejecución

3 de noviembre de 2026. Se compiló y ejecutó SU2_CFD dentro del proyecto, sin modificar la configuración global del sistema. El caso oficial RAE2822 completó600 iteraciones con salida0 y campos finitos. Esto comprueba la operatividad del programa; ese arranque todavía no convergió ni valida el vehículo.

## Procedencia y compatibilidad

La [publicación oficial8.6.0](https://github.com/su2code/SU2/releases/tag/v8.6.0) proporciona un binario macOSIntel. SuSHA-256 coincide con el publicado porGitHub, pero este equipoARM64 rechaza su ejecución con salida127 (`bad CPU type`). Ese intento y el archivo descargado se conservan; no se instalóRosetta.

Se obtuvo la fuente oficial del mismo tag, prefijo de revisión7048fd3, y se compiló con AppleClang21.0.0, Meson y Ninja enARM64. `FUENTE_VERIFICADA.json`, `EIGEN_VERIFICADO.json` y `COMPILACION_NATIVA.json` registran archivos, huellas, opciones, tiempos y ruta del ejecutable. Se usó Eigen en la revisión fijada porSU2, y las revisiones deMeson/Ninja/MEL elegidas por su inicializador. La [guía oficial de compilación](https://su2code.github.io/docs_v7/Build-SU2-Linux-MacOS/) documenta las herramientas y opciones.

Se compila soloSU2_CFD, en doble precisión, dos procesos de compilación, sinMPI/OpenMP, adjuntos, envoltorioPython, CGNS oTecIO. La salidaVTK/CSV permanece disponible. El ejecutable resultante esMach-O ARM64, huella `a12399dbec97a0cb6b86153bf978c74c2b2de66b43f4e4435c53cce7a8abe05f`.

Se conservan tres incidencias de preparación: detección errónea delGit padre al usar una fuente archivada, un nombre de argumento del inicializador corregido y la localización explícita delNinja compilado. No se modificó el código científico deSU2. El directorio fallido `build-native` se conserva; la compilación correcta usa `build-native-r2`.

## Prueba operativa

`../../ejecucion/G4/RAE2822/su2_r1_oficial/` contiene la malla oficial de13937puntos y22842elementos, su configuraciónSST8.6.0 y la ejecución acotada. Cambios: límite600 en lugar99999, intervalo de salida200 y formatos explícitos. Se retienen JST, multigrid3, FGMRES/LU_SGS yCFL100 de la configuración oficial.

La ejecución tarda55,60s de reloj, termina con salida0 y comunica que alcanzó el máximo antes de converger. Los campos conservados finales son finitos, conρmín≈0,2353kg/m³; reconstruyendo la presión ideal a partir de energía, momento yk se obtiene pmín≈20824Pa. Los coeficientes diagnósticos impresos al final sonCL≈0,79849 yCD≈0,020536; no están aprobados.

`su2_r2_adaptativo/` continúa desde ese reinicioASCII, activa los parámetrosCFL adaptativos ya presentes en el caso oficial y permite hasta2000iteraciones adicionales. También solicita salida de variables primitivas e historial de coeficientes. Consultar su proceso real y auditoría antes de aceptar resultados.

## Límites

El caso oficial coincide conNASA enMach0,729,Re6,5millones yα2,31°, pero difiere en temperatura, cuerda, viscosidad turbulenta libre, discretización y geometría. El mayor alejamiento unidireccional de vértices del perfil respecto al polígonoNASA es0,001509c. Se estudia primero la operatividad y convergencia; faltan contrasteCp normalizado correctamente, condiciones equivalentes, sensibilidad de malla/modelo y cargas conservadas.

El programa se invoca por ruta absoluta desde los scripts del proyecto. No es necesario añadir variables permanentes al perfil de la terminal ni instalar otros programas para repetir estas ejecuciones.
