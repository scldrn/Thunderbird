# Benchmark compresible seleccionado: ONERA M6

Se recuperaron el CAD STEP de borde de salida afilado y 271 medidas de Cp del caso 2308, en siete estaciones. [TMR mantiene geometría, datos y condiciones](https://tmbwg.github.io/turbmodels/onerawingnumerics_val.html); [NASA confirma su nueva ubicación](https://www.nasa.gov/nasa-turbulence-modeling-resource/).

Propuesta de contraste: Mach 0,84, α=3,06°, Re de cuerda raíz afilada 14,6 millones y T=300 K. El encabezado experimental conserva Mach 0,8395 y Re basado en cuerda media 11,72 millones. La sexta estación se interpreta como η=0,96. La diferencia entre borde experimental grueso y CAD afilado debe constar al comparar. El documento explicativo de [ONERA](https://tmbwg.github.io/turbmodels/Onerawingnumerics_val/ONERA_M6_Test_Case_TMR.pdf) precisa que los datos originales son presiones, sin coeficientes integrales medidos de sustentación, arrastre o momento.

`calificar_datos.py` verifica estructura de datos, finitud, número de tomas, validez geométrica y huellas; guarda `CALIFICACION.json`. Recuperar entradas no acredita una solución CFD. Faltan malla, contornos, modelo, piloto de coste y sensibilidad. No se transfieren prestaciones de esta ala al A07. La elección del benchmark es metodológica y no cambia la arquitectura de ventiladores internos.
