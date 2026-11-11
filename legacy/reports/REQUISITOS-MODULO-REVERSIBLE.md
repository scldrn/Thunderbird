# Módulo reversible: especificación de investigación y límite de masa

## Decisión actual

Se prioriza estudiar paso variable activo, manteniendo el sentido de giro del motor, para desacoplar inversión de empuje e inversión de velocidad del rotor. No se ha identificado un módulo comercial completo que cumpla los requisitos. No confundir hélice de paso ajustable manualmente con paso controlable en vuelo.

MIT documenta un cambio de paso positivo a negativo en aproximadamente70ms en SU prototipo, con el motor a régimen máximo. Este dato no es una constante de tiempo de empuje ni una garantía de70ms para una hélice de46cm. Fuente primaria: https://acl.mit.edu/projects/variable-pitch-quadrotor

## Requisitos obtenidos por cálculo

Configuración actual:5kg,8 rotores, estaciones longitudinales±0,25L, centro de gravedad supuesto5cm hacia reactor, reserva simultánea de momento1Nm en cualquier dirección. Los siguientes límites se derivan de las facetas del conjunto de fuerzas y momentos; se verificaron adicionalmente180solicitudes aleatorias mediante programación lineal.

| Aceleración adicional omnidireccional | Relación empuje inverso/positivo | Mínimo positivo por módulo | Magnitud inversa por módulo |
|---|---:|---:|---:|
| 0,5g | 1,0 | 29,68N | 29,68N |
| 0,5g | 0,8 | 32,98N | 26,39N |
| 0,5g | 0,6 | 37,11N | 22,26N |
| 1g | 1,0 | 38,94N | 38,94N |
| 1g | 0,8 | 43,27N | 34,61N |
| 1g | 0,6 | 48,68N | 29,21N |

Se ignoran par reactivo de rotor, dinámica y pérdidas entre estelas. Es un requisito estático del modelo, no una especificación de producto validada.

## Presupuesto mecánico explícito

Masas de referencia: reactor1,080kg; motores8×0,128kg; combustible0,156kg. Asignaciones de diseño NO verificadas: piel350g, brazos y bloqueos250g, aviónica y cableado200g, instalación reactor150g, reserva250g.

Con pack12S1P estimado980g quedan560g para los ocho conjuntos de hélice, ESC, servo y buje:70g por estación, además del motor ya contado. No se ha encontrado ni demostrado que un conjunto de46cm cumpla ese límite.

Con pack12S2P estimado1960g, el presupuesto supera5kg en420g ANTES de esos ocho conjuntos. Esto descarta ESTA asignación, no toda arquitectura posible de5kg. Reducir la reserva para hacer cuadrar la suma no constituye validación.

## Caída de tensión: corrección necesaria

Se emplea resistencia DC de referencia12,8mΩ por celda al50%SOC, según ficha P50B. Se usa como constante en una sensibilidad, no como modelo térmico completo. Fuente: https://www.molicel.com/wp-content/uploads/Product-Data-Sheet-of-INR-21700-P50B-80122.pdf

Para tensión en circuito abierto supuesta3,7V/celda:

| Escenario | Pack | Potencia terminal usada | Corriente por celda | Tensión terminal pack | Disipación óhmica estimada |
|---|---|---:|---:|---:|---:|
| 0,5g | 12S1P | 1,55kW | 40,6A | 38,2V | 253W |
| 0,5g | 12S2P | 1,55kW | 18,6A | 41,5V | 107W |
| 1g | 12S1P | 2,36kW | 70,3A | 33,6V | 759W |
| 1g | 12S2P | 2,36kW | 29,6A | 39,8V | 270W |

La ficha limita corriente continua a60A con corte térmico80°C. Estar por debajo de60A no demuestra duración segura ni temperatura admisible. No se calcula temperatura sin capacidad térmica y refrigeración. Los niveles de potencia son máximos muestreados del estudio previo; con paso variable a régimen alto habrá pérdidas de perfil incluso cerca de empuje cero que ese modelo no representa.

El dato de40,2N del motor de referencia fue publicado a46,94V. No se puede asignar ese mismo empuje a38,2V. Como sensibilidad no validada, escalar empuje con el cuadrado de tensión da26,6N, menor que29,7N requeridos para0,5g. No predice el comportamiento de un rotor de paso variable: justifica exigir una curva empuje/RPM/paso/tensión, o estudiar otro bobinado compatible. Fuente del motor: https://store.tmotor.com/product/mn5008-kv400-motor-antigravity-type.html

## Arquitectura mecánica que debe verificarse

Cada estación necesita: motor; eje/buje con rodamientos para variar paso; dos portapalas; mando colectivo por servo y articulación que no transmita giro al servo; sensor o referencia de paso; controlador de motor; unión al brazo con bloqueo. El plegado de palas añade otra articulación distinta de la de paso y exige bloqueo antes de girar. Esta descripción es funcional, no un diseño dimensionado de piezas.

No se eligen servo, rodamientos ni espesor de buje sin calcular momento aerodinámico de paso, fuerza centrífuga, inercia y fatiga de palas. El motor elegido como referencia es una combinación de paso fijo; su eje no acredita compatibilidad directa con el buje propuesto.

## Criterios del siguiente ensayo o dato requerido

1. Curvas de empuje y potencia en ambos sentidos, con combinación concreta de motor y rotor, entre tensión mínima y máxima del pack.
2. Masa pesada de módulo completo, incluidos ESC y mecanismo; contrastar70g adicionales por estación en la variante12S1P.
3. Inversión de empuje medida bajo carga, asentamiento y corriente pico;70ms es referencia experimental ajena, no requisito ya alcanzado.
4. Par reactivo y momento giroscópico para incorporarlos al control.
5. Curvas de perfil cerca de paso cero: no asumir consumo cero con rotor girando.
6. Geometría y bloqueo de plegado, verificados antes de considerar transición.

Los modelos actuales no bastan para cerrar el diseño. La alternativa0,5g permanece como rama de estudio; la1g requiere un presupuesto distinto o componentes más favorables. No se cambia el objetivo del usuario ni se afirma velocidad transónica.

Código y datos: modulo_reversible.py y resultados/modulo_reversible_requisitos.json. Los cálculos no reemplazan ensayos de hardware.
