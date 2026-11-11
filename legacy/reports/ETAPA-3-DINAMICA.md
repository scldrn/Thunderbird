# Masa acoplada y dinámica: resultados condicionales

No constituyen validación de un vehículo ni prueba de optimalidad geométrica.

## Masa e inercia

`cierre_masa.py` acopla masa de motores, batería, estructura, combustible y reactor con centro de gravedad, tensor de inercia y empujes requeridos. Se usa un asignador lineal por pseudoinversa y cotas suficientes de fuerza y momento; no es el asignador de mínima potencia. Las potencias son cotas del modelo de discos aislados, no medidas ni cotas físicas garantizadas con interacción aerodinámica.

108 escenarios; 31 satisfacen los filtros numéricos de masa y separación desplegada. Solo cinco incluyen reactor. El candidato con reactor, rotores de 30 cm y garantía estática de aceleración de 1 g en cualquier dirección resulta en 9,9963 kg: deja únicamente 3,7 g respecto al límite de 10 kg. Depende de tecnología optimista no verificada: 200 N/kg de módulo propulsor, eficiencia efectiva 0,8 y batería de 8 kW/kg y 220 Wh/kg utilizables. No se ha identificado hardware que cumpla conjuntamente estas prestaciones.

Su masa incluye 3,484 kg de módulos propulsores y 2,481 kg de batería. Potencia pico conservadora del asignador: 19,85 kW; cota de estacionario: 7,88 kW. Escenario de 30 s de operación eléctrica y combustible equivalente a 30 s al consumo máximo del reactor. Esto no demuestra 30 s a 1000 km/h ni una transición viable. Los brazos se representan mediante una fracción de masa; articulaciones, bloqueos, cableado y carenados requieren un presupuesto constructivo independiente. La separación verifica esferas envolventes de discos desplegados; no valida brazos, estelas, retracción ni volumen interno.

## Simulación reproducible

`dinamica.py`: cuerpo rígido de seis grados de libertad, ocho estados de empuje reversibles, saturación y actuadores de primer orden. Maniobra: desplazamiento de un metro, regreso, después giro de 30 grados. Se prueban dos orientaciones iniciales y constantes de tiempo de 30, 70 y 150 ms. Traslación sin cambio intencional de orientación; el giro posterior es una prueba separada. No se ha barrido toda dirección ni orientación.

El equilibrio estacionario pasa la verificación. Reducir el paso de 2 a 1 ms cambia la trayectoria menos de 0,78 mm en el caso contrastado. Esto verifica consistencia numérica; no exactitud física.

Sin compensación, un desplazamiento de 1 m en 0,8 s produce errores máximos de 4,4, 11,3 y 25,3 cm respectivamente. La compensación exacta del mismo modelo reduce artificialmente mucho el error; no debe interpretarse como precisión realizable.

`robustez.py`: el controlador supone 70 ms, mientras el actuador real del modelo tiene 30, 70 o 150 ms; orientación inicial de 90 grados.

| Duración del desplazamiento | Error máximo entre los tres casos | Saturación en algún caso |
|---|---:|---|
| 1,2 s | 6,1 cm | No |
| 0,8 s | 9,8 cm | No |
| 0,5 s | 24,8 cm | Sí, en los tres |

El caso de 0,5 s solicita entre 1,56 y 1,77 veces el límite de algún actuador antes del recorte. La saturación no demuestra imposibilidad con otro asignador o arquitectura; demuestra que esta configuración y este controlador no siguen fielmente esa referencia. Los errores se calculan sobre la secuencia completa, incluido el giro posterior.

No se incluyen inversión real del rotor, dinámica del paso variable, par reactivo del motor, momento giroscópico del rotor, aeroelasticidad, interacción de estelas, viento, ruido, latencia de sensores ni restricciones eléctricas transitorias. Las constantes de tiempo elegidas son escenarios, no datos de hardware seleccionado.

## Interpretación

Objetivo provisional útil: un metro en 0,8–1,2 s, manteniendo orientación, antes de exigir 0,5 s. No es una especificación garantizada. El sistema completo con reactor sigue sin cerrar con margen de ingeniería. No se demuestra que ocho rotores desplegables sean óptimos ni que puedan guardarse dentro del fuselaje.

## Fuentes externas y alcance

- Brescianini y D’Andrea, Mechatronics 2018: demostración experimental de control independiente de posición y orientación con ocho rotores reversibles. No demuestra este fuselaje, esta masa ni velocidad transónica: https://www.flyingmachinearena.ethz.ch/wp-content/publications/2018/breMECH18.pdf
- JetCat P250 PRO S V2, ficha del fabricante usada para masa y consumo de referencia: https://www.jetcat.de/en/productdetails/produkte/jetcat/produkte/Professionell/p250%20pro%20s%20v2
- NASA, modelado de baterías para aviación, interacción entre potencia y energía: https://ntrs.nasa.gov/citations/20240007599

Los valores de simulación son cálculos propios; CSV y código acompañan este informe.
