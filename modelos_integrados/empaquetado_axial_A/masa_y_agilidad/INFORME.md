# Masa, centro de gravedad y giro ideal de las candidatas A

**Resultado condicionado:** abrir más espacio axial no garantiza mayor agilidad. Se añadieron distribuciones de masa explícitas y una maniobra prescrita de 30° sobre el eje de cabeceo, conservando la posición inercial. No se presenta una respuesta física validada ni un tiempo mínimo global de reorientación.

## Qué masas se usan

Las masas geométricas de camisas, álabes y ejes se calculan de los STEP de reserva con densidades SUPUESTAS de 1600/1600/7850 kg/m³. Se excluyen las representaciones macizas de motor y rotor: sus volúmenes no indican su masa real. La piel se sustituye por una masa superficial uniforme sobre el loft cerrado, con densidad supuesta 1600 kg/m³ y espesores de escenario 0,3 u 0,8 mm. Incluye zonas de tapas sin representar su desplazamiento al abrirse.

Por estación se añaden 0,05 / 0,15 / 0,30 kg hipotéticos para equipos no diseñados. Se asigna un módulo propulsivo hipotético de 1 kg en x=+400 mm con radios de giro principales 25/60/60 mm. El equipo restante completa aritméticamente 5 kg y tiene radio de giro por eje de 60 mm. No es un motor seleccionado ni una asignación de batería, combustible o electrónica demostrada.

Se compara colocar el resto en x=0 y desplazarlo para equilibrar CG x=0. El intervalo permitido de su centro, −350 a +50 mm, es una restricción de escenario: no prueba que los equipos quepan en ese lugar. Se rechazan los balances que exigen salir del intervalo. Un total de masa que suma 5 kg por definición no es cierre de masa de ingeniería.

Se integran área, centroides y segundos momentos de triángulos de la piel; los sólidos usan propiedades volumétricas CAD y el teorema de ejes paralelos. El cálculo se comprobó con una caja trasladada analítica y una cáscara esférica. Se conserva el tensor completo en los datos.

## Maniobra y control

Se prescribe θ(u)=30°(10u³−15u⁴+6u⁵), u=t/T, entre reposos. Al girar, la fuerza corporal para mantener la posición se transforma con la actitud: F_B=Rᵀ(0,0,mg). La dinámica exige τ=Iω̇+ω×Iω, conforme a las [ecuaciones de Euler, MIT](https://ocw.mit.edu/courses/16-07-dynamics-fall-2009/resources/mit16_07f09_lec28/). No se usa el momento en posición horizontal como si fuese constante durante todo el giro.

Se mantienen conos efectivos ideales de 45°, capacidad útil 21 N/fan, precarga vertical 1 N/fan y reservas simultáneas de ±0,5 N·m por eje. En cada nodo se calculan intervalos de cabeceo compatibles con las cuatro esquinas de reserva de alabeo/guiñada. Su intersección deja también la reserva de cabeceo y determina las duraciones posibles del perfil. Esta comprobación tiene 61 nodos; tres escenarios se refinan a 241 nodos.

Las ecuaciones de masa rígida omiten giro interno de rotores, reacción, giroscopía, aerodinámica exterior, flexión e interacción entre conductos. Los actuadores realizan instantáneamente cualquier fuerza del modelo. Estas omisiones impiden interpretar los tiempos como velocidad de un producto real.

| Reserva axial exterior | Escenarios que admiten el perfil / explorados | Intervalo de duraciones mínimas de cribado entre los admitidos |
|---:|---:|---:|
| 38 mm | 11 / 12 | 0.392–0.584 s |
| 60 mm | 11 / 12 | 0.444–0.843 s |
| 80 mm | 5 / 12 | 0.715–0.852 s |

Los recuentos son cobertura de escenarios elegidos, no probabilidades de éxito. Las duraciones son límites de una trayectoria y modelo concretos en malla temporal; no se han minimizado todas las trayectorias posibles ni probado factibilidad entre nodos. No se aplican a un giro de 90°, desplazamiento lateral o maniobra a 1000 km/h.

Para comparar inercias con las mismas hipótesis, el caso de piel de 0,3 mm, extra de 50 g por estación y balance longitudinal da:

| Reserva | Inercia de cabeceo | Centro x requerido del equipo restante |
|---:|---:|---:|
| 38 mm | 0.3530 kg·m² | -145 mm |
| 60 mm | 0.3173 kg·m² | -151 mm |
| 80 mm | 0.2889 kg·m² | -153 mm |

## Comprobación de trayectorias reconstruidas

Se reconstruyó una trayectoria nominal por reserva axial, usando el escenario admitido más rápido y añadiendo un 1 % a su duración refinada. Se resolvió nuevamente la asignación en 481 instantes y se verificaron fuerza en ejes inerciales y momento de Euler con el tensor completo. Se guardan fuerzas, ángulos, velocidades y aceleraciones, sin afirmar simulación de motores o seguimiento autónomo.

| Reserva | Duración refinada del cribado | Duración nominal verificada | Cambio al refinar 61→241 nodos |
|---:|---:|---:|---:|
| 38 mm | 0.3918 s | 0.3957 s | 0.000 % |
| 60 mm | 0.4442 s | 0.4486 s | 0.000 % |
| 80 mm | 0.7153 s | 0.7224 s | 0.077 % |

El escenario más rápido de cada grupo usa piel de 0,3 mm, extra de 50 g por estación y balance longitudinal. No se declara estructuralmente admisible esa piel o disponible ese equipo: el cribado estructural anterior no valida esta carrocería. La comparación de tiempos no autoriza reducir espesores para ganar agilidad.

El asignador LP de cada instante no exige continuidad entre soluciones y puede cambiar entre asignaciones equivalentes. Se registran diferencias finitas de fuerza y dirección para detectarlo; no son límites mínimos de hardware ni velocidades mecánicas de álabe. Antes de usar estas trayectorias como mandos, deben imponerse tasas, dinámica y una asignación continua. Un perfil suave del cuerpo no garantiza mandos suaves.

En la reserva de 80 mm, los seis escenarios con el equipo restante centrado en x=0 incumplen el perfil o las reservas; el balance hacia delante recupera cinco de seis casos, y el restante exige situar la masa fuera de la zona supuesta. Esto cuantifica la sensibilidad al CG bajo el módulo hipotético de 1 kg en x=400 mm, sin descartar toda configuración con reserva de 80 mm.

## Consecuencia de diseño

La reserva de 80 mm sigue siendo una candidata de integración, pero no gana por sí sola en agilidad. Las de 38 y 60 mm conservan ventajas en este estudio. La elección debe incluir huella y mapa del propulsor, energía, masa y CG reales, estructura, velocidades de actuación y aerodinámica. No se declara ganador global ni se reduce el objetivo completo a la maniobra de 30°.

Archivos: `ESCENARIOS.json`, `ESCENARIOS.csv`, `VERIFICACION_TRAYECTORIAS.json` y tres NPZ de trayectoria. Código: `agilidad_masa_CG_A.py` y `verificar_agilidad_CG_A.py`. Referencia de dinámica y control omnidireccional: [Brescianini y D’Andrea, ICRA 2016, copia oficial ETH](https://ethz.ch/content/dam/ethz/special-interest/mavt/dynamic-systems-n-control/idsc-dam/People/bdario/brescianini_dandrea_omnidirectional_aerial_vehicle.pdf); su prototipo no valida esta geometría.
