# Integración de aplicaciones — A07

Actualizado: 3 de noviembre de 2026, America/Bogota.

## Blender
Blender 5.2.3 LTS comprobado: importación de 208 piezas desde el STEP A07 de 5 kg objetivo, guardado de .blend y render Cycles CPU terminado. La ejecución dentro del aislamiento falló al detectar Metal; fuera de él se completó. No se modificaron preferencias globales ni la seguridad del sistema.

Abrir `blender/A07_ventiladores_internos.blend`. Colecciones: Exterior, Interior, Compuertas, Aletas y Estudio. Unidades m. Fotogramas 1/40/100: cerrado/elevado/abierto. Esta animación interpola un recorrido conceptual, no un mecanismo dimensionado o una simulación de vuelo. La interpolación Blender no constituye la verificación de 61 posiciones del estudio A07. Se incluyen ejes como objetos vacíos de construcción; no son herrajes. `crear_escena.py` regenera el archivo desde `cad_A07.json.gz`.

## FreeCAD
La copia incompleta de `/Applications/FreeCAD.app` se reparó desde el instalador completo montado el 3 de noviembre. El ejecutable instalado `Contents/Resources/bin/freecadcmd --version` respondió FreeCAD 1.1.4, revisión 20260928, con salida 0 fuera del aislamiento. La importación anterior del STEP, realizada con la copia completa del instalador, produjo 300 objetos documentales, 293 con Shape no nula, sin formas inválidas; estos recuentos de la jerarquía importada NO son un nuevo recuento de piezas de diseño.

El archivo FCStd conserva sólidos importados, no reconstruye el historial paramétrico de fabricación. Archivo: `freecad/A07_ventiladores_internos.FCStd`.

## ParaView
Reparado el 3 de noviembre de 2026 a petición del usuario. Se descargó la distribución oficial estándar 6.2.0 Apple Silicon, en sustitución del intento anterior con el instalador `unsigned`. Se comprobó SHA-256, se instaló en `/Applications/ParaView-6.2.0.app` y se verificaron firma y notarización. `pvpython --version` terminó con salida 0. La causa precisa del código 137 anterior permanece sin demostrar; el resultado nuevo sí está comprobado.

`probar_paraview.py` leyó el resultado OpenFOAM de 80 celdas, t=4 s, y guardó `paraview/prueba_cfd.png`, `paraview/benchmark_poiseuille.pvsm` y `paraview/PRUEBA.json`. La interfaz se abrió con esa escena y se comprobó visualmente. Es un benchmark de canal, no una simulación del vehículo.

Repetir desde la raíz del repositorio, fuera del aislamiento si macOS lo requiere:

```sh
/Applications/ParaView-6.2.0.app/Contents/bin/pvpython investigacion-aeronautica/integracion_apps/probar_paraview.py
```

Para inspeccionar la escena: ParaView → File → Load State → `paraview/benchmark_poiseuille.pvsm`. La escena contiene rutas absolutas al benchmark del proyecto. Véase `REPARACION-PARAVIEW.md` para procedencia y comprobaciones.

## Alcance
Son pruebas de integración y formatos nativos, no nuevas verificaciones aerodinámicas, estructurales o de vuelo. La arquitectura seleccionada continúa siendo ventiladores internos. No se reanudaron los cálculos CFD pausados.
