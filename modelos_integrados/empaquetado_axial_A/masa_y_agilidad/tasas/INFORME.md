# Límites de cambio de fuerza y giro de las candidatas A

Se añade una restricción temporal al estudio anterior de masa y CG. **No es una medición de respuesta de motor ni servo.** Se usa el escenario ilustrativo más rápido de cada candidata (piel de 0,3 mm, extra de 50 g por estación, balance longitudinal y módulo hipotético de 1 kg en x=400 mm). Esa asignación de masa sigue sin demostrar componentes disponibles o resistencia de piel.

## Formulación y alcance

Se conserva el giro prescrito de 0 a 30° con perfil quíntico, masa 5 kg, fuerza transformada con la actitud, tensor de inercia y límites útiles 21 N/fan, cono efectivo 45° y precarga 1 N. Las fuerzas de todos los instantes se resuelven conjuntamente mediante LP disperso. Por componente se impone |ΔF|≤S Δt/√3: es una condición conservadora que asegura ||ΔF||/Δt≤S para la interpolación lineal. No equivale a un límite calibrado de ángulo mecánico o potencia.

Se exploran S=20/50/100 N/s, parámetros de estudio. Las duraciones son una malla finita de factores 1,01/1,5/2/3/5/10 respecto al cribado sin tasas. La tabla muestra el primer caso probado que pasó 41 y 81 nodos; no es el tiempo mínimo global ni una búsqueda continua de óptimo. Un fallo del LP corresponde a este modelo y aproximación, no prueba imposibilidad física de otra asignación o geometría.

Los tiempos parten del cribado anterior con reservas instantáneas de momento. No se obliga a que las correcciones de perturbación respeten a la vez estos límites de tasa: no se acredita rechazo dinámico de perturbaciones ni robustez de vuelo. La aproximación de cono y la caja de tasas pueden ser conservadoras.

## Resultado e integración directa

La interpolación lineal mantiene continuamente los límites convexos de fuerza, precarga y cambio vectorial. Su fuerza y momento no reproducen exactamente la trayectoria no lineal entre nodos. Se integran posición, velocidad, cuaternión y velocidad angular con Newton–Euler para cuantificar ese error en la dinámica rígida ideal. El integrador pasó comprobaciones analíticas de caída libre, par constante sobre eje principal y estacionario; un caso se repitió con paso y tolerancia menores.

| Reserva axial exterior | Límite vectorial S | Primera duración admitida de la malla | Deriva máxima de posición integrada | Error máximo de actitud |
|---:|---:|---:|---:|---:|
| 38 mm | 20 N/s | 1.175 s | 0.924 mm | 0.0234° |
| 38 mm | 50 N/s | 0.784 s | 0.411 mm | 0.0234° |
| 38 mm | 100 N/s | 0.588 s | 0.231 mm | 0.0235° |
| 60 mm | 20 N/s | 1.332 s | 1.188 mm | 0.0234° |
| 60 mm | 50 N/s | 0.888 s | 0.528 mm | 0.0234° |
| 60 mm | 100 N/s | 0.666 s | 0.297 mm | 0.0234° |
| 80 mm | 20 N/s | 1.431 s | 1.369 mm | 0.0234° |
| 80 mm | 50 N/s | 1.073 s | 0.770 mm | 0.0234° |
| 80 mm | 100 N/s | 1.073 s | 0.770 mm | 0.0234° |

La precisión numérica de esta integración no es precisión física del vehículo. No incluye aerodinámica exterior, interacción de chorros, reacción y giroscopía de los rotores, flexibilidad, motores, ESC, transmisión, servo o fluido transitorio. La velocidad de dirección efectiva guardada se calcula sobre el vector de fuerza interpolado; no es velocidad de servo.

Las fuerzas son continuas, pero sus pendientes pueden cambiar bruscamente en los nodos. No se imponen todavía límites a la segunda derivada de fuerza o a la aceleración mecánica del álabe; un actuador físico podría exigir más suavizado o duración.

El estudio confirma que un perfil factible con fuerzas instantáneas puede necesitar más duración cuando se limita su cambio. Las candidatas no se pueden ordenar solo por el paso axial o una inercia: también importan la distribución de masas y las capacidades temporales del propulsor. No se afirma todavía cuál es óptima para 600–1000 km/h o para la envolvente completa de aceleraciones.

Archivos: `RESULTADOS.json` conserva casos admitidos/rechazados y la malla; `VERIFICACION.json` comprueba interpolación e integración; NPZ con fuerzas y estados. Código: `asignacion_tasas_A.py` y `verificar_tasas_A.py`. El siguiente cierre exige mapas instalados de fuerza/momento/potencia y límites de actuación antes de transferir estas demandas a un prototipo autónomo.
