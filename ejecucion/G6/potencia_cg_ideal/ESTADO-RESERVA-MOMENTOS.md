# Reserva simultánea de momentos: ejecución y verificación

Se preparó `reserva_momentos.py` para analizar los 36 escenarios hipotéticos de 5 kg y las ocho esquinas de una caja de momentos ±0,5 N·m. El modelo incorpora un cono interior discretizado supuesto de 45°, precarga vertical de 1 N por ventilador, brazos laterales hipotéticos y límite común ilustrativo de 21 N. Si todas las esquinas tienen solución con ese límite, la convexidad certifica la caja bajo este modelo ideal; un fallo en el cono discretizado no demuestra imposibilidad física ni del cono continuo.

La ejecución original `.venv-aero` (sesión 53901) y sus cuatro pruebas (sesión 85291) terminaron con código 0, pero emitieron advertencias de operaciones de matriz. No se acepta esa ejecución como definitiva. El diagnóstico del entorno `.venv-cad` (44168) se interrumpió; los archivos `scipy/__init__.py` del entorno anterior figuraban como contenido de iCloud sin datos locales, lo cual es una posible causa de la demora, no una demostración de la causa de las advertencias.

Se descargaron NumPy 2.5.4 y SciPy 1.18.1 en `/private/tmp/codex-aero-scipy`, sin alterar las dependencias originales. Se añadieron comprobaciones explícitas de finitud, y se ejecutaron pruebas y matriz usando Python 3.12 del runtime local: seis pruebas pasan sin advertencias; 288/288 esquinas tienen solución en la aproximación interior, con residuo máximo 1,77e−9 en las unidades del sistema mixto. `RESERVA_MOMENTOS.json` es la matriz regenerada y contiene huellas de fuente y código. La carpeta temporal puede desaparecer, por lo que no es un entorno permanente reproducible. La extensión con aceleración simultánea figura en `INFORME-ACELERACION-MOMENTOS.md`.

| Reserva axial | Equipo restante | Casos que cumplen 21 N y la zona supuesta | Capacidad requerida de la aproximación interior, N |
|---:|---|---:|---:|
| 38 mm | x=0 | 6/6 | 16,36–16,49 |
| 60 mm | x=0 | 6/6 | 17,67–17,71 |
| 80 mm | x=0 | 0/6 | 25,69–25,85 |
| 38 mm | CG equilibrado | 5/6 | 14,18 |
| 60 mm | CG equilibrado | 5/6 | 13,90 |
| 80 mm | CG equilibrado | 5/6 | 13,71 |

Cada capacidad corresponde a la peor de ocho esquinas de momentos. Los grupos equilibrados pierden un caso por ubicar el centro del equipo fuera de la zona supuesta. Para 80 mm y equipo en x=0, no obtener certificado con 21 N en el cono interior no prueba imposibilidad en el cono continuo o en el vehículo real. Las capacidades minimizan suma de coeficientes de rayos, una restricción conservadora de fuerza por módulo; no son empujes o potencias medidos. Tampoco son el cálculo anterior de discos paralelos. Los límites de fuerza, CG, palancas, cono y precarga son hipótesis; faltan control dinámico, flujos, potencia y componentes. Estos resultados no validan vuelo.

La comprobación `py_compile` del Python del sistema falló porque intentó escribir en una caché fuera de la zona autorizada; el análisis AST posterior sí pasó sin caché. No se reanudaron CFD pausados.
