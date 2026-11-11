# Estado de la orquestación con Antigravity

**Corte: 8 de noviembre de 2026, 04:08 UTC (7 de noviembre, 23:08 en Bogotá).**
El usuario solicitó delegación paralela. Antigravity se ejecuta mediante su CLI,
con una conversación y un directorio temporal independientes por tarea. Las
salidas se copian a `sesiones_aisladas/`; no se incorporan automáticamente a
las bases aceptadas del proyecto. La concurrencia real y los errores figuran en
los archivos `RESUMEN.json` y `EJECUCION.json` de cada lote.

En nueve lotes de trabajo se despacharon **57 tareas**; en este corte se habían
recogido 46 y 11 seguían en curso. De las recogidas, 24 activaron la bandera de
revisión del supervisor: incluye tanto errores recuperables de comandos como
tiempos agotados o fallas de ejecución. Las tareas sin esa bandera también
necesitan revisión científica. No se resume el progreso del proyecto mediante
estos conteos ni se presenta el número de pruebas informado por una sesión como
validación experimental.

## Resultados candidatos prioritarios

- Dos paquetes reproducibles procesan los datos de una hélice abierta UIUC de
  81,28 mm, en estático y en avance. Se han despachado revisiones independientes
  de archivos, fórmulas y pruebas. Esa hélice no es el ventilador interno C02.
- Un paquete compara modelos matemáticos de discos abiertos para 2, 5 y 10 kg.
  Por ejemplo, con semejanza geométrica, cuatro discos ideales y ρ = 1,225 kg/m³,
  obtiene potencias inducidas de aproximadamente 518, 1509 y 3388 W en
  estacionario; no son potencias eléctricas instaladas ni demostración de vuelo.
- Se preparan entregables sobre equilibrio del centro de masa, demanda de
  empuje descendente, energía y respuesta de actuadores. Las cifras dependen de
  supuestos, y algunas requieren corrección y comprobación independiente.
- Las auditorías cruzadas señalan que una reserva CAD sin masa asignada tiene
  masa **desconocida**, que faltaba información al atribuir una marca de motor,
  y que la convención adoptada para C02 orienta +y CAD hacia la derecha. También
  se corrigió la inferencia de que un archivo no entregado a una sesión no existe.

## Límites y supervisión

Dos sesiones terminaron con `Operation not permitted` y sin suficiente registro
para identificar la causa exacta; sus salidas quedan en cuarentena. El
supervisor se modificó después para conservar el flujo de eventos si falla una
señal, impedir despachar tareas pendientes cuando una interrupción no se
confirma, y detectar archivos añadidos o modificados en las entradas. Esto no
modifica el código cargado por los lotes ya iniciados. Las pruebas locales del
supervisor pasan; no son una garantía absoluta de aislamiento.

El acceso web automático de las sesiones permanece desactivado: las fuentes se
entregan como archivos de referencia. No se han reanudado los CFD históricos
pausados. La arquitectura seleccionada sigue siendo la de ventiladores
internos y todavía no hay mapa instalado, balance completo de masa y energía ni
validación física del vehículo. Las tareas en curso pueden finalizar con error o
requerir nuevas correcciones.

Fuentes principales de los datos de referencia: [UIUC Propeller Database,
volumen 2](https://m-selig.web.engr.illinois.edu/props/volume-2/propDB-volume-2.html)
y [NASA, ensayos de ventilador entubado,
2024](https://ntrs.nasa.gov/api/citations/20230017299/downloads/Weinstein_SciTech2024_Final.pdf?attachment=true).

## Continuación posterior al corte

**Segundo corte: 8 de noviembre, 04:27 UTC.** Los registros contabilizan 76
tareas de trabajo despachadas en 18 lotes, 67 recogidas y nueve aún pendientes o
en curso. Cuarenta y dos de las recogidas tienen alguna bandera de revisión;
esa cifra incluye tanto errores corregibles de comandos como fallos, y no
equivale a 42 resultados científicamente rechazados. Las demás no quedan
aprobadas automáticamente.

Se incorporaron referencias UIUC de
[estático](../ejecucion/G2/referencia_uiuc_mi32_r1/estatico/README.md) y
[avance](../ejecucion/G2/referencia_uiuc_mi32_r1/avance/README.md), con datos,
código, tablas y huellas. Pasaron localmente 18 y 11 pruebas respectivamente;
se eliminó una aserción numérica basada en una incertidumbre no documentada. No
se trasladaron los informes automáticos
que afirmaban sin evidencia rotura, flutter o pérdida de sensibilidad fuera del
intervalo medido; tampoco se aceptó su revisión automática acrítica. El código
del caso de avance se corrigió para retirar afirmaciones similares.

Se despacharon tareas adicionales de cinemática y fallos de compuertas, y de
contratos para datos de masa y propulsión. Una primera revisión de la cinemática
encontró una contradicción sobre el jerk en los extremos del perfil quíntico:
los límites unilaterales no son cero, aunque velocidad y aceleración sí lo son.
Se encargó una corrección independiente; sus resultados todavía son candidatos.
El detector del supervisor también se amplió para reconocer denegaciones
registradas en la salida de comandos. Estas mejoras afectan los nuevos procesos,
no los que ya estaban en curso.

La prueba nueva del integrador 6DOF se ejecutó en un entorno con NumPy y SciPy:
los tres casos imprimieron resultados favorables, pero la ejecución terminó en
error al serializar un valor booleano en JSON. Se conserva el log en
`ejecucion/G6/verificacion_6dof_antigravity_r1/FALLO_SERIALIZACION.log` y se
delegó una corrección. No se considera superada la batería completa hasta que
termine con código de salida cero y reporte legible. El supervisor recibió
además una corrección para esperar brevemente la salida normal de un proceso
antes de intentar finalizarlo después del cierre de sus tuberías.
