# Renders CAD para presentación

Generados por trazado de rayos CPU (Mitsuba 3.9.1) desde los ensamblajes STEP de esta investigación. No se utilizó generación de imágenes por IA.

- `render_CAD_5kg_exterior.png`: variante con masa objetivo de 5 kg.
- `render_CAD_10kg_exterior.png`: variante con masa objetivo de 10 kg.
- `render_CAD_10kg_interior.png`: vista con carcasa oculta para mostrar la integración.

Las piezas originales conservan su forma, posición y escala. Colores y materiales son de presentación. Se ocultan los volúmenes auxiliares del conducto y barridos. Se añaden siluetas de palas dobles dentro de los discos existentes y ejes/bujes cilíndricos ilustrativos, exclusivamente para comunicar la disposición: no representan perfiles, mecanismos de paso variable, bujes o conexiones ya diseñados o validados. No se han modificado los STEP originales.

Las etiquetas de 5 y 10 kg son objetivos, no masas alcanzadas. Los presupuestos anteriores son aproximadamente 5,50 y 10,69 kg más componentes pendientes. La carcasa no tiene todavía las tomas o salidas que requiere la propulsión; no debe presentarse como un producto listo para fabricación o vuelo. Tampoco están resueltos el plegado y la transición a crucero.

Reproducir desde la raíz del proyecto:

```
.venv-cad/bin/python investigacion-aeronautica/modelos_integrados/render_cad.py
```
