# Aceleración y momentos simultáneos: cribado ideal

Se evaluaron los 36 escenarios hipotéticos de 5 kg del estudio de masa previo con dos cajas de aceleración en ejes del cuerpo y una caja simultánea de momentos de ±0,5 N·m por eje. Se supone cuerpo horizontal, gravedad vertical, fuerzas de ventilador ascendentes dentro de un cono efectivo ideal de 45°, precarga vertical 1 N por módulo y capacidad común de 21 N. Los centros de fuerza, las palancas de reacción laterales y el centro de masa son supuestos; no se usan mapas de ventiladores instalados. Cada caja de aceleración comprende **cada componente** entre ±0,25 g o ±0,5 g: sus esquinas tienen norma √3 veces ese valor.

Se resuelven las 8 esquinas de aceleración por las 8 de momento, 64 asignaciones conjuntas por caja, con un cono interior de rayos. Si todas son admisibles con capacidad 21 N, la convexidad garantiza todo el producto de esas cajas en el modelo estático ideal. En cambio, no obtener certificado en la aproximación interior no descarta una solución del cono continuo ni del vehículo físico. Se exige además que el centro del equipo genérico esté en la zona supuesta del estudio de masa anterior.

| Reserva axial | Posición del equipo restante | Caja de ±0,25 g por componente certificada con 21 N y zona | Capacidad requerida por la aproximación, N/módulo |
|---:|---|---:|---:|
| 38 mm | x=0 | 0/6 | 21,35–21,49 |
| 60 mm | x=0 | 0/6 | 23,24–23,30 |
| 80 mm | x=0 | 0/6 | algunas esquinas inviables en el cono interior |
| 38 mm | CG equilibrado | 5/6 | 18,32–18,43 |
| 60 mm | CG equilibrado | 5/6 | 17,89–17,99 |
| 80 mm | CG equilibrado | 5/6 | 18,12–18,21 |

En los grupos equilibrados se excluye un caso de seis porque el centro del equipo restante cae fuera de su zona longitudinal supuesta. Los otros cinco son certificados condicionales de una asignación estática; no acreditan que los equipos quepan, ni respuesta de actuadores o seguimiento de trayectorias. Los recuentos no son probabilidades.

Ningún escenario certifica la caja de ±0,5 g en cada componente. De hecho, la esquina (0,5; 0,5; −0,5) g exige fuerzas horizontales de magnitud √0,5·mg y una fuerza vertical de 0,5·mg: el cociente es √2, superior a tan(45°)=1. Esa esquina es imposible para **cualquier número de fuerzas ascendentes** dentro de ese cono ideal, independientemente de la capacidad; no significa que una aceleración aislada de 0,5 g sea imposible. No se incluyen aerodinámica exterior, empuje reversible ni otras fuentes de fuerza.

Se resolvieron 4.608 esquinas de las cuales 3.312 tuvieron solución en el cono interior; el mayor residuo de igualdad de las soluciones fue 6,23e−9 en unidades mixtas. Las seis pruebas de `verificar_reserva.py` pasaron; incluyen casos analíticos de sustentación, momento y fuerza fuera del cono. `ACELERACION_MOMENTOS.json` guarda los casos y huellas del código y datos. Se utilizó SciPy 1.18.1 y NumPy 2.5.4 en `/private/tmp/codex-aero-scipy`; el entorno temporal no constituye instalación permanente.

La revisión Antigravity `dd1b26e4` confirmó la necesidad de comprobar esquinas conjuntas para certificar un producto de conjuntos. Se descartó su afirmación genérica de que cuatro actuadores son necesariamente subactuados: aquí cada módulo se modela con una fuerza vectorial, y el rango depende del modelo y configuración. El siguiente paso es sustituir el cono, la capacidad y las palancas ideales por datos instalados y añadir dinámica, viento, estructura y presupuesto de potencia. El resultado no demuestra control autónomo ni vuelo real.
