# Reparación de ParaView

Fecha: 3 de noviembre de 2026. Solicitud: «No me funciono, arreglalo».

## Resultado comprobado

ParaView 6.2.0 para Apple Silicon está instalado en `/Applications/ParaView-6.2.0.app`. La prueba de versión, lectura OpenFOAM y renderizado terminó con salida 0. La ventana nativa se abrió con la escena CFD y se comprobó visualmente. No se requiere otra instalación del usuario para esta integración.

## Procedencia y comprobaciones

- Distribución: [servidor oficial de ParaView](https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v6.2&type=binary&os=macOS%20Silicon&downloadFile=ParaView-6.2.0-MPI-OSX11.0-Python3.12-arm64.dmg).
- Archivo descargado: `/private/tmp/aero-paraview-installer/ParaView-6.2.0-arm64.dmg`.
- SHA-256: `df762309fe739de605e093848ae335b3bcfbdcc95c51415120b18980b14608b9`, coincidente con el catálogo [Homebrew Cask](https://formulae.brew.sh/api/cask/paraview.json) consultado durante la reparación. La referencia de esa API puede cambiar con futuras versiones; se conserva la huella utilizada en `../ejecucion/G0/PARAVIEW_INSTALADOR.json`.
- `codesign --verify --deep --strict --verbose=2`: salida 0, válido en disco y requisito designado satisfecho.
- `spctl --assess --type execute --verbose=2`: salida 0, `accepted`, `Notarized Developer ID`.
- `Contents/bin/pvpython --version`: salida 0, `paraview version 6.2.0`.

Se montó el DMG en modo lectura y se copió el paquete con `ditto` a Aplicaciones. El primer intento no interactivo se canceló en la licencia; el montaje interactivo posterior terminó correctamente. No se desactivó Gatekeeper ni se eliminaron atributos de cuarentena.

## Prueba de funcionamiento

`probar_paraview.py` utiliza el `OpenFOAMReader` integrado sobre `../ejecucion/G0/poiseuille_80_outer50_dt_half/benchmark.foam`. Recuperó 80 celdas a t=4 s y un intervalo de magnitud de velocidad de 0,218053–15,380541 m/s. Guardó imagen, estado y registro JSON en `paraview/`. `paraview_prueba.log` conserva la salida del proceso.

Se abrió `benchmark_poiseuille.pvsm` en la interfaz nativa; el lector, la malla coloreada y la leyenda estaban visibles. Esto acredita funcionamiento de esta ruta de lectura y visualización. El benchmark verifica un problema numérico de canal; no valida ventiladores ni prestaciones de vuelo.

El intento anterior con el instalador `unsigned` terminó con código 137. No se aisló su causa exacta; no se atribuye retrospectivamente a una única causa por el éxito de esta instalación.

## Recomprobación posterior

Se repitieron `pvpython --version` y `probar_paraview.py` fuera del aislamiento de ejecución: ambos terminaron con salida 0. El lector volvió a recuperar 80 celdas a t=4 s y se regeneraron escena e imagen; registro `paraview_recomprobacion.log`. Se solicitó abrir esa escena con la aplicación instalada.

Un intento adicional dentro del aislamiento falló al iniciar MPI porque `listen()` sobre un puerto local devolvió `Operation not permitted`. La versión y el render funcionan fuera de ese aislamiento. Este fallo particular no demuestra una avería de la instalación ni explica por sí solo el fallo histórico de la distribución unsigned.

Para abrir manualmente la prueba desde Terminal, sin cambiar las protecciones de macOS:

```sh
open -a /Applications/ParaView-6.2.0.app '/Users/sam/Documents/ChatGPT/New project/investigacion-aeronautica/integracion_apps/paraview/benchmark_poiseuille.pvsm'
```
