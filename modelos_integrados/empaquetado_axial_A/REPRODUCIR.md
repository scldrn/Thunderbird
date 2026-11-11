# Reproducir la comparación de estaciones

Desde la raíz del proyecto, con el entorno `.venv-cad` ya instalado:

```sh
XDG_CACHE_HOME=/tmp/codex-aero-cache .venv-cad/bin/python investigacion-aeronautica/modelos_integrados/buscar_estaciones_axiales_A.py
XDG_CACHE_HOME=/tmp/codex-aero-cache .venv-cad/bin/python investigacion-aeronautica/modelos_integrados/verificar_candidato_axial_A.py
.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/control_reversible_estaciones_A.py
```

El orden importa: la última operación añade los dominios reversibles al informe regenerado por la segunda. Las entradas son la envolvente cerrada medida y el STEP neutral de la rama de doble flujo. Los scripts conservan el diseño seleccionado en su carpeta original y generan alternativas separadas.

`POSES.json` contiene pruebas conservadoras de alojamiento. `RESUMEN.json` conserva la malla finita, el prefiltrado geométrico, capacidades y posiciones. `VERIFICACION.json` reevalúa los mecanismos del STEP, cajas de barrido de todo el intervalo en los cuatro canales, reserva axial, equilibrio ideal y momentos a igual capacidad. `CONTROL_REVERSIBLE.json` añade los dominios más exigentes. Los STEP de 110 piezas representan reservas, no un vehículo ligero fabricable ni una instalación de motor.

Los resultados no incluyen los accionamientos y soportes que todavía no tienen geometría, un presupuesto de masa/CG real, presión/caudal o arrastre de instalación. El volumen cilíndrico reservado es de diámetro exterior; no se presenta como sección de aire útil ni selección de propulsor.
