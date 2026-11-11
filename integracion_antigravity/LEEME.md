# Integración de Codex y Antigravity

## Estado y alcance

La aplicación Antigravity y su CLI `agy` están instaladas. La CLI local respondió
correctamente a consultas de conectividad el 7 de noviembre de 2026. Dos
conversaciones distintas se ejecutaron simultáneamente y terminaron bien; véase
`resultados/20261108T001846Z_65e44bb5/`. El coordinador de esta carpeta permite
enviar varias consultas independientes y
recoger sus respuestas; el resultado de cada una se revisa antes de integrarlo.
La conexión usa el acceso de red y la sesión de Antigravity existentes: no se
guardan credenciales en el proyecto. La disponibilidad puede cambiar por
autenticación, permisos, cuotas o disponibilidad del servicio.

El usuario reactivó la investigación el 7 de noviembre de 2026.
`tareas_preparadas.json` define análisis de lectura sobre archivos concretos;
su existencia por sí sola no demuestra que hayan terminado. Esta integración
no reanuda los contenedores CFD históricos pausados ni inicia cálculos
automáticamente.

## Prueba y uso

Desde la raíz del repositorio:

```sh
python3 investigacion-aeronautica/integracion_antigravity/verificar_orquestador.py
python3 investigacion-aeronautica/integracion_antigravity/orquestar.py --prueba
```

La primera orden prueba el coordinador con un ejecutable simulado y sin red. La
segunda envía dos mensajes inocuos a Antigravity y guarda respuestas y metadatos
en `resultados/`. Necesita una sesión de Antigravity válida, salida a Internet,
acceso a un puerto local y acceso a los datos y registros propios de la CLI.
Desde un entorno aislado puede ser necesario autorizar esos accesos; la prueba
sin ellos falló en este equipo.

Para comprobar además que un agente puede leer la documentación de esta propia
integración dentro del espacio de trabajo, se preparó `prueba_lectura.json`:

```sh
python3 investigacion-aeronautica/integracion_antigravity/orquestar.py \
  --tareas investigacion-aeronautica/integracion_antigravity/prueba_lectura.json \
  --trabajadores 1 --timeout 60
```

Esa prueba se completó con éxito tras la autorización del usuario; el resultado
está en `resultados/20261108T002302Z_8811f252/lectura_integracion.json`.

Con autorización para que Google procese los archivos de entrada identificados,
se pueden lanzar las tareas preparadas o un archivo con la misma estructura:

```sh
python3 investigacion-aeronautica/integracion_antigravity/orquestar.py \
  --tareas investigacion-aeronautica/integracion_antigravity/tareas_preparadas.json \
  --trabajadores 2 --timeout 300
```

El límite local configurable es de uno a cuatro procesos; no es un límite
garantizado por Google. Cada proceso usa una conversación nueva y escribe su
resultado en un JSON separado con horas, estado de la CLI, identificador de
conversación, uso informado y huella de la instrucción. `SUCCESS` acredita que
hubo respuesta, no que la respuesta sea correcta o completa. Revise `stderr`:
en modo no interactivo una solicitud de permisos puede ser denegada sin que la
CLI marque el proceso como fallido. No ponga secretos en las instrucciones;
estas se pasan como argumentos de proceso y se envían al proveedor.

## Límites y división de trabajo

El coordinador usa modo `plan`, sandbox y reglas por sesión que deniegan
escritura mediante herramientas, comandos, web y MCP. Son controles de
Antigravity, no una garantía independiente de aislamiento; no se usa el modo
que aprueba todo. En una carpeta temporal, una prueba independiente confirmó la
lectura de un archivo y la denegación de una escritura; otra confirmó la
denegación de un comando inocuo (`resultados/prueba_denegacion_comando.ndjson`).
No se probaron individualmente todas las herramientas web o MCP. La herramienta
puede consultar archivos del proyecto mediante
sus herramientas de lectura, pero no buscará fuentes en Internet con estas
reglas. Si requiere fuentes o acciones denegadas, debe informar de la ausencia.
No modifica la configuración global de Antigravity.

Los mensajes y los fragmentos de archivo que el agente use pueden transmitirse
a Google para procesar la solicitud. Revise los ajustes y las condiciones de
datos de la cuenta si el proyecto contiene información confidencial. En la
ventana de la aplicación inspeccionada aparecía seleccionado `Turbo`; el
coordinador no usa ese modo y no cambió la configuración de la aplicación.

Codex coordina, contrasta fuentes, revisa los informes y decide qué incorporar.
Los agentes preparan propuestas independientes sobre flujo, masa y energía,
propulsión interna y control; no promueven resultados a la línea base. A07
permanece como referencia conceptual y C02 como candidata separada. Cada
resultado debe citar rutas, hipótesis, fecha y límites físicos.

El primer lote de cuatro agentes se completó en paralelo; su revisión, que
incluye correcciones de afirmaciones excesivas, está en
`REVISION-LOTE-2026-11-07.md`.

## Delegación de trabajo editable aislado

`orquestar_aislado.py` distribuye hasta 32 tareas, con hasta 16 procesos
simultáneos configurables. Copia únicamente las entradas indicadas por tarea a
directorios temporales independientes, permite generar archivos y ejecutar
comandos dentro del sandbox de Antigravity, deniega ejecución fuera de él y
recoge solo los archivos de `salidas/` junto con sus huellas. No modifica
configuración global. Las salidas son candidatas y no se integran a la línea
base sin revisión; el aislamiento depende del sandbox de Antigravity y no es
una garantía de que los cálculos sean correctos.

La prueba `prueba_aislada.json` produjo un archivo Python, lo ejecutó en el
sandbox y devolvió dos entregables. El primer lote real inició 12 sesiones al
mismo tiempo. Ocho acabaron con respuesta técnica exitosa; cuatro finalizaron
con error o tiempo agotado, aunque algunas conservaron archivos parciales. Se
ha iniciado un segundo lote para revisar y recuperar los resultados. Véase
`ESTADO-LOTE-AUTONOMO-01.md`.

El coordinador de lectura registra ahora eventos de herramientas, errores y un
resumen de lote, y señala respuestas con avisos como `REVISAR`. Su prueba de
seis casos incluye detección de eventos truncados y cancelación de un proceso
propio. Los registros iniciales en formato JSON se conservan por separado.

El acceso web de los trabajadores editables está desactivado. Una prueba
aislada de lectura pública intentó sustituir un comando denegado y desactivar
la validación TLS; sus resultados no se aceptan. El supervisor incorpora una
vigilancia en vivo que intenta detener la sesión si observa una denegación de
política o una instrucción de desactivar certificados, y pasa tres pruebas
locales. Esta vigilancia complementa el sandbox; no elimina todos los riesgos ni
garantiza interceptar acciones antes de que se ejecuten. Las fuentes públicas
se incorporan como archivos locales antes de delegarlas.

Para permitir **ediciones** paralelas reales se necesitará un mecanismo de
aislamiento y una revisión de cambios. En el momento de esta comprobación Git
estaba inicializado pero no tenía un primer commit, por lo que no se han creado
worktrees ni se ha supuesto una línea base versionada. No se han instalado MCP
ni conectado una API específica: la integración probada invoca la CLI local.
La ejecución por CLI no implica que las conversaciones aparezcan como pestañas
en la aplicación; esa visibilidad aún no se ha verificado.

## Fuentes

- [Modo no interactivo y salida JSON de Antigravity](https://antigravity.google/docs/cli/headless/).
- [Modos de ejecución](https://antigravity.google/docs/cli/modes).
- [Permisos y prioridad de reglas](https://antigravity.google/docs/permissions?tab=cli).
- [Disponibilidad y cuotas](https://antigravity.google/docs/plans).
- [Uso y tratamiento de datos de Google Antigravity](https://antigravity.google/terms).
- [Presentación de la plataforma y el Agent Manager](https://developers.googleblog.com/en/build-with-google-antigravity-our-new-agentic-development-platform/).
