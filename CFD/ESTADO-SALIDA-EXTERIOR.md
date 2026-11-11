# Ensayo exterior del canal: arranque en ejecución

La malla del conducto aislado con seis álabes y aire exterior pasó `checkMesh -allGeometry -allTopology`: 1.263.510 tetraedros, no ortogonalidad máxima 57,236°, skewness máxima 0,72055 y un único dominio fluido conectado. Son criterios de calidad de malla; no demuestran resolución de capa límite ni independencia de malla/dominio. `GEOMETRY_AUDIT.json` contrasta el volumen con fórmula independiente y verifica orientación positiva de tetraedros.

El dominio exterior tiene radio 0,336 m y se extiende 0,504 m aguas abajo del labio. El taladro tiene radio 42 mm y la camisa exterior radio 46 mm. No es el CAD A completo ni contiene rotor, motor o carrocería. Se conserva la geometría interna del canal antiguo, pero se agregan pared exterior, labio y contornos lejanos; también cambia malla, campo inicial y turbulencia ambiente. No es una comparación de una única variable.

## Inicialización

`potentialFoam -initialiseUBCs` resolvió un campo potencial para mejorar continuidad inicial. La divergencia absoluta media de volumen notificada es 5,0161e−7 s⁻¹ y el indicador integrado normalizado aproximadamente 5,20e−7. Todos los valores interiores de velocidad son finitos.

El máximo inicial es 226,93 m/s en (−0,027480; 0,017115; −0,033871) m, cerca de un álabe. Con velocidad de sonido supuesta 340,3 m/s equivale a Mach 0,667. El campo potencial no incluye separación, viscosidad ni compresibilidad: ese pico impide interpretarlo como solución física incompresible aceptada. El ensayo temporal se usa únicamente para diagnosticar arranque y evolución. Si persisten velocidades locales altas, será necesario tratamiento compresible y revisión geométrica/resolución antes de aceptar cargas. No se recorta artificialmente U, lo que rompería continuidad.

## Configuración y procesos

URANS SST, Euler, convección upwind, dos correcciones exteriores, Courant máximo 0,3 y paso inicial 1e−7 s. Velocidad impuesta de entrada 40 m/s. Presión cinemática cero en el contorno lejano con entrada/salida de velocidad según presión. Turbulencia de entrada k=6 m²/s², omega=894,43 s⁻¹; ambiente k=1e−6 m²/s², omega=10 s⁻¹. Son condiciones supuestas, pendientes de sensibilidad.

Ventana solicitada: 0,00025 s; es deliberadamente un diagnóstico corto y queda muy por debajo del descarte físico de 0,01 s. No se aceptarán cargas medias ni se dimensionarán servos con ese resultado. Se registran fuerzas sobre cada álabe, paredes y todos los sólidos, tracción en toda la frontera, transporte de momento, integral de velocidad y caudales.

Solver iniciado y confirmado vivo con `docker top`: contenedor `codex-aero-exterior-urans-v1`, sesión de ejecución 23250. Vigilante: sesión 36522, `WATCHDOG_STATE.json`; solicita parada ordenada ante U no finita, U>1000 m/s o colapso extremo de paso. Son umbrales de catástrofe numérica, no criterios de exactitud. El contenedor auxiliar de inicialización se detuvo expresamente tras guardar resultados; su código de parada no es un fallo del solver exterior.

No reiniciar por una consulta que ceda el control. Consultar Docker y avance del registro. `ejecutar_transitorio.py` conservará campos y series al terminar y comprobará si alcanzó el tiempo solicitado. La aceptación física continúa pendiente del muestreo, sensibilidad, balance, compresibilidad local y mapa de propulsor instalado.

## Evolución y vigilancia complementaria

El archivo de máximos muestra caída de 226,93 m/s iniciales a 116,20 m/s a t=0,0000165144 s. El pico sigue siendo diagnóstico del arranque, no una solución física aceptada. La impresión de máximos en log no quedó confirmada pese a habilitar log=true sin modificar parámetros de flujo. Se añadió `vigilar_campos_exterior.py`, sesión 29596, que observa directamente el archivo de diagnóstico y guarda `WATCHDOG_FIELDS_STATE.json`. Complementa al vigilante 36522 de paso/log, sin reiniciar el solver 23250.
